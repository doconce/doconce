#!/usr/bin/env python
# Compile all stand-alone exercises to latex and ipynb
# (Must first unzip archive)

import glob, os

dofiles = glob.glob('*.do.txt')
dofiles.remove('index.do.txt')   # compile to html only

for dofile in dofiles:
    cmd = 'doconce format pdflatex %s --latex_code_style=vrb --figure_prefix=../ --movie_prefix=../' % dofile
    os.system(cmd)
    # Edit .tex file and remove doconce-specific things
    cmd = 'doconce subst "%% #.+" "" %s.tex' % dofile[:-7]  # preprocess
    os.system(cmd)
    cmd = 'doconce subst "%%.*" "" %s.tex' % dofile[:-7]

    cmd = 'doconce format ipynb %s --figure_prefix=../  --movie_prefix=../' % dofile
    os.system(cmd)

# Edit FILE_EXTENSIONS to adjust what kind of files that is listed in index.html
cmd = 'doconce format html index --html_style=bootstrap'
os.system(cmd)
