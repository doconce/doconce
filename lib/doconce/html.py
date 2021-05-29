from __future__ import print_function
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from past.builtins import basestring
from builtins import object
import os, glob, sys, glob, base64, uuid
import regex as re
import shlex
from .common import     table_analysis, plain_exercise, insert_code_blocks, \
    insert_tex_blocks, indent_lines, online_python_tutor, bibliography, _linked_files, \
    safe_join, is_file_or_url, envir_delimiter_lines, doconce_exercise_output, \
     get_legal_pygments_lexers, has_custom_pygments_lexer, emoji_url, \
     fix_ref_section_chapter, cite_with_multiple_args2multiple_cites, \
    INLINE_TAGS, INLINE_TAGS_SUBST
from .misc import option, _abort
from doconce import globals
from .misc import errwarn, debugpr
from . import jupyter_execution
# ---- Import a pygments syntax highlighter for DocOnce ----
from pygments import __version__ as pygm
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight
from pygments.styles import get_all_styles

html_quote, html_warning, html_question, html_notice = None, None, None, None
html_summary, html_block, html_box = None, None, None
box_shadow = 'box-shadow: 8px 8px 5px #888888;'

# Filename generator to store a list of dependencies for html output
_file_collection_filename = '.%s_html_file_collection'

# Mapping from LANG envir in Typesetting Styles to programming language
# Typesetting Styles: !bc LANG[cod|pro][postfix]
envir2syntax = globals.envir2syntax
envir2syntax.update({'sys': 'text', 'cc': 'text', 'ccq': 'text'})

# From https://service.real.com/help/library/guides/realone/ProductionGuide/HTML/htmfiles/colors.htm:
color_table = [
    ('white', '#FFFFFF', 'rgb(255,255,255)'),
    ('silver', '#C0C0C0', 'rgb(192,192,192)'),
    ('gray', '#808080', 'rgb(128,128,128)'),
    ('black', '#000000', 'rgb(0,0,0)'),
    ('yellow', '#FFFF00', 'rgb(255,255,0)'),
    ('fuchsia', '#FF00FF', 'rgb(255,0,255)'),
    ('red', '#FF0000', 'rgb(255,0,0)'),
    ('maroon', '#800000', 'rgb(128,0,0)'),
    ('lime', '#00FF00', 'rgb(0,255,0)'),
    ('olive', '#808000', 'rgb(128,128,0)'),
    ('green', '#008000', 'rgb(0,128,0)'),
    ('purple', '#800080', 'rgb(128,0,128)'),
    ('aqua', '#00FFFF', 'rgb(0,255,255)'),
    ('teal', '#008080', 'rgb(0,128,128)'),
    ('blue', '#0000FF', 'rgb(0,0,255)'),
    ('navy', '#000080', 'rgb(0,0,128)'),]

# html code and corresponding regex (here for reusability)
movie2html = {
    '.mp4': "\n    <source src='%(stem)s.mp4'  type='video/mp4;  codecs=\"avc1.42E01E, mp4a.40.2\"'>",
    '.webm': "\n    <source src='%(stem)s.webm' type='video/webm; codecs=\"vp8, vorbis\"'>",
    '.ogg': "\n    <source src='%(stem)s.ogg'  type='video/ogg;  codecs=\"theora, vorbis\"'>",
    'movie_regex':
        r'<(\w+) src=\'(.+)\'\s+type=\'video/(?:mp4|webm|ogg);\s+codecs=[\\]{0,1}\".+[\\]{0,1}\"\'>',
}


def add_to_file_collection(filename, basename=None, mode='a'):
    """Add `filename` to a the collection of files needed to make the HTML output work

    The HTML output from DocOnce might include file dependencies. This function
    creates a basename file with a list dependencies (`filename`)
    :param str filename: filename to add to `basename`
    :param str basename: file basename continaing the collection of required fiiles.
    Default is `.<globals.dofile_basename>_html_file_collection`
    :param str mode: mode for the `open` command, default 'a' (append). If 'r',
    `basename` is only read out
    :return: files in the `basename` file, filename `filename_dep` with list of dependencies
    :rtype: Tuple[List[str], str]
    """
    if isinstance(filename, basestring):
        filenames = [filename]
    elif isinstance(filename, (list,tuple)):
        filenames = filename
    else:
        raise TypeError('filename=%s is %s, not supported' % (filename, type(filename)))
    if not basename:
        basename = globals.dofile_basename
    filename_dep = _file_collection_filename % basename
    # Read out the file content to a list of files
    if os.path.exists(filename_dep):
        f = open(filename_dep, 'r')
        files = [name.strip() for name in f.read().split()]
        f.close()
    else:
        files = []
    if mode in ['a', 'w']:
        f = open(filename_dep, mode)
        for name in filenames:
            # in append 'a' mode skip already registered files
            if mode == 'a' and name in files:
                continue
            f.write(name + '\n')
            files.append(name)
        f.close()
    return files, filename_dep


# HTML code

html_cell_code = (
            '  <div class="input">\n'
            '    <div class="inner_cell">\n'
            '      <div class="input_area">\n'
            '        %s'        # code <div> with class highlight
            '      </div>\n'
            '    </div>\n'
            '  </div>\n')
html_cell_output = (
            '  <div class="output_wrapper">\n'
            '    <div class="output">\n'
            '      <div class="output_area">\n'
            '        <div class="output_subarea output_stream output_stdout output_text">'
            '          %s\n'      # code output wrapped in <pre> 
            '        </div>\n'
            '      </div>\n'
            '    </div>\n'
            '  </div>\n')

html_cell_wrap = '<div class="cell border-box-sizing code_cell rendered">\n'

html_cell = html_cell_wrap + \
            html_cell_code + \
            html_cell_output + \
            '</div>\n'

html_toggle_btn = (
            '\n'
            '<script type="text/javascript">\n'
            'function show_hide_code%(hash)s(){\n'
            '  $("#code%(hash)s").toggle();\n'
            '}\n'
            '</script>\n'
            '<button type="button" onclick="show_hide_code%(hash)s()">Show/Hide code</button>\n'
            '<div id="code%(hash)s" style="display:none">\n'
            '%(formatted_code)s\n'
            '</div>\n')

html_sagecell = (
            '\n<div class="sage_compute">\n'
            '<script type="text/x-sage">\n'
            '%s\n'
            '</script>\n'
            '</div>\n')

html_toc_ = (
            '<h1 id="table_of_contents">%s</h1>\n'  #toc
            '%s\n'                                  #hr
            '<div class=\'toc\'>\n'
            '%s'                                    #html for chapters/sections/etc
            '</div>\n<br>')

html_tab = '<span class="tab"> '


# Style sheets

css_toc = ( '.tab {\n'
            '  padding-left: 1.5em;\n'
            '}\n'
            'div.toc p,a {\n'
            '  line-height: 1.3;\n'
            '  margin-top: 1.1;\n'
            '  margin-bottom: 1.1;\n'
            '}\n')

css_style = (
            '\n'
             '%s\n'
             '<style type="text/css">\n'
             '%s\n'
             'div { text-align: justify; text-justify: inter-word; }\n') + \
            css_toc + \
            '</style>\n'

admon_styles_text = ('.alert-text-small   { font-size: 80%%;  }\n'
                     '.alert-text-large   { font-size: 130%%; }\n'
                     '.alert-text-normal  { font-size: 90%%;  }\n')

admon_styles1 = admon_styles_text + \
                ('.notice, .summary, .warning, .question, .block {\n'
                 'border: 1px solid; margin: 10px 0px; padding:15px 10px 15px 50px;\n'
                 'background-repeat: no-repeat; background-position: 10px center;\n'
                 '}\n'
                 '.notice   { color: #00529B; background-color: %(background_notice)s;\n'
                 'background-image: url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/%(icon_notice)s); }\n'
                 '.summary  { color: #4F8A10; background-color: %(background_summary)s;\n'
                 'background-image:url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/%(icon_summary)s); }\n'
                 '.warning  { color: #9F6000; background-color: %(background_warning)s;\n'
                 'background-image: url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/%(icon_warning)s); }\n'
                 '.question { color: #4F8A10; background-color: %(background_question)s;\n'
                 'background-image:url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/%(icon_question)s); }\n'
                 '.block    { color: #00529B; background-color: %(background_notice)s; }\n')

admon_styles2 = admon_styles_text + (
    '.alert {\n'
    '  padding:8px 35px 8px 14px; margin-bottom:18px;\n'
    '  text-shadow:0 1px 0 rgba(255,255,255,0.5);\n'
    '  border:1px solid %(boundary)s;\n'
    '  border-radius: 4px;\n'
    '  -webkit-border-radius: 4px;\n'
    '  -moz-border-radius: 4px;\n'
    '  color: %(color)s;\n'
    '  background-color: %(background)s;\n'
    '  background-position: 10px 5px;\n'
    '  background-repeat: no-repeat;\n'
    '  background-size: 38px;\n'
    '  padding-left: 55px;\n'
    '  width: 75%%;\n'
    ' }\n'
    '.alert-block {padding-top:14px; padding-bottom:14px}\n'
    '.alert-block > p, .alert-block > ul {margin-bottom:1em}\n'
    '.alert li {margin-top: 1em}\n'
    '.alert-block p+p {margin-top:5px}\n'
    '.alert-notice { background-image: url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/'
    '%(icon_notice)s); }\n'
    '.alert-summary  { background-image:url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/'
    '%(icon_summary)s); }\n'
    '.alert-warning { background-image: url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/'
    '%(icon_warning)s); }\n'
    '.alert-question {background-image:url(RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/'
    '%(icon_question)s); }\n')

# alt: background-image: url(data:image/png;base64,iVBORw0KGgoAAAAN...);

css_solarized = ('/* solarized style */\n'
                 'body {\n'
                 '  margin: 5;\n'
                 '  padding: 0;\n'
                 '  border: 0; /* Remove the border around the viewport in old versions of IE */\n'
                 '  width: 100%;\n'
                 '  background: #fdf6e3;\n'
                 '  min-width: 600px;	/* Minimum width of layout - remove if not required */\n'
                 '  font-family: Verdana, Helvetica, Arial, sans-serif;\n'
                 '  font-size: 1.0em;\n'
                 '  line-height: 1.3em;\n'
                 '  color: #657b83;\n'
                 '}\n'
                 'a { color: #859900; text-decoration: underline; }\n'
                 'a:hover, a:active { outline:none }\n'
                 'a, a:active, a:visited { color: #859900; }\n'
                 'a:hover { color: #268bd2; }\n'
                 'h1, h2, h3 { margin:.8em 0 .2em 0; padding:0; line-height: 125%; }\n'
                 'h2 { font-variant: small-caps; }\n'
                 'tt, code { font-family: monospace, sans-serif; box-shadow: none; }\n'
                 'hr { border: 0; width: 80%; border-bottom: 1px solid #aaa; }\n'
                 'p { text-indent: 0px; }\n'
                 'p.caption { width: 80%; font-style: normal; text-align: left; }\n'
                 'hr.figure { border: 0; width: 80%; border-bottom: 1px solid #aaa; }\n')

css_solarized_dark = ('/* solarized dark style */\n'
                      'body {\n'
                      '  background-color: #002b36;\n'
                      '  color: #839496;\n'
                      '  font-family: Menlo;\n'
                      '}\n'
                      'code { background-color: #073642; color: #93a1a1; box-shadow: none; }\n'
                      'a { color: #859900; text-decoration: underline; }\n'
                      'a:hover, a:active { outline:none }\n'
                      'a, a:active, a:visited { color: #b58900; }\n'
                      'a:hover { color: #2aa198; }\n')

def css_link_solarized_highlight(style='light'):
    return ('\n'
            '<link href="RAW_GITHUB_URL/doconce/doconce/master/bundled/html_styles/style_solarized_box/css/'
            'solarized_%(style)s_code.css" rel="stylesheet" type="text/css" title="%(style)s"/>\n'
            '<script src="RAW_GITHUB_URL/doconce/doconce/master/bundled/html_styles/style_solarized_box/'
            'js/highlight.pack.js"></script>\n'
            '<script>hljs.initHighlightingOnLoad();</script>\n') % vars()

css_link_solarized_thomasf_light = \
    '<link href="https://thomasf.github.io/solarized-css/solarized-light.min.css" rel="stylesheet">'
css_link_solarized_thomasf_dark = \
    '<link href="https://thomasf.github.io/solarized-css/solarized-dark.min.css" rel="stylesheet">'
css_solarized_thomasf_gray = (
    'h1, h2, h3, h4 { color:#839496; font-weight: bold; } /* gray */\n'
    'code { padding: 0px; background-color: inherit; }\n'
    'pre {\n'
    '  border: 0pt solid #93a1a1;\n'
    '  box-shadow: none;\n'
    '}\n')

css_solarized_thomasf_green = ('h1 {color: #b58900;}  /* yellow */\n'
                               '/* h1 {color: #cb4b16;}  orange */\n'
                               '/* h1 {color: #d33682;}  magenta, the original choice of thomasf */\n'
                               'code { padding: 0px; background-color: inherit; }\n'
                               'pre {\n'
                               '  border: 0pt solid #93a1a1;\n'
                               '  box-shadow: none;\n'
                               '}\n')  # h2, h3 are green

# css for jupyter blocks
css_jupyter_blocks = (
    'div.highlight {\n'
    '    border: 1px solid #cfcfcf;\n'
    '    border-radius: 2px;\n'
    '    line-height: 1.21429em;\n'
    '}\n'
    'div.cell {\n'
    '    width: 100%;\n'
    '    padding: 5px 5px 5px 0;\n'
    '    margin: 0;\n'
    '    outline: none;\n'
    '}\n'
    'div.input {\n'
    '    page-break-inside: avoid;\n'
    '    box-orient: horizontal;\n'
    '    box-align: stretch;\n'
    '    display: flex;\n'
    '    flex-direction: row;\n'
    '    align-items: stretch;\n'
    '}\n'
    'div.inner_cell {\n'
    '    box-orient: vertical;\n'
    '    box-align: stretch;\n'
    '    display: flex;\n'
    '    flex-direction: column;\n'
    '    align-items: stretch;\n'
    '    box-flex: 1;\n'
    '    flex: 1;\n'
    '}\n'
    'div.input_area {\n'
    '    border: 1px solid #cfcfcf;\n'
    '    border-radius: 4px;\n'
    '    background: #f7f7f7;\n'
    '    line-height: 1.21429em;\n'
    '}\n'
    'div.input_area > div.highlight {\n'
    '    margin: .4em;\n'
    '    border: none;\n'
    '    padding: 0;\n'
    '    background-color: transparent;\n'
    '}\n'
    'div.output_wrapper {\n'
    '    position: relative;\n'
    '    box-orient: vertical;\n'
    '    box-align: stretch;\n'
    '    display: flex;\n'
    '    flex-direction: column;\n'
    '    align-items: stretch;\n'
    '}\n'
    '.output {\n'
    '    box-orient: vertical;\n'
    '    box-align: stretch;\n'
    '    display: flex;\n'
    '    flex-direction: column;\n'
    '    align-items: stretch;\n'
    '}\n'
    'div.output_area {\n'
    '    padding: 0;\n'
    '    page-break-inside: avoid;\n'
    '    box-orient: horizontal;\n'
    '    box-align: stretch;\n'
    '    display: flex;\n'
    '    flex-direction: row;\n'
    '    align-items: stretch;\n'
    '}\n'
    'div.output_subarea {\n'
    '    padding: .4em .4em 0 .4em;\n'
    '    box-flex: 1;\n'
    '    flex: 1;\n'
    '}\n'    
    'div.output_text {\n'
    '    text-align: left;\n'
    '    color: #000;\n'
    '    line-height: 1.21429em;\n'
    '}\n'
)

css_body = ('\n'
            'body {\n'
            '  margin-top: 1.0em;\n'
            '  background-color: #ffffff;\n'
            '  font-family: Helvetica, Arial, FreeSans, san-serif;\n'
            '  color: #000000;\n'
            '}\n')

css_base = ('h1 {{ font-size: 1.8em; color: {h_color}; }}\n'
            'h2 {{ font-size: 1.6em; color: {h_color}; }}\n'
            'h3 {{ font-size: 1.4em; color: {h_color}; }}\n'
            'h4 {{ font-size: 1.2em; color: {h_color}; }}\n'
            'a {{ color: {h_color}; text-decoration:none; }}\n'
            'tt {{ font-family: "Courier New", Courier; }}\n'
            'p {{ text-indent: 0px; }}\n'
            'hr {{ border: 0; width: 80%; border-bottom: 1px solid #aaa}}\n'
            'p.caption {{ width: 80%; font-style: normal; text-align: left; }}\n'
            'hr.figure {{ border: 0; width: 80%; border-bottom: 1px solid #aaa; }}')

css_blueish = "/* blueish style */\n" + \
              css_body + \
              css_base.format(h_color='#1e36ce') + \
              "\npre { background: #ededed; color: #000; padding: 15px;}\n" + \
              css_jupyter_blocks

css_blueish2 = "/* blueish2 style (as blueish style, but different pre and code tags\n" \
               "   (only effective if pygments is not used))\n*/\n" + \
               css_body + \
               css_base.format(h_color='#1e36ce') + \
               ('\n'
                'pre {\n'
                '  background-color: #fefbf3;\n'
                '  vpadding: 9px;\n'
                '  border: 1px solid rgba(0,0,0,.2);\n'
                '  -webkit-box-shadow: 0 1px 2px rgba(0,0,0,.1);\n'
                '  -moz-box-shadow: 0 1px 2px rgba(0,0,0,.1);\n'
                '  box-shadow: 0 1px 2px rgba(0,0,0,.1);\n'
                '}\n'
                'pre, code { font-size: 90%; line-height: 1.6em; }\n') + \
               css_jupyter_blocks

css_bloodish = "/* bloodish style */\n" + \
               ('body {\n'
                '  font-family: Helvetica, Verdana, Arial, Sans-serif;\n'
                '  color: #404040;\n'
                '  background: #ffffff;\n'
                '}\n') + \
               css_base.format(h_color='#8A0808') + \
               css_jupyter_blocks

# Tactile theme from GitHub web page generator
css_tactile = ('\n'
               '/* Builds on\n'
               '   https://meyerweb.com/eric/tools/css/reset/\n'
               '   v2.0 | 20110126\n'
               '   License: none (public domain)\n'
               '   Many changes for DocOnce by Hans Petter Langtangen.\n'
               '*/\n'
               'html, body, div, span, applet, object, iframe,\n'
               'h1, h2, h3, h4, h5, h6, p, blockquote, pre,\n'
               'a, abbr, acronym, address, big, cite, code,\n'
               'del, dfn, em, img, ins, kbd, q, s, samp,\n'
               'small, strike, strong, sub, sup, tt, var,\n'
               'b, u, i, center,\n'
               'dl, dt, dd, ol, ul, li,\n'
               'fieldset, form, label, legend,\n'
               'table, caption, tbody, tfoot, thead, tr, th, td,\n'
               'article, aside, canvas, details, embed,\n'
               'figure, figcaption, footer, header, hgroup,\n'
               'menu, nav, output, ruby, section, summary,\n'
               'time, mark, audio, video {\n'
               '	margin: 0;\n'
               '	padding: 0;\n'
               '	border: 0;\n'
               '	font-size: 100%%;\n'
               '	font: inherit;\n'
               '	vertical-align: baseline;\n'
               '}\n'
               '/* HTML5 display-role reset for older browsers */\n'
               'article, aside, details, figcaption, figure,\n'
               'footer, header, hgroup, menu, nav, section {\n'
               '	display: block;\n'
               '}\n'
               '\n'
               'body { line-height: 1; }\n'
               'ol, ul { list-style: none; }\n'
               'blockquote, q {	quotes: none; }\n'
               'blockquote:before, blockquote:after,\n'
               'q:before, q:after { content: ''; content: none; }\n'
               'table {	border-collapse: collapse; border-spacing: 0; }\n'
               '\n'
               'body {\n'
               '  font-size: 1em;\n'
               '  line-height: 1.5;\n'
               '  background: #e7e7e7 url(RAW_GITHUB_URL/doconce/num-methods-for-PDEs'
               '/master/doc/web/images/body-bg.png) 0 0 repeat;\n'
               "  font-family: 'Helvetica Neue', Helvetica, Arial, serif;\n"
               '  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);\n'
               '  color: #6d6d6d;\n'
               '  width: 620px;\n'
               '  margin: 0 auto;\n'
               '}\n'
               '\n'
               'pre, code {\n'
               '  font-family: "Monospace";\n'
               '  margin-bottom: 30px;\n'
               '  font-size: 14px;\n'
               '}\n'
               '\n'
               'code {\n'
               '  border: solid 2px #ddd;\n'
               '  padding: 0 3px;\n'
               '}\n'
               '\n'
               'pre {\n'
               '  padding: 20px;\n'
               '  color: #222;\n'
               '  text-shadow: none;\n'
               '  overflow: auto;\n'
               '  border: solid 4px #ddd;\n'
               '}\n'
               '\n'
               'a { color: #d5000d; }\n'
               'a:hover { color: #c5000c; }\n'
               'ul, ol, dl { margin-bottom: 20px; }\n'
               '\n'
               'hr {\n'
               '  height: 1px;\n'
               '  line-height: 1px;\n'
               '  margin-top: 1em;\n'
               '  padding-bottom: 1em;\n'
               '  border: none;\n'
               '}\n'
               '\n'
               'b, strong { font-weight: bold; }\n'
               'em { font-style: italic; }\n'
               'table { width: 100%%; border: 1px solid #ebebeb; }\n'
               'th { font-weight: 500; }\n'
               'td { border: 4px solid #ddd; text-align: center; font-weight: 300; }\n'
               '\n'
               '/* red color: #d5000d; /*black color: #303030; gray is default */\n'
               '\n'
               'h1 {\n'
               '  font-size: 32px;\n'
               '  font-weight: bold;\n'
               '  margin-bottom: 8px;\n'
               '  %s\n'
               '}\n'
               '\n'
               'h2 {\n'
               '  font-size: 22px;\n'
               '  font-weight: bold;\n'
               '  margin-bottom: 8px;\n'
               '  %s\n'
               '}\n'
               '\n'
               'h3 { font-size: 18px; }\n'
               'p { font-weight: 300; margin-bottom: 20px; margin-top: 12px; }\n'
               'a { text-decoration: none; }\n'
               'p a { font-weight: 400; }\n'
               '\n'
               'blockquote {\n'
               '  font-size: 1.6em;\n'
               '  border-left: 10px solid #e9e9e9;\n'
               '  margin-bottom: 20px;\n'
               '  padding: 0 0 0 30px;\n'
               '}\n'
               '\n'
               'ul li {\n'
               '  list-style: disc inside;\n'
               '  padding-left: 20px;\n'
               '}\n'
               '\n'
               'ol li {\n'
               '  list-style: decimal inside;\n'
               '  padding-left: 3px;\n'
               '}\n'
               '\n'
               'dl dt {\n'
               '  color: #303030;\n'
               '}\n'
               '\n'
               'footer {\n'
               "  background: transparent url('../images/hr.png') 0 0 no-repeat;\n"
               '  margin-top: 40px;\n'
               '  padding-top: 20px;\n'
               '  padding-bottom: 30px;\n'
               '  font-size: 13px;\n'
               '  color: #aaa;\n'
               '}\n'
               '\n'
               'footer a {\n'
               '  color: #666;\n'
               '}\n'
               'footer a:hover {\n'
               '  color: #444;\n'
               '}\n'
               '\n'
               '\n'
               '/* #Media Queries\n'
               '================================================== */\n'
               '\n'
               '/* Smaller than standard 960 (devices and browsers) */\n'
               '@media only screen and (max-width: 959px) {}\n'
               '\n'
               '/* Tablet Portrait size to standard 960 (devices and browsers) */\n'
               '@media only screen and (min-width: 768px) and (max-width: 959px) {}\n'
               '\n'
               '/* Mobile Landscape Size to Tablet Portrait (devices and browsers) */\n'
               '@media only screen and (min-width: 480px) and (max-width: 767px) {}\n'
               '\n'
               '/* Mobile Portrait Size to Mobile Landscape Size (devices and browsers) */\n'
               '@media only screen and (max-width: 479px) {}\n'
               ) + css_jupyter_blocks

# too small margin bottom: h1 { font-size: 1.8em; color: #1e36ce; margin-bottom: 3px; }

css_rossant = ('\n'
               '/* Style from https://cyrille.rossant.net/theme/css/styles.css */\n'
               '\n'
               'html, button, input, select, textarea {\n'
               '    font-family: "Source Sans Pro", sans-serif;\n'
               '    font-size: 18px;\n'
               '    font-weight: 300;\n'
               '    color: #000;\n'
               '}\n'
               '\n'
               'a { color: #0088cc; text-decoration: none; }\n'
               '\n'
               'a:hover { color: #005580; }\n'
               '\n'
               'code {\n'
               '    /*font-size: .9em;*/\n'
               "    font-family: 'Ubuntu Mono';\n"
               '    padding: 0 .1em;\n'
               '}\n'
               '\n'
               '.highlight pre {\n'
               "    font-family: 'Ubuntu Mono';\n"
               '    font-size: .9em;\n'
               '    padding: .5em;\n'
               '    word-wrap: normal;\n'
               '    overflow: auto;\n'
               '    white-space: pre;\n'
               '}\n'
               '\n'
               'blockquote {\n'
               '    color: #777;\n'
               '    border-left: .5em solid #eee;\n'
               '    padding: 0 0 0 .75em;\n'
               '}\n'
               '\n'
               'h1, h2, h3, h4, h5, h6 {\n'
               '    font-weight: 300;\n'
               '}\n'
               '\n'
               'h1 {\n'
               '    font-size: 2.25em;\n'
               '    margin: 0 0 .1em -.025em;\n'
               '    padding: 0 0 .25em 0;\n'
               '    border-bottom: 1px solid #aaa;\n'
               '}\n'
               '\n'
               '\n'
               'h2 {\n'
               '    color: #555;\n'
               '    font-size: 1.75em;\n'
               '    margin: 1.75em 0 .5em 0;\n'
               '    padding: 0 0 .25em 0;\n'
               '    border-bottom: 1px solid #ddd;\n'
               '}\n'
               '\n'
               'h3 {\n'
               '    margin: 1.25em 0 .75em 0;\n'
               '    font-size: 1.35em;\n'
               '    color: #777;\n'
               '}\n'
               ) + css_jupyter_blocks


def share(code_type,
          url=None,
          buttons=['email', 'facebook', 'google+', 'linkedin',
                   'twitter', 'print'],
          method='simplesharebuttons.com'):
    namespace =  {'url': url}
    s = ''
    if method == 'simplesharebuttons.com':
        if code_type == 'css':
            s +=('\n'
                 '<style type="text/css">\n'
                 '\n'
                 '#share-buttons img {\n'
                 'width: 35px;\n'
                 'padding: 5px;\n'
                 'border: 0;\n'
                 'box-shadow: 0;\n'
                 'display: inline;\n'
                 '}\n'
                 '\n'
                 '</style>\n')

        elif code_type == 'buttons':
            s += ('\n'
                  '<!-- Got these buttons from simplesharebuttons.com -->\n'
                  '<center>\n'
                  '<div id="share-buttons">\n')

            if 'email' in buttons:
                s += ('\n'
                      '    <!-- Email -->\n'
                      '    <a href="mailto:?Subject=Interesting link&amp;Body=I%%20saw%%20this%%20and%%20thought%%20of%%20you!%%20 %(url)s">\n'
                      '        <img src="https://simplesharebuttons.com/images/somacro/email.png" alt="Email" />\n'
                      '    </a>\n') % namespace
            if 'facebook' in buttons:
                s += ('\n'
                      '    <!-- Facebook -->\n'
                      '    <a href="https://www.facebook.com/sharer.php?u=%(url)s" target="_blank">\n'
                      '        <img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" />\n'
                      '    </a>\n') % namespace
            if 'google+' in buttons:
                s +=('\n'
                     '    <!-- Google+ -->\n'
                     '    <a href="https://plus.google.com/share?url=%(url)s" target="_blank">\n'
                     '        <img src="https://simplesharebuttons.com/images/somacro/google.png" alt="Google" />\n'
                     '    </a>\n') % namespace

            if 'linkedin' in buttons:
                s += ('\n'
                      '    <!-- LinkedIn -->\n'
                      '    <a href="https://www.linkedin.com/shareArticle?mini=true&amp;url=%(url)s" target="_blank">\n'
                      '        <img src="https://simplesharebuttons.com/images/somacro/linkedin.png" alt="LinkedIn" />\n'
                      '    </a>\n') % namespace

            if 'twitter' in buttons:
                s += ('\n'
                      '    <!-- Twitter -->\n'
                      '    <a href="https://twitter.com/share?url=%(url)s&amp;name=Interesting link&amp;hashtags=interesting" target="_blank">\n'
                      '        <img src="https://simplesharebuttons.com/images/somacro/twitter.png" alt="Twitter" />\n'
                      '    </a>\n') % namespace

            if 'print' in buttons:
                s += ('\n'
                      '<!-- Print -->\n'
                      '    <a href="javascript:;" onclick="window.print()">\n'
                      '        <img src="https://simplesharebuttons.com/images/somacro/print.png" alt="Print" />\n'
                      '    </a>\n'
                      '\n'
                      '</div>\n') % namespace
        s += '</center>\n'
    return s


def toc2html(html_style, bootstrap=True,
             max_headings=17, # max no of headings in pull down menu
             ):
    global tocinfo  # computed elsewhere

    # level_depth: how many levels that are represented in the toc
    level_depth = int(option('toc_depth=', '-1'))
    if level_depth == -1:  # Use -1 to indicate that doconce decides
        # Compute suitable depth in toc
        if bootstrap:
            # We can have max 17 lines in a dropdown box without a scrollbar
            # so see what is suitable to include in such a box
            level2no = {}
            for item in tocinfo['sections']:
                level = item[1]
                if level in level2no:
                    level2no[level] += 1
                else:
                    level2no[level] = 1
            level_depth = 0
            num_headings = 0  # total no of headings in n levels
            for n in 0, 1, 2, 3:
                if n in level2no:
                    num_headings += level2no[n]
                    if num_headings <= max_headings:
                        level_depth += 1
                    else:
                        break
        else:
            level_depth = 2  # default in a normal toc

    indent = int(option('html_toc_indent=', '3'))
    nested_list = indent == 0

    level_min = tocinfo['highest level']
    if level_depth == 0:  # too many sections? avoid empty navigation...
        level_max = level_min  # include all top levels
    else:
        level_max = level_min + level_depth - 1

    # font types (bootstrap pull-down Contents menu)
    style = 'font-size: 80%;'
    if html_style in ['bootswatch_yeti', 'bootswatch_lumen', 'bootswatch_slate', 'bootswatch_superhero']:
        style = 'font-size: 14px; padding: 4px 15px;'

    ul_class = ' class="nav"' if bootstrap else ''
    toc_html = ''
    uls = 0  # no of active <ul> sublists
    for i in range(len(tocinfo['sections'])):
        title, level, label, href = tocinfo['sections'][i]
        if level > level_max:
            continue
        spaces = '&nbsp;'*(indent*(level - level_min))
        if nested_list and i > 0 and level > tocinfo['sections'][i-1][1]:
            toc_html += '     <ul%s>\n' % ul_class
            uls += 1
        btitle = title = title.strip()
        if level_depth >= 2 and level == level_min:
            btitle = '<b>%s</b>' % btitle  # bold for highest level
        toc_html += '     <!-- navigation toc: --> <li><a href="#%s" style="%s">%s%s</a></li>\n' % (href, style, spaces, btitle)
        if nested_list and i < len(tocinfo['sections'])-1 and \
               tocinfo['sections'][i+1][1] < level:
            toc_html += '     </ul>\n'
            uls -= 1
    # remaining </ul>s
    if nested_list:
        for j in range(uls):
            toc_html += '     </ul>\n'
    if toc_html == '' and tocinfo['sections']:
        errwarn('*** error: no table of contents generated from toc2html - BUG in doconce')
        _abort()
    return toc_html


class CreateApp(object):
    """
    Class for interactive Bokeh plots.
    Written by Fredrik Eikeland Fossan <fredrik.e.fossan@ntnu.no>.
    """
    def __init__(self, plot_info):
        from numpy import linspace
        from bokeh.models.widgets import Slider, TextInput
        from bokeh.models import ColumnDataSource, HBox, VBoxForm

        N = 200
        colors = ['red', 'green', 'indigo', 'orange', 'blue', 'grey', 'purple']
        possible_inputs = ['x_axis_label', 'xrange', 'yrange', 'sliderDict', 'title', 'number_of_graphs']

        y = None
        # Formula given or just Python function?
        if ".py" in plot_info[0]:
            # Python module with compute function
            compute = None
            msg = "from " + plot_info[0][0:-3] + " import compute"
            errwarn('...exec: ' + msg)
            exec(msg)
            import inspect
            arg_names = inspect.getargspec(compute).args
            argString = ""
            for n, arg in enumerate(arg_names):
                argString = argString + arg
                if n != len(arg_names) - 1:
                    argString = argString + ", "
            computeString = "y = compute(" + argString + ")"
            self.computeString = computeString
            self.compute = compute

        self.curve = plot_info[0]
        x_axis_label = None
        y_axis_label = None
        xrange = (0, 10)
        yrange = (0, 10)
        sliderDict = None
        title = None
        number_of_graphs = None
        legend = None
        reverseAxes = False

        self.source = []
        self.sliderList = []

        for n in range(1,len(plot_info)):
            # Update inputs

            exec(plot_info[n].strip())

        self.x = linspace(xrange[0], xrange[1], N)
        self.reverseAxes = reverseAxes
        if sliderDict != None:
            self.parameters = list(sliderDict.keys())

            for n, param in enumerate(self.parameters):
                exec("sliderInstance = Slider(" + sliderDict[param] + ")") # Todo: Fix so exec is not needed
                exec("self.sliderList.append(sliderInstance)") # Todo: Fix so exec is not needed
                # get first value of param
                exec(param + " = "  + 'self.sliderList[n].value') # Todo: Fix so exec is not needed

        # Set up plot
        from bokeh.plotting import Figure
        assert len(xrange) == 2; assert len(yrange) == 2
        self.plot = Figure(
            plot_height=400, plot_width=400, title=title,
            tools="crosshair,pan,reset,resize,save,wheel_zoom",
            x_range=xrange, y_range=yrange)
        self.plot.xaxis.axis_label = x_axis_label
        self.plot.yaxis.axis_label = y_axis_label
        # generate the first curve:
        x = self.x
        if ".py" in plot_info[0]:
            exec(self.computeString)
            errwarn('...exec: ' + self.computeString)
        else:
            exec(plot_info[0]) #  execute y = f(x, params)
            errwarn('...exec: ' + plot_info[0])
        #print 'XXX', y  # nan for womersley test!

        if type(y) is list:
            if legend == None:
                legend = [legend]*len(y)
            for n in range(len(y)):

                if self.reverseAxes:
                    x_plot = y[n]
                    y_plot = self.x
                else:
                    x_plot = self.x
                    y_plot = y[n]
                self.source.append(
                    ColumnDataSource(data=dict(x=x_plot, y=y_plot)))
                self.plot.line(
                    'x', 'y',
                    source=self.source[n], line_width=3,
                    line_color=colors[n], legend=legend[n])
        else:
            if self.reverseAxes:
                x_plot = y
                y_plot = self.x
            else:
                x_plot = self.x
                y_plot = y
            self.source.append(
                ColumnDataSource(data=dict(x=x_plot, y=y_plot)))
            self.plot.line(
                'x', 'y',
                source=self.source[0], line_width=3, legend=legend)

    def update_data(self, attrname, old, new):
        # Get the current slider values
        y = None
        x = self.x
        for n, param in enumerate(self.parameters):
            exec(param + " = "  + 'self.sliderList[n].value')
        # generate the new curve:
        if ".py" in self.curve:
            compute = self.compute
            exec(self.computeString) #  execute y = compute(x, params)
            errwarn('...exec: ' + self.computeString)
        else:
            exec(self.curve) #  execute y = f(x, params)
            errwarn('...exec: ' + self.curve)

        if type(y) is list:
            for n in range(len(y)):
                if self.reverseAxes:
                    x_plot = y[n]
                    y_plot = self.x
                else:
                    x_plot = self.x
                    y_plot = y[n]
                self.source[n].data = dict(x=x_plot, y=y_plot)
        else:
            if self.reverseAxes:
                x_plot = y
                y_plot = x
            else:
                x_plot = x
                y_plot = y
            self.source[0].data = dict(x=x_plot, y=y_plot)


def embed_IBPLOTs(filestr, format):
    """
    Replace all IBPLOT tags by proper script and bokeh code.
    Written by Fredrik Eikeland Fossan with edits by H. P. Langtangen.
    """
    from bokeh.document import Document
    from bokeh.client import push_session
    from bokeh.embed import autoload_server
    from bokeh.models import HBox, VBoxForm

    document = Document()
    session = push_session(document)

    # Find all IBPLOT tags and store them
    IBPLOT_tags = []
    IBPLOT_lines = []
    for line in filestr.splitlines():
        if line.startswith('IBPLOT:'):
            errwarn('*** found IBPLOT command\n    ' + line)
            try:
                plot_info = line[8:-1].split(';')
            except Exception:
                plot_info = []
            if not plot_info:
                errwarn('*** error: inline plot specification\n    %s\ncould not be split wrt ;' % line)
                _abort()

            new_plot_info = []
            n = 0
            for element in plot_info:
                if not element:
                    continue
                if element[0] ==' ':
                    element = element[1:]
                if element[-1] ==' ':
                    element = element[:-1]
                if element[-1] == ']' and n == len(plot_info) -1:
                    element = element[:-1]
                new_plot_info.append(element)
                n += 1
            IBPLOT_tags.append(new_plot_info)
            IBPLOT_lines.append(line)

    appLayoutList = []
    for app_info in IBPLOT_tags:
        app = CreateApp(app_info)
        for w in app.sliderList:
            w.on_change('value', app.update_data)
        inputs = VBoxForm(children=app.sliderList)
        layout = HBox(children=[inputs, app.plot], width=800)
        document.add_root(layout)
        appLayoutList.append(layout)

    # Replace each IBPLOT tag by proper HTML code
    app_no = 0
    for tags, line in zip(IBPLOT_tags, IBPLOT_lines):
        text = autoload_server(appLayoutList[app_no], session_id=session.id)
        if format == 'html':
            filestr = filestr.replace(line, '<!--\n%s\n-->\n' % line + text)
        else:
            filestr = filestr.replace(line, '')
        app_no += 1

    document.add_root(layout)
    return filestr, session


def embed_newcommands(filestr):
    from .expand_newcommands import process_newcommand
    newcommands_files = list(
        sorted([name
                for name in glob.glob('newcommands*.tex')
                if not name.endswith('.p.tex')]))
    newcommands = ''
    for filename in newcommands_files:
        f = open(filename, 'r')
        text = ''
        for line in f.readlines():
            if line.startswith(r'\newcommand') or \
               line.startswith(r'\renewcommand'):
                pattern, dummy = process_newcommand(line)
                m = re.search(pattern, filestr)
                if m:
                    text += line
        text = text.strip()
        if text:
            newcommands += '\n<!-- %s -->\n' % filename + '$$\n' + text \
                           + '\n$$\n\n'
    return newcommands


def mathjax_header(filestr):
    newcommands = embed_newcommands(filestr)
    if option('siunits'):
        siunitx1 = '\nMathJax.Ajax.config.path["siunitx"] = "https://rawgit.com/burnpanck/MathJax-siunitx/master/";'
        siunitx2 = ', "[siunitx]/siunitx.js"'
    else:
        siunitx1 = siunitx2 = ''

    mathjax_script_tag = ('\n\n'
                          '<script type="text/x-mathjax-config">%s\n'
                          'MathJax.Hub.Config({\n'
                          '  TeX: {\n'
                          '     equationNumbers: {  autoNumber: "AMS"  },\n'
                          '     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js", "color.js"%s]\n'
                          '  }\n'
                          '});\n'
                          '</script>\n'
                          '<script type="text/javascript" async\n'
                          ' src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML">\n'
                          '</script>\n') % (siunitx1, siunitx2)
    #<meta tag is valid only in html head anyway, so this was removed:
    #<!-- Fix slow MathJax rendering in IE8 -->
    #<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7">
    latex = '\n\n' + mathjax_script_tag + newcommands + '\n\n'
    return latex


def html_verbatim(m):
    code = m.group('subst')
    begin = m.group('begin')
    end = m.group('end')
    # Must quote special characters
    code = code.replace('&', '&amp;')
    code = code.replace('<', '&lt;')
    code = code.replace('>', '&gt;')
    code = code.replace('"', '&quot;')
    return r'%(begin)s<code>%(code)s</code>%(end)s' % vars()


def html_code(filestr, code_blocks, code_block_types,
              tex_blocks, format):
    """Replace code and LaTeX blocks by html environments."""

    html_style = option('html_style=', '')
    pygm, pygm_style = get_pygments_style(code_block_types)

    filestr = insert_code_blocks(filestr, code_blocks, format, complete_doc=True, remove_hid=False)

    code_style = pygm_style
    filestr = jupyter_execution.process_code_blocks(filestr, code_style, format)

    # Remove all <p></p> between </div> and <div> ?
    filestr = re.sub(r'</div>[\n]+<p></p>[\n]+(<!--.*-->[\n]{1})*[\n]+', r'\1', filestr)

    # Inline math cannot have x<z<w as this is interpreted as tags
    # and becomes invisible
    filestr2 = re.sub(r'<!--(.+?)-->', '', filestr)  # remove comments first
    inline_math = re.findall(r'\\\( (.+?) \\\)', filestr2, flags=re.DOTALL)
    for m in inline_math:
        if '<' in m:
            m_new = m
            m_new = re.sub(r'([^ ])<', '\g<1> <', m_new)
            m_new = re.sub(r'<([^ ])', '< \g<1>', m_new)
            if m_new != m:
                errwarn('*** warning: inline math in HTML must have space around <:')
                errwarn('    %s  ->  %s' % (m, m_new))
            filestr = filestr.replace(r'\( %s \)' % m, r'\( %s \)' % m_new)
    for i in range(len(tex_blocks)):
        if re.search(r'[^ {}]<', tex_blocks[i]) or re.search(r'<[^ {}]', tex_blocks[i]):
            errwarn('*** warning: math block in HTML must have space around <:')
            errwarn(tex_blocks[i])
            tex_blocks[i] = re.sub(r'([^ {}])<', '\g<1> <', tex_blocks[i])
            tex_blocks[i] = re.sub(r'<([^ {}])', '< \g<1>', tex_blocks[i])
            errwarn('    changed to')
            errwarn(tex_blocks[i])
            print()

    if option('wordpress'):
        # Change all equations to $latex ...$\n
        replace = [
            (r'\[', '$latex '),
            (r'\]', ' $\n'),
            (r'\begin{equation}', '$latex '),
            (r'\end{equation}', ' $\n'),
            (r'\begin{equation*}', '$latex '),
            (r'\end{equation*}', ' $\n'),
            (r'\begin{align}', '$latex '),
            (r'\end{align}', ' $\n'),
            (r'\begin{align*}', '$latex '),
            (r'\end{align*}', ' $\n'),
            ]
        for i in range(len(tex_blocks)):
            if '{align' in tex_blocks[i]:
                tex_blocks[i] = tex_blocks[i].replace('&', '')
                tex_blocks[i] = tex_blocks[i].replace('\\\\', ' $\n\n$latex ')
            for from_, to_ in replace:
                tex_blocks[i] = tex_blocks[i].replace(from_, to_)
            tex_blocks[i] = re.sub(r'label\{.+?\}', '', tex_blocks[i])

        # Newlines in HTML become real newlines on wordpress.com,
        # remove newlines between words (but don't merge with code
        # blocks and don't merge lines starting with !),
        # word and link, word and emphasize, etc.
        # Technique: add \n and remove it if the line qualifies for
        # merging with the next
        lines = filestr.splitlines()
        ignorelines = ['^![be]', '^\d+ <<<!!(MATH|CODE)',]
        acceptlines_next = ['^[(A-Za-z0-9]', '^ +ref\{',
                            '^ *(<a +href=|<em>|<b>|<code>|\$latex |<font)',]
        acceptlines_present = ['([A-Za-z0-9.,;:?)]|</a>|</em>|</b>|</code>|\$|</font>) *$',]
        for i in range(len(lines)-1):
            #errwarn('Line:', i, lines[i])
            lines[i] += '\n'
            # Ignore merging this line with the next?
            ignore = False
            for pattern in ignorelines:
                if re.search(pattern, lines[i]):
                    ignore = True
                    #errwarn('This is an ignore line ' + pattern)
                    break
            if not ignore:
                # Next line must not be an ignore line
                ignore = False
                for pattern in ignorelines:
                    if re.search(pattern, lines[i+1]):
                        ignore = True
                        #errwarn('Next line is an ignore line ' + pattern)
                        break
                # Present line must be an accept line
                accept_present = False
                for pattern in acceptlines_present:
                    if re.search(pattern, lines[i]):
                        accept_present = True
                        #errwarn('Present line is an accept line ' + pattern)
                        break
                # Next line must be an accept line
                accept_next = False
                for pattern in acceptlines_next:
                    if re.search(pattern, lines[i+1]):
                        accept_next = True
                        #errwarn('Next line is an accept line', pattern)
                        break
                if (not ignore) and accept_present and accept_next:
                    # Line ends in correct character
                    # Merge with next line
                    lines[i] = lines[i].rstrip() + ' '
                    #errwarn('Merge!')
        filestr = ''.join(lines)
        # Must do the removal of \n in <li>.+?</li> later when </li> is added

    for i in range(len(tex_blocks)):
        """
        Not important - the problem was repeated label.
        if 'begin{equation' in tex_blocks[i]:
            # Make sure label is on a separate line inside begin{equation}
            # environments (insert \n after labels with something before)
            tex_blocks[i] = re.sub('([^ ]) +label\{', '\g<1>\nlabel{',
                                   tex_blocks[i])
        """
        if 'label' in tex_blocks[i]:
            # Fix label -> \label in tex_blocks
            tex_blocks[i] = tex_blocks[i].replace(r' label{', r' \label{')
            tex_blocks[i] = re.sub(r'^label\{', r'\\label{', tex_blocks[i],
                                   flags=re.MULTILINE)

    debugpr('File before call to insert_code_blocks (format html):', filestr)
    # I might have to move stuff up here ..
    filestr = insert_tex_blocks(filestr, tex_blocks, format, complete_doc=True)
    debugpr('File after call to insert_code_and tex (format html):', filestr)

    needs_online_python_tutor = any(x.startswith('pyoptpro') for x in code_block_types)
    if pygm or needs_online_python_tutor:
        c = re.compile(r'^!bc(.*?)\n', re.MULTILINE)
        filestr = c.sub(r'\n\n', filestr)
        filestr = re.sub(r'!ec\n', r'\n', filestr)
        debugpr('After replacement of !bc and !ec (pygmentized code):', filestr)
    else:
        c = re.compile(r'^!bc(.*?)\n', re.MULTILINE)
        # <code> gives an extra line at the top unless the code starts
        # right after (do that - <pre><code> might be important for many
        # HTML/CSS styles).
        filestr = c.sub(r'<!-- begin verbatim block \g<1>-->\n<pre><code>', filestr)
        filestr = re.sub(r'!ec\n',
                r'</code></pre>\n<!-- end verbatim block -->\n',
                filestr)
        # Note: ccq envir is not put in blockquote tags, only if
        # pygments is used (would need to first substitute !bc ccq, but
        # !ec poses problems - drop this for plan pre/code tags since
        # pygments is the dominating style)

    if option('wordpress'):
        MATH_TYPESETTING = 'WordPress'
    else:
        MATH_TYPESETTING = 'MathJax'
    c = re.compile(r'^!bt *\n', re.MULTILINE)
    m1 = c.search(filestr)
    # INLINE_TAGS['math'] won't work since we have replaced
    # $...$ by \( ... \)
    pattern = r'\\\( .+? \\\)'
    m2 = re.search(pattern, filestr)
    math = bool(m1) or bool(m2)

    if MATH_TYPESETTING == 'MathJax':
        # LaTeX blocks are surrounded by $$
        filestr = re.sub(r'!bt *\n', '$$\n', filestr)
        # Add more space before and after equations
        #filestr = re.sub(r'!bt *\n', '&nbsp;<br>&nbsp;<br>\n$$\n', filestr)
        # (add extra newline after $$ since Google's blogspot HTML
        # needs that line to show the math right - otherwise it does not matter)
        filestr = re.sub(r'!et *\n', '$$\n\n', filestr)
        #filestr = re.sub(r'!et *\n', '$$\n&nbsp;<br>\n\n', filestr)

        # Remove inner \[..\] from equations $$ \[ ... \] $$
        filestr = re.sub(r'\$\$\s*\\\[', '$$', filestr)
        filestr = re.sub(r'\\\]\s*\$\$', '$$', filestr)
        # Equation references (ref{...}) must be \eqref{...} in MathJax
        # (note: this affects also (ref{...}) syntax in verbatim blocks...)
        filestr = re.sub(r'\(ref\{(.+?)\}\)', r'\\eqref{\g<1>}', filestr)

    elif MATH_TYPESETTING == 'WordPress':
        filestr = re.sub(r'!bt *\n', '\n', filestr)
        filestr = re.sub(r'!et *\n', '\n', filestr)
        # References are not supported
        # (note: this affects also (ref{...}) syntax in verbatim blocks...)
        filestr = re.sub(r'\(ref\{(.+?)\}\)',
                         r'<b>(REF to equation \g<1> not supported)</b>', filestr)
    else:
        # Plain verbatim display of LaTeX syntax in math blocks
        filestr = c.sub(r'<blockquote><pre>\n', filestr)
        filestr = re.sub(r'!et *\n', r'</pre></blockquote>\n', filestr)

    # --- Final fixes for html format ---

    # Replace old-fashion <a name=""></a> anchors with id=""
    if option('html_style=', '').startswith('boots'):
        filestr = re.sub(r'<h(\d)(.*?)>(.+?) <a name="(.+?)"></a>',
                     r'<h\g<1>\g<2> id="\g<4>" class="anchor">\g<3>', filestr)
        # (use class="anchor" such that we can easily set the position of
        # headings in e.g. bootstrap CSS; use :_id to make h1/h2 identifier different)
    filestr = re.sub(r'<h(\d)(.*?)>(.+?) <a name="(.+?)"></a>',
                     r'<h\g<1>\g<2> id="\g<4>">\g<3>', filestr)
    filestr = re.sub(r'<a name="([^"]+)"></a>',
                     r'<div id="\g<1>"></div>', filestr)

    # Add MathJax script if math is present (math is defined right above)
    if math and MATH_TYPESETTING == 'MathJax':
        latex = mathjax_header(filestr)
        if '<body>' in filestr:
            # Add MathJax stuff after <body> tag
            filestr = filestr.replace('<body>\n', '<body>' + latex)
        else:
            # Add MathJax stuff to the beginning
            filestr = latex + filestr

    # Copyright
    from .common import get_copyfile_info
    cr_text = get_copyfile_info(filestr, format=format)
    if cr_text is not None:
        filestr = filestr.replace('Copyright COPYRIGHT_HOLDERS',
                                  cr_text)

    # Add </li> in lists
    cpattern = re.compile('<li>(.+?)(\s+)<li>', re.DOTALL)
    def find_list_items(match):
        """Return replacement from match of <li> tags."""
        # Does the match run out of the list?
        if re.search(r'</?(ul|ol)>', match.group(1)):
            return '<li>' + match.group(1) + match.group(2)
        else:
            return '<li>' + match.group(1) + '</li>' + match.group(2)

    # cpattern can only detect every two list item because it cannot work
    # with overlapping patterns. Remedy: have two <li> to avoid overlap,
    # fix that after all replacements are done.
    filestr = filestr.replace('<li>', '<li><li>')
    filestr = cpattern.sub(find_list_items, filestr)
    # Fix things that go wrong with cpattern: list items that go
    # through end of lists over to next list item.
    cpattern = re.compile('<li>(.+?)(\s+)(</?ol>|</?ul>)', re.DOTALL)
    filestr = cpattern.sub('<li>\g<1></li>\g<2>\g<3>', filestr)
    filestr = filestr.replace('<li><li>', '<li>')  # fix
    if option('wordpress'):
        # Remove \n from <li>...</li>
        pattern = r'<li>.+?</li>'
        filestr = re.sub(pattern, lambda m: m.group().replace('\n', ' '),
                         filestr, flags=re.DOTALL)

    # Find all URLs to files (non http, ftp)
    pattern = '<a href=' + _linked_files
    files = re.findall(pattern, filestr)
    for f, dummy in files:
        if not (f.startswith('http') or f.startswith('ftp') or \
           f.startswith('file:')):
            add_to_file_collection(f)

    # Change a href links so they open URLs in new windows?
    if option('html_links_in_new_window'):
        filestr = filestr.replace('target="_self"', 'target="_blank"')

    # Add info about the toc (for construction of navigation panels etc.).
    # Just dump the tocinfo dict so that we can read it and take eval
    # later
    import pprint
    global tocinfo
    if tocinfo is not None and isinstance(tocinfo, dict):
        toc = '\n<!-- tocinfo\n%s\nend of tocinfo -->\n\n' % \
              pprint.pformat(tocinfo)

        if '<body>' in filestr:
            # toc before the <body> tag
            filestr = filestr.replace('<body>\n', toc + '<body>\n')
        else:
            # Insert tocinfo at the beginning
            filestr = toc + filestr

    # Add header from external template
    template = option('html_template=', default='')
    if html_style == 'vagrant':
        errwarn('*** warning: --html_style=vagrant is deprecated,')
        errwarn('    just use bootstrap as style and combine with')
        errwarn('    template from bundled/html_styles/style_vagrant')
        html_style == 'bootstrap'

    # Make toc for navigation
    toc_html = ''
    if html_style.startswith('boots'):
        toc_html = toc2html(html_style, bootstrap=True, max_headings=10000)
        # Fix
        toc_html = re.sub(r'id="table_of_contents">', 'id="table_of_contents" class="anchor">', toc_html)
    elif html_style in ('solarized',):
        toc_html = toc2html(html_style, bootstrap=False)
    # toc_html lacks formatting, run some basic formatting here
    tags = 'emphasize', 'bold', 'math', 'verbatim', 'colortext'
    # drop URLs in headings?
    from . import common
    for tag in tags:
        toc_html = re.sub(INLINE_TAGS[tag],
                          INLINE_TAGS_SUBST[format][tag],
                          toc_html)

    if template:
        title = ''
        date = ''

        header = '<!-- document title -->' in filestr  # will the html file get a header?
        if header:
            errwarn(('*** warning: TITLE may look strange with a template -\n'
                     '             it is recommended to comment out the title: #TITLE:'))
            pattern = r'<center>[\s]*<h1>(.+?)</h1>[\n]</center>  <!-- document title -->'
            m = re.search(pattern, filestr)
            if m:
                title = m.group(1).strip()

        authors = '<!-- author(s):' in filestr
        if authors:
            errwarn(('\n'
                     '*** warning: AUTHOR may look strange with a template -\n'
                     ' it is recommended to comment out all authors: #AUTHOR.\n'
                     ' Usually better to hardcode authors in a footer in the template.'))

        # Extract title
        if title == '':
            # The first section heading or a #TITLE: ... line becomes the title
            pattern = r'<!--\s+TITLE:\s*(.+?) -->'
            m = re.search(pattern, filestr)
            if m:
                title = m.group(1).strip()
                filestr = re.sub(pattern, '\n<h1>%s</h1>\n' % title, filestr)
            else:
                # Use the first ordinary heading as title
                m = re.search(r'<h\d id=.+?">(.+?)<', filestr)
                if m:
                    title = m.group(1).strip()

        # Extract date
        pattern = r'<center>[\n]<h\d>(.+?)</h\d>[\n]</center>\s*<!-- date -->'
        m = re.search(pattern, filestr)
        if m:
            date = m.group(1).strip()
            # remove date since date is in template
            filestr = re.sub(pattern, '', filestr)

        # Load template file
        try:
            f = open(template, 'r'); template = f.read(); f.close()
        except IOError as e:
            errwarn('*** error: could not find template "%s"' % template)
            errwarn(e)
            _abort()

        # Check that template does not have "main content" begin and
        # end lines that may interfere with the automatically generated
        # ones in DocOnce (may destroy the split_html command)
        m = re.findall(r'(<!-- %s+ main content %s+)' % (globals.main_content_char, globals.main_content_char), template)
        if m:
            errwarn('*** error: template contains lines that may interfere')
            errwarn('    with markers that doconce inserts - remove these')
            for line in m:
                errwarn(line)
            _abort()

        # template can only have slots for title, date, main, table_of_contents
        template = latin2html(template) # code non-ascii chars
        # replate % by %% in template, except for %(title), %(date), %(main),
        # etc which are the variables we can plug into the template.
        # The keywords list holds the names of these variables (can define
        # more than we actually use).
        keywords = ['title', 'date', 'main', 'table_of_contents']
        for keyword in keywords:
            from_ = '%%(%s)s' % keyword
            to_ = '@@@%s@@@' % keyword.upper()
            template = template.replace(from_, to_)
        template = template.replace('%', '%%')
        for keyword in keywords:
            to_ = '%%(%s)s' % keyword
            from_ = '@@@%s@@@' % keyword.upper()
            template = template.replace(from_, to_)

        variables = {keyword: '' for keyword in keywords} # init
        variables.update({'title': title, 'date': date, 'main': filestr,
                          'table_of_contents': toc_html})
        if '%(date)s' in template and date == '':
            errwarn('*** warning: template contains date (%(date)s)')
            errwarn('    but no date is specified in the document')
        filestr = template % variables

    if html_style.startswith('boots'):
        # Change chapter headings to page
        filestr = re.sub(r'<h1>(.+?)</h1> <!-- chapter heading -->',
                         '<h1 class="page-header">\g<1></h1>', filestr)
    else:
        filestr = filestr.replace(' <!-- chapter heading -->', ' <hr>')
    if html_style.startswith('boots'):
        # Insert toc if toc
        if '***TABLE_OF_CONTENTS***' in filestr:
            contents = globals.locale_dict[globals.locale_dict['language']]['Contents']
            try:
                filestr = filestr.replace('***TABLE_OF_CONTENTS***',
                                          toc_html)
                filestr = filestr.replace('***CONTENTS_PULL_DOWN_MENU***',
                                          contents)
            except UnicodeDecodeError:
                filestr = filestr.replace('***TABLE_OF_CONTENTS***',
                                          toc_html)
                filestr = filestr.replace('***CONTENTS_PULL_DOWN_MENU***',
                                          contents)

        jumbotron = option('html_bootstrap_jumbotron=', 'on')
        if jumbotron != 'off':
            # Fix jumbotron for title, author, date, toc, abstract, intro
            pattern = r'(^<center>[\n]<h1>[^\n]+</h1>[\n]</center>' \
                      r'[^\n]+document title.+?)' \
                      r'(^<!-- !split -->|^<h[123] id="|^<center>[\n]<h1 id="|^<div class="page-header">)'
            # Exclude lists (not a good idea if they are part of the intro...)
            #pattern = r'(^<center>[\n]<h1>[^\n]+</h1>[\n]</center>' \
            #          r'[^\n]+document title.+?)' \
            #          r'(^<!-- !split -->|^<h[123]>[^\n]+?<a name=[^\n]+?</h[123]>|^<div class="page-header">|<[uo]l>)'
            m = re.search(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
            if m:
                # If the user has a !split in the beginning, insert a button
                # to click (typically bootstrap design).
                # Also make the title h2 instead of h1 since h1 is REALLY
                # big in the jumbotron.
                core = m.group(1)
                rest = m.group(2)
                if jumbotron == 'h2':
                    core = core.replace('h1>', 'h2>')
                button = '<!-- potential-jumbotron-button -->' \
                         if '!split' in m.group(2) else ''
                text = '<div class="jumbotron">\n' + core + \
                       button + '\n</div> <!-- end jumbotron -->\n\n' + rest
                # re.sub might be problematic for large amounts of text as
                # group symbols in text, like $1,\ 2,\ 3$ may fool the regex
                # subst. Since we have m.group() we can use str.replace
                #filestr = re.sub(pattern, text, filestr, flags=re.DOTALL|re.MULTILINE)
                filestr = filestr.replace(m.group(), text)
                # Last line may give trouble if there is no !split
                # before first section and the document is long...

        # Fix slidecells? Just a start...this is hard...
        if '<!-- !bslidecell' in filestr:
            filestr = process_grid_areas(filestr)


    if MATH_TYPESETTING == 'WordPress':
        # Remove all comments for wordpress.com html
        pattern = re.compile('<!-- .+? -->', re.DOTALL)
        filestr = re.sub(pattern, '', filestr)

    # Add social media sharing buttons
    url = option('html_share=', None)
    # --html_share=https://mysite.com/specials,twitter,facebook,linkedin
    if url is not None:
        if ',' in url:
            words = url.split(',')
            url = words[0]
            buttons = words[1:]
            code = share(code_type='buttons', url=url, buttons=buttons)
        else:
            code = share(code_type='buttons', url=url)
        filestr = re.sub(r'^</body>\n', code + '\n\n' + '</body>\n',
                         filestr, flags=re.MULTILINE)

    # Add links for Bokeh plots
    if 'Bokeh.logger.info(' in filestr:
        bokeh_version = '0.9.0'
        head = ('\n'
                '<!-- Tools for embedded Bokeh plots -->\n'
                '<link rel="stylesheet"\n'
                '      href="https://cdn.pydata.org/bokeh/release/bokeh-%(bokeh_version)s.min.css"\n'
                '      type="text/css" />\n'
                '<script type="text/javascript"\n'
                '	src="https://cdn.pydata.org/bokeh/release/bokeh-%(bokeh_version)s.min.js">\n'
                '</script>\n'
                '<script type="text/javascript">\n'
                '  Bokeh.set_log_level("info");\n'
                '</script>\n'
                ) % vars()
        filestr = re.sub(r'^</head>\n', head + '\n\n</head>\n',
                         filestr, flags=re.MULTILINE)

    # Add exercise logo
    html_style = option('html_style=', 'blueish')
    icon = option('html_exercise_icon=', 'None')
    icon_width = option('html_exercise_icon_width=', '100')
    if icon.lower() != 'none':
        if icon == 'default':
            if html_style == 'solarized' or html_style == 'bloodish':
                icon = 'question_black_on_gray.png'
                #icon = 'question_white_on_black.png'
            elif html_style.startswith('blue'):
                #icon = 'question_blue_on_white1.png'
                #icon = 'question_white_on_blue_tiny.png'
                icon = 'question_blue_on_white2.png'
            else:
                icon = 'exercise1.svg'
        icon_path = 'RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/' + icon
        pattern = r'(<h3>(Exercise|Project|Problem) \d+:.+</h3>)'
        filestr = re.sub(pattern, '\g<1>\n\n<img src="%s" width=%s align="right">\n' % (icon_path, icon_width), filestr)

    filestr = html_remove_whitespace(filestr)

    return filestr


def format_code_html(code_block, code_block_type, code_style, postfix='', execute=True, show='format'):
    """Process the block to output the formatted code. Also
    output booleans to trigger execution and rendering of the block

    The output `show` is one of ['format','pre','hide','text','output','html'].
    The output `code_style` is a style e.g. from `--pygments_html_style`.
    The output `execute` is a boolean indicating whether
    the code should be executed.
    :param str code_block: code
    :param str code_block_type: block type e.g. 'pycod-e'
    :param code_style: any style from e.g. pygments
    :return: formatted_code, comment, execute, show
    :rtype: Tuple[str, str, bool, str]
    """
    formatted_code = ''
    comment = ''
    if show == 'hide':
        return formatted_code, comment, execute, show
    LANG, codetype, postfix = code_block_type
    # Format code based on `show` and its code type
    if LANG == 'pyopt' and codetype == 'pro':
        formatted_code = online_python_tutor(code_block, return_tp='iframe')
        execute = False
    elif LANG == 'pysc' and codetype == 'pro':
        # Wrap Sage Cell code around the code
        # https://github.com/sagemath/sagecell/blob/master/doc/embedding.rst
        formatted_code = html_sagecell % code_block
        execute = False
    elif code_style != 'off':
        # Syntax highlighting with pygments
        # Get the code block's language
        language_ = 'text'
        if LANG in envir2syntax:
            language_ = envir2syntax[LANG]
        elif LANG in get_legal_pygments_lexers():
            language_ = LANG
        # Typeset code with pygments
        lexer = get_lexer_by_name(language_)
        linenos = option('pygments_html_linenos')
        formatter = HtmlFormatter(linenos=linenos,
                                  noclasses=True,
                                  style=code_style)
        formatted_code = highlight(code_block, lexer, formatter)
        if postfix == '-h':
            # Embed some jquery JavaScript for a show/hide button
            hash = str(uuid.uuid4())[:4]
            formatted_code = html_toggle_btn % vars()

        # Fix som ugly html code: error boxes
        formatted_code = re.sub(r'<span style="border: 1px .*?">(.+?)</span>', '\g<1>', formatted_code)
        indent = ''
        m = re.search(r'^( +).*><pre ', formatted_code, re.MULTILINE)
        if m:
            indent = m.groups()[0]
        formatted_code = re.sub(r'><pre ', r'>\n'+indent+'  <pre ', formatted_code)
        formatted_code = re.sub(r'</pre><', r'</pre>\n'+indent+'<', formatted_code)
        formatted_code = re.sub(r'<span></span>', r'', formatted_code)

        # Write a comment before the rendering with a description of the rendering
        comment = '\n<!-- code=%s (!bc %s%s%s) ' % (language_, LANG, codetype, postfix)
        comment += 'typeset with pygments style "%s%s" -->\n' % (code_style, postfix)
    else:
        # Substitute & first, otherwise & in &quot; becomes &amp;quot;
        formatted_code = code_block.replace('&', '&amp;')
        formatted_code = code_block.replace('<', '&lt;')
        formatted_code = code_block.replace('>', '&gt;')
        formatted_code = code_block.replace('"', '&quot;')
        execute = False
        show = 'pre'
    return formatted_code, comment, execute, show


def format_cell_html(formatted_code, formatted_output, execution_count, show):
    """Format a code cell and its output

    This function is referenced by `format_cell` in jupyter_execution.py.
    :param str formatted_code: formatted code
    :param str formatted_output: formatted block
    :param str execution_count: execution count in the rendered cell
    :param str show: how to format the output e.g. 'format','pre','hide','text','output'
    :return: formatted_output
    :rtype: str
    """
    if not show:
        pass
    elif show == 'hide':
        pass
    elif show == 'pre':
        formatted_output = '<pre>' + formatted_code + formatted_output + '</pre>'
    elif show == 'format':
        # Render of the code and code output and indent
        # the whole cell (input and output) as in jupyter notebook
        formatted_output = html_cell % (formatted_code,
                                        formatted_output)
    elif show == 'text':
        # Render of the code as text in a cell input
        formatted_output = html_cell_wrap + \
                           html_cell_code % (formatted_code) + \
                           '</div>'
    elif show == 'output':
        # Render as code output
        formatted_output = html_cell_wrap + \
                           html_cell_output % formatted_output + \
                           '</div>'
    else:
        errwarn('*** error: show=%s not recognized' % str(show))
        _abort()
    return formatted_output


def html_remove_whitespace(filestr):
    """Reduce redunant newlines and empty <p></p> tags

    Eliminate any <p> that goes with blanks up to <p> or a section heading
    :param str filestr: text string
    :return: filestr
    :rtype: str
    """
    #pattern = r'<p>\s+(?=<p>|<p id=|<[hH]\d[^>]*>)' #old: stray <p> should not be present
    pattern = r'<p>\s*</p>'
    filestr = re.sub(pattern, '', filestr)
    # Extra blank before section heading
    pattern = r'(?<!center>)\s+(?=^<[hH]\d[^>]*>)'
    filestr = re.sub(pattern, '\n', filestr, flags=re.MULTILINE)
    # Elimate <p> before equations $$ and before lists
    filestr = re.sub(r'<p>\s*</p>\s+(\$\$|<ul>|<ol>)', r'\g<1>', filestr)
    # Eliminate <p> after </h1>, </h2>, etc.
    #filestr = re.sub(r'(</[hH]\d[^>]*>)\s+<p>', '\g<1>\n', filestr)
    #bad side effect in deck.js slides
    # Remove remaining too much space before <p>
    filestr = re.sub(r'\s{3,}<p>', r'\n\n<p>', filestr)
    # Remove repeated <p></p>'s
    filestr = re.sub(r'(\s+<p>\s*</p>){2,}', r'\g<1>', filestr)
    # Remove <p> + space up to </endtag>
    filestr = re.sub(r'<p>\s+(?=</)', r'<p>\n', filestr)
    return filestr


def process_grid_areas(filestr):
    # Extract all cell areas
    pattern = r'(^<!-- +begin-grid-area +-->(.+?)^<!-- +end-grid-area +-->)'
    cell_areas = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    # Work with each cell area
    for full_text, internal in cell_areas:
        cell_pos = [(int(p[0]), int(p[1])) for p in
                    re.findall(r'<!-- !bslidecell +(\d\d)', internal)]
        if cell_pos:
            # Find the table size
            num_rows    = max([p[0] for p in cell_pos]) + 1
            num_columns = max([p[1] for p in cell_pos]) + 1
            table = [[None]*(num_columns) for j in range(num_rows+1)]
            # Grab the content of each cell
            cell_pattern = r'(<!-- !bslidecell +(\d\d) *[.0-9 ]*?-->(.+?)<!-- !eslidecell -->)'
            cells = re.findall(cell_pattern, internal,
                               flags=re.DOTALL|re.MULTILINE)
            # Insert individual cells in table
            for cell_envir, pos, cell_text in cells:
                table[int(pos[0])][int(pos[1])] = cell_text
            # Construct new HTML text by looping over the table
            # (note that the input might have the cells in arbitrary
            # order while the output is traversed in correct cell order)
            new_text = '<div class="row"> <!-- begin cell row -->\n'
            for c in range(num_columns):
                new_text += '  <div class="col-sm-4">\n    <p> <!-- subsequent paragraphs come in larger fonts, so start with a paragraph -->'
                for r in range(num_rows):
                    new_text += table[r][c]
                new_text += '  </div> <!-- column col-sm-4 -->\n'
            new_text += '</div> <!-- end cell row -->\n'
            filestr = filestr.replace(full_text, new_text)
    return filestr


def interpret_bokeh_plot(text):
    """Find script and div tags in a Bokeh HTML file."""
    # Structure of the file
    """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Damped vibrations</title>
    
            <link rel="stylesheet" href="https://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.css" type="text/css" />
            <script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.js"></script>
            <script type="text/javascript">
                Bokeh.set_log_level("info");
            </script>
    
            <script type="text/javascript">
                Bokeh.$(function() {
                    var modelid = "af0bc57e-f573-4a7f-be80-504fab00b254";
                    var modeltype = "PlotContext";
                    var elementid = "4a9dd7a1-f20c-4fe5-9917-13d172ef031a";
                    Bokeh.logger.info("Realizing plot:")
                    Bokeh.logger.info(" - modeltype: PlotContext");
                    Bokeh.logger.info(" - modelid: af0bc57e-f573-4a7f-be80-504fab00b254");
                    Bokeh.logger.info(" - elementid: 4a9dd7a1-f20c-4fe5-9917-13d172ef031a");
                    var all_models = ...
    
                    Bokeh.load_models(all_models);
                    var model = Bokeh.Collections(modeltype).get(modelid);
                    var view = new model.default_view({model: model, el: '#4a9dd7a1-f20c-4fe5-9917-13d172ef031a'});
                    Bokeh.index[modelid] = view
                });
            </script>
        </head>
        <body>
            <div class="plotdiv" id="4a9dd7a1-f20c-4fe5-9917-13d172ef031a"></div>
        </body>
    </html>
    """
    # Extract the script and all div tags
    scripts = re.findall(r'<script type="text/javascript">.+?</script>', text, flags=re.DOTALL)
    if len(scripts) != 2:
        errwarn('*** warning: bokeh file contains more than two script tags,')
        errwarn('    will be using the last one! (use output_file(..., mode="cdn"))')
    script = scripts[-1]
    divs = re.findall(r'<div class="plotdiv".+?</div>', text, flags=re.DOTALL)
    return script, divs


def html_figure(m):
    """Format figures for the html format

    Return HTML code to embed a figure in .html output. The syntax is
    `FIGURE:[filename[, options][, sidecap=BOOL][, frac=NUM]] [caption]`.
    Keywords: `sidecap` (default is False), `frac` (default is ),
    Options: `--html_figure_hrule`, --html_figure_caption`, `--html_responsive_figure_width`
    :param _regex.Match m: regex match  object
    :return: HTML code
    :rtype: str
    """
    caption = m.group('caption').strip().strip('"').strip("'")
    filename = m.group('filename').strip()
    opts = m.group('options').strip()
    info = dict()

    # Extract figure label
    pattern = r'(label\{(.+?)\})'
    m_label = re.search(pattern, caption)
    if m_label:
        label = '<!-- figure label: --> %s' % m_label.group(1)
        caption = re.sub(pattern,
                         ' <!-- caption label: %s -->' % m_label.group(2),
                         caption)
    else:
        label = ''
    # Place label in top of the figure such that links point to the
    # top regardless of whether the caption is at the top of bottom

    sidecap = False

    # Process any inline figure opts
    if opts:
        info = shlex.split(opts)
        info = dict(s.strip(',').split('=') for s in info)
        # responsive figure width option
        if option('html_responsive_figure_width'):
            styleset = "width:100%;"
            if 'width' in info:
                styleset = "max-width:%s;" % info['width']
            info.update(style=styleset + info.get('style', ''))
        # sidecap, frac keywords
        frac = 1
        for opt, val in info.items():
            if opt == 'sidecap': #TODO docs?
                sidecap = True if val=='True' else False
            elif opt == 'frac':
                frac = float(val)
        # Set align='bottom' by default
        info.update(align=info.get('align','bottom'))
        # String of options
        opts = ' '.join(['%s="%s"' % (opt, value)
                         for opt, value in info.items()
                         if opt not in ['frac', 'sidecap']])

    # Bokeh plot?
    bokeh_plot = False
    if filename.endswith('.html') and not filename.startswith('http'):
        f = open(filename, 'r')
        content = f.read()
        f.close()
        if 'Bokeh.set_log_level' in content:
            bokeh_plot = True
            script, divs = interpret_bokeh_plot(content)
            image = '\n<!-- Bokeh plot -->\n%s\n%s' % (script, '\n'.join(divs))
        else:
            errwarn('*** error: figure file "%s" must be a Bokeh plot' % filename)
            _abort()

    if not filename.startswith('http') and not bokeh_plot:
        add_to_file_collection(filename)

    # Write the <img> tag
    if not bokeh_plot:
        image = '<img src="%s" %s>' % (filename, opts) #TODO

    # Wrap the <img> tag in html code
    if caption:
       # Caption above figure and an optional horizontal rules:
       hrules = option('html_figure_hrule=', 'top')
       top_hr = bottom_hr = ''
       if 'top' in hrules:
           top_hr = '\n<hr class="figure">'
       if 'bottom' in hrules:
           bottom_hr = '\n<hr class="figure">'
       placement = option('html_figure_caption=', 'top')
       if sidecap == False:
           if placement == 'top':
               text = ("\n"
                    "<center> %s <!-- FIGURE -->%s\n"
                    '<center>\n<p class="caption"> %s </p>\n</center>\n'
                    "<p>%s</p>%s\n"
                    "</center>\n") % (label, top_hr, caption, image, bottom_hr)
           else:
               text = ("\n"
                    "<center> %s <!-- FIGURE -->%s\n"
                    "<p>%s</p>\n"
                    '<center><p class="caption"> %s </p></center>%s\n'
                    "</center>\n") % (label, top_hr, image, caption, bottom_hr)
       else:
           # sidecap is implemented as table
           text = ("\n"
                   "<center> %s <!-- FIGURE -->%s\n"
                   "<table>\n"
                   "<tr>\n"
                   '<td style="width:%s;">%s</td>\n'
                   '<td><p class="caption"> %s </p></td>\n'
                   "</tr>\n"
                   "</table>%s\n"
                   "</center>\n"
                   ) % (label, top_hr, str(int(frac*100)) + '%', image, caption, bottom_hr)
    else:
       # Just insert image file when no caption
       #s = '<center><p>%s</p></center>' % image # without <linebreak>
       # with two <linebreak>:
       text = ('<br/><br/>\n'
               '<center>\n'
               '<p>%s</p>\n'
               '</center>\n'
               '<br/><br/>') % image

    return text


def html_footnotes(filestr, format, pattern_def, pattern_footnote):
    # Keep definitions where they are
    # (a bit better: place definitions before next !split)
    # Number the footnotes

    footnotes = re.findall(pattern_def, filestr, flags=re.MULTILINE|re.DOTALL)
    names = [name for name, footnote, dummy in footnotes]
    footnotes = {name: text for name, text, dummy in footnotes}

    name2index = {names[i]: i+1 for i in range(len(names))}

    def subst_def(m):
        # Make a table for the definition
        name = m.group('name').strip()
        text = m.group('text').strip()
        html = '\n<p id="def_footnote_%s"><a href="#link_footnote_%s"><b>%s:</b></a> %s</p>\n' % (name2index[name], name2index[name], name2index[name], text)
        # (<a name=""></a> is later replaced by a div tag)
        return html

    filestr = re.sub(pattern_def, subst_def, filestr,
                     flags=re.MULTILINE|re.DOTALL)

    def subst_footnote(m):
        name = m.group('name').strip()
        if name in name2index:
            i = name2index[m.group('name')]
        else:
            errwarn('*** error: found footnote with name "%s", but this one is not defined' % name)
            _abort()
        if option('html_style=', '').startswith('boots'):
            # Use a tooltip construction so the footnote appears when hovering over
            text = ' '.join(footnotes[name].strip().splitlines())
            # Note: formatting does not work well with a tooltip
            # could issue a warning of we find * (emphasis) or ` or "..": ".." link
            if '*' in text:
                newtext, n = re.subn(r'\*(.+?)\*', r'\g<1>', text)
                if n > 0:
                    errwarn('*** warning: found emphasis tag *...* in footnote, which was removed')
                    errwarn('    in tooltip (since it does not work with bootstrap tooltips)')
                    errwarn('    but not in the footnote itself.')
                    errwarn(text + '\n')
                text = newtext
            if '`' in text:
                newtext, n = re.subn(r'`(.+?)`', r'\g<1>', text)
                if n > 0:
                    errwarn('*** warning: found inline code tag `...` in footnote, which was removed')
                    errwarn('    in tooltip (since it does not work with bootstrap tooltips):')
                    errwarn(text + '\n')
                text = newtext
            if '"' in text:
                newtext, n1 = re.subn(r'"(.+?)" ?:\s*"(.+?)"', r'\g<1>', text)
                newtext, n2 = re.subn(r'URL ?:\s*"(.+?)"', r'\g<1>', newtext)
                if n1 > 0 or n2 > 0:
                    errwarn('*** warning: found link tag "...": "..." in footnote, which was removed')
                    errwarn('    from tooltip (since it does not work with bootstrap tooltips)')
                    errwarn(text)
                text = newtext
            html = ' <button type="button" class="btn btn-primary btn-xs" rel="tooltip" data-placement="top" title="%s"><a href="#def_footnote_%s" id="link_footnote_%s" style="color: white">%s</a></button>' % (text, i, i, i)
            # (<a name=""></a> is later replaced by a div tag)
        else:
            html = r' [<a id="link_footnote_%s" href="#def_footnote_%s">%s</a>]' % (i, i, i)
            # (<a name=""></a> is later replaced by a div tag)
        return html

    filestr = re.sub(pattern_footnote, subst_footnote, filestr)
    return filestr


def html_table(table):
    column_width = table_analysis(table['rows'])
    ncolumns = len(column_width)
    column_spec = table.get('columns_align', 'c'*ncolumns).replace('|', '')
    heading_spec = table.get('headings_align', 'c'*ncolumns).replace('|', '')
    a2html = {'r': 'right', 'l': 'left', 'c': 'center'}
    bootstrap = option('html_style=', '').startswith('boots')

    if bootstrap:
        #span = ncolumns+1
        # Base span on total width of all columns
        span = min(int(sum(column_width)/100.0*12), 12)
        s = ('\n'
             '<div class="row">\n'
             '  <div class="col-xs-%d">\n'
             '    <table class="dotable table-striped table-hover table-condensed">\n'
             ) % span
    else:
        s = '<table class="dotable" border="1">\n'
    for i, row in enumerate(table['rows']):
        if row == ['horizontal rule']:
            continue
        if i == 1 and \
           table['rows'][i-1] == ['horizontal rule'] and \
           table['rows'][i+1] == ['horizontal rule']:
            headline = True
            # Empty column headings?
            skip_headline = max([len(column.strip())
                                 for column in row]) == 0
        else:
            headline = False

        if headline and not skip_headline:
            s += '<thead>\n'
        s += '<tr>'
        for column, w, ha, ca in \
                zip(row, column_width, heading_spec, column_spec):
            if headline:
                if not skip_headline:
                    # Use td tag if math or code or bootstrap
                    if r'\(' in column or '<code>' in column or bootstrap:
                        tag = 'td'
                        if bootstrap:
                            if r'\(' in column or '<code>' in column:
                                bold = '', ''
                            else:
                                bold = '<b>', '</b>'
                        else:
                            bold = '', ''
                    else:
                        tag = 'th'
                        bold = '', ''
                    s += '<%s align="%s">%s%s%s</%s> ' % \
                    (tag, a2html[ha], bold[0], column.center(w), bold[1], tag)
            else:
                s += '<td align="%s">   %s    </td> ' % \
                     (a2html[ca], column.ljust(w))
        s += '</tr>\n'
        if headline:
            if not skip_headline:
                s += '</thead>\n'
            s += '<tbody>\n'
    s += '</tbody>\n'
    if bootstrap:
        s += '    </table>\n  </div> <!-- col-xs-%d -->\n</div> <!-- cell row -->\n' % span
    else:
        s += '</table>\n'
    return s


def html_movie(m):
    """Format movies for the html format

    Return HTML code to embed a movie in HTML output. The syntax is
    `MOVIE: [filename[, height=NUM][, width=NUM]] [caption]`.
    Keywords: width (default is 640px), height (default is 365px)
    Options: `--html_figure_hrule`, --html_figure_caption`, `--html_responsive_figure_width`
    :param _regex.Match m: regex match
    :return: HTML code
    :rtype: str
    """
    filename = m.group('filename').strip()
    caption = m.group('caption').strip().strip('"').strip("'")
    opts = m.group('options').strip()
    info = dict()

    # Process any inline figure opts
    if opts:
        info = shlex.split(opts)
        info = dict(s.strip(',').split('=') for s in info)
        # String of options
        opts = ' '.join(['%s="%s"' % (opt, value)
                         for opt, value in info.items()
                         if opt not in ['frac', 'sidecap']])

    # Autoplay
    autoplay = option('html_video_autoplay=', 'False')
    if autoplay in ('on', 'off', 'True', 'true'):
        autoplay = True
    else:
        autoplay = False

    if 'youtu.be' in filename:
        filename = filename.replace('youtu.be', 'youtube.com')
    if 'youtube.com' in filename:
        if not 'youtube.com/embed/' in filename:
            filename = filename.replace('watch?v=', '')
            filename = filename.replace('youtube.com/', 'youtube.com/embed/')
            filename = filename.replace('https://youtube.com/', 'https://www.youtube.com/')
    elif 'vimeo.com' in filename:
        if not 'player.vimeo.com/video/' in filename:
            if filename.startswith('http://'):
                filename = 'https://' + filename[7:]
            if not filename.startswith('https://') :
                filename = 'https://' + filename
            filename = filename.replace('https://vimeo.com', 'https://player.vimeo.com/video')

    if not filename.startswith('http'):
        add_to_file_collection(filename)

    # Default width and height
    width = info.get('width', 640)
    height = info.get('height', 365)

    if '*' in filename or '->' in filename:
        # Animation Based on Filename Generators
        # frame_*.png
        # frame_%04d.png:0->120
        # https://some.net/files/frame_%04d.png:0->120
        from . import DocWriter
        try:
            header, jscode, form, footer, frames = \
                    DocWriter.html_movie(filename, **info)
        except ValueError as e:
            errwarn('*** error: %s' % str(e))
            _abort()
        text = jscode + form
        if caption:
            text += '\n<br><em>' + caption + '</em><br>\n\n'
        if not frames[0].startswith('http'):
            add_to_file_collection(frames)
    elif 'youtube.com' in filename or 'vimeo.com' in filename:
        # Make html for a local YouTube/Vimeo frame
        text = ('\n'
                '<iframe width="%s" height="%s" src="%s" frameborder="0" allowfullscreen></iframe>\n'
                ) % (width, height, filename)
        if caption:
            text += """\n<p><em>%s</em></p>\n\n""" % caption
    else:
        # Some movie file
        stem, ext = os.path.splitext(filename)
        if ext == '':
            errwarn('*** error: never specify movie file without extension')
            _abort()

        if ext in ('.mp4', '.ogg', '.webm'):
            # Use new HTML5 video tag
            autoplay = 'autoplay ' if autoplay else ''
            sources3 = option('no_mp4_webm_ogg_alternatives', True)
            text = ("\n"
                    "<div>\n"
                    "<video %(autoplay)sloop controls width='%(width)s' height='%(height)s' preload='none'>") \
                   % vars()
            movie_exists = False
            mp4_exists = False
            if sources3:
                # Set up loading of three alternatives.
                # Specify mp4 as first video because on iOS only
                # the first specified video is loaded, and mp4
                # can play on iOS.
                msg = 'movie: trying to find'
                if is_file_or_url(stem + '.mp4', msg) in ('file', 'url'):
                    text += movie2html['.mp4'] % vars()
                    movie_exists = True
                    mp4_exists = True
                if is_file_or_url(stem + '.webm', msg) in ('file', 'url'):
                    text += movie2html['.webm'] % vars()
                    movie_exists = True
                if is_file_or_url(stem + '.ogg', msg) in ('file', 'url'):
                    text += movie2html['.ogg'] % vars()
                    movie_exists = True
            else:
                # Load just the specified file
                if is_file_or_url(stem + ext, msg) in ('file', 'url'):
                    text += movie2html[ext] % vars()
                    movie_exists = True
            if not movie_exists:
                errwarn('*** warning: movie "%s" was not found' % filename)
                if sources3:
                    errwarn('    could not find any .ogg/.mp4/.webm version of this filename')
                    import time
                    time.sleep(5)  # let the warning shine for a while
                    #_abort()

            text += ("\n"
                     "</video>\n"
                     "</div>\n"
                     "<p><em>%s</em></p>\n"
                     ) % caption
            #if not mp4_exists:
            if True:
                # Seems that there is a problem with .mp4 movies as well...
                text += ("\n"
                         "<!-- Issue warning if in a Safari browser -->\n"
                         '<script language="javascript">\n'
                         "if (!!(window.safari)) {\n"
                         '  document.write('
                         '"<div style=\\"width:95%%; padding:10px; border:1px solid #100; border-radius:4px;\\">'
                         '<p><font color=\\"red\\">'
                         'The above movie will not play in Safari - use Chrome, Firefox, or Opera.</font></p></div>"'
                         ')}\n'
                         "</script>\n\n")
        elif ext in ('.mp3', '.m4a',):
            # Use HTML5 audio tag
            text = ('\n'
                    '<audio src="%s"><p>Your browser does not support the audio element.</p>\n'
                    '</audio>\n') % filename
        else:
            # Old HTML embed tag
            autoplay = 'true' if autoplay else 'false'
            text = ('\n'
                    '<embed src="%s" %s autoplay="%s" loop="true"></embed>\n'
                    '<p><em>%s</em></p>\n') % (filename, opts, autoplay, caption)
    return text


def html_author(authors_and_institutions, auth2index, inst2index, index2inst, auth2email):
    # Make a short list of author names - can be extracted elsewhere
    # from the HTML code and used in, e.g., footers.
    authors = [author for author in auth2index]
    if len(authors) > 1:
        authors[-1] = 'and ' + authors[-1]
    authors = ', '.join(authors)
    text = ("\n\n"
            "<p></p>\n"
            "<!-- author(s): %s -->\n") % authors

    def email(author):
        address = auth2email[author]
        if address is None:
            email_text = ''
        else:
            name, place = address.split('@')
            #email_text = ' (<tt>%s</tt> at <tt>%s</tt>)' % (name, place)
            email_text = ' (<tt>%s at %s</tt>)' % (name, place)
        return email_text

    one_author_at_one_institution = False
    if len(auth2index) == 1:
        author = list(auth2index.keys())[0]
        if len(auth2index[author]) == 1:
            one_author_at_one_institution = True
    if one_author_at_one_institution:
        # drop index
        author = list(auth2index.keys())[0]
        text += '\n<center>\n<b>%s</b> %s\n</center>\n\n' % \
            (author, email(author))
        text += '\n\n<!-- institution -->\n\n'
        text += '<center>\n<b>%s</b>\n</center>\n\n' % (index2inst[1])
    else:
        for author in auth2index:
            text += '\n<center>\n<b>%s</b> %s%s\n</center>\n\n' % \
                (author, str(auth2index[author]), email(author))
        text += '\n\n<!-- institution(s) -->\n\n'
        for index in index2inst:
            text += '<center>\n[%d] <b>%s</b>\n</center>\n\n' % \
                    (index, index2inst[index])
    text += '<br>\n\n'
    return text


def html_abstract(m):
    # m is r'<b>\g<type>.</b> \g<text>\n\g<rest>'
    type = m.group('type')
    type = globals.locale_dict[globals.locale_dict['language']].get(type, type)
    text = m.group('text')
    rest = m.group('rest')
    if type.lower() == 'preface':
        # Drop heading
        return '%(text)s\n%(rest)s' % vars()
    else:
        return '<b>%(type)s.</b> %(text)s\n%(rest)s' % vars()


def html_ref_and_label(section_label2title, format, filestr):
    # This is the first format-specific function to be called.
    # We therefore do some HTML-specific fixes first.

    filestr = fix_ref_section_chapter(filestr, format)

    # extract the labels in the text (filestr is now without
    # mathematics and associated labels)
    running_text_labels = re.findall(r'label\{(.+?)\}', filestr)

    # make special anchors for all the section titles with labels:
    for label in section_label2title:
        # make new anchor for this label (put in title):
        title = section_label2title[label]
        title_pattern = r'(_{3,9}|={3,9})\s*%s\s*(_{3,9}|={3,9})\s*label\{%s\}' % (re.escape(title), label)
        title_new = '\g<1> %s <a name="%s"></a> \g<2>' % (title.replace('\\', '\\\\'), label)
        # (Note: the <a name=""> anchor is replaced by id="" in html_code)
        filestr, n = re.subn(title_pattern, title_new, filestr)
        # (a little odd with mix of doconce title syntax and html NAME tag...)
        if n == 0:
            #raise Exception('problem with substituting "%s"' % title)
            pass

    # turn label{myname} to anchors <a name="myname"></a>
    filestr = re.sub(r'label\{(.+?)\}', r'<a name="\g<1>"></a>', filestr)
    # (<a name=""></a> is later replaced by a div tag)

    # replace all references to sections by section titles:
    for label in section_label2title:
        title = section_label2title[label]
        filestr = filestr.replace('ref{%s}' % label,
                                  '<a href="#%s">%s</a>' % (label, title))

    # This special character transformation is easier done
    # with encoding="utf-8" in the first line in the html file:
    # (but we do it explicitly to make it robust)
    filestr = latin2html(filestr)
    # (wise to do latin2html before filestr = '\n'.join(lines) below)

    # Number all figures, find all figure labels and replace their
    # references by the figure numbers
    # (note: figures are already handled!)
    #
    caption_start = '<p class="caption">'
    caption_pattern = r'%s(.+?)</p>' % caption_start
    #label_pattern = r'%s.+?<a name="(.+?)">' % caption_start
    label_pattern = r'%s.+? <!-- caption label: (.+?) -->' % caption_start
    # Should have <h\d id=""> type of labels too

    # References to custom numbered environments are also handled here
    # We look for all such environments, extract their numbers
    # from special comment tag and record it to label2no along with Figure's
    # numbers
    #
    # We allow 'no-number numbers' like 'Theorem A', so use number=([^\s]+?) pattern
    # instead of number=(\d+?)

    custom_env_pattern = r'<!--\s*custom environment:\s*label=([^\s]+?),\s*number=([^\s]+?)\s*-->'

    lines = filestr.splitlines()
    label2no = {}
    fig_no = 0
    for i in range(len(lines)):
        if caption_start in lines[i]:
            m = re.search(caption_pattern, lines[i])
            if m:
                fig_no += 1
                caption = m.group(1)
                from_ = caption_start + caption
                to_ = caption_start + 'Figure %d: ' % fig_no + caption
                lines[i] = lines[i].replace(from_, to_)

            m = re.search(label_pattern, lines[i])
            if m:
                label2no[m.group(1)] = fig_no

        # process custom environments
        m = re.search(custom_env_pattern, lines[i])
        if m:
            label2no[m.group(1)] = m.group(2)

            # replace the special comment with an anchor
            lines[i] = re.sub(custom_env_pattern,
                    "<div id=\"%s\" />" % m.group(1), lines[i])

    filestr = '\n'.join(lines)

    for label, no in label2no.items():
        filestr = filestr.replace('ref{%s}' % label,
                                  '<a href="#%s">%s</a>' % (label, str(no)))
        # we allow 'non-number numbers' for custom environments like 'theorem A'
        # so str(no)

    # replace all other references ref{myname} by <a href="#myname">myname</a>:
    for label in running_text_labels:
        filestr = filestr.replace('ref{%s}' % label,
                                  '<a href="#%s">%s</a>' % (label, label))

    # insert anchors in all section headings without label in case
    # we want a table of contents with links to each section
    section_pattern = re.compile(r'^\s*(_{3,9}|={3,9})(.+?)(_{3,9}|={3,9})\s*$',
                                 re.MULTILINE)
    m = section_pattern.findall(filestr)
    for i in range(len(m)):
        heading1, title, heading2 = m[i]
        newtitle = title
        if not '<a name="' in title:
            # Note: because filestr has already been encoded, first undo the deconding on the title
            newtitle = title + ' <a name="%s"></a>' % string2href(html2latin(title))
        # (Note: the <a name=""> anchor is replaced by id="" in html_code)
        filestr = filestr.replace(heading1 + title + heading2,
                                  heading1 + newtitle+ heading2,
                                  1) # count=1: only the first!

    return filestr


def html_exercise(exer):
    exerstr, solstr = doconce_exercise_output(
        exer,
        solution_header='__Solution.__',
        answer_header='__Answer.__',
        hint_header='__Hint.__')
    bootstrap = option('html_style=', '').startswith('boots')
    if bootstrap:
        # Bootstrap typesetting where hints and solutions can be folded
        language = globals.locale_dict['language']
        envir2heading = dict(hint=r'(?P<heading>__{0}(?P<hintno> \d+)?\.__)'.format(globals.locale_dict[language]['Hint']),
                             ans=r'(?P<heading>__{0}\.__)'.format(globals.locale_dict[language]['Answer']),
                             sol=r'(?P<heading>__{0}\.__)'.format(globals.locale_dict[language]['Solution']))
        global _id_counter # need this trick to update this var in subst func
        _id_counter = 0
        for envir in 'hint', 'ans', 'sol':

            def subst(m):
                global _id_counter
                _id_counter += 1
                heading = m.group('heading')
                body = m.group('body')
                id = 'exer_%d_%d' % (exer['no'], _id_counter)
                visible_text = heading
                unfold = bootstrap_collapse(
                    visible_text=heading, collapsed_text=body,
                    id=id, button_text='', icon='hand-right')
                replacement = '\n# ' + envir_delimiter_lines[envir][0] + '\n' + unfold + '\n# ' + envir_delimiter_lines[envir][1] + '\n'
                return replacement

            pattern = '\n# ' + envir_delimiter_lines[envir][0] + '\s+' + envir2heading[envir] + '(?P<body>.+?)' + '\n# ' + envir_delimiter_lines[envir][1] + '\n'
            exerstr = re.sub(pattern, subst, exerstr, flags=re.DOTALL)
            solstr = re.sub(pattern, subst, solstr, flags=re.DOTALL)
    return exerstr, solstr


def html_index_bib(filestr, index, citations, pubfile, pubdata):
    if citations:
        filestr = cite_with_multiple_args2multiple_cites(filestr)
    for label in citations:
        filestr = filestr.replace('cite{%s}' % label,
                                  '<a href="#%s">[%d]</a>' % \
                                  (label, citations[label]))
    if pubfile is not None:
        bibtext = bibliography(pubdata, citations, format='doconce')
        for label in citations:
            try:
                bibtext = bibtext.replace(
                    'label{%s}' % label, '<a name="%s"></a>' % label)
                # (<a name=""></a> is later replaced by a div tag)
            except UnicodeDecodeError as e:
                if "can't decode byte" in str(e):
                    try:
                        bibtext = bibtext.replace(
                            'label{%s}' % label, '<a name="%s"></a>' % label)
                    except UnicodeDecodeError as e:
                        errwarn('UnicodeDecodeError: ' + e)
                        errwarn('*** error: problems in %s' % pubfile)
                        errwarn('    with key ' + label)
                        errwarn('    tried to do decode("utf-8"), but it did not work')
                        _abort()
                else:
                    errwarn(e)
                    errwarn('*** error: problems in %s' % pubfile)
                    errwarn('    with key ' + label)
                    _abort()

        bibtext = ('\n'
                   '<!-- begin bibliography -->\n'
                   '%s\n'
                   '<!-- end bibliography -->\n') % bibtext

        filestr = re.sub(r'^BIBFILE:.+$', bibtext, filestr, flags=re.MULTILINE)

    # could use anchors for idx{...}, but multiple entries of an index
    # would lead to multiple anchors, so remove them all:
    filestr = re.sub(r'idx\{([^\{\}]*(?:\{[^\}]*\})?[^\}]*)\}\n?', '', filestr)

    return filestr

# Module variable holding info about section titles etc.
# To be used in navitation panels.
global tocinfo
tocinfo = None


def html_toc(sections, filestr):
    # Find minimum section level
    level_min = 4
    for title, level, label in sections:
        if level < level_min:
            level_min = level

    toc_depth = int(option('toc_depth=', 2))

    extended_sections = []  # extended list for toc in HTML file
    toc = globals.locale_dict[globals.locale_dict['language']]['toc']
    # This function is always called, only extend headings if a TOC is wanted
    m = re.search(r'^TOC: +[Oo]n', filestr, flags=re.MULTILINE)
    if m:
        extended_sections.append(
            (toc, level_min, 'table_of_contents', 'table_of_contents'))
    #hr = '<hr>'
    hr = ''
    s = ''
    # (we add class="anchor" in the calling code the above heading, if necessary)
    for i in range(len(sections)):
        title, level, label = sections[i]
        if label is not None:
            href = label
        else:
            href = string2href(title)
        indent = ((level - level_min))
        if level <= toc_depth:
            s += '<p>' + (html_tab * indent) + \
                 '<a href="#%s">%s</a>' % (href, title ) + '</p>\n'#'<br>\n'
        extended_sections.append((title.strip(), level, label, href))
    s = html_toc_ % (toc, hr, s)
    #s += '<p>%s\n</p>\n' % hr
    # Store for later use in navigation panels etc.
    global tocinfo
    tocinfo = {'sections': extended_sections, 'highest level': level_min}

    return s


def bootstrap_collapse(visible_text, collapsed_text,
                       id, button_text='', icon='pencil'):
    """Generate HTML Bootstrap code for a collapsing/unfolding text."""
    # icon types:
    # https://www.w3schools.com/bootstrap/bootstrap_ref_comp_glyphs.asp
    text = ('\n'
            '<p>\n'
            '<a class="glyphicon glyphicon-%(icon)s showdetails" data-toggle="collapse"\n'
            ' data-target="#%(id)s" style="font-size: 80%%;">%(button_text)s</a>\n'
            '<a href="#%(id)s" data-toggle="collapse">\n'
            '%(visible_text)s\n'
            '</a>\n'
            '<div class="collapse-group">\n'
            '<p><div class="collapse" id="%(id)s">\n'
            '%(collapsed_text)s\n'
            '</div></p>\n'
            '</div>\n'
            '</p>\n') % vars()
    return text


def html_inline_comment(m):
    # See latex.py for explanation
    name = m.group('name').strip()
    comment = m.group('comment').strip()
    chars = {',': 'comma', ';': 'semicolon', '.': 'period'}
    if name[:4] == 'del ':
        for char in chars:
            if comment == char:
                return r' <font color="red"> (<b>edit %s</b>: delete %s)</font>' % (name[4:], chars[char])
        return r' <font color="red">(<b>edit %s</b>:)</font> <del> %s </del>' % (name[4:], comment)
    elif name[:4] == 'add ':
        for char in chars:
            if comment == char:
                return r'<font color="red">%s (<b>edit %s</b>: add %s)</font>' % (comment, name[4:], chars[char])
        return r' <font color="red">(<b>edit %s</b>:) %s</font>' % (name[4:], comment)
    else:
        # Ordinary name
        comment = ' '.join(comment.splitlines()) # '\s->\s' -> ' -> '
        if ' -> ' in comment:
            # Replacement
            if comment.count(' -> ') != 1:
                errwarn('*** wrong syntax in inline comment:')
                errwarn(comment)
                errwarn('(more than two ->)')
                _abort()
            orig, new = comment.split(' -> ')
            return r' <font color="red">(<b>%s</b>:)</font> <del> %s </del> <font color="red">%s</font>' % (name, orig, new)
        else:
            # Ordinary comment
            return '\n<!-- begin inline comment -->\n<font color="red">(<b>%s</b>: %s)</font>\n<!-- end inline comment -->\n' % (name, comment)


def html_quiz(quiz):
    import string
    bootstrap = option('html_style=', '').startswith('boots')
    button_text = option('html_quiz_button_text=', '')
    question_prefix_default = globals.lookup_locale_dict('question_prefix')
    common_choice_prefix_default = globals.lookup_locale_dict('choice_prefix')
    question_prefix = quiz.get('question prefix',
                               option('quiz_question_prefix=', question_prefix_default))
    common_choice_prefix = option('quiz_choice_prefix=', common_choice_prefix_default)
    hr = '<hr>' if option('quiz_horizontal_rule=', 'on') == 'on' else ''
    quiz_expl = option('quiz_explanations=', 'on')

    text = ''
    if 'new page' in quiz:
        text += '<!-- !split -->\n<h2>%s</h2>\n\n' % quiz['new page']

    text += '<!-- begin quiz -->\n'
    # Don't write Question: ... if inside an exercise section
    if quiz.get('embedding', 'None') in ['exercise',]:
        pass
    else:
        text += '%s\n<p>\n<b>%s</b> ' % (hr, question_prefix)

    text += quiz['question'] + '</p>\n'

    # List choices as paragraphs
    for i, choice in enumerate(quiz['choices']):
        #choice_no = i+1
        choice_no = string.ascii_uppercase[i]
        answer = choice[0].capitalize() + '!'
        choice_prefix = common_choice_prefix
        if 'choice prefix' in quiz:
            if isinstance(quiz['choice prefix'][i], basestring):
                choice_prefix = quiz['choice prefix'][i]
        if choice_prefix == '' or choice_prefix[-1] in ['.', ':', '?']:
            pass  # don't add choice number/letter
        else:
            choice_prefix += ' %s:' % choice_no
        if not bootstrap:  # plain html: show tooltip when hovering over choices
            tooltip = answer
            expl = ''
            if len(choice) == 3 and quiz_expl == 'on':
                expl = choice[2]
            if '<img' in expl or '$$' in expl or '<pre' in expl:
                errwarn('*** warning: quiz explanation contains block (fig/code/math)')
                errwarn('    and is therefore skipped')
                errwarn(expl + '\n')
                expl = ''  # drop explanation when it needs blocks
            # Should remove markup
            pattern = r'<a href="(.+?)">(.*?)</a>'  # URL
            expl = re.sub(pattern, '\g<2> (\g<1>)', expl)
            pattern = r'\\( (.+?) \\)'  # inline math
            expl = re.sub(pattern, '\g<1>', expl)  # mimic italic....
            tags = 'p blockquote em code b'.split()
            for tag in tags:
                expl = expl.replace('<%s>' % tag, ' ')
                expl = expl.replace('</%s>' % tag, ' ')
            tooltip = answer + ' ' + ' '.join(expl.splitlines())
            text += '\n<p><div title="%s"><b>%s</b>\n%s\n</div></p>\n' % (tooltip, choice_prefix, choice[1])
        else:
            id = 'quiz_id_%d_%s' % (quiz['no'], choice_no)
            if len(choice) == 3:
                expl = choice[2]
            else:
                if choice[0] == 'right':
                    expl = 'Correct!'
                else:
                    expl = 'Wrong!'
            # Use collapse functionality, see https://jsfiddle.net/8cYFj/
            visible_text = '&nbsp;<b>%s</b>\n%s' % (choice_prefix, choice[1])
            collapsed_text = '<img src="RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/%s.gif">\n%s' % ('correct' if choice[0] == 'right' else 'incorrect', expl)
            text += bootstrap_collapse(
               visible_text, collapsed_text,
               id, button_text, icon='pencil')

    if not bootstrap and hr:
        text += '%s\n' % hr
    text += '<!-- end quiz -->\n'
    return text


def html_box(block, format, text_size='normal'):
    """Add a HTML box with text, code, equations inside. Can have shadow."""
    # box_shadow is a global variable set in the top of the file
    shadow = ' ' + box_shadow if option('html_box_shadow') else ''
    return ('\n'
            '<!-- begin box -->\n'
            '<div style="width:95%%; padding:10px; border:1px solid #000; border-radius:4px; %s">\n'
            '%s\n'
            '</div>\n'
            '<!-- end box -->\n') % (shadow, block)


def html_quote(block, format, text_size='normal'):
    return ('<blockquote>\n'
            '%s\n'
            '</blockquote>\n') % (indent_lines(block, format, ' '*4, trailing_newline=False))

global admon_css_vars        # set in define
global html_admon_style      # set below

html_admon_style = option('html_admon=', None)
if html_admon_style is None:
    # Set sensible default value
    if re.search(r'solarized\d?_dark', option('html_style=', '')):
        html_admon_style = 'solarized_dark'
    elif option('html_style=', '').startswith('solarized'):
        html_admon_style = 'solarized_light'
    elif option('html_style=') == 'blueish2':
        html_admon_style = 'yellow'
    elif option('html_style=', '').startswith('boots'):
        html_admon_style = 'bootstrap_alert'
    else:
        html_admon_style = 'gray'

for _admon in globals.admons:
    # _Admon is constructed at import time, used as default title, but
    # will always be in English because of the early construction
    _Admon = globals.locale_dict[globals.locale_dict['language']].get(_admon, _admon).capitalize()  # upper first char

    # Below we could use
    # <img src="data:image/png;base64,iVBORw0KGgoAAAANSUh..."/>
    # for embedding images in the html code rather than just including them
    _text = ('\n'
             "def html_%(_admon)s(block, format, title='%(_Admon)s', text_size='normal'):\n"
             '    # No title?\n'
             "    if title.lower().strip() == 'none':\n"
             "        title = ''\n"
             '    # Blocks without explicit title should have empty title\n'
             "    if title == 'Block':  # block admon has no default title\n"
             "        title = ''\n"
             '\n'
             '    # Make pygments background equal to admon background for colored admons?\n'
             "    keep_pygm_bg = option('keep_pygments_html_bg')\n"
             '    pygments_pattern = r\'"background: .+?">\'\n'
             '\n'
             '    # html_admon_style is global variable\n'
             "    if option('html_style=', '')[:5].startswith('boots'):\n"
             '        # Bootstrap/Bootswatch html style\n'
             '\n'
             "        if html_admon_style == 'bootstrap_panel':\n"
             "            alert_map = {'warning': 'warning', 'notice': 'primary',\n"
             "                         'summary': 'danger', 'question': 'success',\n"
             "                         'block': 'default'}\n"
             '            text = \'<div class="panel panel-%%s">\' %% alert_map[\'%(_admon)s\']\n'
             "            if '%(_admon)s' != 'block':  # heading?\n"
             '                text += """\n'
             '  <div class="panel-heading">\n'
             '  <h3 class="panel-title">%%s</h3>\n'
             '  </div>""" %% title\n'
             '            text += """\n'
             '<div class="panel-body">\n'
             '<!-- subsequent paragraphs come in larger fonts, so start with a paragraph -->\n'
             '%%s\n'
             '</div>\n'
             '</div>\n'
             '""" %% block\n'
             '        else: # bootstrap_alert\n'
             "            alert_map = {'warning': 'danger', 'notice': 'success',\n"
             "                         'summary': 'warning', 'question': 'info',\n"
             "                         'block': 'success'}\n"
             '\n'
             '            if not keep_pygm_bg:\n'
             '                # 2DO: fix background color!\n'
             '                block = re.sub(pygments_pattern, r\'"background: %%s">\' %%\n'
             "                               admon_css_vars[html_admon_style]['background'], block)\n"
             '            text = """<div class="alert alert-block alert-%%s alert-text-%%s"><b>%%s</b>\n'
             '%%s\n'
             '</div>\n'
             '""" %% (alert_map[\'%(_admon)s\'], text_size, title, block)\n'
             '        return text\n'
             '\n'
             '    elif html_admon_style == \'colors\':\n'
             '        if not keep_pygm_bg:\n'
             '            block = re.sub(pygments_pattern, r\'"background: %%s">\' %%\n'
             '                           admon_css_vars[\'colors\'][\'background_%(_admon)s\'], block)\n'
             '        janko = """<div class="%(_admon)s alert-text-%%s"><b>%%s</b>\n'
             '%%s\n'
             '</div>\n'
             '""" %% (text_size, title, block)\n'
             '        return janko\n'
             '\n'
             "    elif html_admon_style in ('gray', 'yellow', 'apricot', 'solarized_light', 'solarized_dark'):\n"
             '        if not keep_pygm_bg:\n'
             '            block = re.sub(pygments_pattern, r\'"background: %%s">\' %%\n'
             '                           admon_css_vars[html_admon_style][\'background\'], block)\n'
             '        # Strip off <p> at the end of block to reduce space below the text\n'
             "        block = re.sub(\'(<p>\s*)+$\', '', block)\n"
             '        # Need a <p> after the title to ensure some space before the text\n'
             '        alert = """<div class="alert alert-block alert-%(_admon)s alert-text-%%s">\n'
             '<b>%%s</b>\n'
             '<p>\n'
             '%%s\n'
             '</div>\n'
             '""" %% (text_size, title, block)\n'
             '        return alert\n'
             '\n'
             "    elif html_admon_style == 'lyx':\n"
             '        block = \'<div class="alert-text-%%s">%%s</div>\' %% (text_size, block)\n'
             "        if '%(_admon)s' != 'block':\n"
             '            lyx = """\n'
             '<table width="95%%%%" border="0">\n'
             '<tr>\n'
             '<td width="25" align="center" valign="top">\n'
             '<img src="RAW_GITHUB_URL/doconce/doconce/master/bundled/html_images/lyx_%(_admon)s.png" hspace="5" '
             'alt="%(_admon)s"></td>\n'
             '<th align="left" valign="middle"><b>%%s</b></th>\n'
             '</tr>\n'
             '<tr><td>&nbsp;</td> <td align="left" valign="top"><p>\n'
             '%%s\n'
             '</p></td></tr>\n'
             '</table>\n'
             '""" %% (title, block)\n'
             '        else:\n'
             '            lyx = """\n'
             '<table width="95%%%%" border="0">\n'
             '<tr><th align="left" valign="middle"><b>%%s</b></th>\n'
             '</tr>\n'
             '<tr><td>&nbsp;&nbsp;&nbsp;&nbsp;</td> <td align="left" valign="top"><p>\n'
             '%%s\n'
             '</p></td></tr>\n'
             '</table>\n'
             '""" %% (title, block)\n'
             '        return lyx\n'
             '\n'
             "    elif html_admon_style.startswith('paragraph'):\n"
             '        # Plain paragraph\n'
             "        if '-' in html_admon_style:\n"
             "            font_size = html_admon_style.split('-')[1]\n"
             "            if font_size in ('small', 'large'):\n"
             '                text_size = font_size\n'
             '            else:\n'
             '                if int(font_size) < 100:\n'
             "                    text_size = 'small'\n"
             '                else:\n'
             "                    text_size = 'large'\n"
             '\n'
             '        paragraph = """\n'
             '\n'
             '<!-- admonition: %(_admon)s, typeset as paragraph -->\n'
             '<div class="alert-text-%%s"><b>%%s</b>\n'
             '%%s\n'
             '</div>\n'
             '""" %% (text_size, title, block)\n'
             '        return paragraph\n'
             '    else:\n'
             "        errwarn('*** error: illegal --html_admon=%%s' %% html_admon_style)\n"
             "        errwarn('    legal values are colors, gray, yellow, apricot, lyx,')\n"
             "        errwarn('    paragraph, paragraph-80, paragraph-120; and')\n"
             "        errwarn('    bootstrap_alert or bootstrap_panel for --html_style=bootstrap*|bootswatch*')\n"
             '        _abort()\n'
             '\n') % vars()
    exec(_text)


def define(FILENAME_EXTENSION,
           BLANKLINE,
           INLINE_TAGS_SUBST,
           CODE,
           LIST,
           ARGLIST,
           TABLE,
           EXERCISE,
           FIGURE_EXT,
           CROSS_REFS,
           INDEX_BIB,
           TOC,
           ENVIRS,
           QUIZ,
           INTRO,
           OUTRO,
           filestr):

    # all arguments are dicts and accept in-place modifications (extensions)

    FILENAME_EXTENSION['html'] = '.html'    # output file extension
    BLANKLINE['html'] = '\n<p></p>\n'       # blank input line => new paragraph
    INLINE_TAGS_SUBST['html'] = {           # from inline tags to HTML tags
        # keep math as is:
        'math':          r'\g<begin>\( \g<subst> \)\g<end>',
        #'math2':         r'\g<begin>\g<puretext>\g<end>',
        'math2':         r'\g<begin>\( \g<latexmath> \)\g<end>',
        'emphasize':     r'\g<begin><em>\g<subst></em>\g<end>',
        'bold':          r'\g<begin><b>\g<subst></b>\g<end>',
        'verbatim':      html_verbatim,
        'colortext':     r'<font color="\g<color>">\g<text></font>',
        #'linkURL':       r'\g<begin><a href="\g<url>">\g<link></a>\g<end>',
        'linkURL2':      r'<a href="\g<url>" target="_self">\g<link></a>',
        'linkURL3':      r'<a href="\g<url>" target="_self">\g<link></a>',
        'linkURL2v':     r'<a href="\g<url>" target="_self"><tt>\g<link></tt></a>',
        'linkURL3v':     r'<a href="\g<url>" target="_self"><tt>\g<link></tt></a>',
        'plainURL':      r'<a href="\g<url>" target="_self"><tt>\g<url></tt></a>',
        'inlinecomment': html_inline_comment,
        'chapter':       r'\n<center>\n<h1>\g<subst></h1>\n</center> <!-- chapter heading -->',
        'section':       r'\n<h1>\g<subst></h1>',
        'subsection':    r'\n<h2>\g<subst></h2>',
        'subsubsection': r'\n<h3>\g<subst></h3>\n',
        'paragraph':     r'<b>\g<subst></b>' + '\n',
        'abstract':      html_abstract,
        'title':         r'\n\n<center>\n<h1>\g<subst></h1>\n</center>  <!-- document title -->\n',
        'date':          r'<center>\n<h4>\g<subst></h4>\n</center> <!-- date -->\n<br>',
        'author':        html_author,
        'figure':        html_figure,
        'movie':         html_movie,
        'comment':       '<!-- %s -->',
        'linebreak':     r'\g<text><br />',
        'footnote':      html_footnotes,
        'non-breaking-space': '&nbsp;',
        'horizontal-rule': '<hr>',
        'ampersand1':    r'\g<1> &amp; \g<2>',
        'ampersand2':    r' \g<1>&amp;\g<2>',
        'emoji':         r'\g<1><img src="%s\g<2>.png" width="22px" height="22px" align="center">\g<3>' % emoji_url
        }

    if option('wordpress'):
        INLINE_TAGS_SUBST['html'].update({
            'math':          r'\g<begin>$latex \g<subst>$\g<end>',
            'math2':         r'\g<begin>$latex \g<latexmath>$\g<end>'
            })

    ENVIRS['html'] = {
        'quote':         html_quote,
        'warning':       html_warning,
        'question':      html_question,
        'notice':        html_notice,
        'summary':       html_summary,
        'block':         html_block,
        'box':           html_box,
    }

    CODE['html'] = html_code

    # how to typeset lists and their items in html:
    LIST['html'] = {
        'itemize':
        {'begin': '\n<ul>\n', 'item': '<li>', 'end': '</ul>\n\n'},

        'enumerate':
        {'begin': '\n<ol>\n', 'item': '<li>', 'end': '</ol>\n\n'},

        'description':
        {'begin': '\n<dl>\n', 'item': '<dt>%s<dd>', 'end': '</dl>\n\n'},

        'separator': '',  # no need for blank lines between items and before/after
        }

    # how to typeset description lists for function arguments, return
    # values, and module/class variables:
    ARGLIST['html'] = {
        'parameter': '<b>argument</b>',
        'keyword': '<b>keyword argument</b>',
        'return': '<b>return value(s)</b>',
        'instance variable': '<b>instance variable</b>',
        'class variable': '<b>class variable</b>',
        'module variable': '<b>module variable</b>',
        }

    FIGURE_EXT['html'] = {
        'search': ('.html', '.png', '.gif', '.jpg', '.jpeg', '.svg'),
        'convert': ('.png', '.gif', '.jpg')}

    CROSS_REFS['html'] = html_ref_and_label
    TABLE['html'] = html_table
    INDEX_BIB['html'] = html_index_bib
    EXERCISE['html'] = html_exercise
    TOC['html'] = html_toc
    QUIZ['html'] = html_quiz

    # Delete the file containing a list of file requirements for html output
    if os.path.exists(_file_collection_filename % globals.dofile_basename):
        os.remove(_file_collection_filename % globals.dofile_basename)

    # Embedded style sheets and links to styles
    css_links = ''
    css = ''
    html_style = option('html_style=', '')
    if  html_style in ('solarized', 'solarized_light'):
        css = css_solarized
        css_links = css_link_solarized_highlight('light')
    elif  html_style == 'solarized_dark':
        css = css_solarized_dark
        css_links = css_link_solarized_highlight('dark')
    elif html_style in ('solarized2_light', 'solarized2'):
        css = css_solarized_thomasf_gray
        css_links = css_link_solarized_highlight('light') + '\n' + \
                    css_link_solarized_thomasf_light
    elif html_style == 'solarized2_dark':
        css = css_solarized_thomasf_gray
        css_links = css_link_solarized_highlight('dark') + '\n' + \
                    css_link_solarized_thomasf_dark

    elif html_style in ('solarized3_light', 'solarized3'):
        # Note: have tried to remove the extra box around code,
        # but did not succeed, think the original css file of thomasf
        # must be manipulated in some way...a lot of tries did not
        # succeed
        css = css_solarized_thomasf_green
        css_links = css_link_solarized_highlight('light') + '\n' + \
                    css_link_solarized_thomasf_light
    elif html_style == 'solarized3_dark':
        css_links = css_link_solarized_highlight('dark') + '\n' + \
                    css_link_solarized_thomasf_dark
    elif html_style == 'blueish':
        css = css_blueish
    elif html_style == 'blueish2':
        css = css_blueish2
    elif html_style == 'bloodish':
        css = css_bloodish
    elif html_style.startswith('tactile'):
        h1_color = h2_color = ''
        if '-' in html_style:
            if html_style.endswith('red'):
                h1_color = h2_color = 'color: #d5000d;'
            elif html_style.endswith('black'):
                h1_color = h2_color = 'color: #303030;'
        css = css_tactile % (h1_color, h2_color)
    elif html_style == 'rossant':
        css = css_rossant
    elif html_style == 'plain':
        css = ''
    else:
        css = css_blueish # default

    if option('pygments_html_style=', None) not in ('none', 'None', 'off', 'no') \
        and not option('html_style=', 'blueish').startswith('solarized') \
        and not option('html_style=', 'blueish').startswith('tactile'):
        # Remove pre style as it destroys the background for pygments
        css = re.sub(r'(pre|pre, code) +\{.+?\}', r'/* \g<1> style removed because it will interfer with pygments */', css, flags=re.DOTALL)

    # Fonts
    body_font_family = option('html_body_font=', None)
    heading_font_family = option('html_heading_font=', None)
    google_fonts = ('Patrick+Hand+SC', 'Molle:400italic', 'Happy+Monkey',
                    'Roboto+Condensed', 'Fenix', 'Yesteryear',
                    'Clicker+Script', 'Stalemate',
                    'Herr+Von+Muellerhoff', 'Sacramento',
                    'Architects+Daughter', 'Kotta+One',)
    if body_font_family == '?' or body_font_family == 'help' or \
       heading_font_family == '?' or heading_font_family == 'help':
        errwarn(' '.join(google_fonts))
        _abort()
    link = "@import url(https://fonts.googleapis.com/css?family=%s);"
    import_body_font = ''
    if body_font_family is not None:
        if body_font_family in google_fonts:
            import_body_font = link % body_font_family
        else:
            errwarn('*** warning: --html_body_font=%s is not valid' % body_font_family)
    import_heading_font = ''
    if heading_font_family is not None:
        if heading_font_family in google_fonts:
            import_heading_font = link % heading_font_family
        else:
            errwarn('*** warning: --html_heading_font=%s is not valid' % heading_font_family)
    if import_body_font or import_heading_font:
        css = '    ' + '\n    '.join([import_body_font, import_heading_font]) \
              + '\n' + css
    if body_font_family is not None:
        css = re.sub(r'font-family:.+;',
                     "font-family: '%s';" % body_font_family.replace('+', ' '),
                     css)
    if heading_font_family is not None:
        css += "\n    h1, h2, h3 { font-family: '%s'; }\n" % heading_font_family.replace('+', ' ')

    global admon_css_vars
    admon_styles = ['gray', 'yellow', 'apricot', 'colors', 'lyx', 'paragraph',
                    'bootstrap_alert', 'bootstrap_panel',
                    'solarized_light', 'solarized_dark']
    admon_css_vars = {style: {} for style in admon_styles}
    admon_css_vars['yellow']  = dict(boundary='#fbeed5', background='#fcf8e3')
    admon_css_vars['apricot'] = dict(boundary='#FFBF00', background='#fbeed5')
    #admon_css_vars['gray']    = dict(boundary='#bababa', background='whiteSmoke')
    admon_css_vars['gray']    = dict(boundary='#bababa', background='#f8f8f8') # same color as in pygments light gray background
    admon_css_vars['bootstrap_alert']  = dict(background='#ffffff')
    admon_css_vars['bootstrap_panel']  = dict(background='#ffffff')
    admon_css_vars['solarized_light'] = dict(boundary='#93a1a1', background='#eee8d5')
    admon_css_vars['solarized_dark'] = dict(boundary='#93a1a1', background='#073642')
    for style in admon_styles:
        admon_css_vars[style]['color'] = '#555'
    admon_css_vars['solarized_dark']['color'] = '#93a1a1'
    # Override with user's values
    html_admon_bg_color = option('html_admon_bg_color=', None)
    html_admon_bd_color = option('html_admon_bd_color=', None)
    if html_admon_bg_color is not None:
        for tp in ('yellow', 'apricot', 'gray'):
            admon_css_vars[tp]['background'] = html_admon_bg_color
    if html_admon_bd_color is not None:
        for tp in ('yellow', 'apricot', 'gray'):
            admon_css_vars[tp]['boundary'] = html_admon_bd_color

    for a in globals.admons:
        if a != 'block':
            admon_css_vars['yellow']['icon_' + a]  = 'small_yellow_%s.png' % a
            admon_css_vars['apricot']['icon_' + a] = 'small_yellow_%s.png' % a
            admon_css_vars['gray']['icon_' + a]    = 'small_gray_%s.png' % a
            admon_css_vars['solarized_light']['icon_' + a] = 'small_yellow_%s.png' % a
            admon_css_vars['solarized_dark']['icon_' + a] = 'small_gray_%s.png' % a
        else:
            admon_css_vars['yellow']['icon_' + a]  = ''
            admon_css_vars['apricot']['icon_' + a] = ''
            admon_css_vars['gray']['icon_' + a]    = ''
            admon_css_vars['solarized_light']['icon_' + a] = ''
            admon_css_vars['solarized_dark']['icon_' + a] = ''
    admon_css_vars['colors'] = dict(
        background_notice='#BDE5F8',
        background_block='#BDE5F8',
        background_summary='#DFF2BF',
        background_warning='#FEEFB3',
        background_question='#DFF2BF',
        icon_notice='Knob_Info.png',
        icon_summary='Knob_Valid_Green.png',
        icon_warning='Knob_Attention.png',
        icon_question='Knob_Forward.png',
        icon_block='',
        )
    if option('html_admon_shadow'):
        # Add a shadow effect to the admon_styles2 boxes
        global admon_styles2
        admon_styles2 = re.sub(
            r'(-webkit-|-moz-|)(border-radius: \d+px;)',
            '\g<1>\g<2> \g<1>%s' % box_shadow,
            admon_styles2)

    # Need to add admon_styles? (html_admon_style is global)
    for admon in globals.admons:
        if '!b'+admon in filestr and '!e'+admon in filestr:
            if html_admon_style == 'colors':
                css += (admon_styles1 % admon_css_vars[html_admon_style])
                break
            elif html_admon_style in ('gray', 'yellow', 'apricot',
                                      'solarized_light', 'solarized_dark'):
                css += (admon_styles2 % admon_css_vars[html_admon_style])
                break
            elif html_admon_style in ('lyx',) or html_admon_style.startswith('paragraph'):
                css += admon_styles_text.replace('%%', '%')
                break

    style = css_style % (css_links, css)
    css_filename = option('css=')
    if css_filename:
        style = ''
        if ',' in css_filename:
            css_filenames = css_filename.split(',')
        else:
            css_filenames = [css_filename]
        for css_filename in css_filenames:
            if css_filename:
                if not os.path.isfile(css_filename):
                    # Put the style in the file when the file does not exist
                    f = open(css_filename, 'w')
                    f.write(css)
                    f.close()
                style += '<link rel="stylesheet" href="%s">\n' % css_filename
                add_to_file_collection(css_filename)


    if html_style.startswith('boots'):
        boots_version = '3.1.1'
        if html_style == 'bootstrap':
            boots_style = 'boostrap'
            urls = ['https://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version]
        elif html_style == 'bootstrap_bootflat':
            boots_style = 'bootflat'
            urls = ['https://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version,
                    'RAW_GITHUB_URL/bootflat/bootflat.github.io/master/bootflat/css/bootflat.css']
        elif html_style.startswith('bootstrap_'):
            # Local DocOnce stored or modified bootstrap themes
            boots_style = html_style.split('_')[1]
            urls = ['https://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version,
                    'RAW_GITHUB_URL/doconce/doconce/master/bundled/html_styles/style_bootstrap/css/%s.css' % html_style]
        elif html_style.startswith('bootswatch'):
            default = 'cosmo'
            boots_style = default if 'bootswatch_' not in html_style else \
                          html_style.split('_')[1]
            legal_bootswatch_styles = 'cerulean cosmo flatly journal lumen readable simplex spacelab united yeti amelia cyborg darkly slate spruce superhero'.split()
            if boots_style not in legal_bootswatch_styles:
                errwarn('*** error: wrong bootswatch style %s' % boots_style)
                errwarn('    legal choices:\n    %s' % ', '.join(legal_bootswatch_styles))
                _abort()
            urls = ['https://netdna.bootstrapcdn.com/bootswatch/%s/%s/bootstrap.min.css' % (boots_version, boots_style)]
            # Dark styles need some recommended options
            dark_styles = 'amelia cyborg darkly slate superhero'.split()
            if boots_style in dark_styles:
                if not option('keep_pygments_html_bg') or option('pygments_html_style=', None) is None or \
                        option('html_code_style=', None) is None or option('html_pre_style=', None) is None:
                    errwarn(('\n'
                             '*** warning: bootswatch style "%s" is dark and some\n'
                             '    options to doconce format html are recommended:\n'
                             '    --pygments_html_style=monokai     # dark background\n'
                             '    --keep_pygments_html_bg           # keep code background in admons\n'
                             '    --html_code_style=inherit         # use <code> style in surroundings (no red)\n'
                             '    --html_pre_style=inherit          # use <pre> style in surroundings\n') %
                            boots_style)
        else:
            errwarn('*** wrong --html_style=%s' % html_style)
            _abort()

        style = ('\n'
                 '<!-- Bootstrap style: %s -->\n'
                 '<!-- doconce format html %s %s -->\n'
                 '%s\n'
                 '<!-- not necessary\n'
                 '<link href="https://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css" rel="stylesheet">\n'
                 '-->\n') % (html_style,
                             globals.filename,
                             ' '.join(sys.argv[1:]),
                             '\n'.join(['<link href="%s" rel="stylesheet">' % url for url in urls]))

    style_changes = ''
    if option('html_code_style=', 'on') in ('off', 'transparent', 'inherit'):
        style_changes += ('\n'
                          '/* Let inline verbatim have the same color as the surroundings */\n'
                          'code { color: inherit; background-color: transparent; }\n')
    if option('html_pre_style=', 'on') in ('off', 'transparent', 'inherit'):
        style_changes += ('\n'
                          '/* Let pre tags for code blocks have the same color as the surroundings */\n'
                          'pre { color: inherit; background-color: transparent; }\n')
    if html_style.startswith('boots'):
        height = 50  # fixed header hight in pixels, varies with style
        if 'bootswatch' in html_style:
            _style = html_style.split('_')[-1]
            if _style in ('simplex', 'superhero'):
                height = 40
            elif _style in ('yeti',):
                height = 45
            elif _style in ('cerulean', 'cosmo', 'lumen', 'spacelab', 'united', 'slate', 'cyborg', 'amelia'):
                height = 50
            elif _style.startswith('journal') or _style in ('flatly', 'darkly'):
                height = 60
            elif _style in ('readable',):
                height = 64
        if html_style.startswith('bootstrap'):
            height = 50
        style_changes += (
                             '/* Add scrollbar to dropdown menus in bootstrap navigation bar */\n'
                             '.dropdown-menu {\n'
                             '   height: auto;\n'
                             '   max-height: 400px;\n'
                             '   overflow-x: hidden;\n'
                             '}\n'
                             '\n'
                             '/* Adds an invisible element before each target to offset for the navigation\n'
                             '   bar */\n'
                             '.anchor::before {\n'
                             '  content:"";\n'
                             '  display:block;\n'
                             '  height:%spx;      /* fixed header height for style %s */\n'
                             '  margin:-%spx 0 0; /* negative fixed header height */\n'
                             '}\n') % (height, html_style, height)
        if '!bquiz' in filestr:
            # Style for buttons for collapsing paragraphs
            style_changes += ('\n'
                              '/*\n'
                              "in.collapse+a.btn.showdetails:before { content:'Hide details'; }\n"
                              ".collapse+a.btn.showdetails:before { content:'Show details'; }\n"
                              '*/\n')
    body_style = option('html_body_style=', None)
    if body_style is not None:
        style_changes += ('\n'
                          'body { %s; }\n') % body_style
    if style_changes:
        style += ('\n'
                  '<style type="text/css">\n'
                  '%s</style>\n') % style_changes

    # Add sharing buttons
    url = option('html_share=', None)
    if url is not None:
        style += share(code_type='css')

    meta_tags = ('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
                 '<meta name="generator" content="DocOnce: https://github.com/doconce/doconce/" />\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n')
    bootstrap_title_bar = ''
    title = ''
    m = re.search(r'^TITLE: *(.+)$', filestr, flags=re.MULTILINE)
    if m:
        title = m.group(1).strip()
        meta_tags += '<meta name="description" content="%s">\n' % title

        if html_style.startswith('boots'):

            # Make link back to the main HTML file
            outfilename = option('html_output=', None)
            if outfilename is None:
                outfilename = globals.dofile_basename + '.html'
            else:
                outfilename = outfilename.strip('.html') + '.html'
                if not outfilename.endswith('.html'):
                    outfilename += '.html'

            if option('html_bootstrap_navbar=', 'on') != 'off':
                custom_links = option('html_bootstrap_navbar_links=', None)
                code_custom_links = ''
                if custom_links is not None:
                    custom_links = custom_links.split(';')
                    for custom_link in custom_links:
                        link, url = custom_link.split('|')
                        link = link.strip()
                        url = url.strip()
                        code_custom_links += \
                            ('\n'
                             '  <div class="navbar-header">\n'
                             '    <button type="button" class="navbar-toggle" data-toggle="collapse" '
                             'data-target=".navbar-responsive-collapse">\n'
                             '      <span class="icon-bar"></span>\n'
                             '      <span class="icon-bar"></span>\n'
                             '      <span class="icon-bar"></span>\n'
                             '    </button>\n'
                             '    <a class="navbar-brand" href="%s">%s</a>\n'
                             '  </div>\n') % (url, link)

                bootstrap_title_bar = \
                    ('\n'
                     '<!-- Bootstrap navigation bar -->\n'
                     '<div class="navbar navbar-default navbar-fixed-top">\n'
                     '  <div class="navbar-header">\n'
                     '    <button type="button" class="navbar-toggle" data-toggle="collapse" '
                     'data-target=".navbar-responsive-collapse">\n'
                     '      <span class="icon-bar"></span>\n'
                     '      <span class="icon-bar"></span>\n'
                     '      <span class="icon-bar"></span>\n'
                     '    </button>\n'
                     '    <a class="navbar-brand" href="%s">%s</a>\n'
                     '  </div>\n'
                     '%s\n'
                     '  <div class="navbar-collapse collapse navbar-responsive-collapse">\n'
                     '    <ul class="nav navbar-nav navbar-right">\n'
                     '      <li class="dropdown">\n'
                     '        <a href="#" class="dropdown-toggle" data-toggle="dropdown">***CONTENTS_PULL_DOWN_MENU*** '
                     '<b class="caret"></b></a>\n'
                     '        <ul class="dropdown-menu">\n'
                     '***TABLE_OF_CONTENTS***\n'
                     '        </ul>\n'
                     '      </li>\n'
                     '    </ul>\n'
                     '  </div>\n'
                     '</div>\n'
                     '</div> <!-- end of navigation bar -->\n') % \
                    (outfilename, title, code_custom_links)


    keywords = re.findall(r'idx\{([^\{\}]*(?:\{[^\}]*\})?[^\}]*)\}', filestr)
    # idx with verbatim is usually too specialized - remove them
    # Strip cross-references as well
    keywords = [keyword.split('|')[0] for keyword in keywords
                if not '`' in keyword]
    # Keywords paragraph
    from . import common
    m = re.search(INLINE_TAGS['keywords'], filestr, flags=re.MULTILINE)
    if m:
        keywords += re.split(r', *', m.group(1))
    # keyword!subkeyword -> keyword subkeyword
    keywords = ','.join(keywords).replace('!', ' ')

    if keywords:
        meta_tags += '<meta name="keywords" content="%s">\n' % keywords

    scripts = ''
    if option('pygments_html_style=', 'default') == 'highlight.js':
        scripts += ('\n'
                    '<!-- use highlight.js and styles for code -->\n'
                    '<script src="RAW_GITHUB_URL/doconce/doconce/master/bundled/html_styles'
                    '/style_solarized_box/js/highlight.pack.js"></script>\n'
                    '<script>hljs.initHighlightingOnLoad();</script>\n'
)

    if '!bc pyscpro' in filestr or 'envir=pyscpro' in filestr:
        # Embed Sage Cell server
        # See https://github.com/sagemath/sagecell/blob/master/doc/embedding.rst
        scripts += ('\n'
                    '<script src="https://sagecell.sagemath.org/static/jquery.min.js"></script>\n'
                    '<script src="https://sagecell.sagemath.org/embedded_sagecell.js"></script>\n'
                    '<link rel="stylesheet" type="text/css" href="https://sagecell.sagemath.org/static/sagecell_embed.css">\n'
                    '<script>\n'
                    '$(function () {\n'
                    '   // Make *any* div with class "sage_compute" a Sage cell\n'
                    '   sagecell.makeSagecell({inputLocation: "div.sage_compute",\n'
                    '                          evalButtonText: "Evaluate"});\n'
                    '   document.getElementsByClassName("sage_compute")[0].closest(".input").style.paddingBottom=95;\n'
                    '});\n'
                    '</script>\n')

    if '!bu-' in filestr:
        scripts += "\n<!-- USER-DEFINED ENVIRONMENTS -->\n"

    # Had to take DOCTYPE out from 1st line to load css files from github...
    # <!DOCTYPE html>
    INTRO['html'] = ('<!--\n'
                     'HTML file automatically generated from DocOnce source\n'
                     '(https://github.com/doconce/doconce/)\n'
                     'doconce format html %s %s\n'
                     '-->\n') % (globals.filename, ' '.join(sys.argv[1:]))
    INTRO['html'] += ('<html>\n'
                     '<head>\n'
                     '%s\n'
                     '<title>%s</title>\n'
                     '%s\n'
                     '%s\n'
                     '</head>\n'
                     '<body>\n\n') % (meta_tags, title, style, scripts)

    OUTRO['html'] = ''
    if html_style.startswith('boots'):
        INTRO['html'] += bootstrap_title_bar
        INTRO['html'] += ('\n'
                          '<div class="container">\n'
                          "\n"
                          '<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p> <!-- add vertical space -->\n')

        OUTRO['html'] += ('\n'
                          '</div>  <!-- end container -->\n'
                          '<!-- include javascript, jQuery *first* -->\n'
                          '<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>\n'
                          '<script src="https://netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>\n'
                          '\n'
                          '<!-- Bootstrap footer\n'
                          '<footer>\n'
                          '<a href="https://..."><img width="250" align=right src="https://..."></a>\n'
                          '</footer>\n'
                          '-->\n')

    # Need for jquery library? !bc pypro-h (show/hide button for code)
    m = re.search(r'^!bc +([a-z0-9]+)-h', filestr, flags=re.MULTILINE)
    if m and 'ajax.googleapis.com/ajax/libs/jquery' not in OUTRO['html']:
        OUTRO['html'] += ('\n'
                          '<script type="text/javascript" '
                          'src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.js"></script>\n')


    from .common import has_copyright
    copyright_, symbol = has_copyright(filestr)
    if copyright_:
        OUTRO['html'] += ('\n'
                          '\n'
                          '<center style="font-size:80%">\n'
                          '<!-- copyright --> {} Copyright COPYRIGHT_HOLDERS\n'
                          '</center>\n').format("&copy;" if symbol else "")
    OUTRO['html'] += ('\n'
                      '\n'
                      '</body>\n'
                      '</html>\n')

def latin2html(text):
    """
    Transform a text with possible latin-1 characters to the
    equivalent valid text in HTML with all special characters
    with ordinal > 159 encoded as &#number;

    Method: convert from plain text (open(filename, 'r')) to utf-8,
    run through each character c, if ord(c) > 159,
    add the HTML encoded text to a list, otherwise just add c to the list,
    then finally join the list to make the new version of the text.

    Note: A simpler method is just to set
    <?xml version="1.0" encoding="utf-8" ?>
    as the first line in the HTML file, see how rst2html.py
    starts the HTML file.
    (However, the method below shows how to cope with special
    European characters in general.)

    :param str text: text to be converted to html
    :return: html code
    :rtype: str
    """
    # Only run this algorithm for plain ascii files, otherwise
    # text is unicode utf-8 which is easily shown without encoding
    # non-ascii characters in html.
    if not isinstance(text, str):
        return text

    text_new = []
    for c in text:
        try:
            if ord(c) > 159:
                text_new.append('&#%d;' % ord(c))
            else:
                text_new.append(c)
        except Exception as e:
            errwarn('character causing problems: ' + c)
            raise e.__class__('%s: character causing problems: %s' % \
                              (e.__class__.__name__, c))
    return ''.join(text_new)


def html2latin(html):
    """
    Transform a HTML text with possible special characters to the
    equivalent text with latin-1 characters. This is the opposite of
    the latin2html function.
    Note: A simpler method would be to use `import html; html.unescape(html)`

    :param str html: html code
    :return: text - conversion of html to latin text
    :rtype: str
    """
    if not isinstance(html, str):
        return html
    unicode_chars = re.findall(r'(?:&#)(\d+)(?:;)', html)
    unicode_chars = list(set(unicode_chars))
    text = html
    for u in unicode_chars:
        try:
            text = re.sub(r'&#'+u+';', chr(int(u)), text)
        except Exception as e:
            errwarn('unicode character causing problems: ' + '&#'+u+';')
            raise e.__class__('%s: character causing problems: %s' % \
                              (e.__class__.__name__, '&#'+u+';'))
    return text


def string2href(title=''):
    """ Create strings that are safe to pass to href in anchors or other html tag properties

    Given a header with a title e.g. " Section 1: what's this å? ", create a string e.g.
    "section-1-what-s-this-&#229;" that can be safely passed to href in anchor links (<a href=.../>).

    :param str title: title of the heading
    :return: href
    :rtype: str
    """
    href = re.sub('[\W_]+', '-', title.lower())
    href = latin2html(href)
    return href.strip('-')


def get_pygments_style(code_block_types):
    """ Return pygments version and pygments style used

    `pygm` is the pygments version. Abort if it is None and
    `--pygments_html_style` is used.
    :param code_block_types:
    :return: pygm, pygm_style
    :rtype: str, str
    """
    pygm_style = option('pygments_html_style=', default='default')
    legal_pygm_styles = 'monokai manni rrt perldoc borland colorful default murphy vs trac tango fruity autumn ' \
                        'bw emacs vim pastie friendly native'.split()
    global pygm
    if pygm_style in ['none', 'None', 'off', 'no']:
        pygm_style = 'off'
        return pygm, pygm_style
    elif pygm_style not in legal_pygm_styles:
        errwarn('*** error: wrong pygments style "%s"' % pygm_style)
        errwarn('    must be among\n%s' % str(legal_pygm_styles)[1:-1])
        _abort()
    if pygm_style and pygm is None:
        errwarn('*** error: pygments could not be found though '
                '--pygments_html_style="%s" is used' % pygm_style)
        _abort()
    # Can turn off pygments on the cmd line
    if pygm is not None:
        if 'ipy' in code_block_types:
            if not has_custom_pygments_lexer('ipy'):
                envir2syntax['ipy'] = 'python'
        if 'do' in code_block_types:
            if not has_custom_pygments_lexer('doconce'):
                envir2syntax['do'] = 'text'
        if pygm_style is None:
            # Set sensible default values
            if option('html_style=', '').startswith('solarized'):
                if 'pyscpro' in code_block_types:
                    # Must have pygments style for Sage Cells to work
                    pygm_style = 'perldoc'
                else:
                    pygm_style = 'none'
                    # 2nd best: perldoc (light), see below
            elif option('html_style=', '').startswith('tactile'):
                pygm_style = 'trac'
            elif option('html_style=', '') == 'rossant':
                pygm_style = 'monokai'
            else:
                pygm_style = 'default'
        else:
            # Fix style for solarized and rossant
            if option('html_style=') == 'solarized':
                if pygm_style != 'perldoc':
                    errwarn('*** warning: --pygm_style=%s is not recommended when --html_style=solarized' % pygm_style)
                    errwarn('    automatically changed to --html_style=perldoc')
                    pygm_style = 'perldoc'
            elif option('html_style=') == 'solarized_dark':
                if pygm_style != 'friendly':
                    errwarn('*** warning: --pygm_style=%s is not recommended when --html_style=solarized_dark' % pygm_style)
                    errwarn('    automatically changed to --html_style=friendly')
                    errwarn('    (it is recommended not to specify --pygm_style for solarized_dark)')
                    pygm_style = 'friendly'
        legal_styles = list(get_all_styles()) + ['none', 'None', 'off', 'no']
        if pygm_style not in legal_styles:
            errwarn('pygments style "%s" is not legal, must be among\n%s' % (pygm_style, ', '.join(legal_styles)))
            #_abort()
            errwarn('using the "default" style...')
            pygm_style = 'default'
        if pygm_style in ['none', 'None', 'off', 'no']:
            pygm = None
    return pygm, pygm_style
