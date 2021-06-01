from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import subprocess
from jupyter_client import KernelManager, kernelspec
from nbformat.v4 import output_from_msg
from . import misc
try:
    from queue import Empty  # Py 3
except ImportError:
    from Queue import Empty # Py 2
import base64, uuid
import regex as re
from .misc import errwarn, _abort, option
from .globals import envir2syntax, syntax_executable
from .common import safe_join, get_code_block_args
from pygments.lexers import get_lexer_by_name


class JupyterKernelClient:
    """Create and start a Jupyter kernel in a programming language.

    Use the jupyter-client API to create and start a jupyter kernel, which can be used to run code.
    The input programming language is searched between the list of installed Jupyter kernels.
    .. seealso::
        - jupyter-client: https://jupyter-client.readthedocs.io/en/latest/index.html
        - Jupyter kernels: https://github.com/jupyter/jupyter/wiki/Jupyter-kernels
    .. note::
        - Install the IJulia Jupyter kernel with `using Pkg; Pkg.add("IJulia");Pkg.build("IJulia")` in julia
        - Uninstall IJulia: `Pkg.rm("IJulia")` in julia, then `jupyter kernelspec uninstall mykernel`
        - Install the bash kernel: https://github.com/takluyver/bash_kernel
        - Install the IR kerneld for R: https://irkernel.github.io/installation/
        after upgrading to R 3.4+: https://github.com/duckmayr/install-update-r-on-linux
        - List the currently installed kernels: jupyter kernelspec list
    """
    def __init__(self, syntax):
        """Initialize the class by creating and starting a Jupyter kernel

        :param str syntax: programming language of the Jupyter kernel
        """
        kernel_name = self.find_kernel_name(syntax)
        self.kernel_name = kernel_name
        self.manager = KernelManager(kernel_name=kernel_name)
        if not self.kernel_name:
            return
        self.kernel = self.manager.start_kernel()
        self.client = self.manager.client()
        self.client.start_channels()

    def is_alive(self):
        """Check if the kernel process is running

        :return: True or False
        :rtype: bool
        """
        return self.manager.is_alive()

    @staticmethod
    def find_kernel_name(syntax):
        """Internal function to searched a Jupyter kernel between the list of
        Jupyter kernels installed.

        :param str syntax: programming language of the Jupyter kernel
        :return: kernel name
        :rtype: str or None
        """
        # Get Kernel specifications
        # Kernel names look like: ['python3', 'ir', 'julia-1.6', 'bash']
        # Kernel languages look like: ['python', 'R', 'julia', 'bash']
        # Kernel display names look like: ['Python 3', 'R', 'Julia 1.6.1', 'Bash']
        kernelspecmanager = kernelspec.KernelSpecManager()
        kernel_specs = kernelspecmanager.get_all_specs()
        kernel_name = [spec for spec in kernel_specs]
        languages = [kernel_specs[spec]['spec']['language'].lower() for spec in kernel_specs]
        display_names = [kernel_specs[spec]['spec']['display_name'] for spec in kernel_specs]
        if syntax in languages:
            return kernel_name[languages.index(syntax)]
        else:
            errwarn('*** No Jupyter kernels found for %s. The kernels available are:' % syntax)
            errwarn('    %s' % ','.join(kernel_name))
            errwarn('    To install Jupyter kernels see https://github.com/jupyter/jupyter/wiki/Jupyter-kernels')
            return ''

    def run_cell(self, source, timeout=120):
        """Execute code in kernel

        :param str source: code to run
        :param int timeout: timeout
        :return: execution output, execution count
        :rtype: Tuple[List[str], int]
        """
        outs = []
        execution_count = None
        if 'client' not in self.__dir__():
            outs, execution_count
        if misc.option('verbose-execute'):
            print("Executing cell:\n{}\nExecution in\n{}\n".format(source, os.getcwd()))

        # Adapted from nbconvert.ExecutePreprocessor
        # Copyright (c) IPython Development Team.
        # Distributed under the terms of the Modified BSD License.
        msg_id = self.client.execute(source)
        # wait for finish, with timeout
        while True:
            try:
                msg = self.client.shell_channel.get_msg(timeout=timeout)
            except Empty:
                print("Timeout waiting for execute reply", timeout)
                print("Tried to run the following source:\n{}".format(source))
                try:
                    exception = TimeoutError
                except NameError:
                    exception = RuntimeError
                raise exception("Cell execution timed out")

            if msg['parent_header'].get('msg_id') == msg_id:
                if misc.option('verbose-execute'):
                    print("Wrong message id")
                break
            else:
                if misc.option('verbose-execute'):
                    print("Not our reply")
                continue

        while True:
            try:
                # We've already waited for execute_reply, so all output
                # should already be waiting. However, on slow networks, like
                # in certain CI systems, waiting < 1 second might miss messages.
                # So long as the kernel sends a status:idle message when it
                # finishes, we won't actually have to wait this long, anyway.
                msg = self.client.iopub_channel.get_msg(timeout=5)
            except Empty:
                if misc.option('verbose-execute'):
                    print("Timeout waiting for IOPub output")
                break
            if msg['parent_header'].get('msg_id') != msg_id:
                if misc.option('verbose-execute'):
                    print("Not output from our execution")
                continue

            if misc.option('verbose-execute'):
                print(msg)

            msg_type = msg['msg_type']
            content = msg['content']

            # set the prompt number for the input and the output
            if 'execution_count' in content:
                execution_count = content['execution_count']
                # cell['execution_count'] = content['execution_count']

            if msg_type == 'status':
                if content['execution_state'] == 'idle':
                    if misc.option('verbose-execute'):
                        print("State is idle")
                    break
                else:
                    if misc.option('verbose-execute'):
                        print("Other status")
                    continue
            elif msg_type == 'execute_input':
                continue
            elif msg_type == 'clear_output':
                outs[:] = []
                if misc.option('verbose-execute'):
                    print("Request to clear output")
                continue
            elif msg_type.startswith('comm'):
                if misc.option('verbose-execute'):
                    print("Output start with 'comm'")
                continue

            display_id = None
            if msg_type in {'execute_result', 'display_data', 'update_display_data'}:
                display_id = msg['content'].get('transient', {}).get('display_id', None)
                if msg_type == 'update_display_data':
                    if misc.option('verbose-execute'):
                        print("Update_display_data doesn't get recorded")
                    continue

            try:
                out = output_from_msg(msg)
            except ValueError:
                print("unhandled iopub msg: " + msg_type)

            outs.append(out)

            if misc.option('verbose-execute'):
                print("Cell execution result:\n{}\n".format(out))

        return outs, execution_count

    def stop(self):
        """Shutdown the kernel."""
        if 'client' in self.__dir__():
            self.client.stop_channels()
            self.manager.shutdown_kernel()


# Helper functions to format code blocks, currently to the html, latex, and pdflatex formats

# Definitions for embedding images, captions, labels
html_pdf = (
    '<object width="500" height="375" type="application/pdf" data="{filename_stem}">'
    '<p>PDF cannot be displayed in your browser. See {filename_stem}</p>'
    '</object>')

html_png = (
    '<div class="output_png output_subarea">'
    '<img src="{filename_stem}">'
    '</div>')

html_caption = ''

html_label = '<div id="{label}"></div>'

latex_pdf = (
    "\n"
    "\\begin{{center}}\n"
    "   \\includegraphics[width=0.8\\textwidth]{{{filename_stem}}}\n"
    "{caption}{label}"
    "\\end{{center}}\n"
)

latex_png = latex_pdf

latex_caption = "   \\captionof{{figure}}{{{caption}}}\n"

latex_label = "   \\label{{{label}}}\n"


def start_kernel(syntax, kernel_client):
    """Start a Jupyter kernel for a specified programming language

    Given a programming language `syntax`, start a Jupyter kernel, if not already started.
    The Jupyter kernels are started using the JupyterKernelClient class and inserted
    in the input kernels `kernel_client` dictionary
    :param str syntax: the kernel's programming language
    :param Dict[str -> JupyterKernelClient] kernel_client: dictionary of kernel names to
    instances of (JupyterKernelClient)
    :param Dict[str -> JupyterKernelClient] kernels: dictionary of JupyterKernelClient instances
    """
    if option("execute"):
        if syntax in kernel_client:
            # Already started
            pass
        else:
            kernel_client[syntax] = JupyterKernelClient(syntax=syntax)
            if syntax == 'python':
                outputs, count = kernel_client[syntax].run_cell(
                    "%matplotlib inline\n" +
                    "from IPython.display import set_matplotlib_formats\n" +
                    "set_matplotlib_formats('pdf', 'png')"
                )


def execute_subprocess(code, syntax, code_style='', format=None):
    """WORK IN PROGRESS. Execute code using Python's subprocess

    Execute code using Python's subprocess and return a formatted output
    :param str code: code to execute
    :param str syntax: programming language of the code
    :param str code_style: optional typesetting of code blocks
    :param str format: output formatting, one of ['html', 'latex', 'pdflatex']
    :return: formatted_output or ''
    :rtype: str
    """
    formatted_output = ''
    execution_count = 0
    basename = 'tmp_code'
    syntax2suffix = dict(zip(envir2syntax.values(), envir2syntax.keys()))
    syntax2run = {'bash': 'bash', 'r': 'Rscript', 'julia': 'julia', 'java': 'javac'}
    if syntax in ['python', 'bash', 'julia', 'r']:  # add 'console'?
        # Save to <file>.<envir>
        filename_code = basename + '.' + syntax2suffix[syntax]
        f = open(filename_code, 'w')
        f.write(code)
        f.close()
        # Execute the file
        result = subprocess.run(syntax2run[syntax] + ' ' + filename_code, stdout=subprocess.PIPE, shell=True)
        result.stdout = result.stdout.decode("utf-8")
        begin, end = formatted_code_envir("bash", code_style, format)
        formatted_output = "\n{}\n{}{}".format(begin, result.stdout, end)
    else:
        print(formatted_output)
    return formatted_output, execution_count


def process_code_blocks(filestr, code_style, format):
    """Process a filestr with code blocks

    Loop through a file and process the code it contains.
    :param str filestr: text string
    :param str code_style: optional typesetting of code blocks
    :param str format: output formatting, one of ['html', 'latex', 'pdflatex']
    :return: filestr
    :rtype: str
    """
    execution_count = 0
    lines = filestr.splitlines()
    current_code_envir = None
    current_code = ""
    kernel_client = {}
    for i in range(len(lines)):
        if lines[i].startswith('!bc'):
            LANG, codetype, postfix = get_code_block_args(lines[i])
            current_code_envir = LANG + codetype + postfix or 'dat'
            prog = envir2syntax.get(LANG, '')
            lines[i] = ""
        elif lines[i].startswith('!ec'):
            # See if code has to be shown and executed, then format it
            lines[i] = ''
            # Determine if the code should be executed, shown, and format it
            # The globals.py > syntax_executable var lists all supported languages
            formatted_code, comment, execute, show = format_code(current_code,
                                                                 current_code_envir,
                                                                 code_style,
                                                                 format)
            # Check if there is any label{} or caption{}
            label, caption = get_label_and_caption(lines, i)
            # Execute and/or show the code and its output
            formatted_output = ''
            if execute:
                # Note: the following if-statement is not necessary;
                # get_execute_show returns execute=False for syntax not in syntax_executable
                if envir2syntax.get(LANG, '') in syntax_executable:
                    if prog not in kernel_client:
                        start_kernel(prog, kernel_client)
                    if kernel_client[prog].is_alive():
                        formatted_output, execution_count_ = execute_code_block(
                            current_code=current_code,
                            current_code_envir=current_code_envir,
                            kernel_client=kernel_client[prog],
                            format=format,
                            code_style=code_style,
                            caption=caption,
                            label=label)
                    else:
                        # This is not used yet because syntax_executable is used in format_code to set execute to False
                        formatted_output, execution_count = execute_subprocess(code=current_code,
                                           syntax=envir2syntax.get(LANG, ''),
                                           code_style=code_style,
                                           format=format)
            # Format a code cell and its output
            if show != 'hide':
                if show != 'output':
                    execution_count += 1
                formatted_code = format_cell(formatted_code, formatted_output, execution_count, show, format)
                lines[i] = comment + formatted_code
            current_code_envir = None
            current_code = ""
        else:
            if current_code_envir is not None:
                # Code will be formatted later
                current_code += lines[i] + "\n"
                lines[i] = ""

    # Stop all Jupyter kernels
    #if option("execute"):
    for kernel in kernel_client.values():
        kernel.stop()

    # Remove empty lines for the html format
    if format in ['html']:
        lines = list(filter(lambda l: len(l), lines))

    filestr = safe_join(lines, delimiter='\n')
    return filestr


def execute_code_block(current_code, current_code_envir, kernel_client, format, code_style='', caption=None, label=None):
    """
    Execute a code block and return it formatted together with any code output

    Execute a code block in a jupyter kernel, process the code's output and return a formatted string
    :param str current_code: line of
    :param str current_code_envir:
    :param JupyterKernelClient kernel_client: instance of JupyterKernelClient
    :param str format: output formatting, one of ['html', 'latex', 'pdflatex']
    :param str code_style: optional typesetting of code blocks
    :return: text_out, execution_count
    :rtype: str, int
    """
    text_out = ''
    execution_count = 0
    # Execute the code
    if kernel_client is None:
        return text_out, execution_count
    elif current_code_envir.endswith('out'):      # Output cell
        # Skip executing the code
        outputs = [{'text': current_code}]
    else:
        outputs, execution_count = kernel_client.run_cell(current_code)
    # Process the output from execution
    if current_code_envir.endswith("hid"):      # Hide cell output
        # Skip writing the output, except for ipynb
        if format != 'ipynb':
            outputs = []
    elif current_code_envir.endswith("-e"):     # Hide also in ipynb
        # Skip writing the output even in ipynb
        outputs = []
    if len(outputs) > 0:
        ansi_escape = re.compile(r'\x1b[^m]*m')
        begin, end = formatted_code_envir("pyout", code_style, format)
        for output in outputs:
            if "text" in output:
                text_output = ansi_escape.sub("", output["text"])
                text_out += "\n{}\n{}{}".format(begin, text_output, end)
            if "data" in output:
                data = output["data"]
                if "application/pdf" in data or "image/png" in data:
                    cache_folder = ".doconce_figure_cache"
                    filename_stem = "{}/{}".format(cache_folder, str(uuid.uuid4()))
                    if "application/pdf" in data:
                        img_data = data["application/pdf"]
                        suffix = ".pdf"
                    else:
                        img_data = data["image/png"]
                        suffix = ".png"
                    # Save image to folder
                    if not os.path.exists(cache_folder):
                        os.makedirs(cache_folder)
                    filename = "{}{}".format(filename_stem, suffix)
                    g = open(filename, "wb")
                    g.write(base64.decodebytes(bytes(img_data, encoding="utf-8")))
                    g.close()
                    # Capture caption and label
                    caption_code = ""
                    label_code = ""
                    if caption is not None:
                        formatter = embed_caption_label(attribute='caption', format=format)
                        caption_code = formatter.format(caption=caption)
                    if label is not None:
                        formatter = embed_caption_label(attribute='label', format=format)
                        label_code = formatter.format(label=label)
                    img_formatter = embed_image(image_type=suffix, format=format)
                    text_out += img_formatter.format(filename_stem=filename_stem + suffix,
                                                     caption=caption_code,
                                                     label=label_code)
                elif "text/plain" in data:  # add text only if no image
                    text_output = ansi_escape.sub("", output["data"]["text/plain"])
                    text_out += "\n{}\n{}{}".format(begin, text_output, end)
            elif "traceback" in output:
                # TODO: convert ANSI escape chars to colors
                traceback = "\n".join(output["traceback"])
                traceback = ansi_escape.sub("", traceback)
                text_out += "\n{}\n{}{}".format(begin, traceback, end)

    return text_out, execution_count


def format_code(code_block, code_block_type, code_style, format):
    """Process the block to output the formatted code. Also
        output booleans to trigger execution and rendering of the block

    Wrapper function redirecting to `format_code_latex` in latex.py
    or `format_code_html` in doconce.py.
    :param str code_block: code
    :param str code_block_type: block type e.g. 'pycod-e'
    :param str code_style: optional typesetting of code blocks
    :param str format: output format, one of ['html', 'latex', 'pdflatex']
    :return: formatted_code, comment, execute, show (see the invoked function)
    :rtype: Tuple[str, str, bool, str]
    """
    LANG, codetype, postfix = get_code_block_args('!bc ' + code_block_type)
    execute, show = get_execute_show((LANG, codetype, postfix))
    if format in ['latex', 'pdflatex']:
        from .latex import format_code_latex
        return format_code_latex(code_block, (LANG, codetype, postfix), code_style, postfix, execute, show)
    elif format in ['html']:
        from .html import format_code_html
        return format_code_html(code_block, (LANG, codetype, postfix), code_style, postfix, execute, show)


def get_execute_show(envir):
    """Return whether the code should be executed and showed

    Based on the postfix (e.g. '-e') on a code environment (e.g. 'pycod-e'),
    return whether the code should be executed and shown.
    The output `show` is one of ['format','pre','hide','text','output','html'].
    :param tuple[str, str, str] envir: code blocks arguments e.g. ('py','cod','-h')
    :return: execute, show
    :rtype: bool, str
    """
    (LANG, codetype, postfix) = envir
    prog = envir2syntax.get(LANG, '')
    execute = True
    show = 'format'
    if postfix == '-h':     # Show/Hide button (in html)
        execute = False
    elif postfix == 'hid':  # Hide the cell
        execute = True
        show = 'hide'
    elif postfix == '-e':   # Hide also in ipynb
        execute = True
        show = 'hide'
    elif postfix == 'out':  # Output cell
        execute = True      # execute_code_block will render this as code output
        show = 'output'
    elif postfix == '-t':   # Code as text
        execute = False
        show = 'text'
    # Only execute python
    if not option('execute'):
        execute = False
    elif prog not in syntax_executable:
        execute = False
    return execute, show


def format_cell(formatted_code, formatted_output, execution_count, show, format):
    """Wrapper function to format a code cell and its output

    Wrapper function redirecting to `format_cell_latex` in latex.py
    or `format_cell_html` in doconce.py.
    :param str formatted_code: formatted code
    :param str formatted_output: formatted block
    :param int execution_count: execution count in the rendered cell
    :param str show: how to format the output e.g. 'format','pre','hide','text','output'
    :param str format: output format, one of ['html', 'latex', 'pdflatex']
    :return: func
    :rtype: func -> func
    """
    if format in ['latex','pdflatex']:
        from .latex import format_cell_latex
        return format_cell_latex(formatted_code, formatted_output, execution_count, show)
    elif format in ['html']:
        from .html import format_cell_html
        return format_cell_html(formatted_code, formatted_output, execution_count, show)


def formatted_code_envir(envir, envir_spec, format):
    """
    Get environments for formatted code

    Wrapper for html_code_envir, latex_code_envir, and any similar future methods
    :param str envir: code environment e.g. "pycod"
    :param str envir_spec: optional typesetting of code blocks
    :param str format: output format, one of ['html', 'latex', 'pdflatex']
    :return: tuple of html tags/latex environments
    :rtype: [str, str]
    """
    supported_formats = ['html', 'latex', 'pdflatex']
    if format == 'html':
        begin, end = html_code_envir(envir, envir_spec)
    elif format in ['latex', 'pdflatex']:
        begin, end = latex_code_envir(envir, envir_spec)
    else:
        errwarn('*** error: unsupported format "%s"' % format)
        errwarn('    must be among\n%s' % str(supported_formats))
        _abort()
    return begin, end


def html_code_envir(envir, envir_spec):
    """
    Return html tags that can be used to wrap formatted code

    This method was created to enhance modularization of code. See latex_code_envir in latex.py
    :param tuple[str, str, str] envir: code blocks arguments e.g. ('py','cod','-h')
    :param str envir_spec: optional typesetting of code blocks
    :return: tuple of html tags, e.g. ('<pre>','</pre>')
    :rtype: [str, str]
    """
    begin, end = '<pre>', '</pre>'
    if envir_spec.endswith("out") and option("ignore_output"):
        begin, end = '',''
    elif envir_spec.endswith("-e"):
        begin, end = '',''
    return begin, end


def latex_code_envir(envir, envir_spec):
    """
    Return a latex environment command to wrap formatted code

    Given any code environments and any typesetting of code blocks, return a latex environment
    that can be used to wrap the formatted code
    :param tuple[str, str, str] envir: code blocks arguments e.g. ('py','cod','-h')
    :param envir_spec: optional typesetting of code blocks
    :return: tuple of latex environments, e.g. ('\\bpycod', '\\epycod')
    :rtype: [str, str]
    """
    if envir_spec is None:
        return '\\b' + envir[0] + envir[1], '\\e' + envir[0] + envir[1]
    elif envir[2].endswith("out") and option("ignore_output"):
        return '',''
    elif envir[2].endswith("-e"):
        return '',''
    # Untested old code in the case --latex_code_style is used
    envir = ''.join(envir)

    leftmargin = option('latex_code_leftmargin=', '2')
    bg_vpad = '_vpad' if option('latex_code_bg_vpad') else ''

    envir2 = envir if envir in envir_spec else 'default'

    package = envir_spec[envir2]['package']
    background = envir_spec[envir2]['background']
    # Default styles
    any_style = ''
    lst_style = 'style=simple,xleftmargin=%smm' % leftmargin
    vrb_style = 'numbers=none,fontsize=\\fontsize{9pt}{9pt},baselinestretch=0.95,xleftmargin=%smm' % leftmargin
    # mathescape can be used with minted and lstlisting
    # see https://tex.stackexchange.com/questions/149710/how-to-write-math-symbols-in-a-verbatim,
    # minted can only have math in comments within the code
    # but mathescape make problems with bash and $#
    # (can perhaps be fixed with escapechar=... but I haven't found out)
    if not envir.startswith('sh'):
        pyg_style = 'fontsize=\\fontsize{9pt}{9pt},linenos=false,mathescape,baselinestretch=1.0,' \
                    'fontfamily=tt,xleftmargin=%smm' % leftmargin
    else:
        # Leave out mathescape for unix shell
        pyg_style = 'fontsize=\\fontsize{9pt}{9pt},linenos=false,baselinestretch=1.0,' \
                    'fontfamily=tt,xleftmargin=%smm' % leftmargin
    if envir_spec[envir2]['style'] is not None:
        # Override default style
        if package == 'lst':
            lst_style = envir_spec[envir2]['style']
        elif package == 'vrb':
            vrb_style = envir_spec[envir2]['style']
        elif package == 'pyg':
            pyg_style = envir_spec[envir2]['style']
        else:
            any_style = envir_spec[envir2]['style']

    envir_tp = ''
    if envir.endswith('pro'):
        envir_tp = 'pro'
        envir = envir[:-3]
    elif envir.endswith('cod'):
        envir_tp = 'cod'
        envir = envir[:-3]
    # Mappings from DocOnce code environments to lstlisting names
    # Capitalization does not seem to matter, so I modify envir2syntax
    envir2lst = envir2syntax
    envir2lst.update({'rst': 'text', 'latex': 'TeX', 'js': 'Java', 'sys': 'bash', 'ipy': 'python', 'do': 'text'})

    if envir in ('ipy', 'do'):
        # Find substitutes for ipy and doconce if these lexers
        # are not installed
        # (third-party repos, does not come with pygments, but
        # warnings have been issued by doconce format, with
        # URLs to where the code can be obtained)
        try:
            get_lexer_by_name('ipy')
        except:
            envir2syntax['ipy'] = 'python'
        try:
            get_lexer_by_name('doconce')
        except:
            envir2syntax['do'] = 'text'

    if package == 'pyg':
        begin = '\\begin{minted}[%s]{%s}' % (pyg_style, envir2syntax.get(envir, 'text'))
        end = '\\end{minted}'
    elif package == 'lst':
        if envir2lst.get(envir, 'text') == 'text':
            begin = '\\begin{lstlisting}[language=Python,%s]' % (lst_style,)
        else:
            begin = '\\begin{lstlisting}[language=%s,%s]' % (envir2lst.get(envir, 'text'), lst_style)
        end = '\\end{lstlisting}'
    elif package == 'vrb':
        begin = '\\begin{Verbatim}[%s]' % vrb_style
        end = '\\end{Verbatim}'
    else:  # \begin{package}
        if any_style:
            begin = '\\begin{%s}[%s]' % (package, any_style)
        else:
            begin = '\\begin{%s}' % package
        end = '\\end{%s}' % package

    if background != 'white':
        if envir_tp == 'pro':
            begin = '\\begin{pro%s}{cbg_%s}{bar_%s}' % (bg_vpad, background, background) + begin
            if package in ('vrb', 'pyg'):
                end = end + '\n\\end{pro%s}\n\\noindent' % bg_vpad
            else:
                end = end + '\\end{pro%s}\n\\noindent' % bg_vpad
        else:
            begin = '\\begin{cod%s}{cbg_%s}' % (bg_vpad, background) + begin
            if package in ('vrb', 'pyg'):
                end = end + '\n\\end{cod%s}\n\\noindent' % bg_vpad
            else:
                end = end + '\\end{cod%s}\n\\noindent' % bg_vpad
    return begin, end


def get_label_and_caption(lines, i):
    """Capture any label and caption immediately after a code environment's end

    Use regex on the two lines after a code environment's end (e.g. !ec) to
    extract any label or caption. NB! This method might modify the two lines
    after the code environment by removing any label{} and caption{} commands
    :param list lines: lines of code
    :param int i: current index
    :return: label and caption
    :rtype: (str, str)
    """
    # capture any caption and label in the next two
    # lines after the end of the code environment
    label = None
    label_regex = re.compile(r"[\\]*label\{(.*?)\}")
    label_match = re.search(label_regex, "".join(lines[i + 1:i + 3]))
    if label_match:
        label = label_match.group(1)
    caption = None
    caption_regex = re.compile(r"[\\]*caption\{(.*?)\}")
    caption_match = re.search(caption_regex, "".join(lines[i + 1:i + 3]))
    if caption_match:
        caption = caption_match.group(1)
    # Remove label{} and caption{}
    if len(lines) > i + 1:
        lines[i + 1] = re.sub(label_regex, "", lines[i + 1])
        lines[i + 1] = re.sub(caption_regex, "", lines[i + 1])
    if len(lines) > i + 2:
        lines[i + 2] = re.sub(label_regex, "", lines[i + 2])
        lines[i + 2] = re.sub(caption_regex, "", lines[i + 2])
    return label, caption


def embed_caption_label(attribute, format):
    """Return code for formatting images in different formats

    :param str attribute: one in ['caption','label']
    :param str format: output format, one of ['html', 'latex', 'pdflatex']
    :return: string for embedding code
    :rtype: str
    """
    supported_formats = ['html', 'latex', 'pdflatex']
    if format == 'html':
        if attribute == 'caption':
            output = html_caption
        elif attribute == 'label':
            output = html_label
    elif format in ['latex', 'pdflatex']:
        if attribute == 'caption':
            output = latex_caption
        elif attribute == 'label':
            output = latex_label
    else:
        errwarn('*** error: unsupported format "%s"' % format)
        errwarn('    must be among\n%s' % str(supported_formats))
        _abort()
    return output


def embed_image(image_type, format):
    """Return code for formatting images in different formats

    Wrapper function to return a string of code for embedding code/images in html or latex
    :param str format: output format, one of ['html', 'latex', 'pdflatex']
    :param str image_type: one of ['pdf', 'png']
    :return: string for embedding code
    :rtype: str
    """
    supported_formats = ['html', 'latex', 'pdflatex']
    image_type = image_type.strip('.')
    if format == 'html':
        if image_type == 'pdf':
            output = html_pdf
        elif image_type == 'png':
            output = html_png
    elif format in ['latex', 'pdflatex']:
        output = latex_pdf
    else:
        errwarn('*** error: unsupported format "%s"' % format)
        errwarn('    must be among\n%s' % str(supported_formats))
        _abort()
    return output
