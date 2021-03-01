from __future__ import print_function
from __future__ import absolute_import
from builtins import range
# https://sphinx.pocoo.org/ext/math.html#

# can reuse most of rst module:
from .rst import *
from .common import align2equations, online_python_tutor, \
     get_legal_pygments_lexers, has_custom_pygments_lexer
from .misc import option, _abort
from .doconce import errwarn
# used in sphinx_dir
import time, shutil, glob, re
from doconce.misc import system, load_preprocessed_doconce_file

# RunestoneInteractive book counters
question_counter = 0
video_counter = 0

edit_markup_warning = False

def sphinx_figure(m):
    result = ''
    # m is a MatchObject

    filename = m.group('filename')
    caption = m.group('caption').strip()

    # Stubstitute DocOnce label by rst label in caption
    # (also, remove final period in caption since caption is used as hyperlink
    # text to figures).

    m_label = re.search(r'label\{(.+?)\}', caption)
    if m_label:
        label = m_label.group(1)
        result += '\n.. _%s:\n' % label
        # remove . at the end of the caption text
        parts = caption.split('label')
        parts[0] = parts[0].rstrip()
        if parts[0] and parts[0][-1] == '.':
            parts[0] = parts[0][:-1]
        parts[0] = parts[0].strip()
        # insert emphasize marks if not latex $ at the
        # beginning or end (math subst does not work for *$I=1$*)
        # or if not boldface or emphasize already in the caption
        caption_font = option('sphinx_figure_captions=', 'emphasize')
        if parts[0] and \
           caption_font == 'emphasize' and \
           not parts[0].startswith('$') and \
           not parts[0].endswith('$') and \
           not '*' in parts[0] and \
           not '_' in parts[0]:
            parts[0] = '*' + parts[0] + '*'
        #caption = '  label'.join(parts)
        caption = parts[0]
        # contrary to rst_figure, we do not write label into caption
        # since we just want to remove the whole label as part of
        # the caption (otherwise done when handling ref and label)

    else:
        if caption and caption[-1] == '.':
            caption = caption[:-1]

    # math is ignored in references to figures, test for math only
    if caption.startswith('$') and caption.endswith('$'):
        errwarn('*** warning: math only in sphinx figure caption (it will be ignored by sphinx, resulting in empty caption)\n  %s\n    FIGURE: [%s' % (caption, filename))

    #stem = os.path.splitext(filename)[0]
    #result += '\n.. figure:: ' + stem + '.*\n'  # utilize flexibility  # does not work yet
    result += '\n.. figure:: ' + filename + '\n'
    opts = m.group('options')
    if opts:
        # opts: width=600 frac=0.5 align=center
        # opts: width=600, frac=0.5, align=center
        info = [s.split('=') for s in opts.split()]
        fig_info = ['   :%s: %s' % (opt, value.replace(',', ''))
                    for opt, value in info
                    if opt not in ['frac', 'sidecap']]
        result += '\n'.join(fig_info)
    if caption:
        result += '\n\n   ' + caption + '\n'
    else:
        result += '\n\n'
    #errwarn('sphinx figure: caption=\n', caption, '\nresult:\n', result)
    return result

def sphinx_movie(m):
    filename = m.group('filename')
    special_movie = '*' in filename or '->' in filename or 'youtu.be' in filename or 'youtube.com' in filename or 'vimeo.com' in filename
    if option('runestone') and not special_movie:
        # Use RunestoneInteractive video environment
        global video_counter
        video_counter += 1
        text = """
.. video:: video_%d
   :controls:

   %s
""" % (video_counter, filename)
        return text
    else:
        # Use plain html code
        return rst_movie(m)


def sphinx_quiz_runestone(quiz):
    quiz_feedback = option('quiz_explanations=', 'on')

    text = ''
    if 'new page' in quiz:
        text += '.. !split\n%s\n%s' % (quiz['new page'], '-'*len(quiz['new page']))

    text += '.. begin quiz\n\n'
    global question_counter
    question_counter += 1
    # Multiple correct answers?
    if sum([1 for choice in quiz['choices'] if choice[0] == 'right']) > 1:
        text += '.. mchoicema:: question_%d' % question_counter + '\n'
    else:
        text += '.. mchoicemf:: question_%d' % question_counter + '\n'

    def fix_text(s, tp='answer'):
        """
        Answers and feedback in RunestoneInteractive book quizzes
        cannot contain math, figure and rst markup. Perform fixes.
        """
        drop = False
        if 'math::' in s:
            errwarn('\n*** warning: quiz %s with math block not supported:' % tp)
            errwarn(s)
            drop = True
        if '.. code-block::' in s:
            errwarn('\n*** warning: quiz %s with code block not supported:' % tp)
            errwarn(s)
            drop = True
        if '.. figure::' in s:
            errwarn('\n*** warning: quiz %s with figure not supported:' % tp)
            errwarn(s)
            drop = True
        if drop:
            return ''
        # Make multi-line paragraph a one-liner
        s = ' '.join(s.splitlines()).rstrip()
        # Fixes
        pattern = r'`(.+?) (<https?.+?)>`__'  # URL
        s = re.sub(pattern, '<a href="\g<2>"> \g<1> </a>', s)
        pattern = r'``(.+?)``'  # verbatim
        s = re.sub(pattern, '<tt>\g<1></tt>', s)
        pattern = r':math:`(.+?)`'  # inline math
        s = re.sub(pattern, '<em>\g<1></em>', s)  # mimic italic....
        pattern = r':\*(.+?)\*'  # emphasize
        s = re.sub(pattern, '\g<1>', s, flags=re.DOTALL)
        return s

    import string
    correct = []
    for i, choice in enumerate(quiz['choices']):
        if i > 4:  # not supported
            errwarn('*** warning: quiz with %d choices gets truncated (first 5)' % len(quiz['choices']))
            break
        letter = string.ascii_lowercase[i]
        text += '   :answer_%s: ' % letter
        answer = fix_text(choice[1], tp='answer')
        if not answer:
            answer = 'Too advanced typesetting prevents the text from being rendered'
        text += answer + '\n'
        if choice[0] == 'right':
            correct.append(letter)
    if correct:
        text += '   :correct: ' + ', '.join(correct) + '\n'
    else:
        errwarn('*** error: correct choice in quiz has index > 5 (max 5 allowed for RunestoneInteractive books)')
        errwarn(quiz['question'])
        _abort()
    for i, choice in enumerate(quiz['choices']):
        if i > 4:  # not supported
            break
        letter = string.ascii_lowercase[i]
        text += '   :feedback_%s: ' % letter  # must be present
        if len(choice) == 3 and quiz_feedback == 'on':
            feedback = fix_text(choice[2], tp='explanation')
            if not feedback:
                feedback = '(Too advanced typesetting prevents the text from being rendered)'
            text += feedback
        text += '\n'

    text += '\n' + indent_lines(quiz['question'], 'sphinx', ' '*3) + '\n\n\n'
    return text

def sphinx_quiz(quiz):
    if option('runestone'):
        return sphinx_quiz_runestone(quiz)
    else:
        return rst_quiz(quiz)


from .latex import fix_latex_command_regex as fix_latex

def sphinx_code(filestr, code_blocks, code_block_types,
                tex_blocks, format):
    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks.

    # default mappings of !bc environments and pygments languages:
    envir2pygments = dict(
        cod='python', pro='python',
        pycod='python', cycod='cython',
        pypro='python', cypro='cython',
        fcod='fortran', fpro='fortran',
        ccod='c', cppcod='c++',
        cpro='c', cpppro='c++',
        mcod='matlab', mpro='matlab',
        plcod='perl', plpro='perl',
        shcod='bash', shpro='bash',
        rbcod='ruby', rbpro='ruby',
        #sys='console',
        sys='text',
        rst='rst',
        css='css', csspro='css', csscod='css',
        dat='text', csv='text', txt='text',
        cc='text', ccq='text',  # not possible with extra indent for ccq
        ipy='ipy',
        xmlcod='xml', xmlpro='xml', xml='xml',
        htmlcod='html', htmlpro='html', html='html',
        texcod='latex', texpro='latex', tex='latex',
        latexcod='latex', latexpro='latex', latex='latex',
        do='doconce',
        pyshell='python',
        pyoptpro='python', pyscpro='python',
        )

    # grab line with: # sphinx code-blocks: cod=python cpp=c++ etc
    # (do this before code is inserted in case verbatim blocks contain
    # such specifications for illustration)
    m = re.search(r'.. *[Ss]phinx +code-blocks?:(.+)', filestr)
    if m:
        defs_line = m.group(1)
        # turn specifications into a dictionary:
        for definition in defs_line.split():
            key, value = definition.split('=')
            envir2pygments[key] = value

    # First indent all code blocks

    for i in range(len(code_blocks)):
        if code_block_types[i].startswith('pyoptpro') and not option('runestone'):
            code_blocks[i] = online_python_tutor(code_blocks[i],
                                                 return_tp='iframe')
        if code_block_types[i].endswith('-h'):
            indentation = ' '*8
        else:
            indentation = ' '*4
        code_blocks[i] = indent_lines(code_blocks[i], format,
                                      indentation)

    # After transforming align environments to separate equations
    # the problem with math labels in multiple eqs has disappeared.
    # (doconce.py applies align2equations, which takes all align
    # envirs and translates them to separate equations, but align*
    # environments are allowed.
    # Any output of labels in align means an error in the
    # align -> equation transformation...)
    math_labels = []
    multiple_math_labels = []  # sphinx has problems with multiple math labels
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], format)
        # extract all \label{}s inside tex blocks and typeset them
        # with :label: tags
        label_regex = fix_latex( r'label\{(.+?)\}', application='match')
        labels = re.findall(label_regex, tex_blocks[i])
        if len(labels) == 1:
            tex_blocks[i] = '   :label: %s\n' % labels[0] + tex_blocks[i]
        elif len(labels) > 1:
            multiple_math_labels.append(labels)
        if len(labels) > 0:
            math_labels.extend(labels)
        tex_blocks[i] = re.sub(label_regex, '', tex_blocks[i])

        # fix latex constructions that do not work with sphinx math
        # (just remove them)
        commands = [r'\begin{equation}',
                    r'\end{equation}',
                    r'\begin{equation*}',
                    r'\end{equation*}',
                    #r'\begin{eqnarray}',
                    #r'\end{eqnarray}',
                    #r'\begin{eqnarray*}',
                    #r'\end{eqnarray*}',
                    #r'\begin{align}',
                    #r'\end{align}',
                    #r'\begin{align*}',
                    #r'\end{align*}',
                    r'\begin{multline}',
                    r'\end{multline}',
                    r'\begin{multline*}',
                    r'\end{multline*}',
                    #r'\begin{split}',
                    #r'\end{split}',
                    #r'\begin{gather}',
                    #r'\end{gather}',
                    #r'\begin{gather*}',
                    #r'\end{gather*}',
                    r'\[',
                    r'\]',
                    # some common abbreviations (newcommands):
                    r'\beqan',
                    r'\eeqan',
                    r'\beqa',
                    r'\eeqa',
                    r'\balnn',
                    r'\ealnn',
                    r'\baln',
                    r'\ealn',
                    r'\beq',
                    r'\eeq',  # the simplest name, contained in others, must come last!
                    ]
        for command in commands:
            tex_blocks[i] = tex_blocks[i].replace(command, '')
        # &=& -> &=
        tex_blocks[i] = re.sub('&\s*=\s*&', ' &= ', tex_blocks[i])
        # provide warnings for problematic environments

    # Replace all references to equations that have labels in math environments:
    for label in math_labels:
        filestr = filestr.replace('(:ref:`%s`)' % label, ':eq:`%s`' % label)

    multiple_math_labels_with_refs = [] # collect the labels with references
    for labels in multiple_math_labels:
        for label in labels:
            ref = ':eq:`%s`' % label  # ref{} is translated to eq:``
            if ref in filestr:
                multiple_math_labels_with_refs.append(label)

    if multiple_math_labels_with_refs:
        errwarn("""
*** warning: detected non-align math environment with multiple labels
    (Sphinx cannot handle this equation system - labels will be removed
    and references to them will be empty):""")
        for label in multiple_math_labels_with_refs:
            errwarn('    label{%s}' % label)
        print()

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'sphinx')

    # Remove all !bc ipy and !bc pyshell since interactive sessions
    # are automatically handled by sphinx without indentation
    # (just a blank line before and after)
    filestr = re.sub(r'^!bc +d?ipy *\n(.*?)^!ec *\n',
                     '\n\g<1>\n', filestr, re.DOTALL|re.MULTILINE)
    filestr = re.sub(r'^!bc +d?pyshell *\n(.*?)^!ec *\n',
                     '\n\g<1>\n', filestr, re.DOTALL|re.MULTILINE)

    # Check if we have custom pygments lexers
    if 'ipy' in code_block_types:
        if not has_custom_pygments_lexer('ipy'):
            envir2pygments['ipy'] = 'python'
    if 'do' in code_block_types:
        if not has_custom_pygments_lexer('doconce'):
            envir2pygments['do'] = 'text'

    # Make correct code-block:: language constructions
    legal_pygments_languages = get_legal_pygments_lexers()
    for key in set(code_block_types):
        if key in envir2pygments:
            if not envir2pygments[key] in legal_pygments_languages:
                errwarn("""*** warning: %s is not a legal Pygments language (lexer)
found in line:
  %s

    The 'text' lexer will be used instead.
""" % (envir2pygments[key], defs_line))
                envir2pygments[key] = 'text'

        #filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
        #                 '\n.. code-block:: %s\n\n' % envir2pygments[key], filestr,
        #                 flags=re.MULTILINE)

        # Check that we have code installed to handle pyscpro
        if 'pyscpro' in filestr and key == 'pyscpro':
            try:
                import icsecontrib.sagecellserver
            except ImportError:
                errwarn("""
*** warning: pyscpro for computer code (sage cells) is requested, but'
    icsecontrib.sagecellserver from https://github.com/kriskda/sphinx-sagecell
    is not installed. Using plain Python typesetting instead.""")
                key = 'pypro'

        if key == 'pyoptpro':
            if option('runestone'):
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                    '\n.. codelens:: codelens_\n   :showoutput:\n\n',
                    filestr, flags=re.MULTILINE)
            else:
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 '\n.. raw:: html\n\n',
                                 filestr, flags=re.MULTILINE)
        elif key == 'pyscpro':
            if option('runestone'):
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 """
.. activecode:: activecode_
   :language: python

""", filestr, flags=re.MULTILINE)
            else:
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 '\n.. sagecellserver::\n\n',
                                 filestr, flags=re.MULTILINE)
        elif key == 'pysccod':
            if option('runestone'):
                # Include (i.e., run) all previous code segments...
                # NOTE: this is most likely not what we want
                include = ', '.join([i for i in range(1, activecode_counter)])
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 """
.. activecode:: activecode_
   :language: python
   "include: %s
""" % include, filestr, flags=re.MULTILINE)
            else:
                errwarn('*** error: pysccod for sphinx is not supported without the --runestone flag\n    (but pyscpro is via Sage Cell Server)')
                _abort()

        elif key == '':
            # any !bc with/without argument becomes a text block:
            filestr = re.sub(r'^!bc$', '\n.. code-block:: text\n\n', filestr,
                             flags=re.MULTILINE)
        elif key.endswith('hid'):
            if key in ('pyhid', 'jshid', 'htmlhid') and option('runestone'):
                # Allow runestone books to run hidden code blocks
                # (replace pyhid by pycod, then remove all !bc *hid)
                for i in range(len(code_block_types)):
                    if code_block_types[i] == key:
                        code_block_types[i] = key.replace('hid', 'cod')

                key2language = dict(py='python', js='javascript', html='html')
                language = key2language[key.replace('hid', '')]
                include = ', '.join([i for i in range(1, activecode_counter)])
                filestr = re.sub(r'^!bc +%s\s*\n' % key,
                                 """
.. activecode:: activecode_
   :language: %s
   :include: %s
   :hidecode:

""" % (language, include), filestr, flags=re.MULTILINE)
            else:
                # Remove hidden code block
                pattern = r'^!bc +%s\n.+?^!ec' % key
                filestr = re.sub(pattern, '', filestr,
                                 flags=re.MULTILINE|re.DOTALL)
        else:
            show_hide = False
            if key.endswith('-h'):
                key_orig = key
                key = key[:-2]
                show_hide = True
            # Use the standard sphinx code-block directive
            if key in envir2pygments:
                pygments_language = envir2pygments[key]
            elif key in legal_pygments_languages:
                pygments_language = key
            else:
                errwarn('*** error: detected code environment "%s"' % key)
                errwarn('    which is not registered in sphinx.py (sphinx_code)')
                errwarn('    or not a language registered in pygments')
                _abort()
            if show_hide:
                filestr = re.sub(r'^!bc +%s\s*\n' % key_orig,
                                 '\n.. container:: toggle\n\n    .. container:: header\n\n        **Show/Hide Code**\n\n    .. code-block:: %s\n\n' % \
                                 pygments_language, filestr, flags=re.MULTILINE)
                # Must add 4 indent in corresponding code_blocks[i], done above
            else:
                filestr = re.sub(r'^!bc +%s\s*\n' % key,
                                 '\n.. code-block:: %s\n\n' % \
                                 pygments_language, filestr, flags=re.MULTILINE)

    # any !bc with/without argument becomes a text block:
    filestr = re.sub(r'^!bc.*$', '\n.. code-block:: text\n\n', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^!ec *\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '', filestr, flags=re.MULTILINE)

    filestr = re.sub(r'^!bt *\n', '\n.. math::\n', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!et *\n', '\n', filestr, flags=re.MULTILINE)
    # Fix lacking blank line after :label:
    filestr = re.sub(r'^(   :label: .+?)(\n *[^ ]+)', r'\g<1>\n\n\g<2>',
                     filestr, flags=re.MULTILINE)

    # Insert counters for runestone blocks
    if option('runestone'):
        codelens_counter = 0
        activecode_counter = 0
        lines = filestr.splitlines()
        for i in range(len(lines)):
            if '.. codelens:: codelens_' in lines[i]:
                codelens_counter += 1
                lines[i] = lines[i].replace('codelens_', 'codelens_%d' %
                                            codelens_counter)
            if '.. activecode:: activecode_' in lines[i]:
                activecode_counter += 1
                lines[i] = lines[i].replace('activecode_', 'activecode_%d' %
                                            activecode_counter)
        filestr = '\n'.join(lines)


    # Final fixes

    filestr = fix_underlines_in_headings(filestr)
    # Ensure blank line before and after comments
    filestr = re.sub(r'([.:;?!])\n^\.\. ', r'\g<1>\n\n.. ',
                     filestr, flags=re.MULTILINE)
    filestr = re.sub(r'(^\.\. .+)\n([^ \n]+)', r'\g<1>\n\n\g<2>',
                     filestr, flags=re.MULTILINE)

    # Line breaks interfer with tables and needs a final blank line too
    lines = filestr.splitlines()
    inside_block = False
    for i in range(len(lines)):
        if lines[i].startswith('<linebreakpipe>') and not inside_block:
            inside_block = True
            lines[i] = lines[i].replace('<linebreakpipe> ', '') + '\n'
            continue
        if lines[i].startswith('<linebreakpipe>') and inside_block:
            lines[i] = '|' + lines[i].replace('<linebreakpipe>', '')
            continue
        if inside_block and not lines[i].startswith('<linebreakpipe>'):
            inside_block = False
            lines[i] = '| ' + lines[i] + '\n'
    filestr = '\n'.join(lines)

    # Remove double !split (TOC with a prefix !split gives two !splits)
    pattern = '^.. !split\s+.. !split'
    filestr = re.sub(pattern, '.. !split', filestr, flags=re.MULTILINE)

    if option('html_links_in_new_window'):
        # Insert a comment to be recognized by automake_sphinx.py such that it
        # can replace the default links by proper modified target= option.
        #filestr = '\n\n.. NOTE: Open external links in new windows.\n\n' + filestr
        # Use JavaScript instead
        filestr = """.. raw:: html

        <script type="text/javascript">
        $(document).ready(function() {
            $("a[href^='http']").attr('target','_blank');
        });
        </script>

""" + filestr


    # Remove too much vertical space
    filestr = re.sub(r'\n{3,}', '\n\n', filestr)

    return filestr

def sphinx_ref_and_label(section_label2title, format, filestr):
    # Special fix early in the process:
    # Deal with !split - by default we place splits before
    # the all the topmost sections
    # (This must be done before labels are put above section
    # headings)
    if '!split' in filestr and not option('sphinx_keep_splits'):
        errwarn('*** warning: new !split inserted (override all existing !split)')
        # Note: the title is at this stage translated to a chapter heading!
        # This title/heading must be removed for the algorithm below to work
        # (remove it, then insert afterwards)
        pattern = r'^.. Document title:\n\n={3,9}.+?={3,9}'
        m = re.search(pattern, filestr, flags=re.MULTILINE)
        title_replacement = '<<<<<<<DOCUMENT TITLE>>>>>>>>>>>>' # "unlikely" str
        if m:
            title = m.group()
            filestr = filestr.replace(title, title_replacement)
        else:
            title = ''

        topmost_section = 0
        for i in [9, 7, 5]:
            if re.search(r'^%s' % ('='*i), filestr, flags=re.MULTILINE):
                topmost_section = i
                errwarn('    before every %s heading %s' % \
                        ('='*topmost_section, '='*topmost_section))
                errwarn('    because this strategy gives a well-functioning')
                errwarn('    table of contents in Sphinx')
                errwarn('    (use --sphinx_keep_splits to enforce your own !split commands)')
                break
        if topmost_section:
            # First remove all !split
            filestr = re.sub(r'^!split *\n', '', filestr, flags=re.MULTILINE)
            # Insert new splits before all topmost sections
            pattern = r'^%s (.+?) %s' % \
                      ('='*topmost_section, '='*topmost_section)
            lines = filestr.splitlines()
            for i in range(len(lines)):
                if re.search(pattern, lines[i]):
                    lines[i] = '!split\n' + lines[i]

            filestr = '\n'.join(lines)
        filestr = filestr.replace(title_replacement, title)

    filestr = ref_and_label_commoncode(section_label2title, format, filestr)

    # replace all references to sections:
    for label in section_label2title:
        filestr = filestr.replace('ref{%s}' % label, ':ref:`%s`' % label)

    # Not of interest after sphinx got equation references:
    #from common import ref2equations
    #filestr = ref2equations(filestr)

    # Replace remaining ref{x} as :ref:`x`
    filestr = re.sub(r'ref\{(.+?)\}', ':ref:`\g<1>`', filestr)

    return filestr

def sphinx_index_bib(filestr, index, citations, pubfile, pubdata):
    # allow user to force the use of original bibliography keys instead of numbered labels
    numbering = not option('sphinx_preserve_bib_keys', False)

    filestr = rst_bib(filestr, citations, pubfile, pubdata, numbering=numbering)
    from .common import INLINE_TAGS

    for word in index:
        # Drop verbatim, emphasize, bold, and math in index
        word2 = word.replace('`', '')
        word2 = word2.replace('$', '').replace('\\', '')
        word2 = re.sub(INLINE_TAGS['bold'],
                       r'\g<begin>\g<subst>\g<end>', word2,
                       flags=re.MULTILINE)
        word2 = re.sub(INLINE_TAGS['emphasize'],
                       r'\g<begin>\g<subst>\g<end>', word2,
                       flags=re.MULTILINE)

        # Typeset idx{word} as ..index::
        if '!' not in word and ',' not in word:
            # .. index:: keyword
            filestr = filestr.replace(
                'idx{%s}' % word,
                '\n.. index:: ' + word2 + '\n')
        elif '!' not in word:
            # .. index::
            #    single: keyword with comma
            filestr = filestr.replace(
                'idx{%s}' % word,
                '\n.. index::\n   single: ' + word2 + '\n')
        else:
            # .. index::
            #    single: keyword; subentry
            word3 = word2.replace('!', '; ')
            filestr = filestr.replace(
                'idx{%s}' % word,
                '\n.. index::\n   single: ' + word3 + '\n')

            # Symmetric keyword; subentry and subentry; keyword
            #filestr = filestr.replace(
            #    'idx{%s}' % word,
            #    '\n.. index::\n   pair: ' + word3 + '\n')
    return filestr

def sphinx_inline_comment(m):
    # Explicit HTML typesetting does not work, we just use bold
    name = m.group('name').strip()
    comment = m.group('comment').strip()

    global edit_markup_warning
    if (not edit_markup_warning) and \
           (name[:3] in ('add', 'del', 'edi') or '->' in comment):
        errwarn('*** warning: sphinx/rst is a suboptimal format for')
        errwarn('    typesetting edit markup such as')
        errwarn('    ' + m.group())
        errwarn('    Use HTML or LaTeX output instead, implement the')
        errwarn('    edits (doconce apply_edit_comments) and then use sphinx.')
        edit_markup_warning = True

    chars = {',': 'comma', ';': 'semicolon', '.': 'period'}
    if name[:4] == 'del ':
        for char in chars:
            if comment == char:
                return r' (**edit %s**: delete %s)' % (name[4:], chars[char])
        return r'(**edit %s**: **delete** %s)' % (name[4:], comment)
    elif name[:4] == 'add ':
        for char in chars:
            if comment == char:
                return r'%s (**edit %s: add %s**)' % (comment, name[4:], chars[char])
        return r' (**edit %s: add**) %s (**end add**)' % (name[4:], comment)
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
            return r'(**%s: remove** %s) (**insert:**)%s (**end insert**)' % (name, orig, new)
        else:
            # Ordinary comment
            return r'[**%s**: %s]' % (name, comment)

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
    if not 'rst' in BLANKLINE:
        # rst.define is not yet ran on these dictionaries, do it:
        from . import rst
        rst.define(FILENAME_EXTENSION,
                   BLANKLINE,
                   INLINE_TAGS_SUBST,
                   CODE,
                   LIST,
                   ARGLIST,
                   TABLE,
                   FIGURE_EXT,
                   INTRO,
                   OUTRO,
                   filestr)

    FILENAME_EXTENSION['sphinx'] = FILENAME_EXTENSION['rst']
    BLANKLINE['sphinx'] = BLANKLINE['rst']
    CODE['sphinx'] = CODE['rst']
    LIST['sphinx'] = LIST['rst']
    FIGURE_EXT['sphinx'] = {
        'search': ('.png', '.gif', '.jpg', '.jpeg'),
        'convert': ('.png', '.gif', '.jpg')}
    CROSS_REFS['sphinx'] = sphinx_ref_and_label
    INDEX_BIB['sphinx'] = sphinx_index_bib
    TABLE['sphinx'] = TABLE['rst']
    EXERCISE['sphinx'] = EXERCISE['rst']
    ENVIRS['sphinx'] = ENVIRS['rst']
    INTRO['sphinx'] = INTRO['rst'].replace(
        '.. Automatically generated reStructuredText',
        '.. Automatically generated Sphinx-extended reStructuredText')

    # make true copy of INLINE_TAGS_SUBST:
    INLINE_TAGS_SUBST['sphinx'] = {}
    for tag in INLINE_TAGS_SUBST['rst']:
        INLINE_TAGS_SUBST['sphinx'][tag] = INLINE_TAGS_SUBST['rst'][tag]

    # modify some tags:
    #INLINE_TAGS_SUBST['sphinx']['math'] = r'\g<begin>:math:`\g<subst>`\g<end>'
    # Important to strip the math expression
    INLINE_TAGS_SUBST['sphinx']['math'] = lambda m: r'%s:math:`%s`%s' % (m.group('begin'), m.group('subst').strip(), m.group('end'))
    #INLINE_TAGS_SUBST['sphinx']['math2'] = r'\g<begin>:math:`\g<latexmath>`\g<end>'
    INLINE_TAGS_SUBST['sphinx']['math2'] = lambda m: r'%s:math:`%s`%s' % (m.group('begin'), m.group('latexmath').strip(), m.group('end'))
    INLINE_TAGS_SUBST['sphinx']['figure'] = sphinx_figure
    INLINE_TAGS_SUBST['sphinx']['movie'] = sphinx_movie
    INLINE_TAGS_SUBST['sphinx']['inlinecomment'] = sphinx_inline_comment
    CODE['sphinx'] = sphinx_code  # function for typesetting code

    ARGLIST['sphinx'] = {
        'parameter': ':param',
        'keyword': ':keyword',
        'return': ':return',
        'instance variable': ':ivar',
        'class variable': ':cvar',
        'module variable': ':var',
        }

    TOC['sphinx'] = lambda s, f: ''  # Sphinx automatically generates a toc
    QUIZ['sphinx'] = sphinx_quiz



#---------------------------------------------------------------------------
def sphinx_code_orig(filestr, format):
    # NOTE: THIS FUNCTION IS NOT USED!!!!!!

    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks.

    # grab #sphinx code-blocks: cod=python cpp=c++ etc line
    # (do this before code is inserted in case verbatim blocks contain
    # such specifications for illustration)
    m = re.search(r'#\s*[Ss]phinx\s+code-blocks?:(.+?)\n', filestr)
    if m:
        defs_line = m.group(1)
        # turn defs into a dictionary definition:
        defs = {}
        for definition in defs_line.split():
            key, value = definition.split('=')
            defs[key] = value
    else:
        # default mappings:
        defs = dict(cod='python',
                    pro='python',
                    pycod='python', cycod='cython',
                    pypro='python', cypro='cython',
                    fcod='fortran', fpro='fortran',
                    ccod='c', cppcod='c++',
                    cpro='c', cpppro='c++',
                    mcod='matlab', mpro='matlab',
                    plcod='perl', plpro='perl',
                    shcod='bash', shpro='bash',
                    rbcod='ruby', rbpro='ruby',
                    sys='console',
                    dat='python',
                    ipy='python',
                    xmlcod='xml', xmlpro='xml', xml='xml',
                    htmlcod='html', htmlpro='html', html='html',
                    texcod='latex', texpro='latex', tex='latex',
                    )
        # (the "python" typesetting is neutral if the text
        # does not parse as python)

    # first indent all code/tex blocks by 1) extracting all blocks,
    # 2) intending each block, and 3) inserting the blocks:
    filestr, code_blocks, tex_blocks = remove_code_and_tex(filestr, format)
    for i in range(len(code_blocks)):
        code_blocks[i] = indent_lines(code_blocks[i], format)
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], format)
        # remove all \label{}s inside tex blocks:
        tex_blocks[i] = re.sub(fix_latex(r'\label\{.+?\}', application='match'),
                              '', tex_blocks[i])
        # remove those without \ if there are any:
        tex_blocks[i] = re.sub(r'label\{.+?\}', '', tex_blocks[i])
        # side effects: `label{eq1}` as verbatim, but this is mostly a
        # problem for doconce documentation and can be rephrased...

        # fix latex constructions that do not work with sphinx math
        commands = [r'\begin{equation}',
                    r'\end{equation}',
                    r'\begin{equation*}',
                    r'\end{equation*}',
                    r'\begin{eqnarray}',
                    r'\end{eqnarray}',
                    r'\begin{eqnarray*}',
                    r'\end{eqnarray*}',
                    r'\begin{align}',
                    r'\end{align}',
                    r'\begin{align*}',
                    r'\end{align*}',
                    r'\begin{multline}',
                    r'\end{multline}',
                    r'\begin{multline*}',
                    r'\end{multline*}',
                    r'\begin{split}',
                    r'\end{split}',
                    r'\begin{gather}',
                    r'\end{gather}',
                    r'\begin{gather*}',
                    r'\end{gather*}',
                    r'\[',
                    r'\]',
                    # some common abbreviations (newcommands):
                    r'\beqan',
                    r'\eeqan',
                    r'\beqa',
                    r'\eeqa',
                    r'\balnn',
                    r'\ealnn',
                    r'\baln',
                    r'\ealn',
                    r'\beq',
                    r'\eeq',  # the simplest, contained in others, must come last!
                    ]
        for command in commands:
            tex_blocks[i] = tex_blocks[i].replace(command, '')
        tex_blocks[i] = re.sub('&\s*=\s*&', ' &= ', tex_blocks[i])
        # provide warnings for problematic environments
        #if '{alignat' in tex_blocks[i]:
        #    errwarn('*** warning: the "alignat" environment will give errors in Sphinx:\n' + tex_blocks[i] + '\n')


    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'rst')

    for key in defs:
        language = defs[key]
        if not language in legal_pygments_languages:
            raise TypeError('%s is not a legal Pygments language '\
                            '(lexer) in line with:\n  %s' % \
                                (language, defs_line))
        #filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
        #                 '\n.. code-block:: %s\n\n' % defs[key], filestr,
        #                 flags=re.MULTILINE)
        cpattern = re.compile(r'^!bc\s+%s\s*\n' % key, flags=re.MULTILINE)
        filestr, n = cpattern.subn('\n.. code-block:: %s\n\n' % defs[key], filestr)
        errwarn(key + ' ' + n)
        if n > 0:
            errwarn('sphinx: %d subst %s by %s' % (n, key, defs[key]))

    # any !bc with/without argument becomes a py (python) block:
    #filestr = re.sub(r'^!bc.+\n', '\n.. code-block:: py\n\n', filestr,
    #                 flags=re.MULTILINE)
    cpattern = re.compile(r'^!bc.+$', flags=re.MULTILINE)
    filestr = cpattern.sub('\n.. code-block:: py\n\n', filestr)

    filestr = re.sub(r'^!ec *\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!bt *\n', '\n.. math::\n\n', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^!et *\n', '\n\n', filestr,
                     flags=re.MULTILINE)

    return filestr

def sphinx_code_newmathlabels(filestr, format):
    # NOTE: THIS FUNCTION IS NOT USED!!!!!!

    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks.

    # grab #sphinx code-blocks: cod=python cpp=c++ etc line
    # (do this before code is inserted in case verbatim blocks contain
    # such specifications for illustration)
    m = re.search(r'#\s*[Ss]phinx\s+code-blocks?:(.+?)\n', filestr)
    if m:
        defs_line = m.group(1)
        # turn defs into a dictionary definition:
        defs = {}
        for definition in defs_line.split():
            key, value = definition.split('=')
            defs[key] = value
    else:
        # default mappings:
        defs = dict(cod='python', pycod='python', cppcod='c++',
                    fcod='fortran', ccod='c',
                    pro='python', pypro='python', cpppro='c++',
                    fpro='fortran', cpro='c',
                    sys='console', dat='python')
        # (the "python" typesetting is neutral if the text
        # does not parse as python)

    # First indent all code/tex blocks by 1) extracting all blocks,
    # 2) intending each block, and 3) inserting the blocks.
    # In between, handle the math blocks.

    filestr, code_blocks, tex_blocks = remove_code_and_tex(filestr, format)
    for i in range(len(code_blocks)):
        code_blocks[i] = indent_lines(code_blocks[i], format)

    math_labels = []
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], format)
        # extract all \label{}s inside tex blocks and typeset them
        # with :label: tags
        label_regex1 = fix_latex(r'\label\{(.+?)\}', application='match')
        label_regex2 = fix_latex( r'label\{(.+?)\}', application='match')
        math_labels.extend(re.findall(label_regex1, tex_blocks[i]))
        tex_blocks[i] = re.sub(label_regex1,
                              r' :label: \g<1> ', tex_blocks[i])
        # handle also those without \ if there are any:
        math_labels.extend(re.findall(label_regex2, tex_blocks[i]))
        tex_blocks[i] = re.sub(label_regex2, r' :label: \g<1> ', tex_blocks[i])

    # replace all references to equations:
    for label in math_labels:
        filestr = filestr.replace(':ref:`%s`' % label, ':eq:`%s`' % label)

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'rst')

    for key in defs:
        language = defs[key]
        if not language in legal_pygments_languages:
            raise TypeError('%s is not a legal Pygments language '\
                            '(lexer) in line with:\n  %s' % \
                                (language, defs_line))
        #filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
        #                 '\n.. code-block:: %s\n\n' % defs[key], filestr,
        #                 flags=re.MULTILINE)
        cpattern = re.compile(r'^!bc\s+%s\s*\n' % key, flags=re.MULTILINE)
        filestr = cpattern.sub('\n.. code-block:: %s\n\n' % defs[key], filestr)

    # any !bc with/without argument becomes a py (python) block:
    #filestr = re.sub(r'^!bc.+\n', '\n.. code-block:: py\n\n', filestr,
    #                 flags=re.MULTILINE)
    cpattern = re.compile(r'^!bc.+$', flags=re.MULTILINE)
    filestr = cpattern.sub('\n.. code-block:: py\n\n', filestr)

    filestr = re.sub(r'!ec *\n', '\n', filestr)
    #filestr = re.sub(r'!ec\n', '\n', filestr)
    #filestr = re.sub(r'!ec\n', '', filestr)
    filestr = re.sub(r'!bt *\n', '\n.. math::\n   :nowrap:\n\n', filestr)
    filestr = re.sub(r'!et *\n', '\n\n', filestr)

    return filestr


def _usage_sphinx_dir():
    print("Usage: doconce sphinx_dir short-title=\"some short title\" version=0.1 theme=themename dirname=sphinx-rootdir "
          "toc_depth=2 intersphinx  doconcefile [--runestone]\n\n"
          "Additional command-line arguments: theme_dir=directoryname conf.py=filename logo=filename favicon=filename\n\n"
          "The sphinx_dir command creates a directory (dirname) for compiling a sphinx version of a doconce document. The option --runestone "
          "makes a directory for RunestoneInteractive documents (slightly different from a standard sphinx directory).\n\n"
          "The default dirname is \"sphinx-rootdir\". The intersphinx option is used for links to other sphinx documents.\n\n"
          "toc_depth governs the depth in the table of contents, default value is 2 (sections and subsections are included).\n\n"
          "The copyright in the footer of Sphinx documents is based on the AUTHOR field(s) in doconcefile, and if no "
          "{copyright...} specification is given in the field(s), all authors are listed.\n\n"
          "The theme option can be chosen from basic sphinx themes (agogo, basic, bizstyle, classic, default, epub, haiku, "
          "nature, pyramid, scrolls, sphinxdoc, traditional), extra themes that can be installed (alabaster, bootstrap, "
          "cloud, redcloud, solarized, sphinx_rtd_theme, 'draft', 'flat', 'modern5', 'minimal5', 'responsive'),or themes "
          "that come with DocOnce (ADCtheme, agni, basicstrap, bloodish, cbc, fenics, "
          "fenics_classic, fenics_minimal1, fenics_minimal2, jal, pylons, scipy_lectures, slim-agogo, uio, uio2, vlinux-theme). "
          "See bundled/sphinx_themes/install.txt for how to install extra themes.\n\n"
          "A custom theme can also be specified by giving a \"_themes-like\" directory: theme_dir=dirname, where dirname "
          "can be any path (DocOnce will copy this directory to the sphinx root directory). Note that this must be the "
          "*theme directory* with files like layout.html and theme.conf (not the entire Python package for a theme.) "
          "Alternatively, one can use a standard theme, but provide one's own tailored conf.py file through the conf.py=filename option.\n" 
          "If the file (filename) has empty strings for the project and copyright, those values as well as the variables"
          " depending on these values will get content based on the title, author, and copyright from the DocOnce source"
          " file mydoc.do.txt. (It is recommended to leave project and copyright as empty strings, and latex_documents, "
          "texinfo_documents, and man_pages as empty lists.)\n\n---\n\n"
          "The steps for copying files to the sphinx directory and compiling the document is done by an automatically generated script:\n\n"
          "  python automake_sphinx.py [doconce format options]\n\n"
          "The master file can be split into parts. Here is the typical code:\n\n"
          "  doconce format sphinx mydoc.do.txt\n"
          "  doconce split_rst mydoc\n"
          "  doconce sphinx_dir mydoc  # or with a lot of options...\n"
          "  python automake_sphinx.py\n\n"
          "Note that split_rst must be run prior to sphinx_dir!")

def sphinx_dir():
    if len(sys.argv) < 2:
        _usage_sphinx_dir()
        sys.exit(1)

    # Grab title, author/copyright, version from the command line
    # (set default values first)
    short_title = None
    version = '1.0'
    theme = 'classic'
    doconce_files = []
    sphinx_rootdir = 'sphinx-rootdir'
    toc_depth = 2
    conf_py = None
    theme_dir = None
    logo = None
    favicon = None
    intersphinx = False
    runestone = False
    # For backward compatibility we need to detect title, copyright and author
    # on the command line
    title_cml = copyright_cml = author_cml = None

    # Get user's info
    for arg in sys.argv[1:]:
        if arg.startswith('short_title='):
            short_title = arg.split('=')[1]
        elif arg.startswith('version='):
            version = arg.split('=')[1]
        elif arg.startswith('dirname='):
            sphinx_rootdir = arg.split('=')[1]
        elif arg.startswith('toc_depth='):
            toc_depth = int(arg.split('=')[1])
        elif arg.startswith('theme='):
            theme = arg.split('=')[1]
        elif arg.startswith('conf.py='):
            conf_py = arg.split('=')[1]
        elif arg.startswith('theme_dir='):
            theme_dir = arg.split('=')[1]
        elif arg.startswith('logo='):
            logo = arg.split('=')[1]
        elif arg.startswith('favicon='):
            favicon = arg.split('=')[1]
        elif arg.startswith('intersphinx'):
            intersphinx = True
        elif arg == '--runestone':
            runestone = True
        elif arg.startswith('author='):
            author_cml = arg.split('=')[1]
        elif arg.startswith('copyright='):
            copyright_cml = arg.split('=')[1]
        elif arg.startswith('title='):
            title_cml = arg.split('=')[1]
        else:
            doconce_files.append(arg)

    if not doconce_files:
        print('must have (at least one) doconce file as argument')
        print('doconce sphinx_dir somefile.do.txt')
        sys.exit(1)
    try:
        import sphinx
    except ImportError:
        print('Unable to import sphinx. Install sphinx from sphinx.pocoo.org.')
        print('On Debian systems, install the \'python-sphinx\' package.')
        sys.exit(1)
    if float(sphinx.__version__[:3]) < 1.1:
        print('Abort: sphinx version >= 1.1 required')
        sys.exit(1)

    if len(doconce_files) > 1:
        print('can only specify one main doconce file')
        print('(here you have specified %s)' % ', '.join(doconce_files))
        sys.exit(1)

    filename = doconce_files[0]
    if filename.endswith('do.txt'):
        filename = filename[:-7]
    else:
        if not os.path.isfile(filename + '.do.txt'):
            print('%s.do.txt does not exist' % filename)
            sys.exit(1)

    parts = glob.glob('._%s[0-9][0-9][0-9].rst' % filename)
    parts = [part[:-4] for part in sorted(parts)]

    # Extract title, author from .do.txt file (try mako processed file first)
    fstr = load_preprocessed_doconce_file(filename)
    if 'TITLE:' in fstr:
        for line in fstr.splitlines():
            if line.startswith('TITLE:'):
                title = line[6:].strip()
                break # use the first TITLE spec
        if title_cml is not None:
            print('*** error: cannot give title= on the command line when TITLE is specified in the DocOnce file', filename)
            sys.exit(1)
    else:
        # No TITLE in the DocOnce file
        if title_cml is None:
            title = 'No title'
        else:
            title = title_cml

    if short_title is None:
        # Default is to use title
        short_title = title

    import doconce.doconce
    # The following can be misleading if there are examples on
    # various AUTHOR: in e.g. vertabim code in the .do.txt file
    authors_and_institutions, dummy1, dummy2, dummy3, dummy4, dummy5 = \
         doconce.doconce.interpret_authors(fstr, 'sphinx')
    if authors_and_institutions:
        author = [a for a, i, e in authors_and_institutions]

        if len(author) == 1:
            author = author[0]
        else:
            author = ', '.join(author[:-1]) + ' and ' + author[-1]
        if author_cml is not None:
            print('*** error: cannot give author= on the command line when AUTHOR is specified in the DocOnce file', filename)
            sys.exit(1)
    else:
        if author_cml is None:
            author = 'No author'
        else:
            author = author_cml

    from doconce.common import get_copyfile_info
    copyright_filename = '.' + filename + '.copyright'
    copyright_ = get_copyfile_info(copyright_filename=copyright_filename,
                                   format='sphinx')
    # copyright_ is None if no copyright and no doconce citation
    # copyright_ is 'Made with DocOnce' if just citation and no copyright,
    # otherwise it is a text with authors/institutions and optionally citation
    # in conf.py we *always* include a copyright with authors, so if
    # copyright is None or just 'Made with DocOnce' we add authors and year
    if isinstance(copyright_, str) and 'DocOnce' in copyright_:
        cite_doconce = True
        if copyright_ == 'Made with DocOnce':
            copyright_ = None  # No specified authors or institutions
    else:
        cite_doconce = False

    if copyright_ is None:
        # No copyright given in the file, use copyright= from command
        # line, if it was provided, or use this year and author
        if copyright_cml is None:
            # use this year, author
            this_year = time.asctime().split()[4]
            copyright_ = this_year + ', ' + author
            if cite_doconce:
                copyright_ += '. Made with DocOnce'
        else:
            copyright_ = copyright_cml
    else:
        if copyright_cml is not None:
            print('*** error: cannot give copyright= on the command line when {coppyright...} is specified as part of AUTHOR in the DocOnce file', filename)
            sys.exit(1)

    chapters = '=========' in fstr
    if chapters:
        toc_depth += 1

    if theme_dir is not None and conf_py is None:
        print('theme_dir is given, but then also conf_py must be specified')
        print('Abort!')
        sys.exit(1)

    print('title:', title)
    print('author:', author)
    print('copyright:', copyright_)
    print('theme:', theme)
    print()
    time.sleep(1.5)

    #make_conf_py_runestone(themes, theme, title, short_title,
    #                       copyright_, logo, favicon, intersphinx)

    if os.path.isdir(sphinx_rootdir):
        shutil.rmtree(sphinx_rootdir)
    if sys.platform.startswith('win'):
        f1 = open('tmp_sphinx_gen.bat', 'w')
        f2 = open('tmp_sphinx_gen.inp', 'w')
        f1.write("echo Making %(sphinx_rootdir)s\n"
                 "mkdir %(sphinx_rootdir)s\n"
                 "sphinx-quickstart < tmp_sphinx_gen.inp\n" % vars())
        f2.write(("%(sphinx_rootdir)s\n"
                  "n\n"
                  "_\n"
                  "%(title)s\n"
                  "%(author)s\n"
                  "%(version)s\n"
                  "%(version)s\n"
                  "en\n"
                  ".rst\n"
                  "index\n"
                  "y\n"
                  "y\n"
                  "n\n"
                  "n\n"
                  "n\n"
                  "n\n"
                  "n\n"
                  "y\n"
                  "n\n"
                  "y\n"
                  "y\n"
                  "y\n") % vars())
        f1.close()
        f2.close()
        system('tmp_sphinx_gen',
               failure_info='to generate sphinx directory')
        #os.remove('tmp_sphinx_gen.bat')
        #os.remove('tmp_sphinx_gen.inp')
    else:
        f = open('tmp_sphinx_gen.sh', 'w')
        f.write(("#!/bin/bash\n"
                 "echo Making %(sphinx_rootdir)s\n"
                 "mkdir %(sphinx_rootdir)s\n"
                 "sphinx-quickstart <<EOF\n"
                 "%(sphinx_rootdir)s\n"
                 "n\n"
                 "_\n"
                 "%(title)s\n"
                 "%(author)s\n"
                 "%(version)s\n"
                 "%(version)s\n"
                 "en\n"
                 ".rst\n"
                 "index\n"
                 "y\n"
                 "y\n"
                 "n\n"
                 "n\n"
                 "n\n"
                 "n\n"
                 "n\n"
                 "y\n"
                 "n\n"
                 "y\n"
                 "y\n"
                 "y\n\n"
                 "EOF") % vars())
        f.close()
        system('sh tmp_sphinx_gen.sh',
               failure_info='to generate sphinx directory')
        #os.remove('tmp_sphinx_gen.sh')
    os.chdir(sphinx_rootdir)

    sphinx_basic_themes = 'agogo basic bizstyle classic default epub haiku nature pyramid scrolls sphinxdoc traditional'.split()
    # See what is installed of other themes
    sphinx_potentially_installed_themes = 'alabaster bootstrap cloud redcloud solarized impressjs sphinx_rtd_theme dark ' \
                                          'flat modern5 minimal5 responsive'.split()
    sphinx_installed_themes = []
    try:
        import alabaster
        sphinx_installed_themes.append('alabaster')
    except ImportError:
        pass
    try:
        import sphinx_bootstrap_theme
        sphinx_installed_themes.append('bootstrap')
    except ImportError:
        pass
    try:
        import cloud_sptheme
        sphinx_installed_themes.append('cloud')
        sphinx_installed_themes.append('redcloud')
    except ImportError:
        pass
    try:
        import sphinxjp.themes.impressj
        sphinx_installed_themes.append('impressjs')
    except ImportError:
        pass
    try:
        import sphinxjp.themes.solarized
        sphinx_installed_themes.append('solarized')
    except ImportError:
        pass
    try:
        import sphinx_rtd_theme
        sphinx_installed_themes.append('sphinx_rtd_theme')
    except ImportError:
        pass
    try:
        import tinkerer
        import tinkerer.paths
        sphinx_installed_themes += ['boilerplate', 'dark', 'flat', 'modern5', 'minimal5', 'responsive']
    except ImportError:
        pass

    if theme_dir is None:
        # Copy themes
        import doconce.common
        install_dir = doconce.common.where()
        shutil.copy(os.path.join(install_dir, 'sphinx_themes.zip'), os.curdir)
        devnull = 'NUL' if sys.platform.startswith('win') else '/dev/null'
        system('unzip sphinx_themes.zip > %s' % devnull)
        os.remove('sphinx_themes.zip')
        os.rename('sphinx_themes', '_themes')
        files = sorted(glob.glob(os.path.join('_themes', '*')))
        themes = [name[8:] for name in files
                  if os.path.isdir(name)] + \
                  sphinx_basic_themes + sphinx_installed_themes

        if conf_py is None:
            print('These Sphinx themes were found:', ', '.join(sorted(themes)))
            make_conf_py(themes, theme, title, short_title, copyright_,
                         logo, favicon, intersphinx)
    else:
        # Copy theme_dir
        if not os.path.isdir('_themes'):
            os.mkdir('_themes')
        shutil.copy(theme_dir, os.path.join('_themes', theme_dir))


    if conf_py is not None:
        shutil.copy(os.path.join(os.pardir, conf_py), 'conf.py')

        # Edit the file appropriately if title, author, or copyright are given
        with open('conf.py', 'r') as f:
            conf_text = f.read()

        # Make conf.py ready for latex, man pages, texinfo, epub etc
        # with current doc info
        pattern = r'latex_documents = \[.*?\]'
        replacement = r"latex_documents = [('index', 'doc.tex', project, u'%s',  'manual'),]" % author
        conf_text = re.sub(pattern, replacement, conf_text,
                           flags=re.DOTALL)

        pattern = r'man_pages = \[.*?^# '
        replacement = r"man_pages = [('index', 'doc', project, [u'%s'], 1),]\n\n# " % author
        conf_text = re.sub(pattern, replacement, conf_text,
                           flags=re.DOTALL|re.MULTILINE)

        pattern = r'texinfo_documents = \[.*?\]'
        replacement = r"texinfo_documents = [('index', 'doc', project, u'%s', 'doc', 'One line description of project.', 'Miscellaneous'),]" % author
        conf_text = re.sub(pattern, replacement, conf_text,
                           flags=re.DOTALL)

        pattern = r'''project *= *u?['"](.*?)['"]'''
        m = re.search(pattern, conf_text)
        if m:
            if m.group(1).strip() == '':
                # No title found, take the one from .do.txt
                conf_text = re.sub(pattern, "project = u'%s'" % title,
                                   conf_text)
                conf_text = re.sub(r'html_title.+', "html_title = project", conf_text)
                conf_text = re.sub(r'epub_title.+', "epub_title = project", conf_text)
        pattern = '''^short_title *= *project'''
        m = re.search(pattern, conf_text, flags=re.MULTILINE)
        if short_title != title and m:
            # Update short_title
            conf_text = re.sub(pattern, "short_title = u'%s'" % short_title,
                               conf_text, flags=re.MULTILINE)

        # Fix copyright issues
        pattern = r'''copyright *= *u?['"](.*?)['"]'''
        m = re.search(pattern, conf_text)
        if m:
            if m.group(1).strip() == '':
                # No copyright found, take the one from .do.txt
                conf_text = re.sub(pattern, "copyright = u'%s'" % copyright_,
                                   conf_text)
                conf_text = re.sub(r'epub_copyright.+', "epub_copyright = u'%s'" % copyright_, conf_text)
                conf_text = re.sub(r'epub_author.+', "epub_author = u'%s'" % author, conf_text)
                conf_text = re.sub(r'epub_publisher.+', "epub_publisher = u'%s'" % author, conf_text)
        with open('conf.py', 'w') as f:
            f.write(conf_text)

    # Make a script that can generate all available sphinx themes
    f = open('make_themes.sh', 'w')
    f.write("#!/bin/sh\n"
            "# Make all themes given on the command line (or if no themes are\n"
            "# given, make all themes in _themes/)\n"
            "\n"
            "if [ $# -gt 0 ]; then\n"
            "    themes=$@\n"
            "else\n"
            "    themes=\"%s\"\n"
            "fi\n"
            "\n"
            "for theme in $themes; do\n"
            "    echo \"building theme $theme...\"\n"
            "    doconce subst -m \"^html_theme =.*$\" \"html_theme = '$theme'\" conf.py\n"
            "    make clean\n"
            "    make html\n"
            "    mv -f _build/html sphinx-$theme\n"
            "done\n"
            "echo\n"
            "echo \"Here are the built themes:\"\n"
            "ls -d sphinx-*\n"
            "echo \"for i in sphinx-*; do google-chrome $i/index.html; done\"\n"
            "\n" % (' '.join(themes)))
    f.close()
    os.chmod('make_themes.sh', 0o755)

    # Make index.rst main file for the document
    f = open('index.rst', 'w')
    if parts:
        files = parts
    else:
        files = [filename]
    filenames = '\n   '.join(files)
    title_underline = '='*len(title)
    dropdown_scrollbar = '' if not 'bootstrap' in theme else ("\n"
                                                              ".. raw:: html\n\n"
                                                              "  <style type=\"text/css\">\n"
                                                              "    .dropdown-menu {\n"
                                                              "      height: auto;\n"
                                                              "      max-height: 400px;\n"
                                                              "      overflow-x: hidden;\n"
                                                              "  }\n"
                                                              "  </style>\n")
    f.write((".. Master file automatically created by doconce sphinx_dir\n\n"
             "%(dropdown_scrollbar)s\n"
             "%(title)s\n"
             "%(title_underline)s\n\n"
             "Contents:\n\n"
             ".. toctree::\n"
             "   :maxdepth: %(toc_depth)s\n\n"
             "   %(filenames)s") % vars())

    # Do we have idx{} commands in the document? Cannot just check fstr,
    # that is the top/master file. Need to check the entire file.
    dotext = load_preprocessed_doconce_file(filename, dirpath=os.pardir)
    if 'idx{' in dotext:
        f.write(("\nIndex\n"
                 "=====\n\n"
                 "* :ref:`genindex`\n"))
    f.close()
    os.chdir(os.pardir)

    # Make the automake_sphinx.py compilation file for automatically
    # preparing the sphinx document, copying various files, and running make

    f = open('automake_sphinx.py', 'w')
    f.write(("#!/usr/bin/env python\n"
            "# -*- coding: utf-8 -*-\n"
            "# Autogenerated file (by doconce sphinx_dir).\n"
            "# Purpose: create HTML Sphinx version of document \"%(filename)s\".\n"
            "#\n"
            "# Note: doconce clean removes this file, so if you edit the file,\n"
            "# rename it to avoid automatic removal.\n\n"
            "# To force compilation of the doconce file to sphinx format, remove\n"
            "# the sphinx (.rst) file first.\n"
            "#\n"
            "# Command-line arguments are transferred to the \"doconce format sphinx\"\n"
            "# compilation command.\n"
            "#\n\n"
            "import glob, sys, os, subprocess, shutil, logging\n"
            "logging.basicConfig(\n"
            "    filename='automake_sphinx.log', filemode='w', level=logging.DEBUG,\n"
            "    format='%%(asctime)s - %%(levelname)s - %%(message)s',\n"
            "    datefmt='%%Y.%%m.%%d %%I:%%M:%%S %%p')\n\n\n"
            "command_line_options = ' '.join(['\"%%s\"' %% arg for arg in sys.argv[1:]])\n\n"
            "sphinx_rootdir = '%(sphinx_rootdir)s'\n"
            "source_dir = sphinx_rootdir\n\n"
            "if not os.path.isdir(sphinx_rootdir):\n"
            "    print(\"\"\"*** error: %%(sphinx_rootdir)s does not exist. This means unsuccessful\n"
            "    doconce sphinx_dir command. Try to upgrade to latest DocOnce version.\n"
            "    (The script tmp_sphinx_gen.sh runs sphinx-quickstart - it may have failed.)\n"
            "\"\"\" %% vars())\n"
            "    sys.exit(1)\n\n"
            "def system(cmd, capture_output=False, echo=True):\n"
            "    if echo:\n"
            "        print('running', cmd)\n"
            "    if capture_output:\n"
            "        failure, outtext = subprocess.getstatusoutput(cmd) # Unix/Linux only\n"
            "    else:\n"
            "        failure = os.system(cmd)\n"
            "    if failure:\n"
            "        print('Could not run', cmd)\n"
            "        logging.critical('Could not run %%s' %% cmd)\n"
            "        sys.exit(1)\n"
            "    if capture_output:\n"
            "        return outtext\n\n") % vars())
    if parts == []:
        f.write(("# Compile the doconce file if a sphinx version of it is not found\n"
                 "filename = '%(filename)s'\n"
                 "if not os.path.isfile(filename + '.rst'):\n"
                 "    # Transform doconce format to sphinx format and copy to sphinx directory\n"
                 "    cmd = 'doconce format sphinx %%s %%s' %% (filename, command_line_options)\n"
                 "    print(cmd)\n"
                 "    logging.info('running %%s' %% cmd)\n"
                 "    system(cmd)\n\n"
                 "    # Fix: utf-8 encoding for non-English chars\n"
                 "    cmd = 'doconce guess_encoding %%s.rst' %% filename\n"
                 "    enc = system(cmd, capture_output=True)\n"
                 "    if enc == \"iso-8859-1\":\n"
                 "        # sphinx does not like non-English characters in iso-8859-1\n"
                 "        cmd = 'doconce change_encoding iso-8859-1 utf-8 %%s.rst' %% filename\n"
                 "        logging.info('running %%s' %% cmd)\n"
                 "        system(cmd)\n\n"
                 "# Copy generated sphinx file to sphinx directory\n"
                 "logging.info('copy: %%s.rst to %%s and reading the content' %% (filename, source_dir))\n"
                 "shutil.copy('%%s.rst' %% filename, source_dir)\n"
                 "with open('%%s.rst' %% filename, 'r') as rst_file:\n"
                 "    rst_text = rst_file.read()\n") % vars())
    else:
        # user has run doconce split_rst so doconce format is already
        # run and all parts must be copied
        parts_names = str(parts)
        f.write(("# Copy generated sphinx files to sphinx root directory\n"
                 "filename = '%(filename)s'\n"
                 "rst_text = ''  # holds all text in all .rst files\n"
                 "for part in %(parts_names)s:\n"
                 "    shutil.copy('%%s.rst' %% part, source_dir)\n"
                 "    with open('%%s.rst' %% part, 'r') as rst_file:\n"
                 "        rst_text += rst_file.read()\n")
                % vars())

    f.write(("\n# Copy figures and movies directories\n"
             "figdirs = glob.glob('fig*') + glob.glob('mov*')\n"
             "for figdir in figdirs:\n"
             "    destdir = None\n"
             "    if figdir.startswith('fig'):\n"
             "        # Figures can be anywhere (copied by sphinx to _images)\n"
             "        destdir = os.path.join(source_dir, figdir)\n"
             "    elif figdir.startswith('mov'):\n"
             "        # Movies must be in _static\n"
             "        # Copy only the movies if they are needed through local filenames\n"
             "        if '\"'+ figdir in rst_text or '<' + figdir in rst_text:\n"
             "            destdir = os.path.join(source_dir, '_static', figdir)\n"
             "    if destdir is not None and os.path.isdir(figdir) and not os.path.isdir(destdir):\n"
             "        msg = 'copy: %%s to %%s' %% (figdir, destdir)\n"
             "        print(msg)\n"
             "        logging.info(msg)\n"
             "        shutil.copytree(figdir, destdir)\n\n"
             "# Copy needed figure files in current dir (not in fig* directories)\n"
             "for rstfile in glob.glob(os.path.join(source_dir, '*.rst')) + glob.glob(os.path.join(source_dir, '.*.rst')):\n"
             "    f = open(rstfile, 'r')\n"
             "    text = text_orig = f.read()\n"
             "    f.close()\n"
             "    import re\n"
             "    figfiles = [name.strip() for name in\n"
             "                re.findall('.. figure:: (.+)', text)]\n"
             "    local_figfiles = [name for name in figfiles if not os.sep in name]\n\n"
             "    for name in figfiles:\n"
             "        basename = os.path.basename(name)\n"
             "        if name.startswith('http') or name.startswith('ftp'):\n"
             "            pass\n"
             "        else:\n"
             "            if not os.path.isfile(os.path.join(source_dir, basename)):\n"
             "                msg = 'copy: %%s to %%s' %% (name, source_dir)\n"
             "                print(msg)\n"
             "                logging.info(msg)\n"
             "                shutil.copy(name, source_dir)\n"
             "            if name not in local_figfiles:\n"
             "                # name lies in another directory, make local reference to it\n"
             "                # since it is copied to source_dir\n"
             "                text = text.replace('.. figure:: %%s' %% name,\n"
             "                                    '.. figure:: %%s' %% basename)\n"
             "                logging.info('edit: figure path to %%s' %% basename)\n"
             "    if text != text_orig:\n"
             "        f = open(rstfile, 'w')\n"
             "        f.write(text)\n"
             "        f.close()\n\n"
             "# Copy linked local files, placed in _static*, to source_dir/_static\n"
             "staticdirs = glob.glob('_static*')\n"
             "for staticdir in staticdirs:\n"
             "    if os.listdir(staticdir):  # copy only if non-empty dir\n"
             "        cmd = 'cp -r %%(staticdir)s/* %%(source_dir)s/_static/' %% vars()\n"
             "        logging.info('running %%s' %% cmd)\n"
             "        system(cmd)\n\n"
             "# Create custom files in _static/_templates?\n"
             "if '**Show/Hide Code**' in rst_text:\n"
             "    with open(os.path.join(sphinx_rootdir, '_templates', 'page.html'), 'w') as f:\n"
             "        f.write(\"\"\"\n"
             "{%% extends \"!page.html\" %%}\n\n"
             "{%% set css_files = css_files + [\"_static/custom.css\"] %%}\n\n"
             "{%% block footer %%}\n"
             " <script type=\"text/javascript\">\n"
             "    $(document).ready(function() {\n"
             "        $(\".toggle > *\").hide();\n"
             "        $(\".toggle .header\").show();\n"
             "        $(\".toggle .header\").click(function() {\n"
             "            $(this).parent().children().not(\".header\").toggle(400);\n"
             "            $(this).parent().children(\".header\").toggleClass(\"open\");\n"
             "        })\n"
             "    });\n"
             "</script>\n"
             "{%% endblock %%}\n"
             "\"\"\")\n"
             "    with open(os.path.join(sphinx_rootdir, '_static', 'custom.css'), 'w') as f:\n"
             "        f.write(\"\"\"\n"
             ".toggle .header {\n"
             "    display: block;\n"
             "    clear: both;\n"
             "}\n\n"
             ".toggle .header:after {\n"
             "    content: \" ▼\";\n"
             "}\n\n"
             ".toggle .header.open:after {\n"
             "    content: \" ▲\";\n"
             "}\n"
             "\"\"\")\n\n") % vars())
    # (Note: must do cp -r above since shutil.copy/copytree cannot copy a la cp -r)
    f.write(("os.chdir(sphinx_rootdir)\n"
             "if '--runestone' not in sys.argv:\n"
             "    # Compile web version of the sphinx document\n"
             "    print(os.getcwd())\n"
             "    logging.info('running make clean and make html')\n"
             "    system('make clean')\n"
             "    system('make html')\n\n"
             "    print('Fix generated files:',)\n"
             "    os.chdir('_build/html')\n"
             "    for filename in glob.glob('*.html') + glob.glob('.*.html'):\n"
             "        print(filename)\n"
             "        f = open(filename, 'r'); text = f.read(); f.close()\n"
             "        text_orig = text\n"
             "        # Fix double title in <title> tags\n"
             "        text = re.sub(r'<title>(.+?) &mdash;.+?</title>', r'<title>\g<1></title>', text)\n"
             "        # Fix untranslated math (e.g. in figure captions and raw html)\n"
             "        text = re.sub(r':math:`(.+?)`', r' \( \g<1> \) ', text)\n"
             "        # Fix links to movies\n"
             "        text = re.sub(r'''src=['\"](mov.+?)['\"]''', r'src=\"_static/\g<1>\"', text)\n"
             "        # Fix movie frames in javascript player\n"
             "        text = text.replace(r'.src = \"mov', '.src = \"_static/mov')\n"
             "        # Fix admonition style\n"
             "        text = text.replace('</head>', '''\n"
             "       <style type=\"text/css\">\\n"
             "         div.admonition {\n"
             "           background-color: whiteSmoke;\n"
             "           border: 1px solid #bababa;\n"
             "         }\n"
             "       </style>\n"
             "      </head>\n"
             "    ''')\n\n"
             "        # Check if external links should pop up in separate windows\n"
             "        if '.. NOTE: Open external links in new windows.' in text:\n"
             "            text = text.replace('<a class=\"reference external\"',\n"
             "                                '<a class=\"reference external\" target=\"_blank\"')\n\n"
             "        # Make a link for doconce citation in copyright\n"
             "        if '. Made with DocOnce' in text:\n"
             "            text = text.replace('. Made with DocOnce', '')\n"
             "            text = text.replace('      Created using <a href=\"https://sphinx-doc.org/\">Sphinx', '      "
             "Created using <a href=\"https://github.com/doconce/doconce\">DocOnce</a> and <a href=\"https://sphinx-doc.org/\">Sphinx')\n"
             "        # Remove (1), (2), ... numberings in identical headings\n"
             "        headings_wno = re.findall(r'(?<=(\d|\"))>([^>]+?)          \((\d+)\)<', text)\n"
             "        for dummy, heading, no in headings_wno:\n"
             "            heading = heading.strip()\n"
             "            text = re.sub(r'>%%s +\(%%d\)<' %%\n"
             "                          (re.escape(heading), int(no)),\n"
             "                          '>%%s<' %% heading, text)\n"
             "            text = re.sub(r'title=\"%%s +\(%%d\)\"' %%\n"
             "                          (re.escape(heading), int(no)),\n"
             "                          r'title=\"%%s\"' %% heading, text)\n\n"
             "        if os.path.isfile(filename + '.old~~'):\n"
             "            os.remove(filename + '.old~~')\n"
             "        f = open(filename, 'w'); f.write(text); f.close()\n"
             "        if text != text_orig:\n"
             "            logging.info('edit: %%s' %% filename)\n"
             "    os.chdir('../../')\n"             
             "    print('\\n\\ngoogle-chrome %(sphinx_rootdir)s/_build/html/index.html\\n')\n\n"
             "else:\n"
             "    # Add directory for RunestoneInteractive book\n"
             "    use_runestonebooks_style = True  # False: use user-chosen style\n"
             "    print(\"\"\"\n\ncreate RunestoneInteractive directory\n\"\"\")\n"
             "    sys.path.insert(0, os.curdir)\n"
             "    import conf as source_dir_conf  # read data from conf.py\n\n"
             "    if not os.path.isdir('RunestoneTools'):\n"
             "        system('git clone https://github.com/RunestoneInteractive/RunestoneComponents.git')\n"
             "    os.chdir('RunestoneComponents')\n"
             "    logging.info('creating RunestoneInteractive directory')\n\n"
             "    # Edit conf.py\n"
             "    # This one does not work anymore: run runestone init instead,\n"
             "    print('RunestoneInteractive has recently changed its setup - must abort')\n"
             "    sys.exit(1)\n"
             "    # it's the file runestone/__main__.py and function init()\n"
             "    # Need to build a bash script that runs the command and feeds the answers\n"
             "    # See also https://github.com/RunestoneInteractive/RunestoneComponents\n"
             "    f = open('conf.py.prototype', 'r');  text = f.read();  f.close()\n"
             "    text = text.replace('<ENTER YOUR PROJECT NAME HERE>', source_dir_conf.project)\n"
             "    text = text.replace('<INSERT YOUR PROJECT NAME HERE>', source_dir_conf.project)\n"
             "    text = text.replace('<ENTER YOUR COPYRIGHT NOTICE HERE>', source_dir_conf.copyright)\n"
             "    text = text.replace('<INSERT YOUR PROJECT NAME OR OTHER TITLE HERE>', source_dir_conf.project)\n"
             "    text = text.replace('<INSERT YOUR PROJECT NAME OR OTHER SHORT TITLE HERE>', source_dir_conf.project)\n"
             "    text = text.replace('html_theme_path = [\"_templates\"]', 'html_theme_path = [\"_templates\", \"../_themes\"]')\n"
             "    if not use_runestonebooks_style:\n"
             "        text = text.replace(\"html_theme = 'sphinx_bootstrap'\", \"html_theme = '%%s'\" %% source_dir_conf.html_theme)\n"
             "        text = re.sub(r'html_theme_options = \{.+?\}', 'html_theme_options = ' + str(source_dir_conf.html_theme_options) if "
             "hasattr(source_dir_conf, 'html_theme_options') else 'html_theme_options = {}', text, flags=re.DOTALL)\n"
             "    f = open('conf.py', 'w');  f.write(text);  f.close()\n\n"
             "    # Copy .rst files from sphinx dir\n"
             "    rst_files = [os.path.join(os.pardir, 'index.rst')] + glob.glob(os.path.join(os.pardir, '*.rst')) + "
             "glob.glob(os.path.join(os.pardir, '._*.rst'))\n"
             "    for filename in rst_files:\n"
             "        print('copying', filename, 'to _sources')\n"
             "        logging.info('copy: %%s to _sources' %% filename)\n"
             "        shutil.copy(filename, '_sources')\n"
             "    print('*** running paver build to build the RunestoneInteractive book')\n"
             "    logging.info('running paver build to create the RunestoneInteractive book')\n"
             "    system('paver build')\n\n"
             "    print('\\n\\ngoogle-chrome %(sphinx_rootdir)s/RunestoneTools/build/index.html')\n") % vars())
    f.close()
    os.chmod('automake_sphinx.py', 0o755)
    print(("'automake_sphinx.py' contains the steps to (re)compile the sphinx\n"
           "version. You may want to edit this file, or run the steps manually,\n"
           "or just run it by\n\n"
           "  python automake_sphinx.py\n"
           ))
    # Add scrollbars to navigation bar dropdown menu in case of bootstrap
    # (this css style is already written to index.rst)
    if 'bootstrap' in theme:
        with open(filename + '.rst', 'r') as f:
            text = f.read()
        # Trick to get scrollbar in dropdown menus
        text = (".. raw:: html\n\n"
                "  <style type=\"text/css\">\n"
                "    .dropdown-menu {\n"
                "      height: auto;\n"
                "      max-height: 400px;\n"
                "      overflow-x: hidden;\n"
                "  }\n"
                "  </style>\n\n") + text
        with open(filename + '.rst', 'w') as f:
            f.write(text)

def make_conf_py(themes, theme, title, short_title, copyright_,
                 logo, favicon, intersphinx):
    f = open('conf.py', 'r');  text = f.read();  f.close()

    # Compensate bug July 2016 in Sphinx
    text = text.replace('# import os', 'import os')

    # sphinx-quickstart sets copyright to authors with current year,
    # we customize this
    text = re.sub(r"copyright = u'(\d\d\d\d),.+",
                  r"copyright = u'%s'" % copyright_, text)

    # Propagate short_title
    pattern1 = '^short_title *='
    m = re.search(pattern1, text, flags=re.MULTILINE)
    if not m:
        # No short_title found, insert short_title after project
        pattern2 = r'(project *=.+)'
        if short_title == title:
            text = re.sub(pattern2, "\g<1>\nshort_title = project", text)
        else:
            text = re.sub(pattern2, "\g<1>\nshort_title = u'%s'" % short_title, text)
    else:
        if short_title != title:
            # User has given a short_title, must update short_title =
            text = re.sub(pattern1, "short_title = u'%s'" % short_title, text, flags=re.MULTILINE)

    pattern = r'#? *html_short_title *=.+'
    text = re.sub(pattern, 'html_short_title = short_title', text)
    # html_title defaults to "<project> v<release> documentation",
    # let it just be the title
    text = re.sub(r'# *html_title =.+', 'html_title = project', text)


    themes_list = ["html_theme = '%s'" % theme] + \
                  ["#html_theme = '%s'" % t for t in sorted(themes)]
    themes_code = (r"\ncheck_additional_themes= [\n"
                   r"   'solarized', 'cloud', 'redcloud',\n"
                   r"   'alabaster', 'bootstrap', 'impressjs']\n\n"
                   r"for theme in check_additional_themes:\n"
                   r"    if html_theme == theme:\n"
                   r"        if not theme in additional_themes_installed:\n"
                   r"            raise ImportError(\n"
                   r"                'html_theme = \"%s\", but this theme is not installed. %s' % (theme, additional_themes_url[theme]))\n\n\n\n"
                   r"if html_theme == 'solarized':\n"
                   r"    pygments_style = 'solarized'\n\n")
    text = re.sub(r"^html_theme = '.+?' *$",
                  '\n'.join(themes_list) + themes_code,
                  text, flags=re.MULTILINE)

    # Remove html_theme_path and html_static_path deep down in the conf.py
    # file because we need them earlier and must initialize them ourselves
    text = re.sub(r'# Add any paths that contain custom themes.+\n# *html_theme_path = \[\]', "", text)
    text = re.sub(r"# Add any paths that contain custom static.+?\n# *html_static_path = \['_static'\]", "", text)
    # Paths are added below when we try to import various themes in conf.py

    extensions = ("extensions = [\n"
                  "          #'sphinx.ext.pngmath',\n"
                  "          #'sphinx.ext.jsmath',\n"
                  "          'sphinx.ext.mathjax',\n"
                  "          #'matplotlib.sphinxext.mathmpl',\n"
                  "          #'matplotlib.sphinxext.only_directives',\n"
                  "          'matplotlib.sphinxext.plot_directive',\n"
                  "          'sphinx.ext.autodoc',\n"
                  "          'sphinx.ext.doctest',\n"
                  "          'sphinx.ext.viewcode',\n"
                  "          'sphinx.ext.intersphinx',\n"
                  "          'sphinx.ext.inheritance_diagram',\n"
                  "          'IPython.sphinxext.ipython_console_highlighting']\n\n"
                  "#pngmath_dvipng_args = ['-D 200', '-bg Transparent', '-gamma 1.5']  # large math fonts (200)\n\n"
                  "# Make sphinx aware of the DocOnce lexer\n"
                  "def setup(app):\n"
                  "    from sphinx.highlighting import lexers\n"
                  "    from doconce.misc import DocOnceLexer\n"
                  "    lexers['doconce'] = DocOnceLexer()\n\n"
                  "# Check which additional themes that are installed\n"
                  "additional_themes_installed = []\n"
                  "additional_themes_url = {}\n\n"
                  "# Add any paths that contain custom themes here, relative to this directory.\n"
                  "html_theme_path = ['_themes']\n"
                  "# Add any paths that contain custom static files (such as style sheets) here,\n"
                  "# relative to this directory. They are copied after the builtin static files,\n"
                  "# so a file named \"default.css\" will overwrite the builtin \"default.css\".\n"
                  "html_static_path = ['_static']\n\n"
                  "try:\n"
                  "    import alabaster\n"
                  "    additional_themes_installed.append('alabaster')\n"
                  "except ImportError:\n"
                  "    additional_themes_url['alabaster'] = 'pip install alabaster'\n\n"
                  "try:\n"
                  "    import sphinxjp.themes.solarized\n"
                  "    additional_themes_installed.append('solarized')\n"
                  "except ImportError:\n"
                  "    additional_themes_url['solarized'] = 'https://pypi.org/project/sphinxjp.themes.solarized: pip install --exists-action i sphinxjp.themes.solarized --upgrade'\n\n"
                  "try:\n"
                  "    import cloud_sptheme as csp\n"
                  "    additional_themes_installed.append('cloud')\n"
                  "    additional_themes_installed.append('redcloud')\n"
                  "except ImportError:\n"
                  "    url = 'https://pypi.org/project/cloud_sptheme/: pip install --exists-action i cloud_sptheme --upgrade'\n"
                  "    additional_themes_url['cloud'] = url\n"
                  "    additional_themes_url['redcloud'] = url\n\n\n"
                  "'''\n"
                  "# FIXME: think we do not need to test on basicstrap, but some themes\n"
                  "# need themecore and we must test for that\n"
                  "try:\n"
                  "    import sphinxjp.themecore\n"
                  "    if not 'sphinxjp.themecore' in extensions:\n"
                  "        extensions += ['sphinxjp.themecore']\n"
                  "    additional_themes_installed.append('basicstrap')\n"
                  "except ImportError:\n"
                  "    # Use basicstrap as an example on a theme with sphinxjp.themecore (??)\n"
                  "    additional_themes_url['basicstrap'] = 'https://github.com/tell-k/sphinxjp.themes.basicstrap: pip install --exists-action i sphinx-bootstrap-theme --upgrade'\n"
                  "'''\n\n"
                  "try:\n"
                  "    import sphinxjp.themes.impressjs\n"
                  "    additional_themes_installed.append('impressjs')\n"
                  "except ImportError:\n"
                  "    additional_themes_url['impressjs'] = 'https://github.com/shkumagai/sphinxjp.themes.impressjs: pip install --exists-action i egg=sphinxjp.themes.impressjs --upgrade'\n\n"
                  "try:\n"
                  "    import sphinx_bootstrap_theme\n"
                  "    additional_themes_installed.append('bootstrap')\n"
                  "except ImportError:\n"
                  "    additional_themes_url['bootstrap'] = 'https://github.com/ryan-roemer/sphinx-bootstrap-theme: pip install --exists-action i sphinx-bootstrap-theme --upgrade'\n\n"
                  "try:\n"
                  "    import icsecontrib.sagecellserver\n"
                  "    extensions += ['icsecontrib.sagecellserver']\n"
                  "except ImportError:\n"
                  "    # pip install --exists-action i sphinx-sagecell --upgrade\n"
                  "    pass\n\n"
                  "# Is the document built on readthedocs.org? If so, don't import\n"
                  "on_rtd = os.environ.get('READTHEDOCS', None) == 'True'\n"
                  "if not on_rtd:  # only import and set the theme if we're building docs locally\n"
                  "    try:\n"
                  "        import sphinx_rtd_theme\n"
                  "        additional_themes_installed.append('sphinx_rtd_theme')\n"
                  "    except ImportError:\n"
                  "        additional_themes_url['sphinx_rtd_theme'] = 'pip install sphinx_rtd_theme'\n\n"
                  "tinker_themes = [\n"
                  "  'dark', 'flat', 'modern5', 'minimal5', 'responsive']\n"
                  "# https://tinkerer.me/index.html\n"
                  "# See Preview Another Theme in the sidebar of the above URL\n"
                  "try:\n"
                  "    import tinkerer\n"
                  "    import tinkerer.paths\n"
                  "    additional_themes_installed += tinker_themes\n"
                  "except ImportError:\n"
                  "    for theme in tinker_themes:\n"
                  "        additional_themes_url[theme] = 'pip install tinkerer --upgrade'\n\n")
    # Intersphinx mapping: the look up of URLs can take quite
    # some time, so this is not enabled by default
    if intersphinx:
        extensions += ("\n"
                       "#intersphinx_mapping = {}\n"
                       "# Example configuration for intersphinx for references to the\n"
                       "# the Sphinx documents for Python, NumPy, SciPy, Matplotlib.\n"
                       "# (Domos in https://scipy-lectures.github.com, typically :mod:`scipy.io`\n"
                       "# or :class:`numpy.ndarray` or :func:`math.asin`)\n"
                       "intersphinx_mapping = {\n"
                       "    'python': ('https://docs.python.org/2.7', None),\n"
                       "    'numpy': ('https://docs.scipy.org/doc/numpy', None),\n"
                       "    'scipy': ('https://docs.scipy.org/doc/scipy/reference', None),\n"
                       "    'mpl': ('https://matplotlib.org/', None),\n"
                       "}\n")

    #'matplotlib.sphinxext.ipython_directive',
    #'matplotlib.sphinxext.ipython_console_highlighting',
    # are now in IPython, but not installed as Python modules

    text = re.sub(r'extensions = .*?\]', extensions, text, flags=re.DOTALL)
    html_theme_options = (r"# See https://sphinx.pocoo.org/theming.html for options\n"
                          r"if html_theme in ('default', 'classic'):\n"
                          r"    # pygments_style =\n"
                          r"    html_theme_options = {\n"
                          r"       'rightsidebar': 'false',  # 'true'\n"
                          r"       'stickysidebar': 'false', # Make the sidebar \"fixed\" so that it doesn't scroll out of view for long body content.  This may not work well with all browsers.  Defaults to false.\n"
                          r"       'collapsiblesidebar': 'false', # Add an *experimental* JavaScript snippet that makes the sidebar collapsible via a button on its side. *Doesn't work together with \"rightsidebar\" or \"stickysidebar\".* Defaults to false.\n"
                          r"       'externalrefs': 'false', # Display external links differently from internal links.  Defaults to false.\n"
                          r"       # For colors and fonts, see default/theme.conf for default values\n"
                          r"       #'footerbgcolor':    # Background color for the footer line.\n"
                          r"       #'footertextcolor:'  # Text color for the footer line.\n"
                          r"       #'sidebarbgcolor':   # Background color for the sidebar.\n"
                          r"       #'sidebarbtncolor':  # Background color for the sidebar collapse button (used when *collapsiblesidebar* is true).\n"
                          r"       #'sidebartextcolor': # Text color for the sidebar.\n"
                          r"       #'sidebarlinkcolor': # Link color for the sidebar.\n"
                          r"       #'relbarbgcolor':    # Background color for the relation bar.\n"
                          r"       #'relbartextcolor':  # Text color for the relation bar.\n"
                          r"       #'relbarlinkcolor':  # Link color for the relation bar.\n"
                          r"       #'bgcolor':          # Body background color.\n"
                          r"       #'textcolor':        # Body text color.\n"
                          r"       #'linkcolor':        # Body link color.\n"
                          r"       #'visitedlinkcolor': # Body color for visited links.\n"
                          r"       #'headbgcolor':      # Background color for headings.\n"
                          r"       #'headtextcolor':    # Text color for headings.\n"
                          r"       #'headlinkcolor':    # Link color for headings.\n"
                          r"       #'codebgcolor':      # Background color for code blocks.\n"
                          r"       #'codetextcolor':    # Default text color for code blocks, if not set differently by the highlighting style.\n"
                          r"       #'bodyfont':         # Font for normal text.\n"
                          r"       #'headfont':         # Font for headings.\n"
                          r"    }\n\n"
                          r"elif html_theme == 'alabaster':\n"
                          r"    # Doc: https://pypi.python.org/pypi/alabaster\n"
                          r"    extensions += ['alabaster']\n"
                          r"    html_theme_path += [alabaster.get_path()]\n"
                          r"    html_theme_sidebars = {\n"
                          r"      '**': [\n"
                          r"        'about.html',\n"
                          r"        'navigation.html',\n"
                          r"        'relations.html',\n"
                          r"        'searchbox.html',\n"
                          r"        'donate.html',\n"
                          r"      ]\n"
                          r"    }\n\n"
                          r"elif html_theme == 'sphinx_rtd_theme':\n"
                          r"    # Doc: https://pypi.python.org/pypi/sphinx_rtd_theme\n"
                          r"    if not on_rtd:\n"
                          r"        html_theme_path += [sphinx_rtd_theme.get_html_theme_path()]\n\n"
                          r"elif html_theme == 'sphinxdoc':\n"
                          r"    # Doc: https://sphinx-doc.org/theming.html\n"
                          r"    html_theme_options = {\n"
                          r"       'nosidebar': 'false',  # 'true'\n"
                          r"    }\n\n"
                          r"elif html_theme == 'solarized':\n"
                          r"    extensions += ['sphinxjp.themecore', 'sphinxjp.themes.solarized']\n\n"
                          r"elif html_theme in ('cloud', 'redcloud'):\n"
                          r"    html_theme_path += [csp.get_theme_dir()]\n\n"
                          r"elif html_theme == 'impressjs':\n"
                          r"    html_theme_path += [csp.get_theme_dir()]\n"
                          r"    if not 'sphinxjp.themecore' in extensions:\n"
                          r"        extensions += ['sphinxjp.themecore']\n\n"
                          r"elif html_theme == 'scrolls':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    pass\n"
                          r"    #html_theme_options = {\n"
                          r"       #'headerbordercolor':,\n"
                          r"       #'subheadlinecolor:',\n"
                          r"       #'linkcolor':,\n"
                          r"       #'visitedlinkcolor':\n"
                          r"       #'admonitioncolor':\n"
                          r"    #}\n\n"
                          r"elif html_theme == 'agogo':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    pass\n\n"
                          r"elif html_theme == 'nature':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    html_theme_options = {\n"
                          r"       'nosidebar': 'false',  # 'true'\n"
                          r"    }\n\n"
                          r"elif html_theme == 'traditional':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    html_theme_options = {\n"
                          r"       'nosidebar': 'false',  # 'true'\n"
                          r"    }\n\n"
                          r"elif html_theme == 'haiku':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    html_theme_options = {\n"
                          r"       'nosidebar': 'false',  # 'true'\n"
                          r"    }\n\n"
                          r"elif html_theme == 'pyramid':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    html_theme_options = {\n"
                          r"       'nosidebar': 'false',  # 'true'\n"
                          r"    }\n\n"
                          r"elif html_theme == 'bizstyle':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    html_theme_options = {\n"
                          r"       'nosidebar': 'false',  # 'true'\n"
                          r"       'rightsidebar': 'false',  # 'true'\n"
                          r"    }\n\n"
                          r"elif html_theme == 'epub':\n"
                          r"    # Doc: https://sphinx.pocoo.org/theming.html\n"
                          r"    html_theme_options = {\n"
                          r"       'relbar1': 'true',\n"
                          r"       'footer': 'true',\n"
                          r"    }\n\n"
                          r"elif html_theme == 'basicstrap':\n"
                          r"    html_theme_options = {\n"
                          r"       'rightsidebar': 'false',  # 'true'\n"
                          r"    }\n\n"
                          r"elif html_theme == 'bootstrap':\n"
                          r"    # Doc: https://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html#customization\n"
                          r"    html_theme_options = {\n"
                          r"        'navbar_title': short_title,\n\n"
                          r"        # Global TOC depth for \"site\" navbar tab. (Default: 1)\n"
                          r"        # Switching to -1 shows all levels.\n"
                          r"        'globaltoc_depth': -1,\n\n"
                          r"        # HTML navbar class (Default: \"navbar\") to attach to <div> element.\n"
                          r"        # For black navbar, do \"navbar navbar-inverse\"\n"
                          r"        'navbar_class': \"navbar navbar-inverse\",\n\n"
                          r"        # Fix navigation bar to top of page?\n"
                          r"        # Values: \"true\" (default) or \"false\"\n"
                          r"        'navbar_fixed_top': \"true\",\n\n"
                          r"        # Location of link to source.\n"
                          r"        # Options are \"nav\" (default), \"footer\" or anything else to exclude.\n"
                          r"        'source_link_position': \"footer\",\n\n"
                          r"        # Any Bootswatch theme (https://bootswatch.com/) can be used\n"
                          r"        #'bootswatch_theme': 'readable',\n\n"
                          r"        # A list of tuples containing pages or urls to link to.\n"
                          r"        # Valid tuples should be in the following forms:\n"
                          r"        #    (name, page)                 # a link to a page\n"
                          r"        #    (name, \"/aa/bb\", 1)          # a link to an arbitrary relative url\n"
                          r"        #    (name, \"https://example.com\", True) # arbitrary absolute url\n"
                          r"        # Note the \"1\" or \"True\" value above as the third argument to indicate\n"
                          r"        # an arbitrary url.\n"
                          r"        #'navbar_links': [('PDF', '../mydoc.pdf', True), ('HTML', '../mydoc.html', True)],\n\n"
                          r"        # TODO: Future.\n"
                          r"        # Add page navigation to it's own navigation bar.\n"
                          r"        #'navbar_page_separate': True,\n"
                          r"    }\n"
                          r"    html_theme_path += sphinx_bootstrap_theme.get_html_theme_path()\n\n"
                          r"elif html_theme == 'scipy_lectures':\n"
                          r"    # inherits the default theme and has all those options\n"
                          r"    # set rightsidebar to true and nodesidebar to true to get\n"
                          r"    # sidebar with the matching colors\n"
                          r"    html_theme_options = {\n"
                          r"        'nosidebar': 'true',\n"
                          r"        'rightsidebar': 'false',\n"
                          r"        'sidebarbgcolor': '#f2f2f2',\n"
                          r"        'sidebartextcolor': '#20435c',\n"
                          r"        'sidebarlinkcolor': '#20435c',\n"
                          r"        'footerbgcolor': '#000000',\n"
                          r"        'relbarbgcolor': '#000000',\n"
                          r"    }\n\n"
                          r"elif html_theme == 'cbc':\n"
                          r"    pygments_style = \"friendly\"\n"
                          r"elif html_theme == 'uio':\n"
                          r"    pygments_style = \"tango\"\n"
                          r"elif html_theme in tinker_themes:\n"
                          r"    html_theme_options = {}\n"
                          r"    extensions += ['tinkerer.ext.blog', 'tinkerer.ext.disqus']\n"
                          r"    html_static_path += [tinkerer.paths.static]\n"
                          r"    html_theme_path += [tinkerer.paths.themes]\n\n\n\n")
    text = re.sub(r'^# *html_theme_options = \{\}', html_theme_options,
                  text, flags=re.MULTILINE)
    #text = re.sub('^# *html_theme_path = \[\]', html_theme_options,

    # Examples on settings: https://pylit.berlios.de/conf.py.html

    text = re.sub(r'# *html_use_index =.+', ("if html_theme == 'impressjs':\n"
                                             "    html_use_index = False\n"), text)

    if logo is not None:
        # Must copy logo file
        logo_basename = os.path.basename(logo)
        shutil.copy(os.path.abspath(logo), logo_basename)
        text = re.sub(r'# *html_logo = None', 'html_logo = "%s"'
                      % logo_basename, text)

    if favicon is not None:
        # Must copy logo file
        favicon_basename = os.path.basename(favicon)
        shutil.copy(os.path.abspath(favicon),
                    os.path.join('_static', favicon_basename))
        text = re.sub(r'# *html_favicon = None', 'html_favicon = "%s"'
                      % favicon_basename, text)

    # For tinker themes we need to copy index.rst to master.rst
    if theme in ['dark', 'flat', 'modern5', 'minimal5', 'responsive']:
        shutil.copy('index.rst', 'master.rst')
        text = text.replace("master_doc = 'index'", "master_doc = 'master'")
        text = re.sub(r'(html_title =.+)', (r'\g<1>\n'
                                            r'tagline = ""  # subtitle\n'
                                            r'html_add_permalinks = None', text))

    f = open('conf.py', 'w');  f.write(text);  f.close()

    # Write _templates/layout.html file for sagecellserver boxes
    try:
        import icsecontrib.sagecellserver
        f = open(os.path.join('_templates', 'layout.html'), 'w')
        f.write(("{% extends \"!layout.html\" %}\n"
                 "{% block linktags %}\n\n"
                 "        <script src=\"https://sagecell.sagemath.org/static/jquery.min.js\"></script>\n"
                 "        <script src=\"https://sagecell.sagemath.org/static/embedded_sagecell.js\"></script>\n\n"
                 "        <script>sagecell.makeSagecell({inputLocation: \".sage\"});</script>\n\n"
                 "        <style type=\"text/css\">\n"
                 "                .sagecell .CodeMirror-scroll {\n"
                 "                        overflow-y: hidden;\n"
                 "                        overflow-x: auto;\n"
                 "                }\n"
                 "                .sagecell .CodeMirror {\n"
                 "                        height: auto;\n"
                 "                }\n"
                 "        </style>\n\n"
                 "    {{ super() }}\n"
                 "{% endblock %}\n"))
        f.close()
    except ImportError:
        pass


def make_conf_py_runestone(themes, theme, title, short_title,
                           copyright_, logo, favicon, intersphinx):
    f = open('conf.py', 'r');  text = f.read();  f.close()
    text = re.sub(r"^project = u'<ENTER.+", "project = u'%s'" % title,
                  flags=re.MULTILINE)
    text = re.sub(r"^copyright = u'<ENTER.+", "copyright = u'%s'" % copyright_,
                  flags=re.MULTILINE)
    text = re.sub(r"'navbar_title':.+", "'navbar_title': '%s'" % title)
    f = open('conf.py', 'w');  f.write(text);  f.close()




# -----------------------------------------------------------------------