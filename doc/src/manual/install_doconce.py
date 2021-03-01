#!/usr/bin/env python
# Automatically generated script by
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# where vagrantbox is the directory arising from
# git clone git@github.com:doconce/vagrantbox.git

# The script is based on packages listed in debpkg_doconce.txt.

from __future__ import print_function
logfile = 'tmp_output.log'  # store all output of all operating system commands
f = open(logfile, 'w'); f.close()  # touch logfile so it can be appended

import subprocess, sys

def system(cmd):
    """Run system command cmd."""
    print(cmd)
    try:
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True, 
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('Command\n  %s\nfailed.' % cmd)
        print('Return code:', e.returncode)
        print(e.output)
        sys.exit(1)
    print(output)
    f = open(logfile, 'a'); f.write(output); f.close()

system('sudo apt-get update --fix-missing')
# Installation script for doconce and all dependencies

# This script is translated from
# doc/src/manual/debpkg_doconce.txt
# in the doconce source tree, with help of
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# (git clone git@github.com:doconce/vagrantbox.git)

# Python v3.4 must be installed (doconce does not work with v3.x)


cmd = """
pyversion=`python -c 'import sys; print(sys.version[:3])'`
if [ $pyversion == '2.7' ]; then echo "Python v${pyversion} cannot be used with DocOnce"; exit 1; fi
# Install downloaded source code in subdirectory srclib

if [ ! -d srclib ]; then mkdir srclib; fi
# Version control systems

"""
system(cmd)
system('sudo apt-get -y install mercurial')
system('sudo apt-get -y install git')
system('sudo apt-get -y install subversion')

# --- Python-based packages and tools ---
system('sudo apt-get -y install python-pip')
system('sudo apt-get -y install idle')
system('sudo apt-get -y install python-dev')
system('sudo apt-get -y install python-setuptools')
# upgrade
system('pip install setuptools')
system('sudo apt-get -y install python-pdftools')
system('pip install ipython')
system('pip install jupyter')
system('pip install tornado')
system('pip install pyzmq')
system('pip install traitlets')
system('pip install pickleshare')
system('pip install jsonschema')

# Preprocessors
system('pip install future')
system('pip install mako')
system('pip install preprocess')

# Publish for handling bibliography
system('pip install python-Levenshtein')
system('sudo apt-get -y install libxml2-dev')
system('sudo apt-get -y install libxslt1-dev')
system('sudo apt-get -y install zlib1g-dev')
system('pip install lxml')
system('pip install publish-doconce')

# Sphinx (with additional third/party themes)
system('pip install sphinx')

system('pip install alabaster')
system('pip install sphinx_rtd_theme')
system('pip install cloud_sptheme')
system('pip install sphinx-bootstrap-theme')
system('pip install sphinxjp.themes.solarized')
system('pip install sphinxjp.themes.impressjs')
system('pip install sphinx-sagecell')
# tinkerer has several themes: minimal5, modern5, flat, dark, responsive
#pip install tinkerer --upgrade

# Runestone sphinx books
system('pip install sphinxcontrib-paverutils')
system('pip install paver')
system('pip install cogapp')

#pip install -e git+https://bitbucket.org/sanguineturtle/pygments-ipython-console#egg=pygments-ipython-console
system('pip install --exists-action i pygments-ipython-console')
system('pip install --exists-action i pygments-doconce')

# XHTML
system('pip install beautifulsoup4')
system('pip install html5lib')

# ptex2tex is not needed if the --latex_code_style= option is used

cmd = """
cd srclib
git clone git@github.com:doconce/ptex2tex.git
cd ptex2tex
python setup.py install
cd latex
sh cp2texmf.sh
cd ../../..
# LaTeX

"""
system(cmd)
system('sudo apt-get -y install texinfo')
system('sudo apt-get -y install texlive')
system('sudo apt-get -y install texlive-extra-utils')
system('sudo apt-get -y install texlive-latex-extra')
system('sudo apt-get -y install texlive-latex-recommended')
system('sudo apt-get -y install texlive-science')
system('sudo apt-get -y install texlive-font-utils')
system('sudo apt-get -y install texlive-humanities')
system('sudo apt-get -y install latexdiff')
system('sudo apt-get -y install auctex')

# Image manipulation
system('sudo apt-get -y install imagemagick')
system('sudo apt-get -y install inkscape')
system('sudo apt-get -y install netpbm')
system('sudo apt-get -y install mjpegtools')
#pdftk has been dropped
#system('sudo apt-get -y install pdftk')
try:
    system('sudo snap install pdftk')
except:
    pass
system('sudo apt-get -y install giftrans')
system('sudo apt-get -y install gv')
system('sudo apt-get -y install evince')
system('sudo apt-get -y install smpeg-plaympeg')
system('sudo apt-get -y install mplayer')
system('sudo apt-get -y install totem')
#libav-tools has been superseded by ffmpeg
#system('sudo apt-get -y install libav-tools')
system('sudo apt-get -y install ffmpeg')

# Misc
system('sudo apt-get -y install ispell')
system('sudo apt-get -y install aspell')
system('sudo apt-get -y install pandoc')
system('sudo apt-get -y install libreoffice')
system('sudo apt-get -y install unoconv')
system('sudo apt-get -y install libreoffice-dmaths')
#epydoc is an old-fashioned output format, will any doconce user use it?
#pip install -e svn+https://epydoc.svn.sourceforge.net/svnroot/epydoc/trunk/epydoc#egg=epydoc

system('sudo apt-get -y install curl')
system('sudo apt-get -y install a2ps')
system('sudo apt-get -y install wdiff')
system('sudo apt-get -y install meld')
system('sudo apt-get -y install diffpdf')
system('sudo apt-get -y install kdiff3')
system('sudo apt-get -y install diffuse')

# tkdiff.tcl:
#tcl8.5-dev tk8.5-dev blt-dev
#https://sourceforge.net/projects/tkdiff/

# example on installing mdframed.sty manually (it exists in texlive,
# but sometimes needs to be in its newest version)

print('Everything is successfully installed!')
