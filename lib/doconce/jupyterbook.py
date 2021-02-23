import os, sys, shutil, re, glob, math
from doconce import globals
from .doconce import read_file, write_file, doconce2format, parse_doconce_filename, handle_index_and_bib, \
    errwarn, _rmdolog, preprocess
from .misc import option, help_print_options, check_command_line_options, system, _abort
from .common import INLINE_TAGS, remove_code_and_tex
import json

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

    # Format citations and add bibliography in DocOnce's html format
    pattern_tag = r'[\w _\-]*'
    pattern = r'cite(?:(\[' + pattern_tag + '\]))?\{(' + pattern_tag + ')\}'
    if re.search(pattern, filestr):
        filestr = handle_index_and_bib(filestr, 'html')

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
    # chapter_titles_auto : ['Header 1', 'Header 2', 'Last Header in DocOnce file']
    # chapter_basenames :   ['01_mybook', '02_mybook', '03_mybook']
    #
    # If sep_section is not empty, these variables become relevant
    # sep_section :         Subdivide the jupyter-book chapters in sections, see --sep_section
    # sec_list :            [['subsection1','subsection2], ['subsection1'] , []]
    # sec_title_list :      [['Subsection 1.1', 'Subsection 1.2'], ['Subsection 2.1'], []]
    # sec_title_list_auto : [['Subheader 1.1', 'Subheader 1.2'], ['Subheader 2.1'], ['Last Subheader in DocOnce file']]
    # sec_basename_list :   [['01_01_mybook', '01_02_mybook'], ['02_01_mybook'], []]

    # Split the DocOnce file in jupyter-book chapters
    chapters = split_file(filestr, INLINE_TAGS[sep])
    sec_list = [[]] * len(chapters)
    sec_title_list_auto = None
    # Extract all jupyter-book sections based on --sep_section
    if sep_section:
        for c, chap in enumerate(chapters):
            # Any text before the first jupyter-book section is part of a jupyter-book chapter,
            # the rest consists in jupyter-book sections
            m = re.search(INLINE_TAGS[sep_section], chap, flags=re.MULTILINE)
            if m:
                pos_sep_section = m.start() if m else 0
                # Write text before the first jupyter-book section as chapter
                chapters[c] = split_file(chap[:pos_sep_section:], INLINE_TAGS[sep_section])[0]
                # The text after the first match of sep_section are jupyter-book sections
                sec_list[c] = split_file(chap[pos_sep_section:], INLINE_TAGS[sep_section])

    # Get titles from title file in options
    chapter_titles, sec_title_list = read_title_file(titles_opt, chapters, sec_list)

    # Extract and write titles to each jupyter-book chapter/section.
    # Also get the basenames for the files to be created later
    def int_formatter(_list):
        return '%0' + str(max(2, math.floor(math.log(len(_list) + 0.01, 10)) + 1)) + 'd_'
    chapter_formatter = int_formatter(chapters)
    chapters, chapter_titles, chapter_titles_auto = titles_to_chunks(chapters, chapter_titles, sep=sep,
                                                chapter_formatter=chapter_formatter, tags=INLINE_TAGS)
    chapter_basenames = [chapter_formatter % (i + 1) + basename for i in range(len(chapters))]
    sec_basename_list = [[]] * len(chapters)
    if sep_section:
        # The following contains section titles extracted  automatically
        sec_title_list_auto = [[]] * len(sec_title_list)
        for c, sections in enumerate(sec_list):
            section_formatter = chapter_formatter % (c + 1) + int_formatter(sections)
            sec_list[c], section_titles, section_titles_auto = titles_to_chunks(sections, sec_title_list[c],
                                                               sep=sep_section, sep2=sep,
                                                               chapter_formatter=section_formatter, tags=INLINE_TAGS)
            sec_title_list[c] = section_titles
            sec_title_list_auto[c] = section_titles_auto
            sec_basename_list[c] = [section_formatter % (i + 1) + basename for i in range(len(sections))]

    # Print out the detected titles if --show_titles was used
    if show_titles_opt:
        if sep_section == '':
            print('\n===== Titles detected using the %s separator:' % sep)
        else:
            print('\n===== Titles detected using the %s and %s separators:' % (sep, sep_section))
        for c in range(len(chapter_titles_auto)):
            print(chapter_titles_auto[c])
            if sep_section:
                for s in range(len(sec_title_list_auto[c])):
                    print(sec_title_list_auto[c][s])
        print('=====')

    # Description of relevant variables
    # all_texts :           ['====== Chapter 1 ======\n Some text', '====== Subsection 1.1 ======\n Some text', ..]
    # all_basenames :       ['01_mybook','01_01_mybook','01_02_mybook','02_mybook']
    # all_suffix :          ['.md','.md','.ipynb','.md']
    # all_fnames :          ['01_mybook.md','01_01_mybook.md','01_02_mybook.ipynb','02_mybook.md']
    # all_titles :          ['Chapter 1','Subsection 1.1', 'Subsection 1.2','Chapter 2']
    # all_nestings :        [0, 1, 1, 0]   # 0 or 1 for jupyter-book chapters or sections, respectively
    #
    # filestr_md :          DocOnce input formatted to pandoc
    # filestr_ipynb :       DocOnce input formatted to ipynb
    # all_texts_md :        list of all chapters and sections from filestr_md
    # all_texts_ipynb :     list of all chapters and sections from filestr_ipynb
    # all_texts_formatted : list of chapters and sections from filestr_ipynb

    # Flatten all texts, basenames, titles, etc for jupyter-book chapters and sections
    all_texts = []
    all_basenames = []
    all_titles = []
    all_nestings = []
    for c in range(len(chapters)):
        all_texts.append(chapters[c])
        all_basenames.append(chapter_basenames[c])
        all_titles.append(chapter_titles[c])
        all_nestings.append(0)
        for s in range(len(sec_list[c])):
            all_texts.append(sec_list[c][s])
            all_basenames.append(sec_basename_list[c][s])
            all_titles.append(sec_title_list[c][s])
            all_nestings.append(1)

    # Create markdown or ipynb filenames for each jupyter-book chapter section
    all_suffix = identify_format(all_texts)
    all_fnames = [b + s for b, s in zip(all_basenames,all_suffix)]

    # Mark the beginning of each jupyter-book chapter and section with its filename in a comment
    all_markings = list(map(lambda x: '!split\n<!-- jupyter-book %s -->\n' % x, all_fnames))
    all_texts = [m + t for m, t in zip(all_markings, all_texts)]

    # Merge all jupyter-book chapters and sections back to a single DocOnce text.
    # Then convert to pandoc and ipynb
    filestr = ''.join(all_texts)
    filestr_md, bg_session = doconce2format(filestr, 'pandoc')
    filestr_ipynb, bg_session = doconce2format(filestr, 'ipynb')

    # Split the texts (formatted to md and ipynb) to individual jupyter-book chapters/sections
    all_texts_md = split_file(filestr_md, '<!-- !split -->\n<!-- jupyter-book .* -->\n')
    all_texts_ipynb = split_ipynb(filestr_ipynb, all_fnames)
    if len(all_texts_md) != len(all_texts_ipynb):
        errwarn('*** error : the lengths of .md and .ipynb files should be the same')
        _abort()

    # Flatten the formatted texts
    all_texts_formatted = [[]] * len(all_fnames)
    for i in range(len(all_fnames)):
        all_texts_formatted[i] = all_texts_md[i]
        if all_fnames[i].endswith('.ipynb'):
            all_texts_formatted[i] = all_texts_ipynb[i]

    # Fix all links whose destination is in a different document
    # e.g. <a href="#Langtangen_2012"> to <a href="02_jupyterbook.html#Langtangen_2012">
    all_texts_formatted = resolve_links_destinations(all_texts_formatted, all_basenames)

    # Write chapters and sections to file
    for i in range(len(all_texts_formatted)):
        write_file(all_texts_formatted[i], dest + all_fnames[i], _encoding=globals.encoding)

    # Create the _toc.yml file
    yml_text = create_toc_yml(all_basenames, titles=all_titles, nesting_levels=all_nestings, dest=dest, dest_toc=dest_toc)

    write_file(yml_text, dest_toc + '_toc.yml', _encoding=globals.encoding)
    print('\nWrote _toc.yml and %d chapter files to these folders:\n  %s\n  %s' %
          (len(all_fnames), os.path.realpath(dest_toc), os.path.realpath(dest)))


def split_file(filestr, separator):
    """Split the text of a doconce file by a regex string.

    Split the text of a doconce file by a separator regex (e.g. the values of
    the INLINE_TAGS dictionary from common.py) and return the chunks of text.
    Note that the first chunk contains any text before the first separator.
    :param str filestr: text string
    :param str separator: regex text, e.g. INLINE_TAGS['chapter'], see common.py
    :return: list of text chunks
    :rtype: list[str]
    """
    chunks = []
    c = re.compile(separator, flags=re.MULTILINE)
    if re.search(c, filestr) is None:
        print('pattern of separator not found in file')
        chunks.append(filestr)
    else:
        pos_prev = 0
        for m in re.finditer(c, filestr):
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


def split_ipynb(ipynb_text, filenames):
    """Split a Jupyter notebook based on filenames present in its blocks

    Given the text of a Jupyter notebook marked with the output filename
    in comments (e.g. <!-- jupyter-book 02_mybook.ipynb -->), return a list of
    Jupyter notebooks separated accordingly.
    :param str ipynb_text: ipynb code marked with individual filenames i.e. <!-- jupyter-book 02_mybook.ipynb -->
    :param list[str] filenames: filenames
    :return: ipynb_texts with the ipynb code for each block
    :rtype: list[str]
    """
    # An ipynb is a python dictionary
    ipynb_dict = json.loads(ipynb_text)
    cells = ipynb_dict.pop('cells')
    # Find the markings with filename in the ipynb blocks
    ind_fname = []
    block_sources = [''.join(c['source']) for c in cells]
    for fname in filenames:
        marking = '<!-- jupyter-book % s -->' % fname
        for b, block in enumerate(block_sources):
            if block.find(marking) > -1:
                ind_fname.append(b)
                break
    if len(ind_fname) != len(filenames):
        errwarn('*** error : could not find all markings in ipynb')
        _abort()
    # Create an ipynb dictionary for each block, then convert to text
    ipynb_texts = [''] * len(filenames)
    for i, ind in enumerate(ind_fname):
        ind2 = None
        if ind + 1 < len(ind_fname):
            ind2 = ind_fname[ind + 1]
        block_dict = ipynb_dict.copy()
        block_dict['cells'] = cells[ind:ind2]
        ipynb_texts[i] = json.dumps(block_dict, indent=1, separators=(',', ':'))
    return ipynb_texts


def read_title_file(titles_opt, chapters, sec_list):
    """Helper function to read and process a file with titles

    Read the file containing titles and process them according to the number of jupyter-book chapters and sections.
    len(sec_list) should be the same as len(chapters), and its elements can be empty lists
    :param str titles_opt: 'auto' or file containing titles
    :param list[str] chapters: DocOnce texts consisting in Jupyter-book chapters
    :param list[list[str]] sec_list: DocOnce texts consisting in Jupyter-book sections.
    :return: tuple with chapter and section titles
    :rtype: (list[str], list[list[str]])
    """
    chapter_titles = []
    sec_title_list = [[]] * len(chapters)
    if titles_opt is not 'auto':
        chapter_titles = [''] * len(chapters)
        input_titles = read_to_list(titles_opt)
        for c in range(len(chapters)):
            chapter_titles[c] = input_titles.pop(0) if len(input_titles) else ''
            section = []
            for _ in range(len(sec_list[c])):
                section.append(input_titles.pop(0) if len(input_titles) else '')
            sec_title_list[c] = section
        if len(input_titles):
            errwarn('*** warning : number of titles is larger than chapters and sections detected. '
                    'These titles will be ignored')
    return chapter_titles, sec_title_list


def titles_to_chunks(chunks, title_list, sep, sep2=None, chapter_formatter='%02d_', tags=INLINE_TAGS):
    """Helper function to extract assign titles to jupyter-book chapters/sections (here called chunks)

    Jupyter-book files must have a # header with the title (see doc jupyter-book >
    Types of content source files > Rules for all content types). This function
    extracts title from the title file or from the headers given by the separator
    provided in the options. If no title is found, provide a default title as e.g.
    03_mydoconcefile.

    :param list[str] chunks: list of text string
    :param list[str] title_list: titles for the chunks. Empty if --titles is us
    :param str sep: separator: chapter|section|subsection
    :param str sep2: second separator in case the first fails: chapter|section|subsection
    :param dict tags: tag patterns, e.g. INLINE_TAGS from common.py
    :param str chapter_formatter: formatter for default filenames
    :return: tuple with the chunks of text having a # header, titles, titles detected
    :rtype: (list[str], list[str], list[str])
    """
    title_list_out = title_list.copy()
    # title list can be empty (when --titles='auto')
    if not len(title_list_out):
        title_list_out = [''] * len(chunks)
    title_list_detected = [''] * len(chunks)
    # Process each chunk: detect and write title in the header of a chapter/section
    for i, chunk in enumerate(chunks):
        title = ''
        # Try to find and remove any title from headers in each chunk
        if title == '':
            chunk, title = create_title(chunk, sep, tags)
        # Same, this time using the second optional separator
        if title == '' and sep2:
            chunk, title = create_title(chunk, sep2, tags)
        # Set default title
        if title == '':
            title = chapter_formatter % (i + 1) + globals.dofile_basename
        # Keep any detected title before overriding them with the file indicated in --titles
        title_list_detected[i] = title
        # Use title from the titles files. This gets skipped if there is no title file
        if i < len(title_list):
            # Skip any empty line in title file
            if title_list[i]:
                title = title_list[i]
        # Write to title list and chunk
        # NB: create_title above removed any detected title from chunk, thus avoiding duplicate titles
        title_list_out[i] = title
        chunk = '=' * 9 + ' ' + title + ' ' + '=' * 9 + '\n' + chunk
        chunks[i] = chunk
    return chunks, title_list_out, title_list_detected


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


def identify_format(text_list):
    """Identify the appropriate formats to convert a list of DocOnce texts.

    Given a list of DocOnce texts, check if they contain code. If so, return the suffix
    '.ipynb' (for the Jupyter Notebook ipynb format), otherwise return '.md' (for
    the pandoc markdown format).
    :param list[str] text_list: list of strings using DocOnce syntax
    :return: list of formats
    :rtype: list[str]
    """
    chunk_formats = [''] * len(text_list)
    for i, text in enumerate(text_list):
        # Convert each text to pandoc, or to ipynb if the text contains any computation
        format = 'pandoc'
        _filestr, code_blocks, code_block_types, tex_blocks = \
            remove_code_and_tex(text, format)
        if len(code_blocks):
            format = 'ipynb'
        chunk_formats[i] += '.md' if format == 'pandoc' else '.ipynb'
    return chunk_formats


def create_toc_yml(basenames, nesting_levels, titles, dest='./', dest_toc='./',     section_paths=None, section_titles=None):
    """Create the content of a _toc.yml file

        Give the lists of paths, titles, and nesting levels, return the content of a _toc.yml file
        :param list[str] basenames: list of file basenames for jupyter-book chapters or sections, i.e.
        strings that can be used after the `file:` section in a _toc.yml
        :param list[str] titles: list of titles to jupyter-book chapters, i.e. strings that can be used
        after the `title:` section in a _toc.yml
        :param list[str] nesting_levels: nesting levels for basenames and titles: # 0 or 1 for jupyter-book
        chapters or sections, respectively
        :param str dest: destination folder for _toc.yml
        :param str dest_toc: destination folder for the chapter files
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
    nesting_prev = 0
    for i, cfname in enumerate(basenames):
        ctitle = escape_chars(titles[i])
        if ctitle:
            nesting = nesting_levels[i]
            if nesting == 0:
                yml_text += '\n'
                yml_text += yml_titledpage(relpath + cfname, ctitle, numbered=False)
            else:
                # Write the sections
                if nesting_prev == 0:
                    yml_text += yml_section(nesting_level=nesting)
                yml_text += yml_nested_section(relpath + cfname, ctitle, nesting_level=nesting)
        nesting_prev = nesting
    yml_text = yml_text.strip('\n')
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


def get_link_destinations(chunk):
    """Find any target of a link in HTML code

    Use regex to find tags with the id or name attribute, which makes them a possible target of a link
    :param str chunk: text string
    :return: destinations, destination_tags
    :rtype: Tuple[list[str], list[str]]
    """
    destinations, destination_tags = [], []
    # html links. label{} has already been converted
    pattern_tag = r'[\w _\-:]'
    pattern = r'<' + pattern_tag + '+ (id|name)=["\'](' + pattern_tag + '+)["\'][^>]*>'
    for m in re.finditer(pattern, chunk):
        match = m.group()
        tag = m.group(2)
        destinations.append(match)
        destination_tags.append(tag)
    return destinations, destination_tags


def fix_links(chunk, tag2file):
    """Find and fix the the destinations of hyperlinks using HTML or markdown syntax

    Fix any link in a string text so that they can target a different html document.
    First use regex on a HTML text to find any HTML or markdown hyperlinks
    (e.g. <a href="#sec1"> or [sec1](#sec1) ). Then use a dictionary to prepend the
    filename to the value of a link's href attribute (e.g. <a href="02_jupyterbook.html#sec1">)
    :param str chunk: text string
    :param dict tag2file: dictionary mapping a tag to a file basename e.g. tag2file['sec1']='02_jupyterbook'
    :return: chunk with fixed links
    :rtype: str
    """
    chunk_out = chunk
    # html links
    pattern_tag = r'[\w _\-:]'
    pattern = r'<' + pattern_tag + '+ href=[\\\]{0,2}["\']#(' + pattern_tag + '+)[\\\]{0,2}["\'][^>]*>'
    for m in re.finditer(pattern, chunk):
        match = m.group()
        tag = m.group(1)
        fixed_tag = match.replace('#' +tag, tag2file.get(tag, tag) + '.html#' + tag)
        chunk_out = chunk_out.replace(match, fixed_tag)
    # markdown links
    pattern = r'\[' + pattern_tag + '+\]\(#(' + pattern_tag + '+)\)'
    for m in re.finditer(pattern, chunk):
        match = m.group()
        tag = m.group(1)
        fixed_tag = match.replace('#' + tag, tag2file.get(tag, tag) + '.html#' + tag)
        chunk_out = chunk_out.replace(match, fixed_tag)
    return chunk_out

def resolve_links_destinations(chunks, chunk_basenames):
    """Fix links in jupyter-book chapters/sections so that they can target destinations in other files

    Prepend a filename to all links' destinations e.g. <a href="#Langtangen_2012"> becomes
    <a href="02_jupyterbook.html#Langtangen_2012">
    :param list[str] chunks: DocOnce texts consisting in Jupyter-book chapters/sections
    :param list[str] chunk_basenames: file basenames for jupyter-book chapters/sections
    :return: chunks with corrected links
    :rtype: Tuple[list[str], list[list[str]]]
    """
    # Flatten the texts and filenames, then get the basenames from filenames
    def strip_end(text, suffix):
        if suffix and text.endswith(suffix):
            return text[:-len(suffix)]
        return text
    all_sects = chunks #+ flatten(sec_list)
    all_basenames = chunk_basenames #+ flatten(sec_basename_list)
    all_basenames = list(map(lambda fname: strip_end(fname, '.md'), all_basenames))
    all_basenames = list(map(lambda fname: strip_end(fname, '.ipynb'), all_basenames))
    # Find all link destinations and create a dictionary tag2file[tag] = destination file
    tag2file = {}
    for i in range(len(all_sects)):
        ch_destinations, ch_destination_tags = get_link_destinations(all_sects[i])
        basename_list = [all_basenames[i]] * len(ch_destinations)
        tag2file.update(zip(ch_destination_tags, basename_list))
    # Fix all href in links by prepending the destination filename
    for c in range(len(chunks)):
        chunks[c] = fix_links(chunks[c], tag2file)
    return chunks


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


def yml_part(part, *files):
    yml = "- part: %s\n  chapters:\n" % part
    for file in files:
        yml += '  - file: %s\n' % file
    return yml + '\n'


def yml_ext_link(url, nesting_level=0, numbered=False):
    return "%s- external: %s\n  numbered: %s\n" % (url, '  ' * nesting_level, numbered)


def yml_header(header):
    return "- header: %s\n" % header


def yml_chapter(file, title, sections, numbered='false'):
    return "- title: %s\n  file: %s\n  numbered: %s\n  sections: %s\n" % \
           (title, file, numbered, sections)
