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

# Make latest bin/doconce doc. The next commands will print this output to quickref.html and quickref.tex
# Use sed to replace terminal colors (four special characters per line) or pdflatex will halt
doconce > doconce_program.sh
sed -i 's/^\x1b\[[0-9;]*m//' doconce_program.sh
sed -i 's/\x1b\[[0-9;]*m//' doconce_program.sh
sed -i 's/\x1b\[[0-9;]*m\s*/\n# /' doconce_program.sh
sed -i 's/\x1b\[[0-9;]*m//g' doconce_program.sh

system doconce format html quickref --pygments_html_style=none --no_preprocess --no_abort --html_style=bootswatch_readable

# This document has error message from multiple labels: some:fig:label
# (because the document is a doconce instruction!)

# pdflatex
system doconce format pdflatex quickref --no_preprocess --latex_font=helvetica --no_ampersand_quote --latex_code_style=vrb --no_abort

# Since we have native latex table and --no_ampersand_quote, we need to
# manually fix the quote examples elsewhere
doconce subst '([^`])Guns & Roses([^`])' '\g<1>Guns {\&} Roses\g<2>' quickref.tex
doconce subst '([^`])Texas A & M([^`])' '\g<2>Texas A {\&} M\g<2>' quickref.tex
system pdflatex -shell-escape -halt-on-error quickref
system pdflatex -shell-escape -halt-on-error quickref

# Sphinx
system doconce format sphinx quickref --no_preprocess --no_abort
rm -rf sphinx-rootdir
#ALE problem reproducible after: `git clean -fd && rm -rf sphinx-rootdir`
#Hack: because doconce sphinx_dir ony works the second time (after an error), trigger that error by creating a bogus conf.py in ./
touch conf.py
system doconce sphinx_dir theme=cbc quickref dirname=sphinx-rootdir
doconce replace 'doconce format sphinx %s' 'doconce format sphinx %s --no-preprocess' automake_sphinx.py
system python automake_sphinx.py
cp quickref.rst quickref.sphinx.rst  # save

# reStructuredText:
system doconce format rst quickref --no_preprocess --no_abort
rst2xml.py quickref.rst > quickref.xml
rst2odt.py quickref.rst > quickref.odt
rst2html.py quickref.rst > quickref.rst.html
rst2latex.py quickref.rst > quickref.rst.tex
system latex quickref.rst.tex
latex quickref.rst.tex
dvipdf quickref.rst.dvi

# Other formats:
system doconce format plain quickref --no_preprocess --no_abort
system doconce format gwiki quickref --no_preprocess --no_abort
system doconce format mwiki quickref --no_preprocess --no_abort
system doconce format cwiki quickref --no_preprocess --no_abort
system doconce format st quickref --no_preprocess --no_abort
system doconce format epytext quickref --no_preprocess --no_abort
system doconce format pandoc quickref --no_preprocess --strict_markdown_output --github_md --no_abort

rm -rf demo
mkdir demo
cp -r quickref.do.txt quickref.html quickref.p.tex quickref.tex quickref.pdf quickref.rst quickref.xml quickref.rst.html quickref.rst.tex quickref.rst.pdf quickref.gwiki quickref.mwiki quickref.cwiki quickref.txt quickref.epytext quickref.st quickref.md sphinx-rootdir/_build/html demo

cd demo
cat > index.html <<EOF
<HTML><BODY>
<TITLE>Demo of Doconce formats</TITLE>
<H3>Doconce demo</H3>

Doconce is a minimum tagged markup language. The file
<a href="quickref.do.txt">quickref.do.txt</a> is the source of the
Doconce quickref, written in the Doconce format.
Running
<pre>
doconce format html quickref.do.txt
</pre>
produces the HTML file <a href="quickref.html">quickref.html</a>.
Going from Doconce to LaTeX is done by
<pre>
doconce format latex quickref.do.txt
</pre>
resulting in the file <a href="quickref.tex">quickref.tex</a>, which can
be compiled to a PDF file <a href="quickref.pdf">quickref.pdf</a>
by running <tt>latex</tt> and <tt>dvipdf</tt> the standard way.
<p>
The reStructuredText (reST) format is of particular interest:
<pre>
doconce format rst    quickref.do.txt  # standard reST
doconce format sphinx quickref.do.txt  # Sphinx extension of reST
</pre>
The reST file <a href="quickref.rst">quickref.rst</a> is a starting point
for conversion to many other formats: OpenOffice,
<a href="quickref.xml">XML</a>, <a href="quickref.rst.html">HTML</a>,
<a href="quickref.rst.tex">LaTeX</a>,
and from LaTeX to <a href="quickref.rst.pdf">PDF</a>.
The <a href="quickref.sphinx.rst">Sphinx</a> dialect of reST
can be translated to <a href="quickref.sphinx.pdf">PDF</a>
and <a href="html/index.html">HTML</a>.
<p>
Doconce can also be converted to
<a href="quickref.gwiki">Googlecode wiki</a>,
<a href="quickref.mwiki">MediaWiki</a>,
<a href="quickref.cwiki">Creole wiki</a>,
<a href="quickref.md">aPandoc</a>,
<a href="quickref.st">Structured Text</a>,
<a href="quickref.epytext">Epytext</a>,
and maybe the most important format of all:
<a href="quickref.txt">plain untagged ASCII text</a>.
</BODY>
</HTML>
EOF

echo
echo "Go to the demo directory $PWD and load index.html into a web browser."

cd ..
dest=../../pub/quickref
cp -r demo/html demo/quickref.pdf demo/quickref.html $dest

dest=../../../../doconce.wiki
cp -r demo/quickref.md $dest

echo "To remove untracked files run:"
echo "git clean -fd ../../.."
