# Variables to be shared across modules

dirname = ''            # The input file's directory. DocOnce cd's into this directory
dofile_basename = ''
filename = ''
fileout = ''
format = ''
encoding = ''

_log = ''
_log_filename = ''

supported_format_names = ['html', 'latex', 'pdflatex', 'rst', 'sphinx', 'st', 'epytext',
                          'plain', 'gwiki', 'mwiki', 'cwiki', 'pandoc', 'ipynb', 'matlabnb']

# Begin-end environments
doconce_envirs = ['c', 't',                # verbatim and tex blocks
            'ans', 'sol', 'subex',        # exercises
            'ans_docend', 'sol_docend',   # exercises at document end
            'pop', 'slidecell', 'notes',  # slides
            'hint', 'remarks',            # exercises
            'quote', 'box',
            'notice', 'summary', 'warning', 'question', 'block', # admon
            'quiz', 'u-',
            ]

# Mapping from LANG envir in Typesetting Styles to programming language
# Typesetting Styles: !bc LANG[cod|pro][postfix]
# NB get_legal_pygments_lexers in common.py
envir2syntax = dict(
        bash='bash', sh='bash',
        pyshell='python', py='python', cy='cython', f='fortran',
        c='c', cpp='c++', rst='rst', swig='c++',
        cu='cuda', cuda='cuda',
        m='matlab', pl='perl',
        latex='latex', tex='latex', html='html',
        xml='xml', rb='ruby', sys='console',
        js='js', java='java',
        dat='text', txt='text', csv='text',
        ipy='ipy', do='doconce',
        r='r', php='php',
        pyopt='python', pysc='python',
        jl='julia'
    )
# Programming languages for which `--execute` is supported using Jupyter kernels
syntax_executable = ['python', 'bash', 'r', 'julia']

## Typesetting Styles: !bc LANG[cod|pro][postfix]
LANG = list(envir2syntax.keys())
# Additional envirs in the .ptex2tex.cfg file as of June 2012.
# Recall that the longest names must come first to be substituted first e.g. bccod before bcc
# Postfixes allowed on code blocks e.g. `pycod-e` and regex to catch them
postfix_code_block = ['-hid', '-h', '-e', '-t', '-out', 'hid', 'out', '-noex']
postfix_err = '-err'
# Code block regex pattern
# '[\w]*?' (any word, non greedy) takes care of additional envirs in the .ptex2tex.cfg file
pattern_code_block = r'^!bc\s' + \
          '(?:(?P<language>' + '|'.join(LANG + ['[\w]*?']) + ')?)' + \
          '(?P<type>' + '|'.join(['', 'cod', 'pro']) + ')' + \
          '(?:(?P<postfix>' + '|'.join(postfix_code_block) + ')?)' + \
          '(?:(?P<postfix_err>' + postfix_err + ')?)' + \
          '\s*$'
# Code block regex pattern to be used with %s, see e.g. pandoc, sphinx, mwiki
postfix_regex = '(?:' + '|'.join(postfix_code_block) + '|)' + '(?:' + postfix_err + ')?'
code_block_regex = r'^!bc\s+%s' + postfix_regex + '\s*\n'

main_content_char = '-'

# Python colors and styling for printing
style = {
    'green': '\033[92m',
    'red': '\033[91m',
    'bold': '\033[1m',
    'underline': '\033[4m',
    'ybackground': '\033[33m',
    'black': '\033[30m',
    'yellow': '\033[33m',
    'magenta': '\033[35',
    'white': '\033[37m',
    'blue': '\033[94m',
    '_end': '\033[0m'
}

# Regular expressions for inline tags:
inline_tag_begin =  r"(?P<begin>(^|\" |[(\s~>{!-]|^__|&[mn]dash;))"
inline_tag_end =    r"(?P<end>($|\" |[.,?!;:)<}!'\s~\[<&;-]))"

# Admonitions
admons = 'notice', 'summary', 'warning', 'question', 'block'

# Identifiers in the text used to identify code and math blocks
_CODE_BLOCK = '<<<!!CODE_BLOCK'
_MATH_BLOCK = '<<<!!MATH_BLOCK'

# Support for non-English languages (not really implemented yet)
locale_dict = dict(
    language='English',  # language to be used
    American={
        # 'English' is an alias for 'American'
        'locale': 'us_US.UTF-8',
        'latex package': 'english',
        'aspell_dictionary' : 'american', # with aspell, this is an alias for 'en_US'
        'toc': 'Table of contents',
        'Contents': 'Contents',
        'Figure': 'Figure',
        'Movie': 'Movie',
        'list of': 'List of',
        'and': 'and',
        'Exercise': 'Exercise',
        'Project': 'Project',
        'Problem': 'Problem',
        'Example': 'Example',
        'Projects': 'Projects',
        'Problems': 'Problems',
        'Examples': 'Examples',
        'Preface': 'Preface',
        'Abstract': 'Abstract',
        'Summary': 'Summary',
        # Admons
        'summary': 'summary',
        'hint': 'hint',
        'question': 'question',
        'notice': 'notice',
        'warning': 'warning',
        # box, quote are silent wrt title
        'remarks': 'remarks', # In exercises
        # Exercise headings
        'Solution': 'Solution',
        'Answer': 'Answer',
        'Hint': 'Hint',
        # At the end (in Sphinx)
        'index': 'Index',
        # References
        'Filename': 'Filename',
        'Filenames': 'Filenames',
        # Quiz
        'question_prefix': 'Question:', # question in multiple-choice quiz
        'choice_prefix': 'Choice',      # choice in multiple-choice quiz
    },
    Norwegian={
        'locale': 'nb_NO.UTF-8', # norsk bokmål
        'latex package': 'norsk',
        'aspell_dictionary' : 'norsk', # with aspell, this is an alias for 'nb'
        'toc': 'Innholdsfortegnelse',
        'Contents': 'Innhold',
        'Figure': 'Figur',
        'Movie': 'Video',
        'list of': 'Liste over',
        'and': 'og',
        'Exercise': 'Oppgave',
        'Project': 'Prosjekt',
        'Problem': 'Problem',
        'Example': 'Eksempel',
        'Exercises': 'oppgaver',
        'Projects': 'prosjekter',
        'Problems': 'problemer',
        'Examples': 'eksempler',
        'Preface': 'Forord',
        'Abstract': 'Sammendrag',
        'Summary': 'Sammendrag',
        'summary': 'sammendrag',
        'hint': 'Hint',
        'question': u'spørsmål',
        'notice': u'observér',
        'warning': 'advarsel',
        'remarks': 'bemerkning',
        'index': 'Stikkordsliste',
        'Solution': u'Løsningsforslag',  # In exercises
        'Answer': 'Fasit',  # In exercises
        'Hint': 'Hint',  # In exercises
        'Filename': 'Filnavn',
        'Filenames': 'Filnavn',
        # Quiz
        'question_prefix': u'Spørsmål:',    # question in multiple-choice quiz
        'choice_prefix': 'Alternativ',      # choice in multiple-choice quiz
    },
    German={
        'locale': 'de_DE.UTF-8',
        'latex package': 'german',
        'aspell_dictionary' : 'deutsch', # with aspell, this is an alias for 'de_DE'
        'toc': 'Inhaltsverzeichnis',
        'Contents': 'Inhalt',
        'Figure': 'Abbildung',
        'Movie': 'Film',
        'list of': 'Liste von',
        'and': 'und',
        'Exercise': u'Übung',
        'Project': 'Projekt',
        'Problem': 'Problem',
        'Example': 'Beispiel',
        'Projects': 'Projekte',
        'Problems': 'Probleme',
        'Examples': 'Beispiele',
        'Preface': 'Vorwort',
        'Abstract': 'Abstract',
        'Summary': 'Zusammenfassung',
        # Admons
        'summary': 'Zusammenfassung',
        'hint': 'Hinweis',
        'question': 'Frage',
        'notice': 'Notiz',
        'warning': 'Warnung',
        # box, quote are silent wrt title
        'remarks': 'Bemerkung', # In exercises
        # Exercise headings
        'Solution': u'Lösung',
        'Answer': 'Antwort',
        'Hint': 'Hinweis',
        # At the end (in Sphinx)
        'index': 'Index',
        # References
        'Filename': 'Dateiname',
        'Filenames': 'Dateiname',
    },
    Basque={
	    'locale': 'eu_ES.UTF-8',
	    'latex package': 'basque',
	    'toc': 'Aurkibidea',
	    'Contents': 'Edukiak',
	    'Figure': 'Irudia',
	    'Movie': 'Filma',
	    'list of': 'Zerrenda',
	    'and': 'eta',
	    'Exercise': 'Ariketa',
	    'Project': 'Proiektua',
	    'Problem': 'Problema',
	    'Example': 'Adibidea',
	    'Projects': 'Proiektuak',
	    'Problems': 'Problemak',
	    'Examples': 'Adibideak',
	    'Preface': 'Hitzaurrea',
	    'Abstract': 'Laburpena',
	    'Summary': 'Laburpena',
	    # Admons
	    'summary': 'laburpena',
	    'hint': 'laguntza',
	    'question': 'galdera',
	    'notice': 'oharra',
	    'warning': 'kontuz',
	    # box, quote are silent wrt title
	    'remarks': 'iruzkinak', # In exercises
	    # Exercise headings
	    'Solution': 'Soluzioa',
	    'Answer': 'Erantzuna',
	    'Hint': 'Laguntza',
	    # At the end (in Sphinx)
	    'index': 'Indizea',
	    # References
	    'Filename': 'Fitxategi',
	    'Filenames': 'Fitxategiak',
    },
    Arabic={
        'locale': 'ar_SA.UTF-8',
        'latex package': 'arabic',
        'aspell_dictionary' : 'arabic', # with aspell, this is an alias for 'ar'
        'toc': u'الفَهْرس',
        'Contents': u'المُحْتويات',
        'Figure': u'رَسْم تَوضِيحي',
        'Movie': u'فِيلم',
        'list of': u'قَائِمة',
        'and': u'و',
        'Exercise': u'تَمْرِين',
        'Project': u'مَشْرُوع',
        'Problem': u'مَسْألة',
        'Example': u'مِثَال',
        'Projects': u'مَشَارِيع',
        'Problems': u'مَسَائِل',
        'Examples': u'أَمْثِلة',
        'Preface': u'مُقَدِّمة',
        'Abstract': u'المُلَّخص',
        'Summary': u'الخُلاصَة',
        # Admons
        'summary': u'الخُلاصة',
        'hint': u'تَلْمِيح',
        'question': u'سُؤال',
        'notice': u'تَنْبِيه',
        'warning': u'تَحْذِير',
        # box, quote are silent wrt title
        'remarks': u'مُلاحَظات', # In exercises
        # Exercise headings
        'Solution': u'الحَل',
        'Answer': u'الجَواب',
        'Hint': u'تَلْميح',
        # At the end (in Sphinx)
        'index': u'الدَّليل',
        # References
        'Filename': u'اسم_الملف',
        'Filenames': u'أسماء_الملفات',
    },
    French={
        'locale': 'fr_FR.UTF-8', # français
        'latex package': 'french',
        'toc': u'Table des matières',
        'Contents': 'Sommaire',
        'Figure': 'Figure',
        'Movie': u'Vidéo',
        'list of': 'Liste des',
        'and': 'et',
        'Exercise': 'Exercice',
        'Project': 'Projet',
        'Problem': u'Problème',
        'Example': 'Exemple',
        'Exercises': 'Exercices',
        'Projects': 'Projets',
        'Problems': u'Problèmes',
        'Examples': 'Exemples',
        'Preface': u'Préface',
        'Abstract': u'Résumé',
        'Summary': u'Résumé',
        'summary': u'résumé',
        'hint': 'Indication',
        'question': u'question',
        'notice': 'note',
        'warning': 'avertissement',
        'remarks': 'remarque',
        'index': 'Index',
        'Solution': 'Solution',  # In exercises
        'Answer': u'Réponse',
        'Hint': 'Indication',
        'Filename': 'Nom de fichier',
        'Filenames': 'Noms de fichier',
        'question_prefix': 'Question:', # question in multiple-choice quiz
        'choice_prefix': 'Alternative', # choice in multiple-choice quiz
        },
    Dutch={
        # Nederlands
        'locale': 'nl_NL.UTF-8',
        'latex package': 'dutch',
        'aspell_dictionary' : 'dutch', # with aspell, this is an alias for 'en_US'
        'toc': 'Inhoudsopgave',
        'Contents': 'Inhoud',
        'Figure': 'Figuur',
        'Movie': 'Film',
        'list of': 'Lijst met',
        'and': 'en',
        'Exercise': 'Oefening',
        'Project': 'Project',
        'Problem': 'Probleem',
        'Example': 'Voorbeeld',
        'Projects': 'Projecten',
        'Problems': 'Problemen',
        'Examples': 'Voorbeelden',
        'Preface': 'Voorwoord',
        'Abstract': 'Abstract',
        'Summary': 'Samenvatting',
        # Admons
        'summary': 'samenvatting',
        'hint': 'hint',
        'question': 'Vraag',
        'notice': 'opmerking',
        'warning': 'waarschuving',
        # box, quote are silent wrt title
        'remarks': 'opmerkingen', # In exercises
        # Exercise headings
        'Solution': 'Oplossing',
        'Answer': 'antwoord',
        'Hint': 'Hint',
        # At the end (in Sphinx)
        'index': 'Inhoudsopgave',
        # References
        'Filename': 'Bestandsnaam',
        'Filenames': 'Bestandsnamen',
        # Quiz
        'question_prefix': 'Vraag:',    # question in multiple-choice quiz
        'choice_prefix': 'Alternatief', # choice in multiple-choice quiz
    },
    Italian={
        'locale': 'it_IT.UTF-8',
        'latex package': 'italian',
        'aspell_dictionary' : 'italian',
        'toc': 'Indice',
        'Contents': 'Contenuto',
        'Figure': 'Figura',
        'Movie': 'Video',
        'list of': 'Lista con',
        'and': 'e',
        'Exercise': 'Esercizio',
        'Project': 'Progetto',
        'Problem': 'Problema',
        'Example': 'Esempio',
        'Projects': 'Progetto',
        'Problems': 'Problemi',
        'Examples': 'Esempi',
        'Preface': 'Prefazione',
        'Abstract': 'Abstract',
        'Summary': 'Riassunto',
        # Admons
        'summary': 'sommario',
        'hint': 'suggerimento',
        'question': 'domanda',
        'notice': 'NB',
        'warning': 'avvertimento',
        # box, quote are silent wrt title
        'remarks': 'osservazioni', # In exercises
        # Exercise headings
        'Solution': 'Soluzione',
        'Answer': 'Risposta',
        'Hint': 'Suggerimento',
        # At the end (in Sphinx)
        'index': 'Indice',
        # References
        'Filename': 'Nome del file',
        'Filenames': 'Nomi dei file',
        # Quiz
        'question_prefix': 'Domanda:',  # question in multiple-choice quiz
        'choice_prefix': 'Alternativa', # choice in multiple-choice quiz
        },
    Spanish={
        # Spanish, Spain
        'locale': 'es_ES.UTF-8',
        'latex package': 'spanish',
        'aspell_dictionary' : 'spanish',
        'toc': 'Tabla de contenido',
        'Contents': 'Contenido',
        'Figure': 'Figura',
        'Movie': 'Video',
        'list of': 'Lista de',
        'and': 'y',
        'Exercise': 'Ejercicio',
        'Project': 'Proyecto',
        'Problem': 'Problema',
        'Example': 'Ejemplo',
        'Projects': 'Proyecto',
        'Problems': 'Problemas',
        'Examples': 'Ejemplos',
        'Preface': 'Prefacio',
        'Abstract': 'Abstracta',
        'Summary': 'Resumen',
        # Admons
        'summary': 'resumen',
        'hint': 'indicio',
        'question': 'pregunta',
        'notice': 'nota',
        'warning': 'advertencia',
        # box, quote are silent wrt title
        'remarks': 'comentarios', # In exercises
        # Exercise headings
        'Solution': 'Soluciones',
        'Answer': 'Respuesta',
        'Hint': 'Indicios',
        # At the end (in Sphinx)
        'index': 'Índice',
        # References
        'Filename': 'Nombre del archivo',
        'Filenames': 'Nombres de los archivos',
        # Quiz
        'question_prefix': 'Pregunta:', # question in multiple-choice quiz
        'choice_prefix': 'Alternativa', # choice in multiple-choice quiz
        },
     Polish={
        'locale': 'pl_PL.UTF-8',
        'latex package': 'polish',
        'aspell_dictionary' : 'polish', 
        'toc': 'Spis treści',
        'Contents': 'Spis treści',
        'Figure': 'Rysunek',
        'Movie': 'Film',
        'list of': 'Lista',
        'and': 'i',
        'Exercise': 'Ćwiczenie',
        'Project': 'Projekt',
        'Problem': 'Problem',
        'Example': 'Przykład',
        'Projects': 'Projekty',
        'Problems': 'Problemy',
        'Examples': 'Przykłady',
        'Preface': 'Wstęp',
        'Abstract': 'Streszczenie',
        'Summary': 'Podsumowanie',
        # Admons
        'summary': 'podsumowanie',
        'hint': 'podpowiedź',
        'question': 'pytanie',
        'notice': 'uwaga',
        'warning': 'uwaga!',
        # box, quote are silent wrt title
        'remarks': 'uwagi', # In exercises
        # Exercise headings
        'Solution': 'Rozwiązanie',
        'Answer': 'Odpowiedź',
        'Hint': 'Podpowiedź',
        # At the end (in Sphinx)
        'index': 'Indeks',
        # References
        'Filename': 'Plik',
        'Filenames': 'Pliki',
        # Quiz
        'question_prefix': 'Pytanie:', # question in multiple-choice quiz
        'choice_prefix': 'Pytanie',      # choice in multiple-choice quiz
        }
    )
# Let English be an alias for American
locale_dict['English'] = locale_dict['American'].copy()
# Create British based on (American) English
locale_dict['British'] = locale_dict['American'].copy()
locale_dict['British']['locale'] = 'en_GB.UTF-8'
locale_dict['British']['aspell_dictionary'] = 'british' # with aspell, this is an alias for 'en_GB'
locale_dict['British']['latex package'] = 'british' # with aspell, this is an alias for 'en_GB'

def lookup_locale_dict(key, fallback_to_english=True):
    if key in locale_dict[locale_dict['language']]:
        return locale_dict[locale_dict['language']][key]

    # could not find localized term
    if fallback_to_english:
        assert key in locale_dict['English'], "'%s' is not in locale_dict" % key
        return locale_dict['English'][key]
    else:
        raise ValueError("'%s' is not in locale_dict for %s" % (key, locale_dict['language']))

doconce_commands = "help, format, find, subst, replace, remove, spellcheck, apply_inline_edits, capitalize, " \
                   "change_encoding, clean, combine_images, csv2table, diff, expand_commands, expand_mako, extract_exercises, " \
           "find_nonascii_chars, fix_bibtex4publish, gitdiff, grab, grep, guess_encoding, gwiki_figsubst, html2doconce, " \
       "html_colorbullets, jupyterbook, include_map, insertdocstr, ipynb2doconce, latex2doconce, latex_dislikes, " \
       "latex_exercise_toc, latex_footer, latex_header, latex_problems, latin2html, lightclean, linkchecker, " \
       "list_fig_src_files, list_labels, makefile, md2html, md2latex, old2new_format, ptex2tex, pygmentize, " \
       "ref_external, remove_exercise_answers, remove_inline_comments, replace_from_file, slides_beamer, " \
       "slides_html, slides_markdown, sphinx_dir, sphinxfix_localURLs, split_html, split_rst, teamod".split(", ")

_registered_commands = [
    ('format', 'Transform doconce file to another format'),
    ('jupyterbook', 'Create directories and files for Jupyter Book'),
    ('ptex2tex', 'Transform ptex2tex files (.p.tex) to ordinary latex file and manage the code environments'),
    ('slides_html', 'Create HTML slides from a (doconce) html file'),
    ('slides_beamer', 'Create LaTeX Beamer slides from a (doconce) latex/pdflatex file'),
    ('slides_markdown', 'Create Remark slides from Markdown'),
    ('split_html', 'Split an html file into parts according to !split commands'),
    ('clean', 'Remove all files that the doconce can regenerate'),
    ('spellcheck', 'Run spellcheck on a set of files'),
    ('grab', 'Grab selected text from a file'),
    ('grep', 'List all figure, movie or included code files'),
    ('find', 'Search for a (regular) expression in all .do.txt files in the current directory tree '
             '(useful when removing compilation errors)'),
    ('subst', 'Substitute a phrase by another using regular expressions'),
    ('diff', 'Find differences between two files'),
    ('gitdiff', 'Find differences between the last two Git versions of several files'),
    ('replace', 'Replace a phrase by another literally (exact text substitution)'),
    ('remove', 'Remove selected text from a file'),
    ('replace_from_file', 'Replace using from and to phrases from file'),
    ('extract_exercises', 'Extract all exercises (projects and problems too)'),
    ('remove_exercise_answers', 'Remove answers from exercises'),
    ('apply_inline_edits', 'Apply all edits specified through inline comments'),
    ('remove_inline_comments', 'Remove all inline comments in a doconce file'),
    ('capitalize', 'Change headings from "This is a Heading" to "This is a heading"'),
    ('guess_encoding', 'Guess the encoding in a text'),
    ('change_encoding', 'Change encoding'),
    ('combine_images', 'Combine several images into one'),
    ('expand_commands', 'Expand short cut commands to full form in files'),
    ('expand_mako', 'Replace all mako function calls by the `results of the calls'),
    ('find_nonascii_chars', 'Find non-ascii characters in a file'),
    ('fix_bibtex4publish', 'Fix common problems in bibtex files for publish import'),
    ('csv2table', 'Convert csv file to doconce table format'),
    ('html2doconce', 'Apply transformations to an html file to help translate the document into DocOnce format'),
    ('ipynb2doconce', 'Translate an IPython/Jupyter notebook to doconce'),
    ('md2html', 'Make HTML file via pandoc from Markdown (.md) file'),
    ('md2latex', 'Make LaTeX file via pandoc from Markdown (.md) file'),
    ('latex2doconce', 'Translate a latex document to doconce (requires usually manual fixing)'),
    ('latex_dislikes', 'Check if there are problems with translating latex to doconce'),
    ('include_map', 'Print an overview of how various files are included in the root doc'),
    ('sphinx_dir', 'Create a directory for the sphinx format (requires sphinx version >= 1.1)'),
    ('split_rst', 'Split a sphinx/rst file into parts according to !split commands'),
    ('insertdocstr', 'Walk through a directory tree and insert doconce files as docstrings in *.p.py files'),
    ('lightclean', 'Remove all redundant files (keep source .do.txt and results: .pdf, .html, sphinx- dirs, '
                   '.mwiki, .ipynb, etc.)'),
    ('gwiki_figsubst', 'Replace figures path with URL'),
    ('html_colorbullets', 'Replace bullets in lists by colored bullets'),
    ('latex_problems', 'Report problems from a LaTeX .log file'),
    ('list_fig_src_files', 'List all figure files, movie files, and source code files needed'),
    ('list_labels', 'List all labels in a document (for purposes of cleaning them up)'),
    ('ref_external', 'Generate script for substituting generalized references'),
    ('linkchecker', 'Check all links in HTML files'),
    ('pygmentize', 'Typeset a doconce document with pygments (for pretty print of doconce itself)'),
    ('makefile', 'Generate a make.py script for translating a doconce file to various formats'),
    ('sphinxfix_localURLs', 'Edit URLs to local files and place them in _static'),
    ('latin2html', 'Replace latex-1 (non-ascii) characters by html codes'),
    ('latex_header', 'Print the header (preamble) for latex file'),
    ('latex_footer', 'Print the footer for latex files'),
    ('latex_exercise_toc', 'Insert a table of exercises in a latex file myfile.p.tex'),
    ('teamod', 'Create a boilerplate directory for a teaching module.')]

doconce_commands = list(map(lambda t: t[0], _registered_commands))

old = "help, format, find, subst, replace, remove, spellcheck, apply_inline_edits, capitalize, change_encoding, " \
           "clean, combine_images, csv2table, diff, expand_commands, expand_mako, extract_exercises, " \
           "find_nonascii_chars, fix_bibtex4publish, gitdiff, grab, grep, guess_encoding, gwiki_figsubst, html2doconce, " \
      "html_colorbullets, jupyterbook, include_map, insertdocstr, ipynb2doconce, latex2doconce, latex_dislikes, " \
      "latex_exercise_toc, latex_footer, latex_header, latex_problems, latin2html, lightclean, linkchecker, " \
      "list_fig_src_files, list_labels, makefile, md2html, md2latex, old2new_format, ptex2tex, pygmentize, " \
      "ref_external, remove_exercise_answers, remove_inline_comments, replace_from_file, slides_beamer, " \
      "slides_html, slides_markdown, sphinx_dir, sphinxfix_localURLs, split_html, split_rst, teamod".split(", ")

_registered_command_line_options = [
    ('--help', 'Print all command-line options for doconce'),
    ('--output=', 'Output filename or file basename for `doconce format` commands. May include an absolute or relative path to another folder. Any relative path for the output file should start from the folder that contains the `do.txt` file being converted.'),
    ('--debug', 'Write a debugging file _doconce_debugging.log with lots of intermediate results'),
    ('--no_abort', 'Do not abort the execution if syntax errors are found.'),
    ('--verbose=', 'Write progress of intermediate steps if they take longer than X seconds. 0: X=15 (default); '
                    '1: X=5; 2: X=0'),
    ('--language=', 'Native language to be used: English (default), Norwegian, German, French, Basque, Arabic, Italian, Polish'),
    ('--preprocess_include_subst', 'Turns on variable substitutions in # #include paths when running Preprocess: '
                    'preprocess -i -DMYDIR=rn1 will lead to the string "MYDIR" being replaced '
                    'by the value "rn1" in # #include "..." statements.'),
    ('--syntax_check=', 'Values: on/off. Turns on/off fix of illegal constructions and the syntax check '
                    '(may be time consuming for large books).'),
    ('--skip_inline_comments', 'Remove all inline comments of the form [ID: comment].'),
    ('--draft', 'Indicates draft (turns on draft elements in LaTeX, otherwise no effect).'),
    ('--CC_license=', 'Template wording for Creative Commons licenses. Default: "Released under CC %s 4.0 license." '
                    'Example: "This work is released under the Creative Commons %s 4.0 license". '
                    'CC license is specified as a part of the copyright syntax, e.g.: '
                    '"AUTHOR: Kaare Dump {copyright|CC BY} at BSU & Some Company Ltd"; or:  '
                    '"AUTHOR: Kaare Dump at BSU & Some Company Ltd. {copyright,2005-present|CC BY-NC}". '
                    'The --CC_license= option has no effect if the license does not start with CC, e.g.: '
                    '"AUTHOR: Kaare Dump at BSU {copyright|Released under the MIT license.}"'),
    ('--align2equations', 'Rewrite align/alignat math environments to separate equation environments. Sometimes '
                    'needed for proper MathJax rendering (e.g., remark slides). Sphinx requires such rewrite '
                    'and will do it regardless of this option.'),
    ('--force_tikz_conversion', 'Force generation SVG/HTML versions of tikz figures, overwriting any previously '
                    'generated SVG/HTML files (applies to all formats except LaTeX)'),
    ('--tikz_libs=', 'TikZ libraries used in figures.'),
    ('--pgfplots_libs=', 'pgfplots libraries used in figures.'),
    ('--IBPLOT', 'automagic translation of IBPLOT commands.'),
    ('--exercise_numbering=', 'absolute: exercises numbered as 1, 2, ... (default); chapter: exercises numbered '
                    'as 1.1, 1.2, ... , 3.1, 3.2, ..., B.1, B.2, etc. with a chapter or appendix prefix.'),
    ('--exercises_in_zip', 'Place the answers+solutions and each exercise as an individual DocOnce file '
                           'in a zip archive.'),
    ('--exercises_in_zip_filename=', 'Filenames of individual exercises in zip archive. logical: use the (first) '
                    'logical filename specified by file=... ; number:  use either absolute exercise number or '
                    'chapter.localnumber.'),
    ('--toc_depth=', 'No of levels in the table of contents. Default: 2, which means chapters, sections, and '
                    'subsections. Set to 1 to exclude subsections. Applies to all formats, except sphinx: '
                    'for sphinx, set toc_depth=... as part of the command doconce sphinx_dir.'),
    ('--encoding=', 'Specify encoding (e.g., latin1 or utf-8).'),
    ('--no_ampersand_quote', 'Turn off special treatment of ampersand (&). Needed, e.g., when native latex code '
                    'for tables are inserted in the document.'),
    ('--no_mako', 'Do not run the Mako preprocessor program.'),
    ('--no_preprocess', 'Do not run the Preprocess preprocessor program.'),
    ('--mako_strict_undefined', 'Make Mako report on undefined variables.'),
    ('--no_header_footer', 'Do not include header and footer in (LaTeX and HTML) documents.'),
    ('--no_emoji', 'Remove all emojis.'),
    ('--siunits', 'Allow siunitx MathJax/LaTeX package for support of SI units in various formats'),
    ('--allow_refs_to_external_docs', 'Do not abort translation if ref{...} to labels not defined in this document.'),
    ('--userdef_environment_file=', 'Read user-defined environments from this file instead of the default '
                    '(userdef_environments.py)'),
    ('--runestone', 'Make a RunestoneInteractive version of a Sphinx document.'),
    ('--max_bc_linelength=', 'Strip lines in !bc environments that are longer than specified '
                    '(to prevent too long lines). Default: None (no length restriction).'),
    ('--replace_ref_by_latex_auxno=', 'Replace all ref{...} by hardcoded numbers from a latex .aux file. '
                    'Makes it possible for a notebook or html page to refer to a latex textbook. Recommended syntax: '
                    'see (ref{my:eq1}) in cite{MyBook}, or see Section ref{my:sec2} in cite{MyBook}.'),
    ('--keep_pygments_html_bg', 'Do not allow change of background in code blocks in HTML.'),
    ('--minted_latex_style=', 'Specify the minted style to be used for typesetting code in LaTeX. See pygmetize -L '
                    'styles for legal names.'),
    ('--pygments_html_style=', 'Specify the minted/pygments style to be used for typesetting code in HTML. '
                    'Default: default (other values: monokai, manni, rrt, perldoc, borland, colorful, murphy, '
                    'trac, tango, fruity, autumn, emacs, vim, pastie, friendly, native, see pygmentize -L styles). '
                    'none, no, off: turn off pygments to typeset computer code in HTML, use plain <pre> tags. '
                    'highlight.js: use highlight.js syntax highlighting, not pygments.'),
    ('--pygments_html_linenos', 'Turn on line numbers in pygmentized computer code in HTML. (In LaTeX line numbers '
                    'can be added via doconce subst or doconce replace such that the verbatim environments '
                    'get the linenos=true parameter.)'),
    ('--xhtml', 'Use BeautifulSoap to try to produce XHTML output. It inserts end tags (e.g. </p>) and guesses where '
                    'to do it.'),
    ('--html_output=', 'Obsolete: use --output.'),
    ('--html_style=', 'Name of theme for HTML style: plain, blueish, blueish2, bloodish, tactile-black, tactile-red, '
                    'rossant solarized, solarized2_light, solarized2_dark, bootstrap, bootswatch, bootstrap_X '
                    '(with  X=bloodish, blue, bluegray, brown, cbc, FlatUI, red), bootswatch_X (with X=cerulean, '
                    'cosmo, flatly, journal, lumen, readable, simplex, spacelab, united, yeti (dark:) amelia, '
                    'cyborg, darkly, slate, spruce, superhero (demos at bootswatch.com))'),
    ('--html_template=', 'Specify an HTML template with header/footer in which the doconce document is embedded. '
                    '(Often preferred to run with --no_title)'),
    ('--no_title', 'Comment out TITLE, AUTHOR, DATE. Often used with HTML templates.'),
    ('--html_code_style=', 'off, inherit, or transparent: enable normal inline verbatim font where foreground '
                    'and background color is inherited from the surroundnings. off, inherit and transparent'
                    ' are just synonyms for inheriting color from the text and make the background color transparent'
                    ' (use e.g. --html_code_style=inherit to avoid the red Boostrap color). Default: on '
                    '(use the css-specified typesetting of <pre> tags). NOTE: the naming "html_code_style" is '
                    'not optimal: it has nothing to do with code block style, but the <code> tag for inline '
                    'verbatim text in the context of bootstrap css styles.'),
    ('--html_pre_style=', 'off, inherit, or transparent: let code blocks inside <pre> tags have foreground '
                    'and background color inherited from the surroundnings. Default: on (use the css-specified '
                    'typesetting of <pre> tags). This option is most relevant for Bootstrap styles to avoid '
                    'white background in code blocks inside colorful admons.'),
    ('--html_toc_indent=', 'No of spaces for indentation of subsections in the table of contents in HTML output. '
                    'Default: 3 (0 gives toc as nested list in Bootstrap-based styles).'),
    ('--html_body_style=', 'Override elements in the <body> style css. Used to enlargen bootswatch fonts, '
                    'for instance: "--html_body_style=font-size:20px;line-height:1.5"'),
    ('--html_body_font=', 'Specify HTML font for text body. =? lists available fonts.'),
    ('--html_heading_font=', 'Specify HTML font for headings. =? lists available fonts.'),
    ('--html_video_autoplay=', 'True for autoplay when HTML is loaded, otherwise False (default).'),
    ('--html_admon=', 'Type of admonition and color: colors, gray, yellow, apricot, lyx, paragraph. For '
                    'html_style=bootstrap*,bootswatch*, the two legal values are boostrap_panel, bootstrap_alert.'),
    ('--html_admon_shadow', 'Add a shadow effect to HTML admon boxes (gray, yellow, apricot).'),
    ('--html_admon_bg_color=', 'Background color of admon in HTML.'),
    ('--html_admon_bd_color=', 'Boundary color of admon in HTML.'),
    ('--css=', 'Specify a .css style file for HTML output. If the file does not exist, the default or specified '
                    'style (--html_style=) is written to it.'),
    ('--html_box_shadow', 'Add a shadow effect in HTML box environments.'),
    ('--html_share=', 'Specify URL and there will be Facebook, Twitter, etc. buttons at the end of the HTML document. '
                    '--html_share=https://mysite.com/specials shares on email, Facebook, Google+, LinkedIn, Twitter, '
                    'and enables a print button too. --html_share=https://mysite.com/specials,twitter,facebook '
                    'shares on Twitter and Facebook only. Sites are separated by comma. The following names '
                    'are allowed: email, facebook, google+, linkedin, twitter, print.'),
    ('--html_exercise_icon=', 'Specify a question icon (as a filename in the bundled/html_images directory in the '
                    'doconce repo) for being inserted to the right in exercises. default: turn on predefined '
                    'question icons according to the chosen style. none: no icons (this is the default value).'),
    ('--html_exercise_icon_width=', 'Width of the icon image in pixels (must be used with --html_exercise_icon).'),
    ('--html_DOCTYPE', 'Insert <!DOCTYPE HTML> in the top of the HTML file. This is required for Internet Explorer'
                    ' and Mozilla. However, some of the CSS files used by DocOnce may not load properly if they are '
                    'not well formed. That is why no doctype is default in the generated HTML files.'),
    ('--html_links_in_new_window', 'Open HTML links in a new window/tab.'),
    ('--html_quiz_button_text=', 'Text on buttons for collapsing/expanding answers and explanations in quizzes '
                    '(with bootstrap styles). Default: Empty (just pencil glyphion).'),
    ('--html_bootstrap_navbar=', 'Turns the Bootstrap navigation bar on/off. Default: on.'),
    ('--html_bootstrap_jumbotron=', 'Turns the Bootstrap jumbotron intro on/off and governs the size of the document '
                    'title. Default: on. Other values: h2, off (h2 gives h2 heading instead of h1, '
                    'off gives no jumbotron).'),
    ('--html_bootstrap_navbar_links=', 'Allows custom links in the navigation bar. Format: link|url;link|url;link|url.'
                    ' Example: "--html_bootstrap_navbar_links=Google|https://google.com;hpl|https://folk.uio.no/hpl"'),
    ('--html_figure_caption=', 'Placement of figure caption: top (default) or bottom. See also the `sidecap` keyword '
                               'for individual figures.'),
    ('--html_figure_hrule=', 'Set horizontal rule(s) above and/or below a figure. top: rule at top (default); '
                    'none, off: no rules; bottom: rule at bottom; top+bottom: rule at top and bottom'),
    ('--html_copyright=', 'Controls where to put copyright statements. everypage: in the footer of every page; '
                    'titlepages or titlepage: in the footer of the titlepage only (default).'),
    ('--cite_doconce', 'Adds a citation to the DocOnce web page if copyright statements are present.'),
    ('--device=', 'Set device to paper, screen, or other (paper impacts LaTeX output).'),
    ('--number_all_equations', 'Switch latex environments such that all equations get a number.'),
    ('--denumber_all_equations', 'Switch latex environments such no equations get a number (useful for removing '
                    'equation labels in slides). Error messages are issued about references to numbered equations '
                    'in the text.'),
    ('--latex_style=', 'LaTeX style package used for the document.\n'
                    '  std: standard LaTeX article or book style,\n'
                    '  Springer_sv: Springer\'s svmono class (the new standard for all Springer books),\n'
                    '  Springer_T2: Springer\'s T2 book style,\n'
                    '  Springer_T4: Springer\'s T4 book style (smaller pagesize than T2),\n'
                    '  Springer_lncse: Springer\'s Lecture Notes in Computational Science and Engineering (LNCSE) style,\n'
                    '  Springer_llncs: Springer\'s Lecture Notes in Computer Science style,\n'
                    '  Springer_lnup:  Springer\'s Lecture Notes in University Physics,\n'
                    '  Springer_collection: Springer\'s style for chapters in LNCSE proceedings,\n'
                    '  tufte-book: use of tufte-book.cls for E. Tufte-inspired layout,\n'
                    '  Koma_Script: Koma Script style,\n'
                    '  siamltex: SIAM\'s standard LaTeX style for papers,\n'
                    '  siamltexmm: SIAM\'s extended (blue) multimedia style for papers.\n'
                    '  elsevier: Elsevier Style'),
    ('--latex_font=', 'LaTeX font choice: helvetica, palatino, utopia, std (Computer Modern, default).'),
    ('--latex_code_style=', '\n  Typesetting of code blocks.\n'
                    '    pyg: use pygments (minted), style is set with --minted_latex_style=\n'
                    '    lst: use lstlistings\n'
                    '    vrb: use Verbatim (default)\n'
                    '  Specifications across languages:\n'
                    '    pyg-blue1\n'
                    '    lst, lst-yellowgray[style=redblue]\n'
                    '    vrb[frame=lines,framesep=2.5mm,framerule=0.7pt]\n'
                    '  Detailed specification for each language:\n'
                    '    default:vrb-red1[frame=lines]@pycod:lst[style=redblue]@pypro:lst-blue1[style=default]@sys:'
                    'vrb[frame=lines,label=\\fbox{{\\tiny Terminal}},framesep=2.5mm,framerule=0.7pt]\n'
                    '  Here, Verbatim[frame=lines] is used for all code environments, except pycod, pypro and sys, '
                    'which have their own specifications.\n'
                    '    pycod: lst package with redblue style (and white background)\n'
                    '    pypro: lst package with default style and blue1 background\n'
                    '    style, sys: Verbatim with the specified arguments and white background.\n'
                    '  (Note: @ is delimiter for the language specifications, syntax is envir:package-background[style '
                    'parameters]@)'),
    ('--latex_code_leftmargin=', 'Sets the left margin in code blocks. Default: 7 (mm).'),
    ('--latex_code_bg=', 'Background color code blocks. Default: white.'),
    ('--latex_code_bg_vpad', 'Vertical padding of background. Has only effect for vrb/pyg-bgcolor styles (not lst!).'),
    ('--latex_code_lststyles=', 'Filename with LaTeX definitions of lst styles.'),
    ('--latex_copyright=', 'Controls where to put copyright statements. everypage: in the footer of every page; '
                    'titlepages: in the footer of the titlepage and chapter pages (for books) only (default).'),
    ('--latex_bibstyle=', 'LaTeX bibliography style. Default: plain.'),
    ('--section_numbering=', 'Turn section numbering on/off. Default: off for all formats except latex and '
                    'pdflatex (on for those).'),
    ('--latex_table_format=', 'Default: quote. Other values: left, center, footnotesize, tiny.'),
    ('--latex_table_row_sep=', r'Row separation factor in tables (command \renewcommand{\arraystretch}{<factor>}. '
                    'Default: 1.0'),
    ('--latex_title_layout=', 'Layout of the title, authors, and date: std: traditional LaTeX layout; titlepage: '
                    'separate page; doconce_heading (default): authors with "footnotes" for institutions; beamer: '
                    'layout for beamer slides.'),
    ('--latex_link_color=', 'Color used in hyperlinks. Default is dark blue if --device=screen, or black if '
                    '--device=paper (invisible in printout or special blue color if --latex_section_headings=blue '
                    'or strongblue). Values are specified either as comma-separated rgb tuples or as color names, '
                    'e.g., --latex_link_color=0.1,0.9,0.85 or --latex_link_color=red or --latex_link_color=gray!70'),
    ('--latex_title_reference=', 'latex code placed in a footnote for the title, typically used for '
                    'acknowledging publisher/source of original version of the document.'),
    ('--latex_encoding=', 'Encoding for \\usepackage[encoding]{inputenc}. Values: utf8 (default) or latin1.'),
    ('--latex_packages=', 'Comma-separated list of latex packages to be included in \\usepackage commands..'),
    ('--latex_papersize=', 'Geometry of page size: a6, a4, std (default).'),
    ('--latex_list_of_exercises=', 'LaTeX typesetting of list of exercises: loe: special, separate list of exercises; '
                    'toc: exercises included as part of the table of contents; none (default): no list of exercises.'),
    ('--latex_movie=', 'Specify package for handling movie/video content. Default: href (hyperlink to movie file). '
                    'Other options: media9, movie15, multimedia (Beamer\'s \\movie command).'),
    ('--latex_movie_controls=', 'Specify control panel for movies. Default: on. Other options: off.'),
    ('--latex_external_movie_viewer', 'Allow external movie viewer for movie15 package.'),
    ('--latex_fancy_header', 'Typesetting of headers on each page: If article: section name to the left and '
                    'page number to the right on even page numbers, the other way around on odd page numners. '
                    'If book: section name to the left and page numner to the right on even page numbers, '
                    'chapter name to the right and page number to the left on odd page numbers.'),
    ('--latex_section_headings=', 'Typesetting of title/section/subsection headings: std (default): standard LaTeX; '
                    'blue: gray blue color; strongblue: stronger blue color; gray: white text on gray background, '
                    'fit to heading width; gray-wide: white text on gray background, wide as the textwidth.'),
    ('--latex_colored_table_rows=', 'Colors on every two line in tables: no (default), gray, blue.'),
    ('--latex_line_numbers', 'Include line numbers for the running text (only active if there are inline comments.'),
    ('--latex_todonotes', 'Use the todonotes package to typeset inline comments. Gives colored bubbles in the '
                    'margin for small inline comments and in the text for larger comments.'),
    ('--latex_double_spacing', 'Sets the LaTeX linespacing to 1.5 (only active if there are inline comments).'),
    ('--latex_labels_in_margin', 'Print equation, section and other LaTeX labels in the margin.'),
    ('--latex_index_in_margin', 'Place entries in the index also in the margin.'),
    ('--latex_preamble=', 'User-provided LaTeX preamble file, either complete or additions to the doconce-generated '
                    'preamble.'),
    ('--latex_no_program_footnotelink', 'If --device=paper, this option removes footnotes with links to computer programs.'),
    ('--latex_admon=', 'Type of admonition in LaTeX: \n'
                    '  colors1: (inspired by the NumPy User Guide) applies different colors for the different admons '
                    'with an embedded icon; \n'
                    '  colors2: like `colors1` but the text is wrapped around the icon; \n'
                    '  mdfbox: rounded boxes with a optional title and no icon (default); \n'
                    '  graybox2: box with square corners, gray background, and narrower than mdfbox, if code it '
                    'reduces to something like mdfbox (mdframed based); the summary admon is in case of A4 format '
                    'only half of the text width with text wrapped around (effective for proposals and articles); \n'
                    '  grayicon: box with gray icons and a default light gray background; \n'
                    '  yellowicon: box yellow icons and a default light yellow background; \n'
                    '  paragraph:  plain paragraph with boldface heading. \n'
                    '  Note: the colors in mdfbox and other boxes can customized.'),
    ('--latex_admon_color=', "The color to be used as background in admonitions. A single value applies to all admons:"
                    " either rgb tuple (--latex_admon_color=0.1,0.1,0.4) or saturated color"
                    "('--latex_admon_color=yellow!5' - note the quotes needed for bash). \n"
                    "  Multiple values can be assigned, one for each admon (all admons must be specified): "
                    "'--latex_admon_color=warning:darkgreen!40!white;notice:darkgray!20!white;"
                    "summary:tucorange!20!white;question:red!50!white;block:darkgreen!40!white'"
                    "   If --latex_admon=mdfbox, the specification above with color1!X!color2 will automatically "
                    "trigger 2*X as the background color of the frametitle.\n"
                    "  There are predefined multiple values, e.g., --latex_admon_color=colors1 gives red warnings, "
                    "blue notice, orange questions, green summaries and yellow blocks, automatically adjusted "
                    "with darker frametitles. \n"
                    "  If --latex_admon=mdfbox, the background of the title and the color "
                    "of the border of box can also be customized by direct editing. For example, a dark blue border "
                    "and light blue title background is obtained by editing the .tex file as \n"
                    "  doconce replace 'linecolor=black,' 'linecolor=darkblue,' mydoc.tex \n"
                    "  doconce subst 'frametitlebackgroundcolor=.*?,' 'frametitlebackgroundcolor=blue!5,' mydoc.tex\n"
                    "  Actually, this particular (and common) edit is automatically done by the option "
                    "--latex_admon_color=bluestyle\n"
                    "--latex_admon_color=yellowstyle (the latter has color yellow!5 instead and yellow!20 for the border)"),
    ('--latex_admon_title_no_period', 'By default, a period is added to title admons that do not have a period, question'
                    ' mark, or similar. This option prevents adding a period such that the title acts like a heading.'),
    ('--latex_admon_envir_map=', 'Mapping of code envirs to new envir names inside admons, e.g., to get a different '
                    'code typesetting inside admons. This is useful if admons have a special color and the color '
                    'background of code blocks does not fit will with the color background inside admons. '
                    'Then it is natural to use a different verbatim code style inside admons. If specifying a number, '
                    'say 2, as in --latex_admon_envir_map=2, an envir like pycod gets the number appended: pycod2. '
                    'One can then in --latex_code_style= or in doconce ptex2tex or ptex2tex specify the typesetting '
                    'of pycod2 environments. Otherwise the specification must be a mapping for each envir that '
                    'should be changed inside the admons: --latex_admon_envir_map=pycod-pycod_yellow,fpro-fpro2 '
                    '(from-to,from-to,... syntax).'),
    ('--latex_subex_header_postfix=', 'Default: ). Gives headers a), b), etc. Can be set to period, colon, etc.'),
    ('--xelatex', 'Use xelatex instead of latex/pdflatex.'),
    ('--latex_double_hyphen', 'Replace single dash - by double dash -- in LaTeX output. Somewhat intelligent, but '
                    'may give unwanted edits. Use with great care!'),
    ('--latex_elsevier_journal=', 'Sets the journal name for the --latex_style=elsevier style. '
                    'Default: none (no journal name).'),
    ('--ipynb_split_pyshell=', 'Split interactive sessions into multiple cells after each output. Applies to pyshell '
                    'and ipy code environments. on, True, yes: split (default). off, False, no: do not split. '
                    'Note that pyshell-t and ipy-t environments just displays the session, while default pyshell and '
                    'ipy removes all output (all output from print statements will come after the entire session).'),
    ('--ipynb_disable_mpl_inline', 'Disable automatic insertion of `%matplotlib inline` before the first import '
                    'of matplotlib.'),
    ('--ipynb_cite=', 'Typesetting of bibliography. plain: simple native typesetting (same as pandoc) (default); '
                    'latex-plain: Similar to latex-style plain; latex: ipynb support for latex-style bibliographies '
                    '(not mature).'),
    ('--ipynb_admon=',  'Typesetting of admonitions (hint, remarks, box, notice, summary, warning, question, '
                    'block - quotes are typeset as quotes). quote: as Markdown quote (default) with gray line '
                    'on the left. paragraph: just the content with the title as paragraph heading. '
                    'hrule: title with horizontal rule above and below, then text and horozontal rule.'),
    ('--ipynb_figure=', 'How to typeset figures in ipynb: md (plain Markdown syntax); imgtag (<img src="..." '
                    'width=...> tag, default); Image (python cell with Image object).'),
    ('--ipynb_movie=', 'How to typeset movies in ipynb: md (plain Markdown syntax, default); HTML: python cell '
                    'with notebook `HTML` object containing the raw HTML code that is used in the DocOnce HTML format; '
                    'ipynb: python cell with notebook `HTML` object with simple/standard ipynb HTML code for '
                    'showing a YouTube or local video with a <video> tag.'),
    ('--ipynb_non_editable_text', "All text in a notebook is set to be uneditable. Code blocks are unchanged"),
    ('--ipynb_non_editable_code', "All codeblocks in a notebook is set to be uneditable"),
    ('--verbose', 'Write out all OS commands run by doconce.'),
    ('--examples_as_exercises', 'Treat examples of the form "==== Example: ..." as in exercise environments.'),
    ('--exercises_as_subsections', 'Forces exercises to be typeset as subsections. Used to override various '
                    'latex environments for exercises (esp. in Springer styles).'),
    ('--solutions_at_end', 'Show solutions to exercises at the end of the document.'),
    ('--without_solutions', 'Leave out solution environments from exercises.'),
    ('--answers_at_end', 'Show answers to exercises at the end of the document.'),
    ('--without_answers', 'Leave out answer environments from exercises.'),
    ('--without_hints', 'Leave out hints from exercises.'),
    ('--exercise_solution=', 'Typesetting of solutions: paragraph, admon, or quote.'),
    ('--wordpress', 'Make HTML output for wordpress.com pages.'),
    ('--tables2csv', 'Write each table to a CSV file table_X.csv, where X is the table number (autonumbered according '
                    'to appearance in the DocOnce source file).'),
    ('--sections_up', 'Upgrade all sections: sections to chapters, subsections to sections, etc.'),
    ('--sections_down', 'Downgrade all sections: chapters to sections, sections to subsections, etc.'),
    ('--os_prompt=', 'Terminal prompt in output from running OS commands (the @@@OSCMD instruction). None or empty: '
                    'no prompt, just the command; nocmd: no command, just the output. Default is "Terminal>".'),
    ('--code_skip_until=', '@@@CODE import: skip lines in files up to (and incuding) specified line.'),
    ('--code_prefix=', 'Prefix all @@@CODE imports with some path.'),
    ('--figure_prefix=', 'Prefix all figure filenames with, e.g., an URL.'),
    ('--movie_prefix=', 'Prefix all movie filenames with, e.g., an URL.'),
    ('--no_mp4_webm_ogg_alternatives', 'Use just the specified (.mp4, .webm, .ogg) movie file; do not allow '
                    'alternatives in HTML5 video tag. Used if the just the specified movie format should be played.'),
    ('--handout', 'Makes slides output suited for printing.'),
    ('--urlcheck', 'Check that all URLs referred to in the document are valid.'),
    ('--labelcheck=', 'Check that all ref{X} has a corresponding label{X}. Fake examples will fail this check and '
                    'so will generalized references. Turn on when useful. Values: off (default), on.'),
    ('--short_title=', "Short version of the document's title."),
    ('--markdown', 'Allow Markdown (and some Extended Markdown) syntax as input.'),
    ('--md2do_output=', 'Dump to file the DocOnce code arising from converting from Markdown. Default value is None '
                    '(no dump). Any filename can be specified: --md2do_output=myfile.do.txt'),
    ('--github_md', 'Turn on GitHub-flavored Markdown dialect of the pandoc translator'),
    ('--slate_md', 'Turn on Slate-extensions to Markdown in the pandoc translator. To be used together with --github_md.'),
    ('--strapdown', 'Wrap Markdown output in HTML header/footer such that the output file (renamed as .html) '
                    'can automatically be rendered as an HTML via strapdownjs.com technology. Combine with '
                    '--github_md for richer output. Styles are set with --bootswatch_theme=cyborg (for instance).'),
    ('--bootswatch_theme=', 'Bootswatch theme for use with --strapdown option.'),
    ('--strict_markdown_output', 'Ensure strict/basic Markdown as output.'),
    ('--multimarkdown_output', 'Allow MultiMarkdown as output.'),
    ('--quiz_question_prefix=', 'Prefix/title before question in quizzes. Default: "Question:". Can also be set '
                    'in square brackets for each individual question. ("Q: [] What is 1+1?" results in '
                    'no prefix/title before the "What is 1+1?".'),
    ('--quiz_choice_prefix=', 'Prefix/title before choices in quizzes. \n  Default for HTML: "Choice", resulting '
                    'in numbered choices "Choice 1:", "Choice 2:", etc. \n  A value with colon, period, or question '
                    'mark (e.g., "Answer:") leaves out the numbering. \n  Default for latex/pdflatex: letter or '
                    'letter+checkbox. \n  Other values: number, number+checkbox, number+circle, letter+circle, letter. '
                    '\n  The checkbox or circle is always omitted if answers or solutions are included (i.e., if '
                    'none of the --without_answers and --without_solutions is set). \n  The choice prefix can also '
                    'be set in square brackets for each individual choice. ("Cr: [] Two" results in no prefix/title '
                    'before the the answer "Two".'),
    ('--quiz_horizontal_rule=', 'on (default): <hr> before and after quiz in HTML. off: no <hr>.'),
    ('--quiz_explanations=', 'on/off. Some output formats do not support explanations with figures, math and/or '
                    'code, this option turns all explanations off.'),
    ('--rst_uio', 'Univ. of Oslo version of rst files for their Vortex system.'),
    ('--rst_mathjax', 'Use raw HTML with MathJax for LaTeX mathematics in rst files.'),
    ('--sphinx_preserve_bib_keys', "Use the user's keys to in bibliography instead of numbers"),
    ('--sphinx_keep_splits', 'Respect user\'s !split commands. Default: Override user\'s !split and insert new '
                    '!split before all topmost sections. This is what makes sense in a Sphinx Table of Contents '
                    'if one wants to split the document into multiple parts.'),
    ('--sphinx_figure_captions=', 'Font style in figure captions: emphasize (default) or normal. If you use boldface '
                    'or emphasize in the caption, the font style will be normal for that caption.'),
    ('--oneline_paragraphs', 'Combine paragraphs to one line (does not work well).'),
    ('--execute', 'Automatically run code blocks and show output below the code block.'),
    ('--execute=', 'continue (default), abort. Enable --execute and allow to abort execution on code errors.'),
    ('--verbose-execute', 'Print output from execute cells.'),
    ('--ignore_output', 'Ignore output cells. Useful when you want to use execute rather than predefined output cells.'),
    ('--html_responsive_figure_width', 'Use figure width as max-width, and set width to 100 percent so that figures '
                        'can shrink to device width.')
    ]
