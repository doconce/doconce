from __future__ import print_function
from __future__ import absolute_import
#from __future__ import division
from past.builtins import execfile
from future import standard_library
standard_library.install_aliases()
#from builtins import zip
#from builtins import str
from builtins import range
from past.builtins import basestring
import os, sys, re
from .misc import get_header_parts_footer, misc_option, remove_verbatim_blocks, \
    copy_latex_packages, copy_datafiles, tablify, get_header_parts_footer, doconce_split_html, \
    errwarn, _abort
from .html import html_remove_whitespace, add_to_file_collection
import pkgutil
from io import BytesIO
import zipfile

reveal_files = 'reveal.js.zip'
csss_files = 'csss.zip'
deck_files = 'deck.js-latest.zip'


def recommended_html_styles_and_pygments_styles():
    """
    List good combinations of HTML slide styles and
    pygments styles for typesetting code.
    """
    combinations = {
        'html': {
            'blueish': ['default'],
            'bloodish': ['default'],
            'solarized': ['perldoc'],
            'solarized2': ['perldoc'],
            'solarized3': ['perldoc'],
            'solarized3_dark': ['native'],
            },
        'deck': {
            'neon': ['fruity', 'native'],
            'sandstone.aurora': ['fruity'],
            'sandstone.dark': ['native', 'fruity'],
            'sandstone.mdn': ['fruity'],
            'sandstone.mightly': ['default', 'autumn', 'manni', 'emacs'],
            'beamer': ['autumn', 'perldoc', 'manni', 'default', 'emacs'],
            'mnml': ['default', 'autumn', 'manni', 'emacs'],
            'sandstone.firefox': ['default', 'manni', 'autumn', 'emacs'],
            'sandstone.default': ['perldoc', 'autumn', 'manni', 'default'],
            'sandstone.light': ['emacs', 'autumn'],  # purple
            'swiss': ['autumn', 'default', 'perldoc', 'manni', 'emacs'],
            'web-2.0': ['autumn', 'default', 'perldoc', 'emacs'],
            'cbc': ['default', 'autumn'],
            },
        'reveal': {
            'beige': ['perldoc',],
            'beigesmall': ['perldoc',],
            'solarized': ['perldoc',],
            'serif': ['perldoc'],
            'simple': ['autumn', 'default', 'perldoc'],
            'white': ['autumn', 'default', 'perldoc'],
            'blood': ['monokai', 'native'],
            'black': ['monokai', 'native'],
            'sky': ['default'],
            'moon': ['fruity', 'native'],
            'night': ['fruity', 'native'],
            'moon': ['fruity', 'native'],
            'darkgray': ['native', 'monokai'],
            'league': ['native', 'monokai'],
            'cbc': ['default', 'autumn'],
            'simula': ['autumn', 'default'],
            },
        'csss': {
            'csss_default': ['monokai'],
            },
        'dzslides': {
            'dzslides_default': ['autumn', 'default'],
            },
        'html5slides': {
            'template-default': ['autumn', 'default'],
            'template-io2011': ['autumn', 'default'],
            },
        'remark': {
            'light': ['autumn', 'default'],
            'dark': ['native', 'monokai'],
            },
        }
    return combinations


def _usage_slides_html():
    print('Usage:\n'
          'doconce slides_html mydoc.html (reveal | deck | csss | dzslides) --html_slide_theme=theme\n'
          '--html_slide_transition=theme --html_footer_logo=name --nav_button=name\n'
          '--font_size=slides --copyright=everypage|titlepage\n'
          '\n'
          'Alternative usage:  doconce slides_html mydoc.html all  #generate all types of slides\n'
          '\n'
          'Options:\n'
          '--html_slide_theme=theme sets the theme for the reveal.js or deck.js slides:\n'
          '  reveal.js: beige, beigesmall, solarized, serif, simple, blood, sky,\n'
          '    moon, night, moon, darkgray, cbc, simula, black, white, league\n'
          '  deck.js: neon, sandstone.aurora, sandstone.dark, sandstone.mdn,\n'
          '    sandstone.mightly, sandstone.firefox, sandstone.default,\n'
          '    sandstone.light, beamer, mnml, swiss, web-2.0, cbc\n'
          '--html_slide_transition=theme sets the theme for reveal.js or deck.js slides:\n'
          '  reveal.js: fade, slide, convex, concave, zoom. Default: none\n'
          '  deck.js: horizontal-slide, vertical-slide, fade. Default: none\n'
          '--html_footer_logo=name sets the footer logo to be used, name is a full URL to the\n'
          '  logo image file, or cbc_footer, cbc_symbol, simula_footer, simula_symbol,\n'
          '  uio_footer, uio_symbol (for which the full path is automatically created)\n'
          '--nav_button=name sets the type of navigation button (next, previous):\n'
          '  text, gray1 (default), gray2, bigblue, blue, green.\n'
          '  See https://raw.github.com/doconce/doconce/master/doc/src/manual/fig/nav_buttons.png\n'
          '  for examples on these types (from left to right).\n'
          '  A value like gray2,top gives buttons only at the top of the page,\n'
          '  gray2,top+bottom gives buttons at the top and bottom (default), while\n'
          '  gray2,bottom gives buttons only at the bottom.\n'
          '  If the "doconce format html" command used bootstrap styles (with\n'
          '  --html_style=bootstrap*|bootswatch*), set just --nav_button=top or\n'
          '  bottom (default) or top+bottom.\n'
          '--font_size= is used to increase the font size for slides.\n'
          '--font_size=slides gives 140% font size in the body text.\n'
          '--font_size=180 gives 180% font size in the body text.\n'
          '--pagination means that one can click on page numbers if a bootstrap\n'
          '  theme is used in the document.\n'
          '--copyright=everypage gives a copyright notice in the footer of\n'
          '  every page (if {copyright...} is specified as part of AUTHOR commands).\n'
          '  With --copyright=titlepage (default), the copyright only appears on\n'
          '  the title page only.\n\n'
          'Notes:\n'
          'reveal and deck slide styles are doconce variants, different from the original styles.\n'
          '        (remark style is not generated by slides_html, but by slides_markdown)\n\n'
          'if doconce is used as slide style, the doconce split_html command is\n'
          '  more versatile than slides_html since it allows the --method\n'
          '  argument, which can be used for physical splits (as in slides_html)\n'
          '  or "split" via just space or rules for separating the parts in\n'
          '  one (big) file.')


def slides_html():
    """
    Split html file into slides and typeset slides using
    various tools. Use !split command as slide separator.
    """
    # Overview: https://www.impressivewebs.com/html-slidedeck-toolkits/
    # Overview: https://www.sitepoint.com/5-free-html5-presentation-systems/
    # x https://leaverou.github.com/CSSS/
    # x https://lab.hakim.se/reveal-js/ (easy and fancy)
    # x https://paulrouget.com/dzslides/ (easy and fancy, Keynote like)
    # https://imakewebthings.com/deck.js/ (also easy)
    # https://code.google.com/p/html5slides/ (also easy)
    # https://slides.seld.be/?file=2010-05-30+Example.html#1 (also easy)
    # https://www.w3.org/Talks/Tools/Slidy2/#(1) (also easy)
    # https://johnpolacek.github.com/scrolldeck.js/ (inspired by reveal.js)
    # https://meyerweb.com/eric/tools/s5/ (easy)
    # https://github.com/mbostock/stack (very easy)
    # https://github.com/markdalgleish/fathom
    # https://shama.github.com/jmpress.js/#/home  # jQuery version of impress
    # https://github.com/bartaz/impress.js/

    # Fancy and instructive demo:
    # https://yihui.name/slides/2011-r-dev-lessons.html
    # (view the source code)

    # pandoc can make dzslides and embeds all javascript (no other files needed)
    # pandoc -s -S -i -t dzslides --mathjax my.md -o my.html

    if len(sys.argv) <= 2:
        _usage_slides_html()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.html'):
        filename += '.html'
    if not os.path.isfile(filename):
        errwarn('*** error: doconce file in html format, %s, does not exist' % filename)
        _abort()
    basename = os.path.basename(filename)
    filestem = os.path.splitext(basename)[0]

    slide_type = sys.argv[2]

    for arg in sys.argv[1:]:
        if arg.startswith('--method='):
            opt = arg.split('=')[1]
            if opt != 'split':
                errwarn('*** error: slides_html cannot accept --method=%s' % opt)
                errwarn('    (the slides will always be split)')
                errwarn('    use split_html with --method=...')
                _abort()

    # Treat the special case of generating a script for generating
    # all the different slide versions that are supported
    if slide_type == 'all':
         r = recommended_html_styles_and_pygments_styles()
         f = open('tmp_slides_html_all.sh', 'w')
         f.write('#!/bin/sh\n\n')
         f.write('doconce format html %s SLIDE_TYPE=dummy SLIDE_THEME=dummy\ndoconce slides_html %s doconce\n\n' %
                 (filestem, filestem))
         for sl_tp in r:
             for style in r[sl_tp]:
                 pygm_style = r[sl_tp][style][0]
                 if sl_tp == 'html':
                     if style.startswith('solarized'):
                         f.write('doconce format html %s SLIDE_TYPE=%s SLIDE_THEME=%s --html_style=%s --html_output=%s_html_%s\ndoconce slides_html %s_html_%s doconce --nav_button=gray2,bottom --font_size=slides\n\n' % (filestem, sl_tp, style, style, filestem, style, filestem, style))
                         if style == 'solarized3':
                             f.write('doconce format html %s SLIDE_TYPE=%s SLIDE_THEME=%s --html_style=%s --html_output=%s_html_%s_space\ndoconce split_html %s_html_solarized3_space --method=space10\n\n' % (filestem, sl_tp, style, style, filestem, style, filestem))
                     else:
                         method = 'colorline' if style == 'blueish' else 'space8'
                         f.write('doconce format html %s --pygments_html_style=%s --keep_pygments_html_bg SLIDE_TYPE=%s SLIDE_THEME=%s --html_style=%s --html_output=%s_html_%s\ndoconce split_html %s_html_%s --method=%s  # one long file\n\n' % (filestem, pygm_style, sl_tp, style, style, filestem, style, filestem, style, method))
                 else:
                     f.write('doconce format html %s --pygments_html_style=%s --keep_pygments_html_bg SLIDE_TYPE=%s SLIDE_THEME=%s\ndoconce slides_html %s %s --html_slide_theme=%s\ncp %s.html %s_%s_%s.html\n\n' % (filestem, pygm_style, sl_tp, style, filestem, sl_tp, style, filestem, filestem, sl_tp, style.replace('.', '_')))
         f.write('echo "Here are the slide shows:"\n/bin/ls %s_*_*.html\n' % filestem)
         print('run\n  sh tmp_slides_html_all.sh\nto generate the slides')
         return


    # --- Create a slide presentation from the HTML file ---

    header, parts, footer = get_header_parts_footer(filename, "html")
    parts = tablify(parts, "html")

    filestr = None
    if slide_type == 'doconce':
        doconce_split_html(header, parts, footer, filestem, filename, slides=True)
    elif slide_type in ('reveal', 'csss', 'dzslides', 'deck', 'html5slides'):
        filestr = generate_html5_slides(header, parts, footer, basename, filename, slide_type)
    else:
        errwarn('*** unknown slide type "%s"' % slide_type)

    if filestr is not None:
        # Make whitespace nicer (clean up code)
        filestr = html_remove_whitespace(filestr)
        # More fixes for html5 slides
        filestr = re.sub(r'<section>\s+(?=<h[12])', r'<section>\n', filestr)
        filestr = re.sub(r'<p>\n</section>', '</section>', filestr)
        filestr = re.sub(r'\s+</section>', '\n</section>', filestr)
        filestr = html_remove_whitespace(filestr)
        # More fixes for html5 slides
        filestr = re.sub(r'<section>\s+(?=<h[12])', r'<section>\n', filestr)
        filestr = re.sub(r'<p>\n</section>', '</section>', filestr)
        filestr = re.sub(r'\s+</section>', '\n</section>', filestr)

        f = open(filename, 'w')
        f.write(filestr)
        f.close()
        print('slides written to ' + filename)


css_deck = ('\n'
            '<style type="text/css">\n'
            '/* Override h1, h2, ... styles */\n'
            'h1 { font-size: 2.8em; }\n'
            'h2 { font-size: 1.5em; }\n'
            'h3 { font-size: 1.4em; }\n'
            'h4 { font-size: 1.3em; }\n'
            'h1, h2, h3, h4 { font-weight: bold; line-height: 1.2; }\n'
            'body { overflow: auto; } /* vertical scrolling */\n'
            'hr { border: 0; width: 80%%; border-bottom: 1px solid #aaa}\n'
            'p.caption { width: 80%%; font-size: 60%%; font-style: italic; text-align: left; }\n'
            'hr.figure { border: 0; width: 80%%; border-bottom: 1px solid #aaa}\n'
            '.slide .alert-text-small   { font-size: 80%%;  }\n'
            '.slide .alert-text-large   { font-size: 130%%; }\n'
            '.slide .alert-text-normal  { font-size: 90%%;  }\n'
            '.slide .alert {\n'
            '  padding:8px 35px 8px 14px; margin-bottom:18px;\n'
            '  text-shadow:0 1px 0 rgba(255,255,255,0.5);\n'
            '  border:5px solid #bababa;\n'
            '    -webkit-border-radius:14px; -moz-border-radius:14px;\n'
            '  border-radius:14px\n'
            '  background-position: 10px 10px;\n'
            '  background-repeat: no-repeat;\n'
            '  background-size: 38px;\n'
            '  padding-left: 30px; /* 55px; if icon */\n'
            '}\n'
            '.slide .alert-block {padding-top:14px; padding-bottom:14px}\n'
            '.slide .alert-block > p, .alert-block > ul {margin-bottom:0}\n'
            '/*.slide .alert li {margin-top: 1em}*/\n'
            '.deck .alert-block p+p {margin-top:5px}\n'
            '/*.slide .alert-notice { background-image: url(https://hplgit.github.io/doconce/\n'
            'bundled/html_images//small_gray_notice.png); }\n'
            '.slide .alert-summary  { background-image:url(https://hplgit.github.io/doconce/\n'
            'bundled/html_images//small_gray_summary.png); }\n'
            '.slide .alert-warning { background-image: url(https://hplgit.github.io/doconce/\n'
            'bundled/html_images//small_gray_warning.png); }\n'
            '.slide .alert-question {background-image:url(https://hplgit.github.io/doconce/\n'
            'bundled/html_images/small_gray_question.png); } */\n'
            '.dotable table, .dotable th, .dotable tr, .dotable tr td {\n'
            '  border: 2px solid black;\n'
            '  border-collapse: collapse;\n'
            '  padding: 2px;\n'
            '}\n'
            '</style>\n\n')

def list_package_data(pkg_data, folder='', suffix=''):
    """List the files inside a package data zip

    The `setup.py` uses a `package_data` keyword to store
    package data. This function loads a `pkg_data` zip file
    and returns a list of the content.
    :param str pkg_data: a package data file listed in `setup.py` > `package_data`
    :param str folder: filter the content on the folder (can be any string)
    :param str suffix: filter the content on suffix (can be any string)
    :return: content of package data
    :rtype: list[str]
    """
    # Get the zip file in the package data
    try:
        package_data = pkgutil.get_data('doconce', pkg_data)
        fobject = BytesIO(package_data)
        zip_obj = zipfile.ZipFile(fobject)
    except IOError as e:
        errwarn('*** error: %s' % str(e))
        errwarn('*** could not retrieve the package data %s' % pkg_data)
        _abort()
    # Get a file inside the zip package, e.g. the deck.js boilerplate
    content = zip_obj.namelist()
    content = list(filter(lambda x: x.startswith(folder) and x.endswith(suffix), content))
    return content

def get_package_data(pkg_data, data_file):
    """Read a file inside a package data zip

    The `setup.py` uses a `package_data` keyword to store
    package data. This function loads a `pkg_data` zip file
    and reads a file therein.
    :param str pkg_data: a package data file listed in `setup.py` > `package_data`
    :param str data_file: a file in pkg_data
    :return: file read out from the zip package
    :rtype: str
    """
    # Get the zip file in the package data
    try:
        package_data = pkgutil.get_data('doconce', pkg_data)
        fobject = BytesIO(package_data)
        zip_obj = zipfile.ZipFile(fobject)
    except IOError as e:
        errwarn('*** error: %s' % str(e))
        errwarn('*** could not retrieve the package data %s' % pkg_data)
        _abort()
    # Get a file inside the zip package, e.g. the deck.js boilerplate
    text = zip_obj.read(data_file).decode('utf-8')
    if not text:
        errwarn('*** error: could not retrieve the boilerplate from Deck.js %s ' % data_file)
        _abort()
    return text

def get_deck_header(info='<!-- deck.js: https://github.com/imakewebthings/deck.js -->\n',
                         css_overrides=css_deck):
    """Extract the header of the boilerplate from deck.js zip file

    The boilerplate file is stored in the unzipped deck.js-latest.zip file
    :param str info: comment or code to add on top of the header
    :param str css_overrides: css code to append to boilerplate
    :return: processed boilerplate
    :rtype: str
    """
    # Get the deck.js boilerplate
    deck_folder = deck_files.replace('.zip', '') + '/'
    fname = os.path.join(deck_folder, 'boilerplate.html')
    boilerplate = get_package_data(deck_files, data_file=fname)
    # Fix the paths to resources in links i.e. add 'deck-latest.js/' in all href/src
    boilerplate = boilerplate.replace('href="', 'href="' + deck_folder)
    boilerplate = boilerplate.replace('src="', 'src="' + deck_folder)
    boilerplate.replace('"'+deck_folder+'#"', '"#"')
    # Get the section within the <head> tags, but remove the <title> tag
    output = boilerplate[boilerplate.find('<head>')+6:boilerplate.find('</head>')]
    output = re.sub(r'\s*<title>[^<>]*</title>\s*', '', output)
    output = info + output + '\n' + css_overrides
    # Insert a %(theme) variable instead of the default theme
    c = re.compile(r'(?P<link><link rel="stylesheet"[^>]+themes\/style\/)[^>]+(?P<css>\.css">)')
    if not re.search(c, output):
        errwarn('*** error: could not find the theme in Deck boilerplate')
    output = re.sub(c, '\g<link>%(theme)s\g<css>', output)
    # Insert a %(theme) variable instead of the default theme
    c = re.compile(r'(?P<comment><!-- Transition theme.*-->)\n(?P<link>\s*<link [^>]*href=")(?P<href>[^>]+\.css)">', re.MULTILINE)
    if not re.search(c, output):
        errwarn('*** error: could not find the trasition theme in Deck boilerplate')
    output = re.sub(c, '\g<comment>\n\g<link>%(transition)s">', output)
    return output

def get_deck_footer(info='<footer>\n<!-- Here goes a footer -->\n</footer>\n\n'):
    """Extract the footer of the boilerplate from the deck.js zip file

    The boilerplate file is stored in the unzipped deck.js-latest.zip file
    :return: processed boilerplate
    :rtype: str
    """
    # Get the deck.js boilerplate
    deck_folder = deck_files.replace('.zip', '') + '/'
    fname = os.path.join(deck_folder, 'boilerplate.html')
    boilerplate = get_package_data(deck_files, data_file=fname)
    # Fix the paths to resources in scripts i.e. add 'deck-latest.js/' in all href/src
    boilerplate = boilerplate.replace('href="', 'href="' + deck_folder)
    boilerplate = boilerplate.replace('src="', 'src="' + deck_folder)
    boilerplate.replace('"' + deck_folder + '#"', '"#"')
    # Get the extension snippets part of the boilerplate
    output = boilerplate[boilerplate.find('<!-- Begin extension snippets'):
                           boilerplate.rfind('<!-- End extension snippets. -->') +
                           len('<!-- End extension snippets. -->')]
    # Append the section of the body with the <script> tags
    output += boilerplate[boilerplate.rfind('</div>') + 6:boilerplate.rfind('</body>')]
    output = info + output
    return output

def generate_html5_slides(header, parts, footer, basename, filename, slide_tp='reveal'):
    if slide_tp not in ['dzslides', 'html5slides']:
        zip_file = eval(slide_tp + '_files')
        copy_datafiles(zip_file)  # copy to subdir if needed

    # Copyright in the footer?
    pattern = r'<center style="font-size:80%">\n<!-- copyright --> (.+)\n</center>'
    m = re.search(pattern, ''.join(footer))
    if m:
        copyright_ = m.group().strip()
    else:
        copyright_ = ''
    html_copyright_placement = misc_option('copyright', 'titlepage')
    if html_copyright_placement == 'titlepages':
        html_copyright_placement = 'titlepage'

    slide_syntax = dict(
        reveal=dict(
            subdir='reveal.js',
            default_theme='beige',
            main_style='reveal',
            slide_envir_begin='<section>',
            slide_envir_end='</section>',
            pop=('fragment', 'li'),
            notes='<aside class="notes">\n<!-- click "s" to activate -->\n\\g<1>\n</aside>\n',
            head_header=('<!-- reveal.js: https://lab.hakim.se/reveal-js/ -->\n'
                         '\n'
                         r'<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, '
                         'user-scalable=no">\n'
                         '\n'
                         '<meta name="apple-mobile-web-app-capable" content="yes" />\n'
                         '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />\n'
                         r'<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, '
                         'user-scalable=no, minimal-ui">\n'
                         '\n'
                         '<link rel="stylesheet" href="reveal.js/css/%(main_style)s.css">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/%(theme)s.css" id="theme">\n'
                         '<!--\n'
                         '<link rel="stylesheet" href="reveal.js/css/reveal.css">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/beige.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/beigesmall.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/solarized.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/serif.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/night.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/moon.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/simple.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/sky.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/darkgray.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/default.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/cbc.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/simula.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/black.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/white.css" id="theme">\n'
                         '<link rel="stylesheet" href="reveal.js/css/theme/league.css" id="theme">\n'
                         '-->\n'
                         '\n'
                         '<!-- For syntax highlighting -->\n'
                         '<link rel="stylesheet" href="reveal.js/lib/css/zenburn.css">\n'
                         '\n'
                         '<!-- Printing and PDF exports -->\n'
                         '<script>\n'
                         'var link = document.createElement( \'link\' );\n'
                         'link.rel = \'stylesheet\';\n'
                         'link.type = \'text/css\';\n'
                         r"link.href = window.location.search.match( /print-pdf/gi ) ? 'css/print/pdf.css' : "
                         '\'css/print/paper.css\';\n'
                         'document.getElementsByTagName( \'head\' )[0].appendChild( link );\n'
                         '</script>\n'
                         '\n'
                         '<style type="text/css">\n'
                         'hr { border: 0; width: 80%%; border-bottom: 1px solid #aaa}\n'
                         'p.caption { width: 80%%; font-size: 60%%; font-style: italic; text-align: left; }\n'
                         'hr.figure { border: 0; width: 80%%; border-bottom: 1px solid #aaa}\n'
                         '.reveal .alert-text-small   { font-size: 80%%;  }\n'
                         '.reveal .alert-text-large   { font-size: 130%%; }\n'
                         '.reveal .alert-text-normal  { font-size: 90%%;  }\n'
                         '.reveal .alert {\n'
                         '  padding:8px 35px 8px 14px; margin-bottom:18px;\n'
                         '  text-shadow:0 1px 0 rgba(255,255,255,0.5);\n'
                         '  border:5px solid #bababa;\n'
                         '  -webkit-border-radius: 14px; -moz-border-radius: 14px;\n'
                         '  border-radius:14px;\n'
                         '  background-position: 10px 10px;\n'
                         '  background-repeat: no-repeat;\n'
                         '  background-size: 38px;\n'
                         '  padding-left: 30px; /* 55px; if icon */\n'
                         '}\n'
                         '.reveal .alert-block {padding-top:14px; padding-bottom:14px}\n'
                         '.reveal .alert-block > p, .alert-block > ul {margin-bottom:1em}\n'
                         '/*.reveal .alert li {margin-top: 1em}*/\n'
                         '.reveal .alert-block p+p {margin-top:5px}\n'
                         '/*.reveal .alert-notice { background-image: url(https://hplgit.github.io/doconce/'
                         'bundled/html_images/small_gray_notice.png); }\n'
                         '.reveal .alert-summary  { background-image:url(https://hplgit.github.io/doconce/'
                         'bundled/html_images/small_gray_summary.png); }\n'
                         '.reveal .alert-warning { background-image: url(https://hplgit.github.io/doconce/'
                         'bundled/html_images/small_gray_warning.png); }\n'
                         '.reveal .alert-question {background-image:url(https://hplgit.github.io/doconce/'
                         'bundled/html_images/small_gray_question.png); } */\n'
                         '/* Override reveal.js table border */\n'
                         '.reveal table td {\n'
                         '  border: 0;\n'
                         '}\n' +
                         css_deck),
            body_header=('\n'
                         '<body>\n'
                         '<div class="reveal">\n'
                         '<div class="slides">\n'),
            footer=('\n'
                    '</div> <!-- class="slides" -->\n'
                    '</div> <!-- class="reveal" -->\n'
                    '\n'
                    '<script src="reveal.js/lib/js/head.min.js"></script>\n'
                    '<script src="reveal.js/js/reveal.js"></script>\n'
                    '\n'
                    '<script>\n'
                    '// Full list of configuration options available here:\n'
                    '// https://github.com/hakimel/reveal.js#configuration\n'
                    'Reveal.initialize({\n'
                    '\n'
                    '  // Display navigation controls in the bottom right corner\n'
                    '  controls: true,\n'
                    '\n'
                    '  // Display progress bar (below the horiz. slider)\n'
                    '  progress: true,\n'
                    '\n'
                    '  // Display the page number of the current slide\n'
                    '  slideNumber: true,\n'
                    '\n'
                    '  // Push each slide change to the browser history\n'
                    '  history: false,\n'
                    '\n'
                    '  // Enable keyboard shortcuts for navigation\n'
                    '  keyboard: true,\n'
                    '\n'
                    '  // Enable the slide overview mode\n'
                    '  overview: true,\n'
                    '\n'
                    '  // Vertical centering of slides\n'
                    '  //center: true,\n'
                    '  center: false,\n'
                    '\n'
                    '  // Enables touch navigation on devices with touch input\n'
                    '  touch: true,\n'
                    '\n'
                    '  // Loop the presentation\n'
                    '  loop: false,\n'
                    '\n'
                    '  // Change the presentation direction to be RTL\n'
                    '  rtl: false,\n'
                    '\n'
                    '  // Turns fragments on and off globally\n'
                    '  fragments: true,\n'
                    '\n'
                    '  // Flags if the presentation is running in an embedded mode,\n'
                    '  // i.e. contained within a limited portion of the screen\n'
                    '  embedded: false,\n'
                    '\n'
                    '  // Number of milliseconds between automatically proceeding to the\n'
                    '  // next slide, disabled when set to 0, this value can be overwritten\n'
                    '  // by using a data-autoslide attribute on your slides\n'
                    '  autoSlide: 0,\n'
                    '\n'
                    '  // Stop auto-sliding after user input\n'
                    '  autoSlideStoppable: true,\n'
                    '\n'
                    '  // Enable slide navigation via mouse wheel\n'
                    '  mouseWheel: false,\n'
                    '\n'
                    '  // Hides the address bar on mobile devices\n'
                    '  hideAddressBar: true,\n'
                    '\n'
                    '  // Opens links in an iframe preview overlay\n'
                    '  previewLinks: false,\n'
                    '\n'
                    '  // Transition style\n'
                    '  transition: \'default\', // default/cube/page/concave/zoom/linear/fade/none\n'
                    '\n'
                    '  // Transition speed\n'
                    '  transitionSpeed: \'default\', // default/fast/slow\n'
                    '\n'
                    '  // Transition style for full page slide backgrounds\n'
                    '  backgroundTransition: \'default\', // default/none/slide/concave/convex/zoom\n'
                    '\n'
                    '  // Number of slides away from the current that are visible\n'
                    '  viewDistance: 3,\n'
                    '\n'
                    '  // Parallax background image\n'
                    r"    //parallaxBackgroundImage: '', // e.g. "
                    '"\'https://s3.amazonaws.com/hakim-static/reveal-js/reveal-parallax-1.jpg\'"\n'
                    '\n'
                    '  // Parallax background size\n'
                    '  //parallaxBackgroundSize: \'\' // CSS syntax, e.g. "2100px 900px"\n'
                    '\n'
                    '  theme: Reveal.getQueryHash().theme, // available themes are in reveal.js/css/theme\n'
                    r"    transition: Reveal.getQueryHash().transition || '%(transition)s', "
                    '// default/cube/page/concave/zoom/linear/none\n'
                    '\n'
                    '});\n'
                    '\n'
                    'Reveal.initialize({\n'
                    '  dependencies: [\n'
                    '      // Cross-browser shim that fully implements classList - '
                    'https://github.com/eligrey/classList.js/\n'
                    '      { src: \'reveal.js/lib/js/classList.js\', condition: function() { '
                    'return !document.body.classList; } },\n'
                    '\n'
                    '      // Interpret Markdown in <section> elements\n'
                    '      { src: \'reveal.js/plugin/markdown/marked.js\', condition: function() { '
                    'return !!document.querySelector( \'[data-markdown]\' ); } },\n'
                    '      { src: \'reveal.js/plugin/markdown/markdown.js\', condition: function() { '
                    'return !!document.querySelector( \'[data-markdown]\' ); } },\n'
                    '\n'
                    '      // Syntax highlight for <code> elements\n'
                    '      { src: \'reveal.js/plugin/highlight/highlight.js\', async: true, callback: function() { '
                    'hljs.initHighlightingOnLoad(); } },\n'
                    '\n'
                    '      // Zoom in and out with Alt+click\n'
                    '      { src: \'reveal.js/plugin/zoom-js/zoom.js\', async: true, condition: function() { '
                    'return !!document.body.classList; } },\n'
                    '\n'
                    '      // Speaker notes\n'
                    '      { src: \'reveal.js/plugin/notes/notes.js\', async: true, condition: function() { '
                    'return !!document.body.classList; } },\n'
                    '\n'
                    '      // Remote control your reveal.js presentation using a touch device\n'
                    '      //{ src: \'reveal.js/plugin/remotes/remotes.js\', async: true, condition: function() { '
                    'return !!document.body.classList; } },\n'
                    '\n'
                    '      // MathJax\n'
                    '      //{ src: \'reveal.js/plugin/math/math.js\', async: true }\n'
                    '  ]\n'
                    '});\n'
                    '\n'
                    'Reveal.initialize({\n'
                    '\n'
                    '  // The "normal" size of the presentation, aspect ratio will be preserved\n'
                    '  // when the presentation is scaled to fit different resolutions. Can be\n'
                    '  // specified using percentage units.\n'
                    '  width: 1170,  // original: 960,\n'
                    '  height: 700,\n'
                    '\n'
                    '  // Factor of the display size that should remain empty around the content\n'
                    '  margin: 0.1,\n'
                    '\n'
                    '  // Bounds for smallest/largest possible scale to apply to content\n'
                    '  minScale: 0.2,\n'
                    '  maxScale: 1.0\n'
                    '\n'
                    '});\n'
                    '</script>\n'
                    '\n'
                    '<!-- begin footer logo\n'
                    '<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px">\n'
                    '<img src="somelogo.png">\n'
                    '</div>\n'
                    '   end footer logo -->\n\n\n'),
            theme=None,
            transition='',
            title=None,
            ),
        csss=dict(
            subdir='csss',
            default_theme='csss_default',
            slide_envir_begin='<section class="slide">',
            slide_envir_end='</section>',
            pop=('delayed', 'li'),
            notes='<p class="presenter-notes">\n<!-- press "Ctrl+P" or "Shift+P" to activate -->\n\\g<1>\n</p>\n',
            head_header=('\n'
                         '<!-- CSSS: https://leaverou.github.com/CSSS/ -->\n'
                         '\n'
                         '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />\n'
                         '<link href="csss/slideshow.css" rel="stylesheet" />\n'
                         '<link href="csss/theme.css" rel="stylesheet" />\n'
                         '<link href="csss/talk.css" rel="stylesheet" />\n'
                         '<script src="csss/prefixfree.min.js"></script>\n'
                         '\n'),
            body_header=('\n'
                         '<body data-duration="10">\n'
                         '\n'),
            footer=('\n'
                    '<script src="csss/slideshow.js"></script>\n'
                    '<script src="csss/plugins/css-edit.js"></script>\n'
                    '<script src="csss/plugins/css-snippets.js"></script>\n'
                    '<script src="csss/plugins/css-controls.js"></script>\n'
                    '<script src="csss/plugins/code-highlight.js"></script>\n'
                    '<script>\n'
                    'var slideshow = new SlideShow();\n'
                    '\n'
                    'var snippets = document.querySelectorAll(\'.snippet\');\n'
                    'for(var i=0; i<snippets.length; i++) {\n'
                    '    new CSSSnippet(snippets[i]);\n'
                    '}\n'
                    '\n'
                    'var cssControls = document.querySelectorAll(\'.css-control\');\n'
                    'for(var i=0; i<cssControls.length; i++) {\n'
                    '    new CSSControl(cssControls[i]);\n'
                    '}\n'
                    '</script>\n'
                    '\n'),
            theme=None,
            transition='',
            title=None,
        ),
        dzslides=dict(
            subdir=None,
            default_theme='dzslides_default',  # just one theme in dzslides
            slide_envir_begin='<section>',
            slide_envir_end='</section>',
            #notes='<div role="note">\n\g<1>\n</div>',
            pop=('incremental', 'ul', 'ol'),
            notes='<details>\n<!-- use onstage shell to activate: invoke https://hplgit.github.io/doconce/'
                  'bundled/dzslides/shells/onstage.html -->\n\\g<1>\n</details>\n',
            #notes='<div role="note">\n<!-- use onstage shell to activate: invoke https://hplgit.github.io/doconce/
            # bundled/dzslides/shells/onstage.html -->\n\\g<1>\n</div>\n',
            head_header=('\n'
                         '<!-- dzslides: https://paulrouget.com/dzslides/ -->\n'
                         '\n'
                         '<!-- One section is one slide -->\n'),
            body_header=('\n'
                         '<body>\n'),
            footer=('\n'
                    '<!-- Define the style of your presentation -->\n'
                    '\n'
                    '<!--\n'
                    'Style by Hans Petter Langtangen hpl@simula.no:\n'
                    'a slight modification of the original dzslides style,\n'
                    'basically smaller fonts and left-adjusted titles.\n'
                    '-->\n'
                    '\n'
                    '<!-- Maybe a font from https://www.google.com/webfonts ? -->\n'
                    '<link href=\'https://fonts.googleapis.com/css?family=Oswald\' rel=\'stylesheet\'>\n'
                    '\n'
                    '<style>\n'
                    'html, .view body { background-color: black; counter-reset: slideidx; }\n'
                    'body, .view section { background-color: white; border-radius: 12px }\n'
                    '/* A section is a slide. It is size is 800x600, and this will never change */\n'
                    'section, .view head > title {\n'
                    '  /* The font from Google */\n'
                    '  font-family: \'Oswald\', arial, serif;\n'
                    '  font-size: 30px;\n'
                    '}\n'
                    '\n'
                    '.view section:after {\n'
                    '  counter-increment: slideidx;\n'
                    '  content: counter(slideidx, decimal-leading-zero);\n'
                    '  position: absolute; bottom: -80px; right: 100px;\n'
                    '  color: white;\n'
                    '}\n'
                    '\n'
                    '.view head > title {\n'
                    '  color: white;\n'
                    '  text-align: center;\n'
                    '  margin: 1em 0 1em 0;\n'
                    '}\n'
                    '\n'
                    'center {\n'
                    '  font-size: 20px;\n'
                    '}\n'
                    'h1 {\n'
                    '  margin-top: 100px;\n'
                    '  text-align: center;\n'
                    '  font-size: 50px;\n'
                    '}\n'
                    'h2 {\n'
                    '  margin-top: 10px;\n'
                    '  margin: 25px;\n'
                    '  text-align: left;\n'
                    '  font-size: 40px;\n'
                    '}\n'
                    'h3 {\n'
                    '  margin-top: 10px;\n'
                    '  margin: 25px;\n'
                    '  text-align: left;\n'
                    '  font-size: 30px;\n'
                    '\n'
                    '}\n'
                    '\n'
                    'ul {\n'
                    '  margin: 0px 60px;\n'
                    '  font-size: 20px;\n'
                    '}\n'
                    '\n'
                    'ol {\n'
                    '  margin: 0px 60px;\n'
                    '  font-size: 20px;\n'
                    '}\n'
                    '\n'
                    'p {\n'
                    '  margin: 25px;\n'
                    '  font-size: 20px;\n'
                    '}\n'
                    '\n'
                    'pre {\n'
                    '  font-size: 50%;\n'
                    '  margin: 25px;\n'
                    '}\n'
                    '\n'
                    'blockquote {\n'
                    '  height: 100%;\n'
                    '  background-color: black;\n'
                    '  color: white;\n'
                    '  font-size: 60px;\n'
                    '  padding: 50px;\n'
                    '}\n'
                    'blockquote:before {\n'
                    '  content: open-quote;\n'
                    '}\n'
                    'blockquote:after {\n'
                    '  content: close-quote;\n'
                    '}\n'
                    '\n'
                    '/* Figures are displayed full-page, with the caption\n'
                    '   on top of the image/video */\n'
                    'figure {\n'
                    '  background-color: black;\n'
                    '  width: 100%;\n'
                    '  height: 100%;\n'
                    '}\n'
                    'figure > * {\n'
                    '  position: absolute;\n'
                    '}\n'
                    'figure > img, figure > video {\n'
                    '  width: 100%; height: 100%;\n'
                    '}\n'
                    'figcaption {\n'
                    '  margin: 70px;\n'
                    '  font-size: 50px;\n'
                    '}\n'
                    '\n'
                    'footer {\n'
                    '  position: absolute;\n'
                    '  bottom: 0;\n'
                    '  width: 100%;\n'
                    '  padding: 40px;\n'
                    '  text-align: right;\n'
                    '  background-color: #F3F4F8;\n'
                    '  border-top: 1px solid #CCC;\n'
                    '}\n'
                    '\n'
                    '/* Transition effect */\n'
                    '/* Feel free to change the transition effect for original\n'
                    '   animations. See here:\n'
                    '   https://developer.mozilla.org/en/CSS/CSS_transitions\n'
                    '   How to use CSS3 Transitions: */\n'
                    'section {\n'
                    '  -moz-transition: left 400ms linear 0s;\n'
                    '  -webkit-transition: left 400ms linear 0s;\n'
                    '  -ms-transition: left 400ms linear 0s;\n'
                    '  transition: left 400ms linear 0s;\n'
                    '}\n'
                    '.view section {\n'
                    '  -moz-transition: none;\n'
                    '  -webkit-transition: none;\n'
                    '  -ms-transition: none;\n'
                    '  transition: none;\n'
                    '}\n'
                    '\n'
                    '.view section[aria-selected] {\n'
                    '  border: 5px red solid;\n'
                    '}\n'
                    '\n'
                    '/* Before */\n'
                    'section { left: -150%; }\n'
                    '/* Now */\n'
                    'section[aria-selected] { left: 0; }\n'
                    '/* After */\n'
                    'section[aria-selected] ~ section { left: +150%; }\n'
                    '\n'
                    '/* Incremental elements */\n'
                    '\n'
                    '/* By default, visible */\n'
                    '.incremental > * { opacity: 1; }\n'
                    '\n'
                    '/* The current item */\n'
                    '.incremental > *[aria-selected] { opacity: 1; }\n'
                    '\n'
                    '/* The items to-be-selected */\n'
                    '.incremental > *[aria-selected] ~ * { opacity: 0; }\n'
                    '\n'
                    '/* The progressbar, at the bottom of the slides, show the global\n'
                    '   progress of the presentation. */\n'
                    '#progress-bar {\n'
                    '  height: 2px;\n'
                    '  background: #AAA;\n'
                    '}\n'
                    '</style>\n'
                    '\n'
                    '<!-- {{{{ dzslides core\n'
                    '#\n'
                    '#\n'
                    '#     __  __  __       .  __   ___  __\n'
                    '#    |  \  / /__` |    | |  \ |__  /__`\n'
                    '#    |__/ /_ .__/ |___ | |__/ |___ .__/ core\n'
                    '#\n'
                    '#\n'
                    '# The following block of code is not supposed to be edited.\n'
                    '# But if you want to change the behavior of these slides,\n'
                    '# feel free to hack it!\n'
                    '#\n'
                    '-->\n'
                    '\n'
                    '<div id="progress-bar"></div>\n'
                    '\n'
                    '<!-- Default Style -->\n'
                    '<style>\n'
                    '* { margin: 0; padding: 0; -moz-box-sizing: border-box; -webkit-box-sizing: border-box; '
                    'box-sizing: border-box; }\n'
                    '[role="note"] { display: none; }\n'
                    'body {\n'
                    '  width: 800px; height: 600px;\n'
                    '  margin-left: -400px; margin-top: -300px;\n'
                    '  position: absolute; top: 50%; left: 50%;\n'
                    '  overflow: hidden;\n'
                    '  display: none;\n'
                    '}\n'
                    '.view body {\n'
                    '  position: static;\n'
                    '  margin: 0; padding: 0;\n'
                    '  width: 100%; height: 100%;\n'
                    '  display: inline-block;\n'
                    '  overflow: visible; overflow-x: hidden;\n'
                    '  /* undo Dz.onresize */\n'
                    '  transform: none !important;\n'
                    '  -moz-transform: none !important;\n'
                    '  -webkit-transform: none !important;\n'
                    '  -o-transform: none !important;\n'
                    '  -ms-transform: none !important;\n'
                    '}\n'
                    '.view head, .view head > title { display: block }\n'
                    'section {\n'
                    '  position: absolute;\n'
                    '  pointer-events: none;\n'
                    '  width: 100%; height: 100%;\n'
                    '}\n'
                    '.view section {\n'
                    '  pointer-events: auto;\n'
                    '  position: static;\n'
                    '  width: 800px; height: 600px;\n'
                    '  margin: -150px -200px;\n'
                    '  float: left;\n'
                    '\n'
                    '  transform: scale(.4);\n'
                    '  -moz-transform: scale(.4);\n'
                    '  -webkit-transform: scale(.4);\n'
                    '  -o-transform: scale(.4);\n'
                    '  -ms-transform: scale(.4);\n'
                    '}\n'
                    '.view section > * { pointer-events: none; }\n'
                    'section[aria-selected] { pointer-events: auto; }\n'
                    'html { overflow: hidden; }\n'
                    'html.view { overflow: visible; }\n'
                    'body.loaded { display: block; }\n'
                    '.incremental {visibility: hidden; }\n'
                    '.incremental[active] {visibility: visible; }\n'
                    '#progress-bar{\n'
                    '  bottom: 0;\n'
                    '  position: absolute;\n'
                    '  -moz-transition: width 400ms linear 0s;\n'
                    '  -webkit-transition: width 400ms linear 0s;\n'
                    '  -ms-transition: width 400ms linear 0s;\n'
                    '  transition: width 400ms linear 0s;\n'
                    '}\n'
                    '.view #progress-bar {\n'
                    '  display: none;\n'
                    '}\n'
                    '</style>\n'
                    '\n'
                    '<script>\n'
                    'var Dz = {\n'
                    '  remoteWindows: [],\n'
                    '  idx: -1,\n'
                    '  step: 0,\n'
                    '  html: null,\n'
                    '  slides: null,\n'
                    '  progressBar : null,\n'
                    '  params: {\n'
                    '    autoplay: "1"\n'
                    '  }\n'
                    '};\n'
                    '\n'
                    'Dz.init = function() {\n'
                    '  document.body.className = "loaded";\n'
                    '  this.slides = Array.prototype.slice.call($$("body > section"));\n'
                    '  this.progressBar = $("#progress-bar");\n'
                    '  this.html = document.body.parentNode;\n'
                    '  this.setupParams();\n'
                    '  this.onhashchange();\n'
                    '  this.setupTouchEvents();\n'
                    '  this.onresize();\n'
                    '  this.setupView();\n'
                    '}\n'
                    '\n'
                    'Dz.setupParams = function() {\n'
                    '  var p = window.location.search.substr(1).split("&");\n'
                    '  p.forEach(function(e, i, a) {\n'
                    '    var keyVal = e.split("=");\n'
                    '    Dz.params[keyVal[0]] = decodeURIComponent(keyVal[1]);\n'
                    '  });\n'
                    '// Specific params handling\n'
                    '  if (!+this.params.autoplay)\n'
                    '    $$.forEach($$("video"), function(v){ v.controls = true });\n'
                    '}\n'
                    '\n'
                    'Dz.onkeydown = function(aEvent) {\n'
                    '  // Do not intercept keyboard shortcuts\n'
                    '  if (aEvent.altKey\n'
                    '    || aEvent.ctrlKey\n'
                    '    || aEvent.metaKey\n'
                    '    || aEvent.shiftKey) {\n'
                    '    return;\n'
                    '  }\n'
                    '  if ( aEvent.keyCode == 37 // left arrow\n'
                    '    || aEvent.keyCode == 38 // up arrow\n'
                    '    || aEvent.keyCode == 33 // page up\n'
                    '  ) {\n'
                    '    aEvent.preventDefault();\n'
                    '    this.back();\n'
                    '  }\n'
                    '  if ( aEvent.keyCode == 39 // right arrow\n'
                    '    || aEvent.keyCode == 40 // down arrow\n'
                    '    || aEvent.keyCode == 34 // page down\n'
                    '  ) {\n'
                    '    aEvent.preventDefault();\n'
                    '    this.forward();\n'
                    '  }\n'
                    '  if (aEvent.keyCode == 35) { // end\n'
                    '    aEvent.preventDefault();\n'
                    '    this.goEnd();\n'
                    '  }\n'
                    '  if (aEvent.keyCode == 36) { // home\n'
                    '    aEvent.preventDefault();\n'
                    '    this.goStart();\n'
                    '  }\n'
                    '  if (aEvent.keyCode == 32) { // space\n'
                    '    aEvent.preventDefault();\n'
                    '    this.toggleContent();\n'
                    '  }\n'
                    '  if (aEvent.keyCode == 70) { // f\n'
                    '    aEvent.preventDefault();\n'
                    '    this.goFullscreen();\n'
                    '  }\n'
                    '  if (aEvent.keyCode == 79) { // o\n'
                    '    aEvent.preventDefault();\n'
                    '    this.toggleView();\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    '/* Touch Events */\n'
                    '\n'
                    'Dz.setupTouchEvents = function() {\n'
                    '  var orgX, newX;\n'
                    '  var tracking = false;\n'
                    '\n'
                    '  var db = document.body;\n'
                    '  db.addEventListener("touchstart", start.bind(this), false);\n'
                    '  db.addEventListener("touchmove", move.bind(this), false);\n'
                    '\n'
                    '  function start(aEvent) {\n'
                    '    aEvent.preventDefault();\n'
                    '    tracking = true;\n'
                    '    orgX = aEvent.changedTouches[0].pageX;\n'
                    '  }\n'
                    '\n'
                    '  function move(aEvent) {\n'
                    '    if (!tracking) return;\n'
                    '    newX = aEvent.changedTouches[0].pageX;\n'
                    '    if (orgX - newX > 100) {\n'
                    '      tracking = false;\n'
                    '      this.forward();\n'
                    '    } else {\n'
                    '      if (orgX - newX < -100) {\n'
                    '        tracking = false;\n'
                    '        this.back();\n'
                    '      }\n'
                    '    }\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.setupView = function() {\n'
                    '  document.body.addEventListener("click", function ( e ) {\n'
                    '    if (!Dz.html.classList.contains("view")) return;\n'
                    '    if (!e.target || e.target.nodeName != "SECTION") return;\n'
                    '\n'
                    '    Dz.html.classList.remove("view");\n'
                    '    Dz.setCursor(Dz.slides.indexOf(e.target) + 1);\n'
                    '  }, false);\n'
                    '}\n'
                    '\n'
                    '/* Adapt the size of the slides to the window */\n'
                    '\n'
                    'Dz.onresize = function() {\n'
                    '  var db = document.body;\n'
                    '  var sx = db.clientWidth / window.innerWidth;\n'
                    '  var sy = db.clientHeight / window.innerHeight;\n'
                    '  var transform = "scale(" + (1/Math.max(sx, sy)) + ")";\n'
                    '\n'
                    '  db.style.MozTransform = transform;\n'
                    '  db.style.WebkitTransform = transform;\n'
                    '  db.style.OTransform = transform;\n'
                    '  db.style.msTransform = transform;\n'
                    '  db.style.transform = transform;\n'
                    '}\n'
                    '\n'
                    '\n'
                    'Dz.getNotes = function(aIdx) {\n'
                    '  var s = $("section:nth-of-type(" + aIdx + ")");\n'
                    '  var d = s.$("[role=\'note\']");\n'
                    '  return d ? d.innerHTML : "";\n'
                    '}\n'
                    '\n'
                    'Dz.onmessage = function(aEvent) {\n'
                    '  var argv = aEvent.data.split(" "), argc = argv.length;\n'
                    '  argv.forEach(function(e, i, a) { a[i] = decodeURIComponent(e) });\n'
                    '  var win = aEvent.source;\n'
                    '  if (argv[0] === "REGISTER" && argc === 1) {\n'
                    '    this.remoteWindows.push(win);\n'
                    '    this.postMsg(win, "REGISTERED", document.title, this.slides.length);\n'
                    '    this.postMsg(win, "CURSOR", this.idx + "." + this.step);\n'
                    '    return;\n'
                    '  }\n'
                    '  if (argv[0] === "BACK" && argc === 1)\n'
                    '    this.back();\n'
                    '  if (argv[0] === "FORWARD" && argc === 1)\n'
                    '    this.forward();\n'
                    '  if (argv[0] === "START" && argc === 1)\n'
                    '    this.goStart();\n'
                    '  if (argv[0] === "END" && argc === 1)\n'
                    '    this.goEnd();\n'
                    '  if (argv[0] === "TOGGLE_CONTENT" && argc === 1)\n'
                    '    this.toggleContent();\n'
                    '  if (argv[0] === "SET_CURSOR" && argc === 2)\n'
                    '    window.location.hash = "#" + argv[1];\n'
                    '  if (argv[0] === "GET_CURSOR" && argc === 1)\n'
                    '    this.postMsg(win, "CURSOR", this.idx + "." + this.step);\n'
                    '  if (argv[0] === "GET_NOTES" && argc === 1)\n'
                    '    this.postMsg(win, "NOTES", this.getNotes(this.idx));\n'
                    '}\n'
                    '\n'
                    'Dz.toggleContent = function() {\n'
                    '  // If a Video is present in this new slide, play it.\n'
                    '  // If a Video is present in the previous slide, stop it.\n'
                    '  var s = $("section[aria-selected]");\n'
                    '  if (s) {\n'
                    '    var video = s.$("video");\n'
                    '    if (video) {\n'
                    '      if (video.ended || video.paused) {\n'
                    '        video.play();\n'
                    '      } else {\n'
                    '        video.pause();\n'
                    '      }\n'
                    '    }\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.setCursor = function(aIdx, aStep) {\n'
                    '  // If the user change the slide number in the URL bar, jump\n'
                    '  // to this slide.\n'
                    '  aStep = (aStep != 0 && typeof aStep !== "undefined") ? "." + aStep : ".0";\n'
                    '  window.location.hash = "#" + aIdx + aStep;\n'
                    '}\n'
                    '\n'
                    'Dz.onhashchange = function() {\n'
                    '  var cursor = window.location.hash.split("#"),\n'
                    '      newidx = 1,\n'
                    '      newstep = 0;\n'
                    '  if (cursor.length == 2) {\n'
                    '    newidx = ~~cursor[1].split(".")[0];\n'
                    '    newstep = ~~cursor[1].split(".")[1];\n'
                    '    if (newstep > Dz.slides[newidx - 1].$$(\'.incremental > *\').length) {\n'
                    '      newstep = 0;\n'
                    '      newidx++;\n'
                    '    }\n'
                    '  }\n'
                    '  this.setProgress(newidx, newstep);\n'
                    '  if (newidx != this.idx) {\n'
                    '    this.setSlide(newidx);\n'
                    '  }\n'
                    '  if (newstep != this.step) {\n'
                    '    this.setIncremental(newstep);\n'
                    '  }\n'
                    '  for (var i = 0; i < this.remoteWindows.length; i++) {\n'
                    '    this.postMsg(this.remoteWindows[i], "CURSOR", this.idx + "." + this.step);\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.back = function() {\n'
                    '  if (this.idx == 1 && this.step == 0) {\n'
                    '    return;\n'
                    '  }\n'
                    '  if (this.step == 0) {\n'
                    '    this.setCursor(this.idx - 1,\n'
                    '                   this.slides[this.idx - 2].$$(\'.incremental > *\').length);\n'
                    '  } else {\n'
                    '    this.setCursor(this.idx, this.step - 1);\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.forward = function() {\n'
                    '  if (this.idx >= this.slides.length &&\n'
                    '      this.step >= this.slides[this.idx - 1].$$(\'.incremental > *\').length) {\n'
                    '      return;\n'
                    '  }\n'
                    '  if (this.step >= this.slides[this.idx - 1].$$(\'.incremental > *\').length) {\n'
                    '    this.setCursor(this.idx + 1, 0);\n'
                    '  } else {\n'
                    '    this.setCursor(this.idx, this.step + 1);\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.goStart = function() {\n'
                    '  this.setCursor(1, 0);\n'
                    '}\n'
                    '\n'
                    'Dz.goEnd = function() {\n'
                    '  var lastIdx = this.slides.length;\n'
                    '  var lastStep = this.slides[lastIdx - 1].$$(\'.incremental > *\').length;\n'
                    '  this.setCursor(lastIdx, lastStep);\n'
                    '}\n'
                    '\n'
                    'Dz.toggleView = function() {\n'
                    '  this.html.classList.toggle("view");\n'
                    '\n'
                    '  if (this.html.classList.contains("view")) {\n'
                    '    $("section[aria-selected]").scrollIntoView(true);\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.setSlide = function(aIdx) {\n'
                    '  this.idx = aIdx;\n'
                    '  var old = $("section[aria-selected]");\n'
                    '  var next = $("section:nth-of-type("+ this.idx +")");\n'
                    '  if (old) {\n'
                    '    old.removeAttribute("aria-selected");\n'
                    '    var video = old.$("video");\n'
                    '    if (video) {\n'
                    '      video.pause();\n'
                    '    }\n'
                    '  }\n'
                    '  if (next) {\n'
                    '    next.setAttribute("aria-selected", "true");\n'
                    '    if (this.html.classList.contains("view")) {\n'
                    '      next.scrollIntoView();\n'
                    '    }\n'
                    '    var video = next.$("video");\n'
                    '    if (video && !!+this.params.autoplay) {\n'
                    '      video.play();\n'
                    '    }\n'
                    '  } else {\n'
                    '    // That should not happen\n'
                    '    this.idx = -1;\n'
                    '    // console.warn("Slide does not exist.");\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.setIncremental = function(aStep) {\n'
                    '  this.step = aStep;\n'
                    '  var old = this.slides[this.idx - 1].$(\'.incremental > *[aria-selected]\');\n'
                    '  if (old) {\n'
                    '    old.removeAttribute(\'aria-selected\');\n'
                    '  }\n'
                    '  var incrementals = $$(\'.incremental\');\n'
                    '  if (this.step <= 0) {\n'
                    '    $$.forEach(incrementals, function(aNode) {\n'
                    '      aNode.removeAttribute(\'active\');\n'
                    '    });\n'
                    '    return;\n'
                    '  }\n'
                    '  var next = this.slides[this.idx - 1].$$(\'.incremental > *\')[this.step - 1];\n'
                    '  if (next) {\n'
                    '    next.setAttribute(\'aria-selected\', true);\n'
                    '    next.parentNode.setAttribute(\'active\', true);\n'
                    '    var found = false;\n'
                    '    $$.forEach(incrementals, function(aNode) {\n'
                    '      if (aNode != next.parentNode)\n'
                    '        if (found)\n'
                    '          aNode.removeAttribute(\'active\');\n'
                    '        else\n'
                    '          aNode.setAttribute(\'active\', true);\n'
                    '      else\n'
                    '        found = true;\n'
                    '    });\n'
                    '  } else {\n'
                    '    setCursor(this.idx, 0);\n'
                    '  }\n'
                    '  return next;\n'
                    '}\n'
                    '\n'
                    'Dz.goFullscreen = function() {\n'
                    '  var html = $(\'html\'),\n'
                    r'      requestFullscreen = html.requestFullscreen || html.requestFullScreen || '
                    'html.mozRequestFullScreen || html.webkitRequestFullScreen;\n'
                    '  if (requestFullscreen) {\n'
                    '    requestFullscreen.apply(html);\n'
                    '  }\n'
                    '}\n'
                    '\n'
                    'Dz.setProgress = function(aIdx, aStep) {\n'
                    '  var slide = $("section:nth-of-type("+ aIdx +")");\n'
                    '  if (!slide)\n'
                    '    return;\n'
                    '  var steps = slide.$$(\'.incremental > *\').length + 1,\n'
                    '      slideSize = 100 / (this.slides.length - 1),\n'
                    '      stepSize = slideSize / steps;\n'
                    '  this.progressBar.style.width = ((aIdx - 1) * slideSize + aStep * stepSize) + \'%\';\n'
                    '}\n'
                    '\n'
                    'Dz.postMsg = function(aWin, aMsg) { // [arg0, [arg1...]]\n'
                    '  aMsg = [aMsg];\n'
                    '  for (var i = 2; i < arguments.length; i++)\n'
                    '    aMsg.push(encodeURIComponent(arguments[i]));\n'
                    '  aWin.postMessage(aMsg.join(" "), "*");\n'
                    '}\n'
                    '\n'
                    'function init() {\n'
                    '  Dz.init();\n'
                    '  window.onkeydown = Dz.onkeydown.bind(Dz);\n'
                    '  window.onresize = Dz.onresize.bind(Dz);\n'
                    '  window.onhashchange = Dz.onhashchange.bind(Dz);\n'
                    '  window.onmessage = Dz.onmessage.bind(Dz);\n'
                    '}\n'
                    '\n'
                    'window.onload = init;\n'
                    '</script>\n'
                    '\n'
                    '\n'
                    '<script> // Helpers\n'
                    'if (!Function.prototype.bind) {\n'
                    '  Function.prototype.bind = function (oThis) {\n'
                    '\n'
                    '    // closest thing possible to the ECMAScript 5 internal IsCallable\n'
                    '    // function\n'
                    '    if (typeof this !== "function")\n'
                    '    throw new TypeError(\n'
                    '      "Function.prototype.bind - what is trying to be fBound is not callable"\n'
                    '    );\n'
                    '\n'
                    '    var aArgs = Array.prototype.slice.call(arguments, 1),\n'
                    '        fToBind = this,\n'
                    '        fNOP = function () {},\n'
                    '        fBound = function () {\n'
                    '          return fToBind.apply( this instanceof fNOP ? this : oThis || window,\n'
                    '                 aArgs.concat(Array.prototype.slice.call(arguments)));\n'
                    '        };\n'
                    '\n'
                    '    fNOP.prototype = this.prototype;\n'
                    '    fBound.prototype = new fNOP();\n'
                    '\n'
                    '    return fBound;\n'
                    '  };\n'
                    '}\n'
                    '\n'
                    'var $ = (HTMLElement.prototype.$ = function(aQuery) {\n'
                    '  return this.querySelector(aQuery);\n'
                    '}).bind(document);\n'
                    '\n'
                    'var $$ = (HTMLElement.prototype.$$ = function(aQuery) {\n'
                    '  return this.querySelectorAll(aQuery);\n'
                    '}).bind(document);\n'
                    '\n'
                    '$$.forEach = function(nodeList, fun) {\n'
                    '  Array.prototype.forEach.call(nodeList, fun);\n'
                    '}\n'
                    '\n'
                    '</script>\n'
                    '\n'),
            theme=None,
            transition='',
            title=None,
        ),
        deck=dict(
            subdir='deck.js-latest',
            default_theme='web-2.0',
            slide_envir_begin='<section class="slide">',
            slide_envir_end='</section>',
            pop=('slide', 'li'),
            notes='<div class="notes">\n<!-- press "n" to activate -->\n\\g<1>\n</div>\n',
            head_header=get_deck_header(),
            body_header=('<body class="deck-container">\n'
                         '\n'
                         '<header>\n'
                         '<!-- Here goes a potential header -->\n'
                         '</header>\n'
                         '\n'
                         '<!-- do not use the article tag - it gives strange sizings -->\n'),
            footer=get_deck_footer(),
            theme=None,
            transition='',
            title=None,
            ),
        html5slides=dict(
            subdir=None,
            default_theme='template-default',   # template-io2011, should use template-io2012:
                                                # https://code.google.com/p/io-2012-slides/
            slide_envir_begin='<article>',
            slide_envir_end='</article>',
            pop=('build', 'ul'),
            notes='<aside class="note">\n<!-- press "p" to activate -->\n\\g<1>\n</aside>\n',
            head_header=('<!-- Google HTML5 Slides:\n'
                         '     https://code.google.com/p/html5slides/\n'
                         '-->\n'
                         '\n'
                         '<meta charset=\'utf-8\'>\n'
                         '<script\n'
                         ' src=\'https://html5slides.googlecode.com/svn/trunk/slides.js\'>\n'
                         '</script>\n'
                         '\n'
                         '</head>\n'
                         '\n'
                         '<style>\n'
                         '/* Your individual styles here... */\n'
                         '</style>\n'),
            body_header=('<body style=\'display: none\'>\n\n'

                         '<!-- See https://code.google.com/p/html5slides/source/browse/trunk/styles.css\n'
                         '     for definition of template-default and other styles -->\n\n'
                         '<section class=\'slides layout-regular %(theme)s\'>\n'
                         '<!-- <section class=\'slides layout-regular template-io2011\'> -->\n'
                         '<!-- <section class=\'slides layout-regular template-default\'> -->\n\n'
                         '<!-- Slides are in <article> tags -->\n\n'),
            footer=('\n'
                    '</section>\n'),
            theme=None,
            transition='',
            title=None,
            ),
        )

    theme = misc_option('html_slide_theme=', default='default')
    # Check that the theme name is registered
    all_combinations = recommended_html_styles_and_pygments_styles()
    if not slide_tp in all_combinations:
        # This test will not be run since it is already tested that
        # the slide type is legal (before calling this function)
        errwarn('*** error: slide type "%s" is not known - abort' % slide_tp)
        errwarn('known slide types: ' + ', '.join(list(all_combinations.keys())))
        _abort()

    # We need the subdir with reveal.js, deck.js, or similar to show
    # the HTML slides so add the subdir to the registered file collection
    if slide_syntax[slide_tp]['subdir'] is not None:
        add_to_file_collection(slide_syntax[slide_tp]['subdir'], filename, 'a')

    if (theme == 'default' or theme.endswith('_default')):
        slide_syntax[slide_tp]['theme'] = slide_syntax[slide_tp]['default_theme']
    else:
        if theme in all_combinations[slide_tp].keys():
            slide_syntax[slide_tp]['theme'] = theme
        else:
            errwarn('*** error: %s theme "%s" is not known - abort' % (slide_tp, theme))
            errwarn('known themes: ' + ', '.join(list(all_combinations[slide_tp].keys())))
            _abort()

    # Slide transition: only implemented for Deck.js
    transition = misc_option('html_slide_transition=', default='')
    if transition in  ['', 'none', 'None', 'off', 'no']:
        if slide_tp == 'deck':
            transition = ''
        elif slide_tp=='reveal':
            transition = 'none'
    # Check that the transition theme is in the folder, then store it in `slide_syntax`
    if slide_tp == 'deck' and transition:
        deck_folder = deck_files.replace('.zip', '')
        transition_theme_folder = os.path.join(deck_folder, 'themes/transition')
        valid_transitions = list_package_data(deck_files,
                                        folder=transition_theme_folder,
                                        suffix='.css')
        valid_transitions = map(
            lambda x: x.replace(transition_theme_folder, '').replace('.css', '').strip('/'), valid_transitions)
        if transition not in valid_transitions:
            errwarn('*** warning: slide transition theme "%s" not found in data package' % transition)
        slide_syntax[slide_tp]['transition'] = \
            os.path.join(deck_folder, os.path.join("themes/transition", transition + ".css"))
    elif slide_tp == 'reveal':
        slide_syntax[slide_tp]['transition'] = transition
        slide_syntax[slide_tp]['footer'] = \
            slide_syntax[slide_tp]['footer'] % slide_syntax[slide_tp]

    # Fill in theme etc.
    slide_syntax[slide_tp]['head_header'] = \
           slide_syntax[slide_tp]['head_header'] % slide_syntax[slide_tp]
    slide_syntax[slide_tp]['body_header'] = \
           slide_syntax[slide_tp]['body_header'] % slide_syntax[slide_tp]

    footer_logo = misc_option('html_footer_logo=', default=None)

    # Handle short forms for cbc, simula, and uio logos
    if footer_logo == 'cbc':
        footer_logo = 'cbc_footer'
    elif footer_logo == 'simula':
        footer_logo = 'simula_footer'
    elif footer_logo == 'uio':
        footer_logo = 'uio_footer'

    # Default footer logo command
    repl = ('<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px;">\n'
            '<img src="%s/cbc_footer.png" width=110%%;></div>\n') % footer_logo

    # Override repl for cbc, simula, uio logos since these are specified
    # without full URLs

    # Path to cbc, simula, uio logo files
    footer_logo_path = dict(reveal='reveal.js/css/images',
                            deck='deck.js-latest/themes/images')
    if footer_logo == 'cbc_footer':
        if slide_tp not in ('reveal', 'deck'):
            raise ValueError('slide type "%s" cannot have --html_footer_logo' ^ slide_tp)
        repl = ('\n<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px;">\n'
                '<img src="%s/cbc_footer.png" width=110%%;></div>\n'
                ) % footer_logo_path[slide_tp]
    elif footer_logo == 'cbc_symbol':
        repl = ('<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 20px;">\n'
                '<img src="%s/cbc_symbol.png" width="50"></div>\n') % footer_logo_path[slide_tp]
    elif footer_logo == 'simula_footer':
        repl = ('<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px;">\n'
                '<img src="%s/simula_footer.png" width=700></div>\n') % footer_logo_path[slide_tp]
    elif footer_logo == 'simula_symbol':
        repl = ('\n<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 10px;">'
                '<img src="%s/simula_symbol.png" width=200></div>\n') % footer_logo_path[slide_tp]
    elif footer_logo == 'uio_footer':
        repl = ('\n<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 0px;">\n'
                '<img src="%s/uio_footer.png" width=450></div>\n') % footer_logo_path[slide_tp]
    elif footer_logo == 'uio_symbol':
        repl = ('\n<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 20px;">\n'
                '\n<img src="%s/uio_symbol.png" width=100></div>\n'
                ) % footer_logo_path[slide_tp]
    elif footer_logo == 'uio_simula_symbol':
        repl = ('\n<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 0px;">\n'
                '<img src="%s/uio_footer.png" width="180"></div>\n'
                '<div style="position: absolute; bottom: 0px; left: 0; margin-left: 250px; margin-bottom: 0px;">\n'
                '<img src="%s/simula_symbol.png" width="250"></div>\n') % \
               (footer_logo_path[slide_tp], footer_logo_path[slide_tp])

    pattern = dict(
        reveal=r'<!-- begin footer logo\s+(.+?)\s+end footer logo -->',
        deck=r'<!-- Here goes a footer -->')

    if footer_logo is not None:
        slide_syntax[slide_tp]['footer'] = re.sub(
            pattern[slide_tp], repl,
            slide_syntax[slide_tp]['footer'], flags=re.DOTALL)

    # Grab the relevant lines in the <head> and <body> parts of
    # the original header
    head_lines = []
    body_lines = []
    inside_style = False
    inside_head = False
    inside_body = False
    for line in header:
        if '<head>' in line:
            inside_head = True
            continue
        elif '</head>' in line:
            inside_head = False
            continue
        elif line.strip().startswith('<body'):
            inside_body = True
            continue
        elif '</body>' in line:
            inside_body = False
            continue
        elif line.strip().startswith('<style'):
            inside_style = True
            continue
        elif '</style>' in line:
            inside_style = False
            continue
        if inside_style:
            continue  # skip style lines
        elif inside_body:
            body_lines.append(line)
        elif inside_head:
            head_lines.append(line)
    slide_syntax[slide_tp]['head_lines'] = ''.join(head_lines)
    slide_syntax[slide_tp]['body_lines'] = ''.join(body_lines)

    slides = ('<!--\n'
              'HTML file automatically generated from DocOnce source\n'
              '(https://github.com/doconce/doconce/)\n'
              'doconce format html %s %s\n'
              '-->\n') % (filename, ' '.join(sys.argv[1:]))
    slides += ('<!DOCTYPE html>\n'
              '<html>\n'
              '<head>\n'
              '%(head_lines)s\n'
              '%(head_header)s\n'
              '<!-- Styles for table layout of slides -->\n'
              '<style type="text/css">\n'
              'td.padding {\n'
              '  padding-top:20px;\n'
              '  padding-bottom:20px;\n'
              '  padding-right:50px;\n'
              '  padding-left:50px;\n'
              '}\n'
              '</style>\n\n'
              '</head>\n\n'
              '%(body_header)s\n\n'
              '%(body_lines)s\n\n') % slide_syntax[slide_tp]

    # Avoid too many numbered equations: use \tag for all equations
    # with labels (these get numbers) and turn all other numbers off
    # by autoNumber: "none"
    slides = slides.replace('autoNumber: "AMS"', 'autoNumber: "none"')

    for part_no, part in enumerate(parts):
        part = ''.join(part)

        if '<!-- begin inline comment' in part:
            pattern = r'<!-- begin inline comment -->\s*\[<b>.+?</b>:\s*<em>(.+?)</em>]\s*<!-- end inline comment -->'
            part = re.sub(pattern,
                          slide_syntax[slide_tp]['notes'], part,
                          flags=re.DOTALL)

        if '<!-- !bnotes' in part:
            pattern = r'<!-- !bnotes .*?-->(.+?)<!-- !enotes.*?-->'
            part = re.sub(pattern,
                          slide_syntax[slide_tp]['notes'], part,
                          flags=re.DOTALL)

        if slide_tp == 'deck':
            if '<!-- document title -->' in part:
                # h1 title should be h2 to fix problems with
                # .csstransforms h1, .csstransforms .vcenter in css files
                pattern = r'<center>\s*<h1>(.+?)</h1>\s*</center>'
                part = re.sub(pattern,
                              r'<h2 style="text-align: center;">\g<1></h2>',
                              part)
                # Date should use b rather than h4 (which is too big)
                pattern = '<center>\s*<h4>(.+?)</h4>\s*</center>'
                part = re.sub(pattern, r'<center><b>\g<1></b></center>', part)

            # <b> does not work, so we must turn on bold manually
            part = part.replace('<b>', '<b style="font-weight: bold">')

        if slide_tp in ('deck', 'reveal'):
            # Add more space around equations
            part = re.sub(r'\$\$([^$]+)\$\$',
                          #r'<p>&nbsp;<br>&nbsp;<br>\n$$\g<1>$$\n&nbsp;<br>',
                          r'<p>&nbsp;<br>\n$$\g<1>$$\n<p>&nbsp;<br>',
                          part)

        if slide_tp == 'reveal' and part_no == 0:
            # Add space after names and after institutions
            part = re.sub(r'<p>\s+<!-- institution\(s\)',
                          r'<p>&nbsp;<br>\n<!-- institution(s)', part)
            part = re.sub(r'<p>\s+<center>\s*<h4>(.+?)</h4>\s*</center>\s+<!-- date -->',
                          r'<p>&nbsp;<br>\n<center><h4>\g<1></h4></center> <!-- date -->',
                          part)

        #if '!bpop' not in part:
        #if slide_tp in ['reveal']:
        part = part.replace('<li>', '<p><li>')  # more space between bullets
        # else: the <p> destroys proper handling of incremental pop up
        # Try this for all and see if any problem appears
        part = part.replace('<li ', '<p><li ')  # more space between bullets

        # Find pygments style
        m = re.search(r'typeset with pygments style "(.+?)"', part)
        pygm_style = m.group(1) if m else 'plain <pre>'
        html_style = slide_syntax[slide_tp]['theme']
        recommended_combinations = all_combinations[slide_tp]
        if html_style in recommended_combinations:
            if pygm_style != 'plain <pre>' and \
               not pygm_style in recommended_combinations[html_style]:
                print('*** warning: pygments style "%s" is not '\
                      'recommended for "%s"!' % (pygm_style, html_style))
                print('recommended styles are %s' % \
                      (', '.join(['"%s"' % combination
                                  for combination in
                                  recommended_combinations[html_style]])))

        # Fix styles: native should have black background for dark themes
        if slide_syntax[slide_tp]['theme'] in ['neon', 'night', 'moon', 'blood']:
            if pygm_style == 'native':
                # Change to black background
                part = part.replace('background: #202020',
                                    'background: #000000')

        # Make h1 section headings centered
        part = part.replace('<h1>', '<h1 style="text-align: center;">')

        # Pieces to pop up item by item as the user is clicking
        if '<!-- !bpop' in part:
            pattern = r'<!-- !bpop (.*?)-->\s*(.+?)\s*<!-- !epop.*?-->'
            cpattern = re.compile(pattern, re.DOTALL)
            #import pprint;pprint.pprint(cpattern.findall(part))
            def subst(m):  # m is match object
                arg = m.group(1).strip()
                if arg:
                    arg = ' ' + arg

                inserted_pop_up = False
                class_tp = slide_syntax[slide_tp]['pop'][0]
                placements = slide_syntax[slide_tp]['pop'][1:]
                body = m.group(2)

                # Insert special pop-up tags for lists, admons, and
                # pygments code blocks first.
                # If none of these are found (inserted_pop_up = False)
                # mark the whole paragraph as pop-up element

                if '<ol>' in body or '<ul>' in body:
                    for tag in placements:
                        tag = '<%s>' % tag.lower()
                        if tag in body:
                            body = body.replace(tag, '%s class="%s%s">' % (tag[:-1], class_tp, arg))
                            inserted_pop_up = True
                if '<div class="alert' in body:
                    # Augment admonitions with pop-up syntax
                    body = body.replace('div class="alert',
                                        'div class="%s alert' % class_tp)
                    inserted_pop_up = True
                if '<div class="highlight' in body:
                    # Augment pygments blocks with pop-up syntax
                    body = body.replace('<div class="highlight',
                                        '<div class="%s" class="highlight' % class_tp)
                    inserted_pop_up = True
                if not inserted_pop_up:
                    # Treat whole block as pop-up paragraph

                    # Hack to preserve spacings before equation (see above),
                    # when <p> is removed (as we must do below)
                    body = body.replace('<p>&nbsp;\s*<br>', '&nbsp;<br>&nbsp;<br>')
                    body = body.replace('<p>', '')  # can make strange behavior
                    # Add a <p class="fragments"> to the whole body
                    # (but only if not code or admon content?)
                    body2 = '\n<p class="%s">\n' % class_tp

                    # Add arguments specified after !bpop?
                    if slide_tp == 'reveal' and arg:  # reveal specific
                        args = arg.split()
                        for arg in args:
                            if arg:
                                body2 += '\n<span class="%s %s">\n' % (class_tp, arg)
                        body2 += body
                        for arg in args:
                            if arg:
                                body2 += '\n</span>\n'
                    else:
                        body2 += body
                    body2 += '\n</p>\n'
                    body = body2
                return body

            part = cpattern.sub(subst, part)

        # Special treatment of the text for some slide tools
        if slide_tp == 'deck':
            part = re.sub(r'<pre>(.+?)</pre>',
                          r'<pre><code>\g<1></code></pre>',
                          part, flags=re.DOTALL)
        if slide_tp == 'reveal':
            part = re.sub(r'<pre>\s*<code>(.+?)</code>\s*</pre>',
                          r'<pre><code data-trim contenteditable>\g<1></code></pre>',
                          part,
                          flags=re.DOTALL)

        # Add space after list, except in admons (ended by </div>)
        part = re.sub(r'</ul>(?!\s*</div>)', r'</ul>\n<p>', part) #TODO: stray <p> tags
        part = re.sub(r'</ol>(?!\s*</div>)', r'</ol>\n<p>', part)

        if html_copyright_placement == 'titlepage' and part_no > 0:
            copyright_ = ''

        slides += ('%s\n'
                   '%s\n'
                   '%s\n'
                   '%s\n\n') % (slide_syntax[slide_tp]['slide_envir_begin'],
                                part,
                                copyright_,
                                slide_syntax[slide_tp]['slide_envir_end'])
    slides += ('\n%s\n\n'
               '</body>\n'
               '</html>\n') % (slide_syntax[slide_tp]['footer'])
    slides = re.sub(r'<!-- !split .*-->\n', '', slides)

    eq_no = 1  # counter for equations
    # Insert \tag for each \label (\label only in equations in HTML)
    labels = re.findall(r'\\label\{(.+?)\}', slides)
    for label in labels:
        slides = slides.replace(r'\label{%s}' % label,
                                r'\tag{%s}' % eq_no)
        slides = slides.replace(r'\eqref{%s}' % label,
                                '<a href="#mjx-eqn-%s">(%s)</a>' %
                                (eq_no, eq_no))
        eq_no += 1

    if slide_tp == 'reveal':
        # Adjust font size in code
        slides = slides.replace('<pre style="', '<pre style="font-size: 80%; ')

    return slides


def _usage_slides_beamer():
    print('Usage:\n'
          'doconce slides_beamer mydoc --beamer_slide_navigation=off --beamer_slide_theme=\\\n'
          '(red_plain | blue_plain | red_shadow | blue_shadow | dark | dark_gradient | vintage) \\\n'
          '--beamer_block_style=mdbox [--handout]\n\n'
          'Options:\n'
          '--beamer_slide_navigation=on turns on navigation links in the header and footer.\n'
          '  The links are defined by sections (only), i.e., headings with 7 = in the source file.\n'
          '--beamer_block_style=X controls how beamer blocks are typeset. X=native gives the '
          '  standard beamer blocks. X=mdbox gives a mdframed box around the content. This is '
          '  preferable for simple slide styles.\n'
          '--handout is used for generating PDF that can be printed as handouts (usually after\n'
          '  using pdfnup to put multiple slides per sheet).')


def generate_beamer_slides(header, parts, footer, basename, filename):
    # Styles: red/blue_plain/shadow, dark, dark_gradient, vintage
    header = ''.join(header)

    # Copyright? Use \logo{} to represent it
    # (It does not seem to work - we must insert it in the date too)
    pattern = r'\\fancyfoot\[C\]\{\{\\footnotesize (.+)\}\}'
    m = re.search(pattern, header)
    if m:
        copyright_text = r'{\tiny ' + m.group(1).strip() + '}'
        copyright_ = r'\logo{%s}' % copyright_text
    else:
        copyright_text = copyright_ = ''

    theme = misc_option('beamer_slide_theme=', default='default')
    if theme != 'default':
        beamerstyle = 'beamertheme' + theme
        packages = [beamerstyle]
        if theme == 'vintage':
            packages.append('vintage_background.png')
        copy_latex_packages(packages)
    handout = '[handout]' if misc_option('handout', False) else ''

    if misc_option('beamer_slide_navigation=', 'off') == 'on':
        frame_options = '[fragile]'
    else:
        # plain signifies no navigation
        frame_options = '[plain,fragile]'

    block_style = misc_option('beamer_block_style=', 'native')
    parskip = 0 if theme.endswith('_plain') else 7

    slides = r"""
%% LaTeX Beamer file automatically generated from DocOnce
%% https://github.com/doconce/doconce

%%-------------------- begin beamer-specific preamble ----------------------

\documentclass%(handout)s{beamer}

\usetheme{%(theme)s}
\usecolortheme{default}

%% turn off the almost invisible, yet disturbing, navigation symbols:
\setbeamertemplate{navigation symbols}{}

%% Examples on customization:
%%\usecolortheme[named=RawSienna]{structure}
%%\usetheme[height=7mm]{Rochester}
%%\setbeamerfont{frametitle}{family=\rmfamily,shape=\itshape}
%%\setbeamertemplate{items}[ball]
%%\setbeamertemplate{blocks}[rounded][shadow=true]
%%\useoutertheme{infolines}
%%
%%\usefonttheme{}
%%\useinntertheme{}
%%
%%\setbeameroption{show notes}
%%\setbeameroption{show notes on second screen=right}

%% fine for B/W printing:
%%\usecolortheme{seahorse}

\usepackage{pgf}
\usepackage{graphicx}
\usepackage{epsfig}
\usepackage{relsize}

\usepackage{fancybox}  %% make sure fancybox is loaded before fancyvrb

\usepackage{fancyvrb}
%%\usepackage{minted} %% requires pygments and latex -shell-escape filename
%%\usepackage{anslistings}
%%\usepackage{listingsutf8}

\usepackage{amsmath,amssymb,bm}
%%\usepackage[latin1]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{colortbl}
\usepackage[english]{babel}
\usepackage{tikz}
\usepackage{framed}
%% Use some nice templates
\beamertemplatetransparentcovereddynamic

%% --- begin table of contents based on sections ---
%% Delete this, if you do not want the table of contents to pop up at
%% the beginning of each section:
%% (Only section headings can enter the table of contents in Beamer
%% slides generated from DocOnce source, while subsections are used
%% for the title in ordinary slides.)
\AtBeginSection[]
{
  \begin{frame}<beamer>[plain]
  \frametitle{}
  %%\frametitle{Outline}
  \tableofcontents[currentsection]
  \end{frame}
}
%% --- end table of contents based on sections ---

%% If you wish to uncover everything in a step-wise fashion, uncomment
%% the following command:

%%\beamerdefaultoverlayspecification{<+->}

\newcommand{\shortinlinecomment}[3]{\note{\textbf{#1}: #2}}
\newcommand{\longinlinecomment}[3]{\shortinlinecomment{#1}{#2}{#3}}

\definecolor{linkcolor}{rgb}{0,0,0.4}
\hypersetup{
    colorlinks=true,
    linkcolor=linkcolor,
    urlcolor=linkcolor,
    pdfmenubar=true,
    pdftoolbar=true,
    bookmarksdepth=3
    }
\setlength{\parskip}{%(parskip)spt}  %% {1em}

\newenvironment{doconceexercise}{}{}
\newcounter{doconceexercisecounter}
\newenvironment{doconce:movie}{}{}
\newcounter{doconce:movie:counter}

\newcommand{\subex}[1]{\noindent\textbf{#1}}  %% for subexercises: a), b), etc
""" % vars()

    if handout:
        slides += r"""
\usepackage{pgfpages} % for handouts
"""

    # Check if we need minted or anslistings:
    if re.search(r'\\usepackage.+minted', header):
        slides = slides.replace(
            r'%\usepackage{minted}', r'\usepackage{minted}')
    if re.search(r'\\usepackage.+listings', header):
        m = re.search(r'^% Define colors.+?^% end of custom lstdefinestyles', header, flags=re.DOTALL|re.MULTILINE)
        lststyles = m.group() if m else ''
        slides = slides.replace(
            r'%\usepackage{listingsutf8}', r'\usepackage{listingsutf8}' + '\n\n' + lststyles)
    if re.search(r'\\usepackage.+anslistings', header):
        slides = slides.replace(
            r'%\usepackage{anslistings}', r'\usepackage{anslistings}')

    if block_style.startswith('mdbox'):
        # Add defnition of an appropriate mdframe
        slides += r"""
\usepackage[framemethod=TikZ]{mdframed}
\newcommand{\frametitlecolor}{gray!65!black}
%\usetikzlibrary{shadows}
%\usetikzlibrary{shadows.blur}
% block with title
\newenvironment{mdboxt}[1]{%
    \begin{mdframed}[%
        frametitle={#1\vphantom{\frametitlecolor}},
        skipabove=0.5\baselineskip,
        skipbelow=0.5\baselineskip,
        outerlinewidth=0.5pt,
        frametitlerule=true,
        frametitlebackgroundcolor=gray!15,
        frametitlefont=\normalfont,
        frametitleaboveskip=3pt,
        frametitlebelowskip=2pt,
        frametitlerulewidth=0.5pt,
        roundcorner=2pt,
        %shadow=true,
        %shadowcolor=green!10!black!40,
        %shadowsize=5pt
        %apptotikzsetting={\tikzset{mdfshadow/.style=blur shadow={shadow blur steps=5,shadow blur extra rounding=1.3pt,xshift=3pt,yshift=-3pt}}}
    ]%
}{\end{mdframed}}

% block without title
\newenvironment{mdbox}{%
    \begin{mdframed}[%
        roundcorner=2pt,
        %shadow=true,
        %shadowcolor=green!10!black!40,
        %shadowsize=5pt
        %apptotikzsetting={\tikzset{mdfshadow/.style=blur shadow={shadow blur steps=5,shadow blur extra rounding=1.3pt,xshift=3pt,yshift=-3pt}}}
    ]%
}{\end{mdframed}}

"""
    if copyright_:
        slides += '\n' + copyright_ + '\n'

    slides += r"""
%-------------------- end beamer-specific preamble ----------------------

% Add user's preamble

"""

    # Add possible user customization from the original latex file,
    # plus the newcommands and \begin{document}
    preamble_divider_line = '% --- end of standard preamble for documents ---'
    if preamble_divider_line not in header:
        errwarn('*** error: generated latex document has missing')
        errwarn('    title, author, and date - add TITLE:, AUTHOR:, DATE:')
        _abort()
    slides += header.split(preamble_divider_line)[1]

    if handout:
        slides_per_page = 4  # 2, 4, 8, 16
        slides += r"""
%%\pgfpagesuselayout{%d on 1}[a4paper,landscape,border shrink=5mm]   %% pdfnup is more flexible
""" % slides_per_page

    for part in parts:
        part = ''.join(part)
        code_free_part = remove_verbatim_blocks(part, 'latex')

        if 'inlinecomment{' in part:
            # Inline comments are typeset as notes in this beamer preamble
            pass
        if '% !bnotes' in part:
            pattern = r'% !bnotes(.+?)% !enotes\s'
            part = re.sub(pattern,
                          r'\\note{\g<1>}', part,
                          flags=re.DOTALL)

        # Keep blocks or make mdbox
        if block_style.startswith('mdbox'):
            def subst(m):
                title = m.group(1).strip()
                text = m.group(2)
                b = 'mdboxt' if title else 'mdbox'
                s = r'\begin{%s}{%s}%s\end{%s}' % (b, title, text, b)
                return s

            pattern = r'\\begin\{block\}\{(.*?)\}(.+)?\\end\{block\}'
            part = re.sub(pattern, subst, part, flags=re.DOTALL)
            # remove margins becomes boxes are not that big
            part = part.replace('leftmargin=7mm', 'leftmargin=0mm')

        # Use smaller margin in slides
        part = part.replace('leftmargin=7mm', 'leftmargin=2mm')

        # Pieces to pop up item by item as the user is clicking
        if '% !bpop' in part:
            num_pops = part.count('% !bpop')
            pattern = r'% !bpop *(.*?)\s+(.+?)\s+% !epop'
            cpattern = re.compile(pattern, re.DOTALL)
            #import pprint;pprint.pprint(cpattern.findall(part))
            def subst(m):  # m is match object
                arg = m.group(1).strip()
                body = m.group(2)

                startswith_block = startswith_list = has_list = False
                pattern_block = r'(\\begin\{block|\\begin\{mdbox|\\summarybox\{|\\begin\{[A-Za-z0-9_]+admon\})'
                pattern_list = r'\\begin\{(enumerate|itemize|description)\}'
                if re.match(pattern_block, body.lstrip()):
                    startswith_block = True
                if re.match(pattern_list, body.lstrip()):
                    startswith_list = True
                if r'\item' in body:
                    has_list = True

                if startswith_block:
                    # Pop up the whole block at once
                    body = '\\pause\n' + body
                elif startswith_list:
                    # Pop up each list item
                    body = re.sub(r'^( *\\item)', r'\\pause\n\g<1>', body,
                                  flags=re.MULTILINE)
                else:
                    # Just pause before what's coming
                    body = '\\pause\n' + body

                '''
                # OLD:
                # Individual pop up of list items if there is only
                # one pop block on this slide, otherwise pause the
                # whole list (in else branch)
                if r'\item' in body: # and num_pops == 1:
                    marker = '[[[[['
                    body = body.replace('\item ', r'\item%s ' % marker)
                    n = body.count('item%s' % marker)
                    for i in range(n):
                        body = body.replace('item%s' % marker,
                                            'item<%d->' % (i+2), 1)
                else:
                    # treat whole part as a block
                    pattern = r'(\\begin\{block|\\begin\{mdbox|\\summarybox\{|\\begin\{[A-Za-z0-9_]+admon\})'
                    m = re.match(pattern, body.lstrip())
                    if m:
                        # body has a construction that is already a block
                        body = r"""
\pause
%s
""" % body
                    else:
                        # wrap body in a block (does not work well if
                        # bpop-epop is already within another block
                        body = r"""
\pause
\begin{block}{}
%s
\end{block}
""" % body
                '''
                return body

            part = cpattern.sub(subst, part)

        # Check that we do not have multiple subsections (i.e., multiple
        # slides) on this split - if so, it is a forgotten !split
        subsections = re.findall(r'\\subsection\{', code_free_part)
        if len(subsections) > 1:
            errwarn('*** error: more than one subsection in a slide (insert missing !split):')
            errwarn(part)
            _abort()

        # Add text for this slide

        # Grab slide title as *first* subsection in part
        pattern = r'subsection\{(.+)\}'  # greedy so it goes to the end
        m = re.search(pattern, code_free_part)
        if m:
            title = m.group(1).strip()
            title = r'\frametitle{%s}' % title + '\n'
            part = re.sub('\\\\.*' + pattern, '', part, count=1)
        elif r'\title{' in code_free_part:
            title = ''
        else:
            title = '% No title on this slide\n'

        # Beamer does not support chapter, paragraph,
        # while section is here used for the toc and subsection
        # for the title
        if r'\chapter{' in code_free_part:
            part = part.replace(r'\chapter{', r'\noindent\textbf{\huge ')
        if r'\paragraph{' in code_free_part:
            part = part.replace(r'\paragraph{', r'\noindent\textbf{')

        section_slide = False
        # \section{} should be \section[short title]{long title}
        # This is signified in a comment
        if r'\section{' in code_free_part:
            section_slide = True

            # Empty section is fine, but if there are more here than
            # labels and comments, we embed that in a separate slide
            # with the same title (otherwise it will come out as garbage)
            section_title = re.search(r'\\section\{(.+)\}', part).group(1)
            remove_patterns = [r'\\section\{.+\}', r'\\label\{.+\}', '^%.*',]
            stripped_part = part
            for pattern in remove_patterns:
                stripped_part = re.sub(pattern, '', stripped_part,
                                       flags=re.MULTILINE)
            stripped_part = stripped_part.strip()
            if stripped_part:
                # Embed everything after section in a new slide
                part = re.sub(r'(\\section\{.+\})', r"""\g<1>

\\begin{frame}%(frame_options)s
\\frametitle{%(section_title)s}
""" % vars(), part)
                part += '\n\\end{frame}\n'

            # Add short title? (\section[short title]{ordinary title})
            short_title = '' # signifies ordinary slide
            m = re.search(r'^% +short +title: +(.+)', code_free_part,
                          flags=re.MULTILINE|re.IGNORECASE)
            if m:
                short_title = m.group(1).strip()
                part = re.sub(r'\\section\{', r'\\section[%s]{' % short_title,
                              part)
                part = part.replace(m.group(), '')  # remove short title comment
            # --- end of section slide treatment ---

        part = part.rstrip()

        # Check if slide is empty
        empty_slide = True
        for line in part.splitlines():
            if line.startswith('%'):
                continue
            if line.strip() != '':
                empty_slide = False

        if r'\title{' in code_free_part:
            # Titlepage needs special treatment
            # Find figure (no caption or figure envir, just includegraphics)
            m = re.search(r'(\\centerline\{\\includegraphics.+\}\})', part)
            if m:
                titlepage_figure = m.group(1)
                # Move titlepage figure to \date{}
                part = part.replace('% <optional titlepage figure>', r'\\ \ \\ ' + '\n' + titlepage_figure)
                # Remove original titlepage figure
                part = re.sub(r'% inline figure\n\\centerline.+', '', part)
            if copyright_text:
                part = part.replace('% <optional copyright>', r'\ \\ ' + '\n' + copyright_text)

            slides += r"""
%(part)s

\begin{frame}%(frame_options)s
\titlepage
\end{frame}
""" % vars()
        elif section_slide:
            # Special section slide, not frame environment
            slides += r"""
%(part)s
""" % vars()
        elif not empty_slide:
            # Ordinary slide
            slides += r"""
\begin{frame}%(frame_options)s
%(title)s
%(part)s
\end{frame}
""" % vars()
    slides += r"""
\end{document}
"""
    slides = re.sub(r'% !split\s+', '', slides)
    return slides


def slides_beamer():
    """
    Split latex file into slides and typeset slides using
    various tools. Use !split command as slide separator.
    """

    if len(sys.argv) <= 1:
        _usage_slides_beamer()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.tex'):
        filename += '.tex'
    if not os.path.isfile(filename):
        errwarn('*** error: doconce file in latex format, %s, does not exist - abort' % filename)
        _abort()
    basename = os.path.basename(filename)
    filestem = os.path.splitext(basename)[0]

    header, parts, footer = get_header_parts_footer(filename, "latex")
    parts = tablify(parts, "latex")

    filestr = generate_beamer_slides(header, parts, footer,
                                     basename, filename)

    if filestr is not None:
        f = open(filename, 'w')
        f.write(filestr)
        f.close()
        print('slides written to ' + filename)
        if misc_option('handout', False):
            print('printing for handout:')
            print('pdfnup --nup 2x3 --frame true --delta "1cm 1cm" --scale 0.9 --outfile %s.pdf %s.pdf' %
                  (filestem, filestem))
            print('or uncomment %%\pgfpagesuselayout{... in %s.tex' % filestem)


def _usage_slides_markdown():
    print('Usage:\n'
          'doconce slides_markdown <file>[.md] <slide_type> --slide_theme=dark\n\n'
          '<slide_type>: remark (the only implemented so far)\n'
          '--slide_theme: light (default) or dark\n\n'
          'Output: <file>.html')


def slides_markdown():
    """
    Transform markdown file to remark slides.
    Must have been generated by doconce format pandoc mydoc.html --github_md
    """

    if len(sys.argv) <= 2:
        _usage_slides_markdown()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.md'):
        filename += '.md'
    if not os.path.isfile(filename):
        errwarn('*** error: doconce file in html format, %s, does not exist' % filename)
        _abort()

    f = open(filename, 'r')
    filestr = f.read()
    f.close()

    slide_type = sys.argv[2]
    if slide_type != 'remark':
        print('*** error: only remark slides are allowed, not %s' % slide_type)

    template = ('\n'
                '<!DOCTYPE html>\n'
                '<html>\n'
                '<head>\n'
                '<title>%(title)s</title>\n'
                '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n'
                '<style type="text/css">\n'
                '  @import url(https://fonts.googleapis.com/css?family=Yanone+Kaffeesatz);\n'
                '  @import url(https://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic);\n'
                '  @import url(https://fonts.googleapis.com/css?family=Ubuntu+Mono:400,700,400italic);\n'
                '\n'
                'body { font-family: \'Droid Serif\'; }\n'
                'h1, h2, h3 {\n'
                '  font-family: \'Yanone Kaffeesatz\';\n'
                '  font-weight: normal;\n'
                '}\n'
                '.remark-code, .remark-inline-code { font-family: \'Ubuntu Mono\'; }\n'
                '%(additional_styling)s\n'
                '</style>\n'
                '</head>\n'
                '\n'
                '<body>\n'
                '%(mathjax)s\n'
                '<textarea id="source">\n'
                '\n'
                '%(class_)s\n'
                '\n'
                '%(main)s\n'
                '\n'
                '</textarea>\n'
                '<script src="https://gnab.github.io/remark/downloads/remark-latest.min.js" type="text/javascript">\n'
                '</script>\n'
                '<script type="text/javascript">\n'
                '  var slideshow = remark.create();\n'
                '</script>\n'
                '</body>\n'
                '</html>\n'
                '\n')

    theme = misc_option('slide_theme=', default='light')
    class_ = 'class: center, middle'
    additional_styling = ''
    if theme == 'dark':
        class_ = 'class: center, middle, inverse'
        additional_styling = ('\n'
                              '\n'
                              '/* Style taken from the official remark demo */\n'
                              'body { font-family: \'Droid Serif\'; }\n'
                              'h1, h2, h3 {\n'
                              '  font-family: \'Yanone Kaffeesatz\';\n'
                              '  font-weight: 400;\n'
                              '  margin-bottom: 0;\n'
                              '}\n'
                              '.remark-slide-content h1 { font-size: 3em; }\n'
                              '.remark-slide-content h2 { font-size: 2em; }\n'
                              '.remark-slide-content h3 { font-size: 1.6em; }\n'
                              '.footnote { position: absolute; bottom: 3em; }\n'
                              'li p { line-height: 1.25em; }\n'
                              '.red { color: #fa0000; }\n'
                              '.large { font-size: 2em; }\n'
                              'a, a > code { color: rgb(249, 38, 114); text-decoration: none; }\n'
                              'code {\n'
                              '  -moz-border-radius: 5px;\n'
                              '  -web-border-radius: 5px;\n'
                              '  background: #e7e8e2;\n'
                              '  border-radius: 5px;\n'
                              '}\n'
                              '.remark-code, .remark-inline-code { font-family: \'Ubuntu Mono\'; }\n'
                              '.remark-code-line-highlighted { background-color: #373832; }\n'
                              '.pull-left { float: left; width: 47%; }\n'
                              '.pull-right { float: right; width: 47%; }\n'
                              '.pull-right ~ p { clear: both; }\n'
                              '#slideshow .slide .content code { font-size: 0.8em; }\n'
                              '#slideshow .slide .content pre code { font-size: 0.9em; padding: 15px; }\n'
                              '.inverse { background: #272822; color: #777872; text-shadow: 0 0 20px #333; }\n'
                              '.inverse h1, .inverse h2 {color: #f3f3f3; line-height: 0.8em; }\n'
                              '\n')

    # MathJax?
    mathjax = ''
    if '$' in filestr:
        # Fix inline math $...$ to \\( ... \\)
        filestr = re.sub(r'([^$])\$([^$]+)\$([^$])',
                         r'\g<1>\\\\( \g<2> \\\\)\g<3>', filestr,
                         flags=re.DOTALL)
        # Remove newlines before and after equations inside $$--$$
        def subst(m):
            eq = m.group(1).strip()
            return '$$\n%s\n$$\n\n' % eq

        filestr = re.sub(r'^\$\$\n+(.+?)\$\$\n+', subst,
                         filestr, flags=re.MULTILINE|re.DOTALL)
        # Insert MathJax script and newcommands
        from .html import mathjax_header
        mathjax = mathjax_header(filestr)

    # Fixes
    filestr = re.sub(r'^## ', '# ', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^### ', '## ', filestr, flags=re.MULTILINE)
    # Turn figures to HTML
    filestr = re.sub(r'^<!-- (<img.+?>.*) -->\n!\[.+$', r'.center[\g<1>]',
                     filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!\[(.*?)\]\((.+?)\)',
    #                 '.center[<img src="\g<2>" width=80%/>]',
    #                 filestr, flags=re.MULTILINE)

    # Remove notes
    filestr = re.sub(r'^<!-- !bnotes.+?^<!-- !enotes -->', '',
                     filestr, flags=re.MULTILINE|re.DOTALL)
    lines = filestr.splitlines()
    # Find title, author and date
    title = ''
    percentage_counter = 0
    for i in range(len(lines)):
        if lines[i].startswith('%'):
            percentage_counter += 1
        if percentage_counter == 1:
            # Title
            lines[i] = lines[i].replace('% ', '# ')
            title = lines[i][1:].lstrip()
        elif percentage_counter == 2:
            # Authors
            lines[i] = '\n\n### ' + '\n\n### '.join(lines[i][1:].lstrip().split(';'))
        elif percentage_counter == 3:
            # Date
            lines[i] = lines[i].replace('% ', '\n\n### ')
            break

    filestr = '\n'.join(lines)

    # Drop pop ups and other constructions
    filestr = re.sub(r'^<!-- ![be]pop -->\s+', '', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^<!-- ![be]slidecell.*\s*', '', filestr,
                     flags=re.MULTILINE)

    if '<!-- !bslidecell' in filestr:
        print('*** warning: !bslidecell-!eslidecell does not work with remark slides')
        print('    (all cells will be placed in their own row...)')

    if theme == 'dark':
        filestr = filestr.replace('<!-- !split -->', '---\nclass: inverse\n')
    else:
        filestr = filestr.replace('<!-- !split -->', '---\n')
    main = filestr
    template = template % vars()
    filename = filename.replace('.md', '.html')
    f = open(filename, 'w')
    f.write(template)
    f.close()
    print('%s slides in %s' % (slide_type, filename))
