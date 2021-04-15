# run this file as:
# pytest --pdb test_run.py      # then in the debugger:  print(out.stdout)
# pytest -s test_run.py         #to capture stout
# pytest -v test_run.py::test_html_remove_whitespace #only one test
# when assers fail, +/- are left/right
import pytest
import contextlib
import tempfile
import os
import sys
import re
import subprocess
import shutil
from doconce.doconce import load_modules

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

def test_folder_checker(tdir, monkeypatch):
    #tdir_rel = os.path.relpath(tdir, start=os.getcwd())
    os.makedirs(os.path.join(tdir, 'mydir'))
    os.path.exists(os.path.join(tdir, 'mydir'))
    from doconce.misc import folder_checker
    # Test that it fails
    monkeypatch.setattr(sys.modules['doconce.misc'], '_abort', lambda *args: sys.exit)
    assert 'this means failure/' == folder_checker(dirname='this means failure')
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
                   '   "<img src=\"mypic.png\" width=500><p style=\"font-size: 0.9em\">'
                   '<i>Figure 1: Figure and label</i></p>\n",'
                   '   "<!-- end figure -->"\n]')
    out = fix_media_src(media_ipynb, dirname='', dest='')
    assert out == media_ipynb
    out = fix_media_src(media_ipynb, dirname='./', dest='./')
    assert out == media_ipynb
    out = fix_media_src(media_ipynb, dirname='.', dest='.')
    assert out == media_ipynb
    assert '<!-- dom:FIGURE: [../../mypic.png,' in fix_media_src(media_ipynb, dirname='..', dest='whatever')
    assert '<!-- dom:FIGURE: [folder/mypic.png,' in fix_media_src(media_ipynb, dirname='folder', dest='')
    media_ipynb = '<img src=\\"wave1D_ipynb.png\\" width=500><p style=\\"font-size: 0.9em\\">'
    assert fix_media_src(media_ipynb, dirname='folder', dest='folder/sub') == media_ipynb.replace('\"wave1D_','\"../wave1D_')
    assert fix_media_src(media_ipynb, dirname='folder/sub', dest='folder') == media_ipynb.replace('\"wave1D_','\"sub/wave1D_')
    assert fix_media_src(media_ipynb, dirname='folder/sub', dest='') == media_ipynb.replace('\"wave1D_','\"folder/sub/wave1D_')
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



### functions in doconce.py
def test_text_lines():
    from doconce.doconce import text_lines, inline_tag_subst
    assert text_lines('') == '\n'
    assert text_lines('a line') == '<p>a line</p>\n'
    assert text_lines('<!--a comment-->') == '<!--a comment-->\n'
    assert text_lines('<p>a line</p>') == '<p>a line</p>\n'
    assert text_lines('  <li> item1') == '  <li> item1\n'
    assert text_lines('  <li> item1') == '  <li> item1\n'
    assert text_lines('</div>') == '</div>\n'
    assert text_lines('  </div>') == '  </div>\n'
    assert text_lines('</table></tr>') == '</table></tr>\n'
    assert text_lines('a\nb\n!split\nc') == '\n<p>a b</p>\n!split\n<p>c</p>\n'
    assert text_lines('!bpop\n  *\n!epop') == '!bpop\n<p>  *</p>\n!epop\n'
    assert text_lines('The\n `!bslidecell` \ncmd') == '<p>The</p>\n `!bslidecell` \n<p>cmd</p>\n'
    load_modules('the global INLINE_TAGS_SUBST is needed', modules=['html'])
    input = inline_tag_subst('Verbatim `pycod -t`', 'html')
    assert text_lines(input) == '<p>Verbatim <code>pycod -t</code></p>\n'
    input = inline_tag_subst('Some *Italics* with text','html')
    assert text_lines(input) == '<p>Some <em>Italics</em> with text</p>\n'

def test_typeset_lists():
    from doconce.doconce import typeset_lists
    assert typeset_lists('a line', format='html') == 'a line\n'
    # TODO fails because of import
    load_modules('the global LIST is needed', modules=['html'])
    assert typeset_lists('    - keyword x: text', format='html').replace(' ','') == \
           '\n<dl>\n<dt>keywordx:<dd>\ntext\n</dl>\n\n'
    load_modules('    - keyword x: text', modules=['latex'])
    assert typeset_lists('    - keyword x: text', format='latex').replace(' ','') == \
           '\\begin{description}\n\\item[keywordx:]\ntext\n\\end{description}\n\n\\noindent\n'



### functions in slides.py
def test_get_package_data():
    from doconce.slides import get_package_data
    data = get_package_data('deck.js-latest.zip', os.path.join('deck.js-latest','boilerplate.html'))
    assert data.find('<!DOCTYPE html>') > -1
    assert data.find('deck.menu.css') > -1
    data = get_package_data('csss.zip', os.path.join('csss', 'theme.css'))
    assert data.find('.slide h1 {') > -1

def test_get_deck_header():
    from doconce.slides import get_deck_header
    output = get_deck_header()
    assert output.find('imakewebthings/deck.js') > -1
    assert output.find('deck.js-latest/') > -1

def test_get_deck_footer():
    from doconce.slides import get_deck_footer
    output = get_deck_footer()
    assert output.find('Begin extension snippets') > -1



### system test
def cp_testdoc(dest, files=None):
    if not files:
        files = ['testdoc.do.txt', '_testdoc.do.txt', 'userdef_environments.py', 'bokeh_test.html', 'testfigs/papers.pub']
    for file in files:
        shutil.copy(file, dest)
    # cp the directory with resources anyway
    shutil.copytree('testfigs', os.path.join(dest, 'testfigs'))  # , dirs_exist_ok=True)

def test_doconce_format_html(tdir):
    # cp files
    cp_testdoc(dest=tdir)
    # run doconce format html
    # check that it fails
    out = subprocess.run('doconce format html fail --no_abort'.split(' '))
    assert out.returncode != 0 # here return code is 1
    # check that it works
    out = subprocess.run('doconce format html testdoc.do.txt --examples_as_exercises'.split(' '),
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

def test_doconce_format_latex(tdir):
    # cp files
    cp_testdoc(dest=tdir)
    # run doconce format html
    # check that it fails
    out = subprocess.run('doconce format latex fail --no_abort'.split(' '))
    assert out.returncode != 0 # here return code is 1
    # check that it works
    out = subprocess.run('doconce format latex testdoc.do.txt --examples_as_exercises'.split(' '),
                         cwd=tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                         encoding='utf8')
    assert out.returncode == 0
    with open('testdoc.p.tex', 'r') as f:
        tex = f.read()
    assert 'common cases.\n\nAnd' in tex
    #assert r' \item \ref{sec1}' in tex

def test_latex_code():
    from doconce.latex import latex_code
    # filestr = latex_code('aa',[],[],[],'latex')
    # TODO cannot do? fails because globals. is not initialized
    pass


def test_doconce_jupyterbook(tdir):
    cp_testdoc(dest=tdir)
    # doconce jupyterbook
    # check that it fails
    out = subprocess.run('doconce jupyterbook fail --no_abort'.split(' '), cwd=tdir)
    assert out.returncode != 0
    # check that it works
    out = subprocess.run('doconce jupyterbook testdoc.do.txt --examples_as_exercises --no_abort'.split(' '),
                         cwd=tdir,      # NB: main process stays in curr dir, subprocesses in tdir
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, #can do this in debugger mode: print(out.stdout)
                         encoding='utf8')
    assert out.returncode == 0
    assert os.path.exists(os.path.join(tdir, '_toc.yml'))
    assert os.path.exists(os.path.join(tdir, '01_testdoc.md'))
    # test --dest and --dest_toc
    out = subprocess.run('doconce jupyterbook testdoc.do.txt --dest=fail!'.split(' '),
                         cwd = tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                         stdout = subprocess.PIPE,
                         stderr = subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                         encoding = 'utf8')
    assert out.returncode != 0
    os.makedirs(os.path.join(tdir, 'content'))
    out = subprocess.run('doconce jupyterbook testdoc.do.txt '
                         '--dest=content --dest_toc=content --examples_as_exercises'.split(' '),
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

def test_doconce_html_slides(tdir):
    # cp files
    cp_testdoc(dest=tdir)
    with cd_context(tdir):
        # first run doconce format html
        out = subprocess.run('doconce format html testdoc.do.txt --examples_as_exercises'.split(' '),
                             cwd=tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                             encoding='utf8')
        assert out.returncode == 0
        # deck.js slides
        os.system('cp testdoc.html temp.html')
        out = subprocess.run('doconce slides_html temp.html deck --html_transition_theme=none '
                             '--html_slide_theme=swiss'.split(' '),
                             cwd=tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                             encoding='utf8')
        assert out.returncode == 0
        with open('temp.html', 'r') as f:
            html = f.read()
        assert html.find('themes/style/swiss.css') > -1
        assert html.find('<link rel="stylesheet" media="screen" href="">') > 10
        # reveal.js slides
        os.system('cp testdoc.html temp.html')
        out = subprocess.run('doconce slides_html temp.html reveal '
                             '--html_slide_theme=solarized --html_slide_transition=none'.split(' '),
                             cwd=tdir,  # NB: main process stays in curr dir, subprocesses in tdir
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,  # can do this in debugger mode: print(out.stdout)
                             encoding='utf8')
        assert out.returncode == 0
        with open('temp.html', 'r') as f:
            html = f.read()
        assert html.find('solarized.css') > -1

def test_html_remove_whitespace():
    from doconce.html import html_remove_whitespace
    assert html_remove_whitespace('') == ''
    out = html_remove_whitespace('\n<p>par 1</p>\n\n<p></p>\n  \n<p>par 2</p>\n\n<!---->\n    \n')
    assert out == '\n<p>par 1</p>\n\n<p>par 2</p>\n\n<!---->\n    \n'

def test_get_header_parts_footer(tdir):
    from doconce.misc import get_header_parts_footer
    with cd_context(tdir):
        fname = 'a.do.txt'
        fname = create_file_with_text(text='', fname=fname)
        header, parts, footer = get_header_parts_footer(fname, format='html')
        assert (header, parts, footer) == ([], [[]], [])
        # TODO
    pass

# Run in IDE
if __name__ == "__main__":
    pytest.main(['-v',
                 '-Wignore',
                 __file__])
