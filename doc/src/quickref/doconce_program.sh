DocOnce version 1.5.8 (from /home/amarin/doconce/lib/doconce)
Usage: doconce command [optional arguments]
commands: help format find subst replace remove spellcheck apply_inline_edits capitalize change_encoding clean combine_images csv2table diff expand_commands expand_mako extract_exercises find_nonascii_chars fix_bibtex4publish gitdiff grab grep guess_encoding gwiki_figsubst html2doconce html_colorbullets jupyterbook include_map insertdocstr ipynb2doconce latex2doconce latex_dislikes latex_exercise_toc latex_footer latex_header latex_problems latin2html lightclean linkchecker list_fig_src_files list_labels makefile md2html md2latex old2new_format ptex2tex pygmentize ref_external remove_exercise_answers remove_inline_comments replace_from_file slides_beamer slides_html slides_markdown sphinx_dir sphinxfix_localURLs split_html split_rst teamod

doconce format html|latex|pdflatex|rst|sphinx|plain|gwiki|mwiki|
               cwiki|pandoc|st|epytext dofile 
# transform doconce file to another format

doconce subst [-s -m -x --restore] regex-pattern \ 
        regex-replacement file1 file2 ... 
# substitute a phrase by another using regular expressions (in this example -s is the re.DOTALL modifier, -m is the re.MULTILINE modifier, -x is the re.VERBOSE modifier, --restore copies backup files back again)

doconce replace from-text to-text file1 file2 ...                      
# replace a phrase by another literally (exact text substitution)

doconce replace_from_file file-with-from-to-replacements file1 file2 ... 
# replace using from and to phrases from file

doconce find expression                                                
# search for a (regular) expression in all .do.txt files in the current directory tree (useful when removing compilation errors)

doconce include_map mydoc.do.txt                                       
# print an overview of how various files are included in the root doc

doconce expand_mako mako_code_file funcname file1 file2 ...            
# replace all mako function calls by the `results of the calls

doconce remove_inline_comments dofile                                  
# remove all inline comments in a doconce file

doconce apply_inline_edits                                             
# apply all edits specified through inline comments

doconce sphinx_dir copyright='John Doe' title='Long title' \
        short_title="Short title" version=0.1 intersphinx \
        /path/to/mylogo.png dofile 
# create a directory for the sphinx format (requires sphinx version >= 1.1)

doconce format sphinx complete_file 
doconce split_rst complete_file 
doconce sphinx_dir complete_file 
python automake_sphinx.py 
# split a sphinx/rst file into parts according to !split commands

doconce insertdocstr rootdir                                           
# walk through a directory tree and insert doconce files as docstrings in *.p.py files

doconce lightclean                                                     
# remove all redundant files (keep source .do.txt and results: .pdf, .html, sphinx- dirs, .mwiki, .ipynb, etc.)

doconce clean                                                          
# remove all files that the doconce can regenerate

doconce change_encoding utf-8 latin1 dofile                            
# change encoding

doconce guess_encoding filename                                        
# guess the encoding in a text

doconce find_nonascii_chars file1 file2 ...                            
# find non-ascii characters in a file

doconce split_html complete_file.html                                  
# split an html file into parts according to !split commands

doconce slides_html slide_type complete_file.html                      
# create HTML slides from a (doconce) html file

doconce slides_beamer complete_file.tex                                
# create LaTeX Beamer slides from a (doconce) latex/pdflatex file

doconce slides_markdown complete_file.md remark --slide_style=light    
# create Remark slides from Markdown

doconce html_colorbullets file1.html file2.html ...                    
# replace bullets in lists by colored bullets

doconce extract_exercises tmp_mako__mydoc                              
# extract all exercises (projects and problems too)

doconce grab --from[-] from-text [--to[-] to-text] file > result       
# grab selected text from a file

doconce remove --from[-] from-text [--to[-] to-text] file > result     
# remove selected text from a file

doconce grep FIGURE|MOVIE|CODE dofile                                  
# list all figure, movie or included code files

doconce spellcheck [-d .mydict.txt] *.do.txt                           
# run spellcheck on a set of files

doconce ptex2tex mydoc -DMINTED pycod=minted sys=Verbatim \
        dat=\begin{quote}\begin{verbatim};\end{verbatim}\end{quote} 
# transform ptex2tex files (.p.tex) to ordinary latex file and manage the code environments

doconce md2html file.md                                                
# make HTML file via pandoc from Markdown (.md) file

doconce md2latex file.md                                               
# make LaTeX file via pandoc from Markdown (.md) file

doconce combine_images image1 image2 ... output_file                   
# combine several images into one

doconce latex_problems mydoc.log [overfull-hbox-limit]                 
# report problems from a LaTeX .log file

doconce list_fig_src_files *.do.txt                                    
# list all figure files, movie files, and source code files needed

doconce list_labels myfile                                             
# list all labels in a document (for purposes of cleaning them up)

doconce ref_external mydoc [pubfile]                                   
# generate script for substituting generalized references

doconce linkchecker *.html                                             
# check all links in HTML files

doconce capitalize [-d .mydict.txt] *.do.txt                           
# change headings from "This is a Heading" to "This is a heading"

doconce latex2doconce latexfile                                        
# translate a latex document to doconce (requires usually manual fixing)

doconce latex_dislikes latexfile                                       
# check if there are problems with translating latex to doconce

doconce ipynb2doconce notebookfile                                     
# translate an IPython/Jupyter notebook to doconce

doconce pygmentize myfile [pygments-style]                             
# typeset a doconce document with pygments (for pretty print of doconce itself)

doconce makefile docname doconcefile [html sphinx pdflatex ...]        
# generate a make.py script for translating a doconce file to various formats

doconce diff file1.do.txt file2.do.txt [diffprog]                      
# find differences between two files (diffprog can be difflib, diff, pdiff, latexdiff, kdiff3, diffuse, ...)

doconce gitdiff file1 file2 file3 ...                                  
# find differences between the last two Git versions of several files

doconce csv2table somefile.csv                                         
# convert csv file to doconce table format

doconce sphinxfix_local_URLs file.rst                                  
# edit URLs to local files and place them in _static

doconce latin2html file.html                                           
# replace latex-1 (non-ascii) characters by html codes

doconce fix_bibtex4publish file1.bib file2.bib ...                     
# fix common problems in bibtex files for publish import

doconce latex_header                                                   
# print the header (preamble) for latex file

doconce latex_footer                                                   
# print the footer for latex files

doconce expand_commands file1 file2 ...                                
# expand short cut commands to full form in files

doconce latex_exercise_toc myfile                                      
# insert a table of exercises in a latex file myfile.p.tex
