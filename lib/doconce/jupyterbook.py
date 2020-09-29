import os, sys, shutil, re, glob, math
from doconce import globals
from .doconce import read_file, write_file, doconce2format, parse_doconce_filename, errwarn, _rmdolog, preprocess
from .misc import option, help_print_options, check_command_line_options, system, _abort
from .common import INLINE_TAGS, remove_code_and_tex

docstring_jupyterbook = """Usage: doconce jupyterbook filename [options] 
Create files for Jupyter Book version: 0.8
Example: doconce jupyterbook filename.do.txt --sep=section
Try 'doconce jupyterbook --help' for more information.
"""

_registered_cmdline_opts_jupyterbook = [
    ('-h','Show this help page'),
    ('--help','Show this help page'),
    ('--sep=','Specify separator for DocOnce file into jupyter-book chapters. [chapter|section|subsection]'),
    ('--dest=','Destination folder for the content'),
    ('--dest_toc=','Destination folder for the _toc.yml file'),
    ('--titles=','File with page titles, i.e. titles in TOC on the left side of the page. Default is \'auto\': '
                 'assign titles based on the separator headers')
]
# Get the list of options for doconce jupyterbook
_legal_cmdline_opts_jupyterbook, _ = list(zip(*_registered_cmdline_opts_jupyterbook))
_legal_cmdline_opts_jupyterbook = list(_legal_cmdline_opts_jupyterbook)

# Get the list of opitions for doconce in general
_legal_command_line_options = [opt for opt, help in globals._registered_command_line_options]

def jupyterbook():
    """
    Create content and TOC for building a jupyter-book version 0.6: https://jupyterbook.org/intro

    This function is called directly from bin/doconce
    """
    # Print help
    if len(sys.argv) < 2:
        print(docstring_jupyterbook)
        sys.exit(1)
    if option('help') or '-h' in sys.argv:
        print_help_jupyterbook()
        sys.exit(1)
    # Check options
    # NB: _legal_command_line_options allows options defined in misc.py/global.py
    if not check_command_line_options(1, option_list=_legal_cmdline_opts_jupyterbook + _legal_command_line_options):
        _abort()

    #Destination directories
    dest = option('dest=', default='./', option_list=_legal_cmdline_opts_jupyterbook)
    dest = folder_checker(dest)
    dest_toc = option('dest_toc=', default='./', option_list=_legal_cmdline_opts_jupyterbook)
    dest_toc = folder_checker(dest_toc)

    # Get options
    sep = option('sep=', default='section', option_list=_legal_cmdline_opts_jupyterbook)
    globals.encoding = option('encoding=', default='')
    titles = option('titles=', default='auto', option_list=_legal_cmdline_opts_jupyterbook)

    # Check if the file exists, then read it in
    globals.filename = sys.argv[1]
    dirname, basename, ext, globals.filename = parse_doconce_filename(globals.filename)
    globals.dofile_basename = basename

    # NOTE: The following is a reworking of code from doconce.py > format_driver
    _rmdolog()     # always start with clean log file with errors
    preprocessor_options = [arg for arg in sys.argv[1:]
                            if not arg.startswith('--')]
    format = 'pandoc'
    filename_preprocessed = preprocess(globals.filename, format, preprocessor_options)

    # Run parts of file2file code in format_driver.
    # Cannot use it directly because file2file writes to file. Consider to modularize file2file
    filestr = read_file(filename_preprocessed, _encoding = globals.encoding)

    # Remove pandoc's title/author/date metadata, which does not get rendered appropriately in
    # markdown/jupyter-book. Consider to write this metadata to the _config.yml file
    for tag in 'TITLE', 'AUTHOR', 'DATE':
        if re.search(r'^%s:.*' % tag, filestr, re.MULTILINE):
            errwarn('Removing heading with %s. Consider to write it in the _config.yml file' % tag.lower())
        filestr = re.sub(r'^%s:.*' % tag, '', filestr, flags=re.MULTILINE)
    # Remove TOC tag
    tag = 'TOC'
    if re.search(r'^%s:.*' % tag, filestr, re.MULTILINE):
        if re.search(r'^%s:.*' % tag, filestr, re.MULTILINE):
            errwarn('Removing the %s tag' % tag.lower())
        filestr = re.sub(r'^%s:.*' % tag, '', filestr, flags=re.MULTILINE)

    # Delete any non-printing characters, commands, and comments
    # Using regex:
    m = re.search(r'\A\s*^(?:#.*\s*|!split\s*)*', filestr, re.MULTILINE)
    if m:
        filestr = filestr[m.end():]
    # No-regex method. This could be an alternative to the previous regex
    '''skip = ''
    for line in filestr.splitlines():
        if not line.strip():
            skip += line + '\n'
        elif not line.startswith('#') and not line.startswith('!'):
            break
        else:
            skip += line +'\n'
    filestr = filestr[len(skip):]
    '''

    # Split in chunks
    chunks, chunk_filenames = [], []
    if re.search(INLINE_TAGS[sep], filestr, flags=re.MULTILINE) is None:
        print('%s pattern not found in file' % sep)
        chunks.append(filestr)
    else:
        pos_prev = 0
        for m in re.finditer(INLINE_TAGS[sep], filestr, flags=re.MULTILINE):
            if m.start() == 0:
                continue
            # Skip separators used for illustration of doconce syntax inside !bc and !ec directives
            if filestr[:m.start()].rfind('!bc') > filestr[:m.start()].rfind('!ec'):
                errwarn('*** warning : skipped a separator, '
                        'which appeared to be inside the !bc and !ec directives')
                continue
            chunk = filestr[pos_prev:m.start()]
            chunks.append(chunk)
            pos_prev = m.start()
        chunk = filestr[m.start():]
        chunks.append(chunk)
    chunk_formatter = str(max(2, math.floor(math.log(len(chunks), 10)) + 1))
    chunk_formatter = '%0' + chunk_formatter + 'd'

    # Get any title from headers in each chunks
    title_list = []
    if titles is 'auto':
        for i,chunk in enumerate(chunks):
            chunk, title = create_title(chunk, sep, INLINE_TAGS)
            #Files must have a title (see docs jupyter-book > Rules for all content types)
            if title == '':
                title = chunk_formatter % (i + 1) + '_' + globals.dofile_basename
            chunk = '='*9 + ' ' + title + ' ' + '='*9 + '\n' + chunk
            chunks[i] = chunk
            title_list.append(title)
    else:
        title_list = read_to_list(titles)

    # Write each chunk to markdown or ipynb
    for i,chunk in enumerate(chunks):
        #Convert each chunk to pandoc, or to ipynb if the text contains any computation
        format = 'pandoc'
        _filestr, code_blocks, code_block_types, tex_blocks = \
            remove_code_and_tex(chunk, format)
        if len(code_blocks):
            format = 'ipynb'
        chunk_ind = chunk_formatter % (i+1) + '_'
        chunk_out, bg_session = doconce2format(chunk, format)
        chunk_filenames.append(chunk_ind + basename)
        full_file_path = dest + chunk_filenames[i]
        full_file_path += '.md' if format == 'pandoc' else '.ipynb'
        write_file(chunk_out, full_file_path, _encoding=globals.encoding)

    # Create the _toc.yml file
    if option('titles=', default=False, option_list=_legal_cmdline_opts_jupyterbook):
        yml_text = create_toc_yml(chunk_filenames, title_list, dest=dest, dest_toc=dest_toc)
    else:
        yml_text = create_toc_yml(chunk_filenames, [], dest=dest, dest_toc=dest_toc)
    print('\nWrote _toc.yml and %d chapter files to these folders:\n  %s\n  %s' %
          (len(chunk_filenames), os.path.realpath(dest_toc), os.path.realpath(dest)))
    write_file(yml_text, dest_toc + '_toc.yml', _encoding=globals.encoding)

def create_title(chunk, sep, INLINE_TAGS):
    """Helper function to allow doconce jupyterbook to automatically assign titles in the TOC

    If a chunk of text starts with the section specified in sep, lift it up
    to a chapter section. This allows doconce jupyterbook to automatically use the
    section's text as title in the TOC on the left

    :param str chunk: text string
    :param str sep: chapter|section|subsection
    :param list[str] INLINE_TAGS: patterns from common.py
    :return: tuple with the chunk stripped of its section header, and title
    :rtype: (str, str)
    """
    title = ''
    m = re.search(INLINE_TAGS[sep], chunk, flags=re.MULTILINE)
    if m and m.start() == 0:
        name2s = {'chapter': 9, 'section': 7, 'subsection': 5, 'subsubsection': 3}
        s = name2s[sep]
        header_old = '=' * s
        pattern = r'^ *%s +(.+?) +%s' % (header_old, header_old)
        # Get the title
        mt = re.match(pattern, chunk)
        if mt:
            title = mt.group(1)
        chunk = re.sub(pattern, '', chunk, flags=re.MULTILINE, count=1)
    return chunk, title

def create_toc_yml(paths, titles = [], dest='./', dest_toc='./'):
    """Create the content of a _toc.yml file

    Give the lists of paths and titles, return the content of a _toc.yml file

    :param list[str] paths: list of paths, i.e. strings that can be used after the `file:` section in a _toc.yml
    :param list[str] titles: list of titles, i.e. strings that can be used after the `title:` section in a _toc.yml
    :return: content of a _toc.yml file
    :rtype: str
    """
    # Get the relative path between the destination folders
    relpath = os.path.relpath(dest, dest_toc)
    if relpath == '.':
        relpath = ''
    else:
        relpath += '/'
    # Get the titles for the TOC
    if not len(titles):
        title_list = [''] * len(paths)
    elif len(titles) != len(paths):
        errwarn('*** error : number of titles given is %d, it should be %d'
                % (len(titles), len(paths)))
        _abort()
    else:
        title_list = titles
    # Produce the text for _toc.yml
    yml_text = ""
    for i, fname in enumerate(paths):
        froot, _ = os.path.splitext(fname)
        title = title_list[i]
        if title:
            # Wrap title in quotes if it contains colons or dashes
            if re.search(':', title) or re.search('-', title):
                title = '"' + title + '"'
            yml_text += yml_titledpage(relpath + froot, title, numbered=False)
        else:
            yml_text += yml_untitledpage(relpath + froot, numbered=False)
    return yml_text

def print_help_jupyterbook():
    """Pretty print help string and command line options

    Help function to print help and formatted command line options for doconce jupyterbook
    """
    from .misc import help_format
    print(docstring_jupyterbook)
    help_print_options(cmdline_opts=_registered_cmdline_opts_jupyterbook)

def read_to_list(file):
    """Read the content of a file to list

    Verify the existence of a file, then read it to a list by
    stripping newlines. The function aborts the program if the file does not exist.

    :param str file: Path to an existing file
    :return: list of strings
    :rtype: list[str]
    """
    if not os.path.isfile(file):
        errwarn('*** error: file "%s" does not exist!' % file)
        _abort()
    with open(file, 'r') as f:
        out = f.read().splitlines()
    return out

def folder_checker(dirname):
    """Verify a path

    Helper function to evaluate the existence and formatting of a folder

    :param str dirname: Path to an existing folder
    :return: directory name
    :rtype: str
    """
    if not os.path.isdir(dirname):
        errwarn('*** error : destination folder not found:\n    %s' % dirname)
        _abort()
    if not dirname.endswith('/'):
        return dirname + '/'
    return dirname


def yml_file(file):
    return "- file: %s\n\n" % file

def yml_untitledpage(file, numbered=False):
    return "- file: %s\n  numbered: %s\n\n" % (file, str(numbered).lower())

def yml_titledpage(file, title, numbered=False):
    return "- file: %s\n  title: %s\n  numbered: %s\n\n" % (file, title, str(numbered).lower())

def yml_nested_sections(nesting_level=1, *files):
    yml = "%ssections:\n" % ('  '*nesting_level)
    for file in files:
        yml += '%s  - file: %s\n' % ('  '*nesting_level, file)
    return yml + '\n'

def yml_part(part, *files):
    yml = "- part: %s\n  chapters:\n" % part
    for file in files:
        yml += '  - file: %s\n' % file
    return yml + '\n'

def yml_ext_link(file, title, external='true', numbered=False):
    return "- file: %s\n  title: %s\n  external: %s\n  numbered: %s\n" % \
           (file, title, external, str(numbered).lower())

def yml_searchbar(title, search):
    return "- title: Search\n  search: true\n" % (title, search)

def yml_divider(divider=True):
    return "- divider: %s\n" % str(divider).lower()

def yml_header(header):
    return "- header: %s\n" % header

def yml_chapter(file, title, sections, numbered='false', expand_sections=True):
    return "- title: %s\n  file: %s\n  numbered: %s\n  expand_sections: %s\n  sections:\n" % \
           (file, title, sections, numbered, str(expand_sections).lower())

def yml_section(file, title, numbered=False):
    return "  - title: %s\n    file: %s\n    numbered: %s" % (file, title, str(numbered).lower())