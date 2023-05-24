> DocOnce is a modestly tagged (Markdown-like) markup language targeting scientific reports, software documentation, books, blog posts, and slides involving much math and code in the text. From DocOnce source you can generate LaTeX, Sphinx, HTML, IPython notebooks, Markdown, MediaWiki, and other formats. This means that you from a single source can get the most up-to-date publishing technologies for paper, tablets, and phones.


---
**NOTE**

If you are new to DocOnce and consider using it, we recommend to also have a look at [Quarto](https://quarto.org). Quarto has almost all functionality that is offered by Doconce, but in contrast to Doconce, Quarto uses more up-to-date technology, is actively developed and has a large user community. 

Some information on the similarities and differences between DocOnce and Quarto can be found at [the bottom of this page](#doconce-and-quarto).

---

### Documentation

 * Tutorial: [Sphinx](http://doconce.github.io/doconce/doc/pub/tutorial/html/index.html),
   [HTML](http://doconce.github.io/doconce/doc/pub/tutorial/tutorial.html),
   [PDF](http://doconce.github.io/doconce/doc/pub/tutorial/tutorial.pdf)
 * Manual: [Sphinx](http://doconce.github.io/doconce/doc/pub/manual/html/index.html),
   [HTML](http://doconce.github.io/doconce/doc/pub/manual/manual.html),
   [PDF](http://doconce.github.io/doconce/doc/pub/manual/manual.pdf)
 * Quick Reference: [Sphinx](http://doconce.github.io/doconce/doc/pub/quickref/html/index.html),
   [HTML](http://doconce.github.io/doconce/doc/pub/quickref/quickref.html),
   [PDF](http://doconce.github.io/doconce/doc/pub/quickref/quickref.pdf)
 * Troubleshooting and FAQ: [Sphinx](http://doconce.github.io/doconce/doc/pub/trouble/html/index.html),
   [HTML](http://doconce.github.io/doconce/doc/pub/trouble/trouble.html),
   [PDF](http://doconce.github.io/doconce/doc/pub/trouble/trouble.pdf)

The tutorial presents the basic syntax and the most fundamental
elements of a scientific document, while the manual has accumulated
all the different features available. The most efficient way to get
started is to look at the [report demo](http://doconce.github.io/teamods/writing_reports/index.html) and study
the [source code](http://doconce.github.io/teamods/writing_reports/_static/report.do.txt.html)
(it has all the basic elements such as title, author, abstract, table
of contents, headings, comments, inline mathematical formulas,
single/multiple equations, with and without numbering, labels,
cross-references to sections and equations, bullet lists, enumerated
lists, copying of computer code from files, inline computer code,
index entries, figures, tables, and admonitions).


### Installation

DocOnce is a Python 3 package that can be installed with `pip` or `conda`. This procedure installs a minimal number of dependencies. 

##### Preliminary steps
* The `python -V` and `pip -V` commands should refer to Python 3.x. If that is not the case, you might want to use the `pip3` and `python3` commands in the following instructions.

##### Installation using pip

Install DocOnce and its dependencies:

```
pip install DocOnce --user
```

##### Installation using conda

Create a conda environment with `pip`:
```
conda create --name doconce python=3
conda activate doconce
conda install pip
```

Install DocOnce:
```
pip install DocOnce
```

##### Installation in a Python virtual environment

A Python virtual environment is an isolated environment for python projects, which makes this option the safest installation. 

Create a virtual environment:
```
python -m venv venv
. venv/bin/activate
```

Install DocOnce:
```
pip install DocOnce
```

##### Comprehensive installation

For carrying out a comprehensive installation clone this repository 
on the local computer and run `pip install` in that directory:

```
git clone --recurse-submodules git@github.com:doconce/doconce.git
cd doconce
pip install -r requirements.txt
python setup.py install
```

Also refer to the [manual](https://doconce.github.io/doconce/doc/pub/manual/manual.html#install:doconce) to upgrade your DocOnce software to the latest update.


### Highlights

 * DocOnce is a modestly tagged markup language (see [syntax example](http://doconce.github.io/teamods/writing_reports/_static/report.do.txt.html)), quite like Markdown, but with many more features, aimed at documents with
   *much math and code in the text* (see [demo](http://doconce.github.io/teamods/writing_reports/index.html)).
 * There is extensive support for book projects. In addition to classical LaTeX-based paper books one gets for free fully responsive, modern-looking, HTML-based ebooks for tablets and phones. Parts of books can, e.g., appear in blog posts for discussion and as IPython notebooks for experimentation and annotation.
 * For documents with math and code, you can generate *clean* plain LaTeX (PDF), HTML (with MathJax and Pygments - embedded in your own templates), Sphinx for attractive web design, Markdown, IPython notebooks, HTML for Google or Wordpress blog posts, and MediaWiki. The LaTeX output has many fancy layouts for typesetting of computer code.
 * DocOnce can also output other formats (though without support for nicely typeset math and code): plain untagged text, Google wiki, Creole wiki, and reStructuredText. From Markdown or reStructuredText you can go to XML, DocBook, epub, OpenOffice/LibreOffice, MS Word, and other formats.
 * The document source is first preprocessed by Preprocess and Mako, which gives you full programming capabilities in the document's text. For example, with Mako it is easy to write a book with all computer code examples in two alternative languages (say Matlab and Python), and you can determine the language at compile time of the document. New user-specific features of DocOnce can also be implemented via Mako.
 * DocOnce extends Sphinx, Markdown, and MediaWiki output such that LaTeX align environments with labels work for systems of equations. DocOnce also adjusts Sphinx and HTML code such that it is possible to refer to equations outside the current web page.
 * DocOnce makes it very easy to write slides with math and code by stripping down running text in a report or book. LaTeX Beamer slides, HTML5 slides (reveal.js, deck.js, dzslides), and Remark (Markdown) slides are supported. Slide elements can be arranged in a grid of cells to easily control the layout.

DocOnce looks similar to [Markdown](http://daringfireball.net/projects/markdown/), [Pandoc-extended
Markdown](http://johnmacfarlane.net/pandoc/), and in particular
[MultiMarkdown](http://fletcherpenney.net/multimarkdown/).  The main
advantage of DocOnce is the richer support for writing large documents
(books) with much math and code and with
tailored output both in HTML and
LaTeX. DocOnce also has special support for exercises, [quizzes](http://doconce.github.io/doconce/doc/pub/quiz/quiz.html), and [admonitions](http://doconce.github.io/doconce/doc/pub/manual/._manual017.html#___sec55),
three very desired features when developing educational material.
Books can be composed of many smaller documents that may exist
independently of the book, thus lowering the barrier of writing books
(see [example](https://github.com/hplgit/setup4book-doconce)).


### News

Here are some of the most recent features and enhancements in DocOnce:
 * October 2020: DocOnce can now produce content files for [Jupyter Book](https://jupyterbook.org/intro.html). 
 * July 2020: Alessandro Marin at the [Centre for Computing in Science Education](http://www.mn.uio.no/ccse/english/) at the University of Oslo, assumes the role of developer and principal maintainer.
 * On 10 October 2016, Hans Petter Langtangen, creator of DocOnce, [passed away](https://www.simula.no/news/hans-petter-langtangen-1962-2016). Kristian Gregorius Hustad, supported by the [Centre for Computing in Science Education](http://www.mn.uio.no/ccse/english/) at the University of Oslo, will assume the role of principal maintainer.

Here are some books written in DocOnce:

![](https://raw.githubusercontent.com/doconce/doconce_doc/main/src/manual/fig/doconce_books.jpg)


### Contribute to DocOnce

Refer to the guide [Getting Started with Development](http://doconce.github.io/doconce/doc/pub/devel/development.html). There you can read about how the DocOnce project is structured, and how to write a run/debug configuration script for a Python IDE. 


### Demo

A [short scientific report](http://doconce.github.io/teamods/writing_reports/index.html)
demonstrates the many formats that DocOnce can generate and how
mathematics and computer code look like. (Note that at the bottom of
the page there is a link to another version of the demo with complete
DocOnce commands for producing the different versions.)

<!-- Note: local links does not work since this README file is a source -->
<!-- code file and not part of the published gh-pages. Use full URL. -->

Another demo shows how DocOnce can be used to [create slides](http://doconce.github.io/doconce/doc/pub/slides/demo/index.html) in
various formats (HTML5 reveal.js, deck.js, etc., as well as LaTeX
Beamer).

DocOnce has support for *responsive* HTML documents with design and
functionality based on Bootstrap styles.  A [Bootstrap demo](http://doconce.github.io/doconce/doc/pub/bootstrap/index.html)
illustrates the many possibilities for colors and layouts.

DocOnce also has support for exercises in [quiz format](http://doconce.github.io/doconce/doc/pub/quiz/quiz.html). Pure quiz files can be *automatically uploaded* to 
[Kahoot!](https://getkahoot.com) online quiz games operated through smart
phones (with the aid of [quiztools](https://github.com/doconce/quiztools) 
for DocOnce to Kahoot! translation).



Several books (up to over 1000 pages) have been written entirely in
DocOnce. The primary format is a publisher-specific LaTeX style, but
HTML or Sphinx formats can easily be generated, such as [this chapter
in Bootstrap style](http://doconce.github.io/primer.html/doc/pub/looplist/looplist-bootstrap.html),
or the [solarized color style](http://doconce.github.io/primer.html/doc/pub/looplist/looplist-solarized.html)
as many prefer. Slides can quickly be generated from the raw text in
the book.  Here are examples in the [reveal.js](http://doconce.github.io/scipro-primer/slides/looplist/html/looplist-reveal-beige.html)
(HTML5) style, or the more traditional [LaTeX Beamer](http://doconce.github.io/scipro-primer/slides/looplist/pdf/looplist-beamer.pdf)
style, and even the modern [IPython notebook](http://nbviewer.ipython.org/url/hplgit.github.io/scipro-primer/slides/looplist/ipynb/looplist.ipynb)
tool, which allows for interactive experimentation and annotation.


### License

DocOnce is licensed under the BSD license, see the included `LICENSE` file.

### Authors

DocOnce was originally written by Hans Petter Langtangen at [hpl@simula.no](mailto:hpl@simula.no) in 2006-2016. Alessandro Marin ([email address](mailto:alessandro.marin@fys.uio.no)) has assumed in 2020 the role of developer and principal maintainer. A lot of people have contributed to testing the software and suggesting improvements. 


### How to cite

#### Link in the copyright

The command-line option `--cite_doconce` can be used
to equip the copyright field with a link to the present page.
Here is an example involving some document `mydoc.do.txt`:


```
TITLE: Some document
AUTHOR: Joe Doe
...
```

Compile to HTML with DocOnce link:


```
Terminal> doconce format html mydoc --cite_doconce
```

The footer of the first page will now contain "Made with DocOnce".

#### Traditional citation in a bibliography

BibTeX format:


```
@misc{DocOnce,
  title = {{DocOnce} markup language},
  author = {H. P. Langtangen},
  url = {https://github.com/doconce/doconce},
  key = {DocOnce},
  note = {\url{https://github.com/doconce/doconce}},
}
```

Publish format:


```
* misc
** {DocOnce} markup language
   key:       DocOnce
   author:    H. P. Langtangen
   url:       https://github.com/doconce/doconce
   status:    published
   sortkey:   DocOnce
   note:      \url{https://github.com/doconce/doconce}
```

## DocOnce and Quarto

Quarto is ["an open-source scientific and technical publishing system"](https://quarto.org) with very similar philosophy as DocOnce: write in a markup-language (like Markdown), convert to, and publish in, many different output formats.

Quarto is developed by [Posit](https://posit.co) together with the user community, see [Quarto's main GitHub repository](https://github.com/quarto-dev/quarto-cli).

DocOnce is no longer actively developed and is in maintance-only mode. This is not likely to change in the near future. There we see Quarto as a good, probably preferable, alternative to DocOnce. We are considering developing a command that converts a DocOnce file (`.do.txt`) to a file compatible with Quarto (`.qmd`).

Not all functionality of DocOnce is natively available with Quarto as of this moment. Here is an overview of the differences. Note that this is a work in progress - we appreciate contribtutions to this list should you have any!

## Noticeable differences between DocOnce and Quarto

- Quarto relies on blocks of text fenced with at least three colons `:::`. While in DocOnce one can quickly locate the end of a fenced block, e.g. `!ec` or `!esol`, this may not be so straightforward in Quarto and closing fences have no label.
- DocOnce supports comments using one or more `#` symbols at the start of a line. As Quarto is based on MarkDown, comments need to be added using plain html, i.e. fenced with `<!--` and `-->`
- Quarto handles references much easier for PDF output. A single render command suffices, there is no need to run pdflatex multiple times
- [preprocessing](https://doconce.github.io/doconce/doc/pub/manual/manual.html#preprocessing-and-postprocessing) using tools like preprocess and mako is not a 'native' Quarto feature, but can probably be emulated in different ways, including using [filters](https://quarto.org/docs/extensions/filters.html).
- converting to Jupyter notebook is not as feauture-rich in Quarto as it is in DocOnce. Figure captions and citations do not always work well. Quarto developers told us they are working on improving the conversion to notebooks
- generating html slides is limited to reveal js

## DocOnce features missing in Quarto

This list is a work in progress...

- when converting to Jupyter notebook (`.ipynb`), DocOnce generates a `ipynb-<filename>-src.tar.gz` file containing images for distribution with the notebook, but Quarto does not. Note that Quarto's `--extract-media` setting may be a solution, this allows a custom folder for images. See https://quarto.org/docs/reference/formats/ipynb.html#rendering
- clickable references in PDF seems broken (using `link-citations: true`) 
- exercise formatting and numbering
  - there is no special support for Exercises as in DocOnce, see ["Exercises, Problems, Projects, and Examples"](https://doconce.github.io/doconce/doc/pub/manual/manual.html#manual:exercises)
	- `::: {#exr}` blocks do not allow formatting of exercises title in `.ipynb`, and overrides `::: {.cell .markdown}` blocks
	- see also https://stackoverflow.com/questions/73288264/shared-counter-in-quarto-for-exercises-examples-etc
  - DocOnce features such as the `--without-solutions` flag for hiding solutions in the output can be done in Quarto using [Project Profiles](https://quarto.org/docs/projects/profiles.html)
- including code verbatim through `@@@CODE` or results from commands through `@@@OSCMD`. The Quarto extension [include-code-files](https://github.com/quarto-ext/include-code-files) may solve this
- Doconce's ["fromto and from-to directives"](https://doconce.github.io/doconce/doc/pub/manual/manual.html#the-fromto-and-from-to-directives) have no alternative in Quarto
- cells in the notebook have a unique id, which when generated by DocOnce, is based on cell content, not on a random hash. This feature [was added](https://github.com/doconce/doconce/pull/223) to be able to have stable cell IDs when regenerating the notebook file from the same doconce file.
	- a workaround seems to be to add a label or tag to each cell with  `#| label:` or `#| tag:`, which then becomes the ID of the cell

## Quarto features not implemented in DocOnce
- figure numbering in notebooks (`.ipynb`) works in Quarto, this is currently a bug in DocOnce
- `::: {.cell .markdown}` blocks for markdown-cells in notebooks, enabling determining which text should be in a single markdown cell
- revealjs: `::: {.fragment}` for stepping through arbitrary content, not just bulleted lists 

## Some practical tips

- The DocOnce `bc pycod-t` environment can be emulated in Quarto using

``````
```python  
print("Hei")
```
``````


Note the use of `python` instead of `{python}`