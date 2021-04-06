# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = '_'
short_title = project
copyright = '2021, A Document for Testing DocOnce'
author = 'A Document for Testing DocOnce'

# The full version, including alpha/beta/rc tags
release = 'Hans Petter Langtangen, Kaare Dump, A. Dummy Author, I. S. Overworked and Outburned and J. Doe'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
          #'sphinx.ext.pngmath',
          #'sphinx.ext.jsmath',
          'sphinx.ext.mathjax',
          #'matplotlib.sphinxext.mathmpl',
          #'matplotlib.sphinxext.only_directives',
          'matplotlib.sphinxext.plot_directive',
          'sphinx.ext.autodoc',
          'sphinx.ext.doctest',
          'sphinx.ext.viewcode',
          'sphinx.ext.intersphinx',
          'sphinx.ext.inheritance_diagram',
          'IPython.sphinxext.ipython_console_highlighting']

#pngmath_dvipng_args = ['-D 200', '-bg Transparent', '-gamma 1.5']  # large math fonts (200)

# Make sphinx aware of the DocOnce lexer
def setup(app):
    from sphinx.highlighting import lexers
    from doconce.misc import DocOnceLexer
    lexers['doconce'] = DocOnceLexer()

# Check which additional themes that are installed
additional_themes_installed = []
additional_themes_url = {}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['_themes']
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

try:
    import alabaster
    additional_themes_installed.append('alabaster')
except ImportError:
    additional_themes_url['alabaster'] = 'pip install alabaster'

try:
    import sphinxjp.themes.solarized
    additional_themes_installed.append('solarized')
except ImportError:
    additional_themes_url['solarized'] = 'https://pypi.org/project/sphinxjp.themes.solarized: pip install --exists-action i sphinxjp.themes.solarized --upgrade'

try:
    import cloud_sptheme as csp
    additional_themes_installed.append('cloud')
    additional_themes_installed.append('redcloud')
except ImportError:
    url = 'https://pypi.org/project/cloud_sptheme/: pip install --exists-action i cloud_sptheme --upgrade'
    additional_themes_url['cloud'] = url
    additional_themes_url['redcloud'] = url


'''
# FIXME: think we do not need to test on basicstrap, but some themes
# need themecore and we must test for that
try:
    import sphinxjp.themecore
    if not 'sphinxjp.themecore' in extensions:
        extensions += ['sphinxjp.themecore']
    additional_themes_installed.append('basicstrap')
except ImportError:
    # Use basicstrap as an example on a theme with sphinxjp.themecore (??)
    additional_themes_url['basicstrap'] = 'https://github.com/tell-k/sphinxjp.themes.basicstrap: pip install --exists-action i sphinx-bootstrap-theme --upgrade'
'''

try:
    import sphinxjp.themes.impressjs
    additional_themes_installed.append('impressjs')
except ImportError:
    additional_themes_url['impressjs'] = 'https://github.com/shkumagai/sphinxjp.themes.impressjs: pip install --exists-action i egg=sphinxjp.themes.impressjs --upgrade'

try:
    import sphinx_bootstrap_theme
    additional_themes_installed.append('bootstrap')
except ImportError:
    additional_themes_url['bootstrap'] = 'https://github.com/ryan-roemer/sphinx-bootstrap-theme: pip install --exists-action i sphinx-bootstrap-theme --upgrade'

try:
    import icsecontrib.sagecellserver
    extensions += ['icsecontrib.sagecellserver']
except ImportError:
    # pip install --exists-action i sphinx-sagecell --upgrade
    pass

# Is the document built on readthedocs.org? If so, don't import
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:  # only import and set the theme if we're building docs locally
    try:
        import sphinx_rtd_theme
        additional_themes_installed.append('sphinx_rtd_theme')
    except ImportError:
        additional_themes_url['sphinx_rtd_theme'] = 'pip install sphinx_rtd_theme'

tinker_themes = [
  'dark', 'flat', 'modern5', 'minimal5', 'responsive']
# https://tinkerer.me/index.html
# See Preview Another Theme in the sidebar of the above URL
try:
    import tinkerer
    import tinkerer.paths
    additional_themes_installed += tinker_themes
except ImportError:
    for theme in tinker_themes:
        additional_themes_url[theme] = 'pip install tinkerer --upgrade'



# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = '0.1'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'agni'
#html_theme = 'ADCtheme'
#html_theme = 'agni'
#html_theme = 'agogo'
#html_theme = 'alabaster'
#html_theme = 'basic'
#html_theme = 'basicstrap'
#html_theme = 'bizstyle'
#html_theme = 'bloodish'
#html_theme = 'bootstrap'
#html_theme = 'cbc'
#html_theme = 'classic'
#html_theme = 'cloud'
#html_theme = 'default'
#html_theme = 'epub'
#html_theme = 'fenics'
#html_theme = 'fenics_classic'
#html_theme = 'fenics_minimal1'
#html_theme = 'fenics_minimal2'
#html_theme = 'haiku'
#html_theme = 'jal'
#html_theme = 'nature'
#html_theme = 'pylons'
#html_theme = 'pyramid'
#html_theme = 'redcloud'
#html_theme = 'scipy_lectures'
#html_theme = 'scrolls'
#html_theme = 'slim-agogo'
#html_theme = 'solarized'
#html_theme = 'sphinx_rtd_theme'
#html_theme = 'sphinxdoc'
#html_theme = 'traditional'
#html_theme = 'uio'
#html_theme = 'uio2'
#html_theme = 'vlinux-theme'
check_additional_themes= [
   'solarized', 'cloud', 'redcloud',
   'alabaster', 'bootstrap', 'impressjs']

for theme in check_additional_themes:
    if html_theme == theme:
        if not theme in additional_themes_installed:
            raise ImportError(
                'html_theme = \"%s\", but this theme is not installed. %s' % (theme, additional_themes_url[theme]))



if html_theme == 'solarized':
    pygments_style = 'solarized'



# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']