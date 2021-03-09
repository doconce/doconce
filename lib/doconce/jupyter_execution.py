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

def process_code_block(current_code, current_code_envir, kernel_client, format, code_style='', caption=None, label=None):
    """
    Execute a code block and return it formatted together with any code output

    Execute a code block in a jupyter kernel, process the code's output and return a formatted string
    :param str current_code: line of
    :param str current_code_envir:
    :param JupyterKernelClient kernel_client: instance of JupyterKernelClient from jupyter_execution.py
    :param str format: output formatting, one of ['html', 'latex', 'pdflatex']
    :param str code_style: optional typesetting of code blocks
    :return: text_out, execution_count
    :rtype: str, int
    """
    text_out = ''
    execution_count = 0
    if kernel_client is None:
        return text_out
    if misc.option("execute") and not current_code_envir.endswith("-t") \
            and not current_code_envir.endswith("out"):
        '''if misc.option("execute") and not current_code_envir.endswith("-t"):
        # NB this works for html but messes up latex.py
        if current_code_envir.endswith("out"):
            # Write the output code block to a fake cell output
            #outputs = [{
            #    "text": current_code
            #}]
            return text_out
        #else:
        #    outputs, execution_count = run_cell(kernel_client, current_code)
        '''
        outputs, execution_count = run_cell(kernel_client, current_code)
        if current_code_envir.endswith("-e"):
            # Skip writing the ouput if -e is used
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
                        # TODO: Currently implemented for latex. Implement for html
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

        if not current_code_envir.endswith('hid'):
            execution_count += 1

    return text_out, execution_count


def formatted_code_envir(envir, envir_spec, format):
    '''
    Wrapper function to get environments for formatted code

    Wrapper for html_code_envir, latex_code_envir, and any similar future methods
    :param str envir: code environment e.g. "pycod"
    :param str envir_spec: optional typesetting of code blocks
    :param str format: output format, one of ['html', 'latex', 'pdflatex']
    :return: tuple of html tags/latex environments
    :rtype: [str, str]
    '''
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
    elif envir_spec.endswith("out") and option("ignore_output"):
        return '',''
    elif envir_spec.endswith("-e"):
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

    global envir2pyg, envir2lst

    if envir in ('ipy', 'do'):
        # Find substitutes for ipy and doconce if these lexers
        # are not installed
        # (third-party repos, does not come with pygments, but
        # warnings have been issued by doconce format, with
        # URLs to where the code can be obtained)
        try:
            get_lexer_by_name('ipy')
        except:
            envir2pyg['ipy'] = 'python'
        try:
            get_lexer_by_name('doconce')
        except:
            envir2pyg['do'] = 'text'

    if package == 'pyg':
        begin = '\\begin{minted}[%s]{%s}' % (pyg_style, envir2pyg.get(envir, 'text'))
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

    :param attribute:
    :param format:
    :return:
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