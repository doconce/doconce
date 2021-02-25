#!/usr/bin/env python
"""
This is the main test suite of DocOnce. Classical unit tests require
a huge amount of work to establish. Instead, we have collected basic
examples on functionality together with an increasing set of
constructions that has caused bugs. By running all translations on
the basic and more demanding texts, and comparing with reference
results, we can easily check if all the functionality invoked by
the tests works. This script puts all results in a file test.v, which
is to be compared to the reference data in test.r.
"""

import subprocess, os, sys, re, doconce.common, time

# recommendation: remove installation and reinstall (to test setup.py)

# Check that we have Internet
if not doconce.common.internet_access(2):
    print('No Internet connection. This verification will be very slow!')
    print('And it will be wrong...')
    time.sleep(3)

system_output = []

def add(filename, logfilename):
    print('...adding file', filename)
    if not os.path.isfile(logfilename):
        raise IOError('Could not open ' + logfilename)
    log = open(logfilename, 'a')
    log.write("\n************** File: %s *****************\n" % filename)
    if not os.path.isfile(filename):
        log.write('NOT FOUND!')
    else:
        f = open(filename, 'r')
        fstr = f.read()
        f.close()
        log.write(fstr)
    log.close()

def clean_and_make(append=True):
    print('\n\nCleaning....................................')
    failure = os.system('sh -x clean.sh > /dev/null')
    if failure:
        raise OSError('Could not run clean.sh successfully')
    print('\n\nRunning make.sh...............................\nin', os.getcwd())
    failure, output = subprocess.getstatusoutput('bash -x make.sh')
    system_output.append(output)
    if failure:
        where = os.getcwd()
        for line in output.splitlines():
            print(line)
        raise OSError('Could not run %s/make.sh successfully!\nRerun manually (go to %s and run ./make.sh' % (where, where))

def apply_regex(logfilename, logfilenameout=None):
    # Subst text that we do not want to see in the diff such as dates
    # Open and create the log files
    if not logfilenameout:
        logfilenameout = logfilename
    log = open(logfilename, 'r')
    text = log.read()
    log.close()
    text += '\n\n'.join(system_output)
    date = r'[A-Z][a-z][a-z], \d?\d [A-Z][a-z][a-z] \d\d\d\d \(\d\d:\d\d\)'
    text = re.sub(date, r'Jan 32, 2100', text)
    date = r'[A-Z][a-z][a-z] \d?\d, \d\d\d\d'
    text = re.sub(date, r'Jan 32, 2100', text)
    text = re.sub(r'^DATE: .*? \(.+?\)$', r'DATE: Jan 32, 2100', text)
    text = re.sub(r'\d+ bytes', r'', text)
    text = re.sub(r'in paragraph at lines .*', r'', text)
    text = re.sub(r'undefined on input line .*', r'', text)
    text = re.sub(r'input line \d+', r'', text)
    text = re.sub(r'Underfull \\vbox.*', r'', text)
    text = re.sub(r'Overfull \\vbox.*', r'', text)
    text = re.sub(r'LaTeX Warning: .+? on page.*', r'', text)
    text = re.sub(r'^ ?\d+\.$', r'...rest of part of LaTeX line number...', text)
    text = re.sub(r'^(line|ine|ne) \d+\.$', r'...rest of part of LaTeX line number...', text)
    text = re.sub(r'\(\/usr\/share\/.+\)', '', text)
    text = re.sub(r'\\usepackage{anslistings,fancyvrb} % (.*)', r'\\usepackage{fancyvrb,anslistings} % \1', text)
    text = re.sub(r'\.{3} checking existence of .*\n\s{4}found!\n', r'', text)
    text = re.sub(r'<function html_verbatim at .*>', r'<function html_verbatim at XXX>', text)
    text = re.sub(r'20\d\d, Hans Petter', r'20XX, Hans Petter', text)
    text = re.sub(r'figure file .*\n\s+can use .*for format.*\n', 
        r'\n', text)
    text = re.sub(r'\.{3}doconce translation: figures \d{1,3}\.\d s \(accumulated time: \d{1,3}\.\d\)', 
        r'...doconce translation: figures XXX s (accumulated time: XXX)', text)
    text = re.sub(r'\(.*pt too wide\)', r'\(XXXpt too wide\)', text)
    text = re.sub(r'\.{3}doconce format used \d{1,3}\.\d s', r'...doconce format used XXX s', text)
    text = re.sub(r'\*{3} warning: hyperlink to URL .* is to a local file,\n.*recommended to be .*\n', r'\n', text)
    text = re.sub(r'\.{3} checking existence of .*\n.*found!\n', r'\n', text)
    #re.sub(r'DocOnce version [\.\d]+', r'/X/X/X', text)
    text = re.sub(r'DocOnce version [\.\d]+ \(.*\)', r'DocOnce version X.X.X', text)
    text = re.sub(os.getenv("HOME")+r'[/\w]*/(\w*)', r'/X/X/\1', text) 
    text = re.sub(r'found \..*png\n', r'', text)
    text = re.sub(r'[\n]*(\.\.\. checking existence.*)[\n]*', r'\n\1\n', text)    
    text = re.sub(r'^fancyvrb.sty\s+[\/\d]+\s*$', r'', text)
    log = open(logfilenameout, 'w')
    log.write(text)
    log.close()

def run():
    thisdir = os.getcwd()
    logfilename = os.path.join(thisdir, 'test.v')
    log = open(logfilename, 'w')
    log.close()  # just touch the file

    # test multiple authors, figure, movie, math, encodings, etc:
    print('...running ./make.sh in test')  # works only under Unix...
    clean_and_make(append=False)

    open(logfilename, 'a').close()
    files = '.do.txt', '.html', '.p.tex', '_bigex.tex', '.tex_doconce_ptex2tex', '.tex_direct', '.rst', '.sphinx.rst', '.gwiki', '.mwiki', '.cwiki', '.st', '.epytext', '.txt', '.md', '.ipynb', '.m', '.tmp'
    files = ['testdoc' + ext for ext in files] + [
        '.testdoc.exerinfo', 'tmp_encodings.txt', 'html_template.do.txt', 'html_template1.html', 'html_template.html', 'template1.html', 'author1.html', 'author1.p.tex', 'author1.rst', 'author1.txt', 'author2_siamltex.tex', 'author2_elsevier.tex', '._testdoc000.html', '._testdoc001.html', '._testdoc002.html', '._testdoc003.html', 'testdoc_wordpress.html', 'testdoc_no_solutions.html', 'testdoc_no_solutions.p.tex', 'mako_test1.html', 'mako_test2.html', 'mako_test3.html', 'mako_test3b.html', 'mako_test4.html', 'automake_sphinx_testdoc.py', 'testdoc_sphinx_index.rst', 'testdoc_sphinx_conf.py', 'automake_sphinx_math_test.py', '.testdoc_html_file_collection', 'make.sh', 'math_test.do.txt', 'math_test.md', 'math_test_html.html', 'math_test_pandoc.html', 'math_test.p.tex', 'math_test.rst', 'testdoc_vagrant.html', '._testdoc_vagrant000.html', '._testdoc_vagrant001.html', '._testdoc_vagrant002.html', '._testdoc000.rst', '._testdoc001.rst', '._testdoc002.rst', 'admon.p.tex', 'admon_colors1.tex', 'admon_colors2.tex', 'admon_mdfbox.tex', 'admon_graybox2.tex', 'admon_grayicon.tex', 'admon_paragraph-footnotesize.tex', 'admon_yellowicon.tex', 'admon_double_envirs.tex', 'admon_colors.html', 'admon_gray.html', 'admon_yellow.html', 'admon_sphinx/admon.html', 'admon_lyx.html', 'admon_paragraph.html', 'admon_apricot.html', 'admon_vagrant.html', 'admon_bootstrap_alert.html', 'admon_bootswatch_panel.html', '._admon_bootstrap_alert001.html', '._admon_bootstrap_alert002.html', 'admon_mwiki.mwiki', 'admon.rst', 'admon_paragraph.txt', 'locale.do.txt', 'locale.html', 'locale.tex', 'slides1.do.txt', 'slides1_reveal.html', 'tmp_slides_html_all.sh', 'slides1_1st.html', 'slides1_deck.html', 'slides1_remark.html', 'slides1.tex', 'slides1_handout.tex', 'slides2.do.txt', 'slides2_reveal.html', 'slides2.p.tex', 'slides2.tex', 'slides3.do.txt', 'slides3_reveal.html', '._slides3-solarized3001.html', 'slides3.p.tex', 'slides3.tex', 'table_1.csv', 'table_2.csv', 'table_3.csv', 'table_4.csv', 'testtable.csv', 'testtable.do.txt', 'github_md.md', 'movies.do.txt', 'movies_3choices.html', 'movies.html', 'movies.p.tex', 'movies.tex', 'movies_media9.tex', 'movies.txt', 'movie_player4.html', 'movie_player5.html', 'movie_player6.html', 'encoding3.do.txt', 'encoding3.p.tex-ascii', 'encoding3.html-ascii', 'encoding3.p.tex-ascii-verb', 'encoding3.html-ascii-verb', 'encoding3.p.tex-utf8', 'encoding3.html-utf8', '_genref1.do.txt', '_genref2.do.txt', '_tmp_genref2.do.txt', 'tmp_subst_references.sh', 'Springer_T2/Springer_T2_book.do.txt','Springer_T2/Springer_T2_book.p.tex', 'Springer_T2/Springer_T2_book.tex', 'test_boots.do.txt', 'test_boots.html', '._test_boots001.html', '._test_boots002.html', 'mdinput2do.do.txt', '.testdoc.quiz', 'encoding1.html', 'testdoc_exer.do.txt', 'nbdemo.ipynb', 'nbdemo.do.txt', 'test_copyright.out', 'tailored_conf.py', 'testdoc_code_prefix.html', 'automake_sphinx.log']
    files.insert(1, '_testdoc.do.txt')
    standalone_exercises = [
        'exercise_1.do.txt', 'selc_composed.do.txt',
        'subexer_a.do.txt',  'exercise_4.do.txt', 'verify_formula.do.txt',
        'exercise_7.do.txt', 'myexer1.do.txt', 'exercise_8.do.txt',
        'exercise_9.do.txt',
        'norm.do.txt', 'index.do.txt', 'make.py',]
    standalone_exercises = [os.path.join('standalone_exercises', f) for f
                            in standalone_exercises]
    files += standalone_exercises
    standalone_exercises = ['Chapter_2.1.do.txt', 'Chapter_2.2.do.txt',
                            'index.do.txt', 'make.py',]
    standalone_exercises = [os.path.join('Springer_T2',
                                         'standalone_exercises', f) for f
                            in standalone_exercises]
    files += standalone_exercises

    for f in files:
        add(f, logfilename)

    # Drop tutorial
    """
    tutdir = os.path.join(os.pardir, 'doc', 'src', 'tutorial')
    print('cd', tutdir)
    os.chdir(tutdir)

    print('...running ./make.sh in doc/tutorial')  # works only under Unix...
    clean_and_make()

    add('make.sh', logfilename)
    os.chdir('demo')
    # concentrate on files generated by doconce (not rst2*.py):
    files = '.do.txt', '.html', '.p.tex', '.rst', '.sphinx.rst', '.gwiki', '.mwiki', '.cwiki', '.st', '.epytext', '.txt', '.md'
    files = ['tutorial' + ext for ext in files]
    for f in files:
        add(f, logfilename)
    add(os.path.join(os.pardir, '_what_is.do.txt'), logfilename)
    add(os.path.join(os.pardir, '_doconce2anything.do.txt'), logfilename)
    """

    os.chdir(thisdir)
    # test DocWriter:
    failure, output = subprocess.getstatusoutput('python ../lib/doconce/DocWriter.py')
    files = 'tmp_DocOnce.do.txt', 'tmp_DocWriter.do.txt', 'tmp_DocWriter.html', \
            'tmp_HTML.html'
    for f in files:
        add(f, logfilename)

    # test manual:
    """
    mandir = os.path.join(os.pardir, 'doc', 'manual')
    print('cd', mandir)
    os.chdir(mandir)

    clean_and_make()

    add('make.sh', logfilename)
    files = '.do.txt', '.html', '.p.tex', '.rst', '.sphinx.rst', '.gwiki', '.mwiki', '.cwiki', '.st', '.epytext', '.txt', '.md'
    files = ['manual' + ext for ext in files]
    for f in files:
        add(f, logfilename)
    add('install.do.txt', logfilename)
    """
    os.chdir(thisdir)

    # test quickref:
    quickdir = os.path.join(os.pardir, 'doc', 'src', 'quickref')
    print('cd', quickdir)
    os.chdir(quickdir)

    clean_and_make()

    add('make.sh', logfilename)
    files = '.do.txt', '.html', '.tex', '.rst', '.sphinx.rst', '.gwiki', '.mwiki', '.cwiki', '.st', '.epytext', '.txt', '.md'
    files = ['quickref' + ext for ext in files]
    for f in files:
        add(f, logfilename)
    
    os.chdir(thisdir)

    # Clean log file using regex
    import time
    time.sleep(5)
    apply_regex(logfilename)


if __name__ == "__main__":
    run()
