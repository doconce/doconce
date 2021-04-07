.. raw:: html

        <script type="text/javascript">
        $(document).ready(function() {
            $("a[href^='http']").attr('target','_blank');
        });
        </script>

.. Automatically generated Sphinx-extended reStructuredText file from DocOnce source
   (https://github.com/doconce/doconce/)

.. |nbsp| unicode:: 0xA0
   :trim:

.. Document title:

A Document for Testing DocOnce
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:Authors: Hans Petter Langtangen (hpl at simula.no), Kaare Dump, A. Dummy Author, I. S. Overworked and Outburned, J. Doe (j_doe at cyberspace.com)
:Date: Jan 32, 2100

The format of this document is
sphinx

*Abstract.* This is a document with many test constructions for doconce syntax.
It was used heavily for the development and kept for testing
numerous constructions, also special and less common cases.

And exactly for test purposes we have an extra line here, which
is part of the abstract.

.. Cannot demonstrate chapter headings since abstract and chapter

.. are mutually exclusive in LaTeX

.. !split

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



Here are two references. Equation |nbsp| :eq:`my:eq1` is fine. Eq. |nbsp| :eq:`my:eq1` too.
Even Equation :eq:`my:eq1` without the tilde.
This equation appears in another part if this document is split.

.. _subsec1:

Subsection 1
------------

.. index:: somefunc function

.. Refer to section/appendix etc. at the beginning of the line

.. and other special fix situations for HTML.

More text, with a reference back to
the section :ref:`sec1` and :ref:`subsec1`, and further to the
the sections :ref:`subsec1` and :ref:`subsubsec:ex`, which
encourages you to do the tasks in :ref:`demo:ex:1` and :ref:`exer:some:formula`.
 :ref:`app1` and :ref:`app2` are also nice elements.

Test Section reference at beginning of line and after a sentence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The section :ref:`subsec1` is fine.
The section :ref:`subsubsec:ex` too.

.. sphinx code-blocks: pycod=python cod=fortran cppcod=c++ sys=console

Computer code
~~~~~~~~~~~~~

Let's do some copying from files too. First from subroutine up to the very end,

.. code-block:: fortran

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

and then just the subroutine,

.. code-block:: fortran

          subroutine test()
          integer i
          real*8 r
          r = 0
          do i = 1, i
             r = r + i
          end do
          return

and finally the complete file with a plain text verbatim environment
(``envir=ccq``):

.. code-block:: text

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

Testing other code environments. First Python:

.. code-block:: doconce

    !bc pycod
    def f(x):
        return x+1
    !ec

which gets rendered as

.. code-block:: python

    def f(x):
        return x+1

Test paragraph and subsubsection headings before
before code.

**Paragraph heading before code.**

.. code-block:: python

    import sys
    sys.path.insert(0, os.pardir)

Subsubsection heading before code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def h(z):
        return z+1

Now a complete program to be shown via Python Online Tutorial:

.. raw:: html

    <iframe width="950" height="500" frameborder="0"
            src="https://pythontutor.com/iframe-embed.html#code=class+Line%3A%0A++++def+__init__%28self%2C+a%2C+b%29%3A%0A++++++++self.a%2C+self.b+%3D+a%2C+b%0A%0A++++def+__call__%28self%2C+x%29%3A%0A++++++++a%2C+b+%3D+self.a%2C+self.b%0A++++++++return+a%2Ax+%2B+b%0A%0Aline+%3D+Line%282%2C+1%29%0Ay+%3D+line%28x%3D3%29%0Aprint%28y%29&py=2&curInstr=0&cumulative=false">
    </iframe>

Another complete program to be typeset as a sage cell:

.. code-block:: text

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

Then Cython (with -h option so it is hidden in html/sphinx):

.. container:: toggle

    .. container:: header

        **Show/Hide Code**

    .. code-block:: cython

        cpdef f(double x):
            return x + 1

Standard Python shell sessions:

.. code-block:: python

    >>> from numpy import linspace, sin
    >>> # Some comment
    >>> x = linspace(0, 2, 11)
    >>> y = sin(x)
    >>> y[0]

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(x, y)

Similar IPython sessions:

.. code-block:: ipy

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

Here is the interactive session again, but with ``pyshell-t``.

.. code-block:: python

    >>> from numpy import linspace, sin
    >>> # Some comment
    >>> x = linspace(0, 2, 11)
    >>> y = sin(x)
    >>> y[0]

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(x, y)

.. This one tests a + sign before a code environment

C++:

.. code-block:: c++

    #include <iostream>
    
    int main()
    {
       std::cout << "Sample output" << std::endl;
       return 0
    }

.. The next should get correctly typset in sphinx (cod is fcod)

.. It also tests emoji before code

And a little bit of Fortran: :dizzy_face:

.. code-block:: doconce

    !bc cod
          subroutine midpt(x, length, a, b)
          real*8 a, b, x
          x = (a + b)/2
          length = b - a
          return
          end
    !ec

which then is typeset as

.. code-block:: fortran

          subroutine midpt(x, length, a, b)
          real*8 a, b, x
          x = (a + b)/2
          length = b - a
          return
          end

HTML:

.. code-block:: html

    <table>
    <tr><td>Column 1</td><td>Column 2</td></tr>
    <tr><td>0.67526 </td><td>0.92871 </td></tr>
    <!-- comment -->
    </table>

But inline HTML code is also important, like text that starts with
``<a href="`` (which can destroy the following text if not properly
quoted).

Matlab with comments requires special typesetting:

.. code-block:: matlab

    % Comment on the beginning of the line can be escaped by %%
    if a > b
      % Indented comment needs this trick
      c = a + b
    end

And here is a system call:

.. code-block:: console

    Terminal> mkdir test
    Terminal> cd test
    Terminal> myprog -f
    output1
    output2

Any valid pygments lexer/language name can appear to, e.g.,

.. code-block:: doconce

    !bc restructuredtext
    =======
    Heading
    =======
    
    Some text.
    !ec

results in

.. code-block:: restructuredtext

    =======
    Heading
    =======
    
    Some text.

.. Here goes hidden code.

.. Python can be treated by some formats, Fortran is always out.

Finally, ``!bc do`` supports highlighting of DocOnce source:

.. code-block:: doconce

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
    
    Formulas can be inline, as in $\nabla\cdot\boldsymbol{u} = 0$, or typeset
    as equations:
    
    !bt
    \begin{align*}
    \nabla\cdot\boldsymbol{u} &= 0,\\ 
    \boldsymbol{u} &= \nabla\phi .
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
format sphinx.
Here is some **red color** and an attempt to write **with
green color containing a linebreak

| code.** Some formats will only display 
| this correctly when ``html`` 
| is the output format.

But here some more running text is added which is not part of
the previous blocks with line breaks.

Running OS commands
~~~~~~~~~~~~~~~~~~~

.. code-block:: console

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

 * even with math :math:`\nabla^2u` [#math1]_

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
   in |nbsp| :math:`7.4/5.5\approx 1.345` |nbsp| s.  Also check that a |nbsp| `link <https://google.com>`__ |nbsp| is
   not broken across lines (drag the browser window to test this).
   (On the other hand, the tilde is used in
   computer code, e.g., as in ``[~x for x in y]`` or in ``y=~x``, and should
   of course remain a tilde in those contexts.)




.. _subsec:ex:

Subsection 2: Testing figures
-----------------------------

.. index:: figures

Test of figures. In particular we refer to Figure :ref:`fig:impact` in which
there is a flow.

.. _fig:impact:

.. figure:: testfigs/wave1D.png
   :width: 200

   Visualization **of** a *wave*

Figures without captions are allowed and will be inlined.

.. figure:: testfigs/wave1D.png
   :width: 200

.. index:: movies

.. Test multi-line caption in figure with sidecap=True

Here is figure :ref:`myfig` with a long (illegal) multi-line caption
containing inline verbatim text:

.. _myfig:

.. figure:: testfigs/wave1D.png
   :width: 500

   A long caption spanning several lines and containing verbatim words like ``my_file_v1`` and ``my_file_v2`` as well as math with subscript as in :math:`t_{i+1}`

.. Must be a blank line after MOVIE or FIGURE to detect this problem

Test URL as figure name:

.. figure:: https://raw.github.com/doconce/doconce/master/doc/src/blog/f_plot.png
   :width: 500

Test SVG figure:

.. figure:: https://openclipart.org/people/jpneok/junebug.svg
   :width: 200

.. Test wikimedia type of files that otherwise reside in subdirs

**Remark.**
Movies are tested in separate file ``movies.do.txt``.

.. Somewhat challenging heading with latex math, \t, \n, ? and parenthesis

.. _decay:sec:theta:

The :math:`\theta` parameter (not :math:`\nabla`?)
--------------------------------------------------

Functions do not always need to be advanced, here is one
involving :math:`\theta`:

.. code-block:: text

    def f(theta):
        return theta**2

**More on :math:`\theta`.**
Here is more text following headline with math.

Newcommands must also be tested in this test report:
:math:`\frac{1}{2}`, :math:`{1/2}`, :math:`\pmb{x}`, :math:`\frac{Du}{dt}`,
both inline and in block:

.. math::
        
        \frac{Du}{dt} = 0\nonumber
        

.. math::
   :label: _auto1

          
        \frac{1}{2} = {1/2}
        
        

.. math::
   :label: _auto2

          
        \frac{1}{2}\pmb{x} = \pmb{n}
        
        

Or with align with label and numbers:

.. math::
   :label: aligneq1

        
        \frac{Du}{dt} = 0
        
        

.. math::
   :label: _auto3

          
        \frac{1}{2} = {1/2}
        
        

.. math::
   :label: aligneq2

          
        \frac{1}{2}\pmb{x} = \pmb{n}
        
        

Sphinx makes a fix here and splits align into multiple equation
environments.

Custom Environments
-------------------

Here is an attempt to create a theorem environment via Mako
(for counting theorems) and comment lines to help replacing lines in
the ``.tex`` by proper begin-end LaTeX environments for theorems.
Should look nice in most formats!

.. begin theorem

**Theorem 5.**
Let :math:`a=1` and :math:`b=2`. Then :math:`c=3`.

.. end theorem

.. begin proof

**Proof.**
Since :math:`c=a+b`, the result follows from straightforward addition.
:math:`\Diamond`

.. end proof

As we see, the proof of Theorem 5 is a modest
achievement.

.. _subsec:table:

Tables
------

.. index:: test index with verbatim text which is possible

.. index:: test two (separate) verbatim expressions which is also possible

.. index::
   single: index with; subindex

.. index:: boldface word in index

.. index:: index with boldface word

.. index::
   single: index with; boldface word in subentry

.. index::
   single: double boldface word;  boldface word in subentry too

.. index with comma could fool sphinx

.. index::
   single: index, with comma, and one more

Let us take this table from the manual:

====  ========  ============  
time  velocity  acceleration  
====  ========  ============  
0.0     1.4186         -5.01  
2.0   1.376512        11.919  
4.0     1.1E+1     14.717624  
====  ========  ============  

The DocOnce source code reads

.. code-block:: text

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
:math:`i`  :math:`h_i`  :math:`\bar T_i`  ``L_i``  
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
exact  ``v_1``  :math:`a_i` + ``v_2``  ``verb_3_``  
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
   :math:`S`         command      
===============  ===============  
$ ||a_0|| $      ``norm|length``  
:math:`x\cap y`          ``x|y``  
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

====================================  ==========================================================  ==========================================================  
                                                                                                                                                              
====================================  ==========================================================  ==========================================================  
       :math:`\mathcal{L}=0`          `080 <../doc/src/manual/mov/wave_frames/frame_0080.png>`__  `085 <../doc/src/manual/mov/wave_frames/frame_0085.png>`__  
            :math:`a=b`               `090 <../doc/src/manual/mov/wave_frames/frame_0090.png>`__  `095 <../doc/src/manual/mov/wave_frames/frame_0095.png>`__  
:math:`\nabla\cdot\boldsymbol{u} =0`  `100 <../doc/src/manual/mov/wave_frames/frame_0100.png>`__  `105 <../doc/src/manual/mov/wave_frames/frame_0105.png>`__  
====================================  ==========================================================  ==========================================================  

A test of verbatim words in heading with subscript :math:`a_i`: ``my_file_v1`` and ``my_file_v2``
-------------------------------------------------------------------------------------------------

**Paragraph with verbatim and math: ``my_file_v1.py`` and ``my_file_v2.py`` define some math :math:`a_{i-1}`.**
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

.. Note: substitutions must not occur inside verbatim, just in ordinary text.

.. code-block:: text

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

The example in the section :ref:`ex:test:1p1` demonstrates how to write a test function.
That is, a special test function for a function ``add`` appears in
the example in the section :ref:`ex:test:1p1`.

.. _ex:test:1p1:

Example 1: A test function
--------------------------

Suppose we want to write a test function for checking the
implementation of a Python function for addition.

.. code-block:: python

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

.. math::
         1 + 1 = 2 

or in tabular form:

===========  =========  
  Problem      Result   
===========  =========  
:math:`1+1`  :math:`2`  
===========  =========  


.. admonition:: Highlight box

   This environment is used to highlight something:
   
   .. math::
            E = mc^2




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

.. !split

LaTeX Mathematics
=================

Here is an equation without label using backslash-bracket environment:

.. math::
         a = b + c 

or with number and label, as in :eq:`my:eq1`, using the equation environment:

.. math::
   :label: my:eq1

        
        {\partial u\over\partial t} = \nabla^2 u 
        

We can refer to this equation by :eq:`my:eq1`.

Here is a system without equation numbers, using the align-asterisk environment:

.. math::
        \begin{align*}
        \pmb{a} &= \pmb{q}\times\pmb{n} \\ 
        b &= \nabla^2 u + \nabla^4 v
        \end{align*}

And here is a system of equations with labels in an align environment:

.. math::
   :label: eq1

        
        a = q + 4 + 5+ 6  
        

.. math::
   :label: eq2

          
        b = \nabla^2 u + \nabla^4 x 
        
        

We can refer to :eq:`eq1`-:eq:`eq2`. They are a bit simpler than
the Navier - Stokes equations. And test LaTeX hyphen in ``CG-2``.
Also test :math:`a_{i-j}` as well as :math:`kx-wt`.

Testing ``alignat`` environment:

.. math::
   :label: eq1a

        
        a = q + 4 + 5+ 6\qquad  \mbox{for } q\geq 0  
        

.. math::
   :label: eq2a

          
        b = \nabla^2 u + \nabla^4 x  x\in\Omega 
        

More mathematical typesetting is demonstrated in the coming exercises.

Below, we have :ref:`demo:ex:1` and :ref:`demo:ex:2`,
as well as :ref:`proj:circle1` and :ref:`exer:you`, and in
between there we have :ref:`exer:some:formula`.

.. !split

Exercises
=========

.. --- begin exercise ---

.. _demo:ex:1:

Problem 2: Flip a Coin
----------------------

.. keywords = random numbers; Monte Carlo simulation; ipynb

.. Torture tests

**a)**
Make a program that simulates flipping a coin :math:`N` times.
Print out "tail" or "head" for each flip and
let the program count the number of heads.

.. --- begin hint in exercise ---

**Hint 1.**
Use ``r = random.random()`` and define head as ``r <= 0.5``.

.. --- end hint in exercise ---

.. --- begin hint in exercise ---

**Hint 2.**
Draw an integer among :math:`\{1,2\}` with
``r = random.randint(1,2)`` and define head when ``r`` is 1.

.. --- end hint in exercise ---

.. --- begin answer of exercise ---

**Answer.**
If the ``random.random()`` function returns a number :math:`<1/2`, let it be
head, otherwise tail. Repeat this :math:`N` number of times.

.. --- end answer of exercise ---

.. --- begin solution of exercise ---

**Solution.**

.. code-block:: python

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
At least there is not much to find in the section :ref:`sec1`.

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
drawing uniformly distributed random numbers from the interval :math:`[0,1)`?

At the end we have a list because that caused problems in LaTeX
in previous DocOnce versions:

1. item1

2. item2

.. --- begin hint in exercise ---

**Hint.**
To answer this question empirically, let a program
draw :math:`N` such random numbers using Python's standard ``random`` module,
count how many of them, :math:`M`, that fall in the interval :math:`(0.5,0.6)`, and
compute the probability as :math:`M/N`.

.. --- end hint in exercise ---

.. --- end exercise ---

.. --- begin exercise ---

.. _proj:circle1:

Project 5: Explore Distributions of Random Circles
--------------------------------------------------

.. keywords = ipynb

The formula for a circle is given by

.. math::
   :label: circle:x

        
        x = x_0 + R\cos 2\pi t,
        
        

.. math::
   :label: circle:y

          
        y = y_0 + R\sin 2\pi t,
        
        

where :math:`R` is the radius of the circle, :math:`(x_0,y_0)` is the
center point, and :math:`t` is a parameter in the unit interval :math:`[0,1]`.
For any :math:`t`, :math:`(x,y)` computed from :eq:`circle:x`-:eq:`circle:y`
is a point on the circle.
The formula can be used to generate ``n`` points on a circle:

.. code-block:: python

    import numpy as np
    
    def circle(R, x0, y0, n=501):
        t = np.linspace(0, 1, n)
        x = x0 + R*np.cos(2*np.pi*t)
        y = y0 + R*np.sin(2*np.pi*t)
        return x, y
    
    x, y = circle(2.0, 0, 0)

.. Often in an exercise we have some comments about the solution

.. which we normally want to keep where they are.

The goal of this project is to draw :math:`N` circles with random
center and radius. Plot each circle using the ``circle`` function
above.

**a)**
Let :math:`R` be normally distributed and :math:`(x_0,y_0)` uniformly distributed.

.. --- begin hint in exercise ---

**Hint.**
Use the ``numpy.random`` module to draw the
:math:`x_0`, :math:`y_0`, and :math:`R` quantities.

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
Let :math:`R` be uniformly distributed and :math:`(x_0,y_0)` normally distributed.
Filename: ``norm``.

**c)**
Let :math:`R` and :math:`(x_0,y_0)` be normally distributed.

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
With some math :math:`a=b` in this solution:

.. math::
         \hbox{math in solution: } a = b 

And code ``a=b`` in this solution:

.. code-block:: text

    a = b  # code in solution

End of solution is here.

.. --- end solution of exercise ---

**a)**
Subexercises are numbered a), b), etc.

.. --- begin hint in exercise ---

**Hint 1.**
First hint to subexercise a).
With math :math:`a=b` in hint:

.. math::
         a=b. 

And with code (in plain verbatim) returning :math:`x+1` in hint:

.. code-block:: text

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
With math in answer: :math:`a=b`.

.. --- end answer of exercise ---

**b)**
Here goes the text for subexercise b).

Some math :math:`\cos^2 x + \sin^2 x = 1` written one a single line:

.. math::
         \cos^2 x + \sin^2 x = 1 \thinspace .

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

Just some text. And some math saying that :math:`e^0=1` on a single line,
to test that math block insertion is correct:

.. math::
         \exp{(0)} = 1 

And a test that the code ``lambda x: x+2`` is correctly placed here:

.. code-block:: text

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

.. math::
         \frac{dy}{dx} = -y(x),\quad y(0)=1 

What is the solution of this equation?


**Choice A:** :math:`y=e^{-y}`

:abbr:`? (Right!)`

**Choice B:** :math:`y=e^{y}`

:abbr:`? (Wrong!)` :abbr:`# (Almost, but the sign is wrong (note the minus!).)`

**Choice C:** .. code-block:: python

    from math import exp
    def f(x):
        return exp(x)

:abbr:`? (Wrong!)`

**Choice D:** The solution cannot be found because there is a derivative in the equation.

:abbr:`? (Wrong!)` :abbr:`# (Equations with derivatives can be solved; they are termed *differential equations*.)`

**Choice E:** The equation is meaningless: an equation must be an equation
for :math:`x` or :math:`y`, not a function :math:`y(x)`.

:abbr:`? (Wrong!)` :abbr:`# (Equations where the unknown is a function, as y(x) here, are called *differential equations*, and are solved by special techniques.)`

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

.. !split

Here goes another section
=========================

With some text, before we continue with exercises.

.. !split

More Exercises
==============

.. --- begin exercise ---

.. _exer:some:formula:

Exercise 10: Make references to projects and problems
-----------------------------------------------------

.. Test comments not at the end only

Pick a statement from :ref:`proj:circle1` or :ref:`demo:ex:1`
and verify it.

Test list at the end of an exercise without other elements (like subexercise,
hint, etc.):

1. item1

2. item2

Filename: ``verify_formula.py``.

.. --- end exercise ---

.. --- begin exercise ---

.. _exer:you:

Project 11: References in a headings do not work well in sphinx
---------------------------------------------------------------

Refer to the previous exercise as :ref:`exer:some:formula`,
the two before that as :ref:`demo:ex:2` and :ref:`proj:circle1`,
and this one as :ref:`exer:you`.
Filename: ``selc_composed.pdf``.

.. --- end exercise ---

.. !split

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


.. !split

.. _app1:

Appendix: Just for testing; part I
==================================

This is the first appendix.

A subsection within an appendix
-------------------------------

Some text.

.. !split

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
site. [**hpl's semi opinion 1**: not sure if in the cloud is understood by all.] I strongly recommend you to use such sites for all serious
programming and scientific writing work - and all other important
files.

The simplest services for hosting project files is Dropbox. [**mp 2**: Simply go to `<https://dropbox.com>`_ and watch the video. It explains how files, like ``myfile.py``, perhaps containing much math, like :math:`\partial u/\partial t`, are easily communicated between machines.] It
is very easy to get started with Dropbox, and it allows you to share
files among (**hpl 3: remove** laptops and mobile units) (**insert:**)computers, tablets, and phones (**end insert**).

.. Test horizontal rule

---------

.. Coments for editing

First, (**edit 4: add comma**) consider a quantity :math:`Q`. (**edit 5: remove** To this end,) (**insert:**)We note that (**end insert**)
:math:`Q>0`, because (**edit 6**: **delete** a) negative (**edit 7: remove** quantity is) (**insert:**)quantities are (**end insert**) (**edit 8**: **delete** just) negative.  (**edit 9: add**) This comes as no surprise. (**end add**)

.. Test tailored latex figure references with page number

Let us refer to Figure :ref:`fig:impact` again.

Test references in a list:

 * :ref:`sec1`

 * :ref:`subsec1`

 * :ref:`fig:impact`

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
