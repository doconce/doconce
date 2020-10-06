import os, sys, shutil, re, glob, math
from doconce import globals
from .doconce import read_file, write_file, doconce2format, parse_doconce_filename, errwarn, _rmdolog, preprocess
from .misc import option, help_print_options, check_command_line_options, system, _abort
from .common import INLINE_TAGS, remove_code_and_tex

docstring_jupyterbook = """Usage: doconce jupyterbook filename [options] 
Create files for Jupyter Book version: 0.8
Example: doconce jupyterbook filename.do.txt --sep=chapter --sep_section=subsection --show_titles
Try 'doconce jupyterbook --help' for more information.
"""

_registered_cmdline_opts_jupyterbook = [
    ('-h', 'Show this help page'),
    ('--help', 'Show this help page'),
    ('--sep=', 'Specify separator for DocOnce file into jupyter-book chapters. [chapter|section|subsection]'),
    ('--sep_section=', 'Specify separator for DocOnce file into jupyter-book sections. '
                       '[chapter|section|subsection], optional'),
    ('--dest=', 'Destination folder for the content'),
    ('--dest_toc=', 'Destination folder for the _toc.yml file'),
    ('--show_titles', 'Print out the titles detected based on the separator headers. '
                      'This can be helpful for the file passed to the --titles option'),
    ('--titles=', 'File with page titles, i.e. titles in TOC on the left side of the page. Default is \'auto\': '
                  'assign titles based on the separator headers')
]
# Get the list of options for doconce jupyterbook
_legal_cmdline_opts_jupyterbook, _ = list(zip(*_registered_cmdline_opts_jupyterbook))
_legal_cmdline_opts_jupyterbook = list(_legal_cmdline_opts_jupyterbook)

# Get the list of opitions for doconce in general
_legal_command_line_options = [opt for opt, help in globals._registered_command_line_options]


def jupyterbook():
    """
    Create content and TOC for building a jupyter-book version 0.8: https://jupyterbook.org/intro

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

    # Destination directories
    dest = option('dest=', default='./', option_list=_legal_cmdline_opts_jupyterbook)
    dest = folder_checker(dest)
    dest_toc = option('dest_toc=', default='./', option_list=_legal_cmdline_opts_jupyterbook)
    dest_toc = folder_checker(dest_toc)

    # Get options
    sep = option('sep=', default='section', option_list=_legal_cmdline_opts_jupyterbook)
    sep_section = option('sep_section=', default='', option_list=_legal_cmdline_opts_jupyterbook)
    globals.encoding = option('encoding=', default='')
    titles_opt = option('titles=', default='auto', option_list=_legal_cmdline_opts_jupyterbook)
    show_titles_opt = option('show_titles', default=False, option_list=_legal_cmdline_opts_jupyterbook)

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
    filestr = read_file(filename_preprocessed, _encoding=globals.encoding)

    # Remove pandoc's title/author/date metadata, which does not get rendered appropriately in
    # markdown/jupyter-book. Consider to write this metadata to the _config.yml file
    for tag in 'TITLE', 'AUTHOR', 'DATE':
        if re.search(r'^%s:.*' % tag, filestr, re.MULTILINE):
            errwarn('*** warning : Removing heading with %s. Consider to place it in _config.yml' % tag.lower())
        filestr = re.sub(r'^%s:.*' % tag, '', filestr, flags=re.MULTILINE)
    # Remove TOC tag
    tag = 'TOC'
    if re.search(r'^%s:.*' % tag, filestr, re.MULTILINE):
        if re.search(r'^%s:.*' % tag, filestr, re.MULTILINE):
            errwarn('*** warning : Removing the %s tag' % tag.lower())
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

    # Description of relevant variables
    # sep :                 Divide the text in jupyter-book chapters, see --sep
    # chapters :            ['whole chapter 1', 'whole chapter 2', 'summary']
    # chapter_titles :      ['Chapter 1', 'Chapter 2', 'Summary']
    # chapter_fnames :      ['01_mybook', '02_mybook', '03_mybook']
    #
    # If sep_section is not empty, these variables become relevant
    # sep_section :         Subdivide the jupyter-book chapters in sections, see --sep_section
    # section_list :        [['subsection1','subsection2], ['subsection1'] , []]
    # section_title_list :  [['Subsection 1.1', 'Subsection 1.2'], ['Subsection 2.1'], []]
    # section_fname_list :  [['01_01_mybook', '01_02_mybook'], ['02_01_mybook'], []]

    # Split the DocOnce file in jupyter-book chapters
    chapters = split_file(filestr, sep, INLINE_TAGS)
    section_list = [[]] * len(chapters)
    # Extract all jupyter-book sections based on --sep_section
    if sep_section:
        for c, chap in enumerate(chapters):
            # Any text before the first jupyter-book section is part of a jupyter-book chapter,
            # the rest consists in jupyter-book sections
            m = re.search(INLINE_TAGS[sep_section], chap, flags=re.MULTILINE)
            if m:
                pos_sep_section = m.start() if m else 0
                # Write text before the first jupyter-book section as chapter
                chapters[c] = split_file(chap[:pos_sep_section:], sep_section, INLINE_TAGS)[0]
                # The text after the first match of sep_section are jupyter-book sections
                section_list[c] = split_file(chap[pos_sep_section:], sep_section, INLINE_TAGS)

    # Get titles from title file in options
    chapter_titles, section_title_list = read_title_file(titles_opt, chapters, section_list)

    # Define a standard formatter for content filenames and default titles. '%02d_' will result in e.g. '03_mybook'
    def formatter(_list):
        return '%0' + str(max(2, math.floor(math.log(len(_list) + 0.01, 10)) + 1)) + 'd_'

    # Extract and write titles to each jupyter-book chapter/section
    chapter_formatter = formatter(chapters)
    chapters, chapter_titles = titles_to_chunks(chapters, chapter_titles, sep=sep,
                                                chapter_formatter=chapter_formatter, tags=INLINE_TAGS)
    if sep_section:
        for c, sections in enumerate(section_list):
            section_formatter = chapter_formatter % (c + 1) + formatter(sections)
            section_list[c], section_titles = titles_to_chunks(sections, section_title_list[c],
                                                               sep=sep_section, sep2=sep,
                                                               chapter_formatter=section_formatter, tags=INLINE_TAGS)
            section_title_list[c] = section_titles

    # Print out the detected titles if --show_titles was used
    if show_titles_opt:
        if sep_section == '':
            print('\n===== Titles detected using the %s separator:' % sep)
        else:
            print('\n===== Titles detected using the %s and %s separators:' % (sep, sep_section))
        for c, ctitle in enumerate(chapter_titles):
            print(ctitle)
            for stitle in section_title_list[c]:
                print(stitle)
        print('=====')

    # Create a markdown or ipynb for each jupyter-book chapter section
    chapter_fnames = create_content_files(chapters, dest, chapter_formatter+basename)
    section_fname_list = [[]] * len(chapters)
    if sep_section:
        for c, sections in enumerate(section_list):
            section_formatter = chapter_formatter % (c + 1) + formatter(sections)
            section_fnames = create_content_files(sections, dest, section_formatter+basename)
            section_fname_list[c] = section_fnames

    # Create the _toc.yml file
    if sep_section == '':
        yml_text = create_toc_yml(chapter_fnames, chapter_titles, dest=dest, dest_toc=dest_toc)
    else:
        yml_text = create_toc_yml(chapter_fnames, chapter_titles, dest=dest, dest_toc=dest_toc,
                                  section_paths=section_fname_list, section_titles=section_title_list)
    write_file(yml_text, dest_toc + '_toc.yml', _encoding=globals.encoding)
    print('\nWrote _toc.yml and %d chapter files to these folders:\n  %s\n  %s' %
          (len(chapter_fnames), os.path.realpath(dest_toc), os.path.realpath(dest)))


def split_file(filestr, sep, tags):
    """Helper function to split the text of a doconce file by a tag

    Split the text of a doconce file by a separator string and return the chunks of text. Note that the first chunk
    contains any text before the first separator.
    :param str filestr: text string
    :param str sep: chapter|section|subsection
    :param dict tags: tag patterns, e.g. INLINE_TAGS from common.py
    :return: list of text chunks
    :rtype: list[str]
    """
    chunks = []
    if re.search(tags[sep], filestr, flags=re.MULTILINE) is None:
        print('%s pattern not found in file' % sep)
        chunks.append(filestr)
    else:
        pos_prev = 0
        for m in re.finditer(tags[sep], filestr, flags=re.MULTILINE):
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
        chunk = filestr[pos_prev:]
        chunks.append(chunk)
    return chunks


def read_title_file(titles_opt, chapters, section_list):
    """Helper function to read and process a file with titles

    Read the file containing titles and process them according to the number of jupyter-book chapters and sections.
    len(section_list) should be the same as len(chapters), and its elements can be empty lists
    :param str titles_opt: 'auto' or file containing titles
    :param list[str] chapters: DocOnce texts consisting in Jupyter-book chapters
    :param list[list[str]] section_list: DocOnce texts consisting in Jupyter-book sections.
    :return: tuple with chapter and section titles
    :rtype: (list[str], list[list[str]])
    """
    chapter_titles = [''] * len(chapters)
    section_title_list = [[]] * len(chapters)
    if titles_opt is not 'auto':
        input_titles = read_to_list(titles_opt)
        for c in range(len(chapters)):
            chapter_titles[c] = input_titles.pop(0) if len(input_titles) else ''
            section = []
            for s in range(len(section_list[c])):
                section.append(input_titles.pop(0) if len(input_titles) else '')
            section_title_list[c] = section
        if len(input_titles):
            errwarn('*** warning : number of titles is larger than chapters and sections detected. '
                    'These titles will be ignored')
    return chapter_titles, section_title_list


def titles_to_chunks(chunks, title_list, sep, sep2=None, chapter_formatter='%02d_', tags=INLINE_TAGS):
    """Helper function to extract assign titles to jupyter-book chapters/sections (here called chunks)

    Jupyter-book files must have a # header with the title (see doc jupyter-book >
    Types of content source files > Rules for all content types). This function
    extracts title from the title file or from the headers given by the separator
    provided in the options. If no title is found, provide a default title as e.g.
    03_mydoconcefile.

    :param list[str] chunks: list of text string
    :param list[str] title_list: titles for the chunks
    :param str sep: separator: chapter|section|subsection
    :param str sep2: second separator in case the first fails: chapter|section|subsection
    :param dict tags: tag patterns, e.g. INLINE_TAGS from common.py
    :param str chapter_formatter: formatter for default filenames
    :return: tuple with the chunks of text having a # header, and titles
    :rtype: (list[str], list[str])
    """
    title_list_out = title_list.copy()
    # title list can be empty (when --titles='auto')
    if not len(title_list_out):
        title_list_out = [''] * len(chunks)
    # Process each chunk: detect and write title in the header of a chapter/section
    for i, chunk in enumerate(chunks):
        title = ''
        # Try to get any title from headers in each chunk
        if title == '':
            chunk, title = create_title(chunk, sep, tags)
        # Try the second optional separator
        if title == '' and sep2:
            chunk, title = create_title(chunk, sep2, tags)
        # Set default title
        if title == '':
            title = chapter_formatter % (i + 1) + globals.dofile_basename
        # Use title from the titles files.
        if i < len(title_list):
            title = title_list[i]
        # Write to title list and chunk
        # NB: create_title above removed any detected title from chunk, thus avoiding duplicate titles
        title_list_out[i] = title
        chunk = '=' * 9 + ' ' + title + ' ' + '=' * 9 + '\n' + chunk
        chunks[i] = chunk
    return chunks, title_list_out


def create_title(chunk, sep, tags):
    """Helper function to allow doconce jupyterbook to automatically assign titles in the TOC

    If a chunk of text starts with the section specified in sep, lift it up
    to a chapter section. This allows doconce jupyterbook to automatically use the
    section's text as title in the TOC on the left

    :param str chunk: text string
    :param str sep: chapter|section|subsection
    :param dict tags: tag patterns, e.g. INLINE_TAGS from common.py
    :return: tuple with the chunk stripped of its section header, and title
    :rtype: (str, str)
    """
    title = ''
    m = re.search(tags[sep], chunk, flags=re.MULTILINE)
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


def create_content_files(text_list, dest, formatter='%02d_'):
    """Helper function to create markdown or ipynb files from DocOnce texts

    Write a list of DocOnce texts to disk using an appropriate format. The format is markdown (.md) or
    Jupyter Notebook (.ipynb) if the text contains code.
    :param list[str] text_list: list of strings using DocOnce syntax
    :param str dest: destination folder
    :param str formatter: formatter for the filename. Default '%02d_'
    :return: list of filenames
    :rtype: list[str]
    """
    chunk_filenames = []
    for i, text in enumerate(text_list):
        # Convert each text to pandoc, or to ipynb if the text contains any computation
        format = 'pandoc'
        _filestr, code_blocks, code_block_types, tex_blocks = \
            remove_code_and_tex(text, format)
        if len(code_blocks):
            format = 'ipynb'
        chunk_ind = formatter % (i + 1)
        chunk_out, bg_session = doconce2format(text, format)
        chunk_filenames.append(chunk_ind)
        full_file_path = dest + chunk_filenames[i]
        full_file_path += '.md' if format == 'pandoc' else '.ipynb'
        write_file(chunk_out, full_file_path, _encoding=globals.encoding)
    return chunk_filenames


def create_toc_yml(chapter_paths, chapter_titles, dest='./', dest_toc='./', section_paths=None, section_titles=None):
    """Create the content of a _toc.yml file

    Give the lists of paths and titles, return the content of a _toc.yml file

    :param list[str] chapter_paths: list of paths to jupyter-book chapters, i.e. strings that can be used
    after the `file:` section in a _toc.yml
    :param list[str] chapter_titles: list of titles to jupyter-book chapters, i.e. strings that can be used
    after the `title:` section in a _toc.yml
    :param str dest: destination folder for _toc.yml
    :param str dest_toc: destination folder for the chapter files
    :param list[list[str]] section_paths: same as chapter_paths but for jupyter-book sections
    :param list[list[str]] section_titles: same as chapter_titles but for jupyter-book sections
    :return: content of a _toc.yml file
    :rtype: str
    """
    def escape_chars(title):
        """Wrap title in quotes if it contains colons, asterisks, bacticks"""
        if re.search(':', title) or re.search('\*', title) or re.search('\`', title):
            title = title.replace('"', '\\"')
            title = '"' + title + '"'
        return title
    # Get the relative path between the destination folders
    relpath = os.path.relpath(dest, dest_toc)
    if relpath == '.':
        relpath = ''
    else:
        relpath += '/'
    # Produce the text for _toc.yml
    yml_text = ""
    for i, cfname in enumerate(chapter_paths):
        cfroot, _ = os.path.splitext(cfname)
        ctitle = escape_chars(chapter_titles[i])
        if ctitle:
            yml_text += yml_titledpage(relpath + cfroot, ctitle, numbered=False)
            # Do not expand the subsections in the navigation bar
            if i == 0:
                yml_text += yml_expand_sections(False)
            # Write the sections
            if section_paths and len(section_paths[i]):
                yml_text += yml_section(nesting_level=1)
                for j, sfname in enumerate(section_paths[i]):
                    sfroot, _ = os.path.splitext(sfname)
                    stitle = escape_chars(section_titles[i][j])
                    yml_text += yml_nested_section(relpath + sfroot, stitle, nesting_level=1)
        yml_text += '\n'
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
    return "- file: %s\n  numbered: %s\n" % (file, str(numbered).lower())


def yml_titledpage(file, title, numbered=False):
    return "- file: %s\n  title: %s\n  numbered: %s\n" % (file, title, str(numbered).lower())


def yml_section(nesting_level=1):
    return "%ssections:\n" % ('  ' * nesting_level)


def yml_nested_section(file, title, nesting_level=1):
    return '%s  - file: %s\n' % ('  ' * nesting_level, file) + \
           '%s    title: %s\n' % ('  ' * nesting_level, title)


def yml_expand_sections(expand=False):
    return '  expand_sections: %s\n' % str(expand).lower()


def yml_part(part, *files):
    yml = "- part: %s\n  chapters:\n" % part
    for file in files:
        yml += '  - file: %s\n' % file
    return yml + '\n'


def yml_ext_link(url, nesting_level=0, numbered=False):
    return "%s- external: %s\n  numbered: %s\n" % (url, '  ' * nesting_level, numbered)


def yml_header(header):
    return "- header: %s\n" % header


def yml_chapter(file, title, sections, numbered='false', expand_sections=True):
    return "- title: %s\n  file: %s\n  numbered: %s\n  expand_sections: %s\n  sections: %s\n" % \
           (file, title, sections, numbered, str(expand_sections).lower())
