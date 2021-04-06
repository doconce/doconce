#!/bin/bash -x
#set -x
#export PS4='+ l.${LINENO}: ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
name=quickref

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

set -x
sh ./clean.sh

# Mako include cannot accept ../manual/quidelines.do.txt so we need a local link
if [ ! -L guidelines.do.txt ]; then
    ln -s ../manual/guidelines.do.txt guidelines.do.txt
fi

# Make latest bin/doconce doc. The next commands will print this output to $name.html and $name.tex
# Use sed to replace terminal colors (four special characters per line) or pdflatex will halt
doconce > doconce_program.sh
sed -i 's/^\x1b\[[0-9;]*m//' doconce_program.sh
sed -i 's/\x1b\[[0-9;]*m//' doconce_program.sh
sed -i 's/\x1b\[[0-9;]*m\s*/\n# /' doconce_program.sh
sed -i 's/\x1b\[[0-9;]*m//g' doconce_program.sh

system doconce format html $name --pygments_html_style=none --no_preprocess --no_abort --html_style=bootswatch_readable

# This document has error message from multiple labels: some:fig:label
# (because the document is a doconce instruction!)

# pdflatex
system doconce format pdflatex $name --no_preprocess --latex_font=helvetica --no_ampersand_quote --latex_code_style=vrb --no_abort

# Since we have native latex table and --no_ampersand_quote, we need to
# manually fix the quote examples elsewhere
doconce subst '([^`])Guns & Roses([^`])' '\g<1>Guns {\&} Roses\g<2>' $name.tex
doconce subst '([^`])Texas A & M([^`])' '\g<2>Texas A {\&} M\g<2>' $name.tex
system pdflatex -shell-escape $name
system pdflatex -shell-escape $name

# Sphinx
system doconce format sphinx $name --no_preprocess --no_abort
rm -rf sphinx-rootdir
#ALE problem reproducible after: `git clean -fd && rm -rf sphinx-rootdir`
#Hack: because doconce sphinx_dir ony works the second time (after an error), trigger that error by creating a bogus conf.py in ./
touch conf.py
system doconce sphinx_dir theme=cbc $name dirname=sphinx-rootdir
doconce replace 'doconce format sphinx %s' 'doconce format sphinx %s --no-preprocess' automake_sphinx.py
system python automake_sphinx.py
cp $name.rst $name.sphinx.rst  # save

# reStructuredText:
system doconce format rst $name --no_preprocess --no_abort
rst2xml.py $name.rst > $name.xml
rst2odt.py $name.rst > $name.odt
rst2html.py $name.rst > $name.rst.html
rst2latex.py $name.rst > $name.rst.tex
system latex $name.rst.tex
latex $name.rst.tex
dvipdf $name.rst.dvi

# Other formats:
system doconce format plain $name --no_preprocess --no_abort
system doconce format gwiki $name --no_preprocess --no_abort
system doconce format mwiki $name --no_preprocess --no_abort
system doconce format cwiki $name --no_preprocess --no_abort
system doconce format st $name --no_preprocess --no_abort
system doconce format epytext $name --no_preprocess --no_abort
system doconce format pandoc $name --no_preprocess --strict_markdown_output --github_md --no_abort

rm -rf demo
mkdir demo
cp -r $name.do.txt $name.html $name.p.tex $name.tex $name.pdf $name.rst $name.xml $name.rst.html $name.rst.tex $name.rst.pdf $name.gwiki $name.mwiki $name.cwiki $name.txt $name.epytext $name.st $name.md sphinx-rootdir/_build/html demo

cd demo
cat > index.html <<EOF
<HTML><BODY>
<TITLE>Demo of Doconce formats</TITLE>
<H3>Doconce demo</H3>

Doconce is a minimum tagged markup language. The file
<a href="$name.do.txt">$name.do.txt</a> is the source of the
Doconce $name, written in the Doconce format.
Running
<pre>
doconce format html $name.do.txt
</pre>
produces the HTML file <a href="$name.html">$name.html</a>.
Going from Doconce to LaTeX is done by
<pre>
doconce format latex $name.do.txt
</pre>
resulting in the file <a href="$name.tex">$name.tex</a>, which can
be compiled to a PDF file <a href="$name.pdf">$name.pdf</a>
by running <tt>latex</tt> and <tt>dvipdf</tt> the standard way.
<p>
The reStructuredText (reST) format is of particular interest:
<pre>
doconce format rst    $name.do.txt  # standard reST
doconce format sphinx $name.do.txt  # Sphinx extension of reST
</pre>
The reST file <a href="$name.rst">$name.rst</a> is a starting point
for conversion to many other formats: OpenOffice,
<a href="$name.xml">XML</a>, <a href="$name.rst.html">HTML</a>,
<a href="$name.rst.tex">LaTeX</a>,
and from LaTeX to <a href="$name.rst.pdf">PDF</a>.
The <a href="$name.sphinx.rst">Sphinx</a> dialect of reST
can be translated to <a href="$name.sphinx.pdf">PDF</a>
and <a href="html/index.html">HTML</a>.
<p>
Doconce can also be converted to
<a href="$name.gwiki">Googlecode wiki</a>,
<a href="$name.mwiki">MediaWiki</a>,
<a href="$name.cwiki">Creole wiki</a>,
<a href="$name.md">aPandoc</a>,
<a href="$name.st">Structured Text</a>,
<a href="$name.epytext">Epytext</a>,
and maybe the most important format of all:
<a href="$name.txt">plain untagged ASCII text</a>.
</BODY>
</HTML>
EOF

echo
echo "Go to the demo directory $PWD and load index.html into a web browser."

cd ..
dest=../../pub/$name
cp -r demo/html demo/$name.pdf demo/$name.html $dest

dest=../../../../doconce.wiki
cp -r demo/$name.md $dest
+ name=quickref
+ set -x
+ sh ./clean.sh
Removing in /X/X/quickref:
+ '[' '!' -L guidelines.do.txt ']'
+ doconce
+ sed -i 's/^\x1b\[[0-9;]*m//' doconce_program.sh
+ sed -i 's/\x1b\[[0-9;]*m//' doconce_program.sh
+ sed -i 's/\x1b\[[0-9;]*m\s*/\n# /' doconce_program.sh
+ sed -i 's/\x1b\[[0-9;]*m//g' doconce_program.sh
+ system doconce format html quickref --pygments_html_style=none --no_preprocess --no_abort --html_style=bootswatch_readable
+ doconce format html quickref --pygments_html_style=none --no_preprocess --no_abort --html_style=bootswatch_readable
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to html
copy complete file doconce_program.sh  (format: shpro)
*** warning: found emphasis tag *...* in footnote, which was removed
    in tooltip (since it does not work with bootstrap tooltips)
    but not in the footnote itself.
There is an exception: by using *user-defined environments* within `!bu-name` and `!eu-name` directives, it is possible to label any type of text and refer to it. For example, one can have environments for examples, tables, code snippets, theorems, lemmas, etc. One can also use Mako functions to implement environments.

*** warning: found inline code tag `...` in footnote, which was removed
    in tooltip (since it does not work with bootstrap tooltips):
There is an exception: by using user-defined environments within `!bu-name` and `!eu-name` directives, it is possible to label any type of text and refer to it. For example, one can have environments for examples, tables, code snippets, theorems, lemmas, etc. One can also use Mako functions to implement environments.

output in quickref.html
+ '[' 0 -ne 0 ']'
+ system doconce format pdflatex quickref --no_preprocess --latex_font=helvetica --no_ampersand_quote --latex_code_style=vrb --no_abort
+ doconce format pdflatex quickref --no_preprocess --latex_font=helvetica --no_ampersand_quote --latex_code_style=vrb --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to pdflatex
copy complete file doconce_program.sh  (format: shpro)
Final all \\label\{(.+?)\}
output in quickref.tex
+ '[' 0 -ne 0 ']'
+ doconce subst '([^`])Guns & Roses([^`])' '\g<1>Guns {\&} Roses\g<2>' quickref.tex
([^`])Guns & Roses([^`]) replaced by \g<1>Guns {\&} Roses\g<2> in quickref.tex
+ doconce subst '([^`])Texas A & M([^`])' '\g<2>Texas A {\&} M\g<2>' quickref.tex
([^`])Texas A & M([^`]) replaced by \g<2>Texas A {\&} M\g<2> in quickref.tex
+ system pdflatex -shell-escape quickref
+ pdflatex -shell-escape quickref
This is pdfTeX, Version 3.14159265-2.6-1.40.18 (TeX Live 2017/Debian) (preloaded format=pdflatex)
 \write18 enabled.
entering extended mode
(./quickref.tex
LaTeX2e <2017-04-15>
Babel <3.18> and hyphenation patterns for 84 language(s) loaded.
(/usr/share/texlive/texmf-dist/tex/latex/base/article.cls
Document Class: article 2014/09/29 v1.4h Standard LaTeX document class



(/usr/share/texlive/texmf-dist/tex/latex/graphics/color.sty



(/usr/share/texlive/texmf-dist/tex/latex/amsmath/amsmath.sty
For additional information on amsmath, use the `?' option.
(/usr/share/texlive/texmf-dist/tex/latex/amsmath/amstext.sty





(/usr/share/texlive/texmf-dist/tex/latex/xcolor/xcolor.sty

(/usr/share/texlive/texmf-dist/tex/latex/colortbl/colortbl.sty


(/usr/share/texlive/texmf-dist/tex/latex/ltablex/ltablex.sty


(/usr/share/texlive/texmf-dist/tex/latex/microtype/microtype.sty



(/usr/share/texlive/texmf-dist/tex/latex/graphics/graphicx.sty
(/usr/share/texlive/texmf-dist/tex/latex/graphics/graphics.sty



(/usr/share/texlive/texmf-dist/tex/latex/fancyvrb/fancyvrb.sty
Style option: `fancyvrb' v2.7a, with DG/SPQR fixes, and firstline=lastline fix 
<2008/02/07> (tvz)) 
 (/usr/share/texlive/texmf-dist/tex/latex/moreverb/moreverb.sty

(/usr/share/texlive/texmf-dist/tex/latex/base/fontenc.sty

(/usr/share/texlive/texmf-dist/tex/latex/ucs/ucs.sty

(/usr/share/texlive/texmf-dist/tex/latex/base/inputenc.sty



(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hyperref.sty
(/usr/share/texlive/texmf-dist/tex/generic/oberdiek/hobsub-hyperref.sty







(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hpdftex.def


(/X/X/mdframed.sty
(/usr/share/texlive/texmf-dist/tex/latex/l3packages/xparse/xparse.sty
(/usr/share/texlive/texmf-dist/tex/latex/l3kernel/expl3.sty



(/usr/share/texlive/texmf-dist/tex/latex/oberdiek/zref-abspage.sty


(/usr/share/texlive/texmf-dist/tex/latex/pgf/frontendlayer/tikz.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/basiclayer/pgf.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/utilities/pgfrcs.sty
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfutil-common.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfutil-common-lists.t
ex)) (/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfutil-latex.def


(/usr/share/texlive/texmf-dist/tex/latex/pgf/basiclayer/pgfcore.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/systemlayer/pgfsys.sty
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsys.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfkeys.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfkeysfiltered.code.t
ex)) 
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsys-pdftex.def
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsys-common-pdf.de
f)))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsyssoftpath.code.
tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsysprotocol.code.
tex))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcore.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmath.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathcalc.code.tex


(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.basic.code
.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.trigonomet
ric.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.random.cod
e.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.comparison
.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.base.code.
tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.round.code
.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.misc.code.
tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.integerari
thmetics.code.tex)))

(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepoints.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepathconstruct.
code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepathusage.code
.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorescopes.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoregraphicstate.c
ode.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoretransformation
s.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorequick.code.tex
)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreobjects.code.t
ex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepathprocessing
.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorearrows.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreshade.code.tex
)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreimage.code.tex

(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreexternal.code.
tex))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorelayers.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoretransparency.c
ode.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepatterns.code.
tex)))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/modules/pgfmoduleshapes.code.tex
) (/usr/share/texlive/texmf-dist/tex/generic/pgf/modules/pgfmoduleplot.code.tex
)
(/usr/share/texlive/texmf-dist/tex/latex/pgf/compatibility/pgfcomp-version-0-65
.sty)
(/usr/share/texlive/texmf-dist/tex/latex/pgf/compatibility/pgfcomp-version-1-18
.sty)) (/usr/share/texlive/texmf-dist/tex/latex/pgf/utilities/pgffor.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/utilities/pgfkeys.sty

(/usr/share/texlive/texmf-dist/tex/latex/pgf/math/pgfmath.sty

(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgffor.code.tex

(/usr/share/texlive/texmf-dist/tex/generic/pgf/frontendlayer/tikz/tikz.code.tex

(/usr/share/texlive/texmf-dist/tex/generic/pgf/libraries/pgflibraryplothandlers
.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/modules/pgfmodulematrix.code.tex
)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/frontendlayer/tikz/libraries/tik
zlibrarytopaths.code.tex)))
(/X/X/md-frame-1.mdf))

Writing index file quickref.idx
(/usr/share/texlive/texmf-dist/tex/latex/idxlayout/idxlayout.sty

(/usr/share/texlive/texmf-dist/tex/latex/tocbibind/tocbibind.sty

Package tocbibind Note: Using section or other style headings.

) (/usr/share/texlive/texmf-dist/tex/latex/ms/ragged2e.sty

No file quickref.aux.

(/usr/share/texlive/texmf-dist/tex/context/base/mkii/supp-pdf.mkii
[Loading MPS to PDF converter (version 2006.09.02).]
) (/usr/share/texlive/texmf-dist/tex/latex/oberdiek/epstopdf-base.sty



(/usr/share/texlive/texmf-dist/tex/latex/hyperref/nameref.sty

ABD: EveryShipout initializing macros ABD: EverySelectfont initializing macros










Package hyperref Warning: old toc file detected, not used; run LaTeX again.


 [1{/var/lib/texmf/fo
nts/map/pdftex/updmap/pdftex.map}] [2] [3]
Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 Note that ab-stracts are rec-og-nized by start-ing with [] or []

[4] [5 <./latex_figs/dizzy_face.png>] [6] [7]
Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 resulting in Some sen-tence with \T1/lmtt/m/n/10 words in verb
atim style\T1/phv/m/n/10 . Multi-line blocks

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 that maps en-vi-ron-ments (\T1/lmtt/m/n/10 xxx\T1/phv/m/n/10 )
 onto valid lan-guage types for Pyg-ments (which

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 ning text. New-com-mands must be de-fined in files with names \T
1/lmtt/m/n/10 newcommands*.tex\T1/phv/m/n/10 .

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 but you can com-bine the files into one file us-ing the []

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 tools for, e.g., com-ment-ing out/in large por-tions of text and
 cre-at-ing macros. 

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 Now we can do [] in the Do-cOnce source

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 The bib-li-og-ra-phy is spec-i-fied by a line \T1/lmtt/m/n/10 
BIBFILE: papers.pub\T1/phv/m/n/10 , where \T1/lmtt/m/n/10 papers.pub

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 (usu-ally af-ter the ti-tle, au-thors, and date). In this case t
he out-put text is \T1/lmtt/m/n/10 internal

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 ment, re-spec-tively. Com-bine with [] and []

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 the GitHub project and ex-am-ine the Do-cOnce source and the \T1
/lmtt/m/n/10 doc/src/make.sh

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 Excellent "Sphinx Tu-to-rial" by C. Reller: "http://people.ee.
ethz.ch/ creller/web/tricks/reST.html" 
[24] (./quickref.aux)

 *File List*
 article.cls    2014/09/29 v1.4h Standard LaTeX document class
  size10.clo    2014/09/29 v1.4h Standard LaTeX file (size option)
 relsize.sty    2013/03/29 ver 4.1
 makeidx.sty    2014/09/29 v1.0m Standard LaTeX package
   color.sty    1999/02/16
   color.cfg    2016/01/02 v1.6 sample color configuration
  pdftex.def    2018/01/08 v1.0l Graphics/color driver for pdftex
setspace.sty    2011/12/19 v6.7a set line spacing
 amsmath.sty    2017/09/02 v2.17a AMS math features
 amstext.sty    2000/06/29 v2.01 AMS text
  amsgen.sty    1999/11/30 v2.0 generic functions
  amsbsy.sty    1999/11/29 v1.2d Bold Symbols
  amsopn.sty    2016/03/08 v2.02 operator names
amsfonts.sty    2013/01/14 v3.01 Basic AMSFonts support
 amssymb.sty    2013/01/14 v3.01 AMS font symbols
  xcolor.sty    2016/05/11 v2.12 LaTeX color extensions (UK)
   color.cfg    2016/01/02 v1.6 sample color configuration
colortbl.sty    2012/02/13 v1.0a Color table columns (DPC)
   array.sty    2016/10/06 v2.4d Tabular extension package (FMi)
      bm.sty    2017/01/16 v1.2c Bold Symbol Support (DPC/FMi)
 ltablex.sty    2014/08/13 v1.1 Modified tabularx
longtable.sty    2014/10/28 v4.11 Multi-page Table package (DPC)
tabularx.sty    2016/02/03 v2.11 `tabularx' package (DPC)
microtype.sty    2018/01/14 v2.7a Micro-typographical refinements (RS)
  keyval.sty    2014/10/28 v1.15 key=value parser (DPC)
microtype-pdftex.def    2018/01/14 v2.7a Definitions specific to pdftex (RS)
microtype.cfg    2018/01/14 v2.7a microtype main configuration file (RS)
graphicx.sty    2017/06/01 v1.1a Enhanced LaTeX Graphics (DPC,SPQR)
graphics.sty    2017/06/25 v1.2c Standard LaTeX Graphics (DPC,SPQR)
    trig.sty    2016/01/03 v1.10 sin cos tan (DPC)
graphics.cfg    2016/06/04 v1.11 sample graphics configuration
    soul.sty    2003/11/17 v2.4 letterspacing/underlining (mf)
  framed.sty    2011/10/22 v 0.96: framed or shaded text with page breaks
moreverb.sty    2008/06/03 v2.3a `more' verbatim facilities
verbatim.sty    2014/10/28 v1.5q LaTeX2e package for verbatim enhancements
 fontenc.sty
   t1enc.def    2017/04/05 v2.0i Standard LaTeX file
     ucs.sty    2013/05/11 v2.2 UCS: Unicode input support
uni-global.def    2013/05/13 UCS: Unicode global data
inputenc.sty    2015/03/17 v1.2c Input encoding file
   utf8x.def    2004/10/17 UCS: Input encoding UTF-8
  helvet.sty    2005/04/12 PSNFSS-v9.2a (WaS) 
 lmodern.sty    2009/10/30 v1.6 Latin Modern Fonts
hyperref.sty    2018/02/06 v6.86b Hypertext links for LaTeX
hobsub-hyperref.sty    2016/05/16 v1.14 Bundle oberdiek, subset hyperref (HO)
hobsub-generic.sty    2016/05/16 v1.14 Bundle oberdiek, subset generic (HO)
  hobsub.sty    2016/05/16 v1.14 Construct package bundles (HO)
infwarerr.sty    2016/05/16 v1.4 Providing info/warning/error messages (HO)
 ltxcmds.sty    2016/05/16 v1.23 LaTeX kernel commands for general use (HO)
ifluatex.sty    2016/05/16 v1.4 Provides the ifluatex switch (HO)
  ifvtex.sty    2016/05/16 v1.6 Detect VTeX and its facilities (HO)
 intcalc.sty    2016/05/16 v1.2 Expandable calculations with integers (HO)
   ifpdf.sty    2017/03/15 v3.2 Provides the ifpdf switch
etexcmds.sty    2016/05/16 v1.6 Avoid name clashes with e-TeX commands (HO)
kvsetkeys.sty    2016/05/16 v1.17 Key value parser (HO)
kvdefinekeys.sty    2016/05/16 v1.4 Define keys (HO)
pdftexcmds.sty    2018/01/21 v0.26 Utility functions of pdfTeX for LuaTeX (HO)
pdfescape.sty    2016/05/16 v1.14 Implements pdfTeX's escape features (HO)
bigintcalc.sty    2016/05/16 v1.4 Expandable calculations on big integers (HO)
  bitset.sty    2016/05/16 v1.2 Handle bit-vector datatype (HO)
uniquecounter.sty    2016/05/16 v1.3 Provide unlimited unique counter (HO)
letltxmacro.sty    2016/05/16 v1.5 Let assignment for LaTeX macros (HO)
 hopatch.sty    2016/05/16 v1.3 Wrapper for package hooks (HO)
xcolor-patch.sty    2016/05/16 xcolor patch
atveryend.sty    2016/05/16 v1.9 Hooks at the very end of document (HO)
atbegshi.sty    2016/06/09 v1.18 At begin shipout hook (HO)
refcount.sty    2016/05/16 v3.5 Data extraction from label references (HO)
 hycolor.sty    2016/05/16 v1.8 Color options for hyperref/bookmark (HO)
 ifxetex.sty    2010/09/12 v0.6 Provides ifxetex conditional
 auxhook.sty    2016/05/16 v1.4 Hooks for auxiliary files (HO)
kvoptions.sty    2016/05/16 v3.12 Key value format for package options (HO)
  pd1enc.def    2018/02/06 v6.86b Hyperref: PDFDocEncoding definition (HO)
hyperref.cfg    2002/06/06 v1.2 hyperref configuration of TeXLive
     url.sty    2013/09/16  ver 3.4  Verb mode for urls, etc.
 hpdftex.def    2018/02/06 v6.86b Hyperref driver for pdfTeX
rerunfilecheck.sty    2016/05/16 v1.8 Rerun checks for auxiliary files (HO)
placeins.sty    2005/04/18  v 2.2
mdframed.sty    2014/05/30 2.0: mdframed
  xparse.sty    2018/02/21 L3 Experimental document command parser
   expl3.sty    2018/02/21 L3 programming layer (loader) 
expl3-code.tex    2018/02/21 L3 programming layer 
l3pdfmode.def    2017/03/18 v L3 Experimental driver: PDF mode
etoolbox.sty    2018/02/11 v2.5e e-TeX tools for LaTeX (JAW)
zref-abspage.sty    2016/05/21 v2.26 Module abspage for zref (HO)
zref-base.sty    2016/05/21 v2.26 Module base for zref (HO)
needspace.sty    2010/09/12 v1.3d reserve vertical space
    tikz.sty    2015/08/07 v3.0.1a (rcs-revision 1.151)
     pgf.sty    2015/08/07 v3.0.1a (rcs-revision 1.15)
  pgfrcs.sty    2015/08/07 v3.0.1a (rcs-revision 1.31)
everyshi.sty    2001/05/15 v3.00 EveryShipout Package (MS)
  pgfrcs.code.tex
 pgfcore.sty    2010/04/11 v3.0.1a (rcs-revision 1.7)
  pgfsys.sty    2014/07/09 v3.0.1a (rcs-revision 1.48)
  pgfsys.code.tex
pgfsyssoftpath.code.tex    2013/09/09  (rcs-revision 1.9)
pgfsysprotocol.code.tex    2006/10/16  (rcs-revision 1.4)
 pgfcore.code.tex
pgfcomp-version-0-65.sty    2007/07/03 v3.0.1a (rcs-revision 1.7)
pgfcomp-version-1-18.sty    2007/07/23 v3.0.1a (rcs-revision 1.1)
  pgffor.sty    2013/12/13 v3.0.1a (rcs-revision 1.25)
 pgfkeys.sty    
 pgfkeys.code.tex
 pgfmath.sty    
 pgfmath.code.tex
  pgffor.code.tex
    tikz.code.tex
md-frame-1.mdf    2014/05/30\ 2.0: md-frame-1
    calc.sty    2014/10/28 v4.3 Infix arithmetic (KKT,FJ)
idxlayout.sty    2012/03/30 v0.4d Configurable index layout
multicol.sty    2017/04/11 v1.8q multicolumn formatting (FMi)
tocbibind.sty    2010/10/13 v1.5k extra ToC listings
ragged2e.sty    2009/05/21 v2.1 ragged2e Package (MS)
everysel.sty    2011/10/28 v1.2 EverySelectfont Package (MS)
   t1phv.fd    2001/06/04 scalable font definitions for T1/phv.
supp-pdf.mkii
epstopdf-base.sty    2016/05/15 v2.6 Base part for package epstopdf
  grfext.sty    2016/05/16 v1.2 Manage graphics extensions (HO)
epstopdf-sys.cfg    2010/07/13 v1.3 Configuration of (r)epstopdf for TeX Live
 ucsencs.def    2011/01/21 Fixes to fontencodings LGR, T3
 nameref.sty    2016/05/21 v2.44 Cross-referencing by name of section
gettitlestring.sty    2016/05/16 v1.5 Cleanup title references (HO)
  ot1lmr.fd    2009/10/30 v1.6 Font defs for Latin Modern
  mt-cmr.cfg    2013/05/19 v2.2 microtype config. file: Computer Modern Roman (
RS)
  omllmm.fd    2009/10/30 v1.6 Font defs for Latin Modern
 omslmsy.fd    2009/10/30 v1.6 Font defs for Latin Modern
 omxlmex.fd    2009/10/30 v1.6 Font defs for Latin Modern
    umsa.fd    2013/01/14 v3.01 AMS symbols A
  mt-msa.cfg    2006/02/04 v1.1 microtype config. file: AMS symbols (a) (RS)
    umsb.fd    2013/01/14 v3.01 AMS symbols B
  mt-msb.cfg    2005/06/01 v1.0 microtype config. file: AMS symbols (b) (RS)
  t1lmtt.fd    2009/10/30 v1.6 Font defs for Latin Modern
  omsphv.fd    
latex_figs/dizzy_face.png
 ***********


Package rerunfilecheck Warning: File `quickref.out' has changed.
(rerunfilecheck)                Rerun to get outlines right
(rerunfilecheck)                or use package `bookmark'.


LaTeX Warning: There were undefined references.


LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.

 )
(see the transcript file for additional information){/usr/share/texmf/fonts/enc
/dvips/lm/lm-ec.enc}{/usr/share/texmf/fonts/enc/dvips/lm/lm-mathsy.enc}{/usr/sh
are/texmf/fonts/enc/dvips/lm/lm-rm.enc}{/usr/share/texmf/fonts/enc/dvips/lm/lm-
mathit.enc}{/usr/share/texlive/texmf-dist/fonts/enc/dvips/base/8r.enc}</usr/sha
re/texlive/texmf-dist/fonts/type1/public/amsfonts/cm/cmsy10.pfb></usr/share/tex
mf/fonts/type1/public/lm/lmmi10.pfb></usr/share/texmf/fonts/type1/public/lm/lmm
i7.pfb></usr/share/texmf/fonts/type1/public/lm/lmr10.pfb></usr/share/texmf/font
s/type1/public/lm/lmr6.pfb></usr/share/texmf/fonts/type1/public/lm/lmr7.pfb></u
sr/share/texmf/fonts/type1/public/lm/lmsy10.pfb></usr/share/texmf/fonts/type1/p
ublic/lm/lmtk10.pfb></usr/share/texmf/fonts/type1/public/lm/lmtt10.pfb></usr/sh
are/texmf/fonts/type1/public/lm/lmtt8.pfb></usr/share/texmf/fonts/type1/public/
lm/lmtt9.pfb></usr/share/texlive/texmf-dist/fonts/type1/urw/helvetic/uhvb8a.pfb
></usr/share/texlive/texmf-dist/fonts/type1/urw/helvetic/uhvr8a.pfb></usr/share
/texlive/texmf-dist/fonts/type1/urw/helvetic/uhvro8a.pfb>
Output written on quickref.pdf (XXX pages, ).
Transcript written on quickref.log.
+ '[' 0 -ne 0 ']'
+ system pdflatex -shell-escape quickref
+ pdflatex -shell-escape quickref
This is pdfTeX, Version 3.14159265-2.6-1.40.18 (TeX Live 2017/Debian) (preloaded format=pdflatex)
 \write18 enabled.
entering extended mode
(./quickref.tex
LaTeX2e <2017-04-15>
Babel <3.18> and hyphenation patterns for 84 language(s) loaded.
(/usr/share/texlive/texmf-dist/tex/latex/base/article.cls
Document Class: article 2014/09/29 v1.4h Standard LaTeX document class



(/usr/share/texlive/texmf-dist/tex/latex/graphics/color.sty



(/usr/share/texlive/texmf-dist/tex/latex/amsmath/amsmath.sty
For additional information on amsmath, use the `?' option.
(/usr/share/texlive/texmf-dist/tex/latex/amsmath/amstext.sty





(/usr/share/texlive/texmf-dist/tex/latex/xcolor/xcolor.sty

(/usr/share/texlive/texmf-dist/tex/latex/colortbl/colortbl.sty


(/usr/share/texlive/texmf-dist/tex/latex/ltablex/ltablex.sty


(/usr/share/texlive/texmf-dist/tex/latex/microtype/microtype.sty



(/usr/share/texlive/texmf-dist/tex/latex/graphics/graphicx.sty
(/usr/share/texlive/texmf-dist/tex/latex/graphics/graphics.sty



(/usr/share/texlive/texmf-dist/tex/latex/fancyvrb/fancyvrb.sty
Style option: `fancyvrb' v2.7a, with DG/SPQR fixes, and firstline=lastline fix 
<2008/02/07> (tvz)) 
 (/usr/share/texlive/texmf-dist/tex/latex/moreverb/moreverb.sty

(/usr/share/texlive/texmf-dist/tex/latex/base/fontenc.sty

(/usr/share/texlive/texmf-dist/tex/latex/ucs/ucs.sty

(/usr/share/texlive/texmf-dist/tex/latex/base/inputenc.sty



(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hyperref.sty
(/usr/share/texlive/texmf-dist/tex/generic/oberdiek/hobsub-hyperref.sty







(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hpdftex.def


(/X/X/mdframed.sty
(/usr/share/texlive/texmf-dist/tex/latex/l3packages/xparse/xparse.sty
(/usr/share/texlive/texmf-dist/tex/latex/l3kernel/expl3.sty



(/usr/share/texlive/texmf-dist/tex/latex/oberdiek/zref-abspage.sty


(/usr/share/texlive/texmf-dist/tex/latex/pgf/frontendlayer/tikz.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/basiclayer/pgf.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/utilities/pgfrcs.sty
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfutil-common.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfutil-common-lists.t
ex)) (/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfutil-latex.def


(/usr/share/texlive/texmf-dist/tex/latex/pgf/basiclayer/pgfcore.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/systemlayer/pgfsys.sty
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsys.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfkeys.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgfkeysfiltered.code.t
ex)) 
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsys-pdftex.def
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsys-common-pdf.de
f)))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsyssoftpath.code.
tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/systemlayer/pgfsysprotocol.code.
tex))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcore.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmath.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathcalc.code.tex


(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.code.tex
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.basic.code
.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.trigonomet
ric.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.random.cod
e.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.comparison
.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.base.code.
tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.round.code
.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.misc.code.
tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/math/pgfmathfunctions.integerari
thmetics.code.tex)))

(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepoints.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepathconstruct.
code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepathusage.code
.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorescopes.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoregraphicstate.c
ode.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoretransformation
s.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorequick.code.tex
)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreobjects.code.t
ex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepathprocessing
.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorearrows.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreshade.code.tex
)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreimage.code.tex

(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoreexternal.code.
tex))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorelayers.code.te
x)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcoretransparency.c
ode.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/basiclayer/pgfcorepatterns.code.
tex)))
(/usr/share/texlive/texmf-dist/tex/generic/pgf/modules/pgfmoduleshapes.code.tex
) (/usr/share/texlive/texmf-dist/tex/generic/pgf/modules/pgfmoduleplot.code.tex
)
(/usr/share/texlive/texmf-dist/tex/latex/pgf/compatibility/pgfcomp-version-0-65
.sty)
(/usr/share/texlive/texmf-dist/tex/latex/pgf/compatibility/pgfcomp-version-1-18
.sty)) (/usr/share/texlive/texmf-dist/tex/latex/pgf/utilities/pgffor.sty
(/usr/share/texlive/texmf-dist/tex/latex/pgf/utilities/pgfkeys.sty

(/usr/share/texlive/texmf-dist/tex/latex/pgf/math/pgfmath.sty

(/usr/share/texlive/texmf-dist/tex/generic/pgf/utilities/pgffor.code.tex

(/usr/share/texlive/texmf-dist/tex/generic/pgf/frontendlayer/tikz/tikz.code.tex

(/usr/share/texlive/texmf-dist/tex/generic/pgf/libraries/pgflibraryplothandlers
.code.tex)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/modules/pgfmodulematrix.code.tex
)
(/usr/share/texlive/texmf-dist/tex/generic/pgf/frontendlayer/tikz/libraries/tik
zlibrarytopaths.code.tex)))
(/X/X/md-frame-1.mdf))

Writing index file quickref.idx
(/usr/share/texlive/texmf-dist/tex/latex/idxlayout/idxlayout.sty

(/usr/share/texlive/texmf-dist/tex/latex/tocbibind/tocbibind.sty

Package tocbibind Note: Using section or other style headings.

) (/usr/share/texlive/texmf-dist/tex/latex/ms/ragged2e.sty


(/usr/share/texlive/texmf-dist/tex/context/base/mkii/supp-pdf.mkii
[Loading MPS to PDF converter (version 2006.09.02).]
) (/usr/share/texlive/texmf-dist/tex/latex/oberdiek/epstopdf-base.sty



(/usr/share/texlive/texmf-dist/tex/latex/hyperref/nameref.sty

(./quickref.out) (./quickref.out) ABD: EveryShipout initializing macros
ABD: EverySelectfont initializing macros








 (./quickref.toc
 [1{/var/lib/texmf/fonts/map/pdftex/u
pdmap/pdftex.map}] 

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 Note that ab-stracts are rec-og-nized by start-ing with [] or []

[4] [5] [6 <./latex_figs/dizzy_face.png>] [7] [8]
Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 resulting in Some sen-tence with \T1/lmtt/m/n/10 words in verb
atim style\T1/phv/m/n/10 . Multi-line blocks

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 that maps en-vi-ron-ments (\T1/lmtt/m/n/10 xxx\T1/phv/m/n/10 )
 onto valid lan-guage types for Pyg-ments (which

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 ning text. New-com-mands must be de-fined in files with names \T
1/lmtt/m/n/10 newcommands*.tex\T1/phv/m/n/10 .

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 but you can com-bine the files into one file us-ing the []

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 tools for, e.g., com-ment-ing out/in large por-tions of text and
 cre-at-ing macros. 

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 Now we can do [] in the Do-cOnce source

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 The bib-li-og-ra-phy is spec-i-fied by a line \T1/lmtt/m/n/10 
BIBFILE: papers.pub\T1/phv/m/n/10 , where \T1/lmtt/m/n/10 papers.pub

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 (usu-ally af-ter the ti-tle, au-thors, and date). In this case t
he out-put text is \T1/lmtt/m/n/10 internal

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 ment, re-spec-tively. Com-bine with [] and []

Overfull \hbox \(XXXpt too wide\) 
\T1/phv/m/n/10 the GitHub project and ex-am-ine the Do-cOnce source and the \T1
/lmtt/m/n/10 doc/src/make.sh

Overfull \hbox \(XXXpt too wide\) 
[]\T1/phv/m/n/10 Excellent "Sphinx Tu-to-rial" by C. Reller: "http://people.ee.
ethz.ch/ creller/web/tricks/reST.html" 
[25] (./quickref.aux)

 *File List*
 article.cls    2014/09/29 v1.4h Standard LaTeX document class
  size10.clo    2014/09/29 v1.4h Standard LaTeX file (size option)
 relsize.sty    2013/03/29 ver 4.1
 makeidx.sty    2014/09/29 v1.0m Standard LaTeX package
   color.sty    1999/02/16
   color.cfg    2016/01/02 v1.6 sample color configuration
  pdftex.def    2018/01/08 v1.0l Graphics/color driver for pdftex
setspace.sty    2011/12/19 v6.7a set line spacing
 amsmath.sty    2017/09/02 v2.17a AMS math features
 amstext.sty    2000/06/29 v2.01 AMS text
  amsgen.sty    1999/11/30 v2.0 generic functions
  amsbsy.sty    1999/11/29 v1.2d Bold Symbols
  amsopn.sty    2016/03/08 v2.02 operator names
amsfonts.sty    2013/01/14 v3.01 Basic AMSFonts support
 amssymb.sty    2013/01/14 v3.01 AMS font symbols
  xcolor.sty    2016/05/11 v2.12 LaTeX color extensions (UK)
   color.cfg    2016/01/02 v1.6 sample color configuration
colortbl.sty    2012/02/13 v1.0a Color table columns (DPC)
   array.sty    2016/10/06 v2.4d Tabular extension package (FMi)
      bm.sty    2017/01/16 v1.2c Bold Symbol Support (DPC/FMi)
 ltablex.sty    2014/08/13 v1.1 Modified tabularx
longtable.sty    2014/10/28 v4.11 Multi-page Table package (DPC)
tabularx.sty    2016/02/03 v2.11 `tabularx' package (DPC)
microtype.sty    2018/01/14 v2.7a Micro-typographical refinements (RS)
  keyval.sty    2014/10/28 v1.15 key=value parser (DPC)
microtype-pdftex.def    2018/01/14 v2.7a Definitions specific to pdftex (RS)
microtype.cfg    2018/01/14 v2.7a microtype main configuration file (RS)
graphicx.sty    2017/06/01 v1.1a Enhanced LaTeX Graphics (DPC,SPQR)
graphics.sty    2017/06/25 v1.2c Standard LaTeX Graphics (DPC,SPQR)
    trig.sty    2016/01/03 v1.10 sin cos tan (DPC)
graphics.cfg    2016/06/04 v1.11 sample graphics configuration
    soul.sty    2003/11/17 v2.4 letterspacing/underlining (mf)
  framed.sty    2011/10/22 v 0.96: framed or shaded text with page breaks
moreverb.sty    2008/06/03 v2.3a `more' verbatim facilities
verbatim.sty    2014/10/28 v1.5q LaTeX2e package for verbatim enhancements
 fontenc.sty
   t1enc.def    2017/04/05 v2.0i Standard LaTeX file
     ucs.sty    2013/05/11 v2.2 UCS: Unicode input support
uni-global.def    2013/05/13 UCS: Unicode global data
inputenc.sty    2015/03/17 v1.2c Input encoding file
   utf8x.def    2004/10/17 UCS: Input encoding UTF-8
  helvet.sty    2005/04/12 PSNFSS-v9.2a (WaS) 
 lmodern.sty    2009/10/30 v1.6 Latin Modern Fonts
hyperref.sty    2018/02/06 v6.86b Hypertext links for LaTeX
hobsub-hyperref.sty    2016/05/16 v1.14 Bundle oberdiek, subset hyperref (HO)
hobsub-generic.sty    2016/05/16 v1.14 Bundle oberdiek, subset generic (HO)
  hobsub.sty    2016/05/16 v1.14 Construct package bundles (HO)
infwarerr.sty    2016/05/16 v1.4 Providing info/warning/error messages (HO)
 ltxcmds.sty    2016/05/16 v1.23 LaTeX kernel commands for general use (HO)
ifluatex.sty    2016/05/16 v1.4 Provides the ifluatex switch (HO)
  ifvtex.sty    2016/05/16 v1.6 Detect VTeX and its facilities (HO)
 intcalc.sty    2016/05/16 v1.2 Expandable calculations with integers (HO)
   ifpdf.sty    2017/03/15 v3.2 Provides the ifpdf switch
etexcmds.sty    2016/05/16 v1.6 Avoid name clashes with e-TeX commands (HO)
kvsetkeys.sty    2016/05/16 v1.17 Key value parser (HO)
kvdefinekeys.sty    2016/05/16 v1.4 Define keys (HO)
pdftexcmds.sty    2018/01/21 v0.26 Utility functions of pdfTeX for LuaTeX (HO)
pdfescape.sty    2016/05/16 v1.14 Implements pdfTeX's escape features (HO)
bigintcalc.sty    2016/05/16 v1.4 Expandable calculations on big integers (HO)
  bitset.sty    2016/05/16 v1.2 Handle bit-vector datatype (HO)
uniquecounter.sty    2016/05/16 v1.3 Provide unlimited unique counter (HO)
letltxmacro.sty    2016/05/16 v1.5 Let assignment for LaTeX macros (HO)
 hopatch.sty    2016/05/16 v1.3 Wrapper for package hooks (HO)
xcolor-patch.sty    2016/05/16 xcolor patch
atveryend.sty    2016/05/16 v1.9 Hooks at the very end of document (HO)
atbegshi.sty    2016/06/09 v1.18 At begin shipout hook (HO)
refcount.sty    2016/05/16 v3.5 Data extraction from label references (HO)
 hycolor.sty    2016/05/16 v1.8 Color options for hyperref/bookmark (HO)
 ifxetex.sty    2010/09/12 v0.6 Provides ifxetex conditional
 auxhook.sty    2016/05/16 v1.4 Hooks for auxiliary files (HO)
kvoptions.sty    2016/05/16 v3.12 Key value format for package options (HO)
  pd1enc.def    2018/02/06 v6.86b Hyperref: PDFDocEncoding definition (HO)
hyperref.cfg    2002/06/06 v1.2 hyperref configuration of TeXLive
     url.sty    2013/09/16  ver 3.4  Verb mode for urls, etc.
 hpdftex.def    2018/02/06 v6.86b Hyperref driver for pdfTeX
rerunfilecheck.sty    2016/05/16 v1.8 Rerun checks for auxiliary files (HO)
placeins.sty    2005/04/18  v 2.2
mdframed.sty    2014/05/30 2.0: mdframed
  xparse.sty    2018/02/21 L3 Experimental document command parser
   expl3.sty    2018/02/21 L3 programming layer (loader) 
expl3-code.tex    2018/02/21 L3 programming layer 
l3pdfmode.def    2017/03/18 v L3 Experimental driver: PDF mode
etoolbox.sty    2018/02/11 v2.5e e-TeX tools for LaTeX (JAW)
zref-abspage.sty    2016/05/21 v2.26 Module abspage for zref (HO)
zref-base.sty    2016/05/21 v2.26 Module base for zref (HO)
needspace.sty    2010/09/12 v1.3d reserve vertical space
    tikz.sty    2015/08/07 v3.0.1a (rcs-revision 1.151)
     pgf.sty    2015/08/07 v3.0.1a (rcs-revision 1.15)
  pgfrcs.sty    2015/08/07 v3.0.1a (rcs-revision 1.31)
everyshi.sty    2001/05/15 v3.00 EveryShipout Package (MS)
  pgfrcs.code.tex
 pgfcore.sty    2010/04/11 v3.0.1a (rcs-revision 1.7)
  pgfsys.sty    2014/07/09 v3.0.1a (rcs-revision 1.48)
  pgfsys.code.tex
pgfsyssoftpath.code.tex    2013/09/09  (rcs-revision 1.9)
pgfsysprotocol.code.tex    2006/10/16  (rcs-revision 1.4)
 pgfcore.code.tex
pgfcomp-version-0-65.sty    2007/07/03 v3.0.1a (rcs-revision 1.7)
pgfcomp-version-1-18.sty    2007/07/23 v3.0.1a (rcs-revision 1.1)
  pgffor.sty    2013/12/13 v3.0.1a (rcs-revision 1.25)
 pgfkeys.sty    
 pgfkeys.code.tex
 pgfmath.sty    
 pgfmath.code.tex
  pgffor.code.tex
    tikz.code.tex
md-frame-1.mdf    2014/05/30\ 2.0: md-frame-1
    calc.sty    2014/10/28 v4.3 Infix arithmetic (KKT,FJ)
idxlayout.sty    2012/03/30 v0.4d Configurable index layout
multicol.sty    2017/04/11 v1.8q multicolumn formatting (FMi)
tocbibind.sty    2010/10/13 v1.5k extra ToC listings
ragged2e.sty    2009/05/21 v2.1 ragged2e Package (MS)
everysel.sty    2011/10/28 v1.2 EverySelectfont Package (MS)
   t1phv.fd    2001/06/04 scalable font definitions for T1/phv.
supp-pdf.mkii
epstopdf-base.sty    2016/05/15 v2.6 Base part for package epstopdf
  grfext.sty    2016/05/16 v1.2 Manage graphics extensions (HO)
epstopdf-sys.cfg    2010/07/13 v1.3 Configuration of (r)epstopdf for TeX Live
 ucsencs.def    2011/01/21 Fixes to fontencodings LGR, T3
 nameref.sty    2016/05/21 v2.44 Cross-referencing by name of section
gettitlestring.sty    2016/05/16 v1.5 Cleanup title references (HO)
quickref.out
quickref.out
  ot1lmr.fd    2009/10/30 v1.6 Font defs for Latin Modern
  mt-cmr.cfg    2013/05/19 v2.2 microtype config. file: Computer Modern Roman (
RS)
  omllmm.fd    2009/10/30 v1.6 Font defs for Latin Modern
 omslmsy.fd    2009/10/30 v1.6 Font defs for Latin Modern
 omxlmex.fd    2009/10/30 v1.6 Font defs for Latin Modern
    umsa.fd    2013/01/14 v3.01 AMS symbols A
  mt-msa.cfg    2006/02/04 v1.1 microtype config. file: AMS symbols (a) (RS)
    umsb.fd    2013/01/14 v3.01 AMS symbols B
  mt-msb.cfg    2005/06/01 v1.0 microtype config. file: AMS symbols (b) (RS)
  t1lmtt.fd    2009/10/30 v1.6 Font defs for Latin Modern
  omsphv.fd    
latex_figs/dizzy_face.png
 ***********


LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.

 )
(see the transcript file for additional information){/usr/share/texmf/fonts/enc
/dvips/lm/lm-ec.enc}{/usr/share/texmf/fonts/enc/dvips/lm/lm-mathsy.enc}{/usr/sh
are/texmf/fonts/enc/dvips/lm/lm-rm.enc}{/usr/share/texmf/fonts/enc/dvips/lm/lm-
mathit.enc}{/usr/share/texlive/texmf-dist/fonts/enc/dvips/base/8r.enc}</usr/sha
re/texlive/texmf-dist/fonts/type1/public/amsfonts/cm/cmsy10.pfb></usr/share/tex
mf/fonts/type1/public/lm/lmmi10.pfb></usr/share/texmf/fonts/type1/public/lm/lmm
i7.pfb></usr/share/texmf/fonts/type1/public/lm/lmr10.pfb></usr/share/texmf/font
s/type1/public/lm/lmr6.pfb></usr/share/texmf/fonts/type1/public/lm/lmr7.pfb></u
sr/share/texmf/fonts/type1/public/lm/lmsy10.pfb></usr/share/texmf/fonts/type1/p
ublic/lm/lmtk10.pfb></usr/share/texmf/fonts/type1/public/lm/lmtt10.pfb></usr/sh
are/texmf/fonts/type1/public/lm/lmtt8.pfb></usr/share/texmf/fonts/type1/public/
lm/lmtt9.pfb></usr/share/texlive/texmf-dist/fonts/type1/urw/helvetic/uhvb8a.pfb
></usr/share/texlive/texmf-dist/fonts/type1/urw/helvetic/uhvr8a.pfb></usr/share
/texlive/texmf-dist/fonts/type1/urw/helvetic/uhvro8a.pfb>
Output written on quickref.pdf (XXX pages, ).
Transcript written on quickref.log.
+ '[' 0 -ne 0 ']'
+ system doconce format sphinx quickref --no_preprocess --no_abort
+ doconce format sphinx quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to sphinx
copy complete file doconce_program.sh  (format: shpro)
*** warning: sphinx/rst is a suboptimal format for
    typesetting edit markup such as
    [add 2: ,]
    Use HTML or LaTeX output instead, implement the
    edits (doconce apply_edit_comments) and then use sphinx.
output in quickref.rst
+ '[' 0 -ne 0 ']'
+ rm -rf sphinx-rootdir
+ touch conf.py
+ system doconce sphinx_dir theme=cbc quickref dirname=sphinx-rootdir
+ doconce sphinx_dir theme=cbc quickref dirname=sphinx-rootdir
Making sphinx-rootdir
Welcome to the Sphinx 3.3.1 quickstart utility.

Please enter values for the following settings (just press Enter to
accept a default value, if one is given in brackets).

Selected root path: .

Error: an existing conf.py has been found in the selected root path.
sphinx-quickstart will not overwrite existing Sphinx projects.

> Please enter a new root path (or just Enter to exit) []: 
You have two options for placing the build directory for Sphinx output.
Either, you use a directory "_build" within the root path, or you separate
"source" and "build" directories within the root path.
> Separate source and build directories (y/n) [n]: 
The project name will occur in several places in the built documentation.
> Project name: > Author name(s): > Project release []: 
If the documents are to be written in a language other than English,
you can select a language here by its language code. Sphinx will then
translate text that it generates into that language.

For a list of supported codes, see
https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language.
> Project language [en]: 
Creating file /X/X/sphinx-rootdir/conf.py.
Creating file /X/X/sphinx-rootdir/index.rst.
Creating file /X/X/sphinx-rootdir/Makefile.
Creating file /X/X/sphinx-rootdir/make.bat.

Finished: An initial directory structure has been created.

You should now populate your master file /X/X/sphinx-rootdir/index.rst and create other documentation
source files. Use the Makefile to build the docs, like so:
   make builder
where "builder" is one of the supported builders, e.g. html, latex or linkcheck.

title: DocOnce Quick Reference
author: Hans Petter Langtangen, H. P. Langtangen, Kaare Dump and A. Dummy Author
copyright: 2XXX, Hans Petter Langtangen, H. P. Langtangen, Kaare Dump and A. Dummy Author
theme: cbc

These Sphinx themes were found: ADCtheme, agni, agogo, alabaster, basic, basicstrap, bizstyle, bloodish, bootstrap, cbc, classic, cloud, default, epub, fenics, fenics_classic, fenics_minimal1, fenics_minimal2, haiku, jal, nature, pylons, pyramid, redcloud, scipy_lectures, scrolls, slim-agogo, solarized, sphinx_rtd_theme, sphinxdoc, traditional, uio, uio2, vlinux-theme
'automake_sphinx.py' contains the steps to (re)compile the sphinx
version. You may want to edit this file, or run the steps manually,
or just run it by

  python automake_sphinx.py

+ '[' 0 -ne 0 ']'
+ doconce replace 'doconce format sphinx %s' 'doconce format sphinx %s --no-preprocess' automake_sphinx.py
replacing doconce format sphinx %s by doconce format sphinx %s --no-preprocess in automake_sphinx.py
+ system python automake_sphinx.py
+ python automake_sphinx.py
Removing everything under '_build'...
Running Sphinx v3.3.1
loading translations [1.0]... not available for built-in messages
making output directory... done
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 2 source files that are out of date
updating environment: [new config] 2 added, 0 changed, 0 removed
reading sources... [ 50%] index
reading sources... [100%] quickref

looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [ 50%] index
writing output... [100%] quickref

generating indices... genindex done
writing additional pages... search done
copying static files... done
copying extra files... done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded.

The HTML pages are in _build/html.
/X/X/sphinx-rootdir
running make clean
running make html
Fix generated files:
genindex.html
index.html
quickref.html
search.html


google-chrome sphinx-rootdir/_build/html/index.html

+ '[' 0 -ne 0 ']'
+ cp quickref.rst quickref.sphinx.rst
+ system doconce format rst quickref --no_preprocess --no_abort
+ doconce format rst quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to rst
copy complete file doconce_program.sh  (format: shpro)
output in quickref.rst
+ '[' 0 -ne 0 ']'
+ rst2xml.py quickref.rst
+ rst2odt.py quickref.rst
+ rst2html.py quickref.rst
+ rst2latex.py quickref.rst
+ system latex quickref.rst.tex
+ latex quickref.rst.tex
This is pdfTeX, Version 3.14159265-2.6-1.40.18 (TeX Live 2017/Debian) (preloaded format=latex)
 restricted \write18 enabled.
entering extended mode
(./quickref.rst.tex
LaTeX2e <2017-04-15>
Babel <3.18> and hyphenation patterns for 84 language(s) loaded.
(/usr/share/texlive/texmf-dist/tex/latex/base/article.cls
Document Class: article 2014/09/29 v1.4h Standard LaTeX document class

(/usr/share/texlive/texmf-dist/tex/latex/cmap/cmap.sty

Package cmap Warning: pdftex in DVI mode - exiting.

) 
(/usr/share/texlive/texmf-dist/tex/latex/base/fontenc.sty

(/usr/share/texlive/texmf-dist/tex/latex/base/inputenc.sty
(/usr/share/texlive/texmf-dist/tex/latex/base/utf8.def









(/usr/share/texlive/texmf-dist/tex/latex/psnfss/helvet.sty


(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hyperref.sty
(/usr/share/texlive/texmf-dist/tex/generic/oberdiek/hobsub-hyperref.sty







(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hdvips.def
(/usr/share/texlive/texmf-dist/tex/latex/hyperref/pdfmark.def

(/usr/share/texlive/texmf-dist/tex/latex/oberdiek/bookmark.sty

No file quickref.rst.aux.

(/usr/share/texlive/texmf-dist/tex/latex/graphics/color.sty



(/usr/share/texlive/texmf-dist/tex/latex/hyperref/nameref.sty


Package hyperref Warning: Rerun to get /PageLabels entry.







Package hyperref Warning: old toc file detected, not used; run LaTeX again.


Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 HTML. Other out-lets in-clude Google's \T1/pcr/m/n/10 blogger.co
m\T1/ptm/m/n/10 , Wikipedia/Wikibooks, IPython/Jupyter

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 AUTHOR: H. P. Langtangen at Center for Biomedical Computing, 
Simula Research Laboratory & Dept. of Informatics, Univ. of Oslo[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 AUTHOR: Kaare Dump Email: dump@cyb.space.com at Segfault, Cyb
erspace Inc.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 name Email: somename@adr.net at institution1 & institution2[]

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 AUTHOR: name Email: somename@adr.net {copyright,2006-present}
 at inst1[] 

Underfull \hbox (badness 10000) 
[]|\T1/pcr/m/n/10 ======= Appendix: heading

Underfull \hbox (badness 1168) 
[]|\T1/pcr/m/n/10 ===== Appendix: heading ===== \T1/ptm/m/n/10 (5

Underfull \hbox (badness 1168) 
[]|\T1/pcr/m/n/10 ===== Exercise: heading ===== \T1/ptm/m/n/10 (5

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 Note that ab-stracts are rec-og-nized by start-ing with \T1/pcr/
m/n/10 __Abstract.__ \T1/ptm/m/n/10 or \T1/pcr/m/n/10 __Summary.__

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/it/10 sized words\T1/ptm/m/n/10 . Sim-i-larly, an un-der-score sur-ro
unds words that ap-pear in bold-face: \T1/pcr/m/n/10 _boldface_

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 This distance corresponds to 7.5~km, which is traveled in $7.
5/5$~s.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 The em-dash is used - without spaces - as alternative to hyph
en with[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 *Premature optimization is the root of all evil.*--- Donald K
nuth.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Note that sublists are consistently indented by one or more b
lanks as[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 shown: bullets must exactly match and continuation lines must
 start[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Some running text. [hpl: There must be a space after the colo
n,[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce format html mydoc.do.txt --skip_inline_comments[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 First consider a quantity $Q$. Without loss of generality, we
 assume[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 $Q>0$. There are three, fundamental, basic property of $Q$.[]
 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 we assume] $Q>0$. There are three[del: ,] fundamental[del: , 
basic][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 [edit: property -> properties] of $Q$. [add: These are not[] 


Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 three-color{red}{(\T1/ptm/b/n/10 del 5\T1/ptm/m/n/10 : ,}) fun-d
a-men-tal-color{red}{(\T1/ptm/b/n/10 del 6\T1/ptm/m/n/10 : , ba-sic}) \T1/ptm/b
/n/10 (**edit

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # sphinx code-blocks: pycod=python cod=fortran cppcod=c++ sys
=console[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 @@@CODE doconce_program.sh  fromto: doconce clean@^doconce sp
lit_rst[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 @@@CODE doconce_program.sh  from-to: doconce clean@^doconce s
plit_rst[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 @@@CODE doconce_program.sh  envir=shpro fromto: name=@[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 \[ \frac{\partial\pmb{u}}{\partial t} + \pmb{u}\cdot\nabla\pm
b{u} = 0.\][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 \[ \frac{\partial\pmb{u}}{\partial t} + \pmb{u}\cdot\nabla\pm
b{u} = 0.\][] 

Overfull \hbox \(XXXpt too wide\) 
[]\T1/ptm/m/n/10 If you want La-TeX math blocks to work with \T1/pcr/m/n/10 lat
ex\T1/ptm/m/n/10 , \T1/pcr/m/n/10 html\T1/ptm/m/n/10 , \T1/pcr/m/n/10 sphinx\T1
/ptm/m/n/10 ,

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 ments: \T1/pcr/m/n/10 \[ ... \]\T1/ptm/m/n/10 , \T1/pcr/m/n/10 e
quation*\T1/ptm/m/n/10 , \T1/pcr/m/n/10 equation\T1/ptm/m/n/10 , \T1/pcr/m/n/10
 align*\T1/ptm/m/n/10 , \T1/pcr/m/n/10 align\T1/ptm/m/n/10 .

Overfull \hbox \(XXXpt too wide\) 
\T1/pcr/m/n/10 alignat*\T1/ptm/m/n/10 , \T1/pcr/m/n/10 alignat\T1/ptm/m/n/10 . 
Other en-vi-ron-ments, such as \T1/pcr/m/n/10 split\T1/ptm/m/n/10 , \T1/pcr/m/n
/10 multiline\T1/ptm/m/n/10 ,

Overfull \hbox \(XXXpt too wide\) 
\T1/pcr/m/n/10 newcommands*.tex\T1/ptm/m/n/10 . Use \T1/pcr/m/n/10 \newcommands
 \T1/ptm/m/n/10 and not \T1/pcr/m/n/10 \def\T1/ptm/m/n/10 . Each

Package hyperref Warning: Ignoring empty anchor on .

Overfull \hbox \(XXXpt too wide\) 
[]  \T1/pcr/m/n/10 \includegraphics[width=0.55\linewidth]{figs/myfig.pdf}  

Overfull \hbox \(XXXpt too wide\) 
[]\T1/pcr/m/n/10 \multicolumn{1}{c}{$v_0$} & \multicolumn{1}{c}{$f_R(v_0)$}\\hl
ine  

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Here is some "some link text": "http://some.net/address"[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Links to files typeset in verbatim mode applies backtics:[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 "`myfile.py`": "http://some.net/some/place/myfile.py".[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 FIGURE: [relative/path/to/figurefile, width=500 frac=0.8] Her
e goes the caption which must be on a single line. label{some:fig:label}[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 MOVIE: [relative/path/to/moviefile, width=500] Here goes the 
caption which must be on a single line.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 MOVIE: [http://www.youtube.com/watch?v=_O7iUiftbKU, width=420
 height=315] YouTube movie.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 MOVIE: [http://vimeo.com/55562330, width=500 height=278] Vime
o movie.[] 


ne 1371.

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |----------------c--------|------------------c---------------
-----|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |      Section type       |        Syntax                    
     |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |----------------l--------|------------------l---------------
-----|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | chapter                 | `========= Heading ========` (9 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | section                 | `======= Heading =======`    (7 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | subsection              | `===== Heading =====`        (5 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | subsubsection           | `=== Heading ===`            (3 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | paragraph               | `__Heading.__`               (2 `
_`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |------------------------------------------------------------
-----|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Terminal> doconce csv2table mydata.csv > mydata_table.do.txt[
] 

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 sert a back-slash). Bib-li-og-ra-phy ci-ta-tions of-ten have \T1
/pcr/m/n/10 name \T1/ptm/m/n/10 on the form \T1/pcr/m/n/10 Author1_Author2_YYYY
\T1/ptm/m/n/10 ,

Overfull \hbox \(XXXpt too wide\) 
[]\T1/ptm/m/n/10 The bib-li-og-ra-phy is spec-i-fied by a line \T1/pcr/m/n/10 B
IBFILE: papers.pub\T1/ptm/m/n/10 , where \T1/pcr/m/n/10 papers.pub

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ref[Section ref{subsec:ex}][in cite{testdoc:12}][a "section":

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 "A Document for Testing DocOnce": "testdoc.html" cite{testdoc
:12}],[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 DocOnce version 1.5.7 (from /X/X/pyt
hon3.6/site-packages/DocOnce-1.5.7-py3.6.egg/doconce)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 commands: help format find subst replace remove spellcheck ap
ply_inline_edits capitalize change_encoding clean combine_images csv2table diff
 expand_commands expand_mako extract_exercises find_nonascii_chars fix_bibtex4p
ublish gitdiff grab grep guess_encoding gwiki_figsubst html2doconce html_colorb
ullets jupyterbook include_map insertdocstr ipynb2doconce latex2doconce latex_d
islikes latex_exercise_toc latex_footer latex_header latex_problems latin2html 
lightclean linkchecker list_fig_src_files list_labels makefile md2html md2latex
 old2new_format ptex2tex pygmentize ref_external remove_exercise_answers remove
_inline_comments replace_from_file slides_beamer slides_html slides_markdown sp
hinx_dir sphinxfix_localURLs split_html split_rst teamod[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce format html|latex|pdflatex|rst|sphinx|plain|gwiki|mwi
ki|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # substitute a phrase by another using regular expressions (i
n this example -s is the re.DOTALL modifier, -m is the re.MULTILINE modifier, -
x is the re.VERBOSE modifier, --restore copies backup files back again)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # replace a phrase by another literally (exact text substitut
ion)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce replace_from_file file-with-from-to-replacements file
1 file2 ...[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # search for a (regular) expression in all .do.txt files in t
he current directory tree (useful when removing compilation errors)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # print an overview of how various files are included in the 
root doc[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce expand_mako mako_code_file funcname file1 file2 ...[]
 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # replace all mako function calls by the `results of the call
s[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce sphinx_dir copyright='John Doe' title='Long title' \[
] 

Overfull \hbox \(XXXpt too wide\) 
 []        \T1/pcr/m/n/10 short_title="Short title" version=0.1 intersphinx \[]
 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # create a directory for the sphinx format (requires sphinx v
ersion >= 1.1)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # split a sphinx/rst file into parts according to !split comm
ands[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # walk through a directory tree and insert doconce files as d
ocstrings in *.p.py files[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # remove all redundant files (keep source .do.txt and results
: .pdf, .html, sphinx- dirs, .mwiki, .ipynb, etc.)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # split an html file into parts according to !split commands[
] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # create LaTeX Beamer slides from a (doconce) latex/pdflatex 
file[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce slides_markdown complete_file.md remark --slide_style
=light[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce grab --from[-] from-text [--to[-] to-text] file > res
ult[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce remove --from[-] from-text [--to[-] to-text] file > r
esult[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce ptex2tex mydoc -DMINTED pycod=minted sys=Verbatim \[]
 

Overfull \hbox \(XXXpt too wide\) 
 []        \T1/pcr/m/n/10 dat=\begin{quote}\begin{verbatim};\end{verbatim}\end{
quote}[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # transform ptex2tex files (.p.tex) to ordinary latex file an
d manage the code environments[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce latex_problems mydoc.log [overfull-hbox-limit][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # list all figure files, movie files, and source code files n
eeded[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # list all labels in a document (for purposes of cleaning the
m up)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # generate script for substituting generalized references[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # change headings from "This is a Heading" to "This is a head
ing"[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # translate a latex document to doconce (requires usually man
ual fixing)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # check if there are problems with translating latex to docon
ce[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # typeset a doconce document with pygments (for pretty print 
of doconce itself)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce makefile docname doconcefile [html sphinx pdflatex ..
.][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # generate a make.py script for translating a doconce file to
 various formats[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # find differences between two files (diffprog can be difflib
, diff, pdiff, latexdiff, kdiff3, diffuse, ...)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # find differences between the last two Git versions of sever
al files[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # replace latex-1 (non-ascii) characters by html codes[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # fix common problems in bibtex files for publish import[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # insert a table of exercises in a latex file myfile.p.tex[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ===== Problem: Derive the Formula for the Area of an Ellipse 
=====[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Derive an expression for the area of an ellipse by integratin
g[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 the area under a curve that defines half of the ellipse.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ===== {Problem}: Derive the Formula for the Area of an Ellips
e =====[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ===== Exercise: Determine the Distance to the Moon =====[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Intro to this exercise. Questions are in subexercises below.[
] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 At the very end of the exercise it may be appropriate to summ
arize[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 and give some perspectives. The text inside the `!bremarks` a
nd `!eremarks`[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 directives is always typeset at the end of the exercise.[] 

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 DocOnce en-vi-ron-ments start with \T1/pcr/m/n/10 !benvirname \T
1/ptm/m/n/10 and end with \T1/pcr/m/n/10 !eenvirname\T1/ptm/m/n/10 , where

Overfull \hbox \(XXXpt too wide\) 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 \multicolumn{1}{c}{time} & \multicolumn{1}{c}{velocity} & \mu
lticolumn{1}{c}{acceleration} \\[] 

Overfull \hbox \(XXXpt too wide\) 
[][][][][][] \T1/ptm/m/n/10 con-tains some il-lus-tra-tions on how to uti-lize 
\T1/pcr/m/n/10 mako \T1/ptm/m/n/10 (clone the GitHub

Overfull \hbox \(XXXpt too wide\) 
[]\T1/ptm/m/n/10 Excellent "Sphinx Tu-to-rial" by C. Reller: "[][][][][][]" 
[25] (./quickref.rst.aux)

LaTeX Warning: There were undefined references.


LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.

 )
(see the transcript file for additional information)
Output written on quickref.rst.dvi (XXX pages, ).
Transcript written on quickref.rst.log.
+ '[' 0 -ne 0 ']'
+ latex quickref.rst.tex
This is pdfTeX, Version 3.14159265-2.6-1.40.18 (TeX Live 2017/Debian) (preloaded format=latex)
 restricted \write18 enabled.
entering extended mode
(./quickref.rst.tex
LaTeX2e <2017-04-15>
Babel <3.18> and hyphenation patterns for 84 language(s) loaded.
(/usr/share/texlive/texmf-dist/tex/latex/base/article.cls
Document Class: article 2014/09/29 v1.4h Standard LaTeX document class

(/usr/share/texlive/texmf-dist/tex/latex/cmap/cmap.sty

Package cmap Warning: pdftex in DVI mode - exiting.

) 
(/usr/share/texlive/texmf-dist/tex/latex/base/fontenc.sty

(/usr/share/texlive/texmf-dist/tex/latex/base/inputenc.sty
(/usr/share/texlive/texmf-dist/tex/latex/base/utf8.def









(/usr/share/texlive/texmf-dist/tex/latex/psnfss/helvet.sty


(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hyperref.sty
(/usr/share/texlive/texmf-dist/tex/generic/oberdiek/hobsub-hyperref.sty







(/usr/share/texlive/texmf-dist/tex/latex/hyperref/hdvips.def
(/usr/share/texlive/texmf-dist/tex/latex/hyperref/pdfmark.def

(/usr/share/texlive/texmf-dist/tex/latex/oberdiek/bookmark.sty

(./quickref.rst.aux) 
(/usr/share/texlive/texmf-dist/tex/latex/graphics/color.sty



(/usr/share/texlive/texmf-dist/tex/latex/hyperref/nameref.sty





 (./quickref.rst.toc

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 HTML. Other out-lets in-clude Google's \T1/pcr/m/n/10 blogger.co
m\T1/ptm/m/n/10 , Wikipedia/Wikibooks, IPython/Jupyter

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 AUTHOR: H. P. Langtangen at Center for Biomedical Computing, 
Simula Research Laboratory & Dept. of Informatics, Univ. of Oslo[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 AUTHOR: Kaare Dump Email: dump@cyb.space.com at Segfault, Cyb
erspace Inc.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 name Email: somename@adr.net at institution1 & institution2[]

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 AUTHOR: name Email: somename@adr.net {copyright,2006-present}
 at inst1[] 

Underfull \hbox (badness 10000) 
[]|\T1/pcr/m/n/10 ======= Appendix: heading

Underfull \hbox (badness 1168) 
[]|\T1/pcr/m/n/10 ===== Appendix: heading ===== \T1/ptm/m/n/10 (5

Underfull \hbox (badness 1168) 
[]|\T1/pcr/m/n/10 ===== Exercise: heading ===== \T1/ptm/m/n/10 (5

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 Note that ab-stracts are rec-og-nized by start-ing with \T1/pcr/
m/n/10 __Abstract.__ \T1/ptm/m/n/10 or \T1/pcr/m/n/10 __Summary.__

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/it/10 sized words\T1/ptm/m/n/10 . Sim-i-larly, an un-der-score sur-ro
unds words that ap-pear in bold-face: \T1/pcr/m/n/10 _boldface_

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 This distance corresponds to 7.5~km, which is traveled in $7.
5/5$~s.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 The em-dash is used - without spaces - as alternative to hyph
en with[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 *Premature optimization is the root of all evil.*--- Donald K
nuth.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Note that sublists are consistently indented by one or more b
lanks as[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 shown: bullets must exactly match and continuation lines must
 start[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Some running text. [hpl: There must be a space after the colo
n,[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce format html mydoc.do.txt --skip_inline_comments[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 First consider a quantity $Q$. Without loss of generality, we
 assume[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 $Q>0$. There are three, fundamental, basic property of $Q$.[]
 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 we assume] $Q>0$. There are three[del: ,] fundamental[del: , 
basic][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 [edit: property -> properties] of $Q$. [add: These are not[] 


Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 three-color{red}{(\T1/ptm/b/n/10 del 5\T1/ptm/m/n/10 : ,}) fun-d
a-men-tal-color{red}{(\T1/ptm/b/n/10 del 6\T1/ptm/m/n/10 : , ba-sic}) \T1/ptm/b
/n/10 (**edit

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # sphinx code-blocks: pycod=python cod=fortran cppcod=c++ sys
=console[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 @@@CODE doconce_program.sh  fromto: doconce clean@^doconce sp
lit_rst[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 @@@CODE doconce_program.sh  from-to: doconce clean@^doconce s
plit_rst[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 @@@CODE doconce_program.sh  envir=shpro fromto: name=@[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 \[ \frac{\partial\pmb{u}}{\partial t} + \pmb{u}\cdot\nabla\pm
b{u} = 0.\][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 \[ \frac{\partial\pmb{u}}{\partial t} + \pmb{u}\cdot\nabla\pm
b{u} = 0.\][] 

Overfull \hbox \(XXXpt too wide\) 
[]\T1/ptm/m/n/10 If you want La-TeX math blocks to work with \T1/pcr/m/n/10 lat
ex\T1/ptm/m/n/10 , \T1/pcr/m/n/10 html\T1/ptm/m/n/10 , \T1/pcr/m/n/10 sphinx\T1
/ptm/m/n/10 ,

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 ments: \T1/pcr/m/n/10 \[ ... \]\T1/ptm/m/n/10 , \T1/pcr/m/n/10 e
quation*\T1/ptm/m/n/10 , \T1/pcr/m/n/10 equation\T1/ptm/m/n/10 , \T1/pcr/m/n/10
 align*\T1/ptm/m/n/10 , \T1/pcr/m/n/10 align\T1/ptm/m/n/10 .

Overfull \hbox \(XXXpt too wide\) 
\T1/pcr/m/n/10 alignat*\T1/ptm/m/n/10 , \T1/pcr/m/n/10 alignat\T1/ptm/m/n/10 . 
Other en-vi-ron-ments, such as \T1/pcr/m/n/10 split\T1/ptm/m/n/10 , \T1/pcr/m/n
/10 multiline\T1/ptm/m/n/10 ,

Overfull \hbox \(XXXpt too wide\) 
\T1/pcr/m/n/10 newcommands*.tex\T1/ptm/m/n/10 . Use \T1/pcr/m/n/10 \newcommands
 \T1/ptm/m/n/10 and not \T1/pcr/m/n/10 \def\T1/ptm/m/n/10 . Each

Package hyperref Warning: Ignoring empty anchor on .

Overfull \hbox \(XXXpt too wide\) 
[]  \T1/pcr/m/n/10 \includegraphics[width=0.55\linewidth]{figs/myfig.pdf}  

Overfull \hbox \(XXXpt too wide\) 
[]\T1/pcr/m/n/10 \multicolumn{1}{c}{$v_0$} & \multicolumn{1}{c}{$f_R(v_0)$}\\hl
ine  

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Here is some "some link text": "http://some.net/address"[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Links to files typeset in verbatim mode applies backtics:[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 "`myfile.py`": "http://some.net/some/place/myfile.py".[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 FIGURE: [relative/path/to/figurefile, width=500 frac=0.8] Her
e goes the caption which must be on a single line. label{some:fig:label}[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 MOVIE: [relative/path/to/moviefile, width=500] Here goes the 
caption which must be on a single line.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 MOVIE: [http://www.youtube.com/watch?v=_O7iUiftbKU, width=420
 height=315] YouTube movie.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 MOVIE: [http://vimeo.com/55562330, width=500 height=278] Vime
o movie.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |----------------c--------|------------------c---------------
-----|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |      Section type       |        Syntax                    
     |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |----------------l--------|------------------l---------------
-----|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | chapter                 | `========= Heading ========` (9 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | section                 | `======= Heading =======`    (7 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | subsection              | `===== Heading =====`        (5 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | subsubsection           | `=== Heading ===`            (3 `
=`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 | paragraph               | `__Heading.__`               (2 `
_`)  |[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 |------------------------------------------------------------
-----|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Terminal> doconce csv2table mydata.csv > mydata_table.do.txt[
] 

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 sert a back-slash). Bib-li-og-ra-phy ci-ta-tions of-ten have \T1
/pcr/m/n/10 name \T1/ptm/m/n/10 on the form \T1/pcr/m/n/10 Author1_Author2_YYYY
\T1/ptm/m/n/10 ,

Overfull \hbox \(XXXpt too wide\) 
[]\T1/ptm/m/n/10 The bib-li-og-ra-phy is spec-i-fied by a line \T1/pcr/m/n/10 B
IBFILE: papers.pub\T1/ptm/m/n/10 , where \T1/pcr/m/n/10 papers.pub

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ref[Section ref{subsec:ex}][in cite{testdoc:12}][a "section":

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 "A Document for Testing DocOnce": "testdoc.html" cite{testdoc
:12}],[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 DocOnce version 1.5.7 (from /X/X/pyt
hon3.6/site-packages/DocOnce-1.5.7-py3.6.egg/doconce)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 commands: help format find subst replace remove spellcheck ap
ply_inline_edits capitalize change_encoding clean combine_images csv2table diff
 expand_commands expand_mako extract_exercises find_nonascii_chars fix_bibtex4p
ublish gitdiff grab grep guess_encoding gwiki_figsubst html2doconce html_colorb
ullets jupyterbook include_map insertdocstr ipynb2doconce latex2doconce latex_d
islikes latex_exercise_toc latex_footer latex_header latex_problems latin2html 
lightclean linkchecker list_fig_src_files list_labels makefile md2html md2latex
 old2new_format ptex2tex pygmentize ref_external remove_exercise_answers remove
_inline_comments replace_from_file slides_beamer slides_html slides_markdown sp
hinx_dir sphinxfix_localURLs split_html split_rst teamod[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce format html|latex|pdflatex|rst|sphinx|plain|gwiki|mwi
ki|[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # substitute a phrase by another using regular expressions (i
n this example -s is the re.DOTALL modifier, -m is the re.MULTILINE modifier, -
x is the re.VERBOSE modifier, --restore copies backup files back again)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # replace a phrase by another literally (exact text substitut
ion)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce replace_from_file file-with-from-to-replacements file
1 file2 ...[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # search for a (regular) expression in all .do.txt files in t
he current directory tree (useful when removing compilation errors)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # print an overview of how various files are included in the 
root doc[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce expand_mako mako_code_file funcname file1 file2 ...[]
 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # replace all mako function calls by the `results of the call
s[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce sphinx_dir copyright='John Doe' title='Long title' \[
] 

Overfull \hbox \(XXXpt too wide\) 
 []        \T1/pcr/m/n/10 short_title="Short title" version=0.1 intersphinx \[]
 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # create a directory for the sphinx format (requires sphinx v
ersion >= 1.1)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # split a sphinx/rst file into parts according to !split comm
ands[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # walk through a directory tree and insert doconce files as d
ocstrings in *.p.py files[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # remove all redundant files (keep source .do.txt and results
: .pdf, .html, sphinx- dirs, .mwiki, .ipynb, etc.)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # split an html file into parts according to !split commands[
] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # create LaTeX Beamer slides from a (doconce) latex/pdflatex 
file[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce slides_markdown complete_file.md remark --slide_style
=light[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce grab --from[-] from-text [--to[-] to-text] file > res
ult[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce remove --from[-] from-text [--to[-] to-text] file > r
esult[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce ptex2tex mydoc -DMINTED pycod=minted sys=Verbatim \[]
 

Overfull \hbox \(XXXpt too wide\) 
 []        \T1/pcr/m/n/10 dat=\begin{quote}\begin{verbatim};\end{verbatim}\end{
quote}[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # transform ptex2tex files (.p.tex) to ordinary latex file an
d manage the code environments[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce latex_problems mydoc.log [overfull-hbox-limit][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # list all figure files, movie files, and source code files n
eeded[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # list all labels in a document (for purposes of cleaning the
m up)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # generate script for substituting generalized references[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # change headings from "This is a Heading" to "This is a head
ing"[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # translate a latex document to doconce (requires usually man
ual fixing)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # check if there are problems with translating latex to docon
ce[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # typeset a doconce document with pygments (for pretty print 
of doconce itself)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 doconce makefile docname doconcefile [html sphinx pdflatex ..
.][] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # generate a make.py script for translating a doconce file to
 various formats[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # find differences between two files (diffprog can be difflib
, diff, pdiff, latexdiff, kdiff3, diffuse, ...)[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # find differences between the last two Git versions of sever
al files[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # replace latex-1 (non-ascii) characters by html codes[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # fix common problems in bibtex files for publish import[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 # insert a table of exercises in a latex file myfile.p.tex[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ===== Problem: Derive the Formula for the Area of an Ellipse 
=====[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Derive an expression for the area of an ellipse by integratin
g[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 the area under a curve that defines half of the ellipse.[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ===== {Problem}: Derive the Formula for the Area of an Ellips
e =====[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 ===== Exercise: Determine the Distance to the Moon =====[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 Intro to this exercise. Questions are in subexercises below.[
] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 At the very end of the exercise it may be appropriate to summ
arize[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 and give some perspectives. The text inside the `!bremarks` a
nd `!eremarks`[] 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 directives is always typeset at the end of the exercise.[] 

Overfull \hbox \(XXXpt too wide\) 
\T1/ptm/m/n/10 DocOnce en-vi-ron-ments start with \T1/pcr/m/n/10 !benvirname \T
1/ptm/m/n/10 and end with \T1/pcr/m/n/10 !eenvirname\T1/ptm/m/n/10 , where

Overfull \hbox \(XXXpt too wide\) 

Overfull \hbox \(XXXpt too wide\) 
 []\T1/pcr/m/n/10 \multicolumn{1}{c}{time} & \multicolumn{1}{c}{velocity} & \mu
lticolumn{1}{c}{acceleration} \\[] 

Overfull \hbox \(XXXpt too wide\) 
[][][][][][] \T1/ptm/m/n/10 con-tains some il-lus-tra-tions on how to uti-lize 
\T1/pcr/m/n/10 mako \T1/ptm/m/n/10 (clone the GitHub

Overfull \hbox \(XXXpt too wide\) 
[]\T1/ptm/m/n/10 Excellent "Sphinx Tu-to-rial" by C. Reller: "[][][][][][]" 
[26] (./quickref.rst.aux)

LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.

 )
(see the transcript file for additional information)
Output written on quickref.rst.dvi (XXX pages, ).
Transcript written on quickref.rst.log.
+ dvipdf quickref.rst.dvi
+ system doconce format plain quickref --no_preprocess --no_abort
+ doconce format plain quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to plain
copy complete file doconce_program.sh  (format: shpro)
*** made link to new HTML file movie_player1.html
    with code to display the movie 
    http://vimeo.com/55562330
output in quickref.txt
+ '[' 0 -ne 0 ']'
+ system doconce format gwiki quickref --no_preprocess --no_abort
+ doconce format gwiki quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to gwiki
copy complete file doconce_program.sh  (format: shpro)
*** warning: footnotes are not supported for format gwiki
    footnotes will be left in the doconce syntax
*** made link to new HTML file movie_player1.html
    with code to display the movie 
    http://vimeo.com/55562330
output in quickref.gwiki
+ '[' 0 -ne 0 ']'
+ system doconce format mwiki quickref --no_preprocess --no_abort
+ doconce format mwiki quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to mwiki
copy complete file doconce_program.sh  (format: shpro)
*** warning: footnotes are not supported for format mwiki
    footnotes will be left in the doconce syntax
*** made link to new HTML file movie_player1.html
    with code to display the movie 
    http://vimeo.com/55562330
output in quickref.mwiki
+ '[' 0 -ne 0 ']'
+ system doconce format cwiki quickref --no_preprocess --no_abort
+ doconce format cwiki quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to cwiki
copy complete file doconce_program.sh  (format: shpro)
*** warning: footnotes are not supported for format cwiki
    footnotes will be left in the doconce syntax
*** made link to new HTML file movie_player1.html
    with code to display the movie 
    http://vimeo.com/55562330
output in quickref.cwiki
+ '[' 0 -ne 0 ']'
+ system doconce format st quickref --no_preprocess --no_abort
+ doconce format st quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to st
copy complete file doconce_program.sh  (format: shpro)
*** warning: footnotes are not supported for format st
    footnotes will be left in the doconce syntax
*** made link to new HTML file movie_player1.html
    with code to display the movie 
    http://vimeo.com/55562330
output in quickref.st
+ '[' 0 -ne 0 ']'
+ system doconce format epytext quickref --no_preprocess --no_abort
+ doconce format epytext quickref --no_preprocess --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to epytext
copy complete file doconce_program.sh  (format: shpro)
*** warning: footnotes are not supported for format epytext
    footnotes will be left in the doconce syntax
*** made link to new HTML file movie_player1.html
    with code to display the movie 
    http://vimeo.com/55562330
output in quickref.epytext
+ '[' 0 -ne 0 ']'
+ system doconce format pandoc quickref --no_preprocess --strict_markdown_output --github_md --no_abort
+ doconce format pandoc quickref --no_preprocess --strict_markdown_output --github_md --no_abort
running mako on quickref.do.txt to make tmp_mako__quickref.do.txt
Translating doconce text in tmp_mako__quickref.do.txt to pandoc
copy complete file doconce_program.sh  (format: shpro)
*** warning: footnotes are not supported for format pandoc
    footnotes will be left in the doconce syntax
output in quickref.md
+ '[' 0 -ne 0 ']'
+ rm -rf demo
+ mkdir demo
+ cp -r quickref.do.txt quickref.html quickref.p.tex quickref.tex quickref.pdf quickref.rst quickref.xml quickref.rst.html quickref.rst.tex quickref.rst.pdf quickref.gwiki quickref.mwiki quickref.cwiki quickref.txt quickref.epytext quickref.st quickref.md sphinx-rootdir/_build/html demo
cp: cannot stat 'quickref.p.tex': No such file or directory
+ cd demo
+ cat
+ echo

+ echo 'Go to the demo directory /X/X/demo and load index.html into a web browser.'
Go to the demo directory /X/X/demo and load index.html into a web browser.
+ cd ..
+ dest=../../pub/quickref
+ cp -r demo/html demo/quickref.pdf demo/quickref.html ../../pub/quickref
+ dest=../../../../doconce.wiki
+ cp -r demo/quickref.md ../../../../doconce.wiki