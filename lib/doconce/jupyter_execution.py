from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os

from jupyter_client import KernelManager
from nbformat.v4 import output_from_msg
from . import misc
try:
    from queue import Empty  # Py 3
except ImportError:
    from Queue import Empty # Py 2
import re, base64, uuid
from .misc import errwarn, _abort, option
from .common import safe_join, process_code_envir_postfix
class JupyterKernelClient:
    def __init__(self):
        self.manager = KernelManager(kernel_name='python3')
        self.kernel = self.manager.start_kernel()
        self.client = self.manager.client()
        self.client.start_channels()

def stop(kernel_client):
    kernel_client.client.stop_channels()
    kernel_client.manager.shutdown_kernel()


def run_cell(kernel_client, source, timeout=120):
    if misc.option('verbose-execute'):
        print("Executing cell:\n{}\nExecution in\n{}\n".format(source, os.getcwd()))

    # Adapted from nbconvert.ExecutePreprocessor
    # Copyright (c) IPython Development Team.
    # Distributed under the terms of the Modified BSD License.
    msg_id = kernel_client.client.execute(source)
    # wait for finish, with timeout
    while True:
        try:
            msg = kernel_client.client.shell_channel.get_msg(timeout=timeout)
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

    outs = []
    execution_count = None

    while True:
        try:
            # We've already waited for execute_reply, so all output
            # should already be waiting. However, on slow networks, like
            # in certain CI systems, waiting < 1 second might miss messages.
            # So long as the kernel sends a status:idle message when it
            # finishes, we won't actually have to wait this long, anyway.
            msg = kernel_client.client.iopub_channel.get_msg(timeout=5)
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
    kernel_client = None
    if option("execute"):
        kernel_client = JupyterKernelClient()
        # This enables PDF output as well as PNG for figures.
        # We only use the PDF when available, but PNG should be added as fallback.
        outputs, count = run_cell(
            kernel_client,
            "%matplotlib inline\n" +
            "from IPython.display import set_matplotlib_formats\n" +
            "set_matplotlib_formats('pdf', 'png')"
        )

    for i in range(len(lines)):
        if lines[i].startswith('!bc'):
            words = lines[i].split()
            if len(words) == 1:
                current_code_envir = 'ccq'
            else:
                current_code_envir = words[1]
            if current_code_envir is None:
                # Should not happen since a !bc is encountered first and
                # current_code_envir is then set above
                # There should have been checks for this in doconce.py
                errwarn('*** error: mismatch between !bc and !ec')
                errwarn('\n'.join(lines[i - 3:i + 4]))
                _abort()
            lines[i] = ""
        elif lines[i].startswith('!ec'):
            if current_code_envir is None:
                # No envir set by previous !bc?
                errwarn('*** error: mismatch between !bc and !ec')
                errwarn('    found !ec without a preceding !bc at line')
                errwarn('\n'.join(lines[i - 8:i - 1]))
                errwarn('error line >>>', lines[i])
                errwarn('\n'.join(lines[i + 1:i + 8]))
                _abort()
            # See if code has to be shown and executed, then format it
            lines[i] = ''
            formatted_code, comment, execute, show = format_code(current_code,
                                                                 current_code_envir,
                                                                 code_style,
                                                                 format)
            # Check if there is any label{} or caption{}
            label, caption = get_label_and_caption(lines, i)
            # Execute and/or show the code and its output
            formatted_output = ''
            if execute:
                formatted_output, execution_count_ = execute_code_block(
                    current_code=current_code,
                    current_code_envir=current_code_envir,
                    kernel_client=kernel_client,
                    format=format,
                    code_style=code_style,
                    caption=caption,
                    label=label)
            if show is not 'hide':
                if show is not 'output':
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

    if option("execute"):
        stop(kernel_client)

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
    if kernel_client is None:
        return text_out, execution_count
    if current_code_envir.endswith('out'):      # Output cell
        outputs = [{'text': current_code}]
    else:
        outputs, execution_count = run_cell(kernel_client, current_code)
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
    :return:
    """
    postfix = process_code_envir_postfix(code_block_type)
    execute, show = get_execute_show(postfix)
    if len(postfix):
        code_block_type = code_block_type[:-len(postfix)]
    if format in ['latex','pdflatex']:
        from .latex import format_code_latex
        return format_code_latex(code_block, code_block_type, code_style, postfix, execute, show)
    elif format in ['html']:
        from .html import format_code_html
        return format_code_html(code_block, code_block_type, code_style, postfix, execute, show)


def get_execute_show(postfix):
    """Return whether the code should be executed and showed

    Based on the postfix (e.g. '-e') on a code environment (e.g. 'pycod-e'),
    return whether the code should be executed and shown
    :param str postfix: postfix (e.g. '-e') to code environment (e.g. 'pycod-e')
    :return: execute, show
    :rtype: bool, str
    """
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
        return execute, show
    elif postfix == '-t':   # Code as text
        execute = False
        show = 'text'
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
    :param str envir: code environment e.g. "pycod"
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
    :param envir: code environment e.g. "pycod"
    :param envir_spec: optional typesetting of code blocks
    :return: tuple of latex environments, e.g. ('\\bpycod', '\\epycod')
    :rtype: [str, str]
    """
    if envir_spec is None:
        return '\\b' + envir, '\\e' + envir
    elif envir.endswith("out") and option("ignore_output"):
        return '',''
    elif envir.endswith("-e"):
        return '',''

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

    # Mappings from DocOnce code environments to Pygments and lstlisting names
    envir2lst = dict(
        pyshell='Python',
        py='Python', cy='Python', f='Fortran',
        c='C', cpp='C++', bash='bash', sh='bash', rst='text',
        m='Matlab', pl='Perl', swig='C++',
        latex='TeX', html='HTML', js='Java',
        java='Java',
        xml='XML', rb='Ruby', sys='bash',
        dat='text', txt='text', csv='text',
        ipy='Python', do='text',
        # pyopt and pysc are treated explicitly
        r='r', php='php',
    )

    envir2pygments = dict(
        pyshell='python',
        py='python', cy='cython', f='fortran',
        c='c', cpp='c++', cu='cuda', cuda='cuda', sh='bash', rst='rst', swig='c++',
        bash='bash',
        m='matlab', pl='perl',
        latex='latex',
        html='html',
        xml='xml', rb='ruby', sys='console',
        js='js', java='java',
        dat='text', txt='text', csv='text',
        ipy='ipy', do='doconce',
        # pyopt and pysc are treated explicitly
        r='r', php='php'
    )

    if envir in ('ipy', 'do'):
        # Find substitutes for ipy and doconce if these lexers
        # are not installed
        # (third-party repos, does not come with pygments, but
        # warnings have been issued by doconce format, with
        # URLs to where the code can be obtained)
        try:
            get_lexer_by_name('ipy')
        except:
            envir2pygments['ipy'] = 'python'
        try:
            get_lexer_by_name('doconce')
        except:
            envir2pygments['do'] = 'text'

    if package == 'pyg':
        begin = '\\begin{minted}[%s]{%s}' % (pyg_style, envir2pygments.get(envir, 'text'))
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
