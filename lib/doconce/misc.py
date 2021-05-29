from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from past.builtins import execfile
from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import str
from builtins import range
from past.builtins import basestring
from past.utils import old_div
import os, sys, shutil, glob, time, subprocess, codecs
import regex as re
from doconce import __version__ as version
from doconce import globals
from functools import reduce
# ---- Import a pygments syntax highlighter for DocOnce ----
from pygments.lexers import get_lexer_by_name
from pygments.lexer import RegexLexer, \
     bygroups, include, using, this, do_insertions
from pygments.token import Punctuation, Text, Comment, Keyword, \
     Name, String, Generic, Operator, Number, Whitespace, Literal
from pygments.formatters import HtmlFormatter
from pygments import highlight
from pygments.styles import get_all_styles
from doconce import __file__ as doconce_dir

doconce_dir = os.path.dirname(doconce_dir)
html_images = 'html_images.zip'
latexstyle_files = 'latex_styles.zip'

_part_filename = '._%s%03d'
_part_filename_wildcard = '._*[0-9][0-9][0-9]'

_config_path = os.path.join(os.path.expanduser('~'), '.config', 'doconce', 'default.cfg')

_legal_command_line_options = \
      [opt for opt, help in globals._registered_command_line_options]


def help_doconce():
    # Command-line interface description language: http://docopt.org/
    print(('DocOnce version %s (from %s)' % (version, os.path.dirname(doconce_dir))))
    print('Usage:\n'
          '\033[1mdoconce <command> [<argument>] <file>[.do.txt] [options]\033[0m\n\n')
    # Print all commands
    print('Commands: \n\033[1m%s\033[0m' % (' '.join(globals.doconce_commands)))
    # Print all commands with their description
    print(('\nCommands description:'))
    template = "\033[1m{0:35}\033[0m \033[94m{1:10}\033[0m"
    # Narrow down help when calling doconce <command> --help
    if sys.argv[1] in globals.doconce_commands:
        ind = globals.doconce_commands.index(sys.argv[1])
        command, help = globals._registered_commands[ind]
        print(template.format(command, help))
    else:
        for command, help in globals._registered_commands:
            print(template.format(command, help))


def help_format():
    # Command-line interface description language: http://docopt.org/
    command_line_options = globals._registered_command_line_options
    template = "\033[1m{0:35}\033[0m \033[94m{1:10}\033[0m"
    # Narrow down help when calling doconce format --<cmd-option> --help
    if sys.argv[2] == '--help':
        print(('Usage:\n'
               '\033[1mdoconce format <format> <file>[.do.txt] [options]\033[0m\n'
               '\n'
               'Generate files in a certain output format from an input DocOnce file with .txt.do suffix\n\n'
               'Formats supported:\n'))
        print('\033[1m%s\033[0m\n\n' % ' '.join(globals.supported_format_names))
        print('Help Options:')
        help_options = [('--help', 'Show help options'),
                ('CMD --help', 'Print the options for a doconce command `CMD`'),
                ('CMD --<cmd-option> --help', 'Print a specific command-line option <cmd-option> for doconce')]
        for opt, help in help_options:
            print(template.format(opt, help))
        print(('\nOptions:'))
    else:
        opts = list(map(lambda t: t[0].rstrip('='), command_line_options))
        if sys.argv[2] in opts:
            ind = opts.index(sys.argv[2])
            command_line_options = [command_line_options[ind]]
    help_print_options(command_line_options, template)

def help_print_options(cmdline_opts, template="\033[1m{0:35}\033[0m \033[94m{1:10}\033[0m"):
    """Print help

    Print formatted command options

    :param cmdline_opts: Command-line options
    :param str template: Optional template for print
    """
    for opt, help in cmdline_opts:
        if opt.endswith('='):
            opt += '...'
        print(template.format(opt, help))


def mkdir_p(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def make_config():
    # Make doconce_config_default.py file (based on newest set of options)
    config_variables = []  # list of (var, value) pairs
    for opt in _legal_command_line_options:
        var = opt[2:]
        if var[-1] == '=':
            var = var[:-1]
            value = ''
        else:
            value = 'False'
        config_variables.append((var.replace('-', '_'), value))

    config = {}
    s = '{'
    for var, value in config_variables:
        line = "'%s': %s," % (var, value)
        if value == '':
            line = '#' + line
        s += '\n    '+line
    s += '\n}'
    mkdir_p(os.path.dirname(_config_path))
    with open(_config_path, 'w') as f:
        f.write(s)

def get_config():
    if not (os.path.exists(_config_path) and os.path.isfile(_config_path)):
        print("generating config file at '%s'" % _config_path)
        make_config()
    with open(_config_path, 'r') as f:
        s = f.read()
        config = eval(s)
        #config = json.load(f)
    return config


doconce_config = get_config()

def option(name, default=None, option_list = _legal_command_line_options):
    """Return options specified in command-line

    Return value of command-line option formatted as ``--name``.
    If name ends with a = (as in --language=``value``), return the value
    or `default` in case the option was not specified.
    If name does not end with a = (as in ``--help``), return True or False whether
    the option ``--name`` is found or not.
    Abort if the option ``--name`` is not valid, ie not present in ``option_list``.


    :param str name: filename to be read
    :param any default: optional encoding string. Usually the encoding variable in globals.py
    :param list[str] option_list: optional list of command options. Default is _legal_command_line_options from globals._registered_command_line_options
    :return: string with the text read
    :rtype: str|boolean
    """
    # Note: Do not use fancy command-line parsers as much functionality
    # is dependent on command-line info (preprocessor options for instance)
    # that is not compatible with simple options( --name).

    option_name = '--' + name
    if not option_name in option_list:
        errwarn('test for illegal option: ' + option_name)
        _abort()

    # Check if a command-line option has dash instead of underscore,
    # which is a common mistake
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            if '=' in arg:
                arg = arg.split('=')[0] + '='
            if arg not in option_list and \
              ('--' + arg[2:].replace('-', '_')) in option_list:
                errwarn('found option %s, should be %s' %
                        (arg, '--' + arg[2:].replace('-', '_')))
                _abort()

    value = None  # initialization

    # Check if name is in configuration file (doconce_config)
    # and get a default value from there
    name_dash2underscore = name.replace('-', '_')
    if name_dash2underscore in doconce_config:
        value = doconce_config[name_dash2underscore]

    # Let the user's default value override that in the config file
    if default is not None:
        value = default

    # Finally, let the command line override everything
    if option_name.endswith('='):
        for arg in sys.argv[1:]:
            if arg.startswith(option_name):
                parts = arg.split('=')
                opt = parts[0]
                value = '='.join(parts[1:])
                break
    elif option_name in sys.argv:
        value = True

    return value

def check_command_line_options(option_start, option_list=_legal_command_line_options):
    """Check command-line options

    Error handling: check if all command-line options starting with --
    are legal. If not, show a message with the wrong option. This
    function does not abort the program.

    :param int option_start: start index of options to check in sys.argv
    :return: True if all command-line options are legal, False otherwise
    :rtype: boolean
    """
    #
    for arg_user in sys.argv[option_start:]:
        arg = arg_user
        if '=' in arg:
            arg = arg.split('=')[0] + '='
        if arg[:2] == '--':
            if not arg in option_list:
                errwarn('*** warning: unrecognized command-line option')
                print('    ' + arg_user)
                return False
    return True


def misc_option(name, default=None):
    """
    As option, but for options related to other doconce programs
    than doconce format.
    """
    option_name = '--' + name
    value = default
    if option_name.endswith('='):
        for arg in sys.argv[1:]:
            if arg.startswith(option_name):
                parts = arg.split('=')
                opt = parts[0]
                value = '='.join(parts[1:])
                break
    elif option_name in sys.argv:
        value = True
    return value

def debugpr(heading='', text=''):
    """Add `heading` and `text` to the log/debug file.

    :param str heading: heading to be added
    :param str text: text to be added
    """
    if option('debug'):
        if globals.encoding:
            globals._log = codecs.open('_doconce_debugging.log','a', globals.encoding)
        else:
            globals._log = open('_doconce_debugging.log','a')
        out_class = str(type(text)).split("'")[1]
        pre = '\n' + '*'*60 + '\n%s>>> ' % out_class if text else ''
        globals._log.write(pre + heading + '\n\n')
        globals._log.write(text + '\n')
        globals._log.close()

def _rmdolog():
    """Remove the .dolog file
    """
    logfilename = globals.dofile_basename + '.dolog'
    if os.path.isfile(logfilename):
        os.remove(logfilename)

def errwarn(msg, end='\n', style=''):
    """Function for reporting errors and warnings to screen and file.

    :param str msg: text message
    :param str end: string appended after the last value, default a newline
    :param str style: style msg with color or formatting
    """
    if style:
        print(globals.style[style] + msg + globals.style['_end'], end=end)
    else:
        print(msg, end=end)
    if globals.dofile_basename is None:
        return
    logfilename = globals.dofile_basename + '.dlog'
    mode = 'a' if os.path.isfile(logfilename) else 'w'
    if globals.encoding:
        err = codecs.open(logfilename, mode, globals.encoding)
    else:
        err = open(logfilename, mode)
    err.write(msg)
    if end == '\n':
        err.write('\n')

def _abort():
    """Abort the program's execution

    Print a general error and call sys.exit(1)
    """
    if '--no_abort' in sys.argv:
        errwarn('avoided abortion because of --no-abort')
    else:
        print('Abort! (add --no_abort on the command line to avoid this abortion)')
        sys.exit(1)

def system(cmd, abort_on_failure=True, verbose=False, failure_info=''):
    """Run OS commands.

    If abort_on_failure: abort when cmd gives failure and print
    command and failure_info (to explain what the command does).

    :param str cmd:
    :param bool abort_on_failure: abort when cmd gives failure
    :param bool verbose: print command run. Also triggered by DocOnce's --verbose option
    :param str failure_info: message to print when cmd gives failure
    :return: failure code from os.system()
    :rtype: int
    """
    if verbose or '--verbose' in sys.argv:
        print('running ' + cmd)
    failure = os.system(cmd)
    if failure:
        print('could not run ' + cmd + ' ' + failure_info)
        if abort_on_failure:
            _abort()
    return failure

def remove_verbatim_blocks(text, format):
    if format in ("latex", "pdflatex"):
        envirs = r'([Vv]erbatim|minted|lstlisting|latex|tex)'
        pattern = r'^\\begin\{%s\}.*^\\end\{%s\}' % (envirs, envirs)
        text = re.sub(pattern, '', text, flags=re.MULTILINE|re.DOTALL)
        # Do not remove comments too (they are actively used when searching
        # text returned from this function)
        ##text = re.sub(r'(?<=[^!?@|\\])%.*', '', text)
        return text


def load_preprocessed_doconce_file(filename, dirpath=''):
    """
    Load as complete doconce file as possible. That is,
    try to load the file after mako processing,
    tmp_mako__filename.do.txt,
    if it does not exist, try loading
    tmp_preprocess_filename.do.txt,
    and if it does not exist, try the original doconce file,
    filename.do.txt
    (it may include other files and therefore lack parts of
    the document's text).
    dirpath is a path prefix for filename. For example, if
    ../mydoc.do.txt is the original doconce file,
    filename=mydoc and dirpath=os.pardir.
    """
    after_mako = os.path.join(dirpath, 'tmp_mako__' + filename + '.do.txt')
    after_preprocess = os.path.join(dirpath, 'tmp_preprocess__' + filename + '.do.txt')
    orig_doconce = os.path.join(dirpath, filename + '.do.txt')
    if os.path.isfile(after_mako):
        dofile = open(after_mako, 'r')
        dotext = dofile.read()
        dofile.close()
    elif os.path.isfile(after_preprocess):
        dofile = open(after_preprocess, 'r')
        dotext = dofile.read()
        dofile.close()
    elif os.path.isfile(orig_doconce):
        dofile = open(orig_doconce, 'r')
        dotext = dofile.read()
        dofile.close()
    else:
        errwarn('*** error: could not find any file related to %s.do.txt in %s' % (filename, os.getcwd()))
        errwarn('    searched for:')
        errwarn('    ' + after_mako)
        errwarn('    ' + after_preprocess)
        errwarn('    ' + orig_doconce)
        _abort()
    return dotext

# -------------- functions used by the doconce program -------------

def _usage_remove_inline_comments():
    print('Usage:\n'
          'doconce remove_inline_comments <file.do.txt>')

def remove_inline_comments():
    try:
        filename = sys.argv[1]
    except IndexError:
        _usage_remove_inline_comments()
        sys.exit(0)
    if not os.path.isfile(filename):
        print('*** error: file %s does not exist!' % filename)
        sys.exit(1)

    shutil.copy(filename, filename + '.old~~')
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    from . import doconce
    filestr = doconce.subst_away_inline_comments(filestr)
    f = open(filename, 'w')
    f.write(filestr)
    f.close()
    print('inline comments removed in ' + filename)

def apply_inline_edits():
    try:
        filename = sys.argv[1]
    except IndexError:
        print('Usage:\n'
              'doconce apply_inline_edits myfile.do.txt')
        sys.exit(0)

    if not os.path.isfile(filename):
        print('*** error: file %s does not exist!' % filename)
        sys.exit(1)

    shutil.copy(filename, filename + '.old~~')
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    # pattern is taken as INLINE_TAGS['inlinecomment'] but with
    # modified names and comments patterns.
    # 1. Replacements
    pattern = r'''\[(?P<name>[A-Za-z0-9 '+-]+?):(?P<space>\s+)(?P<subst>[^\]]+?) -> (?P<replacement>.+?)\]'''
    filestr = re.sub(pattern, r'\g<replacement>', filestr, flags=re.DOTALL)
    # 2. Deletes
    pattern = r'''\[del:\s+(.*?)\]'''
    filestr = re.sub(pattern, '', filestr, flags=re.DOTALL)
    # 3. Adds
    pattern = r'''\[add:\s+(.*?)\]'''
    filestr = re.sub(pattern, r'\g<1>', filestr, flags=re.DOTALL)

    f = open(filename, 'w')
    f.write(filestr)
    f.close()
    print('inline edits applied in ' + filename)


def _usage_latin2html():
    print('Usage:\n'
          'doconce latin2html <file.html>\n\n'
          'Replace latex-1 (non-ascii) characters by html codes')


def latin2html():
    """
    Substitute latin characters by their equivalent HTML encoding
    in an HTML file. See latin2html in html.py for more
    documentation.
    """
    if len(sys.argv) < 2:
        _usage_latin2html()
        sys.exit(0)
    from .html import latin2html
    for filename in sys.argv[1:]:
        if not os.path.isfile(filename):
            print('*** error: file %s does not exist!' % filename)
            continue
        oldfilename = filename + '.old~~'
        shutil.copy(filename, oldfilename)
        print('transformin latin characters to HTML encoding in ' + filename)
        f = open(oldfilename, 'r')
        try:
            text = f.read()
            newtext = latin2html(text)
            f.close()
            f = open(filename, 'w')
            f.write(newtext)
            f.close()
        except Exception as e:
            print(e.__class__.__name__ + ' : ' + str(e))


# replace is taken from scitools
def _usage_find_nonascii_chars():
    print('Usage:\n'
          'doconce find_nonascii_chars <file1> <file2> ...')


def find_nonascii_chars():
    if len(sys.argv) <= 1:
        _usage_find_nonascii_chars()
        sys.exit(0)

    filenames = wildcard_notation(sys.argv[1:])
    for filename in filenames:
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                text = f.read()
        else:
            print('File %s not found' % filename)
            sys.exit(1)
        for i, c in enumerate(text):
            if ord(c) > 127:
                print('non-ascii character', c, ' (ord=%d)' % ord(c))
                print('appearing in the text from %s:' % filename)
                print(text[i-40:i], '--> %s <--' % c, text[i:i+40])


def _usage_gwiki_figsubst():
    print('Usage:\n'
          'doconce <wikifile.gwiki> <URL-stem>\n\n'
          'Replace figures path with URL'
          'Example:\n'
          'doconce myfile.gwiki https://code.google.com/p/myproject/trunk/doc/somedir')


def gwiki_figsubst():
    if len(sys.argv) < 3:
        _usage_gwiki_figsubst()
        sys.exit(0)
    gwikifile = sys.argv[1]
    URLstem = sys.argv[2]

    if not os.path.isfile(gwikifile):
        print('*** error: file %s does not exist!' % gwikifile)
        sys.exit(1)

    # first grep out all filenames with local path:
    shutil.copy(gwikifile, gwikifile + '.old~~')
    f = open(gwikifile, 'r')
    fstr = f.read()
    f.close()

    pattern = r'\(the URL of the image file (.+?) must be inserted here\)'
    #figfiles = re.findall(pattern, fstr)
    replacement = r'%s/\g<1>' % URLstem
    fstr, n = re.subn(pattern, replacement, fstr)
    pattern = re.compile(r'<wiki:comment>\s+Put the figure file .*?</wiki:comment>', re.DOTALL)
    fstr, n2 = pattern.subn('', fstr)
    f = open(gwikifile, 'w')
    f.write(fstr)
    f.close()
    print('Replaced %d figure references in %s' % (n, gwikifile))
    if n != n2:
        print('Something strange: %d fig references and %g comments... Bug.' % (n, n2))


# subst is taken from scitools
def _usage_subst():
    print('Usage:\n'
          'doconce subst [-s -m -x --restore] <pattern> <replacement> <file1> <file2> <file3> ...\n'
          'Options:\n'
          '--restore brings back the backup files\n'
          '-s is the re.DOTALL or re.S modifier\n'
          '-m is the re.MULTILINE or re.M modifier\n'
          '-x is the re.VERBOSE or re.X modifier')


def _scitools_subst(patterns, replacements, filenames,
                    pattern_matching_modifiers=0):
    """
    Replace a set of patterns by a set of replacement strings (regular
    expressions) in a series of files.
    The function essentially performs::

      for filename in filenames:
          file_string = open(filename, 'r').read()
          for pattern, replacement in zip(patterns, replacements):
              file_string = re.sub(pattern, replacement, file_string)

    A copy of the original file is taken, with extension `.old~~`.
    """
    # if some arguments are strings, convert them to lists:
    if isinstance(patterns, basestring):
        patterns = [patterns]
    if isinstance(replacements, basestring):
        replacements = [replacements]
    if isinstance(filenames, basestring):
        filenames = [filenames]

    # pre-compile patterns:
    cpatterns = [re.compile(pattern, pattern_matching_modifiers) \
                 for pattern in patterns]
    modified_files = dict([(p,[]) for p in patterns])  # init
    messages = []   # for return info

    for filename in filenames:
        if not os.path.isfile(filename):
            print('*** error: file %s does not exist!' % filename)
            continue
        f = open(filename, 'r');
        filestr = f.read()
        f.close()

        for pattern, cpattern, replacement in \
            zip(patterns, cpatterns, replacements):
            if cpattern.search(filestr):
                filestr = cpattern.sub(replacement, filestr)
                shutil.copy2(filename, filename + '.old~~') # backup
                f = open(filename, 'w')
                f.write(filestr)
                f.close()
                modified_files[pattern].append(filename)

    # make a readable return string with substitution info:
    for pattern in sorted(modified_files):
        if modified_files[pattern]:
            replacement = replacements[patterns.index(pattern)]
            if replacement == '':
                replacement = '<empty string>'
            messages.append('%s replaced by %s in %s' % \
                                (pattern, replacement,
                                 ', '.join(modified_files[pattern])))

    return ', '.join(messages) if messages else 'no substitutions'


def wildcard_notation(files):
    """
    On Unix, a command-line argument like *.py is expanded
    by the shell. This is not done on Windows, where we must
    use glob.glob inside Python. This function provides a
    uniform solution.
    """
    if isinstance(files, basestring):
        files = [files]  # ensure list when single filename is given
    if sys.platform[:3] == 'win':
        import glob, operator
        filelist = [glob.glob(arg) for arg in files]
        files = reduce(operator.add, filelist)  # flatten
    return files


def subst():
    if len(sys.argv) < 3:
        _usage_subst()
        sys.exit(0)

    from getopt import getopt
    optlist, args = getopt(sys.argv[1:], 'smx', ['restore'])
    if not args:
        print('no filename(s) given')
        sys.exit(1)

    restore = False
    pmm = 0  # pattern matching modifiers (re.compile flags)
    for opt, value in optlist:
        if opt in ('-s',):
            if not pmm:  pmm = re.DOTALL
            else:        pmm = pmm|re.DOTALL
        if opt in ('-m',):
            if not pmm:  pmm = re.MULTILINE
            else:        pmm = pmm|re.MULTILINE
        if opt in ('-x',):
            if not pmm:  pmm = re.VERBOSE
            else:        pmm = pmm|re.VERBOSE
        if opt in ('--restore',):
            restore = True

    if restore:
        for oldfile in args:
            newfile = re.sub(r'\.old~~$', '', oldfile)
            if not os.path.isfile(oldfile):
                print('%s is not a file!' % oldfile); continue
            os.rename(oldfile, newfile)
            print('restoring %s as %s' % (oldfile,newfile))
    else:
        pattern = args[0]; replacement = args[1]
        s = _scitools_subst(pattern, replacement,
                            wildcard_notation(args[2:]), pmm)
        print(s)  # print info about substitutions


# replace is taken from scitools
def _usage_replace():
    print('Usage:\n'
          'doconce replace from-text to-text <file1> <file2> ...')


def replace():
    if len(sys.argv) < 4:
        _usage_replace()
        sys.exit(0)

    from_text = sys.argv[1]
    to_text = sys.argv[2]
    filenames = wildcard_notation(sys.argv[3:])
    for filename in filenames:
        if not os.path.isfile(filename):
            print('*** error: file %s does not exist!' % filename)
            continue
        f = open(filename, 'r')
        text = f.read()
        f.close()
        if from_text in text:
            backup_filename = filename + '.old~~'
            shutil.copy(filename, backup_filename)
            print('replacing %s by %s in %s' % (from_text, to_text, filename))
            text = text.replace(from_text, to_text)
            f = open(filename, 'w')
            f.write(text)
            f.close()


def _usage_replace_from_file():
    print("Usage:\n"
          "doconce replace_from_file <from-to-file> <file-old> <file-new> ...\n\n"
          "<from-to-file> is a file containg two columns with the from and to parts for each substitution. "
          "Comment lines starting with # are allowed.\n"
          "The output from doconce list_labels has a form suitable for being extended with a second column "
          "with new labels and run with this command to clean up label names.")


def replace_from_file():
    """
    Replace one set of words by another set of words in a series of files. The set of words are stored in a file (given on the command line). The data format of the file is

    word replacement-word
    word
    # possible comment line, recognized by starting with #
    word
    word replacement-word

    That is, there are either one or two words on each line. In case of two words, the first is to be replaced by the second. (This format fits well with the output of list_labels)
    """
    if len(sys.argv) < 3:
        _usage_replace_from_file()
        sys.exit(0)

    fromto_file = sys.argv[1]
    f = open(fromto_file, 'r')
    fromto_lines = f.readlines()
    f.close()

    filenames = wildcard_notation(sys.argv[2:])

    for filename in filenames:
        f = open(filename, 'r')
        text = f.read()
        f.close()
        replacements = False
        for line in fromto_lines:
            if line.startswith('#'):
                continue
            words = line.split()
            if len(words) == 2:
                from_text, to_text = words

                if from_text in text:
                    backup_filename = filename + '.old~~'
                    shutil.copy(filename, backup_filename)
                    print('replacing %s by %s in %s' % (from_text, to_text, filename))
                    text = text.replace(from_text, to_text)
                    replacements = True
        if replacements:
            f = open(filename, 'w')
            f.write(text)
            f.close()


def _usage_find():
    print('Usage:\n'
          'doconce find <expression>\n\n'
          'Searches for all .do.txt files in subdirectories and writes out filename, line number and line containing expression\n'
          '<expression> is interpreted as a regular expression (the command is similar to a Unix find & grep)\n')


def find():
    if len(sys.argv) < 2:
        _usage_find()
        sys.exit(0)
    expression = sys.argv[1]
    for dirpath, dirnames, filenames in os.walk(os.curdir):
        for filename in filenames:
            if filename.endswith('.do.txt') and not filename.startswith('tmp_'):
                filename = os.path.join(dirpath, filename)
                with open(filename, 'r') as f:
                    found = False
                    for i, line in enumerate(f.readlines()):
                        m = re.search(expression, line)
                        if m:
                            if not found:
                                print() # newline between files
                            print('%s, %4d: %s' % (filename, i+1, m.group()))
                            found = True


def _usage_include_map():
    print('Usage:\n'
          'doconce include_map <file>[.do.txt]\n'
          'List all recursive includes in a DocOnce <file>')


def include_map():
    if len(sys.argv) < 2:
        _usage_include_map()
        sys.exit(0)
    filename = sys.argv[1]
    # Could have preprocess variables for include at the rest of the
    # command line

    def find_include(name, indent=''):
        if not os.path.isfile(name):
            print('*** file "%s" was not found!' % name)
            # Could be non-existing or the filename may contain
            # preprocess variable(s)
            return
        with open(name, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if '#include ' in line:
                includefile = line.split('#include')[1].strip()[1:-1]
                includefile = os.path.join(os.path.dirname(name), includefile)
                print(indent + ' #include ' + includefile)
                find_include(includefile, indent + '    ')

    print(filename)
    find_include(filename)


def _usage_expand_mako():
    print('Usage:\n'
          'doconce expand_mako <mako_code_file.txt> <funcname> <file>[.do.txt]\n\n'
          'Replaces mako calls to functions by the function bodies')

# This replacement function for re.sub must be global since expand_mako,
# where it is used, has an exec statement

def expand_mako():
    if len(sys.argv) < 4:
        _usage_expand_mako()
        sys.exit(0)
    mako_filename = sys.argv[1]
    funcname = sys.argv[2]
    filenames = wildcard_notation(sys.argv[3:])

    # Get mako function code
    f = open(mako_filename, 'r')
    mako_text = f.read()
    f.close()
    func_lines = []
    inside_func = False
    for line in mako_text.splitlines():
        if re.search(r'^\s*def\s+%s' % funcname, line):  # starts with funcname?
            inside_func = True
            func_lines.append(line)
        elif inside_func:
            if line == '' or line[0] == ' ':  # indented line?
                func_lines.append(line)
            else:
                inside_func = False

    funcname_text = '\n'.join(func_lines)
    print('Extracted function %s from %s:\n' % (funcname, mako_filename) + funcname_text)
    print(func_lines)
    try:
        exec(funcname_text)
    except Exception as e:
        print('*** error: could not turn function code into a Python function')
        print(e)
        _abort()
        # Note: if funcname has FORMAT tests the exec will fail, but
        # one can make an alternative version of funcname in another file
        # where one returns preprocess # #if FORMAT in ... statements
        # in the returned text.

    # Substitute ${funcname(..., ..., ...)}
    pattern = r'(\$\{(%(funcname)s\s*\(.+?\))\})' % vars()

    for filename in filenames:
        # Just the filestem without .do.txt is allowed
        if not filename.endswith('.do.txt'):
            filename += '.do.txt'
        if not os.path.isfile(filename):
            print('*** error: file %s does not exist!' % filename)
            continue
        f = open(filename, 'r')
        text = f.read()
        f.close()
        m = re.search(pattern, text, flags=re.DOTALL)
        if m:
            backup_filename = filename + '.old~~'
            shutil.copy(filename, backup_filename)
            print('expanding mako function %s in %s' % (funcname, filename))
            calls = re.findall(pattern, text, flags=re.DOTALL)
            for mako_call, python_call in calls:
                try:
                    replacement = eval(python_call)
                except Exception as e:
                    print('*** error: could not run call\n%s' % python_call)
                    _abort()
                text = text.replace(mako_call, replacement)

            f = open(filename, 'w')
            f.write(text)
            f.close()


def _usage_linkchecker():
    print('Usage:\n'
          'doconce linkchecker (<file1.html> | <file1.do.txt> | <tmp_mako__file1.do.txt>) ...\n\n'
          'Check if URLs or links to local files in DocOnce or HTML files are valid.')


def linkchecker():
    if len(sys.argv) <= 1:
        _usage_linkchecker()
        sys.exit(0)
    from .common import is_file_or_url
    prefix = '(file:///|https?://|ftp://)'
    pattern_html = r'href="(%s.+?)"' % prefix
    pattern_do = r'''"[^"]+?" ?:\s*"(%s.+?)"''' % prefix
    missing = []
    for filename in sys.argv[1:]:
        ext = os.path.splitext(filename)[1]
        if not ext in ('.html', '.htm', '.txt'):
            print('*** error: %s is not a DocOnce or HTML file' % filename)
            continue
        f = open(filename, 'r')
        text = f.read()
        f.close()
        if filename.endswith('.do.txt'):
            pattern = pattern_do
        else:
            patterh = pattern_html
        links = re.findall(pattern, text, flags=re.IGNORECASE)
        missing.append([filename, []])
        for link in links:
            check = is_file_or_url(link, msg=None)
            if check in ('file', 'url'):
                print('%s:' % filename + ' ' + link + ' exists as ' + check)
            else:
                print('%s:' % filename + ' ' + link + ' WAS NOT FOUND')
                missing[-1][1].append(link)
    for filename, missing_links in missing:
        if missing_links:
            print('\n\n*** missing links in %s:\n%s' % \
                  (filename, '\n'.join(['"%s"' % link
                                        for link in missing_links])))


def _dofix_localURLs(filename, exclude_adr):
    if os.path.splitext(filename)[1] != '.rst':
        print('Wrong filename extension in "%s" - must be a .rst file' % filename)
        _abort()

    f = open(filename, 'r')
    text = f.read()
    f.close()
    """
    # This is for doconce format:
    link1 = r'''"(?P<link>[^"]+?)" ?:\s*"(?P<url>([^"]+?\.html?|[^"]+?\.txt|[^"]+?\.pdf|[^"]+?\.f|[^"]+?\.c|[^"]+?\.cpp|[^"]+?\.cxx|[^"]+?\.py|[^"]+?\.java|[^"]+?\.pl))"'''
    link2 = r'("URL"|"url"|URL|url) ?:\s*"(?P<url>.+?)"'
    groups1 = [(link, url) for link, url, url in re.findall(link1, text)]
    print(groups1)
    print(groups2)
    """
    link_pattern = r'<([A-Za-z0-9/._-]+?)>`_'
    links = re.findall(link_pattern, text)
    num_fixed_links = 0
    for link in links:
        if link in exclude_adr:
            print('not modifying ' + link)
            if link.endswith('htm') or link.endswith('html'):
                print('Note: %s\n      is an HTML file that may link to other files.\n      This may require copying many files! Better: link to _static directly in the doconce document.' % link)
            continue
        if not (link.startswith('http') or link.startswith('file:/') or \
            link.startswith('_static')):
            if os.path.isfile(link):
                if not os.path.isdir('_static'):
                    os.mkdir('_static')
                newlink = os.path.join('_static', os.path.basename(link))
                text = text.replace('<%s>' % link, '<%s>' % newlink)
                print('fixing link to %s as link to %s' % (link, newlink))
                print('       copying %s to _static' % os.path.basename(link))
                shutil.copy(link, newlink)
                if link.endswith('htm') or link.endswith('html'):
                    print('Note: %s\n      is an HTML file that may link to other files.\n      This may require copying many files! Better: link to _static directly in the doconce document.' % link)
                num_fixed_links += 1
    if num_fixed_links > 0:
        os.rename(filename, filename + 'old~~')
        f = open(filename, 'w')
        f.write(text)
        f.close()
    return num_fixed_links


def _usage_sphinxfix_localURLs():
    print('Usage:\n'
          'doconce sphinxfix_localURLs <file1.rst> <file2.rst> ... -not adr1 adr2 ...\n\n'
          'Each link to a local file, e.g., "link": "src/dir1/myfile.txt", is replaced by a link \n'
          'to the file placed in _static: "link": "_static/myfile.txt". The file myfile.txt is copied\n'
          'from src/dir1 to _static. The user must later copy all _static/* files to the _static \n'
          'subdirectory in the sphinx directory. Note that local links to files in _static are not modified.\n'
          '\n'
          'The modification of links is not always wanted. The -not adr1 adr2 makes it possible to exclude\n'
          'modification of a set of addresses adr1, adr2, ...\n'
          '\n'
          'Example:\n'
          'doconce sphinxfix_localURLs <file1.rst> <file2.rst> -not src/dir1/mymod1.py src/dir2/index.html\n\n'
          'The old files are available as <file1.rst>.old~~, file2.rst.old~~ etc.\n\n'
          'Note that local links to HTML files which are linked to other local HTML documents (say a Sphinx\n'
          'document) demand all relevant files to be copied to _static. In such cases it is best to physically\n'
          'place the HTML documents in _static and let the DocOnce document link directly to _static.\n'
          '\n'
          'In general, it is better to link to _static from the DocOnce document rather than relying on the \n'
          'fixes in this script...\n')


def sphinxfix_localURLs():
    if len(sys.argv) < 2:
        _usage_sphinxfix_localURLs()
        sys.exit(0)
    # Find addresses to exclude
    idx = -1  # index in sys.argv for the -not option
    for i, arg in enumerate(sys.argv[1:]):
        if arg.endswith('-not'):
            idx = i+1
    exclude_adr = sys.argv[idx+1:] if idx > 0 else []
    if idx > 0:
       del sys.argv[idx:]
    for filename in sys.argv[1:]:
        if os.path.dirname(filename) != '':
            print('doconce sphinxfix_localURLs must be run from the same directory as %s is located in' % filename)
        num_fixed_links = _dofix_localURLs(filename, exclude_adr)
        if num_fixed_links > 0:
            print("\nYou must copy _static/* to the sphinx directory's _static directory")


def _usage_latex_exercise_toc():
    print('Usage:\n'
          'doconce latex_exercise_toc <file>[.do.txt] ["List of exercises"]\n\n'
          'The following line can be inserted in the text of an exercise:\n'
          '# Short: My own short title\n'
          'This defines a short version of the title of the exercise to be used in the toc table.\n'
          'This is convenient when the automatic truncation of (long) titles fails (it happens if \n'
          'truncated in the middle of mathematical $...$ constructions). Any short title is\n'
          'appearing in the table exactly how it is written, so this is also a method to avoid\n'
          'truncating a title.')


def latex_exercise_toc():
    if len(sys.argv) < 2:
        _usage_latex_exercise_toc()
        sys.exit(0)
    dofile = sys.argv[1]
    if dofile.endswith('.do.txt'):
        dofile = dofile[:-7]
    exerfile = '.' + dofile + '.exerinfo'
    if not os.path.isfile(exerfile):
        print('no file %s with exercises from %s found' % (exerfile, dofile))
        return

    f = open(exerfile, 'r')
    exer = eval(f.read())
    f.close()

    try:
        heading = sys.argv[2]
    except IndexError:
        # Build default heading from types of environments found
        types_of_exer = set()
        for ex in exer:
            if ex['type'] != 'Example':
                types_of_exer.add(ex['type'])
        types_of_exer = list(types_of_exer)
        types_of_exer = ['%ss' % tp for tp in types_of_exer]  # plural
        types_of_exer = [tp for tp in sorted(types_of_exer)]  # alphabetic order
        if len(types_of_exer) == 1:
            types_of_exer = types_of_exer[0]
        elif len(types_of_exer) == 2:
            types_of_exer = ' and '.join(types_of_exer)
        elif len(types_of_exer) > 2:
            types_of_exer[-1] = 'and ' + types_of_exer[-1]
            types_of_exer = ', '.join(types_of_exer)
        heading = "List of %s" % types_of_exer
    latex = r"""
\clearpage %% pagebreak before list of exercises
\subsection*{%s}
\\begin{tabular}{lrll}
""" % heading
    max_title_length = 45
    for ex in exer:
        if ex['type'] == 'Example':
            continue
        title = ex['title']
        # Short title?
        short = ''
        for line in ex['text'].splitlines():
            m = re.search(r'#\s*[Ss]hort:\s*(.+)', line)
            if m:
                short = m.group(1).strip()
                title = short
                break
        if not short:
            # Truncate long titles
            if len(title) > max_title_length:
                words = title.split()
                title = []
                for word in words:
                    title.append(word)
                    if len(' '.join(title)) > max_title_length - 5:
                        title.append('...')
                        break
                title = ' '.join(title)
        title = title.replace('\\', '\\\\') # re.sub later swallows \
        latex += ex['type'] + ' & ' + str(ex['no']) + ' & ' + title
        if ex['label']:
            latex += r' & p.~\pageref{%s}' % ex['label']
        else:
            # Leave pageref empty
            latex += ' &'
        latex += ' \\\\\\\\' + '\n'
        # (need 8 \ for \\ to survive because re.sub below eats them)
    latex += r"""\end{tabular}
% --- end of table of exercises
\clearpage % pagebreak after list of exercises

"""
    texfile = dofile + '.p.tex'
    if os.path.isfile(texfile):
        f = open(texfile, 'r')
    else:
        texfile = dofile + '.tex'
        if os.path.isfile(texfile):
            f = open(texfile, 'r')
        else:
            print('*** error: no .tex or .p.tex file for %s' % dofile)
            sys.exit(1)
    shutil.copy(texfile, texfile + '.old~~')
    filestr = f.read()
    f.close()
    if r'\tableofcontents' in filestr:
        # Insert table of exercises on the next line
        filestr = re.sub(r'(tableofcontents.*$)', '\g<1>\n' + latex,
                         filestr, flags=re.MULTILINE)
        f = open(texfile, 'w')
        f.write(filestr)
        print('table of exercises inserted in ' + texfile)
        f.close()
    else:
        print('*** error: cannot insert table of exercises because there is no')
        print('    table of contents requested in the ' + dofile + ' document')


def _usage_combine_images():
    print('Usage:\n'
          'doconce combine_images (pdf | png) [-4] <image1> <image2> ... <output_file>\n\n'
          'Applies montage if not PDF or EPS images, else pdftk, pdfnup and pdfcrop.\n'
          'Images are combined with two each row, by default, but doconce combine_images -3 ... gives 3 '
          'images in each row. The first command-line argument can be a file extension and the '
          'filenames can then be given without extension:\n\n'
          'Example:\n'          
          'doconce combine_images pdf -2 u1 u2 u12')


def combine_images():

    if len(sys.argv) < 3:
        _usage_combine_images()
        sys.exit(0)

    if sys.argv[1] in ('pdf', 'png', 'jpg', 'eps', 'ps', 'jpeg', 'tif', 'tiff'):
        extension = sys.argv[1]
        del sys.argv[1]
    else:
        extension = None

    if sys.argv[1].startswith('-'):
        num_columns = int(sys.argv[1][1:])
        del sys.argv[1]
    else:
        num_columns = 2

    bitmap_formats = '.png', '.tif', '.tiff', '.gif', '.jpeg', '.jpg'
    imagefiles = sys.argv[1:-1]
    # See if files have extension
    for i in range(len(imagefiles)):
        basename, ext = os.path.splitext(imagefiles[i])
        if not ext and extension is not None:
            imagefiles[i] = imagefiles[i] + '.' + extension

    for name in imagefiles:
        if not os.path.isfile(name):
            print('*** error: file "%s" is non-existing' % name)
            _abort()
    output_file = sys.argv[-1]
    basename, ext = os.path.splitext(output_file)
    if not ext and extension is not None:
        output_file += '.' + extension

    ext = [os.path.splitext(f)[1] for f in imagefiles]
    montage = False
    # If one of the formats in formats: montage = True
    for format in bitmap_formats:
        if format in ext:
            montage = True

    cmds = []
    if montage:
        cmds.append('montage -background white -geometry 100%% -tile %dx %s %s' % (num_columns, ' '.join(imagefiles), output_file))
        cmds.append('convert -trim %s %s' % (output_file, output_file))

    else:
        # Assume all are .pdf or .eps
        # Convert EPS to PDF
        for i in range(len(imagefiles)):
            f = imagefiles[i]
            if '.eps' in f:
                cmds.append('ps2pdf -DEPSCrop %s' % f)
                imagefiles[i] = f.replace('.eps', '.pdf')

        # Combine PDF images
        num_rows = int(round(old_div(len(imagefiles),float(num_columns))))
        cmds.append('pdftk %s output tmp.pdf' % ' '.join(imagefiles))
        cmds.append('pdfnup --nup %dx%d --outfile tmp.pdf tmp.pdf' % (num_columns, num_rows))
        cmds.append('pdfcrop tmp.pdf %s' % output_file)
        cmds.append('rm -f tmp.pdf')
    print()
    for cmd in cmds:
        system(cmd, verbose=True)
    print('output in ' + output_file)


def _usage_expand_commands():
    print('Usage:\n'
          'doconce expand_commands <file1> <file2> ...\n\n'
          'A file .expand_commands may define _replace and _regex_subst lists for str.replace and re.sub \n'
          'substitutions (respectively) to be applied to <file1> <file2> ...\n\n'
          'By default we use some common LaTeX math abbreviations:\n'
          '_replace = [\n'
          r"(r'\bals', r'\begin{align*}'),  # must appear before \bal"
          '\n'
          r"(r'\eals', r'\end{align*}'),"
          '\n'
          r"(r'\bal', r'\begin{align}'),"
          '\n'
          r"(r'\eal', r'\end{align}'),"
          '\n'
          r"(r'\beq', r'\begin{equation}'),"
          '\n'
          r"(r'\eeq', r'\end{equation}'),"
          '\n'
          ']\n\n'
          '_regex_subst = []\n')


def expand_commands():
    if len(sys.argv) < 2:
        _usage_expand_commands()
        sys.exit(0)

    # Default set of str.replace and re.sub substitutions
    _replace = [
    (r'\bals', r'\begin{align*}'),  # must appear before \bal
    (r'\eals', r'\end{align*}'),
    (r'\bal', r'\begin{align}'),
    (r'\eal', r'\end{align}'),
    (r'\beq', r'\begin{equation}'),
    (r'\eeq', r'\end{equation}'),
    ]

    # These \ep subst don't work properly
    _regex_subst = [
    (r'^\ep\n', r'\\thinspace .\n', re.MULTILINE),
    (r'\ep\n', r' \\thinspace .\n'),
    (r'\ep\s*\\\]', r' \\thinspace . \]'),
    (r'\ep\s*\\e', r' \\thinspace . \e'),
    (r' \\thinspace', 'thinspace'),
    ]
    _regex_subst = []

    expand_commands_file = '.expand_commands'
    if os.path.isfile(expand_commands_file):
        execfile(expand_commands_file)
    else:
        replace = []
        regex_subst = []
    # Add standard definitions (above)
    replace += _replace
    regex_subst += _regex_subst

    filenames = sys.argv[1:]
    for filename in filenames:
        changed = False
        f = open(filename, 'r')
        text = f.read()
        f.close()
        for from_, to_ in replace:
            if from_ in text:
                text = text.replace(from_, to_)
                print('replacing %s by %s in %s' % (from_, to_, filename))
                changed = True
        for item in regex_subst:
            if len(item) == 2:
                from_, to_ = item
                if re.search(from_, text):
                    text = re.sub(from_, to_, text)
                    print('substituting %s by %s in %s' % (from_, to_, filename))
                    changed = True
            elif len(item) == 3:
                frm_, to_, modifier = item
                if re.search(from_, text, flags=modifier):
                    text = re.sub(from_, to_, text, flags=modifier)
                    print('substituting %s by %s in %s' % (from_, to_, filename))
                    changed = True
        if changed:
            shutil.copy(filename, filename + '.old~~')
            f = open(filename, 'w')
            f.write(text)
            f.close()


def copy_latex_packages(packages):
    """
    Copy less well-known latex packages to the current directory
    if the packages are not found on the (Unix) system.
    """
    datafile = latexstyle_files  # global variable (latex_styles.zip)
    missing_files = []
    import subprocess
    for style in packages:
        stem, ext = os.path.splitext(style)
        if ext == '':
            style += '.sty'
        cmd = 'kpsewhich %s' % style
        output = ''
        try:
            output = subprocess.check_output(cmd, shell=True,
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            pass
        if output == '':
            missing_files.append(style)
    if missing_files:
        # Copy zipfile with styles to current dir
        print('*** missing style files:')
        print('    ' + ', '.join(missing_files))
        from . import doconce
        doconce_dir = os.path.dirname(doconce.__file__)
        doconce_datafile = os.path.join(doconce_dir, datafile)
        shutil.copy(doconce_datafile, os.curdir)
        import zipfile
    for filename in missing_files:
        # Extract file from zip archive
        if not os.path.isfile(filename):
            try:
                zipfile.ZipFile(datafile).extract(filename)
                msg = 'extracted'
            except:
                msg = 'could not extract'
            print('%s %s (from %s in the doconce installation)' % \
                  (msg, filename, latexstyle_files))
    if os.path.isfile(datafile):
        os.remove(datafile)


def _usage_ptex2tex():
    print((
        'Usage:\n'
        'doconce ptex2tex <file>[.p.tex] [-Dvar1=val1 ...] \\\n'
        r"'[cod=\begin{quote}\begin{verbatim}@\end{verbatim}\end{quote} pypro=Verbatim fcod=minted ccod=ans "
        r"cpppro=anslistings:nt]'"
        '\n\n'
        'doconce ptex2tex <file>[.p.tex] -Dvar1=val1 ... envir=ans:nt\n\n'
        r'doconce ptex2tex <file>[.p.tex] \\'
        '\n'
        r"'sys=\begin{Verbatim}[frame=lines,label=\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt]"
        r"@\end{Verbatim}' \\"
        '\n'
        r"envir=minted --minted_leftmargin=2"
        '\n  (recall quotes in arguments with backslash),\n\n'
        'doconce ptex2tex <file>[.p.tex] envir=Verbatim\n'
        '\n'
        'Verbatim (from fancyvrb) is the default value for envir and is used for all environments, with some options '
        'added (base linestretch 0.85 and font size 9pt).\n'
        '\n'
        'Note that specifications of how "!bc environment" is to be typeset in latex is done by environment=begin@end, '
        'where begin is the latex begin command, end is the latex end command, and the two must be separated by the '
        r'at sign (@). Writing just environment=package implies the latex commands \begin{package} and \end{package}.'
        '\n\n'
        'Choosing environment=minted gives the minted environment with the specified language inserted. Similarly, '
        'environment=ans, environment=ans:nt, environment=anslistings, or environment=anslistings:nt imply the '
        'anslistings package with the right environment'
        r'(\begin{c++:nt} for instance for !bc cppcod or !bc cpppro, environment=ans:nt - :nt means no title over '
        r'the code box).'
        '\n\n'
        'If environment is simply the string "envir", the value applies to all registered environments. Specifying '
        'e.g. sys=... and then envir=ans, will substitute the sys environment by the specified syntax and all other '
        'environments will apply the latex construct from anslistings.sty.'
    ))


def ptex2tex():
    if len(sys.argv) <= 1:
        _usage_ptex2tex()
        sys.exit(0)

    filename = sys.argv[1]
    if filename.endswith('.p.tex'):
        filename = filename[:-6]
    if not os.path.isfile(filename + '.p.tex'):
        print('no file %s' % (filename + '.p.tex'))
        _abort()
    f = open(filename + '.p.tex', 'r')
    ptex2tex_filestr = f.read()
    f.close()

    # All envirs in the .ptex2tex.cfg file as of June 2012.
    # (Recall that the longest names must come first so that they
    # are substituted first, e.g., \bcc after \bccod)
    envirs = ['pro', 'pypro', 'cypro', 'cpppro', 'cpro', 'fpro', 'plpro', 'shpro', 'mpro',
              'cod', 'pycod', 'cycod', 'cppcod', 'ccod', 'fcod', 'plcod', 'shcod', 'mcod',
              'rst', 'cppans', 'pyans', 'fans', 'bashans', 'swigans', 'uflans', 'sni',
              'dat', 'dsni', 'sys', 'slin', 'ipy', 'pyshell', 'rpy', 'plin', 'ver', 'warn',
              'rule', 'summ', 'ccq', 'cc', 'ccl', 'txt', 'htmlcod', 'htmlpro', 'html', 'rbpro',
              'rbcod', 'rb', 'xmlpro', 'xmlcod', 'xml', 'latexpro', 'latexcod', 'latex']
    # envirs is not longer used - we just read what the user has in the file

    # Accept all envirs in envir2syntax, plus all
    # registered lexers in pygments
    from .common import get_legal_pygments_lexers
    ptex2tex_begin_pattern = r'^\\b([a-z0-9+_]+)$'
    user_envirs = re.findall(ptex2tex_begin_pattern, ptex2tex_filestr,
                             flags=re.MULTILINE)

    # Process command-line options

    preprocess_options = []  # -Dvariable or -Dvariable=value
    envir_user_spec = []     # user's specified environments
    for arg in sys.argv[2:]:
        if arg.startswith('-D') or arg.startswith('-U'):
            preprocess_options.append(arg)
        elif '=' in arg:
            # envir
            items = arg.split('=')
            envir, value = items[0], '='.join(items[1:])
            if '@' in value:
                begin, end = value.split('@')

                if envir == 'envir':
                    # User specifies all ptex2tex environments at once
                    # as "envir=begin@end"
                    for e in user_envirs:
                        envir_user_spec.append((e, begin, end))
                else:
                    envir_user_spec.append((envir, begin, end))
            else:
                # Fix value=minted and value=ans*:
                # they need the language explicitly
                if value == 'minted':
                    envir2syntax = dict(
                        do='doconce',
                        pyshell='python',
                        py='python', cy='cython', f='fortran',
                        c='c', cpp='c++', cu='cuda', cuda='cuda', sh='bash', rst='rst', swig='c++',
                        m='matlab', pl='perl',
                        latex='latex',
                        html='html',
                        xml='xml', rb='ruby', sys='console',
                        js='js', java='java',
                        dat='text', txt='text', csv='text',
                        ipy='ipy'
                        # pyopt and pysc are treated in latex.py
                    )
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

                    legal_lexers = get_legal_pygments_lexers()
                    for user_envir in user_envirs:
                        if user_envir in envir2syntax:
                            pass
                        elif user_envir in legal_lexers:
                            envir2syntax[user_envir] = user_envir

                    if envir == 'envir':
                        leftmargin = '7' # mm
                        for arg in sys.argv[1:]:
                            if arg.startswith('--minted_leftmargin='):
                                leftmargin = arg.split('=')[1]
                        for lang in envir2syntax:
                            # mathescape can be used with minted and lstlisting
                            # see https://tex.stackexchange.com/questions/149710/how-to-write-math-symbols-in-a-verbatim, minted can only have math in comments within the code
                            # but mathescape make problems with bash and $#
                            # (can perhaps be fixed with escapechar=... but
                            # I haven't found out)
                            if lang != 'sh':
                                begin = '\\' + 'begin{minted}[fontsize=\\fontsize{9pt}{9pt},linenos=false,mathescape,baselinestretch=1.0,fontfamily=tt,xleftmargin=%smm]{' % leftmargin + envir2syntax[lang] + '}'
                            else:
                                begin = '\\' + 'begin{minted}[fontsize=\\fontsize{9pt}{9pt},linenos=false,baselinestretch=1.0,fontfamily=tt,xleftmargin=%smm]{' % leftmargin + envir2syntax[lang] + '}'
                            end = '\\' + 'end{minted}'
                            envir_user_spec.append((lang, begin, end))
                    else:
                        for lang in envir2syntax:
                            if envir.startswith(lang + 'cod') or \
                               envir.startswith(lang + 'pro'):
                                begin = '\\' + 'begin{' + value + '}{' \
                                        + envir2syntax[lang] + '}'
                                end = '\\' + 'end{' + value + '}'
                                envir_user_spec.append((envir, begin, end))
                elif value.startswith('ans'):
                    # Mapping from code envirs to valid anslistings names
                    envir2listings = dict(
                        pyshell='python',
                        py='python', cy='python', f='fortran',
                        cpp='c++', sh='bash', swig='swigcode',
                        ufl='uflcode', m='matlab', c='c++',
                        latex='latexcode', xml='xml',
                        pyopt='python', ipy='python')
                    if envir == 'envir':
                        for lang in envir2listings:
                            language = envir2listings[lang]
                            if value.endswith(':nt'):
                                language += ':nt'
                            begin = '\\' + 'begin{' + language + '}'
                            end = '\\' + 'end{' + language + '}'
                            envir_user_spec.append((lang, begin, end))
                    else:
                        for lang in envir2listings:
                            if envir.startswith(lang + 'cod') or \
                               envir.startswith(lang + 'pro'):
                                lang = envir2listings[lang]
                                if value.endswith(':nt'):
                                    lang += ':nt'
                                begin = '\\' + 'begin{' + lang + '}'
                                end = '\\' + 'end{' + lang + '}'
                                envir_user_spec.append((envir, begin, end))
                else:
                    # value is not minted or ans*
                    options = ''
                    if value == 'Verbatim':
                        # provide lots of options
                        options = r'[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.95,xleftmargin=0mm]'
                    elif value == 'Verbatim-0.85':
                        # provide lots of options
                        options = r'[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.85,xleftmargin=0mm]'
                    elif value == 'Verbatim-indent':
                        options = r'[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.95,xleftmargin=8mm]'

                    begin = '\\' + 'begin{' + value + '}' + options
                    end = '\\' + 'end{' + value + '}'
                    if envir == 'envir':
                        for e in user_envirs:
                            envir_user_spec.append((e, begin, end))
                    else:
                        envir_user_spec.append((envir, begin, end))

    # Find which environments that will be defined and which
    # latex packages that must be included.

    ans = ['c++', 'c', 'fortran', 'python', 'cython', 'xml',
           'bash', 'swigcode', 'uflcode', 'matlab', 'progoutput',
           'latexcode', 'anycode']
    ans = ans + [i+':nt' for i in ans]
    package2envir = dict(fancyvrb='Verbatim', anslistings=ans, minted='minted')
    latexenvir2package = {}
    for package in package2envir:

        if isinstance(package2envir[package], list):
            for latexenvir in package2envir[package]:
                latexenvir2package[latexenvir] = package
        else: # str
            latexenvir2package[package2envir[package]] = package
    #import pprint; pprint.pprint(envir_user_spec)
    # Run through user's specifications and grab latexenvir from
    # end = \end{latexenvir}, find corresponding package and add to set
    packages = set()
    for envir, begin, end in envir_user_spec:
        m = re.search(r'\\end\{(.+?)\}', end)
        if m:
            latexenvir = m.group(1)
            if latexenvir in latexenvir2package:
                packages.add(latexenvir2package[latexenvir])
            else:
                print('No package known for latex environment "%s" ' % latexenvir)
    packages = list(packages)
    # fancyvrb is needed for \code{...} -> \Verb!...! translation
    if not 'fancyvrb' in packages:
        packages.append('fancyvrb')

    # Run preprocess
    if not preprocess_options:
        if 'minted' in packages:
            preprocess_options += ['-DMINTED']
    if '-DMINTED' in preprocess_options and 'minted' in packages:
        packages.remove('minted')  # nicer with just one \usepackage{minted}


    output_filename = filename + '.tex'
    cmd = 'preprocess %s %s > %s' % \
          (' '.join(preprocess_options),
           filename + '.p.tex',
           output_filename)
    system(cmd, failure_info="""
preprocess failed or is not installed;
download preprocess from https://code.google.com/p/preprocess""")

    # Mimic ptex2tex by replacing all code environments by
    # a plain verbatim command
    f = open(output_filename, 'r')
    filestr = f.read()
    f.close()

    # Replace the environments specified by the user
    from .latex import fix_latex_command_regex
    for envir, begin, end in envir_user_spec:
        for postfix in ['cod', 'pro', '']:
            ptex2tex_begin = '\\' + 'b' + envir + postfix
            ptex2tex_end = '\\' + 'e' + envir + postfix
            begin_pattern = r'^\%s$' % ptex2tex_begin
            end_pattern = r'^\%s$' % ptex2tex_end
            if re.search(fix_latex_command_regex(begin_pattern),
                         filestr, flags=re.MULTILINE):
                filestr = re.sub(
                    begin_pattern,
                    fix_latex_command_regex(begin, application='replacement'),
                    filestr, flags=re.MULTILINE)
                filestr = re.sub(
                    end_pattern,
                    fix_latex_command_regex(end, application='replacement'),
                    filestr, flags=re.MULTILINE)
                print('%s (!bc %s) -> %s\n' % (ptex2tex_begin, envir, begin))

    # Replace other environments by a default choice
    begin = r"""\begin{Verbatim}[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.95]"""
    end = r"""\end{Verbatim}"""
    #begin = r"""\begin{quote}\begin{verbatim}"""
    #end = r"""\end{verbatim}\end{quote}"""
    for envir in user_envirs:
        ptex2tex_begin = '\\' + 'b' + envir
        ptex2tex_end = '\\' + 'e' + envir
        begin_pattern = r'^\%s$' % ptex2tex_begin
        end_pattern = r'^\%s$' % ptex2tex_end
        if re.search(fix_latex_command_regex(begin_pattern),
                     filestr, flags=re.MULTILINE):
            filestr = re.sub(
                begin_pattern,
                fix_latex_command_regex(begin, application='replacement'),
                filestr, flags=re.MULTILINE)
            filestr = re.sub(
                end_pattern,
                fix_latex_command_regex(end, application='replacement'),
                filestr, flags=re.MULTILINE)
            print('%s (!bc %s) -> %s ("%s" is unsupported so we use Verbatim)\n' % (ptex2tex_begin, envir, begin, envir))

    # Make sure we include the necessary verbatim packages
    if packages:
        filestr = filestr.replace(r'\usepackage{ptex2tex}',
           r'\usepackage{%s} %% packages needed for verbatim environments' %
                                          (','.join(packages)))
    else:
        filestr = filestr.replace(r'\usepackage{ptex2tex}', '')

    # Copy less well-known latex packages to the current directory
    stylefiles = [name for name in ['minted', 'anslistings', 'fancyvrb']
                  if name in packages]
    # preprocess is run so we can check which less known packages
    # that are required
    less_known_packages = ['mdframed', 'titlesec',]  # more?
    #stylefiles += less_known_packages
    copy_latex_packages(stylefiles)


    if 'minted' in packages:
        cmd = 'pygmentize'
        try:
            output = subprocess.check_output(cmd, shell=True,
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(r"""You have requested the minted latex style, but this
requires the pygments package to be installed. On Debian/Ubuntu: run
Terminal> sudo apt-get install python-pygments
Or
Terminal> git clone https://bitbucket.org/birkenfeld/pygments-main pygments
Terminal> cd pygments; python setup.py install
""")
            _abort()

    filestr = replace_code_command(filestr)

    f = open(output_filename, 'w')
    f.write(filestr)
    f.close()
    print('output in ' + output_filename)


def replace_code_command(filestr):
    """Replace \code{...} by \Verb!...! or \textttt{...}."""

    # Remove one newline (two implies far too long inline verbatim)
    pattern = re.compile(r'\\code\{([^\n}]*?)\n(.*?)\}', re.DOTALL)
    # (this pattern does not handle \code{...} with internal } AND \n!)
    filestr = pattern.sub(r'\\code{\g<1> \g<2>}', filestr)
    verb_command = 'Verb'  # requires fancyvrb package, otherwise use std 'verb'

    verb_delimiter = '!'
    alt_verb_delimiters = '?', '@', '|'  # can't use ~,%,#,$,^,&,* in latex headings
    cpattern = re.compile(r"""\\code\{(.*?)\}([ \n,.;:?!)"'-])""", re.DOTALL)
    # Check if the verbatim text contains verb_delimiter and make
    # special solutions for these first
    alt_verb_delimiter = None
    for verbatim, dummy in cpattern.findall(filestr):
        if verb_delimiter in verbatim:
            for delimiter in alt_verb_delimiters:
                if delimiter not in verbatim:
                    alt_verb_delimiter = delimiter
                    break
            if alt_verb_delimiter is None:
                alt_verb_delimiter = alt_verb_delimiters[0]
                print(r"""
*** warning: inline verbatim "%s"
    contains all delimiters %s that the LaTeX
    command \\Verb can make use of - be prepared for strange output that
    requires manual editing (or use doconce replace/subst) of
    \\Verb%s%s%s
    or move this line verbatim expression to a code block !bc ... !ec.
""" % (verbatim, [verb_delimiter] + list(alt_verb_delimiter),
       alt_verb_delimiter, verbatim, alt_verb_delimiter))
            # Here one can have a problem in that verbatim contains
            # special regex chars such as $, \, ., etc. Use re.escape
            pattern = re.escape(r'\code{%s}' % verbatim) + r"""([ \n,.;:?!)"'-])"""
            replacement = r'\\%s%s%s%s\g<1>' % \
            (verb_command, alt_verb_delimiter, verbatim, alt_verb_delimiter)
            # Note: A previous occurence in cpattern.findall may have performed
            # this substitution
            filestr = re.sub(pattern, replacement, filestr, flags=re.DOTALL)
    # Exceptional cases are dealt with, proceed with the standard case
    filestr = cpattern.sub(r'\\%s%s\g<1>%s\g<2>' %
                           (verb_command, verb_delimiter, verb_delimiter),
                           filestr)

    '''
    # If fontsize is part of the \Verb command (which is not wise, since
    # explicit fontsize is not suitable for section headings),
    # first handle combination of \protect and \code
    fontsize = 10          # should be configurable from the command line
    cpattern = re.compile(r"""\\protect\s*\\code\{(.*?)\}([ \n,.;:?!)"'-])""", re.DOTALL)
    filestr = cpattern.sub(r'{\\fontsize{%spt}{%spt}\protect\\%s!\g<1>!}\g<2>' %
                           (fontsize, fontsize, verb_command), filestr)
    # Handle ordinary \code
    cpattern = re.compile(r"""\\code\{(.*?)\}([ \n,.;:?!)"'-])""", re.DOTALL)
    filestr = cpattern.sub(r'{\\fontsize{%spt}{%spt}\\%s!\g<1>!}\g<2>' %
                           (fontsize, fontsize, verb_command), filestr)
    '''
    # \Verb!...! does not cause linebreak in latex, therefore shift to \texttt{}
    # where possible since this will reduce overfull hboxes
    filestr = re.sub(r'\\protect\s*\\Verb!([^{}_$\^#%&\\]+?)!',
                     r'\\texttt{\g<1>}', filestr)
    filestr = re.sub(r'\\Verb!([^{}_$\^#%&\\]+?)!',
                     r'\\texttt{\g<1>}', filestr)
    return filestr


def _usage_grab():
    print('Usage:\n'
          'doconce grab --from[-] from-text [--to[-] to-text] <file>  > <output-file>')


def grab():
    """
    Grab a portion of text from a file, starting with from-text
    (included if specified as --from, not included if specified
    via --from-) up to the first occurence of to-text (--to implies
    that the last line is included, --to_ excludes the last line).
    If --to[-] is not specified, all text up to the end of the file
    is returned.

    from-text and to-text are specified as regular expressions.
    """
    if len(sys.argv) < 4:
        _usage_grab()
        sys.exit(0)

    filename = sys.argv[-1]
    if not sys.argv[1].startswith('--from'):
        print('missing --from fromtext or --from_ fromtext option on the command line')
        _abort()
    from_included = sys.argv[1] == '--from'
    from_text = sys.argv[2]

    # Treat --to

    # impossible text (has newlines) that will never be found
    # is used as to-text if this is not specified
    impossible_text = '@\n\n@'
    try:
        to_included = sys.argv[3] == '--to'
        to_text = sys.argv[4]
    except IndexError:
        to_included = True
        to_text = impossible_text

    from_found = False
    to_found = False
    copy = False
    lines = []  # grabbed lines
    for line in open(filename, 'r'):
        m_from = re.search(from_text, line)
        m_to = re.search(to_text, line)
        if m_from and not from_found:
            copy = True
            from_found = True
            if from_included:
                lines.append(line)
        elif m_to:
            copy = False
            to_found = True
            if to_included:
                lines.append(line)
        elif copy:
            lines.append(line)
    if not from_found:
        print('Could not find match for from regex "%s"' % from_text)
        sys.exit(1)
    if not to_found and to_text != impossible_text:
        print('Could not find match for to   regex "%s"' % to_text)
        sys.exit(1)
    print(''.join(lines).rstrip())


def remove_text(filestr, from_text, from_included, to_text, to_included):
    """
    Remove a portion of text from the string filestr.
    See remove() for explanation of arguments.
    """
    impossible_text = '@\n\n@'  # must be compatible with remove()

    from_found = False
    to_found = False
    remove = False
    lines = []  # survived lines
    for line in filestr.splitlines():
        m_from = re.search(from_text, line)
        m_to = re.search(to_text, line)
        if m_from:
            remove = True
            from_found = True
            if not from_included:
                lines.append(line)
        elif m_to:
            remove = False
            to_found = True
            if not to_included:
                lines.append(line)
        elif not remove:
            lines.append(line)

    return '\n'.join(lines).rstrip() + '\n', from_found, to_found


def _usage_remove():
    print('Usage:\n'
          'doconce remove --from[-] from-text [--to[-] to-text] <file> > <output-file>')


def remove():
    """
    Remove a portion of text from a file, starting with from-text
    (included if specified as --from, not included if specified
    via --from-) up to the first occurence of to-text (--to implies
    that the last line is included, --to_ excludes the last line).
    If --to[-] is not specified, all text up to the end of the file
    is returned.

    from-text and to-text are specified as regular expressions.
    """
    if len(sys.argv) < 4:
        _usage_remove()
        sys.exit(0)

    filename = sys.argv[-1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()

    if not sys.argv[1].startswith('--from'):
        print('missing --from fromtext or --from_ fromtext option on the command line')
        sys.exit(1)
    from_included = sys.argv[1] == '--from'
    from_text = sys.argv[2]

    # Treat --to

    # impossible text (has newlines) that will never be found
    # is used as to-text if this is not specified
    impossible_text = '@\n\n@'
    try:
        to_included = sys.argv[3] == '--to'
        to_text = sys.argv[4]
    except IndexError:
        to_included = True
        to_text = impossible_text

    filestr, from_found, to_found = remove_text(
        filestr, from_text, from_included, to_text, to_included)

    if not from_found:
        print('Could not find match for from regex "%s"' % from_text)
        sys.exit(1)
    if not to_found and to_text != impossible_text:
        print('Could not find match for to   regex "%s"' % to_text)
        sys.exit(1)

    os.rename(filename, filename + '.old~~')
    f = open(filename, 'w')
    f.write(filestr)
    f.close()


def _usage_remove_exercise_answers():
    print('Usage:\n'
          'doconce remove_exercise_answers file_in_some_format')


def remove_exercise_answers():
    if len(sys.argv) < 2:
        _usage_remove_exercise_answers()
        sys.exit(0)

    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()

    envirs = ['solution of exercise', 'short answer in exercise']
    from_texts = [r'--- begin ' + envir for envir in envirs]
    to_texts = [r'--- end ' + envir for envir in envirs]
    for from_text, to_text in zip(from_texts, to_texts):
        filestr, from_found, to_found = remove_text(
            filestr, from_text, True, to_text, True)
    if from_found and to_found:
        pass
    else:
        print('no answers/solutions to exercises found in ' + filename)

    os.rename(filename, filename + '.old~~')
    f = open(filename, 'w')
    f.write(filestr)
    f.close()


def clean():
    return _clean(light=False)


def lightclean():
    return _clean(light=True)


def _clean(light):
    """
    Remove all DocOnce-generated files and the Trash dir if it exists.
    Place new removed files in Trash.

    For example, if ``d1.do.txt`` and ``d2.do.txt`` are found,
    all files ``d1.*`` and ``d1.*`` are deleted, except when ``*``
    is ``.do.txt`` or ``.sh``. The subdirectories ``sphinx-*``,
    ``sphinx_*``, ``html_images``, ``latex_figs``, and
    ``standalone_exercises`` are also removed,
    as well as all ``*~`` and ``tmp*`` files and all files made from
    splitting (split_html, split_rst).
    """
    if os.path.isdir('Trash'):
        print()
        shutil.rmtree('Trash')
        print('Removing Trash directory')
    removed = []

    trash_files = ['_doconce_debugging.log', '__tmp.do.txt', 'texput.log']
    # "secret" files (.trash$hash)
    trash_files += glob.glob('.trash[a-f0-9]*') + glob.glob('._.trash[a-f0-9]*')
    for trash_file in trash_files:
        if os.path.isfile(trash_file):
            removed.append(trash_file)

    doconce_files = glob.glob('*.do.txt')
    for dof in doconce_files:
        namestem = dof[:-7]
        generated_files = glob.glob(namestem + '.*')
        extensions_to_keep = ['.do.txt', '.sh', '.py', '*.pl']
        if light:
            extensions_to_keep += ['.pdf', '.html', '.txt', '.gwiki', '.mwiki', '.cwiki', '.ipynb', '.m']
        for ext in extensions_to_keep:
            filename = namestem + ext
            if os.path.isfile(filename):
                if filename in generated_files:
                    generated_files.remove(filename)
        for f in generated_files:
            removed.append(f)
        if not light:
            ipynb_tarfile = 'ipynb-%s-src.tar.gz' % namestem
            if os.path.isfile(ipynb_tarfile):
                removed.append(ipynb_tarfile)

    removed.extend(
        glob.glob('*~') + glob.glob('.*~') + glob.glob('tmp*') +
        glob.glob('.*.exerinfo') +
        glob.glob('.*.quiz*') +
        glob.glob('.*_html_file_collection') +
        glob.glob('.*.copyright') +
        glob.glob('automake_sphinx.*')
        )
    if not light:
        removed.extend(
            glob.glob(_part_filename_wildcard + '.html') +
            glob.glob(_part_filename_wildcard + '.rst')
            )

    directories = ['html_images', 'latex_figs', 'standalone_exercises']
    directories += glob.glob('_minted-*')
    if not light:
        directories += glob.glob('sphinx-*') + glob.glob('sphinx_*')

    for d in directories:
        if os.path.isdir(d):
            removed.append(d)

    if removed:
        print('Remove: ' + ' '.join(removed) + ' (-> Trash)')
        os.mkdir('Trash')
        for f in removed:
            try:
                shutil.move(f, 'Trash')
            except shutil.Error as e:
                if 'already exists' in str(e):
                    pass
                else:
                    print('Move problems with %s %s' % (f, e))
            if os.path.isdir(f):
                shutil.rmtree(f)


def _usage_guess_encoding():
    print('Usage:\n'
          'doconce guess_encoding filename')


def _encoding_guesser(filename, verbose=False):
    """Try to guess the encoding of a file."""
    if not os.path.isfile(filename):
        print('*** error: file %s does not exist' % filename)
        _abort()
    encodings = ['ascii', 'us-ascii', 'iso-8859-1', 'iso-8859-2',
                 'iso-8859-3', 'iso-8859-4', 'cp37', 'cp930', 'cp1047',
                 'utf-8', 'utf-16', 'windows-1250', 'windows-1252',]
    for encoding in encodings:
        try:
            if verbose:
                print('Trying encoding ' + encoding + " with open(filename, 'r', encoding="+encoding+')')
            f = open(filename, 'r', encoding=encoding)
            f.read()
            f.close()
        except Exception as e:
            if verbose:
                print('failed: %s' % e)
        else:
            break
    return encoding


def guess_encoding():
    if len(sys.argv) != 2:
        _usage_guess_encoding()
        sys.exit(0)
    filename = sys.argv[1]
    print(_encoding_guesser(filename, verbose=False))


def _usage_change_encoding():
    print('Usage:\n'
          'doconce change_encoding from-encoding to-encoding <file1> <file2> ...\n\n'
          'Example:\n'
          'doconce change_encoding utf-8 latin1 myfile.do.txt')


def _change_encoding_unix(filename, from_enc, to_enc):
    backupfile = filename + '.old~~'
    if sys.platform.startswith('linux'):
        cmd = 'iconv -f %s -t %s %s --output %s' % \
              (from_enc, to_enc, backupfile, filename)
    elif sys.platform == 'darwin':
        cmd = 'iconv -f %s -t %s %s > %s' % \
              (from_enc, to_enc, backupfile, filename)
    else:
        print('changing encoding is not implemented on Windows machines')
        _abort()
    os.rename(filename, backupfile)
    failure = system(cmd, abort_on_failure=False)
    if failure:
        # Restore file
        shutil.copy(backupfile, filename)
        os.remove(backupfile)


def _change_encoding_python(filename, from_enc, to_enc):
    f = codecs.open(filename, 'r', from_enc)
    text = f.read()
    f.close()
    f = codecs.open(filename, 'w', to_enc)
    f.write(text)
    f.close()


def change_encoding():
    if len(sys.argv) < 4:
        _usage_change_encoding()
        sys.exit(0)

    from_encoding = sys.argv[1]
    to_encoding = sys.argv[2]
    filenames = wildcard_notation(sys.argv[3:])
    for filename in filenames:
        _change_encoding_unix(filename, from_encoding, to_encoding)
        # Perhaps better alternative with pure Python:
        #_change_encoding_python(filename, from_encoding, to_encoding)


def html_imagefile(imagename):
    filename = os.path.join(html_images[:-4], imagename + '.png')
    return filename


def copy_datafiles(datafile):
    """
    Get a doconce datafile, ``files.zip`` or ``files.tar.gz``, to
    the current directory and pack it out unless the subdirectory
    ``files`` (with all the files) already exists.
    """
    if datafile.endswith('.zip'):
        subdir = datafile[:-4]
        import zipfile
        uncompressor = zipfile.ZipFile
    elif datafile.endswith('.tar.gz'):
        subdir = datafile[:-7]
        import tarfile
        uncompressor = tarfile.TarFile
    if not os.path.isdir(subdir):
        from . import doconce
        doconce_dir = os.path.dirname(doconce.__file__)
        doconce_datafile = os.path.join(doconce_dir, datafile)
        shutil.copy(doconce_datafile, os.curdir)
        uncompressor(datafile).extractall()
        print('made subdirectory ' + subdir)
        os.remove(datafile)
        return True
    else:
        return False


def _usage_html_colorbullets():
    print('Usage:\n'
          'doconce html_colorbullets <file>[.html]')


def html_colorbullets():
    # A much better implementation, avoiding tables, is given
    # here: https://www.eng.buffalo.edu/webguide/Bullet_Lists.html
    """
    Replace unordered lists by a table, in order to replace
    ``<li>`` tags (and the default bullets) by
    images of balls with colors.
    """
    if len(sys.argv) <= 1:
        _usage_html_colorbullets()
        sys.exit(0)

    red_bullet = 'bullet_red2.png'
    green_bullet = 'bullet_green2.png'
    #red_bullet = 'bullet_red1.png'
    #green_bullet = 'bullet_green1.png'

    filenames = sys.argv[1:]
    for filename in filenames:
        f = open(filename, 'r')
        text = f.read()
        f.close()
        #if '<li>' in text:
        #    copy_datafiles(html_images)  # copy html_images subdir if needed
        lines = text.splitlines()
        f = open(filename, 'w')
        level = 0
        for line in lines:
            linel = line.lower()
            if '<ul>' in linel:
                level += 1
                line = '<p><table border="0">\n'
            if '</ul>' in linel:
                line = '</td></tr></table>\n'
                level -= 1
            if '<li>' in linel:
                line = line.replace('<li>', """</tr><p><tr><td valign='top'><img src="BULLET"></td><td>""")
                if level == 1:
                    #image_filename = html_imagefile(red_bullet)
                    image_filename = 'https://hplgit.github.io/doconce/bundled/html_images/' + red_bullet
                elif level >= 2:
                    #image_filename = html_imagefile(green_bullet)
                    image_filename = 'https://hplgit.github.io/doconce/bundled/html_images/' + green_bullet
                line = line.replace('BULLET', image_filename)
            f.write(line + '\n')
        f.close()


def _usage_split_html():
    print('Usage:\n'
          'doconce split_html <file>[.html] --method=... --nav_button=name --pagination \\\n'
          '--reference="acknowledgment/author" --font_size=slides --copyright=everypage|titlepage\n'
          '\n'
          'Options:\n'
          '--method=(split | space8 | hrule | colorline) specifies pagebreak, physical split with a new page \n'
          '(--method=split) or just N blank lines (--method=spaceN) or a horizontal rule (--method=hrule) with\n'
          'blank lines above and below, or a colored line (--method=colorline). Default is --method=split.\n'
          '\n'
          '--nav_button=name sets the type of navigation button (next, previous): text, gray1 (default), gray2, \n'
          'bigblue, blue, green. See (https://raw.github.com/hplgit/doconce/master/doc/src/manual/fig/nav_buttons.png\n'
          'for examples on these types (from left to right). A value like -nav_button=gray2,top gives buttons only at \n'
          'the top of the page, gray2,top+bottom gives buttons at the top and bottom (default), while gray2,bottom \n'
          'gives buttons only at the bottom.\n'
          'If the "doconce format html" command used bootstrap styles (with --html_style=bootstrap*|bootswatch*), \n'
          'set just --nav_button=top or bottom (default) or top+bottom.\n'
          '\n'
          '--pagination means that one can click on pages at the button if a bootstrap theme is used in the document.\n'
          '\n'
          '--font_size= is used to increase the font size for slides.\n'
          '--font_size=slides gives 140% font size in the body text.\n'
          '--font_size=180 gives 180% font size in the body text.\n'
          '\n'
          '--reference=... is used to insert a reference for acknowledging where the source of the text is published, \n'
          'typically the reference of a book if the document is the HTML version of a chapter in the book. The \n'
          'reference appears at the top of every page in small font.\n'
          '\n'
          'Example:\n'
          '--reference="This text is taken from Appendix H.2 in the book <em>A Primer on Scientific Programming \n'
          'with Python</em> by H. P. Langtangen, 4th edition, Springer, 2014."\n'
          '\n'
          '--copyright=everypage gives a copyright notice in the footer of every page (if {copyright...} is specified\n'
          'as part of AUTHOR commands). With --copyright=titlepage (default), the copyright only appears on the title\n'
          'page only.'
          )


def split_html():
    """
    Split html file into parts. Use !split command as separator between
    parts.
    """
    if len(sys.argv) <= 1:
        _usage_split_html()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.html'):
        basename = filename
        filename += '.html'
    else:
        basename = filename[:-5]

    method = misc_option('method=', 'split')

    # Note: can only do tablify and support slidecell specifications
    # if --method=split (tablify requires the file split into parts)

    if method != 'split':
        # Load text
        f = open(filename, 'r')
        filestr = f.read()
        f.close()

    if method.startswith('space'):
        if len(method) > len('space'):
            num_lines = int(method[5:])
        else:
            num_lines = 8
        filestr = filestr.replace(
            '<!-- !split -->',
            '<!-- !split -->' + '<br>'*num_lines)
    elif method in ('hr', 'hrule'):
        filestr = filestr.replace(
            '<!-- !split -->',
            '<!-- !split -->' + '<br><br><br><hr><br><br><br>')
    elif method in ('colorline',):
        filestr = filestr.replace(
            '<!-- !split -->',
            '<!-- !split -->' + '<br><br><br><br><br><br><img src="%s"><br><br>'
            % 'https://hplgit.github.io/doconce/bundled/html_images/colorline.png')
    else:
        header, parts, footer = get_header_parts_footer(filename, "html")
        parts = tablify(parts, "html")

        files = doconce_split_html(header, parts, footer, basename, filename)
        print('%s now links to the generated files' % filename)
        print(', '.join(files))

    if method != 'split':
        # Remove notes
        filestr = re.sub(r'^<!-- !bnotes.+?^<!-- !enotes -->', '',
                         filestr, flags=re.MULTILINE|re.DOTALL)
        '''
        # Fix font size for solarized *slides* - won't do this so it affects
        # all kind of documents. And if method != 'split', we have one
        # file and can crank up the font in the browser once and for all.
        if re.search(r"""<link href=["']http.+?solarized.*?\.css""", filestr):
            filestr = filestr.replace(r'<style type="text/css">',
                                      ("<style type=\"text/css\">\n"
                                       "body, td {font-size: 140%;}\n"
                                       "h1 {font-size: 200%;}\n"
                                       "h2 {font-size: 180%;}"))
        '''

        f = open(filename, 'w')
        f.write(filestr)
        f.close()

        if '<!-- !bslidecell' in filestr:
            print('*** warning: !bslidecell-!eslidecell constructions are')
            print('    ignored unless --method=split is specified')
            print('    (--method=spaceX|hr|hrule|colorline all ignores cells)')


def tablify(parts, format="html"):
    """
    Detect !bslidecell XY and !eslidecell environments and typeset
    elements of a part (slide page) as a table.
    """
    begin_comment, end_comment = _format_comments(format)
    for i in range(len(parts)):
        part = ''.join(parts[i])

        if '%s !bslidecell' % begin_comment in part:
            pattern = r'%s !bslidecell +(\d\d) *([.0-9 ]*?)%s\s+(.+?)%s !eslidecell *%s' % (begin_comment, end_comment, begin_comment, end_comment)
            pattern00 = r'%s !bslidecell +00 *[.0-9 ]*?%s\s+(.+?)%s !eslidecell *%s' % (begin_comment, end_comment, begin_comment, end_comment)
            cpattern = re.compile(pattern, re.DOTALL)
            cells = cpattern.findall(part)
            data = []
            row_max = 0
            col_max = 0
            for pos, width, entry in cells:
                try:
                    width = float(width)
                except:
                    width = None

                ypos = int(pos[0])
                xpos = int(pos[1])
                if ypos > row_max:
                    row_max += 1
                if xpos > col_max:
                    col_max += 1
                data.append([(ypos, xpos), entry, width])
            table = [[None]*(col_max+1) for j in range(row_max+1)]
            for r in range(len(table)):
                for s in range(len(table[r])):
                    table[r][s] = ['', None]
            for pos, body, width in data:
                table[pos[0]][pos[1]] = [body, width]
            # Check consistency of widths
            for r, row in enumerate(table):
                widths = []
                has_width = False
                for column, width in row:
                    if width is not None:
                        has_width = True
                        widths.append(width)
                if has_width:
                    if len(row) != len(widths):
                        # Can accept if only two columns
                        if len(row) == 2 and len(widths) == 1:
                            # Find the missing one
                            if table[r][0][1] is None:
                                table[r][0][1] = 1 - widths[0]
                            elif table[r][1][1] is None:
                                table[r][1][1] = 1 - widths[0]
                        else:
                            print('*** error: must specify width of all columns in slidecell table!')
                            print('   ', end=' ')
                            for s, c in enumerate(row):
                                column, width = c
                                print(' %d%d: ' % (r, s), end=' ')
                                if width is not None:
                                    print('no width')
                                else:
                                    print('%g' % width)
                            _abort()
                else:
                    width = old_div(1.,len(row))
                    for s, c in enumerate(row):
                        table[r][s][1] = width

            if format == 'html':
                # typeset table in html
                tbl = '\n<table border="0">\n'
                for row in table:
                    tbl += '<tr>\n'
                    for column, width in row:
                        tbl += '<td class="padding">\n%s</td>\n' % (column)
                        # This is an attempt to control the width of columns,
                        # but it does not work well.
                        #tbl += '<td class="padding"><div style="width: %d%%"> %s </div></td>\n' % (int(100*width), column)

                    tbl += '</tr>\n'
                tbl += '</table>\n'

                # Put the whole table where cell 00 was defined
                cpattern00 = re.compile(pattern00, re.DOTALL)
                #part = cpattern00.sub(tbl, part)  # does not preserve math \
                part = cpattern00.sub('XXXYYY@#$', part)  # some ID and then replace
                part = part.replace('XXXYYY@#$', tbl) # since replace handles \
                # Let the other cells be empty
                part = cpattern.sub('', part)
                part = [line + '\n' for line in part.splitlines()]
                parts[i] = part
            elif format.endswith('latex'):
                # typeset table in beamer latex
                tbl = ''
                for row in table:
                    tbl += r'\begin{columns}' + '\n'
                    for column, width in row:
                        if width is None:
                            raise ValueError('Bug: width is None')
                        tbl += r'\column{%g\textwidth}' % width + \
                               '\n%s\n' % column

                    tbl += r'\end{columns}' + '\n'
                tbl += '\n'

                # Put the whole table where cell 00 was defined
                cpattern00 = re.compile(pattern00, re.DOTALL)
                #part = cpattern00.sub(tbl, part)  # does not preserve math \
                part = cpattern00.sub('XXXYYY@#$', part)  # some ID and then replace
                part = part.replace('XXXYYY@#$', tbl) # since replace handles \
                # Let the other cells be empty
                part = cpattern.sub('', part)
                part = [line + '\n' for line in part.splitlines()]
                parts[i] = part
    return parts


def _format_comments(format='html'):
    if format == 'html':
        return '<!--', '-->'
    elif format == 'latex':
        return '%', ''
    elif format == 'rst' or format == 'sphinx':
        return '..', ''
    else:
        return None, None


def get_header_parts_footer(filename, format='html'):
    """Split files in different file formats

    Return list of lines for header, parts split by !split, and footer.
    This function relies on markers such as "main content",
    "end of main content", "!split"
    :param str filename: text string
    :param str format: default 'html'
    :return: header, parts, footer
    :rtype: list(str, list[str], str)
    """
    header = []
    footer = []
    parts = [[]]
    if format in ('latex', 'pdflatex', 'html'):
        loc = 'header'
    else:
        loc = 'body'  # no header
    begin_comment, end_comment = _format_comments(format)
    f = open(filename, 'r')
    for line in f:
        if re.search(r'^%s %s+ main content %s+ ?%s' %
                     (begin_comment, globals.main_content_char,
                      globals.main_content_char, end_comment), line):
            loc = 'body'
        if re.search(r'^%s !split.*?%s' % (begin_comment, end_comment), line):
            parts.append([])
        if re.search(r'^%s %s+ end of main content %s+ ?%s' %
                     (begin_comment, globals.main_content_char,
                      globals.main_content_char, end_comment), line):
            loc = 'footer'
        if loc == 'header':
            header.append(line)
        elif loc == 'body':
            parts[-1].append(line)
        elif loc == 'footer':
            footer.append(line)
    f.close()
    return header, parts, footer


def doconce_split_html(header, parts, footer, basename, filename, slides=False):
    """Native doconce style splitting of HTML file into parts."""
    html_copyright_placement = misc_option('copyright', 'titlepage')
    if html_copyright_placement == 'titlepages':
        html_copyright_placement = 'titlepage'

    from . import html
    header_str = '\n'.join(header)

    bootstrap = '<!-- Bootstrap style: ' in header_str or \
                bool(re.search(r'<link .*href=.+?boots(trap|watch).*\.css', header_str))

    if bootstrap:
        local_navigation_pics = False    # navigation is in the template

        def bootstrap_navigation(pn, prev_part_filename, next_part_filename):
            text = '<!-- navigation buttons at the bottom of the page -->'
            if '--pagination' in sys.argv:
                # Use Bootstrap pagination
                text += '\n<ul class="pagination">\n'
                if pn > 0:
                    text += '<li><a href="%s">&laquo;</a></li>\n' % prev_part_filename
                max_pagination_pages = 16
                #max_pagination_pages = 4 # for debugging
                if len(parts) <= old_div(max_pagination_pages,2):
                    # Show all pages
                    for i in range(len(parts)):
                        if i == pn:
                           text += '  <li class="active"><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                        else:
                           text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                else:
                    # Show first, last, and pages around the current one
                    if pn >= old_div(max_pagination_pages,2) + 2:
                        i = 0
                        text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                        text += '  <li><a href="">...</a></li>\n'
                    start = max(0, pn-(old_div(max_pagination_pages,2)))
                    stop = min(len(parts), pn+old_div(max_pagination_pages,2)+2)
                    if start == 1:
                        # Special case, add page 1
                        text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, 0) + '.html', 0+1)
                    for i in range(start, stop):
                        if i == pn:
                           text += '  <li class="active"><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                        else:
                           text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                    if pn <= (len(parts) - (old_div(max_pagination_pages,2) + 3)):
                        text += '  <li><a href="">...</a></li>\n'
                        i = len(parts)-1
                        text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)

                if pn < len(parts)-1:
                    text += '  <li><a href="%s">&raquo;</a></li>\n' % next_part_filename
                text += '</ul>\n'
            else:
                # Use plain next and prev buttons with arrows, but
                # Bootstrap style
                text += '\n<ul class="pager">\n'
                if pn > 0:
                    text += (r'  <li class="previous">'
                             '\n'
                             r'    <a href="%s">&larr; Prev</a>'
                             '\n'
                             '  </li>\n') % prev_part_filename
                if pn < len(parts)-1:
                    text += (r'  <li class="next">'
                             '\n'
                             r'    <a href="%s">Next &rarr;</a>'
                             '\n'
                             '  </li>\n') % next_part_filename
                text += '</ul>\n'
            return text
    else:
        local_navigation_pics = False    # avoid copying images to subdir...

    nav_button = 'gray1'
    for arg in sys.argv:
        if arg.startswith('--nav_button='):
            nav_button = arg.split('=')[1]
            break
    if bootstrap:
        nav_button_pos = 'bottom'
        if nav_button in ('top', 'top+bottom'):
            nav_button_pos = nav_button
    else:
        nav_button_pos = 'top+bottom'
        if ',' in nav_button:
            nav_button, nav_button_pos = nav_button.split(',')
        # Values after comma: top, bottom, top+bottom

    # Map nav_button name to actual image file in bundled/html_images
    prev_button = next_button = ''
    if nav_button == 'gray1':
        prev_button = 'prev1'
        next_button = 'next1'
    elif nav_button == 'gray2':
        prev_button = 'prev2'
        next_button = 'next2'
    elif nav_button == 'bigblue':
        prev_button = 'prev3'
        next_button = 'next3'
    elif nav_button == 'blue':
        prev_button = 'prev4'
        next_button = 'next4'
    elif nav_button == 'green':
        prev_button = 'Knob_Left'
        next_button = 'Knob_Forward'
    elif nav_button in ('text', 'top', 'bottom', 'top+bottom'):
        pass
    else:
        print('*** warning: --nav_button=%s is illegal value, text,top+bottom is used' % nav_button)
        nav_button == 'text'
        nav_button_pos = 'top+bottom'

    header_part_line = ''  # 'colorline'
    if local_navigation_pics:
        copy_datafiles(html_images)  # copy html_images subdir if needed
        if prev_button:
            prev_button_filename = html_imagefile(prev_button)
            next_button_filename = html_imagefile(next_button)
            html.add_to_file_collection(prev_button_filename, filename, 'a')
            html.add_to_file_collection(next_button_filename, filename, 'a')
    else:
        if prev_button:
            prev_button_filename = 'https://hplgit.github.io/doconce/bundled/html_images/%s.png' % prev_button
            next_button_filename = 'https://hplgit.github.io/doconce/bundled/html_images/%s.png' % next_button


    # Fix internal links to point to the right splitted file
    name_pattern = r' id="([^"]+?)"[ >]'
    parts_name = [re.findall(name_pattern, ''.join(part)) for part in parts]
    parts_name.append(re.findall(name_pattern, ''.join(header)))
    parts_name.append(re.findall(name_pattern, ''.join(footer)))
    href_pattern = r'<a href="#([^"]+?)"'
    parts_href = [re.findall(href_pattern, ''.join(part)) for part in parts]
    parts_href.append(re.findall(href_pattern, ''.join(header)))
    parts_href.append(re.findall(href_pattern, ''.join(footer)))

    # id="..." can also define anchors (e.g., in bootstrap styles)
    id_pattern = r' id="([^"]+?)"'
    all_ids = [re.findall(id_pattern, ''.join(part)) for part in parts] + \
              [re.findall(id_pattern, ''.join(header)),
               re.findall(id_pattern, ''.join(footer))]
    # Flatten
    ids = []
    for sublist in all_ids:
        for id in sublist:
            ids.append(id)

    parts_name2part = {}   # map a name to where it is defined
    for i in range(len(parts_name)):
        for name in parts_name[i]:
            parts_name2part[name] = i

    import pprint
    # Substitute hrefs in each part, plus header and footer
    for i in range(len(parts_href)):
        for name in parts_href[i]:
            n = parts_name2part.get(name, None) #part where this name is defined
            if n is None and name not in ids:
                print('*** error: <a href="#%s" has no corresponding anchor (<a name= or some id=)' % name)
                print('    Reasons: 1) wrong reference, 2) no BIBFILE, 2) bug in DocOnce.')
                _abort()
                continue  # go to next if abort is turned off
            if n is not None and n != i:
                # Reference to label in another part, except the header
                # and footer (which is included in all parts)
                name_def_filename = _part_filename % (basename, n) + '.html'
                if i < len(parts):
                    part = parts[i]
                elif i == len(parts):
                    part = header
                elif i == len(parts)+1:
                    part = footer
                text = ''.join(part).replace(
                    '<a href="#%s"' % name,
                    '<a href="%s#%s"' % (name_def_filename, name))
                # Side effect: will substitute in header and footer
                # when it should not. This is fixed when the whole
                # file is constructed.
                if i < len(parts):
                    parts[i] = text.splitlines(True)
                elif i == len(parts):
                    header = text.splitlines(True)
                elif i == len(parts)+1:
                    footer = text.splitlines(True)

    # Treat \eqref and labels: MathJax does not support references
    # to eq. labels in other files.
    # Also, skip equation references to external documents.
    label_pattern = r'\\label\{(.+?)\}'  # label in latex equations
    parts_label = [re.findall(label_pattern, ''.join(part)) for part in parts]
    eqref_pattern = r'\\eqref\{(.+?)\}'
    ref_pattern = r'ref(ch)?\[([^\]]*?)\]\[([^\]]*?)\]\[([^\]]*?)\]'
    parts_eqref = [re.findall(eqref_pattern,
                              re.sub(ref_pattern, '', ''.join(part)))
                   for part in parts]

    parts_label2part = {}   # map an eq. label to where it is defined
    for i in range(len(parts_label)):
        for label in parts_label[i]:
            parts_label2part[label] = i
    # Check if there are eqrefs to undefined labels
    if misc_option('labelcheck=', 'off') == 'on':
        undefined_labels = []
        for i in range(len(parts_eqref)):
            for label in parts_eqref[i]:
                if label not in parts_label2part:
                    undefined_labels.append(label)
        if undefined_labels:
            for label in undefined_labels:
                print('*** error: equation ref (ref{%s}) but no label{%s}' % (label, label))
            print('*** error: found references to undefined equation labels')
            print('    (use generalized references ref[][][] if labels are')
            print('    defined outside this doconce document)')
            _abort()
    # Substitute eqrefs in each part.
    # MathJax cannot refer to labels in other HTML files.
    # We generate tag number for each label, in the right numbering
    # and use tags to refer to equations.
    # Info on https://stackoverflow.com/questions/16339000/how-to-refer-to-an-equation-in-a-different-page-with-mathjax
    # Tags are numbered globally, but chapter by chapter if book
    labels = []  # Hold all new tag labels in a list (not list of list as parts_label)
    for part_labels in parts_label:
        labels += part_labels
    label2tag = {}
    i = 0  # tag counter within a chapter
    ch = 0 # chapter number
    has_chapters = False
    for part in parts:
        for line in part:
            if '<!-- chapter heading' in line:  # encountered new chapter?
                if not 'Preface' in line:
                    ch += 1
                    i = 0  # restart numbering
                    has_chapters = True
            if 'label{' in line:
                m = re.search(r'\\label\{(.+?)\}', line)
                if m:
                    label = m.group(1)
                    if label in labels:
                        # This is an equation label
                        i += 1
                        if has_chapters:
                            label2tag[label] = '%d.%d' % (ch, i)
                        else:
                            label2tag[label] = '%d' % i
    # Go from AMS to non equationNumering in MathJax since we do not
    # want any equation without label to have numbers (instead we
    # control all numbers here by inserting \tag)
    for i in range(len(header)):
        if 'autoNumber: "AMS"' in header[i]:
            header[i] = header[i].replace('autoNumber: "AMS"', 'autoNumber: "none"')
            break
    # Insert tags in each part
    for i in range(len(parts)):
        text = ''.join(parts[i])
        if r'\label{' in text:
            labels = re.findall(label_pattern, text)
            for label in labels:
                text = text.replace(
                    r'\label{%s}' % label,
                    r'\tag{%s}' % (label2tag[label]))
        parts[i] = text.splitlines(True)
    # Substitute all \eqrefs (can only have tags, not labels for
    # right navigation to an equation)
    for i in range(len(parts_eqref)):
        for label in parts_eqref[i]:
            if not label in parts_label2part:
                continue
            n = parts_label2part[label]   # part where this label is defined
            if i < len(parts):
                part = parts[i]
                text = ''.join(part)
                if n != i:
                    # Reference to equation with label in another file
                    label_def_filename = _part_filename % (basename, n) + '.html'
                    text = text.replace(
                        r'\eqref{%s}' % label,
                        '<a href="%s#mjx-eqn-%s">(%s)</a>' %
                        (label_def_filename, label2tag[label], label2tag[label]))
                else:
                    text = text.replace(
                        r'\eqref{%s}' % label,
                        '<a href="#mjx-eqn-%s">(%s)</a>' %
                        (label2tag[label], label2tag[label]))
                if i < len(parts):
                    parts[i] = text.splitlines(True)

    generated_files = []
    for pn, part in enumerate(parts):
        header_copy = header[:]
        if bootstrap:
            # Highligh first section in this part in the navigation in header
            m = re.search(r'<h(1|2|3).*?>(.+?)<', ''.join(part))
            if m:
                first_header = m.group(2).strip()
                for k in range(len(header_copy)):
                    if 'navigation toc:' in header[k]:
                        m2 = re.search(r'<li><a href="(.+?)">', header[k])
                        if m2:
                           if m2.group(1) == first_header:
                               header_copy[k] = header[k].replace(
                                   '<li>', '<li class="active">')
                        else:
                            print('*** error: doconce bug: wrong syntax in navigation toc for bootstrap styles')
                            _abort()

        lines = header_copy[:]
        lines.append('<a name="part%04d"></a>\n' % pn)

        # Decoration line?
        if header_part_line and not bootstrap:
            if local_navigation_pics:
                header_part_line_filename = html_imagefile(header_part_line)
            else:
                header_part_line_filename = 'https://hplgit.github.io/doconce/bundled/html_images/%s.png' % header_part_line
            lines.append(('\n'
                          r'<p><br><img src="%s"><p><br><p>\n') %
                         header_part_line_filename)

        part_filename = _part_filename % (basename, pn) + '.html'
        prev_part_filename = _part_filename % (basename, pn-1) + '.html'
        next_part_filename = _part_filename % (basename, pn+1) + '.html'
        generated_files.append(part_filename)

        if bootstrap:
            # Make navigation arrows
            prev_ = next_ = ''
            buttons = bootstrap_navigation(pn, prev_part_filename, next_part_filename)
            # Add jumbotron button reference on first page
            if pn == 0:
                for i in range(len(part)):
                    if part[i].startswith('<!-- potential-jumbotron-button -->'):
                        part[i] = part[i].replace(
                              '<!-- potential-jumbotron-button -->',
                              '\n\n<p><a href="%s" class="btn btn-primary btn-lg">Read &raquo;</a></p>\n\n' %
                              next_part_filename)
                        break
            if 'top' in nav_button_pos:
                lines += buttons.splitlines(True)

        elif 'top' in nav_button_pos:
            # Simple navigation buttons at the top and bottom of the page
            # (only at bottom if the function argument slides is True)
            if not slides:
                lines.append('<p>\n<!-- begin top navigation -->\n') # for easy removal
                # Need a table for navigation pics, otherwise they cannot
                # be on the same line
                lines.append('<table style="width: 100%"><tr><td>\n')
                if pn > 0:
                    if nav_button == 'text':
                        lines.append(r'<div style="text-align: left;"><a href="%s">&laquo; Previous</a></div>'
                                     '\n' % (prev_part_filename))
                    else:
                        lines.append(r'<div style="text-align: left;"><a href="%s">'
                                     r'<img src="%s" border=0 alt="&laquo; Previous"></a></div>' %
                                     (prev_part_filename, prev_button_filename))
                lines.append('</td><td>\n')
                if pn < len(parts)-1:
                    if nav_button == 'text':
                        lines.append(r'<div style="text-align: right;">'
                                     r'<a href="%s">Next &raquo;</a></div>' %
                                     (next_part_filename))
                    else:
                        lines.append(r'<div style="text-align: right;">'
                                     r'<a href="%s"><img src="%s" border=0 alt="Next &raquo;"></a></div>' %
                                     (next_part_filename, next_button_filename))
                lines.append('</td></tr></table>\n')
                lines.append('<!-- end top navigation -->\n</p>\n\n')
                lines.append('<p>\n')


        # Main body of text
        lines += part

        if html_copyright_placement == 'titlepage' and pn > 0:
            # Remove the copyright from the footer
            for i in range(len(footer)):
                if '<!-- copyright -->' in footer[i]:
                    footer[i] = re.sub(r'<!-- copyright --> .+', '<!-- copyright only on the titlepage -->', footer[i])

        # Navigation in the bottom of the page
        lines.append('<p>\n')
        if bootstrap:
            if 'bottom' in nav_button_pos:
                lines += buttons.splitlines(True)
            lines += footer
        elif 'bottom' in nav_button_pos:
            lines.append('<!-- begin bottom navigation -->\n')
            lines.append('<table style="width: 100%"><tr><td>\n')
            if pn > 0:
                if nav_button == 'text':
                    lines.append((r'<div style="text-align: left;"><a href="%s">&laquo; Previous</a></div>'
                                  r'\n') % (prev_part_filename))
                else:
                    lines.append(
                        (r'<div style="text-align: left;"><a href="%s"><img src="%s" border=0 '
                         r'alt="&laquo; Previous"></a></div>'
                         '\n') % (prev_part_filename, prev_button_filename))
            lines.append('</td><td>\n')
            if pn < len(parts)-1:
                if nav_button == 'text':
                    lines.append((r'<div style="text-align: right;"><a href="%s">Next &raquo;</a></div>'
                                 '\n') % (next_part_filename))
                else:
                    lines.append(
                        (r'<div style="text-align: right;"><a href="%s"><img src="%s" border=0 '
                         r'alt="Next &raquo;"></a></div>'
                         '\n') % (next_part_filename, next_button_filename))
            lines.append('</td></tr></table>\n')
            lines.append('<!-- end bottom navigation -->\n</p>\n\n')
            lines += footer

        html.add_to_file_collection(part_filename, filename, 'a')

        part_text = ''.join(lines)
        # Remove references with this file as prefix in href
        # (some Bootstrap functionality does not work without this fix,
        # and in general we should strip local references anyway)
        part_text = part_text.replace('<a href="%s#' % part_filename,
                                      '<a href="#')

        # Insert reference to published version of document?
        ackn = misc_option('reference=', None)
        if ackn is not None:
            ackn1 = '<p style="font-size:80%%">%s</p>' % ackn
            ackn2 = '<div style="font-size:80%%">%s</div>' % ackn
            ackn3 = '<center style="font-size:80%%">%s</center>' % ackn
            if pn >= 1:
                # Place the acknowledgment/reference at the top, right after
                # the (only) !split command in each file
                part_text = part_text.replace(
                    '<!-- !split -->', '<!-- !split -->\n%s' % ackn1)
            elif pn == 0:
                # Include in front page if jumbotron button
                pattern = r'<p><a href=".+?" class="btn btn-primary btn-lg">Read &raquo;</a></p>'
                m = re.search(pattern, part_text)
                if m:  # jumbotron button?
                    button = m.group()
                    part_text = part_text.replace(
                        button, '\n<p>' + ackn2 + '</p>\n' + button)
                else:
                    # Put text after navigation
                    part_text = part_text.replace(
                        '<!-- end bottom navigation -->\n</p>\n',
                        '<!-- end bottom navigation -->\n</p>%s\n' % ackn1)

        # Remove notes
        part_text = re.sub(r'^<!-- !bnotes.+?^<!-- !enotes -->', '',
                           part_text, flags=re.MULTILINE|re.DOTALL)
        # Fix font size for *slides*
        font_size = misc_option('font_size=', 'standard')
        if font_size == 'slides' or font_size.isdigit():
            if font_size.isdigit():
                font_size = int(font_size)
            else:
                font_size = 140
            part_text = part_text.replace(r'<style type="text/css">',
                                          ('<style type="text/css">\n'
                                           'body, td {font-size: %d%%;}\n'
                                           'h1 {font-size: 200%%;}\n'
                                           'h2 {font-size: 180%%;}\n') % (font_size))

        # Write part to ._*.html file
        f = open(part_filename, 'w')
        f.write(part_text)
        f.close()

        # Make sure main html file equals the first part
        if pn == 0:
            shutil.copy(part_filename, filename)
    return generated_files


def _usage_split_rst0():
    print('Usage:\n'
          'doconce split_rst complete_file.rst')


def split_rst0():
    """
    Split a large .rst file into smaller files corresponding
    to each main section (7= in headings).

    The large complete doconce file typically looks like this::

        #>>>>>>> part: header >>>>>
        # #include "header.do.txt"

        #>>>>>>> part: fundamentals >>>>>
        # #include "fundamentals.do.txt"

        #>>>>>>> part: nonlinear >>>>>
        # #include "nonlinear.do.txt"

        #>>>>>>> part: timedep >>>>>
        # #include "timedep.do.txt"

    Note that the comment lines ``#>>>...`` *must* appear right above
    the include directives. The includes are replaced by text, while
    the ``#>>>...`` are still left as markers in the complete document
    for the various sections. These markers are used to split the
    text into parts. For Sphinx to treat section headings right,
    each part should start with a main section (7=).

    The ``split_rst`` command will in this example take the complete
    ``.rst`` file and make files ``header.rst``, ``fundamentals.rst``,
    ``nonlinear.rst``, etc.  The ``doconce sphinx_dir`` command takes
    all these ``.rst`` files as arguments and creates the
    corresponding index file etc. The names of the various ``.rst``
    files are specified in the ``#>>>... Part: ...`` markers. Normally,
    a part name corresponding to the included filename is used.

    CAVEAT: Nested includes in doconce files and doconce files in subdirs.
    SOLUTION: Use #>>> Part: mypart >>> for an include mypart/mypart.do.txt.
    All parts are then split into files in the top directory.

    fig dirs must be copied, but that can be easily done automatically
    if the fig dir name is of the right form.
    """

    if len(sys.argv) <= 1:
        _usage_split_rst0()
        sys.exit(0)

    complete_file = sys.argv[1]
    f = open(complete_file, 'r')
    filestr = f.read()
    f.close()

    # Determine parts
    part_pattern = r'\.\.\s*>>+\s*[Pp]art:\s*%s\s*>>+'
    parts = re.findall(part_pattern % '([^ ]+?)', filestr)

    # Split file
    for i in range(len(parts)):
        if i < len(parts)-1:  # not the last part?
            this_part = part_pattern % parts[i]
            next_part = part_pattern % parts[i+1]
        else:
            this_part = part_pattern % parts[i]
            next_part = '$'  # end of string
        pattern = '%s(.+?)%s' % (this_part, next_part)
        cpattern = re.compile(pattern, re.DOTALL)
        m = cpattern.search(filestr)
        text = m.group(1)
        filename = parts[i] + '.rst'
        f = open(filename, 'w')
        f.write(text)
        f.close()
    print(' '.join(parts))


def _usage_split_rst():
    print('Usage:\n'
          'doconce split_rst <file>[.rst]\n\n'
          'Example:\n'
          'doconce format sphinx mydoc.do.txt\n'
          'doconce sphinx_dir author="Kaare Dump" title="Short title" dirname=mydir mydoc.rst\n'
          'doconce split_rst mydoc.rst\n'
          'python automake_sphinx.py\n')


def split_rst():
    """
    Split rst file into parts. Use !split command as separator between
    parts.
    """
    if len(sys.argv) <= 1:
        _usage_split_rst()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.rst'):
        basename = filename
        filename += '.rst'
    else:
        basename = filename[:-4]

    header, parts, footer = get_header_parts_footer(filename, "rst")
    import pprint
    files = doconce_rst_split(parts, basename, filename)
    print(basename, 'split into')
    print(' '.join(files))


def doconce_rst_split(parts, basename, filename):
    """Native doconce style splitting of rst file into parts."""
    # Write the parts to file and fix references to equations.

    label_pattern = r'.. math::\s+:label: (.+?)$'
    parts_label = [re.findall(label_pattern, ''.join(part), flags=re.MULTILINE)
                   for part in parts]
    parts_label2part = {}   # map an eq. label to where it is defined
    for i in range(len(parts_label)):
        for label in parts_label[i]:  # assume all labels are unique
            parts_label2part[label] = i
    label2tag = {}
    local_eq_no = 1
    for pn, part_label in enumerate(parts_label):
        for label in part_label:
            label2tag[label] = '%d' % (local_eq_no)
            local_eq_no += 1

    # The definition of |nbsp| must be repeated in each part, except the first.
    # The definition is inserted in the beginning of the document, i.e.,
    # in parts[0].
    nbsp = '.. |nbsp| unicode:: 0xA0' in ''.join(parts[0])

    generated_files = []
    for pn, part in enumerate(parts):
        text = ''.join(part)

        # Check if headings are consistent: the first heading must be
        # the highest one
        m = re.search(r'^(%%+|==+|--+|~~+)$', text, flags=re.MULTILINE)
        if m:
            first_heading = m.group(1)
            if first_heading.startswith('='):
                if re.search(r'^(%%+)$', text, flags=re.MULTILINE):
                    print(r"""
*** error: first heading in part %d is a section, but the part
    also contains a chapter.
    !split must be moved to avoid such inconsistent reST headings""" % pn)
                    _abort()
            elif first_heading.startswith('-'):
                if re.search(r'^(%%+|==+)$', text, flags=re.MULTILINE):
                    print(r"""
*** error: first heading in part %d is a subsection, but the part
    also contains a chapter or section.
    !split must be moved to avoid such inconsistent reST headings""" % pn)
                    _abort()
            elif first_heading.startswith('~'):
                if re.search(r'^(%%+|==+|--+)$', text, flags=re.MULTILINE):
                    print(r"""
*** error: first heading in part %d is a subsubsection, but the part
    also contains a chapter, section, or subsection.
    !split must be moved to avoid such inconsistent reST headings""" % pn)
                    _abort()

        part_filename = _part_filename % (basename, pn) + '.rst'
        generated_files.append(part_filename)

        if nbsp and pn > 0 and '|nbsp|' in text:
            text = r"""

.. |nbsp| unicode:: 0xA0
   :trim:

""" + text

        for label in parts_label[pn]:
            # All math labels get an anchor above for equation refs
            # from other parts. The anchor is Eq:label.
            # Also remove the label when we insert a \tag{}.
            text = re.sub(r'.. math::\s+:label: %s\s+' % label,
                          r".. _Eq:%s:\n\n.. math::\n\n    \\tag{%s}\n    " %
                          (label, label2tag[label]), text, flags=re.MULTILINE)
        local_eqrefs = re.findall(r':eq:`(.+?)`', text)
        for label in local_eqrefs:
            # (Ignore non-existent labels - sphinx.py removes labels
            # in non-align math environments anyway)

            #if parts_label2part.get(label, None) == pn:
            # References to local labels in this part used to apply the
            # standard syntax - not anymore since we have tags for all
            # labels
            #pass
            text = text.replace(
                r':eq:`%s`' % label,
                ':ref:`(%s) <Eq:%s>`' %
                (label2tag.get(label, 'label:removed'), label))
        f = open(part_filename, 'w')
        f.write(text)
        f.close()
    return generated_files


def _usage_list_labels():
    print('Usage:\n'
          'doconce list_labels doconcefile.do.txt')


def list_labels():
    """
    List all labels used in a doconce or latex file.
    Since labels often are logically connected to headings in
    a document, the headings are printed in between in the
    output from this function, with a comment sign # in
    front so that such lines can easily be skipped when
    processing the output.

    The purpose of the function is to enable clean-up of labels
    in a document. For example, one can add to the output a
    second column of improved labels and then make replacements.
    """
    if len(sys.argv) <= 1:
        _usage_list_labels()
        sys.exit(0)
    filenames = sys.argv[1:]

    for filename in filenames:
        # Seach in doconce or latex file
        dofile = True if filename.endswith('.do.txt') else False
        lines = open(filename, 'r').readlines()
        labels = []  # not yet used, but nice to collect all labels
        for line in lines:
            # Identify heading and printout
            heading = ''
            if dofile:
                m = re.search(r'={5,9}\s*(.+?)\s*={5,9}', line)
                if m:
                    heading = m.group(1).strip()
            else:
                m = re.search(r'section\*?\{(.+)\}', line) # make .+ greedy
                if m:
                    heading = m.group(1).strip()
            if heading:
                print('# section: ' + heading)

            # Identify label
            if 'label{' in line:
                m = re.search(r'label\{(.+?)\}', line)
                if m:
                    label = m.group(1).strip()
                else:
                    print('Syntax error in line')
                    print(line)
                    _abort()
                print(label)
                labels.append(label)


def _usage_teamod():
    print('Usage:\n'
          'doconce teamod <dirname> [<basename>]\n\n'
          'Create a boilerplate directory <dirname> for a teaching module. \n'
          'The filenames created are named after <basename>')


def teamod():
    if len(sys.argv) < 2:
        _usage_teamod()
        sys.exit(0)
    dirname = sys.argv[1]
    name = 'teamod'
    if len(sys.argv) > 2:
        name = sys.argv[2]
    if os.path.isdir(dirname):
        os.rename(dirname, dirname + '.old~~')
        print('directory %s exists, renamed to %s.old~~' % (dirname, dirname))
    os.mkdir(dirname)
    os.chdir(dirname)
    os.mkdir('fig-%s' % name)
    os.mkdir('src-%s' % name)
    os.mkdir('slides-%s' % name)
    f = open('main_%s.do.txt' % name, 'w')
    f.write('# Main file for teaching module "%s"\n\n'
            'TITLE: Here Goes The Title ...\n'
            'AUTHOR: name1 email:..@.. at institution1, institution2, ...\n'
            'AUTHOR: name2 at institution3\n'
            'DATE: today\n\n'
            '# #include "%s.do.txt"\n' % (name, name))
    f.close()
    f = open('%s.do.txt' % name, 'w')
    f.write('# Teaching module: %s\n'
            '======= Section =======\n\n'
            '===== Subsection =====\n'
            'idx{example}\n'
            'label{mysubsec}\n\n'
            '__Paragraph.__ Running text...\n\n'
            'Some mathematics:\n\n'
            '!bt\n'
            r'\begin{align}\n'
            'a &= b,  label{eq1}\\\n'
            'a &= b,  label{eq2}\n'
            '\end{align}\n'
            '!et\n'
            'or\n\n'
            '!bt\n'
            '\[ a = b, \quad c=d \]\n'
            '!et\n\n'
            'Some code:\n'
            '!bc pycod\n'
            'def f(x):\n'
            'return x + 1\n'
            '!ec\n\n'
            'A list with\n\n'
            '* item1\n'
            '* item2\n'
            '* subitem2\n'
            '* item3\n'
            'continued on a second line\n\n\n')
    f.close()


def _usage_assemble():
    print('Usage:\n'
          'doconce assemble master.do.txt')


def assemble():
    # See 2DO and teamod.do.txt

    # Assume some master.do.txt including other .do.txt recursively.
    # search for all @@@CODE, FIGURE, MOVIE and archive in list/dict.
    # search for all #include ".+\.do\.txt", call recursively
    # for each of these with dirname and dotxtname as arguments.
    # Build local links to all src- and figs- directories, make
    # sure all teamod names are unique too.

    # analyzer: old comments on how to implement this. Try the
    # description above first.
    if len(sys.argv) < 2:
        _usage_assemble()
        sys.exit(0)

    master = sys.argv[2]

    # Run analyzer...


def _usage_analyzer():
    print('Usage:\n'
          'doconce analyzer complete_file.do.txt')


def analyzer():
    """
    For a doconce file, possibly composed of many other doconce
    files, in a nested fashion, this function returns a tree
    data structure with the various parts, included files,
    involved source code, figures, movies, etc.

    Method:
    Go through all #include's in a doconce file, find subdirectories
    used in @@@CODE, FIGURE, and MOVIE commands, and make links
    in the present directory to these subdirectories such that
    @@@CODE, FIGURE, and MOVIE works from the present directory.
    This is very important functionality when a doconce document
    is made up of many distributed documents, in different
    directories, included in a (big) document.

    Make recursive calls.
    """
    # 2DO:
    # - start with an example (some Cython intro examples? in a tree?)
    # - make doconce nested_include
    #   which makes a tree of all the dirs that are involved in a
    #   complete document
    # - simply copy all subnits and the complete doc to a new _build dir
    # - simply copy all figs-*, movies-*, src-* to _build
    # - compile

    # IDEA: Have a convention of src-poisson, figs-poisson etc
    # naming and use a simple script here to link from one dir to
    # all src-* and figs-* movies-* found in a series of dir trees. YES!!
    # Maybe use code below to issue warnings if FIGURE etc applies other
    # directories (could extend with eps-*, ps-*, pdf-*, png-*, jpeg-*,
    # gif-*, flv-*, avi-*, ...) and/or do this also in std doconce
    # translation (no, simple stand-alone thing must be fine with
    # figs/, it's the big distributed projects that need this
    # naming convention).  YES! Should be figs-basename(os.getcwd())

    # Can play with fenics tut: put each section in sep dirs,
    # stationary/poisson, transient/diffusion etc.,
    # with local src and figs
    # Need a script that can pack all local src dirs into a separate tree
    # for distribution (doconce pack_src): create new tree, walk a set
    # of trees, for each subdir with name src-*, strip off src-, copy
    # subdir to right level in new tree

    # Support for latex files too (includegraphics, movie15, psfig,
    # input, include), starting point is a .tex file with includes/inputs

    if len(sys.argv) <= 1:
        _usage_analyzer()
        sys.exit(0)

    # Must have this in a function since we need to do this recursively
    filename = sys.argv[1]
    alltext = open(filename, 'r').read()
    # preprocess parts and includes
    part_pattern = r'\.\.\s*>>+\s*[Pp]art:\s*%s\s*>>+'
    parts = re.findall(part_pattern % '([^ ]+?)', alltext)

    include_files = re.findall(r"""[#%]\s+\#include\s*["']([A-Za-z0-9_-., ~]+?)["']""", alltext)
    include_files = [filename for dummy, filename in include_files]

    from .common import INLINE_TAGS
    figure = re.compile(INLINE_TAGS['figure'], re.MULTILINE)
    movie = re.compile(INLINE_TAGS['movie'], re.MULTILINE)
    code = re.compile(r'^\s*@@@CODE\s+([^ ]+?) ')

    for filename in include_files:
        f = open(filename, 'r')
        directory = os.path.dirname(f)
        fstr = f.read()
        f.close()
        # What about figs/myfig/1stver/t.png? Just link to figs...
        # but it's perhaps ok with links at different levels too?
        figure_files = [filename for filename, options, captions in \
                        figure.findall(fstr)]
        movie_files = [filename for filename, options, captions in \
                       movie.findall(fstr)]
        code_files = code.findall(fstr)
        print(figure_files)
        figure_dirs = [os.path.dirname(f) for f in figure_files] # no dir??
        print(figure_dirs)
        dirs = [os.path.join(directory, figure_dir) \
                for figure_dir in figure_dirs]


def _usage_old2new_format():
    """Phased out"""
    print('Usage:\n'
          'doconce <file1.do.txt> <file2.do.txt> ...\n\n'
          'Make substitutions to convert ')


def old2new_format():
    """Phased out"""
    if len(sys.argv) == 1:
        _usage_old2new_format()
        sys.exit(0)
    for filename in sys.argv[1:]:
        print('Converting', filename)
        _old2new(filename)


def _old2new(filename):
    """Phased out"""
    """
    Read file with name filename and make substitutions of
    ___headings___ to === headings ===, etc.
    A backup of the old file is made (filename + '.old').
    """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    os.rename(filename, filename + '.old')

    # perform substitutions:
    nchanges = 0
    for i in range(len(lines)):
        oldline = lines[i]
        # change from ___headings___ to === headings ===:
        lines[i] = re.sub(r'(^\s*)_{7}\s*(?P<title>[^ ].*?)\s*_+\s*$',
                          r'\g<1>======= \g<title> =======' + '\n', lines[i])
        lines[i] = re.sub(r'(^\s*)_{5}\s*(?P<title>[^ ].*?)\s*_+\s*$',
                          r'\g<1>===== \g<title> =====' + '\n', lines[i])
        lines[i] = re.sub(r'(^\s*)_{3}\s*(?P<title>[^ ].*?)\s*_+\s*$',
                          r'\g<1>=== \g<title> ===' + '\n', lines[i])
        if lines[i].startswith('AUTHOR:'):
            # swith to "name at institution":
            if not ' at ' in lines[i]:
                print('Warning, file "%s": AUTHOR line needs "name at institution" syntax' % filename)

        if oldline != lines[i]:
            nchanges += 1
            print('Changing\n  ' + oldline + ' to\n  ' + lines[i])

    print('Performed %d changes in "%s"' % (nchanges, filename))
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()


def latex_header():
    from .doconce.doconce import INTRO
    print(INTRO['latex'])


def latex_footer():
    from .doconce.doconce import OUTRO
    print(OUTRO['latex'])


# -------------------- functions for spell checking ---------------------

_environments = [
    # DocOnce: use regex instead, it is safer (!bc at beginning of line etc.)
    # Mako: use regex
    # hpl tex stuff
    ("\\beq",               "\\eeq"),
    ("\\beqa",              "\\eeqa"),
    ("\\beqan",             "\\eeqan"),
    # Wait until the end with removing comment lines
    ]

# These are relevant if doconce spellcheck is applied to latex or ptex2tex files
_latex_environments = [
   ("\\begin{equation}",   "\\end{equation}"),
    ("\\begin{equation*}",  "\\end{equation*}"),
    ("\\begin{align}",      "\\end{align}"),
    ("\\begin{align*}",     "\\end{align*}"),
    ("\\begin{eqnarray}",   "\\end{eqnarray}"),
    ("\\begin{eqnarray*}",  "\\end{eqnarray*}"),
    ("\\begin{figure}[",    "]"),
    ("\\begin{figure*}[",   "]"),
    ("\\begin{multline}",   "\\end{multiline}"),
    ("\\begin{tabbing}",   "\\end{tabbing}"),
    # ptex2tex environments
    ("\\bccq",              "\\eccq"),
    ("\\bcc",               "\\ecc"),
    ("\\bcod",              "\\ecod"),
    ("\\bpycod",            "\\epycod"),
    ("\\bpro",              "\\epro"),
    ("\\bpypro",            "\\epypro"),
    ("\\brpy",              "\\erpy"),
    ("\\bipy",              "\\eipy"),
    ("\\bfcod",             "\\efcod"),
    ("\\bfpro",             "\\efpro"),
    ("\\bccod",             "\\epcod"),
    ("\\bcpro",             "\\epcro"),
    ("\\bcppcod",           "\\ecppcod"),
    ("\\bcpppro",           "\\ecpppro"),
    ("\\bhtmlcod",          "\\ehtmlcod"),
    ("\\bhtmlpro",          "\\ehtmlpro"),
    ("\\brcod",             "\\ercod"),
    ("\\brpro",             "\\eprro"),
    ("\\bjscod",            "\\ejscod"),
    ("\\bjspro",            "\\ejspro"),
    ("\\blatexcod",         "\\elatexcod"),
    ("\\blatexpro",         "\\elatexpro"),
    ("\\bshcod",            "\\eshcod"),
    ("\\bshpro",            "\\eshpro"),
    ("\\bsys",              "\\esys"),
    ("\\bdat",              "\\edat"),
    ("\\bsni",              "\\esni"),
    ("\\bdsni",             "\\edsni"),
    ("\\bpyshell",          "\\epyshell"),
    ("\\bpy",               "\\epy"),
    ]

_replacements = [
    # General
    (r'cf.', ''),
    # DocOnce
    (r'^<%.+^%>', '', re.MULTILINE|re.DOTALL),  # Mako Python code
    (r'^<%doc.+^</%doc>', '', re.MULTILINE|re.DOTALL),  # Mako comments
    (r'"([^"]*?)":\s*"[^"]+?"', r'\g<1>'),  # links ("`file.py`" -> "": "...")
    (r'''URL:\s*".+?"''', '', re.DOTALL),
    (r"^#.*$", "", re.MULTILINE),
    (r"(idx|label|ref|refaux|cite)\{.*?\}", ""),
    (r"cite\[.+?\]\{.+?\}", ""),
    (r"refch\[.*?\]\[.*?\]\[.*?\]", "", re.DOTALL),
    (r"^(file|solution)=.+$", '', re.MULTILINE),  # file= in exercises
    (r'^ *\|[\-rlc]+?\|', '', re.MULTILINE),  # table line
    (r' +\| +', ' '),  # table line
    ('<linebreak>', ''),
    (r"={3,}",  ""),  # section
    (r"^__(.+?)__", r"\g<1>\n", re.MULTILINE),  # paragraph
    (r"\[\^.+?\]", ""), # footnote
    (r'`[^ ][^`]*?`', ""),
    (r"`[A-Za-z0-9_.]+?`", ""),
    (r"^#.*$",          "", re.MULTILINE),
    (r'"https?://.*?"', ""),
    (r'"ftp://.*?"', ""),
    (r"\b[A-Za-z_0-9/.:]+\.(com|org|net|edu|)\b", ""),  # net name
    (r'\[[A-Za-z]+:\s+[^\]]*?\]', ''),  # inline comment
    (r'''^\s*files? *= *[${}()"'A-Za-z_0-9.,*= ]+\s*$''', '', re.MULTILINE),
    (r'^\s*(kw|keywords) *= *([A-Za-z0-9\-._;, ]+)', '', re.MULTILINE),
    (r'^@@@CODE.*$', '', re.MULTILINE),
    (r'^@@@OSCMD.*$', '', re.MULTILINE),
    (r'^\s*(FIGURE|MOVIE):\s*\[.+?\]',    '', re.MULTILINE),
    (r'^\s*BIBFILE:.+$',    '', re.MULTILINE),
    (r'^\s*TOC:\s+(on|off)', '', re.MULTILINE),
    (r'\$[^{].*?\$', '', re.DOTALL),  # inline math
    (r'\$\{[A-Za-z_].+?\}', '', re.DOTALL),   # mako substitutions (note that ${\cal O}..$ math is not allowed)
    (r'\{copyright.+?\}', ''),
    ('!split', ''),
    (r'![be]slidecell', ''),
    (r'![be]ans', ''),
    (r'![be]sol', ''),
    (r'![be]subex', ''),
    (r'![be]hint', ''),
    (r'![be]notes', ''),
    (r'![be]pop', ''),
    (r'![be]warning', ''),
    (r'![be]summary', ''),
    (r'![be]question', ''),
    (r'![be]notice', ''),
    (r'![be]quote', ''),
    (r'![be]box', ''),
    (r'![be]block', ''),
    (r'![be]remarks', ''),
    (r'![be]quiz', ''),
    (r'![be]u-[^ ]+', ''),  # user-def envirs
    (r'^Cw: *', '', re.MULTILINE),
    (r'^Cr: *', '', re.MULTILINE),
    (r'^E: *', '', re.MULTILINE),
    (r'^Q: *', '', re.MULTILINE),
    (r'^K: *', '', re.MULTILINE),
    (r'^L: *', '', re.MULTILINE),
    # Preprocess
    (r'^#.*ifn?def.*$', '', re.MULTILINE),
    (r'^#.*else.*$', '', re.MULTILINE),
    (r'^#.*endif.*$', '', re.MULTILINE),
    (r'^#include.*$', '', re.MULTILINE),
    # Mako
    (r'^<%.+?^%>', '', re.MULTILINE|re.DOTALL),
    (r'^% .*$', '', re.MULTILINE),
    (r'^<%.*$', '', re.MULTILINE),
    ]

_latex_replacements = [
    (r'%.*$', '', re.MULTILINE),  # comments
    (r'\\.*section\{(.+)\}', '\g<1>'),
    (r'^\\\[[^@]+\\\]',    ''),  # (@ is "unlikely" character)
    (r'\\includegraphics.*?(\.pdf|\.png|\.eps|\.ps|\.jpg)', ''),
    (r'\\(pageref|eqref|ref|label|url|emp)\{.*?\}', ''),
    (r'\\(emph|texttt)\{(.*?)\}', '\g<2>'),
    (r'\\footnote\{', ' '),  # leaves an extra trailing } (ok)
    #(r'\\[Vv]erb(.)(.+?)\1', '\g<2>'),
    (r'\\[Vv]erb(.)(.+?)\1', ''),
    (r'\\index\{.*?\}', ''),
    (r'\$.+?\$', '', re.DOTALL),
    (r'([A-Za-z])~', '\g<1> '),
    (r'``(.+?)''', '\g<1>'),  # very important, otherwise doconce verb eats the text
    (r' \.', '.'),
    ('\n\\.', '.\n'),
    (r':\s*\.', '.'),
    (r' ,', ','),
    ('\n\,', ',\n'),
    (',{2,}', ','),
    # ptex2tex
    (r'^@@@DATA.*$',    '', re.MULTILINE),
    (r'^@@@CMD.*$',    '', re.MULTILINE),
    # hpl's idx latex commands
    (r'\\idx\{.*?\}', ''),
    (r'\\idx(font|f|m|p|st|s|c|e|numpyr|numpy)\{.*?\}', ''),
    (r'\\codett\{.*?\}', ''),
    (r'\\code\{.*?\}', ''),
    ]

_common_typos = [
    '!bsubsex',
    '!esubsex',
    'hiearchy',
    'hieararchy',
    'statment',
    ' imples',
    'imples ',
    'execption',
    'excercise',
    'exersice',
    'eletric',
    'everyting',
    'progam',
    'technqiues',
    'incrased',
    'similarily',
    'occurence',
    'persue',
    'becase',
    'frequence',
    'noticable',
    'peform',
    'paramter',
    'intial',
    'inital',
    'condtion',
    'expontential',
    'differentation',
    'recieved',
    'cateogry',
    'occured',
    '!bc pydoc',
    '!bc pycodc',
    ]


def _grep_common_typos(text, filename, common_typos):
    """Search for common typos and abort program if any is found."""
    found = False
    for i, line in enumerate(text.splitlines()):
        for typo in common_typos:
            if re.search(typo, line):
                print('\ntypo "%s" in line %d in file %s:\n' % \
                      (typo, i+1, filename), line)
                found = True
    if found:
        sys.exit(1)


def _strip_environments(text, environments, verbose=0):
    """Remove environments in the ``environments`` list from the text."""
    # Note: this stripping does not work well for !bc and !bt envirs,
    # because a phrase like `!bc pycod` in running text gives a split...
    for item in environments:
        if len(item) != 2:
            raise ValueError(
                '%s in environments to be stripped is wrong' % (str(item)))
        begin, end = item
        if not begin in text:
            continue
        parts = text.split(begin)
        text = parts[0]
        for part in parts[1:]:
            subparts = part.split(end)
            text += end.join(subparts[1:])
            if verbose > 1:
                print('\n============ split %s <-> %s\ntext so far:' % (begin, end))
                print(text)
                print('\n============\nSkipped:')
                print(subparts[0])
        if verbose > 0:
            print('split away environments: %s %s\nnew text:\n' % (begin, end))
            print(text)
            print('\n==================')
    return text


def _do_regex_replacements(text, replacements, verbose=0):
    """Substitute according to the `replacement` list."""
    for item in replacements:
        if len(item) == 2:
            from_, to_ = item
            text = re.sub(from_, to_, text)
        elif len(item) == 3:
            from_, to_, flags = item
            text = re.sub(from_, to_, text, flags=flags)
        if verbose > 0:
            print('==================')
            print('regex substitution: %s -> %s\nnew text:' % (from_, to_))
            print(text)
    return text


def _do_fixes_4MSWord(text):
    t = text  # short cut
    # Deal with special strange left-overs from removing ref, cite, etc.
    # , , ,
    t = re.sub(r',\s+,', ' ', t)
    # .  period at the beginning of a line
    t = re.sub(r'^\. +', '', t, flags=re.MULTILINE)
    #,   comma at the beginning of a line
    t = re.sub(r'^\, +', '', t, flags=re.MULTILINE)
    # text like   .,
    t = re.sub(r' +,\.', '.', t)
    # or   -.
    t = re.sub(r' +-\.', '.', t)
    # and ( ,  ,   , , )
    t = re.sub(r'\([, ]*\)', ' ', t)
    # initial spaces on a line
    t = re.sub(r'^ +([A-Z])', r'\1', t, flags=re.MULTILINE)
    # too complicated to remove emphasize: t = re.sub(r'(^| +)\*(.+?)\*[, \n.]', r' \2 ', t, flags=re.DOTALL|re.MULTILINE)
    t = re.sub(r'^\s+\*\s+', '', t, flags=re.MULTILINE)
    t = re.sub(r' +\)', ')', t)
    t = t.replace(':)', ')')
    t = re.sub(r'^ +', '', t, flags=re.MULTILINE)
    t = re.sub(r'^\.\n', '\n', t, flags=re.MULTILINE)
    t = re.sub(r'  +', ' ', t)
    t = re.sub(r'\\begin\{.+?\}', '', t)
    t = re.sub(r'\\end\{.+?\}', '', t)
    # Remove space above paragraphs starting with lower case
    t = re.sub(r'\n\n+([a-z])', r' \1', t)
    # Remove newlines at the end of text (to help word)
    # (this might not be desired for grepping in the stripped file)
    if not '--dont_remove_newlines' in sys.argv:
        t = re.sub(r'([A-Za-z0-9,.:!?)])\n(?=[^\n])', '\g<1> ', t)
    # Do these after we have joined lines
    # spaces before comma
    t = re.sub(r'([A-Za-z])[:;?.]?\s+, +', r'\1, ', t)
    # spaces before period
    t = re.sub(r'([A-Za-z])[:;?.]? +\. +', r'\1. ', t)
    # spaces before period
    t = re.sub(r'([A-Za-z])[:;?.]? +\.', r'\1.', t)
    # spaces before colon
    t = re.sub(r'([A-Za-z])[:;?.]? +:', r'\1:', t)

    t = t.replace(', g.,', '')
    t = t.replace('ref[', '')
    t = t.replace('][', '')
    t = t.replace(']', '')
    t = t.replace('[', '')
    t = t.replace(']', '')
    t = t.replace('*', '')
    t = t.replace('|', '')
    t = t.replace('()', '')
    t = t.replace('(-)', '')
    t = t.replace(r'\noindent', '')

    return t


def _spellcheck(filename, language='English', spellchecker='ispell', dictionaries=['.dict4spell.txt'], newdict=None,
                remove_multiplicity=False, strip_file='.strip', verbose=False):
    """
    Spellcheck `filename` and list misspellings in the file misspellings.txt~.
    The `dictionaries` list contains filenames for dictionaries to be
    used with ispell.
    `newdict` is an optional filename for creating a new, updated
    dictionary containing all given dictionaries and all misspellings
    found (assuming they are correct and approved in previous runs).
    `remove_multiplicity` removes multiple occurrences of the same
    misspelling in the misspellings.txt~ (output) file.
    `strip_file` holds the filename of a file with definitions of
    environments to be stripped off in the source file, replacements
    to be performed, and a list of typical misspellings that are first
    check before ispell is run.
    """

    try:
        f = open(filename, 'r')
    except IOError:
        print('\nfile %s does not exist!' % filename)
        _abort()

    text = f.read()
    f.close()

    # Standardize newlines
    text = re.sub(r'(\r\n|\r|\n)', '\n', text)

    # Remove all !bc and !bt blocks
    text = re.sub(r'^!bc(.*?)\n(.*?)^!ec', '',
                  text, flags=re.DOTALL|re.MULTILINE)
    text = re.sub(r'^!bt *\n(.*?)^!et', '', text,
                  flags=re.DOTALL|re.MULTILINE)

    # Remove all comments
    text = re.sub(r'^#.+$', '', text, flags=re.MULTILINE)

    # Check for double words (before removing verbatim)

    pattern = r"\b([\w'\-]+)(\s+\1)+\b"
    found = False
    offset = 30  # no of chars before and after double word to be printed
    start = 0
    while start < len(text)-1:
        m = re.search(pattern, text[start:])
        if m:
            # Words only
            word = m.group(0)
            try:
                [float(w) for w in word.split()]
                is_word = False
            except ValueError:
                # Drop words with underscore, ...
                #drop = ['_', '--',
                is_word = '_' not in word

            if is_word:
                print("\ndouble words detected in %s (marked inside [...]):\n------------------------" % filename)
                print("%s[%s]%s\n------------------------" % \
                      (text[max(0,start+m.start()-offset):start+m.start()],
                       word,
                       text[start+m.end():min(start+m.end()+offset,
                                               len(text)-1)]))
                found = True
            start += m.end()
        else:
            break
    if found:
        pass

    # Remove inline quotes before inline verbatim
    pattern = "``(.+?)''([\n ,.?:)*_-])"
    text = re.sub(pattern, r'\g<1>\g<2>', text, flags=re.DOTALL)
    # Remove inline verbatim
    text = re.sub(r'`[^ ][^`]*?`', '', text)  # remove inline verbatim
    if verbose > 0:
        print('removal of quotes, inline verbatim, code and tex blocks\nnew text:\n')
        print(text)
        print('==================\n')

    # Continue with spell checking

    if os.path.isfile(strip_file):
        execfile(strip_file)
    else:
        environments = []
        replacements = []
        common_typos = []
    # Add standard definitions (above)
    environments += _environments
    replacements += _replacements
    common_typos += _common_typos

    # Add standard latex definitions when spellchecking latex
    if os.path.splitext(filename)[1] == '.tex':
        # Make sure to do latex first (\label{} before label{})
        environments = _latex_environments + environments
        replacements = _latex_replacements + replacements


    _grep_common_typos(text, filename, common_typos)

    text = _strip_environments(text, environments, verbose)
    #print('Text after environment strip:\n', text)

    text = _do_regex_replacements(text, replacements, verbose)
    #print('Text after regex replacements:\n', text)

    text = _do_fixes_4MSWord(text)

    # Write modified text to scratch file and run ispell
    scratchfile = 'tmp_stripped_%s' % filename
    f = open(scratchfile, 'w')
    f.write(text)
    f.close()
    personal_dictionaries = []
    p_opt = ''  # personal dictionary specification for ispell
    for dictionary in dictionaries:
        if os.path.isfile(dictionary):
            p_opt += " -p`pwd`/%s" % dictionary
            f = open(dictionary, 'r')
            personal_dictionaries += f.readlines()
            f.close()
        else:
            print('Dictionary file %s does not exist.' % dictionary)

    personal_dictionaries = list(set(personal_dictionaries))
    misspellings = 'tmp_misspelled_' + filename + '~'

    if not 'aspell_dictionary' in globals.locale_dict[language]:
        print("Language '%s' has no known aspell dictionary" % language)
        sys.exit(0)
    aspell_dictionary = globals.locale_dict[language]['aspell_dictionary']

    cmd = 'cat %s | ' % scratchfile
    if spellchecker == 'ispell':
        cmd += 'ispell -l -t -d %s %s > %s' % \
               (aspell_dictionary, p_opt, misspellings)
    elif spellchecker == 'aspell':

        # The personal file with word list has a special format in aspell, eg 'personal_ws-1.1 en 1'
        f = open(dictionary, 'r')
        line = f.readline()
        f.close()
        pattern = r'personal_ws-1.1 \w+ '
        if line!="" and not re.search(pattern, line):
            print('Warning: aspell requires a special format for the personal file %s.' % dictionary)
            print('         Check that the first line is eg "personal_ws-1.1 en 1"')
        cmd += 'aspell -t -d %s list %s > %s' % \
               (aspell_dictionary, p_opt, misspellings)
    system(cmd)

    # Load misspellings, remove duplicates
    f = open(misspellings, 'r')
    words = f.readlines()
    f.close()
    words2 = list(set(words))  # remove multiple words
    if len(words2) > 0:             # do we have misspellings?
        print('%d misspellings in %s' % (len(words2), filename))
        if remove_multiplicity:
            f = open(misspellings, 'w')
            f.write(words2)
            f.close()
    else:
        os.remove(misspellings)

    # Make convenient updates of personal dictionaries
    if newdict is not None:
        accepted_words = words2 + personal_dictionaries
        if os.path.isfile(newdict):
            f = open(newdict, 'r')
            newdict_words = f.readlines()
            f.close()
            newdict_add = words2 + newdict_words
            newdict_add = sorted(list(set(newdict_add)))
            union = accepted_words + newdict_words
            union = sorted(list(set(union)))
        else:
            union = accepted_words
            newdict_add = words2
        # union is the potentially new personal dictionary
        #
        f = open(newdict, 'w')
        f.writelines(newdict_add)
        f.close()
        f = open('new_dictionary.txt~', 'w')
        f.writelines(union)
        f.close()


def _spellcheck_all(filenames, **kwargs):
    for filename in glob.glob('tmp_misspelled*~') + glob.glob('misspellings.txt~*'):
        os.remove(filename)
    for filename in ['__tmp.do.txt']:
        if filename in sys.argv[1:]:  # iterate over copy
            os.remove(filename)
            del sys.argv[sys.argv.index(filename)]
    for filename in filenames:
        if not filename.startswith('tmp_stripped_'):
            _spellcheck(filename, **kwargs)
    tmp_misspelled = glob.glob('tmp_misspelled*~')
    if len(tmp_misspelled) > 0:
        print()
        if len(filenames) == 1:
            print('See misspellings.txt~ for all misspelled words found.')
        else:
            for name in tmp_misspelled:
                print('See', name, 'for misspellings in', name.replace('tmp_misspelled_', '')[:-1])
        print('Search tmp_stripped_*.do.txt for the misspellings')
        dictfile = kwargs.get('dictionary', '.dict4spell.txt')
        print('When all misspellings are acceptable, cp new_dictionary.txt~',\
              dictfile, '\n')
        sys.exit(1)
    else:
        sys.exit(0)


def _usage_spellcheck():
    print('Usage:\n'
          'doconce spellcheck <file1>[.do.txt] <file2>[.do.txt] ...  # use .dict4spell.txt\n'
          'doconce spellcheck -d .mydict.txt <file1>.do.txt <file2>.do.txt ...\n'
          '\n'
          'Spellcheck of files via ispell (but problematic parts are removed from the\n'
          'files first).\n'
          '\n'
          'Output:\n'
          '\n'
          'misspellings.txt~: dictionary of potentially new accepted words, based on all\n'
          'the current misspellings.\n'
          '\n'
          'new_dictionary.txt~: suggested new dictionary, consisting of the old and all new misspellings\n'
          '(if they can be accepted).\n'
          '\n'
          'tmp_stripped_file1.do.txt: the original files are stripped off for various constructs that cause trouble\n'
          'in spelling and the stripped text is found in files with a filename prefix tmp_stripped_ (this file can \n'
          'be checked for spelling and grammar mistakes in MS Word, for instance, but a better method might be to \n'
          'translate the entire DocOnce document to HTML and import that HTML code into Word.)\n'
          '\n'
          'Usage\n'
          '-----\n'
          '\n'
          'For a new project, do the points below for initializating a new accepted personal dictionary for \n'
          'this project. Thereafter, the process is automated: misspellings.txt~ should be empty if there are \n'
          'no new misspellings.\n'
          "tmp_misspelled*~ are made for each file tested with the file's misspelled words.\n"
          '\n'
          'For each file:\n'
          '\n'
          '* Run spellcheck.py without a dictionary or with a previous dictionary:\n'
          '  doconce spellcheck <file> or doconce spellcheck -d .mydict.txt <file>\n'
          '  (default dictionary file is .dict4spell.txt)\n'
          '* Check misspelled.txt~ for misspelled words. Change wrong words.\n'
          '* Rerun. If all words in misspelled.txt are acceptable, copy new_dictionary.txt to .dict4spell.txt \n'
          '(or another name)\n'
          '* Optional: import tmp_stripped_text.txt into MS Word for grammar check.\n'
          '* Remove tmp_* and *~ files\n'
          '\n'
          'The next time one can run::\n'
          '\n'
          'spellcheck.py <file>*                   # use .dict4spell.txt\n'
          'spellcheck.py -d .mydict.txt <file>*\n'
          '\n'
          'misspellings.txt~ should ideally be empty if there are no (new) spelling errors. One can check \n'
          'that the file is empty or check the $? variable on Unix since this prorgram exits with 1 when spelling\n'
          'errors are found in any of the tested files::\n'
          '\n'
          '# Run spellcheck\n'
          'doconce spellcheck *.do.txt\n'
          'if [ $? -ne 0 ]; then exit; fi\n'
          '\n'
          '\n'
          'How to correct misspellings\n'
          '---------------------------\n'
          '\n'
          'Some misspellings can be hard to find if the word is strange (like "emp", for instance). Then invoke \n'
          '``tmp_stripped_text.txt``, which is the stripped version of the text file being  spellchecked. All \n'
          'references, labels, code segments, etc., are removed in this stripped file. \n'
          'Run ispell on the file:\n'
          '\n'
          'ispell -l -p.dict4spell.txt tmp_stripped_text.txt\n'
          '\n'
          'ispell will prompt you for the misspellings and show the context. A common error in latex is to \n'
          r"forget a ``\ref`` or ``\label`` in front of a label so that the label gets spellchecked. "
          '\nThis may give rise to strange words flagged as misspelled.\n'
          '\n'
          'How to control what is stripped\n'
          '-------------------------------\n'
          '\n'
          'The spellcheck function loads a file .strip, if present, with possibly three lists that defines\n'
          'what is being stripped away in ``tmp_stripped_*`` files:\n'
          '\n'
          '* ``environments``, holding begin-end pairs of environments that should be entirely removed from the text.\n'
          '* ``replacements``, holding (from, to) pairs or (from, to, regex-flags) triplets for substituting text.\n'
          '* ``common_typos``, holding typical wrong spellings of words.\n'
          '\n'
          'execfile is applied to .strip to execute the definition of the lists.\n')


def spellcheck():
    if len(sys.argv) < 2:
        _usage_spellcheck()
        return
    supported_languages = list(filter(lambda l: 'aspell_dictionary' in globals.locale_dict[l], sorted(globals.locale_dict.keys())))
    supported_languages_str = ', '.join(supported_languages)

    import argparse
    parser = argparse.ArgumentParser(prog="doconce spellcheck",
        description="Spellcheck DocOnce documents",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Call doconce spellcheck without any arguments to get more information")
    parser.add_argument('filename', type=str, nargs='+', help='A *.do.txt file to spellcheck')
    parser.add_argument('-d', '--dictionary', type=str, default=None, dest='dictionary',
        help='A personal dictionary file with whitelisted words')
    parser.add_argument('-c', '--command', type=str, default='ispell', dest='spellchecker',
                        help='The spell checker program. ispell or aspell')
    parser.add_argument('-l', '--language', type=str, default='English', dest='language',
        help="Supported languages: %s" % supported_languages_str)
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()
    filenames = args.filename
    dictionary_filename = args.dictionary
    spellchecker = args.spellchecker
    language = args.language
    verbose = args.debug

    if dictionary_filename != None:
        if os.path.isfile(dictionary_filename):
            dictionary = [dictionary_filename]
        else:
            print("ERROR: Dictionary file '%s' does not exist!")
            sys.exit(0)
    else:
        if os.path.isfile('.dict4spell.txt'):
            dictionary = ['.dict4spell.txt']
        else:
            dictionary = []

    if spellchecker not in ['ispell','aspell']:
        print("Unsupported spell checker '%s'. Choose ispell or aspell" % spellchecker)

    if language not in supported_languages:
        print("Unsupported language '%s'" % language)
        print("Supported languages: %s" % supported_languages_str)
        sys.exit(0)

    _spellcheck_all(filenames, language=language, spellchecker=spellchecker, newdict='misspellings.txt~', remove_multiplicity=False,
                    dictionaries=dictionary, verbose=verbose)


def _usage_ref_external():
    print('Usage:\n'
          'doconce ref_external <file>[.do.txt] [pubfile --skip_chapter]\n\n'
          'Must give pubfile if no BIBFILE in <file>[.do.txt]\n'
          '--skip_chapter avoids substitution of Chapter ref{} -> refch[Chapter ...][][].')


def ref_external():
    """
    Examine "# Externaldocuments: ..." in doconce file and publish
    file to suggest a substitution script for transforming
    references to external labels to the ref[][][] generalized
    reference form.
    """
    if len(sys.argv) < 2:
        _usage_ref_external()
        sys.exit(0)

    filename = sys.argv[1]
    if filename.endswith('.do.txt'):
        basename = filename[:-7]
    else:
        basename = filename
    # Analyze the topfile for external documents and publish file
    f = open(basename + '.do.txt', 'r')
    topfilestr = f.read()
    f.close()
    m = re.search('^#\s*[Ee]xternaldocuments:\s*(.+)$', topfilestr,
                  flags=re.MULTILINE)
    if m:
        external_docs = [s.strip() for s in m.group(1).split(',')]
    else:
        print('*** error: no # Externaldocuments: file1, file2, ... in', basename + '.do.txt')
        print('    cannot get info about external documents and their labels!')
        _abort()
    m = re.search('^BIBFILE:\s*(.+)', topfilestr, re.MULTILINE)
    if m:
        pubfile = m.group(1).strip()
    else:
        if len(sys.argv) >= 3:
            pubfile = sys.argv[2]
        else:
            print('*** error: no BIBFILE: file.pub, missing publish file on the command line!')
            _abort()
    print('    working with publish file', pubfile)
    import publish
    # Note: we have to operate publish in the directory
    # where pubfile resides
    pubdir, pubname = os.path.split(pubfile)
    if not pubdir:
        pubdir = os.curdir
    this_dir = os.getcwd()
    os.chdir(pubdir)
    pubdata = publish.database.read_database(pubname)
    os.chdir(this_dir)

    def process_external_doc(extdoc_basename):
        topfile = extdoc_basename + '.do.txt'
        if not os.path.isfile(topfile):
            print('*** error: external document "%s" does not exist' % topfile)
            _abort()
        f = open(topfile, 'r')
        text = f.read()
        m = re.search('^TITLE:\s*(.+)', text, flags=re.MULTILINE)
        if m:
            title = m.group(1).strip()
        else:
            print('*** error: no TITLE: ... in "%s"' % topfile)
            _abort()
        found = False
        key = None
        url = None
        for pub in pubdata:
            if pub['title'].lower() == title.lower():
                key = pub.get('key', None)
                url = pub.get('url', None)
                print('       title:', title)
                print('       url:', url)
                print('       key:', key)
                found = True
                break
        if not found and extdoc_basename != basename:
            print('*** warning: could not find the document')
            print('   ', title)
            print('    in the publish database %s' % pubfile)

        # Try to load the full doconce file as the result of mako,
        # or as the result of preprocess, or just extdoc_basename.do.txt
        dname, bname = os.path.split(extdoc_basename)
        dofile = os.path.join(dname, 'tmp_mako__' + bname + '.do.txt')
        if os.path.isfile(dofile):
            fullfile = dofile
        else:
            dofile = os.path.join(dname, 'tmp_preprocess__' + bname + '.do.txt')
            if os.path.isfile(dofile):
                fullfile = dofile
            else:
                fullfile = topfile
                # Check that there are no includes:
                m = re.search(r'^#\s+#include', text, flags=re.MULTILINE)
                if m:
                    print('*** error: doconce format is not run on %s' % topfile)
                    print('    cannot proceed...')
                    _abort()

        print('    ...processing', fullfile)
        f = open(fullfile, 'r')
        text = f.read()
        f.close()
        # Analyze the full text of the external doconce document
        labels = re.findall(r'label\{(.+?)\}', text)
        return title, key, url, labels, text

    # Find labels and references in this doconce document
    dummy, dummy, dummy, mylabels, mytext = process_external_doc(basename)
    refs = [(prefix, ref) for dummy, prefix, ref in
            re.findall(r'(^|\(|\s+)([A-Za-z]+?)\s+ref\{(.+?)\}', mytext,
                       flags=re.MULTILINE)]
    refs = [(prefix.strip(), ref.strip()) for prefix, ref in refs]
    refs = list(set(refs))
    pattern = r'\(ref\{(.+?)\}\)-\(ref\{(.+?)\}\)'
    eqrefs2 = list(set(re.findall(pattern, mytext)))
    mytext2 = re.sub(pattern, 'XXX', mytext)
    # Now all pairs of equation references are removed, search for triplets
    pattern = r'\(ref\{(.+?)\}\),\s+\(ref\{(.+?)\}\),?\s+and\s+\(ref\{(.+?)\}\)'
    eqrefs3 = list(set(re.findall(pattern, mytext2)))
    mytext3 = re.sub(pattern, 'XXX', mytext2)
    # Now all pairs and triplets are removed and we can collect the remaining
    # single equation references
    eqrefs1 = re.findall(r'\(ref\{(.+?)\}\)', mytext3)

    extdocs_info = {}
    refs2extdoc = {}
    for external_doc in external_docs:
        title, key, url, labels, text = process_external_doc(external_doc)
        extdocs_info[external_doc] = dict(title=title, key=key,
                                          url=url, labels=labels)
        for prefix, ref in refs:
            if ref not in mylabels:
                if ref in labels:
                    refs2extdoc[ref] = (external_doc, prefix)
        for ref in eqrefs1:
            if ref not in mylabels:
                if ref in labels:
                    refs2extdoc[ref] = (external_doc, 1)
        for ref1, ref2 in eqrefs2:
            if ref1 not in mylabels:
                if ref1 in labels:
                    refs2extdoc[ref1] = (external_doc, 2)
            if ref2 not in mylabels:
                if ref2 in labels:
                    refs2extdoc[ref2] = (external_doc, 2)
        for ref1, ref2, ref3 in eqrefs3:
            if ref1 not in mylabels:
                if ref1 in labels:
                    refs2extdoc[ref1] = (external_doc, 3)
            if ref2 not in mylabels:
                if ref2 in labels:
                    refs2extdoc[ref2] = (external_doc, 3)
            if ref3 not in mylabels:
                if ref3 in labels:
                    refs2extdoc[ref3] = (external_doc, 3)

    # We now have all references in refs2extdoc and can via extdocs_info
    # get additional info about all references
    for label in mylabels:
        if label in refs2extdoc:
            print('*** error: ref{%s} in %s was found as' % (label, basename))
            print('    label{%s} in %s and %s' % \
                  (label, basename, refs2extdoc[label][0]))
            _abort()

    # Substitute all external references by ref[][][]
    scriptname = 'tmp_subst_references.sh'
    scriptname2 = 'tmp_grep_references.sh'
    f = open(scriptname, 'w')
    f2 = open(scriptname2, 'w')
    print('substitution script:', scriptname)
    print('grep script (for context of each substitution):', scriptname2)
    dofiles = basename[5:] + '.do.txt' if basename.startswith('main_') else basename + '.do.txt'
    f.write('files="%s"  # files to which substitutions apply\n\n' % dofiles)
    f2.write('files="%s"  # files to which substitutions apply\n\nnlines=6  # no of context lines for each matched line' % dofiles)
    skip_chapter = '--skip_chapter' in sys.argv
    skip_eqs = '--skip_eqs' in sys.argv
    for prefix, ref in refs:
        if skip_chapter and prefix.lower in ('chapter', 'appendix'):
            continue
        if ref not in mylabels:
            f.write(r"doconce subst '%(prefix)s\s+ref\{%(ref)s\}'  " % vars())
            f2.write(r"grep --context=$nlines --line-number -E '%(prefix)s\s+ref\{%(ref)s\}' $files" % vars() + '\n\n')
            ch = 'ch' if prefix.lower() in ('chapter', 'appendix') else ''
            f.write("'ref%(ch)s[%(prefix)s ref{%(ref)s}]" % vars())
            if ref in refs2extdoc:
                if ch:
                    f.write('[ cite{%s}][' %
                            extdocs_info[refs2extdoc[ref][0]]['key'])
                else:
                    f.write('[ in cite{%s}][' %
                            extdocs_info[refs2extdoc[ref][0]]['key'])
                f.write('the document "%s"' %
                        extdocs_info[refs2extdoc[ref][0]]['title'])
                if extdocs_info[refs2extdoc[ref][0]]['url'] is not None:
                    f.write(': "%s"' %
                            extdocs_info[refs2extdoc[ref][0]]['url'])
                if extdocs_info[refs2extdoc[ref][0]]['key'] is not None:
                    f.write(' cite{%s}' %
                            extdocs_info[refs2extdoc[ref][0]]['key'])
                f.write("]'")
            else:
                f.write("[no cite info][no doc info]'")
            f.write(' $files\n\n')
    if skip_eqs:
        f.close()
        return

    if eqrefs1 or eqrefs2 or eqrefs3:
        f.write('\n# Equations:\n')
    for ref in eqrefs1:
        if ref not in mylabels:
            f.write(r"doconce replace '(ref{%(ref)s})'  " % vars())
            f2.write(r"grep --context=$nlines --line-number '(ref{%(ref)s})' $files" % vars() + '\n\n')
            f.write("'ref[(ref{%(ref)s})]" % vars())
            if ref in refs2extdoc:
                f.write('[ in cite{%s}]' %
                        extdocs_info[refs2extdoc[ref][0]]['key'])
                f.write('[reference to specific _equation_ (label %s) in external document "%s": "%s" cite{%s} is not recommended]' %
                        (ref,
                         extdocs_info[refs2extdoc[ref][0]]['title'],
                         extdocs_info[refs2extdoc[ref][0]]['url'],
                         extdocs_info[refs2extdoc[ref][0]]['key']))
            else:
                f.write('[no cite info][no doc info]')
            f.write("' $files\n\n")
    for ref1, ref2 in eqrefs2:
        if ref1 not in mylabels and ref2 not in mylabels:
            f.write(r"doconce replace '(ref{%(ref1)s})-(ref{%(ref2)s})'  " % vars())
            f2.write(r"grep --context=$nlines --line-number '(ref{%(ref1)s})-(ref{%(ref2)s})' $files" % vars() + '\n\n')
            f.write("'ref[(ref{%(ref1)s})-(ref{%(ref2)s})]" % vars())
            if ref1 in refs2extdoc and ref2 in refs2extdoc:
                f.write('[ in cite{%s}]' %
                        extdocs_info[refs2extdoc[ref1][0]]['key'])
                f.write('[reference to specific _equations_ (label %s and %s) in external document "%s": "%s" cite{%s} is not recommended]' %
                        (ref1, ref2,
                         extdocs_info[refs2extdoc[ref1][0]]['title'],
                         extdocs_info[refs2extdoc[ref1][0]]['url'],
                         extdocs_info[refs2extdoc[ref1][0]]['key']))
            else:
                f.write('[no cite info][no doc info]')
            f.write("' $files\n\n")
    for ref1, ref2, ref3 in eqrefs3:
        if ref1 not in mylabels and ref2 not in mylabels \
               and ref3 not in mylabels:
            f.write(r"doconce subst '\(ref\{%(ref1)s\}\),\s+\(ref\{%(ref2)s\}\),?\s+and\s+\(ref{%(ref3)s\}\)'  " % vars())
            f2.write(r"grep --context=$nlines --line-number -E '\(ref\{%(ref1)s\}\),\s+\(ref\{%(ref2)s\}\),?\s+and\s+\(ref{%(ref3)s\}\)' $files" % vars() + '\n\n')
            f.write("'ref[(ref{%(ref1)s}), (ref{%(ref2)s}), and (ref{%(ref3)s})]" % vars())
            if ref1 in refs2extdoc and ref2 in refs2extdoc \
                   and ref3 in refs2extdoc:
                if refs2extdoc[ref1][0] == refs2extdoc[ref2][0] and \
                   refs2extdoc[ref2][0] == refs2extdoc[ref3][0]:
                    f.write('[ in cite{%s}]' %
                            extdocs_info[refs2extdoc[ref1][0]]['key'])
                else:
                    # the equations come from different external docs
                    s = set([extdocs_info[refs2extdoc[ref1][0]]['key'],
                             extdocs_info[refs2extdoc[ref2][0]]['key'],
                             extdocs_info[refs2extdoc[ref3][0]]['key']])
                    f.write('[ cite{%s}]' % ','.join(list(s)))

                f.write('[reference to specific _equations_ (label %s, %s, and %s) in external document "%s": "%s" cite{%s} is not recommended]' %
                        (ref1, ref2, ref3,
                         extdocs_info[refs2extdoc[ref][0]]['title'],
                         extdocs_info[refs2extdoc[ref][0]]['url'],
                         extdocs_info[refs2extdoc[ref][0]]['key']))
            else:
                f.write('[no cite info][no doc info]')
            f.write("' $files\n\n")
    f.close()


def _usage_latex_problems():
    print('Usage:\n'
          'doconce latex_problems <file>[.log] [overfull-hbox-limit --texcode]\n\n'
          'Interpret the .log file and write out latex problems related to\n'
          'undefined references, multiply defined labels, and overfull hboxes.\n'
          'The lower limit for overfull hboxes can be specified as an integer.\n'
          '--texcode causes the problematic lines in overfull hboxes to be printed.\n')


def latex_problems():
    if len(sys.argv) < 2:
        _usage_latex_problems()
        sys.exit(0)

    try:
        overfull_hbox_limit = float(sys.argv[2])
    except IndexError:
        overfull_hbox_limit = 20

    filename = sys.argv[1]
    if not filename.endswith('.log'):
        filename += '.log'
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    ok_overfull_hboxes = []
    # Springer T2 will have some overfull hboxes for chapter headings,
    # remove these from the report 120.1 and 30.8
    t2 = 't2do.sty' in ''.join(lines)
    if t2:
        ok_overfull_hboxes += ['120.1', '30.8']

    multiply_defined_labels = []
    multiply_defined_labels_pattern = r"LaTeX Warning: Label `(.+?)' multiply defined"
    undefined_references = []
    undefined_references_pattern = r"LaTeX Warning: Reference `(.+?)' on page (.+?) undefined"
    overfull_hboxes = []
    overfull_hboxes_pattern = r"Overfull \\hbox \((.+)pt too wide\) .+lines (.+)"
    for line in lines:
        m = re.search(multiply_defined_labels_pattern, line)
        if m:
            multiply_defined_labels.append(m.group(1))
        m = re.search(undefined_references_pattern, line)
        if m:
            undefined_references.append((m.group(1), m.group(2)))
        m = re.search(overfull_hboxes_pattern, line)
        if m:
            overfull_hboxes.append(
                ('%.1f' % float(m.group(1)), m.group(2).strip()))
    problems = False
    if multiply_defined_labels:
        problems = True
        print('\nMultiply defined labels:')
        for label in multiply_defined_labels:
            print('    ', label)
    if undefined_references:
        problems = True
        print('\nUndefined references:')
        for ref, page in undefined_references:
            print('    ', ref, 'on page', page)
    if overfull_hboxes:
        texcode = '--texcode' in sys.argv
        if texcode:
            # Load .tex file
            f = open(filename[:-4] + '.tex', 'r')
            texfile = f.readlines()
            f.close()
        problems = True
        print("\nOverfull hbox'es:")
        for npt, at_lines in overfull_hboxes:
            if float(npt) > overfull_hbox_limit and npt not in ok_overfull_hboxes:
                print('    ', npt, 'lines', at_lines)
                if texcode:
                    line_range = [int(line)-1 for line in at_lines.split('--')]
                    if line_range[1] - line_range[0] < 4 and r'\end' in texfile[line_range[1]]:
                        # Print more surroundings above
                        print('\n*** printing 6 lines above problem line:')
                        print(''.join(texfile[line_range[0]-6:line_range[1]+1]))
                    else:
                        print('\n', ''.join(texfile[line_range[0]:line_range[1]+1]))

    if not problems:
        print('no serious LaTeX problems found in %s!' % filename)


def _usage_grep():
    print('Usage:\n'
          'doconce grep (FIGURE | MOVIE | CODE) <file>[.do.txt]')


def grep():
    if len(sys.argv) < 3:
        _usage_grep()
        sys.exit(0)

    file_tp = sys.argv[1]
    filenames = []
    for filename in sys.argv[2:]:
        if not filename.endswith('.do.txt'):
            filename += '.do.txt'
        if not os.path.isfile(filename):
            continue  # just drop non-existing files to avoid corrupt output
        f = open(filename, 'r')
        filestr = f.read()
        f.close()

        from .common import INLINE_TAGS
        if file_tp == 'FIGURE':
            pattern = INLINE_TAGS['figure']
            filenames += [filename for filename, dummy in
                          re.findall(pattern, filestr, re.MULTILINE)]
        elif file_tp == 'MOVIE':
            pattern = pattern = INLINE_TAGS['movie']
            filenames += [filename for filename, dummy in
                          re.findall(pattern, filestr, re.MULTILINE)]
        elif file_tp == 'CODE':
            pattern = '^@@@CODE +(.+?)\s+'
            filenames += re.findall(pattern, filestr, re.MULTILINE)
        else:
            print('*** error: cannot grep', file_tp, '(not implemented)')
    filenames = list(set(filenames))  # remove multiple filenames
    print(' '.join(filenames))


def _usage_capitalize():
    print('Usage:\n'
          'doconce capitalize [-d file_with_cap_words] <file>[.do.txt]\n'
          'list of capitalized words can also be in .dict4cap.txt\n'
          '(typically, Python, Unix, etc. must be capitalized)')


def capitalize():
    if len(sys.argv) >= 2 and sys.argv[1] == '-d':
        dictionary = [sys.argv[2]]
        del sys.argv[1:3]
    else:
        if os.path.isfile('.dict4cap.txt'):
            dictionary = '.dict4cap.txt'
        else:
            dictionary = ''

    if len(sys.argv) < 2:
        _usage_capitalize()
        sys.exit(0)

    filename = sys.argv[1]

    cap_words = [
        'Celsius', 'Fahrenheit', 'Kelvin',
        'Fahrenheit-Celsius',
        'Newton', 'Gauss', "Gauss'",
        'Legendre', 'Lagrange', 'Markov',
        'Laguerre', 'Taylor', 'Einstein',
        'Maxwell', 'Euler', 'Gaussian', 'Eulerian', 'Lagrangian',
        'Poisson',
        'Heaviside', 'MATLAB', 'Matlab',
        'Trapezoidal', "Simpson's", 'Monte', 'Carlo',
        'ODE', 'PDE', 'Adams-Bashforth', 'Runge-Kutta', 'SIR', 'SIZR', 'SIRV',
        'Python', 'IPython', 'Cython', 'Idle', 'NumPy', 'SciPy', 'SymPy',
        'Matplotlib', 'None', '$N$',
        'Fortran', 'MATLAB', 'SWIG', 'Perl', 'Ruby', 'CPU',
        'DNA', 'British', 'American', 'Internet', # 'Web',
        'HTML', 'MSWord', 'OpenOffice',
        'StringFunction', 'Vec2D', 'Vec3D', 'SciTools', 'Easyviz',
        'Pysketcher',
        ]
    # This functionality is not well implemented so instead of finding
    # a perfect solution we fix well-known special cases.
    # A better software solution would be to read a user-made file
    # with fixes. The fixes below are special for a book project...
    cap_words_fix = [
        ('exer. ref{', 'Exer. ref{'),
        ('exer. (_', 'Exer. (_'),  # latex2doconce external reference
        ('subsection. ref{', 'Subsection. ref{'),
        ('section. ref{', 'Section. ref{'),
        ('chapter. ref{', 'Chapter ref{'),
        ('Python library reference', 'Python Library Reference'),
        # Cannot have C and C++ as a special word since an equation with c
        # will then get capital C...try to repair these cases:
        (' c code', ' C code'),
        (' c program', ' C program'),
        (' c++ ', ' C++ '),
        (' 1d ', ' 1D '),
        (' 2d ', ' 2D '),
        (' 3d ', ' 3D '),
        ('vec2d', 'Vec2D'),
        ('vec3d', 'Vec3D'),
        ('hello, world!', 'Hello, World!'),
        ('hello world', 'Hello World'),
        ('mac os x', 'Mac OS X'),
        ('midpoint integration', 'Midpoint integration'),
        ('midpoint rule', 'Midpoint rule'),
        ('trapozoidal integration', 'Trapozoidal integration'),
        ('trapozoidal rule', 'Trapozoidal rule'),
        ('world wide web', 'World Wide Web'),
        ('cODE', 'code'),
        ('on windows', 'on Windows'),
        ('in windows', 'in Windows'),
        ('under windows', 'under Windows'),
        ('on mac', 'on Mac'),
        ('in mac', 'in Mac'),
        ('under mac', 'under Mac'),
        ('a mac', 'a Mac'),
        ("python's", "Python's"),
        ("forward Euler", "Forward Euler"),
        ("backward Euler", "Backward Euler"),
        ("crank-nicolson", "Crank-Nicolson"),
        ("adams-bashforth", "Adams-Bashforth"),
        ('runge-kutta', 'Runge-Kutta'),
        ]
    for name in 'Newton', 'Lagrange', 'Einstein', 'Poisson', 'Taylor', 'Gibb', \
            'Heun', :
        genetive = "'s"
        cap_words_fix.append((name.lower()+genetive, name+genetive))

    if dictionary:
        f = open(dictionary, 'a')
        cap_words += f.read().split()

    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    shutil.copy(filename, filename + '.old~~')

    filestr, old2new = _capitalize(filestr, cap_words, cap_words_fix)

    f = open(filename, 'w')
    f.write(filestr)
    f.close()
    for old, new in old2new:
        if old != new:
            print(old)
            print(new)
            print()


def _capitalize(filestr, cap_words, cap_words_fix):
    pattern1 = r'^\s*(={3,9})(.+?)(={3,9})'  # sections
    pattern2 = r'^__(.+?[.:?;!])__'       # paragraphs

    sections   = re.findall(pattern1, filestr, flags=re.MULTILINE)
    paragraphs = re.findall(pattern2, filestr, flags=re.MULTILINE)
    orig_titles1 = [t.strip() for s1, t, s2 in sections]
    orig_equals1 = [s1 for s1, t, s2 in sections]
    orig_titles2 = [t.strip() for t in paragraphs]
    orig_headings1 = [s1 + t + s2 for s1, t, s2 in sections]
    orig_headings2 = ['__' + t + '__' for t
                      in re.findall(pattern2, filestr, flags=re.MULTILINE)]

    def capitalize_titles(orig_titles, cap_words):
        cap_words_lower = [s.lower() for s in cap_words]
        new_titles = []
        for title in orig_titles:

            # Exercises, problems, are exceptions (view title as what
            # comes after the initial word)
            word0 = title.split()[0]
            if word0 in ['Exercise:', 'Problem:', 'Project:', 'Example:',
                         '{Exercise}:', '{Problem}:', '{Project}:', '{Example}:',]:
                title = title.replace(word0, '').strip()
                new_title = word0 + ' ' + title.capitalize()
            else:
                new_title = title.capitalize()

            words = new_title.split()
            # Handle hyphens
            old_words = words[:]
            for word in old_words:
                if '-' in word:
                    words.remove(word)
                    words += word.split('-')
                if word[0] == '`' and word[-1] == '`':
                    if word in words:
                        words.remove(word)

            for word in words:
                # Strip away non-alphabetic characters
                word_stripped = ''.join([w for w in list(word)
                                         if w.isalpha()])
                if word_stripped.lower() in cap_words_lower:
                    try:
                        i = cap_words_lower.index(word_stripped.lower())
                        new_word = word.replace(word_stripped, cap_words[i])
                        new_title = new_title.replace(word, new_word)
                    except ValueError:
                        pass

            for wrong_words, fixed_words in cap_words_fix:
                if wrong_words in new_title:
                    new_title = new_title.replace(wrong_words, fixed_words)
            new_titles.append(new_title)
        return new_titles

    new_titles1 = capitalize_titles(orig_titles1, cap_words)
    new_titles2 = capitalize_titles(orig_titles2, cap_words)

    old2new = []
    for new_title, orig_title, orig_heading, s1 in \
            zip(new_titles1, orig_titles1, orig_headings1, orig_equals1):
        new_heading = '%s %s %s' % (s1, new_title, s1)
        filestr = filestr.replace(orig_heading, new_heading)
        old2new.append((orig_title, new_title))
    for new_title, orig_title, orig_heading in \
            zip(new_titles2, orig_titles2, orig_headings2):
        new_heading = '__%s__' % new_title
        filestr = filestr.replace(orig_heading, new_heading)
        old2new.append((orig_title, new_title))
    return filestr, old2new


def _usage_md2html():
    print('Usage:\n'
          'doconce md2html <file>[.do.txt]\n\n'
          'Make HTML from pandoc-exteded Markdown (.html file from .md pandoc file)\n'
          'The purpose is to fix the HTML code with full MathJax support.')


def md2html():
    """
    Translate a .md file to .html that the HTML code gets full LaTeX
    math support.
    The .md file is fixed, then ``pandoc -f markdown -t html`` is run
    to create HTML from Markdown, then the HTML code is fixed.
    """
    if len(sys.argv) < 2:
        _usage_md2html()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.md'):
        if os.path.isfile(filename + '.md'):
            filename += '.md'
        else:
            raise IOError('no file %s.md' % filename)
    # First make sure \eqref survives the pandoc translation
    f = open(filename ,'r'); text = f.read(); f.close()
    text = text.replace('\\eqref{', 'EQREF{')
    f = open(filename ,'w'); f.write(text); f.close()

    # Translate to HTML and fix the MathJax things
    basename = filename[:-3]
    cmd = 'pandoc -f markdown -t html --mathjax -s -o %s.html %s.md' % \
          (basename, basename)
    print(cmd)
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('could not run\n', cmd)
        print(output)
        sys.exit(1)
    f = open('%s.html' % basename, 'r')
    text = f.read()
    f.close()
    # Add extra info
    pattern = r'(<script src=".+?MathJax\.js)'
    replacement = r"""
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  TeX: {
     equationNumbers: {  autoNumber: "AMS"  },
     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js", "color.js"]
  }
});
</script>
\g<1>"""
    # Nothing is done with --siunits option and siunitx package...
    text = re.sub(pattern, replacement, text)
    text = text.replace('EQREF{', '\\eqref{')

    f = open('%s.html' % basename, 'w')
    f.write(text)
    f.close()
    print('output in %s.html' % basename)


def _usage_md2latex():
    print('Usage:\n'
          'doconce md2latex <file>[.do.txt]\n\n'
          'Make LaTeX from pandoc-exteded Markdown (.tex file from .md file).\n'
          'The purpose is to fix the LaTeX code so it compiles.')


def md2latex():
    """
    Read the .md file and fix equation syntax such that LaTeX
    generated from Markdown (via pandoc) compiles.
    """
    if len(sys.argv) < 2:
        _usage_md2latex()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.md'):
        if os.path.isfile(filename + '.md'):
            filename += '.md'
        else:
            raise IOError('no file %s.md' % filename)

    # Remove $$ around begin-end structures
    basename = filename[:-3]
    cmd = 'pandoc -f markdown -t latex -s -o %s.tex %s.md' % \
          (basename, basename)
    print(cmd)
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('could not run\n', cmd)
        print(e.output)
        sys.exit(1)
    f = open('%s.tex' % basename, 'r')
    text = f.read()
    f.close()
    pattern = r'\$\$(\s*\\begin\{.+?\\end\{.+?)\$\$'
    text = re.sub(pattern, r'\g<1>', text)
    f = open('%s.tex' % basename, 'w')
    f.write(text)
    f.close()
    print('output in %s.tex' % basename)


# ----------------------- functions for insertdocstr -----------------------

def insertdocstr():
    """
    This scripts first finds all .do.txt (DocOnce source code) files in a
    directory tree and transforms these to a format given as command-line
    argument to the present script. The transformed file has the extension
    .dst.txt (dst for Doc STring), regardless of the format.

    In the next phase, all .p.py files (Python files that need preprocessing)
    are visited, and for each file the C-like preprocessor (preprocess.py)
    is run on the file to include .dst.txt files into doc strings.
    The result is an ordinary .py file.

    Example:
    A file basename.p.py has a module doc string which looks like
    '''
    # #include "docstrings/doc1.dst.txt"
    '''

    In the subdirectory docstrings we have the file doc1.do.txt, which
    contains the documentation in DocOnce format. The current script
    detects this file, transforms it to be desired format, say Epytext.
    That action results in doc1.epytext. This file is then renamed to
    doc1.dst.txt.

    In the next step, files of the form basename.p.py is visisted, the
    preprocess program is run, and the docstrings/doc1.dst.txt file is
    inserted in the doc string. One can run with Epytext format, which is
    suitable for running Epydoc on the files afterwards, then run with
    Sphinx, and finally re-run with "plain" format such that only quite
    raw plain text appears in the final basename.py file (this is suitable
    for Pydoc, for instance).

    Usage:
    doconce insertdocstr format root [preprocessor options]
    """

    try:
        format = sys.argv[1]
        root = sys.argv[2]
    except:
        print('Usage:\n'
              'doconce insertdocstr format root [preprocessor options]')
        sys.exit(1)

    global doconce_program
    if os.path.isfile(os.path.join('bin', 'doconce')):
        doconce_program = 'python ' + os.path.join(os.getcwd(), 'bin', 'doconce')
    else:
        doconce_program = 'doconce'  # must be found somewhere in PATH
    # alternative: use sys.argv[3] argument to tell where to find doconce
    # can then run "bin/doconce insertdocstr bin" from setup.py

    print('\n----- doconce insertdocstr %s %s\nFind and transform doconce files (.do.txt) ...' % (format, root))
    arg = format
    os.path.walk(root, _walker_doconce, arg)

    print('Find and preprocess .p.py files (insert doc strings etc.)...')
    arg = ' '.join(sys.argv[3:])  # options for preprocessor
    os.path.walk(root, _walker_include, arg)
    print('----- end of doconce insertdocstr -----\n')



# not used:
def _preprocess_all_files(rootdir, options=''):
    """
    Run preprocess on all files of the form basename.p.ext
    in the directory with root rootdir. The output of each
    preprocess run is directed to basename.ext.
    """
    def _treat_a_dir(arg, d, files):
        for f in files:
            path = os.path.join(d, f)
            if '.p.' in f and not '.svn' in f:
                basename_dotp, ext = os.path.splitext(f)
                basename, dotp = os.path.splitext(basename_dotp)
                outfilename = basename + ext
                outpath = os.path.join(d, outfilename)
                cmd = 'preprocess %s %s > %s' % (options, path, outpath)
                system(cmd)

    os.path.walk(rootdir, _treat_a_dir, None)


def _run_doconce(filename_doconce, format):
    """
    Run doconce format filename_doconce.
    The result is a file with extension .dst.txt (same basename
    as filename_doconce).
    """
    if filename_doconce.startswith('__'):
        # old preprocessed file from aborted doconce execution
        print('skipped', filename_doconce)
        return

    global doconce_program # set elsewhere
    cmd = '%s format %s %s' % (doconce_program, format, filename_doconce)
    print('run', cmd)
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise OSError('Could not run\n%s\nin %s\n%s\n\n\n' %
                      (cmd, os.getcwd(), e.output))
    out_filename = output.split()[-1]
    root, ext = os.path.splitext(out_filename)
    new_filename = root + '.dst.txt'
    os.rename(out_filename, new_filename)
    print('(renamed %s to %s for possible inclusion in doc strings)\n' % (out_filename, new_filename))


def _walker_doconce(arg, dir, files):
    format = arg
    # we move to the dir:
    origdir = os.getcwd()
    os.chdir(dir)
    for f in files:
        if f[-7:] == '.do.txt':
            _run_doconce(f, format)
    os.chdir(origdir)


def _run_preprocess4includes(filename_dotp_py, options=''):
    pyfile = filename_dotp_py[:-5] + '.py'
    cmd = 'preprocess %s %s > %s' % (options, filename_dotp_py, pyfile)
    print('run', cmd)
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise OSError('Could not run\n%s\nin %s\n%s\n\n\n' % \
              (cmd, os.getcwd(), e.output))


def _walker_include(arg, dir, files):
    options = arg
    # we move to the dir:
    origdir = os.getcwd()
    os.chdir(dir)
    for f in files:
        if f[-5:] == '.p.py':
            _run_preprocess4includes(f, options)
    os.chdir(origdir)

# ----------------------------------------------------------------------


def which(program):
    """
    Mimic the Unix ``which`` command and return the full path of
    a program whose name is in the `program` argument.
    Return None if the program is not found in any of the
    directories in the user's ``PATH`` variable.
    """
    pathdirs = os.environ['PATH'].split(os.pathsep)
    program_path = None
    for d in pathdirs:
        if os.path.isdir(d):
            if os.path.isfile(os.path.join(d, program)):
                program_path = d
                break
    return program_path


# subst_* below must be global because local functions in _latex2doconce
# disable the use of the important exec(f.read()) statement.


def subst_author_latex2doconce(m):
    author_str = m.group('subst')
    authors = author_str.split(r'\and')
    institutions = ['']*len(authors)
    # footnotes with institutions?
    if r'\footnote{' in author_str:
        for i, author in enumerate(authors):
            if r'\footnote{' in author:
                pattern = r'\footnote\{(.+?\}'
                m2 = re.search(pattern, author)
                if m2:
                    institutions[i] = m2.group(1).strip()
                    authors[i] = re.sub(pattern, '', authors[i])
    authors = ['AUTHOR: %s' % a.strip() for a in authors]
    for i in range(len(authors)):
        if institutions[i] != '':
            authors[i] += ' at ' + institutions[i]
    return '\n'.join(authors)


def subst_paragraph_latex2doconce(m):
    title = m.group(1)
    ending = m.group(2)
    if ending != '.':
        title += ending
    return '=== %s ===\n' % title

global footnote_counter
footnote_counter = 0


def subst_footnote_latex2doconce(m):
    text = m.group(1)
    global footnote_counter
    footnote_counter += 1
    return '[^footnote%d][^footnote%d]: %s' % \
           (footnote_counter, footnote_counter, text)


def _latex2doconce(filestr):
    """Run latex to doconce transformations on filestr."""
    user_subst = []
    user_replace = []
    fixfile = 'latex2doconce_fix.py'
    if os.path.isfile(fixfile):
        # fixfile must contain subst and replace, to be
        # applied _after_ the general subst and replace below
        """
        # re.sub substitutions
        subst = [
        (r'^\be\s+', '!bt\n\\begin{equation}\n', re.MULTILINE),
        (from_, to_, flags),
        ]
        # str.replace replacements
        replace = []
        """
        subst, replace = None, None
        f = open(fixfile)
        exec(f.read())
        f.close()
        if subst and replace:
            user_subst = subst
            user_replace = replace
        else:
            print(fixfile, 'does not contain subst and replace lists or has errors')
            sys.exit(1)

    # cf. doconce.latex.fix_latex_command_regex to see how important
    # it is to quote the backslash correctly for matching, substitution
    # and output strings when using re.sub for latex text!


    subst = [
        # hpl specific things:
        # \ep is difficult to replace automatically...
        #(r'\\ep(\\|\s+|\n)', r'\thinspace . \g<1>*'), # gives tab hinspace .
        #(r'^\ep\n', r'\\thinspace .\n', re.MULTILINE),
        #(r'\ep\n', r' \\thinspace .\n'),
        #(r'\ep\s*\\\]', r' \\thinspace . \]'),
        #(r'\ep\s*\\e', r' \\thinspace . \e'),
        #(r'\\thinspace', 'thinspace'),
        (r'\\code\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\\emp\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\\codett\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\{\\rm\\texttt\{(?P<subst>[^}]+)\}\}', r'`\g<subst>`'),
        (r'\\idx\{(?P<subst>.+?)\}', r'idx{`\g<subst>`}'),
        (r'\\idxf\{(?P<subst>.+?)\}', r'idx{`\g<subst>` function}'),
        (r'\\idxs\{(?P<subst>.+?)\}', r'idx{`\g<subst>` script}'),
        (r'\\idxp\{(?P<subst>.+?)\}', r'idx{`\g<subst>` program}'),
        (r'\\idxc\{(?P<subst>.+?)\}', r'idx{`\g<subst>` class}'),
        (r'\\idxm\{(?P<subst>.+?)\}', r'idx{`\g<subst>` module}'),
        (r'\\idxnumpy\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (from `numpy`)}'),
        (r'\\idxnumpyr\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (from `numpy.random`)}'),
        (r'\\idxst\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (from `scitools`)}'),
        (r'\\idxfn\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (FEniCS)}'),
        (r'\\idxe\{(?P<attr>.+?)\}\{(?P<obj>.+?)\}', r'idx{`\g<attr>` \g<obj>}'),
        (r'\\refeq\{(?P<subst>.+?)\}', r'(ref{\g<subst>})'),
        (r'^\\bpy\s+', r'\bipy' + '\n', re.MULTILINE),
        (r'^\\epy\s+', r'\eipy' + '\n', re.MULTILINE),
        (r'\\footnote\{(.+?)\}', subst_footnote_latex2doconce, re.DOTALL),
        # general latex constructions
        # (comments are removed line by line below)
        (r'\\author\{(?P<subst>.+)\}', subst_author_latex2doconce),
        (r'\\title\{(?P<subst>.+)\}', r'TITLE: \g<subst>'),
        # First one-line headings without short title
        (r'\\chapter\*?\{(?P<subst>.+)\}', r'========= \g<subst> ========='),
        (r'\\section\*?\{(?P<subst>.+)\}', r'======= \g<subst> ======='),
        (r'\\subsection\*?\{(?P<subst>.+)\}', r'===== \g<subst> ====='),
        (r'\\subsubsection\*?\{(?P<subst>.+)\}', r'=== \g<subst> ==='),
        (r'\\paragraph\{(?P<subst>.+?)\}', r'__\g<subst>__'),  # modified later
        # Multiple-line headings
        (r'\\chapter\*?\{(?P<subst>.+?)\}', r'========= \g<subst> =========', re.DOTALL),
        (r'\\section\*?\{(?P<subst>.+?)\}', r'======= \g<subst> =======', re.DOTALL),
        (r'\\subsection\*?\{(?P<subst>.+?)\}', r'===== \g<subst> =====', re.DOTALL),
        (r'\\subsubsection\*?\{(?P<subst>.+?)\}', r'=== \g<subst> ===', re.DOTALL),
        # Multiple-line headings with short title
        (r'\\chapter\*?\[.+?\]\{(?P<subst>.+?)\}', r'========= \g<subst> =========', re.DOTALL),
        (r'\\section\*?\[.+?\]\{(?P<subst>.+?)\}', r'======= \g<subst> =======', re.DOTALL),
        (r'\\subsection\*?\[.+?\]\{(?P<subst>.+?)\}', r'===== \g<subst> =====', re.DOTALL),
        (r'\\subsubsection\*?\[.+?\]\{(?P<subst>.+?)\}', r'=== \g<subst> ===', re.DOTALL),
        (r'\\bf\{(?P<subst>.+?)\}', r'_\g<subst>_'),
        (r'\\emph\{(?P<subst>.+?)\}', r'*\g<subst>*'),
        (r'\\texttt\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\\textit\{(?P<subst>[^}]+)\}', r'*\g<subst>*'),
        (r'\{\\em\s+(?P<subst>.+?)\}', r'*\g<subst>*'),
        (r'\{\\bf\s+(?P<subst>.+?)\}', r'_\g<subst>_'),
        (r'\{\\it\s+(?P<subst>.+?)\}', r'*\g<subst>*'),
        (r'\\textbf\{(?P<subst>.+?)\}', r'_\g<subst>_'),
        (r'\\newpage', ''),
        (r'\\clearpage', ''),
        (r'\\bigskip', ''),
        (r'\\medskip', ''),
        (r'\\eqref\{(?P<subst>.+?)\}', r'(ref{\g<subst>})'),
        (r'(\S)\\label\{', r'\g<1> \\label{'),
        (r'(\S)\\idx(.?)\{', r'\g<1> \\idx\g<2>{'),
        (r'(\S)\\index\{', r'\g<1> \\index{'),
        (r'\\idxfont\{(.+?)\}', r'`\g<1>`'),
        (r'\\index\{(?P<sortkey>.+?)@(?P<index>.+?)\}', r'idx{\g<index>}'),
        (r'\\index\{(?P<subst>.+?)\}', r'idx{\g<subst>}'),
        (r'\\href\{(?P<url>.+?)\}\{(?P<text>.+?)\}', r'"\g<2>": "\g<1>"'),
        (r'\\input\{(?P<subst>.+?)\}', r'# #include "\g<subst>.do.txt"'),
        ] + user_subst
    try:
        for item in subst:
            if len(item) == 2:
                pattern, replacement = item
                cpattern = re.compile(pattern)
            elif len(item) == 3:
                pattern, replacement, flags = item
                cpattern = re.compile(pattern, flags)
            if cpattern.search(filestr):
                filestr = cpattern.sub(replacement, filestr)
            else:
                pass
    except Exception as e:
        print('pattern: %s, replacement: %s' % (pattern, replacement))
        raise e

    replace = [
        # make sure \beqan comes before \beqa and \beq in replacements...
        (r'\begin{document}', ''),
        (r'\end{document}', ''),
        (r'\maketitle', ''),
        (r'\[', r'\begin{equation*}'),
        (r'\]', r'\end{equation*}'),
        (r'\beqan', r'\begin{eqnarray*}'),
        (r'\eeqan', r'\end{eqnarray*}'),
        (r'\beqa', r'\begin{eqnarray}'),
        (r'\eeqa', r'\end{eqnarray}'),
        (r'\beq', r'\begin{equation}'),
        (r'\eeq', r'\end{equation}'),
        (r'\ben', r'\begin{enumerate}'),
        (r'\een', r'\end{enumerate}'),
        (r'\bit', r'\begin{itemize}'),
        (r'\eit', r'\end{itemize}'),
        (r'\para{', r'\paragraph{'),
        (r'\refeq', r'\eqref'),
        # dangerous double derivative: ("''", '"'),
        # should be corrected manually ("``", '"'),
        ("Chapter~", "Chapter "),
        ("Section~", "Section "),
        ("Appendix~", "Appendix "),
        ("Appendices~", "Appendices "),
        ("Figure~", "Figure "),
        ("Table~", "Table "),
        ("Chapters~", "Chapters "),
        ("Sections~", "Sections "),
        ("Figures~", "Figures "),
        ("Tables~", "Tables "),
        ("Chap.~", "Chapter "),
        ("Sec.~", "Section "),
        ("App.~", "Appendix "),
        ("Fig.~", "Figure "),
        ("Tab.~", "Table "),
        (".~", ". "),
        ('@@@CMD ', '@@@OSCMD '),

        ] + user_replace

    # Pure string replacements:
    for from_, to_ in replace:
        if from_ in filestr:
            if filestr != filestr.replace(from_, to_):
                filestr = filestr.replace(from_, to_)

    # Add extra line after label after section
    filestr = re.sub(r'(==={3,9}\n\\label\{.+?\}) *\n(\w)',
                     r'\g<1>\n\n\g<2>', filestr)

    # problems (cannot understand this old code...):
    """
    problems = [
        r'\Sindex\{',
        r'\Sidx.?\{',
        r'\Slabel\{',
        ]
    for problem in problems:
        p = re.findall(problem, filestr)
        if len(p) > 0:
            print('PROBLEM:', problem, '\n', p)
    """

    math_envirs = 'equation', 'eqnarray', 'eqnarray*', 'align', r'align\*', r'equation\*'
    # Avoid picking up equations in comment lines
    math_starters = [r'^([^%%\n]*)(\\begin\{%s\})' % envir for envir in math_envirs]
    math_starters.append(r'^([^%%\n]*)(\\\[)')
    math_enders = [r'^([^%%\n]*)(\\end\{%s\})' % envir for envir in math_envirs]
    math_enders.append(r'^([^%%\n]*)(\\\])')

    # add !bt before and !et after math environments:
    for e in math_starters:
        filestr = re.sub(e, r'\g<1>\n!bt\n\g<2>', filestr, flags=re.MULTILINE)
    for e in math_enders:
        filestr = re.sub(e, r'\g<1>\g<2>\n!et',  filestr, flags=re.MULTILINE)

    # Make sure there is a line after heading (and label)
    filestr = re.sub(r'(===[A-Za-z0-9 ]+?={3,9})\s+(\\label\{.+?\})\s+([A-Za-z ])', r'\g<1>\n\g<2>\n\n\g<3>', filestr)
    filestr = re.sub('(===[A-Za-z0-9 ]+?={3,9})\s+([A-Za-z ])', r'\g<1>\n\n\g<2>', filestr)

    # minted
    pattern = r'\\begin\{minted}\[?.*\]?{(.+?)\}'
    minted2bc = dict(python='py', cython='cy', fortran='f',
                     c='c', bash='sh', rst='rst',
                     matlab='m', perl='pl',
                     latex='latex', html='html', js='js',
                     xml='xml', ruby='rb')
    minted2bc['c++'] = 'cpp'
    def subst_minted_latex2doconce(m):
        lang = m.group(1)
        if lang in minted2bc:
            return '!bc ' + minted2bc[lang]
        else:
            return '!bc'
    filestr = re.sub(pattern, subst_minted_latex2doconce, filestr)
    filestr = filestr.replace('\\end{minted}', '!ec')
    pattern = r'\\begin\{Verbatim}\[?.*\]?{(.+?)\}'
    filestr = re.sub(pattern, '!bc', filestr)
    filestr = filestr.replace('\\end{Verbatim}', '!ec')
    filestr = filestr.replace('\\begin{verbatim}', '!bc')
    filestr = filestr.replace('\\end{verbatim}', '!ec')
    for lang in minted2bc:
        begin_pattern = r'\begin{%s}' % lang
        end_pattern = r'\end{%s}' % lang
        filestr = filestr.replace(begin_pattern, '!bc ' + minted2bc[lang])
        filestr = filestr.replace(end_pattern, '!ec')

    # ptex2tex code environments:
    code_envirs = ['ccq', 'cod', 'pro', 'ccl', 'cc', 'sys',
                   'dsni', 'sni', 'slin', 'ipy', 'rpy',
                   'pyshell', 'plin', 'ver',
                   'warn', 'rule', 'summ',
                   'dat', 'txt'] # sequence important for replace!
    for language in 'py', 'f', 'c', 'cpp', 'sh', 'pl', 'm':
        for tp in 'cod', 'pro':
            code_envirs.append(language + tp)

    for e in code_envirs:
        s = r'\b%s' % e
        filestr = filestr.replace(s, '\n!bc ' + e)
        s = r'\e%s' % e
        filestr = filestr.replace(s, '!ec')

    filestr = filestr.replace('bc rpy', 'bc sys')

    # eqnarray -> align
    filestr = filestr.replace(r'{eqnarray', '{align')
    filestr = re.sub(r'&(\s*)=(\s*)&', '&\g<1>=\g<2>', filestr)
    filestr = re.sub(r'&(\s*)\\approx(\s*)&', '&\g<1>\\\\approx\g<2>', filestr)

    # \item alone on line: join with next line (indentation is fixed later)
    filestr = re.sub(r'\\item\s+(\w)', r'\\item \g<1>', filestr)

    # Make sure all items in lists are on one line so we do not run
    # into indentation problems (lookahead pattern makes this easy)
    pattern = r'(\\item\s+.+?)(?=\\item|\\end\{)'
    list_items = re.findall(pattern, filestr, flags=re.DOTALL)
    for item in list_items:
        filestr = filestr.replace(item, ' '.join(item.splitlines()) + '\n\n')

    # Find subfigures (problems)
    if filestr.count('\\subfigure{') > 0:
        print('\nPROBLEM: found \\subfigure{...} - should be changed (combine individual')
        print('      figure files into a single file; now subfigures are just ignored!)\n')

    # Figures: assumptions are that subfigure is not used and that the label
    # sits inside the caption. Also, width should be a fraction of
    # \linewidth.

    # figures with width spec: psfig, group1: filename, group2: width, group3: caption
    pattern = re.compile(r'\\begin{figure}.*?\\psfig\{.*?=([^,]+?),\s*width=(.+?)\\linewidth.*?\\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'FIGURE: [\g<1>, width=\g<2>] {{{{\g<3>}}}}', filestr)
    # note: cannot treat width=10cm, only width=0.8\linewidth
    # figures: psfig, group1: filename, group2: caption
    pattern = re.compile(r'\\begin{figure}.*?\\psfig\{.*?=([^,]+).*?\\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'FIGURE: [\g<1>, width=400] {{{{\g<2>}}}}', filestr)
    # figures: includegraphics, group1: width, group2: filename, group3: caption
    pattern = re.compile(r'\\begin{figure}.*?\\includegraphics\[width=(.+?)\\linewidth\]\{(.+?)\}.*?\\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'FIGURE: [\g<2>, width=400 frac=\g<1>] {{{{\g<3>}}}}', filestr)
    # includegraphics with other measures of width and caption after fig
    pattern = re.compile(r'\\begin{figure}.*?\\includegraphics\[(.+?)]\{(.+?)\}.*?\\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'# original latex figure with \g<1>\n\nFIGURE: [\g<2>, width=400 frac=1.0] {{{{\g<3>}}}}', filestr)
    # includegraphics with other measures of width and caption before fig
    pattern = re.compile(r'\\begin{figure}.*?\\caption\{(.*?)\}\\includegraphics\[(.+?)]\{(.+?)\}.*?\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'# original latex figure with \g<2>\n\nFIGURE: [\g<3>, width=400 frac=1.0] {{{{\g<1>}}}}', filestr)

    # Better method: grab all begin and end figures and analyze the complete
    # text between begin and end. That can handle comment lines in figures,
    # which now destroy the regex'es above since they will grab the
    # first image anyway.

    captions = re.findall(r'\{\{\{\{(.*?)\}\}\}\}', filestr, flags=re.DOTALL)
    for caption in captions:
        orig_caption = caption
        # Add label to end of caption
        pattern = r'(\\label\{.*?\})'
        m = re.search(pattern, caption)
        if m:
            label = m.group(1)
            caption = caption.replace(label, '')
            caption = caption.strip() + ' ' + label
        # Strip off comments
        lines = caption.splitlines()
        for i in range(len(lines)):
            if '%' in lines[i] and not r'\%' in lines[i]:
                lines[i] = lines[i].split('%')[0]
        # Make one line
        caption = ' '.join(lines)
        filestr = filestr.replace('{{{{%s}}}}' % orig_caption, caption)


    # Process lists, comment lines, @@@CODE lines, and other stuff
    inside_enumerate = False
    inside_itemize = False
    inside_code = False
    appendix = False
    lines = filestr.splitlines()
    for i in range(len(lines)):
        if lines[i].startswith('!bc'):
            inside_code = True
        if lines[i].startswith('!ec'):
            inside_code = False
        if (not inside_code) and lines[i].lstrip().startswith('%'):
            lines[i] = '# ' + lines[i].lstrip()[1:]
        if lines[i].startswith('@@@CODE'):
            # Translate ptex2tex CODE envir to doconce w/regex
            words = lines[i].split(' ')  # preserve whitespace!
            new_line = ' '.join(words[:2])  # command filename, no space in name
            if len(words) > 2:
                restline = ' '.join(words[2:])
                new_line += ' fromto: '
                if '@' in restline:
                    from_, to_ = restline.split('@')[:2]
                    new_line += re.escape(from_)  # regex in doconce
                    new_line += '@' + re.escape(to_)
                else:
                    new_line += re.escape(restline) + '@'
                new_line = new_line.replace(r'\ ', ' ').replace(r'\,', ',').replace(r'\:', ':')
            lines[i] = new_line

        # two types of lists (but not nested lists):
        if r'\begin{enumerate}' in lines[i] or r'\ben' in lines[i]:
            inside_enumerate = True
            lines[i] = ''
        if r'\begin{itemize}' in lines[i] or r'\bit' in lines[i]:
            inside_itemize = True
            lines[i] = ''
        if inside_enumerate or inside_itemize:
            if lines[i].lstrip().startswith(r'\item'):
                l = re.sub(r'\s*\\item\s*', '', lines[i]).strip()
                lines[i] = '  * ' + l
        if r'\end{enumerate}' in lines[i] or r'\een' in lines[i]:
            inside_enumerate = False
            lines[i] = ''
        if r'\end{itemize}' in lines[i] or r'\eit' in lines[i]:
            inside_itemize = False
            lines[i] = ''
        if re.search(r'^\s*\\appendix', lines[i]):
            appendix = True
        if appendix and 'section{' in lines[i] or 'section*{' in lines[i]:
            lines[i] = re.sub(r'section\*?\{(.+?)\}',
                              'section{Appendix: \g<1>}', lines[i])
        if r'\bibliography' in lines[i]:
            lines[i] = re.sub(r'\\bibliography\{(.+?)\}',
                              r'\n_Must run publish import on BibTeX file \g<1>!_\nBIBFILE: papers.pub\n',
                              lines[i])
            lines[i] = re.sub(r'\\bibliographystyle\{.+?\}', '', lines[i])



    # put all newcommands in a file (note: newcommands must occupy only one line!)
    newlines = []
    newcommands = []
    for line in lines:
        l = line.lstrip()
        if l.startswith('\\newcommand{'):
            newcommands.append(l)
        else:
            newlines.append(line)

    filestr = '\n'.join(newlines)
    if newcommands:
        newcommands_file = 'newcommands_keep.tex'
        nf = open(newcommands_file, 'w')
        nf.writelines(newcommands)
        nf.close()

    # Exercises of the following particular format
    pattern = re.compile(r'\\begin\{exercise\}\s*\\label\{(.*?)\}\s*\\exerentry\{(.*?)\}\s*$\s*(.+?)\\hfill\s*\$\\diamond\$\s*\\end\{exercise\}', re.DOTALL|re.MULTILINE)
    filestr = pattern.sub(r'===== Exercise: \g<2> =====\n\\label{\g<1>}\nfile=\n\n\g<3>\n', filestr)

    # Fix "Name of program file:" construction in exercises
    lines = filestr.splitlines()
    program_file = None
    for i in range(len(lines)-1, -1, -1):
        if 'Name of program file' in lines[i]:
            m = re.search(r'Name of program file:\s*`([^`]+?)`', lines[i])
            if m:
                program_file = m.group(1)
                lines[i] = ''
        if lines[i] == 'file=':
            if program_file is not None:
                lines[i] = 'file=' + program_file
                program_file = None
            else:
                # No "Name of program file" was found after last file=.
                # This exercise does not have a program file specified.
                lines[i] = ''
    filestr = '\n'.join(lines)

    # Check idx{} inside paragraphs
    lines = filestr.splitlines()
    last_blank_line = -1
    pattern = r'idx\{.+?\}'
    inside_code_or_math = False
    for i in range(len(lines)):
        if lines[i].startswith('!bc') or lines[i].startswith('!bt'):
            inside_code_or_math = True
        if lines[i].startswith('!ec') or lines[i].startswith('!et'):
            inside_code_or_math = False
        if lines[i].strip() == '' and not inside_code_or_math:
            last_blank_line = i
        if 'idx{' in lines[i] and i < len(lines)-1 \
               and lines[i+1].strip() != '':
            # idx on a line and next line is text
            line = re.sub(pattern, '', lines[i]).strip()
            idx = re.findall(pattern, lines[i])
            if line != '':
                # We have idx{} in the middle of a paragraph, try move
                lines[i] = line
            else:
                lines[i] = '# REMOVE (there was just a single idx{...} on this line)'
            lines[last_blank_line] = '\n' + ' '.join(idx) + \
                                     ' ' + lines[last_blank_line]

    # Tables are difficult: require manual editing?
    inside_table = False
    new_lines = []
    headings = []
    nhlines = 0
    align_headings = []
    for i in range(len(lines)):
        if 'begin{table}' in lines[i] or 'begin{tabular}' in lines[i]:
            inside_table = True
            table_lines = []
            if '{tabular}{' in lines[i]:
                align = lines[i].split('{tabular}{')[-1].split('}')[0]
                align = align.replace('|', '')
            else:
                align = None
        if inside_table:
            if '&' in lines[i]:
                line = lines[i].replace('\\\\', '').strip()
                if '\\hline' in line:
                    line = line.replace('\\hline', '')
                    nhlines += 1
                if '\\multicolumn{' in line:
                    m = re.findall(r'\\multicolumn\{\d+\}\{(.)\}\{(.+?)\}',
                                   line)
                    if m:
                        headings = [heading for align_char, heading in m]
                        align_headings = [align_char for align_char, heading in m]
                        line = line.split('&')
                        # Fill headings from right
                        for j in range(len(line)):
                            line[j] = ''
                        for j, h in enumerate(reversed(headings)):
                            line[len(line)-1-j] = h
                        line = '&'.join(line)
                table_lines.append(line)
            else:
                # \hline, end{table, caption
                pass
        else:
            new_lines.append(lines[i])

        if inside_table and ('end{table}' in lines[i] or 'end{tabular}' in lines[i]):
            inside_table = False
            if table_lines:
                max_column_width = 0
                num_columns = 0
                for j in range(len(table_lines)):
                    columns = [s.strip()
                               for s in table_lines[j].split('&')]
                    max_column_width = max([max_column_width] + \
                                           [len(c) for c in columns])
                    num_columns = max(num_columns, len(columns))
                    table_lines[j] = columns
                max_column_width += 2   # add space before/after widest column
                # Construct doconce table
                # (if the formatting gets wrong, see csv2table, that
                # formatting works well)
                width = max_column_width*num_columns + num_columns+1
                separator0 = '|' + '-'*(width-2) + '|'
                separator1 = separator0
                separator2 = separator0
                if align_headings:
                    # Insert align chars for header from the right
                    # (sometimes 1st column may have no header)
                    s = list(separator1)
                    for j in range(len(align_headings)):
                        s[len(s)-1-old_div(max_column_width,2) - j*max_column_width] = align_headings[len(align_headings)-1-j]
                    separator1 = ''.join(s)
                if align is not None:
                    # As many chars in align as there are columns
                    s = list(separator2)
                    for j in range(len(align)):
                        try:
                            s[old_div(max_column_width,2) + j*max_column_width] = align[j]
                        except IndexError:
                            print('_ERROR:_ something went wrong when translating a table:')
                            for line in table_lines:
                                print(line)
                    separator2 = ''.join(s)
                column_format = ' %%-%ds ' % (max_column_width-2)
                for j in range(len(table_lines)):
                    table_lines[j] = [column_format % c for c in table_lines[j]]
                    table_lines[j] = '|' + '|'.join(table_lines[j]) + '|'
                table = '\n\n' + separator1 + '\n' + table_lines[0] + '\n' + \
                        separator2 + '\n' + '\n'.join(table_lines[1:]) + \
                        '\n' + separator0 + '\n\n'
                if new_lines:
                    new_lines[-1] += table
                else:
                    new_lines.append(table)

    filestr = '\n'.join(new_lines)
    filestr = re.sub(r'^# REMOVE \(there was.+$\s*', '', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'(idx\{.+?\})\s+([^i\n ])', r'\g<1>\n\n\g<2>', filestr)

    # Let paragraphs be subsubsections === ... ===
    pattern = r'__([A-Z].+?)([.?!:])__'
    filestr = re.sub(pattern, subst_paragraph_latex2doconce, filestr)

    # Find all labels and refs and notify about refs to external
    # labels
    problems = False
    labels = re.findall(r'label\{(.+?)\}', filestr)  # figs have label, not \label
    refs = re.findall(r'\\ref\{(.+?)\}', filestr)
    eqrefs = re.findall(r'\\eqref\{(.+?)\}', filestr)
    pagerefs = re.findall(r'\\pageref\{(.+?)\}', filestr)
    refs = refs + eqrefs + pagerefs
    '''
    for ref in refs:
        if ref not in labels:
            print('found reference but no label{%s}' % ref)
            problems = True
            # Attempt to do a generalized reference
            # (Make table of chapters, stand-alone docs and their labels - quite easy if associated chapters and their URLs are in a file!!!)
            filestr = filestr.replace(r'\ref{%s}' % ref,
                      r'(_PROBLEM: external ref_) ref{%s}' % ref)
    '''
    for ref in pagerefs:
        print('pageref{%s} should be rewritten' % ref)
        filestr = filestr.replace(r'\pageref{%s}' % ref,
            r'(_PROBLEM: pageref_) \pageref{%s}' % ref)
        problems = True

    print('\n## search for CHECK to see if auto editing was correct\n')
    if problems:
        print('\n## search for PROBLEM: to see need for manual adjustments\n\n\n')
    filestr = filestr.replace(r'\label{', 'label{')  # done above
    filestr = filestr.replace(r'\ref{', 'ref{')
    filestr = filestr.replace(r'\cite{', 'cite{')
    filestr = filestr.replace(r'\cite[', 'cite[')
    filestr = filestr.replace(r'\noindent', r"""# #if FORMAT in ("latex", "pdflatex")
\noindent
# #endif""")
    filestr = re.sub(r'\\vspace\{(.+?)\}', r"""# #if FORMAT in ("latex", "pdflatex")
\\vspace{\g<1>}
# #endif""", filestr)
    filestr = filestr.replace(r'\_', '_')
    filestr = filestr.replace(r' -- ', ' - ')
    filestr = filestr.replace(r'}--ref', '}-ref')
    filestr = filestr.replace(r'})--(ref', '})-(ref')
    filestr = filestr.replace(r'~', ' ')
    filestr = filestr.replace(r'\end{table}', '')

    # Treat footnotes
    # Footnote at the end of a sentence: enclose in parenthesis
    # (regex is not perfect so
    pattern = r'\\footnote\{([^}]+)\}\.'
    filestr = re.sub(pattern, '.( _CHECK: footnote_ at end of sentence placed in parenthesis) (\g<1>) ', filestr)
    # Without final . means footnote in the middle of a sentence
    pattern = r'\\footnote\{([^}]+)\}'
    filestr = re.sub(pattern, '( _PROBLEM: footnote_ in the middle of a sentence must be rewritten) (\g<1>)', filestr)

    # Check that !bc, !ec, !bt, !ec are at the beginning of the line
    for envir in 'c', 't':
        for tag in '!b', '!e':
            command = tag + envir
            pattern = r'^ +' + command
            filestr = re.sub(pattern, command, filestr, flags=re.MULTILINE)
    # Ensure a blank line before !bt and !bc for nicer layout
    # (easier with lookahead! - se below)
    #filestr = re.sub(r'([A-Za-z0-9,:?!; ])\n^!bt', r'\g<1>\n\n!bt',
    #                 filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'([A-Za-z0-9,:?!; ])\n^!bc', r'\g<1>\n\n!bc',
    #                 filestr, flags=re.MULTILINE)
    filestr = re.sub(r'\s+(?=^!bt|^!bc)', '\n\n', filestr, flags=re.MULTILINE)

    # Inline equations cause trouble
    filestr = re.sub(r'!et +([^\n])', '!et\n\g<1>', filestr)

    return filestr


def latex2doconce():
    """
    Apply transformations to a latex file to help translate the
    document into DocOnce format.

    Suggestions for preparations: avoid pageref, replace subfigures
    by files combined to a single file, avoid footnotes, index inside
    paragraphs, do not start code blocks with indentation, ...
    """
    print(('#ifdef LATEX2DOCONCE\n'
           'This is the result of the doconce latex2doconce program.\n'
           'The translation from LaTeX is just a helper. The text must\n'
           'be carefully examined! (Be prepared that some text might also\n'
           'be lost in the translation - in seldom cases.)\n'
           ))
    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    filestr = _latex2doconce(filestr)

    print('# #endif')   # end of intro with warnings etc.

    print(filestr)  # final output


def _usage_html2doconce():
    print('Usage:\n'
          'doconce html2doconce <file.do.txt>\n\n'
          'Apply transformations to an html file to help translate the document into DocOnce format.')


def html2doconce():
    """
    Apply transformations to an html file to help translate the
    document into DocOnce format.
    """
    if len(sys.argv) < 2:
        _usage_html2doconce()
        sys.exit(0)
    print('# #ifdef HTML2DOCONCE\n'
          'This is the result of the doconce htmldoconce program.\n'
          'The translation from HTML is just a helper. The text must\n'
          'be carefully examined! (Be prepared that some text might also\n'
          'be lost in the translation - in seldom cases.)\n\n')
    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    filestr = _html2doconce(filestr)
    print('# #endif')   # end of intro with warnings etc.
    print(filestr)  # final output to stdout


def _html2doconce(filestr):
    # All headings
    headings = {1: 7, 2: 5, 3: 3}
    def subst(m):
        border = '='*headings[int(m.group(1))]
        return border + ' ' + m.group(2) + ' ' + border + '\n'

    filestr = re.sub(r'<h(\d)>(.+?)</h\d>', subst, filestr)

    # Paragraphs
    filestr = re.sub(r'<p>\s*', '\n', filestr)
    # Various tags
    filestr = re.sub(r'<em>(.+?)</em>', '*\g<1>*', filestr, flags=re.DOTALL)
    filestr = re.sub(r'<b>(.+?)</b>', '_\g<1>_', filestr, flags=re.DOTALL)
    filestr = re.sub(r'<tt>(.+?)</tt>', '`\g<1>`', filestr, flags=re.DOTALL)
    filestr = re.sub(r'^\s*<title>(.+?)</title>', 'TITLE: \g<1>', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'<!--(.+?)-->', '#\g<1>', filestr, flags=re.DOTALL)
    filestr = re.sub(r'<a href="(.+?)">(.+?)</a>', '"\g<2>": "\g<1>"', filestr,
                     flags=re.DOTALL)
    filestr = re.sub(r'<img.*? src="(.+?)".*?>',
                     '\nFIGURE: [\g<1>, width=600 frac=1]\n', filestr,
                     flags=re.DOTALL)
    filestr = re.sub(r'\s*^<pre>\s*', '\n\n!bc cod\n', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'</pre>\s*', '!ec\n', filestr,
                     flags=re.MULTILINE)
    # <code>?
    filestr = re.sub(r'<ul>', '\n', filestr)
    filestr = re.sub(r'</ul>', '\n', filestr)
    # All lists become bullet lists, read line by line and use a stack
    # to improve this
    if '<ol>' in filestr:
        print('*** warning: enumerated lists become bullet lists')
    filestr = re.sub(r'<ol>', '\n', filestr)
    filestr = re.sub(r'</ol>', '\n', filestr)
    filestr = re.sub(r'<li>', '  * ', filestr)

    if '<table' in filestr:
        print('*** warning: html2doconce cannot handle tables.')
        print('    Recommendation: edit manually to CSV format and run')
        print('    doconce csv2table command to create table.')

    return filestr


def _usage_latex_dislikes():
    print('Usage:\n'
          'doconce latex_dislikes <file>\n\n'
          'check if there are problems with translating latex to doconce')


def latex_dislikes():
    """
    Report constructions in latex that will not translate to doconce
    format by latex2dococe and constructions that are not recommended
    for common other formats.

    Rules:

      * Collect all newcommands in a separate file, one definition
        per line (i.e., multi-line definitions are not allowed).
      * Do not use environments for algorithms.
      * Do not use environments for computer code in floating figures.
      * Tables will not be floating. Computer code, tables, algorithms,
        anything but figures, will be inline at the position where they
        are defined.
      * Do not use `description` lists.
    """
    if len(sys.argv) < 2:
        _usage_latex_dislikes()
        sys.exit(0)
    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    # Should we first run through latex2doconce? Many fixes there
    # simplifies things here...
    filestr = _latex2doconce(filestr)

    lines = filestr.splitlines()
    # Add line numbers
    for i in range(len(lines)):
        lines[i] = '%4d: ' % (i+1) + lines[i]
    lines = '\n'.join(lines).splitlines()

    # add line numbers to each line in the latex file
    # list matches (begin, commands) that are problematic
    # and report them for every line
    begin_likes = [
        'equation',
        'equation*',
        'align',
        'align*',
        'itemize',
        'enumerate',
        ]
    begin_ok = [
        'eqnarray',
        'eqnarray*',
        ]

    # dislikes: list of (regex, explanation)
    dislikes = [(r'%s~?\s*\\ref\{(.+?)\}' % tp,
                 r'use %s in \g<1>' % (tp[0].upper() + tp[1:]))
                for tp in
                ('section', 'chapter', 'appendix',
                 'sec.', 'chap.', 'app.')]
    dislikes += [
        (r'\\subfigure', 'Avoid \\subfigure, combine images to a single new image.'),
        (r'\\pageref', 'Avoid \\pageref entirely (page numbers do not make sense in most electronic formats).'),
        #(r'\\psfig\{', 'Avoid \\psfig, use \\includegraphics.'),
        (r'\\begin\{table\}', 'Tables are handled, but can easily become problematic. Test outcome of latex2doconce for this table, make it inline (only tabular) and of a form that easily translates to doconce.'),
        (r'\\begin\{tabular\}', 'Tables are handled, but can easily become problematic. Test outcome of latex2doconce for this tabular environment and adjust if necessary/possible.'),
        ]
    likes_commands = []

    for line in lines:
        if r'\begin{' in line:
            m = re.search(r'\\begin\{(.+?)\}', line)
            if m:
                envir = m.group(1)
                if envir in begin_likes:
                    pass # fine!
                elif envir in begin_ok:
                    print('\n'
                          r"Found \\begin{%s}, which can be handled, but it is recommended to avoid "
                          r"this construction." % envir)
                else:
                    print('\n'
                          r"Found \\begin{%s}, which will not carry over to DocOnce and other formats." % envir)
                    # Could have message here (begin_messages) that
                    # guide rewrites, e.g., lstlisting etc.
                print(line + '\n')

        for regex, message in dislikes:
            if re.search(regex, line):
                print(message)
                print(line + '\n')


def _usage_ipynb2doconce():
    print('Usage:\n'
          'doconce ipynb2doconce notebook.ipynb [--cell_delimiter]\n\n'
          'Translate IPython/Jupyter notebooks to doconce')


def ipynb2doconce():
    if len(sys.argv) < 2:
        _usage_ipynb2doconce()
        sys.exit(0)

    cell_delimiter = '--cell_delimiter' in sys.argv
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print('*** error: no file "%s" found' % filename)
        sys.exit(1)
    f = open(filename, 'r')
    jsonstring = f.read()
    f.close()
    # Turn json string into a NotebookNode object
    try:
        from nbformat.reader import reads
    except ImportError:
        # Try old style
        try:
            from IPython.nbformat.reader import reads
        except ImportError:
            print('*** error: cannot do import nbformat or IPython.nbformat')
            print('    make sure IPython notebook or Jupyter is installed correctly')
            _abort()

    nb = reads(jsonstring)
    # nb is dict-like with keys nbformat_minor, cells, nbformat, metadata

    # checking if we have modern enough ipynb format
    if nb['nbformat'] < 4:
        print(r"""*** error: ipynb file format is too old (at least v4 needed).
Please, upgrade format of your ipynb-file using Jupyter (just open and save
the file) and then try again.
""")
        _abort()

    dostr_list = []
    from .doconce import markdown2doconce
    cell_type_prev = None
    for cell in nb['cells']:
        if cell_delimiter and cell['cell_type'] != cell_type_prev:
            dostr_list.append('# ---------- %s cell\n' % cell['cell_type'])
        if cell['cell_type'] == 'markdown':
            s = markdown2doconce(cell['source'], ipynb_mode=True)
            if cell_type_prev == 'markdown':
                s += '\n'
            else:
                s += '\n\n'
        elif cell['cell_type'] == 'code':
            collapsed = cell['metadata'].get('collapsed', False) \
                        if cell['metadata'] else False
            source = cell['source']
            # Remove % (matplotlib) directives from source
            source = re.sub('^%.+\n', '', source, flags=re.MULTILINE).strip()
            s = '\n!bc py' + ('hid' if collapsed else 'cod') + '\n' + source + '\n!ec\n'

            # include LaTeX output if present
            for output in cell['outputs']:
                if 'data' in output:
                    if 'text/latex' in output['data']:
                        latex_output = output['data']['text/latex']
                        # replace leading and trailing '$$'
                        latex_output = "\\[%s\\]" % latex_output[2:-2]
                        s += "!bt\n" + latex_output + "\n!et\n"
        dostr_list.append(s)
        cell_type_prev = cell['cell_type']
    # Fix common problems
    # Missing blank line before heading
    dostr = "".join(dostr_list)
    dostr = re.sub('^!e([ct])\n===', r'!e\g<1>\n\n===', dostr, flags=re.MULTILINE)
    # Too many blanks before !bt and !bc
    dostr = re.sub(r'\n\n\n+!b([ct])', r'\n\n!b\g<1>', dostr)
    filename = filename.replace('.ipynb', '.do.txt')
    encoding = option("encoding=", default='')
    if encoding:
        import codecs
        f = codecs.open(filename, 'w', encoding)
    else:
        f = open(filename, 'w')
    f.write(dostr)
    f.close()
    print('output in', filename)


class DocOnceLexer(RegexLexer):
    """
    Lexer for DocOnce files.
    """

    name = 'DocOnce'
    aliases = ['doconce']
    filenames = ['*.do.txt']
    mimetypes = ['text/x-doconce']

    tokens = {
        'general': [
            (r'\#.*\n', Comment),
            (r'[{}]', Name.Builtin),
        ],
        'root': [
            (r' .*\n', Text),
            (r'\#.*\n', Comment),
            (r'idx', Name.Builtin),
            (r'label\{.+?\}', Name.Builtin),
            (r'TITLE:', Generic.Heading),
            (r'AUTHOR:', Generic.Heading),
            (r'DATE:', Generic.Heading),
            (r'TOC:', Generic.Heading),
            (r'FIGURE:', Name.Builtin),
            (r'MOVIE:', Name.Builtin),
            #(r'!.+\n', Generic.Strong),
            (r'!.+\n', Name.Builtin),
            (r'@@@CODE .*\n', Generic.Subheading),
            (r'=== .*\n', Generic.Subheading),
            (r'__.+?__\n', Generic.Subheading),
            (r'={3,9} .*\n', Generic.Heading),
            (r'\\\[', String.Backtick, 'displaymath'),
            (r'\\\(', String, 'inlinemath'),
            (r'\$\$', String.Backtick, 'displaymath'),
            (r'\$', String, 'inlinemath'),
            (r'\\([a-zA-Z]+|.)', Keyword, 'command'),
            (r'.*\n', Text),
        ],
        'math': [
            (r'\\([a-zA-Z]+|.)', Name.Variable),
            include('general'),
            (r'[0-9]+', Number),
            (r'[-=!+*/()\[\]]', Operator),
            (r'[^=!+*/()\[\]\\$%&_^{}0-9-]+', Name.Builtin),
        ],
        'inlinemath': [
            (r'\\\)', String, '#pop'),
            (r'\$', String, '#pop'),
            include('math'),
        ],
        'displaymath': [
            (r'\\\]', String, '#pop'),
            (r'\$\$', String, '#pop'),
            (r'\$', Name.Builtin),
            include('math'),
        ],
        'command': [
            (r'\[.*?\]', Name.Attribute),
            (r'\*', Keyword),
            (r'', Text, '#pop'),
        ],
    }

    def analyse_text(text):
        if text[:7] == 'Index: ':
            return True
        if text[:5] == 'diff ':
            return True
        if text[:4] == '--- ':
            return 0.9

class DocOnceLexer(RegexLexer):
    """
    Lexer for DocOnce files.

    Built this one from TexLexer and extended with DocOnce stuff.
    Difficult to get both to work
    """

    name = 'DocOnce'
    aliases = ['doconce']
    filenames = ['*.do.txt']
    mimetypes = ['text/x-doconce']

    tokens = {
        'general': [
            (r'#.*?\n', Comment),
            (r'[{}]', Name.Builtin),
            (r'[&_^]', Name.Builtin),
        ],
        'root': [
            (r'\\\[', String.Backtick, 'displaymath'),
            (r'\\\(', String, 'inlinemath'),
            (r'\$\$', String.Backtick, 'displaymath'),
            (r'\$', String, 'inlinemath'),
            (r'\\([a-zA-Z]+|.)', Keyword, 'command'),
            (r'!.+\n', Name.Builtin),
            (r'@@@CODE .*\n', Generic.Subheading),
            (r'=== .*\n', Generic.Subheading),
            (r'__.+?__\n', Generic.Subheading),
            (r'={3,9} .+? ={3,9}\n', Generic.Heading),
            (r'idx', Name.Builtin),
            (r'label\{.+?\}', Name.Builtin),
            (r'TITLE:', Generic.Heading),
            (r'AUTHOR:', Generic.Heading),
            (r'DATE:', Generic.Heading),
            (r'TOC:', Generic.Heading),
            (r'FIGURE:', Name.Builtin),
            (r'MOVIE:', Name.Builtin),
            include('general'),
            # these two are crucial - no 2 turns on latex math everywhere
            # but not doconce, no 1 does the other way around
            #(r'.*\n', Text),
            (r'[A-Za-z0-9 ]?\n', Text),  # makes latex stuff correct
            (r'[^\\$%&_^{}]+', Text),
            (r'.*\n', Text),
        ],
        'math': [
            (r'\\([a-zA-Z]+|.)', Name.Variable),
            include('general'),
            (r'[0-9]+', Number),
            (r'[-=!+*/()\[\]]', Operator),
            (r'[^=!+*/()\[\]\\$%&_^{}0-9-]+', Name.Builtin),
        ],
        'inlinemath': [
            (r'\\\)', String, '#pop'),
            (r'\$', String, '#pop'),
            include('math'),
        ],
        'displaymath': [
            (r'\\\]', String, '#pop'),
            (r'\$\$', String, '#pop'),
            (r'\$', Name.Builtin),
            include('math'),
        ],
        'command': [
            (r'\[.*?\]', Name.Attribute),
            (r'\*', Keyword),
            (r'', Text, '#pop'),
        ],
    }
    """
    tokens = {
        'general': [
            (r'\#.*\n', Comment),
            (r'[{}]', Name.Builtin),
        ],
        'root': [
            (r' .*\n', Text),
            #(r'!.+\n', Generic.Strong),
            (r'\\\[', String.Backtick, 'displaymath'),
            (r'\\\(', String, 'inlinemath'),
            (r'\$\$', String.Backtick, 'displaymath'),
            (r'\$', String, 'inlinemath'),
            (r'\\([a-zA-Z]+|.)', Keyword, 'command'),
        ],
        'math': [
            (r'\\([a-zA-Z]+|.)', Name.Variable),
            include('general'),
            (r'[0-9]+', Number),
            (r'[-=!+*/()\[\]]', Operator),
            (r'[^=!+*/()\[\]\\$%&_^{}0-9-]+', Name.Builtin),
        ],
        'inlinemath': [
            (r'\\\)', String, '#pop'),
            (r'\$', String, '#pop'),
            include('math'),
        ],
        'displaymath': [
            (r'\\\]', String, '#pop'),
            (r'\$\$', String, '#pop'),
            (r'\$', Name.Builtin),
            include('math'),
        ],
        'command': [
            (r'\[.*?\]', Name.Attribute),
            (r'\*', Keyword),
            (r'', Text, '#pop'),
        ],
    }
    """

    def analyse_text(text):
        return True

# The version below is the best one so far (still far from complete, not
# everything works as intended, so much experimentation is needed to
# extend it, but the result with doconce pygmentize mydoc perldoc looks
# fine). Need to understand more of how the lexers work to make
# further progress: look at DiffLexer, TexLexer, RstLexer, and other text
# lexers in /usr/local/lib/python2.7/dist-packages/Pygments-1.6dev_20131113-py2.7.egg/pygments/lexers/text.py.
# It seems that there is no markdown lexer on the net.

class DocOnceLexer(RegexLexer):
    """
    Lexer for DocOnce files.
    """

    name = 'DocOnce'
    aliases = ['doconce']
    filenames = ['*.do.txt']
    mimetypes = ['text/x-doconce']
    #flags = re.MULTILINE | re.DOTALL  # did not work

    tokens = {
        'root': [
            (r' .*\n', Text),
            (r'\#.*\n', Comment),
            (r'(label|ref|idx)\{.+?\}', Name.Builtin),
            (r'\\(begin|end)\{.+?\}', Name.Builtin),
            #(r'\$.+?\$', String),  # works only occasionally
            #(r'label\{.+?\}', Name.Builtin),
            #('idx', Keyword),
            (r'TITLE:.+\n', Generic.Heading),
            (r'AUTHOR:', Generic.Heading),
            (r'DATE:', Generic.Heading),
            (r'TOC:', Generic.Heading),
            (r'FIGURE:.*\n', Name.Builtin),
            (r'MOVIE:.*\n', Name.Builtin),
            (r'![a-z]+', Keyword),
            (r'@@@CODE .*\n', Generic.Subheading),
            (r'__.+?__', Generic.Subheading),
            (r'\|.+\|\n', String),  # tables
            (r'`.+?`', String.Backtick),  # does not work
            (r'".+?"', String),  # does not work
            (r'={3,9} .* ={3,9}\n', Generic.Heading),
            (r'.*\n', Text),
        ],
    }

    def analyse_text(text):
        True


def _usage_pygmentize():
    print('Usage:\n'
          'doconce pygmentize <file>[.do.txt] [pygments-style]')


def pygmentize():
    """
    Typeset a DocOnce file with pygmentize, using the DocOnceLexer
    class above.

    An alternative is to register the DocOnceLexer with Pygments.
    """
    if len(sys.argv) < 2:
        _usage_pygmentize()
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.do.txt'):
        filename += '.do.txt'
    try:
        pygm_style = sys.argv[2]
    except IndexError:
        pygm_style = 'default'

    f = open(filename, 'r');  text = f.read();  f.close()
    lexer = DocOnceLexer()
    formatter = HtmlFormatter(noclasses=True, style=pygm_style)
    text = highlight(text, lexer, formatter)
    f = open(filename + '.html', 'w');  f.write(text);  f.close()
    print('pygmentized doconce code written to %s.html' % filename)


def _usage_makefile():
    print('Usage:\n'
          'doconce makefile <file>[.do.txt] [html pdflatex latex sphinx gwiki pandoc ipynb deck reveal beamer ...]\n\n'
          'Example:\n'
          'doconce makefile <file>[.do.txt] html sphinx\n\n'
          'A script make.py is generated with the basic steps for running a\n'
          'spellcheck on .do.txt files followed by commands for producing\n'
          'output in various formats (in the sequence specified on the command\n'
          'line). If no formats are specified, html, pdflatex, and sphinx are\n'
          'produced.\n'
          'make.py is a template: edit to set the desired options for compiling\n'
          'to the various formats.\n'
          'make.py autogenerates a unix shell script with all commands: you may\n'
          'use this shell script instead of make.py.\n')


def makefile():
    """Generate a generic (Python) makefile for compiling doconce files."""
    if len(sys.argv) < 3:
        _usage_makefile()
        sys.exit(0)

    dofile = sys.argv[1]
    if dofile.endswith('.do.txt'):
        dofile = dofile[:-7]

    formats = sys.argv[2:]

    # make.py with lots of functions for creating everything you can
    # create, easy to use in ipython
    # make.py mydoc sphinx pdflatex beamer

    if not formats:
        formats = ['pdflatex', 'html', 'sphinx', 'deck', 'reveal', 'beamer']

    make = open('make.py', 'w')
    make.write('''\
#!/usr/bin/env python
"""
Automatically generated file for compiling doconce documents.
"""
import sys, glob, os, shutil, subprocess

logfile = 'tmp_output.log'  # store all output of all operating system commands
f = open(logfile, 'w'); f.close()  # touch logfile so it can be appended

unix_command_recorder = []

def os_system(cmd):
    """Run system command cmd using the simple os.system command."""
    print(cmd)
    failure = os.system(cmd)
    if failure:
        print("""Command
  %s
failed""" % cmd)
        sys.exit(1)
    unix_command_recorder.append(cmd)  # record command for bash script

def system(cmd):
    """Run system command cmd using subprocess module."""
    print(cmd)
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("""Command
  %s
failed""" % cmd)
        print('Return code:', e.returncode)
        print(e.output)
        sys.exit(1)
    print(output)
    f = open(logfile, 'a'); f.write(output); f.close()
    unix_command_recorder.append(cmd)  # record command for bash script
    return output

def spellcheck():
    for filename in glob.glob('*.do.txt'):
        if not filename.startswith('tmp'):
            cmd = 'doconce spellcheck -d .dict4spell.txt %(filename)s' % vars()
            system(cmd)

def latex(name,
          latex_program='pdflatex',    # or 'latex'
          options='--latex_code_style=vrb',
          version='paper',             # or 'screen', '2up', 'A4', 'A4-2up'
          postfix='',                  # or 'auto'
          ptex2tex=None,               # only for ptex2tex step
          ):
    """
    Make latex/pdflatex (according to latex_program) PDF file from
    the doconce file name (without any .do.txt extension).

    version can take the following values:

      * paper: normal page size, --device=paper
      * 2up: normal page size, --device=paper, 2 pages per sheet
      * A4: A4 page size, --device=paper
      * A4-2up: A4 page size, --device=paper, 2 pages per sheet
      * screen: normal pages size, --device=screen

    If a separate ptex2tex step is wanted, fill in all necessary
    commands in the ptex2tex string.
    """
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')
    system('rm -f %(name)s.aux' % vars())

    if version in ('paper', 'A4', '2up', 'A4-2up'):
        if not '--device=paper' in options:
            options += ' --device=paper'
    elif version == 'screen' and '--device=paper' in options:
        options = options.replace('--device=paper', '')
    if version in ('A4', 'A4-2up'):
        if not '--latex_papersize=a4' in options:
            options += ' --latex_papersize=a4'
    if postfix == 'auto':
        if version == 'paper':
            postfix = '4print'
        elif version == 'screen':
            postfix = '4screen'
        else:
            postfix = version

    # Compile source
    cmd = 'doconce format %(latex_program)s %(name)s %(options)s ' % vars()
    system(cmd)

    # Transform .p.tex to .tex?
    if ptex2tex is not None:
        cmd = ptex2tex
        system(cmd)

    # Load latex file into string for examination
    dofile = open(name + '.tex', 'r')
    text = dofile.read()
    dofile.close()

    latex_options = ''
    if latex_program == 'pdflatex':
        latex_options = '-file-line-error -interaction nonstopmode'

    # Run latex
    shell_escape = ' -shell-escape' if 'begin{minted}' in text else ''
    cmd_latex = '%(latex_program)s%(shell_escape)s %(latex_options)s %(name)s' % vars()
    system(cmd_latex)

    if 'idx{' in text:
        cmd = 'makeindex %(name)s' % vars()
        system(cmd)
    if 'BIBFILE:' in text:
        cmd = 'bibtex %(name)s' % vars()
        system(cmd)
    system(cmd_latex)
    system(cmd_latex)
    if latex_program == 'latex':
        cmd = 'dvipdf %(name)s' % vars()
        system(cmd)
        # Could instead of dvipdf run the old-fashioned dvips and ps2pdf

    if version in ('2up', 'A4-2up'):
        # Use pdfnup to make two pages per sheet
        cmd = 'pdfnup --frame true --outfile %(name)s.pdf %(name)s.pdf' % vars()
        system(cmd)
    if postfix:
        shutil.copy(name + '.pdf', name + '-' + postfix + '.pdf')


def html(name, options='', split=False):
    """
    Make HTML file from the doconce file `name`
    (without any .do.txt extension).
    """
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    cmd = 'doconce format html %(name)s %(options)s ' % vars()
    system(cmd)

    if split:
        cmd = 'doconce split_html %(name)s' % vars()


def reveal_slides(name, options='', postfix='reveal', theme='darkgray'):
    """Make reveal.js HTML5 slides from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    if '--pygments_html_style=' not in options:
        from doconce.misc import recommended_html_styles_and_pygment_styles
        combinations = recommended_html_styles_and_pygment_styles()
        options += ' --pygments_html_style=%s' % combinations['reveal'][theme][0]
    if '--keep_pygments_html_bg' not in options:
        options += ' --keep_pygments_html_bg'
    options += ' --html_output="%(name)s-%(postfi)s'

    cmd = 'doconce format html %(name)s %(options)s ' % vars()
    system(cmd)

    cmd = 'doconce slides_html %(name)s-%(postfi)s reveal --html_slide_theme=%(theme)s'
    system(cmd)

def deck_slides(name, options='', postfix='deck', theme='sandstone.default'):
    """Make deck.js HTML5 slides from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    if '--pygments_html_style=' not in options:
        from doconce.misc import recommended_html_styles_and_pygment_styles
        combinations = recommended_html_styles_and_pygment_styles()
        options += ' --pygments_html_style=%s' % combinations['deck'][theme][0]
    if '--keep_pygments_html_bg' not in options:
        options += ' --keep_pygments_html_bg'
    options += ' --html_output="%(name)s-%(postfi)s'

    cmd = 'doconce format html %(name)s %(options)s ' % vars()
    system(cmd)

    cmd = 'doconce slides_html %(name)s-%(postfi)s deck --html_slide_theme=%(theme)s'
    system(cmd)

def beamer_slides(name, options='', postfix='beamer', theme='red_shadow',
                  ptex2tex_envir='minted'):
    """Make latex beamer slides from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')
    system('rm -f %(name)s.aux' % vars())

    # Compile source
    shell_escape = '-shell-escape' if ptex2tex_envir == 'minted' else ''
    cmd = 'doconce format pdflatex %(name)s %(options)s ' % vars()
    system(cmd)
    # Run latex
    cmd = 'doconce ptex2tex %(name)s envir=%(ptex2tex_envir)s' % vars()
    system(cmd)
    cmd = 'doconce slides_beamer %(name)s --beamer_slide_theme=%(theme)s' % vars()
    system(cmd)
    cmd = 'pdflatex %(shell_escape)s %(name)s'
    system(cmd)
    system(cmd)
    system('cp %(name)s.pdf %(name)s-%(postfi).pdf' % vars())

    cmd = 'doconce slides_html %(name)s-%(postfi)s deck --html_slide_theme=%(theme)s'
    system(cmd)


def sphinx(name, options='', dirname='sphinx-rootdir',
           theme='pyramid', automake_sphinx_options='',
           split=False):
    """
    Make Sphinx HTML subdirectory from the doconce file `name`
    (without any .do.txt extension).
    """
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    cmd = 'doconce format sphinx %(name)s %(options)s ' % vars()
    system(cmd)

    if split:
        cmd = 'doconce split_rst %(name)s' % vars()

    # Create sphinx directory
    cmd = 'doconce sphinx_dir theme=%(theme)s %(options)s %(name)s' % vars()
    system(cmd)

    # Compile sphinx
    cmd = 'python automake_sphinx.py %(automake_sphinx_options)s' % vars()
    system(cmd)

def doconce2format(name, format, options=''):
    """Make given format from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    cmd = 'doconce format %(format)s %(name)s %(options)s ' % vars()
    system(cmd)

def plain(name, options=''):
    doconce2format(name, 'plain', options)

def pandoc(name, options=''):
    doconce2format(name, 'pandoc', options)

def ipynb(name, options=''):
    doconce2format(name, 'ipynb', options)

def cwiki(name, options=''):
    doconce2format(name, 'cwiki', options)

def mwiki(name, options=''):
    doconce2format(name, 'mwiki', options)

def gwiki(name, options=''):
    doconce2format(name, 'gwiki', options)

def main():
    """
    Produce various formats from the doconce source.
    """
''')
    make.write('''
    dofile = "%(dofile)s"

    spellcheck()

    common_options = ''
''' % vars())

    for format in formats:
        if format.endswith('latex'):
            make.write(r"""
    # --- latex ---

    common_latex_options = ' --latex_code_style=vrb'

    for version in 'paper', 'screen':  # , 'A4', '2up', 'A4-2up':
        latex(
          dofile,
          latex_program='pdflatex',
          options=common_options + common_latex_options,
          version=version,
          postfix='auto')
""")
        elif format == 'html':
            make.write(r"""
    # --- HTML ---

    common_html_options = ''

    # HTML Bootstrap
    bootstrap_options = ' --html_style=bootswatch_readable --html_code_style=inherit --html_pre_style=inherit --toc_depth=2 --pygments_html_style=default'

    html(
      dofile,
      options=common_options + common_html_options + bootstrap_options,
      split=True)

    # One long HTML file
    #html(dofile, options=common_options + common_html_options + ' --html_style=bloodish --html_output=%s-1' % dofile, split=False)

    # Solarized HTML
    #html(dofile, options=common_options + common_html_options + ' --html_style=solarized3 --html_output=%s-solarized' % dofile, split=True)
""")
        elif format == 'sphinx':
            make.write(r"""
    # --- Sphinx ---

    sphinx_themes = ['pyramid',]
    for theme in sphinx_themes:
        dirname = 'sphinx-rootdir' if len(sphinx_themes) == 1 else 'sphinx-rootdir-%s' % theme
        sphinx(
          dofile,
          options=common_options + '',
          dirname=dirname,
          theme=theme,
          automake_sphinx_options='',
          split=False)
""")
        elif format == 'reveal':
            make.write(r"""

    # --- reveal.js slides ---

    reveal_slides(
      dofile,
      options=common_options + '',
      postfix='reveal',
      theme='darkgray')
""")
        elif format == 'deck':
            make.write(r"""
    # --- deck.js slides ---

    deck_slides(
      dofile,
      options=common_options + '',
      postfix='deck',
      theme='sandstone.default')
""")
        elif format == 'beamer':
            make.write(r"""
    # --- latex beamer slides ---

    beamer_slides(
      dofile,
      options=common_options + '',
      postfix='beamer',
      theme='red_shadow',
      ptex2tex_envir='minted')  # 'ans:nt'
""")
        elif format.endswith('wiki') or format in ('pandoc', 'plain', 'ipynb'):
            make.write(r"""
    doconce2format(dofile, format, options=common_options + '')

""")
    # Are there slides documents in addition?
    dofile_slides = glob.glob('slides_*.do.txt')
    for dofile in dofile_slides:
        # Is the TOC surrounded by a WITH_TOC test directive?
        f = open(dofile, 'r'); text = f.read(); f.close()
        with_toc = ' -DWITH_TOC' if 'WITH_TOC' in text else ''

        dofile = dofile[:-7]
        make.write(r"""
    # Slides file %(dofile)s
    dofile = "%(dofile)s"
""" % vars())
        for format in formats:
            if format == 'html':
                make.write(r"""
    html_style = 'bloodish'
    # One long HTML file
    html(
      dofile,
      options=common_options + ' --html_output=%(dofile)s-1 --html_style=%(html_style)s' % vars() + with_toc,
      split=False)
    system('doconce replace "<li>" "<p><li>" %(dofile)s-1.html' % vars())

    # Splitted HTML file
    html(
      dofile,
      options=common_options + ' --html_style=%(html_style)s' % vars() + with_toc,
      split=True)
    system('doconce replace "<li>" "<p><li>" %(dofile)s.html' % vars())

    # One long solarized file
    html(
      dofile,
      options=common_options + ' --html_style=solarized --html_output=%(dofile)s-solarized --pygments_html_style=perldoc --pygments_html_linenos' % vars() + with_toc,
      split=False)
    system('doconce replace "<li>" "<p><li>" %(dofile)s-solarized.html' % vars())
    reveal_slides(
      dofile,
      options=common_options + '',
      postfix='reveal',
      theme='darkgray')

    deck_slides(
      dofile,
      options=common_options + '',
      postfix='deck',
      theme='sandstone.default')
""")
            elif format.endswith('latex'):
                make.write(r"""
    beamer_slides(
      dofile,
      options=common_options + ' --latex_code_style=pyg',
      postfix='beamer',
      theme='red_shadow')

    # Ordinary latex document (for printing)
    latex(
      dofile,
      latex_program='pdflatex',
      options=common_options + ' --device=paper' + with_toc,
      )
""")
    make.write(r"""
    # Dump all Unix commands run above as a Bash script
    bash = open('tmp_make.sh', 'w')
    print('see tmp_make.sh for an equivalent auto-generated unix script')
    bash.write('''\
#!/bin/bash
set -x  # display all commands in output

# Safe execution of a Unix command: exit if failure
function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}
''')
    for cmd in unix_command_recorder:
        if cmd.startswith('doconce format') or cmd.startswith('rm '):
            bash.write('\\n')  # delimiter line in script
        bash.write('system ' + cmd + '\\n')
    bash.close()

    print('see tmp_output.log for the output of all the commands')
""")
    make.write(r"""

if __name__ == '__main__':
    main()
""")
    make.close()
    print('generated make.py for compiling %s.do.txt' % dofile)
    print('make.py is basically a template: edit to set the desired options')
    print('\n*** warning: the generated make.py script is experimental\n    and tested to a very little extent! (latex, html, sphinx are tested)')


def _usage_fix_bibtex4publish():
    print('Usage:\n'
          'doconce fix_bibtex4publish <fil1e.bib> <file2.bib> ...\n\n'
          'Fix a bibtex file so that the values are enclosed by braces (only) and publish can import the data.')


def fix_bibtex4publish():
    """Edit BibTeX files so that publish can import them."""
    if len(sys.argv) < 2:
        _usage_fix_bibtex4publish()
        sys.exit(0)

    bibfiles = sys.argv[1:]
    for bibfile in bibfiles:
        if not bibfile.endswith('.bib'):
            print(bibfile, 'is not a BibTeX file')
            _abort()
        shutil.copy(bibfile, bibfile + '.old~~')
        f = open(bibfile, 'r')
        lines = f.readlines()
        f.close()
        print('\n*** working with', bibfile, '\n')

        for line in lines:
            print(line)
        keys = []
        for i in range(len(lines)):
            # Classification line? Fix to lower case publication type
            if lines[i].lstrip().startswith('@'):
                m = re.search(r'^\s*@(.+?)\{(.+), *$', lines[i])
                if m:
                    pub_type = m.group(1)
                    key = m.group(2)
                    print('\n--- found %s (key %s)\n' % (pub_type, key))
                    pub_type = pub_type.lower()
                    if pub_type == 'incollection':
                        pub_type = 'inproceedings'
                    keys.append(key)
                    lines[i] = '@%s{%s,\n' % (pub_type, key)
            # Data line? Enclose value in {}, lower case variable, etc.
            elif re.search(r'^\s*[A-Za-z ]+=', lines[i]):
                words = lines[i].split('=')
                old_variable = words[0]
                variable = old_variable.lower().strip()
                if len(words) > 2:
                    # A = in the value..
                    print(words)
                    value = '='.join(words[1:]).strip()
                else:
                    value = words[1].strip()
                if value[-1] == ',':
                    value = value[:-1]
                old_value = value
                fixed = False
                if value.startswith('"'):
                    value = '{' + value[1:-1].lstrip()
                    fixed = True
                if value.endswith('"'):
                    value = value[:-1].rstrip() + '}'
                    fixed = True
                if value[0] != '{':
                    value = '{' + value.lstrip()
                    fixed = True
                if value[-1] != '}':
                    value = value.rstrip() + '}'
                    fixed = True
                lines[i] = '%-15s = %s,\n' % (variable, value)
                if fixed:
                    print('%s = %s' % (old_variable, old_value))
                    print('...fixed to...')
                    print('%-15s = %s\n' % (variable, value))
            elif lines[i].strip() == '':
                pass # ok
            elif lines[i].strip() == '}':
                pass # ok
            elif lines[i].lstrip().startswith('%'):
                pass # ok
            else:
                # Loose sentence, this one should be glued with the
                # former one
                # NOT IMPLEMENTED
                print('*** error: broken line')
                print(lines[i])
                print('Glue with previous line!')
                _abort()

        f = open(bibfile, 'w')
        f.writelines(lines)
        f.close()


def _usage_list_fig_src_files():
    print('Usage:\n'
          'doconce list_fig_src_files *.do.txt')


def list_fig_src_files():
    """
    List all figure, movie, and source code files needed in a
    set of .do.txt files. Useful when splitting a document into
    new chapters and directories.
    """
    if len(sys.argv) < 2:
        _usage_list_fig_src_files()
        sys.exit(0)

    from .common import INLINE_TAGS
    code_pattern = '^@@@CODE +([^ ]+)'
    figs = []
    movs = []
    cods = []
    for filename in sys.argv[1:]:
        f = open(filename, 'r');  text = f.read();  f.close()
        figs += [figfile for figfile, options, caption in
                 re.findall(INLINE_TAGS['figure'], text, flags=re.MULTILINE)]
        movs += [movfile for movfile, options, caption in
                 re.findall(INLINE_TAGS['movie'], text, flags=re.MULTILINE)]
        cods += re.findall(code_pattern, text, flags=re.MULTILINE)
    if figs:
        print('\n'.join(figs))
    if movs:
        print('\n'.join(movs))
    if cods:
        print('\n'.join(cods))


def _usage_csv2table():
    print('Usage:\n'
          'doconce csv2table <file.csv> [--headings=clr --columns=rrl --delimiter=;] > <outfile>')


def csv2table():
    """Convert a csv file to a DocOnce table."""
    if len(sys.argv) < 2:
        _usage_csv2table()
        sys.exit(0)

    delimiter = ','
    for arg in sys.argv[1:]:
        if arg.startswith('--delimiter='):
            delimiter = arg.split('=')[1]

    import csv
    filename = sys.argv[1]
    csvfile = open(filename, 'r')
    table = []
    for row in csv.reader(csvfile, delimiter=delimiter):
        if row:
            table.append(row)
    csvfile.close()
    # Now, table is list of lists
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = table[i][j].strip()

    #import pprint;pprint.pprint(table)
    num_columns = 0
    max_column_width = 0
    for row in table:
        num_columns = max(num_columns, len(row))
        for column in row:
            max_column_width = max(max_column_width, len(column))
    # Add empty cells
    for i in range(len(table)):
        table[i] = table[i] + ['']*(num_columns-len(table[i]))

    align_headings = align_columns = 'c'*num_columns
    for arg in sys.argv[1:]:
        if arg.startswith('--headings='):
            align_headings = list(arg.split('=')[1])
            if len(align_headings) != num_columns:
                print('*** error: %s has wrong no of columns (should be %d)' % \
                      (arg, num_columns))
        if arg.startswith('--columns='):
            align_columns = list(arg.split('=')[1])
            if len(align_columns) != num_columns:
                print('*** error: %s has wrong no of columns (should be %d)' % \
                      (arg, num_columns))


    # Construct doconce table
    width = (max_column_width+2)*num_columns + num_columns+1
    separator0 = '|' + '-'*(width-2) + '|'
    separator1 = separator0
    separator2 = separator0

    s = list(separator1)
    for j in range(num_columns):
        s[old_div(max_column_width,2) + 1 + j*(max_column_width+3)] = align_headings[j]
    separator1 = ''.join(s)

    s = list(separator2)
    for j in range(num_columns):
        s[old_div(max_column_width,2) + 1 + j*(max_column_width+3)] = align_columns[j]
    separator2 = ''.join(s)

    column_format = ' %%-%ds ' % max_column_width
    for j in range(len(table)):
        table[j] = [column_format % c for c in table[j]]
        table[j] = '|' + '|'.join(table[j]) + '|'
    text = '\n\n' + separator1 + '\n' + table[0] + '\n' + \
           separator2 + '\n' + '\n'.join(table[1:]) + \
           '\n' + separator0 + '\n\n'
    print(text)


# ------------ diff two files ----------------
_diff_programs = {
    'latexdiff': ('https://www.ctan.org/pkg/latexdiff', 'latexdiff'),
    'pdiff': ('https://www.gnu.org/software/a2ps/ https://www.gnu.org/software/wdiff/', 'a2ps wdiff texlive-latex-extra texlive-latex-recommended'),
    'kdiff3': ('https://www.gnu.org/software/wdiff/', 'kdiff3'),
    'diffuse': ('https://diffuse.sourceforge.net/', 'diffuse'),
    'xxdiff': ('https://xxdiff.sourceforge.net/local/', 'fldiff'),
    'fldiff': ('https://packages.debian.org/sid/fldiff', 'fldiff'),
    'meld': ('https://meldmerge.org/', 'meld'),
    'tkdiff.tcl': ('https://sourceforge.net/projects/tkdiff/', 'not in Debian')
    }


def _missing_diff_program(program_name):
    print(program_name, 'is not installed.')
    print('see', _diff_programs[program_name][0])
    if not _diff_programs[program_name][1].startswith('not in'):
        print('Ubuntu/Debian Linux: sudo apt-get install', \
              _diff_programs[program_name][1])
    sys.exit(1)


def _usage_diff():
    print('Usage:\n'
          'doconce diff oldfile newfile [<diffprog>]\n\n'
          '<diffprog> may be difflib (default), pdiff, diff, diffuse, kdiff3, xxdiff, meld, latexdiff\n'
          'Output in diff.*')


def diff():
    """Find differences between two files."""
    if len(sys.argv) < 3:
        _usage_diff()
        sys.exit(0)
    system('rm -f _diff.*')

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    try:
        diffprog = sys.argv[3]
    except:
        diffprog = 'difflib'

    if diffprog == 'difflib':
        diffing_files = pydiff(file1, file2)
        if diffing_files:
            print('differences found, see ', \
                  ','.join([name + '.html|.txt' for name in diffing_files]))

    elif diffprog == 'latexdiff':
        if which('latexdiff'):
            latexdiff(file1, file2)
        else:
            _missing_diff_program('latexdiff')

    else:
        diff_files(file1, file2, diffprog)


def pydiff(files1, files2, n=3, prefix_diff_files='tmp_diff_'):
    """
    Use Python's difflib to compute the difference between
    files1 and files2 (can be corresponding lists of files
    or just two strings if only one set of files is to be
    compared).
    Produce text and html diff.
    """
    import difflib, time, os
    if isinstance(files1, str):
        files1 = [files1]
    if isinstance(files2, str):
        files2 = [files2]

    sizes = []  # measure diffs in bytes
    diff_files = []  # filestem of non-empty diff files generated
    for fromfile, tofile in zip(files1, files2):

        if not os.path.isfile(fromfile):
            print(fromfile, 'does not exist')
            _abort()
        if not os.path.isfile(tofile):
            print(tofile, 'does not exist')
            _abort()

        fromdate = time.ctime(os.stat(fromfile).st_mtime)
        todate = time.ctime(os.stat(tofile).st_mtime)

        fromlines = open(fromfile, 'U').readlines()
        tolines = open(tofile, 'U').readlines()

        diff_html = difflib.HtmlDiff().make_file(
            fromlines, tolines, fromfile, tofile, context=True, numlines=n)
        diff_plain = difflib.unified_diff(
            fromlines, tolines, fromfile, tofile, fromdate, todate, n=n)
        filename_plain = prefix_diff_files + tofile + '.txt'
        filename_html  = prefix_diff_files + tofile + '.html'

        f = open(filename_plain, 'w')
        # Need to add newlines despite doc saying that trailing newlines are
        # inserted...
        diff_plain = [line + '\n' for line in diff_plain]
        f.writelines(diff_plain)
        f.close()

        f = open(filename_html, 'w')
        f.writelines(diff_html)
        f.close()
        size = os.path.getsize(filename_plain)
        # Any diff? (Could also just test if the file strings are different)
        if size > 4:
            sizes.append(size)
            diff_files.append(prefix_diff_files + tofile)
        else:
            os.remove(filename_plain)
            os.remove(filename_html)
    return diff_files  # empty if no differences


def check_diff(diff_file):
    size = os.path.getsize(diff_file)
    if size > 4:
        print('diff in', diff_file)
    else:
        os.remove(diff_file)


def latexdiff(files1, files2):
    """Highlight file differences with latexdiff."""
    if not which('latexdiff'):
        _missing_diff_program('latexdiff')

    if isinstance(files1, str):
        files1 = [files1]
    if isinstance(files2, str):
        files2 = [files2]

    for fromfile, tofile in zip(files1, files2):

        # Must convert to latex if doconce files
        if fromfile.endswith('.do.txt'):
            basename = fromfile[:-7]
            failure1 = os.system('doconce format pdflatex %s' % basename)
            failure2 = os.system('doconce ptex2tex %s' % basename)
            fromfile = basename + '.tex'

        if tofile.endswith('.do.txt'):
            basename = tofile[:-7]
            failure1 = os.system('doconce format pdflatex %s' % basename)
            failure2 = os.system('doconce ptex2tex %s' % basename)
            tofile = basename + '.tex'

        diff_file = 'tmp_diff_%s.tex' % os.path.basename(tofile)
        failure = os.system('latexdiff %s %s > %s' %
                            (fromfile, tofile, diff_file))
        failure = os.system('pdflatex %s' % diff_file)
        size = os.path.getsize(diff_file)
        if size > 4:
            print('output in', diff_file[:-3] + 'pdf')


def diff_files(files1, files2, program='diff'):
    """
    Run some diff program:

          diffprog file1 file2 > tmp_diff_*.txt/.pdf/.html

    for file1, file2 in zip(files1, files2).
    """
    if isinstance(files1, str):
        files1 = [files1]
    if isinstance(files2, str):
        files2 = [files2]

    for fromfile, tofile in zip(files1, files2):
        cmd = '%s %s %s' % (program, fromfile, tofile)
        if program in ['diffuse', 'kdiff3', 'xxdiff', 'fldiff', 'meld', 'tkdiff.tcl']:
            # GUI program
            if which(program):
                system(cmd, verbose=True)
            else:
                _missing_diff_program(program)
        elif program == 'diff':
            diff_file = 'tmp_diff_%s.txt' % os.path.basename(tofile)
            system(cmd + ' > ' + diff_file, verbose=True)
            check_diff(diff_file)
        elif program == 'pdiff':
            diff_file = 'tmp_diff_%s' % os.path.basename(tofile)
            if which('pdiff'):
                system(cmd + ' -- -1 -o %s.ps' % diff_file)
                system('ps2pdf -sPAPERSIZE=a4 %s.ps; rm -f %s.ps' %
                       (diff_file, diff_file))
            else:
                _missing_diff_program(program)
            print('diff in %s.pdf' % diff_file)
        else:
            print(program, 'not supported')
            _abort()


def _usage_gitdiff():
    print('Usage:\n'
          'doconce gitdiff <file1> <file2> <file3>')


def gitdiff():
    """Make diff of newest and previous version of files (under Git)."""
    if len(sys.argv) < 2:
        _usage_gitdiff()
        sys.exit(0)

    #diffprog = sys.argv[1]
    filenames = sys.argv[1:]
    old_files = []
    for filename in filenames:
        cmd = 'git log %s' % filename
        try:
            output = subprocess.check_output(cmd, shell=True,
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            commits = re.findall(r'^commit\s+(.+)$', output,
                                 flags=re.MULTILINE)
            dates = re.findall(r'^Date:\s+(.+)\d\d:\d\d:\d\d .+$', output,
                               flags=re.MULTILINE)
            system('git checkout %s %s' % (commits[1], filename))
            old_filename = '__' + dates[1].replace(' ', '_') + filename
            shutil.copy(filename, old_filename)
            system('git checkout %s %s' % (commits[0], filename))
            old_files.append(old_filename)
            print('doconce diff', old_filename, filename)
            #pydiff(filenames, old_files)


def _usage_extract_exercises():
    print('Usage:\n'
          'doconce extract_exercises tmp_mako__<file>[.do.txt] "--filter=keyword 1;keyword 2; some key word" \\\n'
          '--exercise_numbering=chapter --examples_as_exercises\n\n'
          'Extract exercises to a separate document. Inherit numbering from parent document.\n'
          'Must use tmp_mako__*.do.txt as file to have includes in place.\n'
          'Note:\n'
          'extracting exercises may create a need for generalized references to the original document (ref[][][]).\n')


def extract_exercises():
    if len(sys.argv) < 2:
        _usage_extract_exercises()
        sys.exit(0)

    filename = sys.argv[1]
    if filename.endswith('.do.txt'):
        basename = filename[:-7]
    else:
        basename = filename
        filename += '.do.txt'

    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    # Load .exerinfo file
    exerinfoname = '.%s.exerinfo' % basename.replace('tmp_mako__', '')
    if not os.path.isfile(exerinfoname):
        print('*** error: you must compile the document with doconce format')
        print('    before running doconce extract_exercises (need the %s file)' % exerinfoname)
        _abort()
    else:
        with open(exerinfoname, 'r') as f:
            exerinfo = eval(f.read())

    keywords = []
    filter = misc_option('filter=', None)
    if filter is not None:
        keywords = re.split(r';\s*', filter)

    if option('examples_as_exercises'):
        exer_heading_pattern = r'^ *(=====) *\{?(Example|Exercise|Problem|Project)\}?: *(?P<title>[^ =-].+?)\s*====='
    else:
        exer_heading_pattern = r'^ *(=====) *\{?(Exercise|Problem|Project)\}?: *(?P<title>[^ =-].+?)\s*====='
    keywords_pattern = r'^#?\s*(keywords|kw) *= *([A-Za-z0-9\-._;, ]+)'
    has = dict(DATE=False, TOC=False, Externaldocuments=False)
    exer = []
    exer_tp = []
    inside_exer = False
    for i, line in enumerate(lines):
        if line.startswith('TITLE:'):
            line = line.replace('TITLE: ', 'TITLE: Exercises from ')
            exer.append(line)
        elif line.startswith('TOC:'):
            exer.append(line)
            has['TOC'] = True
        elif line.startswith('AUTHOR:'):
            exer.append(line)
        elif line.startswith('DATE:'):
            exer.append(line)
            exer.append('\n\n# ExTRALINES\n\n')
            has['DATE'] = True
        elif line.startswith('========= '):
            exer.append(line)
        elif line.startswith('# Externaldocuments:'):
            # Copy document list and add mother document
            exer.append('\n' + line.rstrip() + ', ' +
                        basename.replace('tmp_mako__', '') + '\n')
            has['Externaldocuments'] = True

        if re.search(exer_heading_pattern, line):  # inside exercise?
            inside_exer = True
            exer.append([])
            exer_tp.append(None)
        if inside_exer:
            # Filter afterwards
            if not isinstance(exer[-1], list):
                print('inside exercise, but exer[-1] is not a list', exer[-1])
            exer[-1].append(line)

            m = re.search(keywords_pattern, line)
            if m:
                exer_tp[-1] = [name.strip() for name in m.group(2).split(';')]

        if inside_exer and i < len(lines)-1 and lines[i+1].startswith('====='):
            inside_exer = False

    # Strip off blank lines at the end of each exercise
    for line in exer:
        if isinstance(line, list):
            for i in range(len(line)-1, -1, -1):
                if line[i] == '\n':
                    line[i] = ''
                else:
                    break

    filename = basename[10:] + '_exer.do.txt'
    f = open(filename, 'w')
    exer_numbering = option('exercise_numbering=', 'absolute')
    labels2numbers = {}
    i = 0
    for line in exer:
        # Is line an ordinary line (chapter heading) or an exercise section?
        if isinstance(line, list):
            # come to  exercise section since line is list of lines
            print_this_exer = not keywords  # default: print if no filtering
            if keywords and exer_tp[i] is not None:
                print_this_exer = False
                # Any of this exercise's keywords among those in the filter:
                for keyword in exer_tp[i]:
                    if keyword in keywords:
                        print_this_exer = True

            if print_this_exer:
                # Find (first) label in this exercise
                label = None
                for exer_line in line:
                    if 'label{' in exer_line:
                        m = re.search(r'label{(.+?)}', exer_line)
                        if m:
                            label = m.group(1)
                            break
                if label is None:
                    print('*** error: doconce extract_exercises requires that every exercise has a label!')
                    print('    Add missing labels!')
                    _abort()
                # Find corresponding number info of this exercise
                if label is not None:
                    for ex in exerinfo:
                        if ex.get('label', None) == label:
                            labels2numbers[label] = ex['no'] if exer_numbering == 'absolute' else '%s.%s' % (ex['chapter_no'], ex['chapter_exercise'])

                #f.write('\n\n# --- begin exercise ---\n\n') # will lead to double numbering
                for exer_line in line:
                    f.write(exer_line)
                #f.write('\n# --- end exercise ---\n\n')
                f.write('\n') # nice with a blank line
            i += 1
        elif isinstance(line, str):
            f.write(line)
    f.close()
    # Check if we have references to the original document,
    # also add labels2numbers
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    labels = re.findall(r'label\{(.+?)\}', filestr)
    refs = re.findall(r'ref\{(.+?)\}', filestr)
    for ref in refs:
        if not ref in labels:
            print('\n*** warning: reference ref{%s} - no label found in document' % ref)
            print('    need generalized reference ref[][][] in the original document for this label!')

    extra_text = ''
    if not has['DATE']:
        # No DATE and hence no # ExTRALINES, add that to the top
        filestr = '\n# ExTRALINES\n\n' + filestr
    if not has ['Externaldocuments']:
        # Need add at least the mother document as external document
        # because of generalized refs back to that document
        extra_text += '# Externaldocuments: %s' % basename.replace('tmp_mako__', '')
    if not has['TOC']:
        extra_text += '\n\nTOC: off\n\n'
    # Add labels2numbers data structure
    extra_text += '\n# Mapping from exercise labels to numbers: label2numbers = %s' % repr(labels2numbers)

    filestr = re.sub(r'# ExTRALINES', extra_text, filestr)
    f = open(filename, 'w')
    f.write(filestr)
    f.close()
    print('exercises extracted to', filename)


def find_file_with_extensions(filename_in, allowed_extensions=['']):
    """Check the existence of a filename having given extensions.
    Return relative directory, basename, extension, and complete filename,

    Given an input filename (e.g. './book' or 'mybook/book.do.txt') and a
    list of allowed extensions (e.g. ['.do.txt']), return the file's
        * relative directory `dirname` ('' or 'mybook', but never '.' or './);
        * basename `basename` ('book');
        * extension `ext` ('.do.txt');
        * complete filename `filename` ('book.do.txt').
    Relative directories such as './', '../' are stripped of all output.
    Use `allowed_extensions=''` for checking exact matches, but this causes
    the extension to be ''. Return a tuple of None if the file was not found.
    :param str filename_in: Filename or its basename.
    :param list(str) allowed_extensions: list of legal extensions
    :return: tuple of dirname, basename, ext, and filename
    :rtype: (str, str, str, str)
    """
    # Get the directory name. Make it a relative path
    dirname = os.path.dirname(filename_in)
    dirname = os.path.relpath(dirname or '.', start=os.getcwd())
    if dirname == '.':
        dirname = ''
    if dirname.startswith('./'):
        dirname = dirname[2:]
        #_abort()

    ext, basename, filename_out = None, None, None
    dir_basename = filename_in
    # Try to split every allowed suffix from input filename.
    # If it works, check if the file exists
    for ext_i in allowed_extensions:
        if ext_i != '':
            if not ext_i.startswith('.'):
                ext_i = '.' + ext_i
            tmp = filename_in.split(ext_i)
            if len(tmp) == 2 and tmp[-1] == '':
                dir_basename = tmp[0]
        #else:
            #dir_basename = filename_in
            #if ext_i.endswith(''):
            #    ext_i = ext_i[:-1]

        # Check that the filename exists
        if os.path.isfile(dir_basename + ext_i):
            # Extension found
            ext = ext_i
            basename = os.path.basename(dir_basename)
            # Compose the filename (basename + suffix, but no path)
            filename_out = basename + ext
            break
    if ext == None:
        print('*** error: could not find any file "%s*"' % filename_in)
        print('    with extensions "%s"' % '" , "'.join(allowed_extensions))
        dirname, basename = None, None
        #_abort()
    # Remove initial '.' or  './'
    if basename and basename.startswith('./'):
        basename = basename[2:]
    if filename_out and filename_out.startswith('./'):
        filename_out = filename_out[2:]
    return dirname, basename, ext, filename_out


def folder_checker(dirname):
    """Convert to relative path and verify that it exists

    Helper function to evaluate the existence and formatting of a folder

    :param str dirname: Path to an existing folder
    :return: relative path to the input directory
    :rtype: str
    """
    # Convert to path relative to current directory
    dirname = os.path.relpath(dirname , start=os.getcwd())
    if not os.path.isdir(dirname):
        errwarn('*** error : destination folder not found:\n    %s' % dirname)
        _abort()
    if not dirname.endswith('/'):
        return dirname + '/'
    return dirname