
.. raw:: html

        <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
          TeX: {
             equationNumbers: {  autoNumber: "AMS"  },
             extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js", "color.js"]
          }
        });
        </script>
        <script type="text/javascript" async
         src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
        </script>
        
        

.. Automatically generated reStructuredText file from DocOnce source
   (https://github.com/doconce/doconce/)

.. |nbsp| unicode:: 0xA0
   :trim:

.. Document title:

A Document for Testing DocOnce
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:Authors: Hans Petter Langtangen (hpl at simula.no), Kaare Dump, A. Dummy Author, I. S. Overworked and Outburned, J. Doe (j_doe at cyberspace.com)
:Date: Jan 32, 2100

Made with DocOnce

.. contents:: Table of contents
   :depth: 2

.. !split

The format of this document is
rst

*Abstract.* This is a document with many test constructions for doconce syntax.
It was used heavily for the development and kept for testing
numerous constructions, also special and less common cases.

And exactly for test purposes we have an extra line here, which
is part of the abstract.

.. Cannot demonstrate chapter headings since abstract and chapter

.. are mutually exclusive in LaTeX

.. _sec1:

Section 1
=========

Here is a nested list:

  * item1

  * item2

  * item3 which continues on the next line to test that feature

  * and a sublist

    * with indented subitem1

    * and a subitem2

  * and perhaps an ordered sublist

   a. first item

   b. second item, continuing on a new line

**Here is a list with paragraph heading.**

  * item1

  * item2

Here is a list with subsubsection heading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  * item1

  * item2


..

    Here are two lines that make up
    a block quote for testing *emphasized words* and **boldface words**,
    also with hypens:
    *pre*-fix, post-*fix*, **pre**-fix, post-**fix**.



Here are two references. Equation |nbsp| (`my:eq1`_) is fine. Eq. |nbsp| (`my:eq1`_) too.
Even Equation (`my:eq1`_) without the tilde.

.. _subsec1:

Subsection 1
------------

.. Refer to section/appendix etc. at the beginning of the line

.. and other special fix situations for HTML.

More text, with a reference back to
the section `Section 1`_ and `Subsection 1`_, and further to the
the sections `Subsection 1`_ and `URLs`_, which
encourages you to do the tasks in `Problem 2: Flip a Coin`_ and `Exercise 10: Make references to projects and problems`_.
 `Appendix: Just for testing; part I`_ and `Appendix: Just for testing; part II`_ are also nice elements.

Test Section reference at beginning of line and after a sentence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The section `Subsection 1`_ is fine.
The section `URLs`_ too.

.. sphinx code-blocks: pycod=python cod=fortran cppcod=c++ sys=console

Computer code
~~~~~~~~~~~~~

Let's do some copying from files too. First from subroutine up to the very end::

              subroutine test()
              integer i
              real*8 r
              r = 0
              do i = 1, i
                 r = r + i
              end do
              return
        C     END1
        
              program testme
              call test()
              return

and then just the subroutine::

        
              subroutine test()
              integer i
              real*8 r
              r = 0
              do i = 1, i
                 r = r + i
              end do
              return

and finally the complete file with a plain text verbatim environment
(``envir=ccq``)::

        C     a comment
        
              subroutine test()
              integer i
              real*8 r
              r = 0
              do i = 1, i
                 r = r + i
              end do
              return
        C     END1
        
              program testme
              call test()
              return

Testing other code environments. First Python::

        !bc pycod
        def f(x):
            return x+1
        !ec

which gets rendered as::

        def f(x):
            return x+1

Here is a program that is supposed to be interactive via
Python Online Tutorial, but that service is not accessible
for the present format::

        class Line:
            def __init__(self, a, b):
                self.a, self.b = a, b
        
            def __call__(self, x):
                a, b = self.a, self.b
                return a*x + b
        
        line = Line(2, 1)
        y = line(x=3)
        print(y)

Some more Python code (actually specified as a sage cell, but
such cells are not supported by this format)::

        a = 2
        b = 3
        print('a+b:', a + b)
        
        # In a sage cell we can also plot
        from matplotlib.pyplot import *
        from numpy import *
        x = linspace(0, 4*pi, 101)
        y = exp(-0.1*x)*cos(x)
        plot(x, y)
        xlabel('x'); ylabel('y')
        show()

Then Cython (with -h option so it is hidden in html/sphinx)::

        cpdef f(double x):
            return x + 1

Standard Python shell sessions::

        >>> from numpy import linspace, sin
        >>> # Some comment
        >>> x = linspace(0, 2, 11)
        >>> y = sin(x)
        >>> y[0]

        >>> import matplotlib.pyplot as plt
        >>> plt.plot(x, y)

Similar IPython sessions::

        In [1]: from numpy import linspace, sin
        In [2]: # Some comment
        In [3]: x = linspace(0, 2, 11)
        In [4]: y = sin(x)
        In [5]: y[0]
        Out[5]: 0
        In [6]: import matplotlib.pyplot as plt
        In [7]: plt.plot(x, y)
        In [8]: a='multiple-\nline\noutput'
        In [9]: a
        Out[9]: 'multiple-\nline\noutput'
        In [10]: print(a)
        multiple-
        line
        output

Here is the interactive session again, but with ``pyshell-t``::

        >>> from numpy import linspace, sin
        >>> # Some comment
        >>> x = linspace(0, 2, 11)
        >>> y = sin(x)
        >>> y[0]

        >>> import matplotlib.pyplot as plt
        >>> plt.plot(x, y)

.. This one tests a + sign before a code environment

C++::

        #include <iostream>
        
        int main()
        {
           std::cout << "Sample output" << std::endl;
           return 0
        }

.. The next should get correctly typset in sphinx (cod is fcod)

.. It also tests emoji before code

And a little bit of Fortran: :dizzy_face::

        !bc cod
              subroutine midpt(x, length, a, b)
              real*8 a, b, x
              x = (a + b)/2
              length = b - a
              return
              end
        !ec

which then is typeset as::

              subroutine midpt(x, length, a, b)
              real*8 a, b, x
              x = (a + b)/2
              length = b - a
              return
              end

HTML::

        <table>
        <tr><td>Column 1</td><td>Column 2</td></tr>
        <tr><td>0.67526 </td><td>0.92871 </td></tr>
        <!-- comment -->
        </table>

But inline HTML code is also important, like text that starts with
``<a href="`` (which can destroy the following text if not properly
quoted).

Matlab with comments requires special typesetting::

        % Comment on the beginning of the line can be escaped by %%
        if a > b
          % Indented comment needs this trick
          c = a + b
        end

And here is a system call::

        Terminal> mkdir test
        Terminal> cd test
        Terminal> myprog -f
        output1
        output2

Any valid pygments lexer/language name can appear to, e.g.::

        !bc restructuredtext
        =======
        Heading
        =======
        
        Some text.
        !ec

results in::

        =======
        Heading
        =======
        
        Some text.

.. Here goes hidden code.

.. Python can be treated by some formats, Fortran is always out.

Finally, ``!bc do`` supports highlighting of DocOnce source::

        ======= DocOnce test file =======
        
        ===== Computer code =====
        
        Inline verbatim code, as in `import numpy as np`, is allowed, as well as
        code blocks:
        
        !bc pycod
        from math import sin
        
        def f(x):
            """Example on a function."""
            return sin(x) + 1
        
        print(f(0))
        !ec
        
        
        ===== Mathematics =====
        
        Formulas can be inline, as in $\nabla\cdot\bm{u} = 0$, or typeset
        as equations:
        
        !bt
        \begin{align*}
        \nabla\cdot\bm{u} &= 0,\\ 
        \bm{u} &= \nabla\phi .
        \end{align*}
        !et
        
        === Subsubsection heading ===
        
        DocOnce files can have chapters, sections, subsections, and subsubsections.
        
        __Paragraph heading.__ Paragraphs may have headings.

It is time to test ``verbatim inline font`` especially with ``a newline
inside the text`` and an exclamation mark at the end: ``BEGIN``! For
spellcheck, test ``a verbatim expression`` in ``another`` in a ``third``.
Also test exclamation mark as in ``!bc`` and ``!ec`` as well as ``a != b``.
Also test backslashes and braces like ``\begin``, ``\begin{enumerate}``,
``\end{this}\end{that}``, and ``{something \inside braces}``.

The following attempt to exemplify colored text does not work in
format rst.
Here is some **red color** and an attempt to write **with
green color containing a linebreak

| code.** Some formats will only display 
| this correctly when ``html`` 
| is the output format.

But here some more running text is added which is not part of
the previous blocks with line breaks.

Running OS commands
~~~~~~~~~~~~~~~~~~~

        Terminal> python -c 'print("Testing\noutput\nfrom\nPython.")'
        Testing
        output
        from
        Python.

Footnotes
~~~~~~~~~

Here is a test of footnotes [#footnote]_, which are handy in text.
They are used in different flavors, now in

 * list items (note below that footnotes work after math, verbatim, and URLs - bin fact old and emphasize too!)

 * even with math \\( \nabla^2u \\) [#math1]_

 * and code ``h[i] += 1`` [#code]_ (*must* have space between inline code and footnote!)

 * and `links <https://google.com>`__ [#google-search]_

which gives flexibility in writing.
This is the third [#example-of-the-third-footnote]_ example.

.. [#footnote] Typesetting of the footnote depends on the format.
   Plain text does nothing, LaTeX removes the
   definition and inserts the footnote as part of the LaTeX text.
   reStructuredText and Sphinx employ a similar type of typesetting
   as Extended Markdown and DocOnce, and in HTML we keep the same
   syntax, just displayed properly in HTML.

.. [#math1] Math footnotes can be dangerous since it
   interferes with an exponent.

.. [#code] One-line footnote.

.. [#google-search] `<google.com>`_ is perhaps the most famous
   web site today.

Here is some more text before a new definition of a footnote that was
used above.


.. admonition:: Non-breaking space character

   This paragraph aims to test `non-breaking space character <https://en.wikipedia.org/wiki/Non-breaking_space>`__, and a typical
   example where this is needed is in physical units: 7.4 |nbsp| km is traveled
   in |nbsp| \\( 7.4/5.5\approx 1.345 \\) |nbsp| s.  Also check that a |nbsp| `link <https://google.com>`__ |nbsp| is
   not broken across lines (drag the browser window to test this).
   (On the other hand, the tilde is used in
   computer code, e.g., as in ``[~x for x in y]`` or in ``y=~x``, and should
   of course remain a tilde in those contexts.)




.. _subsec:ex:

Subsection 2: Testing figures
-----------------------------

Test of figures. In particular we refer to Figure `fig:impact`_ in which
there is a flow.

.. _fig:impact:

.. figure:: testfigs/wave1D.png
   :width: 200

   *Visualization **of** a *wave**  (fig:impact)

Figures without captions are allowed and will be inlined.

.. figure:: testfigs/wave1D.png
   :width: 200

.. Test multi-line caption in figure with sidecap=True

Here is figure `myfig`_ with a long (illegal) multi-line caption
containing inline verbatim text:

.. _myfig:

.. figure:: testfigs/wave1D.png
   :width: 500

   *A long caption spanning several lines and containing verbatim words like ``my_file_v1`` and ``my_file_v2`` as well as math with subscript as in $t_{i+1}$*  (myfig)

.. Must be a blank line after MOVIE or FIGURE to detect this problem

Test URL as figure name:

.. figure:: https://raw.github.com/doconce/doconce/master/doc/src/blog/f_plot.png
   :width: 500

.. Test wikimedia type of files that otherwise reside in subdirs

**Remark.**
Movies are tested in separate file ``movies.do.txt``.

.. Somewhat challenging heading with latex math, \t, \n, ? and parenthesis

.. _decay:sec:theta:

The \\( \theta \\) parameter (not \\( \nabla \\)?)
--------------------------------------------------

Functions do not always need to be advanced, here is one
involving \\( \theta \\)::

        def f(theta):
            return theta**2

**More on \\( \theta \\).**
Here is more text following headline with math.

Newcommands must also be tested in this test report:
\\( \frac{1}{2} \\), \\( {1/2} \\), \\( \pmb{x} \\), \\( \frac{Du}{dt} \\),
both inline and in block

.. raw:: html

        $$
        \begin{align}
        \frac{Du}{dt} &= 0\nonumber
        \\ 
        \frac{1}{2} &= {1/2}\\ 
        \frac{1}{2}\pmb{x} &= \pmb{n}
        \end{align}
        $$

Or with align with label and numbers

.. raw:: html

        $$
        \begin{align}
        \frac{Du}{dt} &= 0
        \label{aligneq1}
        \\ 
        \frac{1}{2} &= {1/2}\\ 
        \frac{1}{2}\pmb{x} &= \pmb{n}
        \label{aligneq2}
        \end{align}
        $$

.. Must test more complicated align and matrix compositions

.. where DocOnce inserts auto-numbered labels etc.

First one numbered (automatically)

.. raw:: html

        $$
        \begin{align}
        \begin{pmatrix}
        G_2 + G_3 & -G_3 & -G_2 & 0 \\ 
        -G_3 & G_3 + G_4 & 0 & -G_4 \\ 
        -G_2 & 0 & G_1 + G_2 & 0 \\ 
        0 & -G_4 & 0 & G_4
        \end{pmatrix}
        &=
        \begin{pmatrix}
         v_1 \\ 
         v_2 \\ 
         v_3 \\ 
         v_4
        \end{pmatrix}
        + \cdots \\ 
        \begin{pmatrix}
         C_5 + C_6 & -C_6 & 0 & 0 \\ 
         -C_6 & C_6 & 0 & 0 \\ 
         0 & 0 & 0 & 0 \\ 
         0 & 0 & 0 & 0
        \end{pmatrix}
          &= \frac{d}{dt}\begin{pmatrix}
         v_1 \\ 
         v_2 \\ 
         v_3 \\ 
         v_4
        \end{pmatrix} +
        \begin{pmatrix}
         0 \\ 
         0 \\ 
         0 \\ 
         -i_0
        \end{pmatrix}
        \nonumber
        \end{align}
        $$

Second numbered (automatically)

.. raw:: html

        $$
        \begin{align}
        \begin{pmatrix}
        G_1 + G_2\\ 
        -G_3 & G_4
        \end{pmatrix}
        &=
        \begin{pmatrix}
         v_1 \\ 
         v_2
        \end{pmatrix}
        + \cdots\nonumber
        \\ 
        \left(\begin{array}{ll}
        y & 2\\ 
        2 & 1
        \end{array}\right)
        \left(\begin{array}{ll}
        0 \\ x
        \end{array}\right)
        &= \begin{pmatrix}
        A \\ B
        \end{pmatrix}
        \end{align}
        $$

Both numbered, with label by the user

.. raw:: html

        $$
        \begin{align}
        \begin{pmatrix}
        G_1 + G_2\\ 
        -G_3 & G_4
        \end{pmatrix}
        &=
        \begin{pmatrix}
         v_1 \\ 
         v_2
        \end{pmatrix}
        + \cdots \label{mymatrix:eq1}
        \\ 
        \label{mymatrix:eq2}
        \left(\begin{array}{ll}
        y & 2\\ 
        2 & 1
        \end{array}\right)
        \left(\begin{array}{ll}
        0 \\ x
        \end{array}\right)
        &= \begin{pmatrix}
        A \\ B
        \end{pmatrix}
        \end{align}
        $$

Now we refer to Equations (mymatrix:eq1)-(mymatrix:eq2).

Custom Environments
-------------------

Here is an attempt to create a theorem environment via Mako
(for counting theorems) and comment lines to help replacing lines in
the ``.tex`` by proper begin-end LaTeX environments for theorems.
Should look nice in most formats!

.. begin theorem

**Theorem 5.**
Let \\( a=1 \\) and \\( b=2 \\). Then \\( c=3 \\).

.. end theorem

.. begin proof

**Proof.**
Since \\( c=a+b \\), the result follows from straightforward addition.
\\( \Diamond \\)

.. end proof

As we see, the proof of Theorem 5 is a modest
achievement.

.. _subsec:table:

Tables
------

.. index with comma could fool sphinx

Let us take this table from the manual:

====  ========  ============  
time  velocity  acceleration  
====  ========  ============  
0.0     1.4186         -5.01  
2.0   1.376512        11.919  
4.0     1.1E+1     14.717624  
====  ========  ============  

The DocOnce source code reads::

        
          |--------------------------------|
          |time  | velocity | acceleration |
          |--l--------r-----------r--------|
          | 0.0  | 1.4186   | -5.01        |
          | 2.0  | 1.376512 | 11.919       |
          | 4.0  | 1.1E+1   | 14.717624    |
          |--------------------------------|
        

Here is yet another table to test that we can handle more than
one table:

====  ========  ============  
time  velocity  acceleration  
====  ========  ============  
0.0   1.4186    -5.01         
1.0   1.376512  11.919        
3.0   1.1E+1    14.717624     
====  ========  ============  

And one with math headings (that are expanded and must be treated
accordingly), verbatim heading and entry, and no space around the pipe
symbol:

=========  ===========  ================  =======  
\\( i \\)  \\( h_i \\)  \\( \bar T_i \\)  ``L_i``  
=========  ===========  ================  =======  
0                    0               288  -0.0065  
1               11,000               216      0.0  
2               20,000               216    0.001  
3               32,000               228   0.0028  
4               47,000               270      0.0  
5               51,000               270  -0.0028  
6               71,000               214  ``NaN``  
=========  ===========  ================  =======  

And add one with verbatim headings (with underscores),
and rows starting with ``|-`` because of a negative number,
and ``|`` right before and after verbatim word (with no space):

=====  =======  =====================  ===========  
exact  ``v_1``  \\( a_i \\) + ``v_2``  ``verb_3_``  
=====  =======  =====================  ===========  
    9     9.62                   5.57         8.98  
  -20   -23.39                  -7.65       -19.93  
   10    17.74                  -4.50         9.96  
    0    -9.19                   4.13        -0.26  
=====  =======  =====================  ===========  

Pipe symbols in verbatim and math text in tables used to pose difficulties,
but not
anymore:

===============  ===============  
   \\( S \\)         command      
===============  ===============  
$ ||a_0|| $      ``norm|length``  
\\( x\cap y \\)          ``x|y``  
===============  ===============  

Here is a table with X alignment:

=====  ==========================================================================================================================================================================================================================  
 Type                                                                                                         Description                                                                                                          
=====  ==========================================================================================================================================================================================================================  
  X    Alignment character that is used for specifying a potentially very long text in a column in a table. It makes use of the ``tabularx`` package in LaTeX, otherwise (for other formats) it means ``l`` (centered alignment).  
l,r,c  standard alignment characters                                                                                                                                                                                               
=====  ==========================================================================================================================================================================================================================  

Finally, a table with math
(``bm`` that expands to ``boldsymbol``, was tricky, but
cleanly handled now)
and URLs.

.. Mako code to expand URLs in the table

.. (These types of tables did not work before Jan 2014)

=============================  ==========================================================  ==========================================================  
                                                                                                                                                       
=============================  ==========================================================  ==========================================================  
    \\( \mathcal{L}=0 \\)      `080 <../doc/src/manual/mov/wave_frames/frame_0080.png>`__  `085 <../doc/src/manual/mov/wave_frames/frame_0085.png>`__  
         \\( a=b \\)           `090 <../doc/src/manual/mov/wave_frames/frame_0090.png>`__  `095 <../doc/src/manual/mov/wave_frames/frame_0095.png>`__  
\\( \nabla\cdot\bm{u} =0  \\)  `100 <../doc/src/manual/mov/wave_frames/frame_0100.png>`__  `105 <../doc/src/manual/mov/wave_frames/frame_0105.png>`__  
=============================  ==========================================================  ==========================================================  

A test of verbatim words in heading with subscript \\( a_i \\): ``my_file_v1`` and ``my_file_v2``
-------------------------------------------------------------------------------------------------

**Paragraph with verbatim and math: ``my_file_v1.py`` and ``my_file_v2.py`` define some math \\( a_{i-1} \\).**
Here is more ``__verbatim__`` code and
some plain text on a new line.

.. Test various types of headlines

**Just bold**
-------------

Some text.

*Just emphasize*
----------------

Some text.

``Just verbatim``
-----------------

Some text.

**Bold** beginning
------------------

Some text.

*Emphasize* beginning
---------------------

Some text.

``Verbatim`` beginning
----------------------

Some text.

Maybe **bold end**
------------------

Some text.

Maybe *emphasize end*
---------------------

Some text.

Maybe ``verbatim end``
----------------------

Some text.

The middle has **bold** word
----------------------------

Some text.

The middle has *emphasize* word
-------------------------------

Some text.

The middle has ``verbatim`` word
--------------------------------

Some text.

***Just emphasize*.**
Some text.

**``Just verbatim``.**
Some text.

***Emphasize* beginning.**
Some text.

**``Verbatim beginning``.**
Some text.

**Maybe *emphasize end*.**
Some text.

**Maybe ``verbatim end``.**
Some text.

**The middle has *emphasize* word.**
Some text.

**The middle has ``verbatim`` word.**
Some text.

**Ampersand.**
We can test Hennes & Mauritz, often abbreviated H&M, but written
as ``Hennes & Mauritz`` and ``H & M``.
A sole ``&`` must also work.

.. Note: substitutions must not occur inside verbatim, just in ordinary text::

        # Just to check that ampersand works in code blocks:
        c = a & b

**Quotes.**
Let us also add a test of quotes such as "double quotes, with numbers
like 3.14 and newline/comma and hyphen (as in double-quote)"; written
in the standard LaTeX-style that gives correct LaTeX formatting and
ordinary double quotes for all non-LaTeX formats.  Here is another
sentence that "caused" a bug in the past because double backtick
quotes could imply verbatim text up to a verbatim word starting with
period, like ``.txt``.

More quotes to be tested for spellcheck:
("with parenthesis"), "with newline"
and "with comma", "hyphen"-wise, and "period".

Bibliography test
-----------------

Here is an example: [Ref01]_ discussed propagation of
large destructive water waves, [Ref02]_ gave
an overview of numerical methods for solving the Navier - Stokes equations,
while the use of Backward Kolmogorov equations for analyzing
random vibrations was investigated in [Ref03]_.
The book chapter [Ref04]_ contains information on
C++ software tools for programming multigrid methods. A real retro
reference is [Ref05]_ about a big FORTRAN package.
Multiple references are also possible, e.g., see
[Ref01]_ [Ref04]_.

We need to cite more than 10 papers to reproduce an old formatting
problem with blanks in the keys in reST format:
[Ref06]_ [Ref03]_ [Ref07]_ [Ref01]_
and
[Ref02]_ [Ref08]_ [Ref09]_ [Ref10]_ [Ref11]_ [Ref12]_ [Ref13]_
and all the work of
[Ref14]_ [Ref04]_ [Ref15]_ as well as
old work [Ref05]_ and [Ref16]_, and the
talk [Ref17]_.
Langtangen also had two thesis [Ref18]_ [Ref16]_
back in the days.
More retro citations are
the old ME-IN323 book [Ref19]_ and the
[Ref20]_ OONSKI '94 paper.

.. --- begin exercise ---

.. _Example:

Example 1: Examples can be typeset as exercises
-----------------------------------------------

Examples can start with a subsection heading starting with ``Example:``
and then, with the command-line option ``--examples_as_exercises`` be
typeset as exercises. This is useful if one has solution
environments as part of the example.

**a)**
State some problem.

**Solution.**
The answer to this subproblem can be written here.

**b)**
State some other problem.

**Hint 1.**
A hint can be given.

**Hint 2.**
Maybe even another hint?

**Solution.**
The answer to this other subproblem goes here,
maybe over multiple doconce input lines.

.. --- end exercise ---

User-defined environments
-------------------------

The example in the section `Example 1: A test function`_ demonstrates how to write a test function.
That is, a special test function for a function ``add`` appears in
the example in the section `Example 1: A test function`_.

.. _ex:test:1p1:

Example 1: A test function
--------------------------

Suppose we want to write a test function for checking the
implementation of a Python function for addition::

        def add(a, b):
            return a + b
        
        def test_add():
            a = 1; b = 1
            expected = a + b
            computed = add(a, b)
            assert expected == computed

.. _ex:math:1p1:

Example 2: Addition
-------------------

We have

.. raw:: html

        $$ 1 + 1 = 2 $$

or in tabular form:

===========  =========  
  Problem      Result   
===========  =========  
\\( 1+1 \\)  \\( 2 \\)  
===========  =========  


.. admonition:: Highlight box

   This environment is used to highlight something
   
   .. raw:: html
   
           $$ E = mc^2 $$




.. _subsubsec:ex:

URLs
----

Testing of URLs: hpl's home page `hpl <https://folk.uio.no/hpl>`__, or
the entire URL if desired, `<https://folk.uio.no/hpl>`_.  Here is a
plain file link `<testdoc.do.txt>`_, or `<testdoc.do.txt>`_, or
`<testdoc.do.txt>`_ or `<testdoc.do.txt>`_ or `a link with
newline <testdoc.do.txt>`__. Can test spaces with the link with word
too: `hpl <https://folk.uio.no/hpl>`__ or `hpl <https://folk.uio.no/hpl>`__. Also ``file:///`` works: `link to a
file <file:///home/hpl/vc/doconce/doc/demos/manual/manual.html>`__ is
fine to have. Moreover, "loose" URLs work, i.e., no quotes, just
the plain URL as in `<https://folk.uio.no/hpl>`_, if followed by space, comma,
colon, semi-colon, question mark, exclamation mark, but not a period
(which gets confused with the periods inside the URL).

Mail addresses can also be used: `hpl@simula.no <mailto:hpl@simula.no>`__, or just a `mail link <mailto:hpl@simula.no>`__, or a raw `<mailto:hpl@simula.no>`_.

Here are some tough tests of URLs, especially for the ``latex`` format:
`Newton-Cotes <https://en.wikipedia.org/wiki/Newton%E2%80%93Cotes_formulas>`__ formulas
and a `good book <https://www.springer.com/mathematics/computational+science+%26+engineering/book/978-3-642-23098-1>`__. Need to test
Newton-Cotes with percentage in URL too:
`<https://en.wikipedia.org/wiki/Newton%E2%80%93Cotes_formulas>`_
and `<https://en.wikipedia.org/wiki/Newton-Cotes#Open_Newton.E2.80.93Cotes_formulae>`_ which has a shebang.

For the ``--device=paper`` option it is important to test that URLs with
monospace font link text get a footnote
(unless the ``--latex_no_program_footnotelink``
is used), as in this reference to
`decay_mod <https://github.com/hplgit/INF5620/tree/gh-pages/src/decay/experiments/decay_mod.py>`__, `ball1.py <https://tinyurl.com/pwyasaa/formulas.ball1.py>`__,
and `ball2.py <https://tinyurl.com/pwyasaa/formulas.ball2.py>`__.

.. Comments should be inserted outside paragraphs (because in the rst

.. format extra blanks make a paragraph break).

.. Note that when there is no https: or file:, it can be a file link

.. if the link name is URL, url, "URL", or "url". Such files should,

.. if rst output is desired, but placed in a ``_static*`` folder.

More tough tests: repeated URLs whose footnotes when using the
``--device=paper`` option must be correct. We have
`google <https://google.com>`__, `google <https://google.com>`__, and
`google <https://google.com>`__, which should result in exactly three
footnotes.

.. !split and check if these extra words are included properly in the comment

LaTeX Mathematics
=================

Here is an equation without label using backslash-bracket environment

.. raw:: html

        $$ a = b + c $$

or with number and label, as in Equation (my:eq1), using the equation environment

.. raw:: html

        $$
        \begin{equation}
        {\partial u\over\partial t} = \nabla^2 u \label{my:eq1}
        \end{equation}
        $$

We can refer to this equation by Equation (my:eq1).

Here is a system without equation numbers, using the align-asterisk environment

.. raw:: html

        $$
        \begin{align*}
        \pmb{a} &= \pmb{q}\times\pmb{n} \\ 
        b &= \nabla^2 u + \nabla^4 v
        \end{align*}
        $$

More mathematical typesetting is demonstrated in the coming exercises.

Below, we have `Problem 2: Flip a Coin`_ and `Project 4: Compute a Probability`_,
as well as `Project 5: Explore Distributions of Random Circles`_ and `Project 11: References in a headings do not work well in rst`_, and in
between there we have `Exercise 10: Make references to projects and problems`_.

Exercises
=========

.. --- begin exercise ---

.. _demo:ex:1:

Problem 2: Flip a Coin
----------------------

.. keywords = random numbers; Monte Carlo simulation; ipynb

.. Torture tests

**a)**
Make a program that simulates flipping a coin \\( N \\) times.
Print out "tail" or "head" for each flip and
let the program count the number of heads.

.. --- begin hint in exercise ---

**Hint 1.**
Use ``r = random.random()`` and define head as ``r <= 0.5``.

.. --- end hint in exercise ---

.. --- begin hint in exercise ---

**Hint 2.**
Draw an integer among \\( \{1,2\} \\) with
``r = random.randint(1,2)`` and define head when ``r`` is 1.

.. --- end hint in exercise ---

.. --- begin answer of exercise ---

**Answer.**
If the ``random.random()`` function returns a number \\( <1/2 \\), let it be
head, otherwise tail. Repeat this \\( N \\) number of times.

.. --- end answer of exercise ---

.. --- begin solution of exercise ---

**Solution.**::

        import sys, random
        N = int(sys.argv[1])
        heads = 0
        for i in range(N):
            r = random.random()
            if r <= 0.5:
                heads += 1
        print('Flipping a coin %d times gave %d heads' % (N, heads))

.. --- end solution of exercise ---

**b)**
Vectorize the code in a) using boolean indexing.

Vectorized code can be written in many ways.
Sometimes the code is less intuitive, sometimes not.
At least there is not much to find in the section `Section 1`_.

**c)**
Vectorize the code in a) using ``numpy.sum``.

.. --- begin answer of exercise ---

**Answer.**
``np.sum(np.where(r <= 0.5, 1, 0))`` or ``np.sum(r <= 0.5)``.

.. --- end answer of exercise ---

In this latter subexercise, we have an
example where the code is easy to read.

My remarks
~~~~~~~~~~

Remarks with such a subsubsection is treated as more text
after the last subexercise. Test a list too:

1. Mark 1.

2. Mark 2.

Filenames: ``flip_coin.py``, ``flip_coin.pdf``.

.. Closing remarks for this Problem

Remarks          (1)
~~~~~~~~~~~~~~~~~~~~

These are the exercise remarks, appearing at the very end.

.. solution files: mysol.txt, mysol_flip_coin.py, yet_another.file

.. --- end exercise ---

Not an exercise
---------------

Should be possible to stick a normal section in the middle of many
exercises.

.. --- begin exercise ---

.. _my:exer1:

Exercise 3: Test of plain text exercise
---------------------------------------

Very short exercise. What is the capital
of Norway?
Filename: ``myexer1``.

.. --- end exercise ---

.. --- begin exercise ---

.. _demo:ex:2:

Project 4: Compute a Probability
--------------------------------

.. Minimalistic exercise

What is the probability of getting a number between 0.5 and 0.6 when
drawing uniformly distributed random numbers from the interval \\( [0,1) \\)?

At the end we have a list because that caused problems in LaTeX
in previous DocOnce versions:

1. item1

2. item2

.. --- begin hint in exercise ---

**Hint.**
To answer this question empirically, let a program
draw \\( N \\) such random numbers using Python's standard ``random`` module,
count how many of them, \\( M \\), that fall in the interval \\( (0.5,0.6) \\), and
compute the probability as \\( M/N \\).

.. --- end hint in exercise ---

.. --- end exercise ---

.. --- begin exercise ---

.. _proj:circle1:

Project 5: Explore Distributions of Random Circles
--------------------------------------------------

.. keywords = ipynb

The formula for a circle is given by

.. raw:: html

        $$
        \begin{align}
        x &= x_0 + R\cos 2\pi t,
        \label{circle:x}\\ 
        y &= y_0 + R\sin 2\pi t,
        \label{circle:y}
        \end{align}
        $$

where \\( R \\) is the radius of the circle, \\( (x_0,y_0) \\) is the
center point, and \\( t \\) is a parameter in the unit interval \\( [0,1] \\).
For any \\( t \\), \\( (x,y) \\) computed from Equations (circle:x)-(circle:y)
is a point on the circle.
The formula can be used to generate ``n`` points on a circle::

        import numpy as np
        
        def circle(R, x0, y0, n=501):
            t = np.linspace(0, 1, n)
            x = x0 + R*np.cos(2*np.pi*t)
            y = y0 + R*np.sin(2*np.pi*t)
            return x, y
        
        x, y = circle(2.0, 0, 0)

.. Often in an exercise we have some comments about the solution

.. which we normally want to keep where they are.

The goal of this project is to draw \\( N \\) circles with random
center and radius. Plot each circle using the ``circle`` function
above.

**a)**
Let \\( R \\) be normally distributed and \\( (x_0,y_0) \\) uniformly distributed.

.. --- begin hint in exercise ---

**Hint.**
Use the ``numpy.random`` module to draw the
\\( x_0 \\), \\( y_0 \\), and \\( R \\) quantities.

.. --- end hint in exercise ---

.. --- begin answer of exercise ---

**Answer.**
Here goes the short answer to part a).

.. --- end answer of exercise ---

.. --- begin solution of exercise ---

**Solution.**
Here goes a full solution to part a).

.. --- end solution of exercise ---

**b)**
Let \\( R \\) be uniformly distributed and \\( (x_0,y_0) \\) normally distributed.
Filename: ``norm``.

**c)**
Let \\( R \\) and \\( (x_0,y_0) \\) be normally distributed.

Filename: ``circles``.

.. Closing remarks for this Project

Remarks          (2)
~~~~~~~~~~~~~~~~~~~~

At the very end of the exercise it may be appropriate to summarize
and give some perspectives.

.. --- end exercise ---

.. --- begin exercise ---

.. _exer:dist:

Exercise 6: Determine some Distance
-----------------------------------

Intro to this exercise. Questions are in subexercises below.

.. --- begin solution of exercise ---

**Solution.**
Here goes a full solution of the whole exercise.
With some math \\( a=b \\) in this solution

.. raw:: html

        $$ \hbox{math in solution: } a = b $$

And code ``a=b`` in this solution::

        a = b  # code in solution

End of solution is here.

.. --- end solution of exercise ---

**a)**
Subexercises are numbered a), b), etc.

.. --- begin hint in exercise ---

**Hint 1.**
First hint to subexercise a).
With math \\( a=b \\) in hint

.. raw:: html

        $$ a=b. $$

And with code (in plain verbatim) returning \\( x+1 \\) in hint::

        def func(x):
            return x + 1  # with code in hint

.. --- end hint in exercise ---

.. --- begin hint in exercise ---

**Hint 2.**
Second hint to subexercise a).

Test list in hint:

1. item1

2. item2

.. --- end hint in exercise ---

Filename: ``subexer_a.pdf``.

.. --- begin answer of exercise ---

**Answer.**
Short answer to subexercise a).
With math in answer: \\( a=b \\).

.. --- end answer of exercise ---

**b)**
Here goes the text for subexercise b).

Some math \\( \cos^2 x + \sin^2 x = 1 \\) written one a single line

.. raw:: html

        $$ \cos^2 x + \sin^2 x = 1 \thinspace .$$

.. --- begin hint in exercise ---

**Hint.**
A hint for this subexercise.

.. --- end hint in exercise ---

Filename: ``subexer_b.pdf``.

.. --- begin solution of exercise ---

**Solution.**
Here goes the solution of this subexercise.

.. --- end solution of exercise ---

.. No meaning in this weired test example:

The text here belongs to the main (intro) part of the exercise. Need
closing remarks to have text after subexercises.

Test list in exercise:

1. item1

2. item2

.. Closing remarks for this Exercise

Remarks          (3)
~~~~~~~~~~~~~~~~~~~~

Some final closing remarks, e.g., summarizing the main findings
and their implications in other problems can be made. These
remarks will appear at the end of the typeset exercise.

.. --- end exercise ---

.. --- begin exercise ---

Some exercise without the "Exercise:" prefix
--------------------------------------------

.. Another minimalistic exercise

Just some text. And some math saying that \\( e^0=1 \\) on a single line,
to test that math block insertion is correct

.. raw:: html

        $$ \exp{(0)} = 1 $$

And a test that the code ``lambda x: x+2`` is correctly placed here::

        lambda x: x+2

.. Have some comments at the end of the exercise to see that

.. the Filename: ... is written correctly.

.. --- end exercise ---

.. --- begin exercise ---

.. _sec:this:exer:de:

Exercise 8: Solution of differential equation
---------------------------------------------



.. begin quiz

Given

.. raw:: html

        $$ \frac{dy}{dx} = -y(x),\quad y(0)=1 $$

What is the solution of this equation?


**Choice A:** \\( y=e^{-y} \\)

:abbr:`? (Right!)`

**Choice B:** \\( y=e^{y} \\)

:abbr:`? (Wrong!)` :abbr:`# (Almost, but the sign is wrong (note the minus!).)`

**Choice C:** Code::

        from math import exp
        def f(x):
            return exp(x)

:abbr:`? (Wrong!)` :abbr:`# (Ooops, forgot a minus: exp(-x), otherwise this Python code must be considered as a good answer. It is more natural, though, to write the solution to the problem in mathematical notation  .. raw:: html          $$ y(x) = e^{-y}.$$)`

**Choice D:** The solution cannot be found because there is a derivative in the equation.

:abbr:`? (Wrong!)` :abbr:`# (Equations with derivatives can be solved; they are termed *differential equations*.)`

**Choice E:** The equation is meaningless: an equation must be an equation
for \\( x \\) or \\( y \\), not a function \\( y(x) \\).

:abbr:`? (Wrong!)` :abbr:`# (Equations where the unknown is a function, as \\( y(x) \\) here, are called *differential equations*, and are solved by special techniques.)`

.. end quiz



.. --- end exercise ---

.. --- begin exercise ---

Example 9: Just an example
--------------------------

.. This example needs the --examples_as_exercises option, otherwise

.. it is just typeset as it is written.

**a)**
What is the capital of Norway?

**Answer.**
Oslo.

.. --- end exercise ---

Here goes another section
=========================

With some text, before we continue with exercises.

More Exercises
==============

.. --- begin exercise ---

.. _exer:some:formula:

Exercise 10: Make references to projects and problems
-----------------------------------------------------

.. Test comments not at the end only

Pick a statement from `Project 5: Explore Distributions of Random Circles`_ or `Problem 2: Flip a Coin`_
and verify it.

Test list at the end of an exercise without other elements (like subexercise,
hint, etc.):

1. item1

2. item2

Filename: ``verify_formula.py``.

.. --- end exercise ---

.. --- begin exercise ---

.. _exer:you:

Project 11: References in a headings do not work well in rst
------------------------------------------------------------

Refer to the previous exercise as `Exercise 10: Make references to projects and problems`_,
the two before that as `Project 4: Compute a Probability`_ and `Project 5: Explore Distributions of Random Circles`_,
and this one as `Project 11: References in a headings do not work well in rst`_.
Filename: ``selc_composed.pdf``.

.. --- end exercise ---

References
==========

.. [Ref01]
   **H. P. Langtangen and G. Pedersen**. Propagation of Large Destructive Waves,
   *International Journal of Applied Mechanics and Engineering*,
   7(1),
   pp. 187-204,


.. [Ref02]
   **H. P. Langtangen, K.-A. Mardal and R. Winther**. Numerical Methods for Incompressible Viscous Flow,
   *Advances in Water Resources*,
   25,
   pp. 1125-1146,


.. [Ref03]
   **H. P. Langtangen**. Numerical Solution of First Passage Problems in Random Vibrations,
   *SIAM Journal of Scientific and Statistical Computing*,
   15,
   pp. 997-996,


.. [Ref04]
   **K.-A. Mardal, G. W. Zumbusch and H. P. Langtangen**. Software Tools for Multigrid Methods,
   Advanced Topics in Computational Partial Differential Equations -- Numerical Methods and Diffpack Programming,
   edited by **H. P. Langtangen and A. Tveito**,
   Springer,
   2003,
   Edited book,
   `\urlhttp://some.where.org <\urlhttp://some.where.org>`_.

.. [Ref05]
   **H. P. Langtangen**. The FEMDEQS Program System,
   *Department of Mathematics, University of Oslo*,
   `http://www.math.uio.no/old/days/hpl/femdeqs.pdf <http://www.math.uio.no/old/days/hpl/femdeqs.pdf>`_,


.. [Ref06]
   **H. P. Langtangen**. Stochastic Breakthrough Time Analysis of an Enhanced Oil Recovery Process,
   *SIAM Journal on Scientific Computing*,
   13,
   pp. 1394-1417,


.. [Ref07]
   **M. Mortensen, H. P. Langtangen and G. N. Wells**. A FEniCS-Based Programming Framework for Modeling Turbulent Flow by the Reynolds-Averaged Navier-Stokes Equations,
   *Advances in Water Resources*,
   34(9),
   `doi: 10.1016/j.advwatres.2011.02.013 <https://dx.doi.org/10.1016/j.advwatres.2011.02.013>`__,


.. [Ref08]
   **S. Glimsdal, G. Pedersen, K. Atakan, C. B. Harbitz, H. P. Langtangen and F. L\ovholt**. Propagation of the Dec. |nbsp| 26, 2004 Indian Ocean Tsunami: Effects of Dispersion and Source Characteristics,
   *International Journal of Fluid Mechanics Research*,
   33(1),
   pp. 15-43,


.. [Ref09]
   **S. Rahman, J. Gorman, C. H. W. Barnes, D. A. Williams and H. P. Langtangen**. Numerical Investigation of a Piezoelectric Surface Acoustic Wave Interaction With a One-Dimensional Channel,
   *Physical Review B: Condensed Matter and Materials Physics*,
   74,
   2006,


.. [Ref10]
   **J. B. Haga, H. Osnes and H. P. Langtangen**. On the Causes of Pressure Oscillations in Low-Permeable and Low-Compressible Porous Media,
   *International Journal of Analytical and Numerical Methods in Geomechanics*,
   `doi: 10.1002/nag.1062 <https://dx.doi.org/10.1002/nag.1062>`__,
   2011,
   `http://onlinelibrary.wiley.com/doi/10.1002/nag.1062/abstract <http://onlinelibrary.wiley.com/doi/10.1002/nag.1062/abstract>`_.

.. [Ref11]
   **H. P. Langtangen**. *Computational Partial Differential Equations - Numerical Methods and Diffpack Programming*,
   second edition,
   *Texts in Computational Science and Engineering*,
   Springer,


.. [Ref12]
   **H. P. Langtangen**. *Python Scripting for Computational Science*,
   third edition,
   *Texts in Computational Science and Engineering*,
   Springer,


.. [Ref13]
   **H. P. Langtangen and G. Pedersen**. Finite Elements for the Boussinesq Wave Equations,
   Waves and Non-linear Processes in Hydrodynamics,
   edited by **J. Grue, B. Gjevik and J. E. Weber**,
   Kluwer Academic Publishers,
   pp. pp. 117-126,
   1995,
   `http://www.amazon.ca/Waves-Nonlinear-Processes-Hydrodynamics-John/dp/0792340310 <http://www.amazon.ca/Waves-Nonlinear-Processes-Hydrodynamics-John/dp/0792340310>`_.

.. [Ref14]
   **H. P. Langtangen**. *A Primer on Scientific Programming With Python*,
   third edition,
   *Texts in Computational Science and Engineering*,
   Springer,


.. [Ref15]
   **P. V. Jeberg, H. P. Langtangen and C. B. Terp**. Optimization With Diffpack: Practical Example From Welding,
   *Simula Research Laboratory*,
   Internal report,


.. [Ref16]
   **H. P. Langtangen**. Computational Methods for Two-Phase Flow in Oil Reservoirs,
   Ph.D. Thesis,
   Mechanics Division, Department of Mathematics, University of Oslo,
   1989,
   Dr. |nbsp| Scient. |nbsp| thesis..

.. [Ref17]
   **H. P. Langtangen**. Computational Modeling of Huge Tsunamis From Asteroid Impacts,
   Invited keynote lecture at the \emphInternational conference on Computational Science 2007 (ICCS'07), Beijing, China,


.. [Ref18]
   **H. P. Langtangen**. Solution of the Navier-Stokes Equations With the Finite Element Method in Two and Three Dimensions,
   M.Sc. Thesis,
   Mechanics Division, Department of Mathematics, University of Oslo,
   1985,
   Cand.Scient. thesis.

.. [Ref19]
   **H. P. Langtangen and A. Tveito**. Numerical Methods in Continuum Mechanics,
   *Center for Industrial Research*,
   1991,
   Lecture notes for a course (ME-IN 324). 286 pages..

.. [Ref20]
   **H. P. Langtangen**. Diffpack: Software for Partial Differential Equations,
   Proceedings of the Second Annual Object-Oriented Numerics Conference (OON-SKI'94), Sunriver, Oregon, USA,
   edited by **A. Vermeulen**,


.. _app1:

Appendix: Just for testing; part I
==================================

This is the first appendix.

A subsection within an appendix
-------------------------------

Some text.

.. _app2:

Appendix: Just for testing; part II
===================================

This is more stuff for an appendix.

Appendix: Testing identical titles          (1)
-----------------------------------------------

Without label.

.. _test:title:id1:

Appendix: Testing identical titles          (2)
-----------------------------------------------

With label.

.. _test:title:id2:

Appendix: Testing identical titles          (3)
-----------------------------------------------

What about inserting a quiz?



.. !split
Test of quizzes
---------------.. begin quiz



**Fundamental test:** What is the capital of Norway?


**Answer 1:** Stockholm

:abbr:`? (Wrong!)` :abbr:`# (Stockholm is the capital of Sweden.)`

**Answer 2:** London

:abbr:`? (Wrong!)`

**Answer 3:** Oslo

:abbr:`? (Right!)`

**Choice D:** Bergen

:abbr:`? (Wrong!)` :abbr:`# (Those from Bergen would claim so, but nobody else.)`

.. end quiz



Appendix: Testing identical titles          (4)
-----------------------------------------------

Without label.


.. admonition:: Tip

   Here is a tip or hint box, typeset as a notice box.




Need a lot of text to surround the summary box.
Version control systems allow you to record the history of files
and share files among several computers and collaborators in a
professional way. File changes on one computer are updated or
merged with changes on another computer. Especially when working
with programs or technical reports it is essential
to have changes documented and to
ensure that every computer and person involved in the project
have the latest updates of the files.
Greg Wilson' excellent `Script for Introduction to Version Control <https://software-carpentry.org/2010/07/script-for-introduction-to-version-control/>`__ provides a more detailed motivation why you will benefit greatly
from using version control systems.


.. admonition:: Summary

   **Bold remark:** Make some text with this summary.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.
   Much testing in this document, otherwise stupid content.




Projects that you want to share among several computers or project
workers are today most conveniently stored at some web site "in the
cloud" and updated through communication with that site. I strongly
recommend you to use such sites for all serious programming and
scientific writing work - and all other important files.

The simplest services for hosting project files are `Dropbox <https://dropbox.com>`__ and `Google Drive <https://drive.google.com>`__.
It is very easy to get started with these systems, and they allow you
to share files among laptops and mobile units with as many users as
you want. The systems offer a kind of version control in that the
files are stored frequently (several times per minute), and you can go
back to previous versions for the last 30 days. However, it is
challenging  to find the right version from the past when there are
so many of them.

More seriously, when several people may edit files simultaneously, it
can be difficult detect who did what when, roll back to previous
versions, and to manually merge the edits when these are
incompatible. Then one needs more sophisticated tools than Dropbox or
Google Drive: project hosting services with true version control
systems.  The following text aims at providing you with the minimum
information to started with such systems. Numerous other tutorials
contain more comprehensive material and in-depth explanations of the
concepts and tools.

The idea with project hosting services is that you have the files
associated with a project in the cloud. Many people may share these
files.  Every time you want to work on the project you explicitly
update your version of the files, edit the files as you like, and
synchronize the files with the "master version" at the site where the
project is hosted.  If you at some point need to go back to a
version of the files at some particular point in the past,
this is an easy operation. You can also use tools to see
what various people have done with the files in the various versions.

All these services are very similar. Below we describe how you get
started with Bitbucket, GitHub, and Googlecode. Launchpad works very
similarly to the latter three. All the project hosting services have
excellent introductions available at their web sites, but the recipes
below are much shorter and aim at getting you started as quickly as
possible by concentrating on the most important need-to-know steps.
The Git tutorials we refer to later in this document contain more
detailed information and constitute of course very valuable readings
when you use version control systems every day. The point now is
to get started.

Appendix: Testing inline comments
---------------------------------

.. Names can be [ A-Za-z0-9_'+-]+

Projects that you want to share among several computers or project
workers are today most conveniently stored at some web site "in the
cloud" and updated through communication with that
site. **(**hpl's semi opinion 1**: not sure if in the cloud is
understood by
all.**) I strongly recommend you to use such sites for all serious
programming and scientific writing work - and all other important
files.

The simplest services for hosting project files is Dropbox. **(**mp 2**: Simply go to `<https://dropbox.com>`_ and watch the video. It explains
how files, like ``myfile.py``, perhaps containing much math, like
\\( \partial u/\partial t \\), are easily communicated between machines.**) It
is very easy to get started with Dropbox, and it allows you to share
files among **(**hpl 3**: laptops and mobile units -> computers, tablets,
and phones**).

.. Test horizontal rule

---------

.. Coments for editing

Firstcolor{red}{(**add 4**: ,}) consider a quantity \\( Q \\). **(**edit 5**: To this end, -> We note that**)
\\( Q>0 \\), because **(**del 6**: a**) negative **(**edit 7**: quantity is -> quantities
are**) **(**del 8**: just**) negative. **(**add 9**: This comes as no surprise.**)

.. Test tailored latex figure references with page number

Let us refer to Figure `fig:impact`_ again.

Test references in a list:

 * `Section 1`_

 * `Subsection 1`_

 * `fig:impact`_

Appendix: Testing headings ending with ``verbatim inline``
----------------------------------------------------------

The point here is to test 1) ``verbatim`` code in headings, and 2)
ending a heading with verbatim code as this triggers a special
case in LaTeX.

We also test mdash---used as alternative to hyphen without spaces around,
or in quotes:


..

    *Fun is fun*.---Unknown.



The ndash should also be tested - as in the Hanson - Nilson equations
on page 277 - 278.

And finally, what about admons, quotes, and boxes? They are tested
in a separate document: ``admon.do.txt``.

.. [#example-of-the-third-footnote] Not much to add here, but the footnote
   is at the end with only one newline.
