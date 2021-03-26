# run this file as:
# pytest --pdb test_run.py      # then in the debugger:  print(out.stdout)
# pytest -s test_run.py         #to capture stout
import pytest
import contextlib
import tempfile
import os
import sys
import re
import subprocess
import shutil

@contextlib.contextmanager
def cd_context(name):
    """cd as a context manager"""
    old = os.getcwd()
    os.chdir(name)
    yield
    os.chdir(old)

@pytest.fixture
def tdir():
    """Create a temporary testing dir"""
    tmpdir = tempfile.mkdtemp(prefix='test-doconce-')
    yield tmpdir
    shutil.rmtree(tmpdir)

def create_file_with_text(text='', fname=None):
    """ Then do os.remove(fname)"""
    if not fname:
        _, fname = tempfile.mkstemp()
    with open(fname, 'w') as f:
        f.write(text)
    return fname



### functions in misc.py
def test_find_file_with_extensions(tdir):
    from doconce.misc import find_file_with_extensions
    with cd_context(tdir):
        fname = 'a.do.txt'
        fname = create_file_with_text(text='', fname=fname)
        dirname, basename, ext, filename = find_file_with_extensions(fname, allowed_extensions=['.do.txt'])
        assert (dirname, basename, ext, filename) == ('','a','.do.txt',fname)
        dirname, basename, ext, filename = find_file_with_extensions(fname, allowed_extensions=['.txt','.do.txt'])
        assert (dirname, basename, ext, filename) == ('', 'a.do', '.txt', fname)
        dirname, basename, ext, filename = find_file_with_extensions(fname, allowed_extensions=[''])
        assert (dirname, basename, ext, filename) == ('', 'a.do.txt', '', fname)
        # ./ is stripped
        dirname, basename, ext, filename = find_file_with_extensions('./'+fname, allowed_extensions=['.do.txt'])
        assert (dirname, basename, ext, filename) == ('', 'a', '.do.txt', fname)
        # file not found
        dirname, basename, ext, filename = find_file_with_extensions(fname, allowed_extensions=['.do'])
        assert (dirname, basename, ext, filename) == (None, None, None, None)

def test_folder_checker(tdir):
    tdir_rel = os.path.relpath(tdir, start=os.getcwd())
    os.makedirs(os.path.join(tdir, 'mydir'))
    os.path.exists(os.path.join(tdir, 'mydir'))
    from doconce.misc import folder_checker
    # Test that it fails (I cannot, the code contains an _abort)
    #assert False == folder_checker(dirname='this fails')
    # Test current directory
    out = folder_checker(dirname='.')
    assert out == './'
    out = folder_checker(dirname='./')
    assert out == './'
    # Test relative paths
    mydir_abs = os.path.join(tdir, 'mydir')
    mydir_rel = os.path.relpath(mydir_abs, start=os.getcwd()) + '/'
    out = folder_checker(dirname=mydir_abs)
    assert out == mydir_rel
    # Test absolute paths
    out = folder_checker(dirname=mydir_abs)
    assert out == mydir_rel
    # Test from a different directory
    with cd_context(tdir):
        mydir_rel2 = os.path.relpath(mydir_abs, start=os.getcwd()) + '/'
        out = folder_checker(dirname=mydir_abs)
        assert out == mydir_rel2
        out = folder_checker(dirname=mydir_rel2)
        assert out == mydir_rel2


### functions in jupyterbook.py
def test_get_link_destinations():
    from doconce.jupyterbook import get_link_destinations
    text = ' "[Figure 1](#ch1:figure)\\n",\n    ' \
           '"<!-- dom:FIGURE: [wave1D_ipynb.png, width=500] Figure and label ' \
           '<div id=\\"ch1:figure\\"></div> -->\\n",\n' \
           '    "<!-- begin figure -->\\n",\n' \
           '    "<div id=\\"ch1:figure\\"></div>\\n",\n    '
    destinations, destination_tags = get_link_destinations(text)
    assert destinations == ['<div id=\\"ch1:figure\\">', '<div id=\\"ch1:figure\\">']
    assert destination_tags == ['ch1:figure', 'ch1:figure']
    destinations, destination_tags = get_link_destinations(re.sub('\\\\n', '\n', text))
    assert destinations == ['<div id=\\"ch1:figure\\">', '<div id=\\"ch1:figure\\">']
    assert destination_tags == ['ch1:figure', 'ch1:figure']

def test_fix_media_src():
    from doconce.jupyterbook import fix_media_src
    media_ipynb = (' "source":[\n'
                   '"Figure reference: [ch1:figure](ch1:figure.html#ch1:figure)\n",\n'
                   '"<!-- dom:FIGURE: [mypic.png, width=500] Figure and label <div id=\"ch1:figure\"></div> -->\n",'
                   '   "<div id=\"ch1:figure\"></div>\n",'
                   '   "<img src=\"mypic.png\" width=500><p style=\"font-size: 0.9em\"><i>Figure 1: Figure and label</i></p>\n",'
                   '   "<!-- end figure -->"\n]')
    dirname, dest = '', ''
    out = fix_media_src(media_ipynb, dirname, dest)
    assert out == media_ipynb
    dirname, dest = './', './'
    out = fix_media_src(media_ipynb, dirname, dest)
    assert out == media_ipynb
    dirname, dest = '.', '.'
    out = fix_media_src(media_ipynb, dirname, dest)
    assert out == media_ipynb
    # TODO more examples
    pass

def test_split_file():
    from doconce.jupyterbook import split_file
    md = 'nothing'
    chunks = split_file(md, separator='\n')
    assert chunks == [md]
    md = '<!-- !split -->\n<!-- jupyter-book 01_jupyterbook.ipynb -->\n# Chapter 1\n\n<!-- ch1:figure.html#ch1:figure -->'
    chunks = split_file('before' + md, separator='<!-- !split -->\n<!-- jupyter-book .* -->\n')
    assert chunks == ['before', md]



### functions in html.py
def test_string2href():
    from doconce.html import string2href
    assert string2href('') == ''
    assert string2href(' Section 1: what\'s this å? ') == 'section-1-what-s-this-&#229;'
    assert string2href(' @-"test? ') == 'test'



### system test
def cp_testdoc(dest):
    shutil.copy('testdoc.do.txt', dest)
    shutil.copytree('testfigs', os.path.join(dest,'testfigs'))#, dirs_exist_ok=True)
    shutil.copy('_testdoc.do.txt', dest)
    shutil.copy('userdef_environments.py', dest)
    shutil.copy('bokeh_test.html', dest)
    shutil.copy('papers.pub', dest)

def test_doconce_format_html(tdir):
    # cp files
    cp_testdoc(dest=tdir)
    # run doconce format html
    # check that it fails
    out = subprocess.run(['doconce', 'format', 'html', 'testdoc.do.txtasdasds','--no_abort'])
    assert out.returncode != 0 # here return code is 1
    # check that it works
    out = subprocess.run(['doconce','format', 'html', 'testdoc.do.txt', '--examples_as_exercises'],
                         cwd=tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                         encoding='utf8')
    assert out.returncode == 0
    # TODO: consider to check STDOUT
    assert os.path.exists(os.path.join(tdir, 'testdoc.html'))
    # normalize output
    from tests import apply_regex
    apply_regex(os.path.join(tdir, 'testdoc.html'), logfilenameout=os.path.join(tdir, 'testdoc2.html'))
    shutil.copy(os.path.join(tdir, 'testdoc2.html'),'.')
    # TODO diff
    # TODO test from a different directory
    pass

def test_doconce_jupyterbook(tdir):
    cp_testdoc(dest=tdir)
    # doconce jupyterbook
    # check that it fails
    out = subprocess.run(['doconce', 'jupyterbook', 'fail!', '--no_abort'], cwd=tdir)
    assert out.returncode != 0
    # check that it works
    out = subprocess.run(['doconce', 'jupyterbook', 'testdoc.do.txt', '--examples_as_exercises','--no_abort'],
                         cwd=tdir,      # NB: main process stays in curr dir, subprocesses in tdir
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, #can do this in debugger mode: print(out.stdout)
                         encoding='utf8')
    assert out.returncode == 0
    assert os.path.exists(os.path.join(tdir, '_toc.yml'))
    assert os.path.exists(os.path.join(tdir, '01_testdoc.md'))
    # test --dest and --dest_toc
    out = subprocess.run(['doconce', 'jupyterbook', 'testdoc.do.txt', '--dest=fail!'],
                         cwd = tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                         stdout = subprocess.PIPE,
                         stderr = subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                         encoding = 'utf8')
    assert out.returncode != 0
    os.makedirs(os.path.join(tdir, 'content'))
    out = subprocess.run(['doconce', 'jupyterbook', 'testdoc.do.txt',
                          '--dest=content', '--dest_toc=content', '--examples_as_exercises'],
                         cwd=tdir,      # NB: main process stays in curr dir, subprocesses in tdir
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, #can do this in debugger mode: print(out.stdout)
                         encoding='utf8')
    assert out.returncode == 0
    assert os.path.exists(os.path.join(tdir, 'content/_toc.yml'))
    assert os.path.exists(os.path.join(tdir, 'content/01_testdoc.md'))
    # absolute paths
    # call from current and parent directory
    for dest in ['.', '..']:
        with cd_context(dest):
            out = subprocess.run(['doconce', 'jupyterbook', os.path.join(tdir,'testdoc.do.txt'),
                                  '--dest=' + os.path.join(tdir,'content'),
                                  '--dest_toc=' + os.path.join(tdir,'content'),
                                  '--examples_as_exercises'],
                                 cwd=tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                                 encoding='utf8')
            assert out.returncode == 0
            assert os.path.exists(os.path.join(tdir, '_toc.yml'))
            assert os.path.exists(os.path.join(tdir, '01_testdoc.md'))

def test_html_remove_whitespace():
    pass

def test_get_header_parts_footer():
    pass

# Run in IDE
if __name__ == "__main__":
    pytest.main(['-v',
                 '-Wignore',
                 __file__])
