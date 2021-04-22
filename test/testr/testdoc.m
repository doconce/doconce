%% A Document for Testing DocOnce
% 
% Author: Hans Petter Langtangen [1, 2] (hpl@simula.no)
% Author: Kaare Dump [3] 
% Author: A. Dummy Author  
% Author: I. S. Overworked and Outburned [4, 5, 6, 7] 
% Author: J. Doe  (j_doe@cyberspace.com)
% 
% [1] Center for Biomedical Computing, Simula Research Laboratory
% [2] Department of Informatics, University of Oslo
% [3] Segfault, Cyberspace
% [4] Inst1
% [5] Inst2, Somewhere
% [6] Third Inst, Elsewhere
% [7] Fourth Inst
% 
% Date: Jan 32, 2100
% 
% Made with DocOnce
% 
% 
% 
% Table of contents:
% 
%  Section 1 
%      Here is a list with subsubsection heading 
%    Subsection 1 
%      Test Section reference at beginning of line and after a sentence 
%      Computer code 
%      Subsubsection heading before code 
%      Running OS commands 
%      Footnotes 
%    Subsection 2: Testing figures 
%    The $\theta$ parameter (not $\nabla$?) 
%    Custom Environments 
%    Tables 
%    A test of verbatim words in heading with subscript $a_i$: |my_file_v1| and |my_file_v2| 
%    *Just bold* 
%    _Just emphasize_ 
%    |Just verbatim| 
%    *Bold* beginning 
%    _Emphasize_ beginning 
%    |Verbatim| beginning 
%    Maybe *bold end* 
%    Maybe _emphasize end_ 
%    Maybe |verbatim end| 
%    The middle has *bold* word 
%    The middle has _emphasize_ word 
%    The middle has |verbatim| word 
%    Bibliography test 
%    Example 1: Examples can be typeset as exercises 
%    User-defined environments 
%    Example 1: A test function 
%    Example 2: Addition 
%    URLs 
%  LaTeX Mathematics 
%  Exercises 
%    Problem 2: Flip a Coin 
%      My remarks 
%      Remarks 
%    Not an exercise 
%    Exercise 3: Test of plain text exercise 
%    Project 4: Compute a Probability 
%    Project 5: Explore Distributions of Random Circles 
%      Remarks 
%    Exercise 6: Determine some Distance 
%      Remarks 
%    Some exercise without the "Exercise:" prefix 
%    Exercise 8: Solution of differential equation 
%    Example 9: Just an example 
%  Here goes another section 
%  More Exercises 
%    Exercise 10: Make references to projects and problems 
%    Project 11: References to "Project 4: Compute a Probability" in a heading works for matlabnb 
%  References 
%  Appendix: Just for testing; part I 
%    A subsection within an appendix 
%  Appendix: Just for testing; part II 
%    Appendix: Testing identical titles 
%    Appendix: Testing identical titles 
%    Appendix: Testing identical titles 
%    Appendix: Testing identical titles 
%    Appendix: Testing inline comments 
%    Appendix: Testing headings ending with |verbatim inline| 
% 
% % !split
% 
% The format of this document is
% matlabnb
% 
% *Abstract.* This is a document with many test constructions for doconce syntax.
% It was used heavily for the development and kept for testing
% numerous constructions, also special and less common cases.
% 
% And exactly for test purposes we have an extra line here, which
% is part of the abstract.
% 
% % Cannot demonstrate chapter headings since abstract and chapter
% % are mutually exclusive in LaTeX
% 
%% Section 1
% 
% Here is a nested list:
% 
%   * item1
% 
%   * item2
% 
%   * item3 which continues on the next line to test that feature
% 
%   * and a sublist
% 
%     * with indented subitem1
% 
%     * and a subitem2
% 
% 
%   * and perhaps an ordered sublist
% 
%    # first item
% 
%    # second item, continuing on a new line
% 
% 
% *Here is a list with paragraph heading.* 
%   * item1
% 
%   * item2
% 
%% Here is a list with subsubsection heading
%   * item1
% 
%   * item2
% 
% !bquote
% Here are two lines that make up
% a block quote for testing _emphasized words_ and *boldface words*,
% also with hypens:
% _pre_-fix, post-_fix_, *pre*-fix, post-*fix*.
% !equote
% 
% Here are two references. Equation (ref{my:eq1}) is fine. Eq. (ref{my:eq1}) too.
% Even Equation (ref{my:eq1}) without the tilde.
% 
%% Subsection 1
% 
% % Refer to section/appendix etc. at the beginning of the line
% % and other special fix situations for HTML.
% 
% More text, with a reference back to
% the section "Section 1" and "Subsection 1", and further to the
% the sections "Subsection 1" and "URLs", which
% encourages you to do the tasks in "Problem 2: Flip a Coin" and "Exercise 10: Make references to projects and problems".
%  "Appendix: Just for testing; part I" and "Appendix: Just for testing; part II" are also nice elements.
% 
%% Test Section reference at beginning of line and after a sentence
% The section "Subsection 1" is fine.
% The section "URLs" too.
% 
% % sphinx code-blocks: pycod=python cod=fortran cppcod=c++ sys=console
% 
%% Computer code
% Let's do some copying from files too. First from subroutine up to the very end,
% 
%        subroutine test()
%        integer i
%        real*8 r
%        r = 0
%        do i = 1, i
%           r = r + i
%        end do
%        return
%  C     END1
%  
%        program testme
%        call test()
%        return
% and then just the subroutine,
%  
%        subroutine test()
%        integer i
%        real*8 r
%        r = 0
%        do i = 1, i
%           r = r + i
%        end do
%        return
% and finally the complete file with a plain text verbatim environment
% (|envir=ccq|):
%  C     a comment
%  
%        subroutine test()
%        integer i
%        real*8 r
%        r = 0
%        do i = 1, i
%           r = r + i
%        end do
%        return
%  C     END1
%  
%        program testme
%        call test()
%        return
% 
% Testing other code environments. First Python:
% 
%  !bc pycod
%  def f(x):
%      return x+1
%  !ec
% which gets rendered as
% 
%  def f(x):
%      return x+1
% 
% Test paragraph and subsubsection headings before
% before code.
% 
% *Paragraph heading before code.* 
%  import sys
%  sys.path.insert(0, os.pardir)
% 
%% Subsubsection heading before code
%  def h(z):
%      return z+1
% 
% Here is a program that is supposed to be interactive via
% Python Online Tutorial, but that service is not accessible
% for the present format.
% 
%  class Line:
%      def __init__(self, a, b):
%          self.a, self.b = a, b
%  
%      def __call__(self, x):
%          a, b = self.a, self.b
%          return a*x + b
%  
%  line = Line(2, 1)
%  y = line(x=3)
%  print(y)
% 
% Some more Python code (actually specified as a sage cell, but
% such cells are not supported by this format).
% 
%  a = 2
%  b = 3
%  print('a+b:', a + b)
%  
%  # In a sage cell we can also plot
%  from matplotlib.pyplot import *
%  from numpy import *
%  x = linspace(0, 4*pi, 101)
%  y = exp(-0.1*x)*cos(x)
%  plot(x, y)
%  xlabel('x'); ylabel('y')
%  show()
% 
% Then Cython (with -h option so it is hidden in html/sphinx):
% 
%  cpdef f(double x):
%      return x + 1
% 
% Standard Python shell sessions:
% 
%  >>> from numpy import linspace, sin
%  >>> # Some comment
%  >>> x = linspace(0, 2, 11)
%  >>> y = sin(x)
%  >>> y[0]
%  0
%  >>> import matplotlib.pyplot as plt
%  >>> plt.plot(x, y)
% 
% Similar IPython sessions:
% 
%  In [1]: from numpy import linspace, sin
%  In [2]: # Some comment
%  In [3]: x = linspace(0, 2, 11)
%  In [4]: y = sin(x)
%  In [5]: y[0]
%  Out[5]: 0
%  In [6]: import matplotlib.pyplot as plt
%  In [7]: plt.plot(x, y)
%  In [8]: a='multiple-\nline\noutput'
%  In [9]: a
%  Out[9]: 'multiple-\nline\noutput'
%  In [10]: print(a)
%  multiple-
%  line
%  output
% 
% Here is the interactive session again, but with |pyshell-t|.
% 
%  >>> from numpy import linspace, sin
%  >>> # Some comment
%  >>> x = linspace(0, 2, 11)
%  >>> y = sin(x)
%  >>> y[0]
%  0
%  >>> import matplotlib.pyplot as plt
%  >>> plt.plot(x, y)
% 
% % This one tests a + sign before a code environment
% C++:
%  #include <iostream>
%  
%  int main()
%  {
%     std::cout << "Sample output" << std::endl;
%     return 0
%  }
% % The next should get correctly typset in sphinx (cod is fcod)
% % It also tests emoji before code
% And a little bit of Fortran: :dizzy_face:
% 
%  !bc cod
%        subroutine midpt(x, length, a, b)
%        real*8 a, b, x
%        x = (a + b)/2
%        length = b - a
%        return
%        end
%  !ec
% which then is typeset as
% 
%        subroutine midpt(x, length, a, b)
%        real*8 a, b, x
%        x = (a + b)/2
%        length = b - a
%        return
%        end
% 
% HTML:
% 
%  <table>
%  <tr><td>Column 1</td><td>Column 2</td></tr>
%  <tr><td>0.67526 </td><td>0.92871 </td></tr>
%  <!-- comment -->
%  </table>
% 
% But inline HTML code is also important, like text that starts with
% |<a href="| (which can destroy the following text if not properly
% quoted).
% 
% Matlab with comments requires special typesetting:
% 
% Comment on the beginning of the line can be escaped by %%
if a > b
% Indented comment needs this trick
c = a + b
end
% 
% And here is a system call:
% 
%  Terminal> mkdir test
%  Terminal> cd test
%  Terminal> myprog -f
%  output1
%  output2
% 
% Any valid pygments lexer/language name can appear to, e.g.,
% 
%  !bc restructuredtext
%  =======
%  Heading
%  =======
%  
%  Some text.
%  !ec
% results in
% 
%  =======
%  Heading
%  =======
%  
%  Some text.
% 
% % Here goes hidden code.
% % Python can be treated by some formats, Fortran is always out.
% 
% 
% 
% Finally, |!bc do| supports highlighting of DocOnce source:
% 
%  ======= DocOnce test file =======
%  
%  ===== Computer code =====
%  
%  Inline verbatim code, as in `import numpy as np`, is allowed, as well as
%  code blocks:
%  
%  !bc pycod
%  from math import sin
%  
%  def f(x):
%      """Example on a function."""
%      return sin(x) + 1
%  
%  print(f(0))
%  !ec
%  
%  
%  ===== Mathematics =====
%  
%  Formulas can be inline, as in $\nabla\cdot\bm{u} = 0$, or typeset
%  as equations:
%  
%  !bt
%  \begin{align*}
%  \nabla\cdot\bm{u} &= 0,\\ 
%  \bm{u} &= \nabla\phi .
%  \end{align*}
%  !et
%  
%  === Subsubsection heading ===
%  
%  DocOnce files can have chapters, sections, subsections, and subsubsections.
%  
%  __Paragraph heading.__ Paragraphs may have headings.
% 
% It is time to test |verbatim inline font| especially with |a newline
% inside the text| and an exclamation mark at the end: |BEGIN|! For
% spellcheck, test |a verbatim expression| in |another| in a |third|.
% Also test exclamation mark as in |!bc| and |!ec| as well as |a != b|.
% Also test backslashes and braces like |\begin|, |\begin{enumerate}|,
% |\end{this}\end{that}|, and |{something \inside braces}|.
% 
% The following attempt to exemplify colored text does not work in
% format matlabnb.
% Here is some red color and an attempt to write with
% green color containing a linebreak
% code. Some formats will only display 
% this correctly when |html| 
% is the output format.
% But here some more running text is added which is not part of
% the previous blocks with line breaks.
% 
%% Running OS commands
%  Terminal> python -c 'print("Testing\noutput\nfrom\nPython.")'
%  Testing
%  output
%  from
%  Python.
% 
%% Footnotes
% Here is a test of footnotes [^footnote], which are handy in text.
% They are used in different flavors, now in
% 
%  * list items (note below that footnotes work after math, verbatim, and URLs - bin fact old and emphasize too!)
% 
%  * even with math $\nabla^2u$[^math1]
% 
%  * and code |h[i] += 1|[^code] (_must_ have space between inline code and footnote!)
% 
%  * and links <https://google.com>[^google-search]
% 
% which gives flexibility in writing.
% This is the third[^example-of-the-third-footnote] example.
% 
%   [^footnote]: Typesetting of the footnote depends on the format.
% Plain text does nothing, LaTeX removes the
% definition and inserts the footnote as part of the LaTeX text.
% reStructuredText and Sphinx employ a similar type of typesetting
% as Extended Markdown and DocOnce, and in HTML we keep the same
% syntax, just displayed properly in HTML.
% [^math1]: Math footnotes can be dangerous since it
% interferes with an exponent.
% [^code]: One-line footnote.
% 
% [^google-search]: <google.com> is perhaps the most famous
% web site today.
% 
% Here is some more text before a new definition of a footnote that was
% used above.
% 
% !bnotice Non-breaking space character
% This paragraph aims to test non-breaking space character <https://en.wikipedia.org/wiki/Non-breaking_space>, and a typical
% example where this is needed is in physical units: 7.4 km is traveled
% in $7.4/5.5\approx 1.345$ s.  Also check that a link <https://google.com> is
% not broken across lines (drag the browser window to test this).
% (On the other hand, the tilde is used in
% computer code, e.g., as in |[~x for x in y]| or in |y=~x|, and should
% of course remain a tilde in those contexts.)
% !enotice
% 
%% Subsection 2: Testing figures
% 
% Test of figures. In particular we refer to Figure ref{fig:impact} in which
% there is a flow.
% 
% <<testfigs/wave1D.png>>
% 
% Figures without captions are allowed and will be inlined.
% 
% <<testfigs/wave1D.png>>
% 
% % Test multi-line caption in figure with sidecap=True
% 
% Here is figure ref{myfig} with a long (illegal) multi-line caption
% containing inline verbatim text:
% 
% <<testfigs/wave1D.png>>
% 
% % Must be a blank line after MOVIE or FIGURE to detect this problem
% 
% Test URL as figure name:
% 
% <<https://raw.github.com/doconce/doconce/master/doc/src/blog/f_plot.png>>
% 
% % Test wikimedia type of files that otherwise reside in subdirs
% 
% *Remark.* Movies are tested in separate file |movies.do.txt|.
% 
% % Somewhat challenging heading with latex math, \t, \n, ? and parenthesis
% 
%% The $\theta$ parameter (not $\nabla$?)
% 
% Functions do not always need to be advanced, here is one
% involving $\theta$:
!bc
%  def f(theta):
%      return theta**2
% 
% *More on $\theta$.* Here is more text following headline with math.
% 
% Newcommands must also be tested in this test report:
% $\frac{1}{2}$, ${1/2}$, $\pmb{x}$, $\frac{Du}{dt}$,
% both inline and in block:
% 
% $$\frac{Du}{dt} &= 0\nonumber \\  \frac{1}{2} &= {1/2} \\  \frac{1}{2}\pmb{x} &= \pmb{n}$$
% 
% Or with align with label and numbers:
% 
% $$\frac{Du}{dt} &= 0  \\  \frac{1}{2} &= {1/2} \\  \frac{1}{2}\pmb{x} &= \pmb{n}$$
% 
% % Must test more complicated align and matrix compositions
% % where DocOnce inserts auto-numbered labels etc.
% 
% First one numbered (automatically):
% 
% $$\begin{pmatrix} G_2 + G_3 & -G_3 & -G_2 & 0 \\  -G_3 & G_3 + G_4 & 0 & -G_4 \\  -G_2 & 0 & G_1 + G_2 & 0 \\  0 & -G_4 & 0 & G_4 \end{pmatrix} &= \begin{pmatrix}  v_1 \\   v_2 \\   v_3 \\   v_4 \end{pmatrix} + \cdots   \\  \begin{pmatrix}  C_5 + C_6 & -C_6 & 0 & 0 \\   -C_6 & C_6 & 0 & 0 \\   0 & 0 & 0 & 0 \\   0 & 0 & 0 & 0 \end{pmatrix}   &= \frac{d}{dt}\begin{pmatrix}  v_1 \\   v_2 \\   v_3 \\   v_4 \end{pmatrix} + \begin{pmatrix}  0 \\   0 \\   0 \\   -i_0 \end{pmatrix} \nonumber  \end{align}$$
% 
% Second numbered (automatically):
% 
% $$\begin{pmatrix} G_1 + G_2\\  -G_3 & G_4 \end{pmatrix} &= \begin{pmatrix}  v_1 \\   v_2 \end{pmatrix} + \cdots\nonumber  \\  \left(\begin{array}{ll} y & 2\\  2 & 1 \end{array}\right) \left(\begin{array}{ll} 0 \\ x \end{array}\right) &= \begin{pmatrix} A \\ B \end{pmatrix}  \end{align}$$
% 
% Both numbered, with label by the user:
% 
% $$\begin{pmatrix} G_1 + G_2\\  -G_3 & G_4 \end{pmatrix} &= \begin{pmatrix}  v_1 \\   v_2 \end{pmatrix} + \cdots  \\   \left(\begin{array}{ll} y & 2\\  2 & 1 \end{array}\right) \left(\begin{array}{ll} 0 \\ x \end{array}\right) &= \begin{pmatrix} A \\ B \end{pmatrix} \end{align}$$
% Now we refer to Equations (mymatrix:eq1)-(mymatrix:eq2).
% 
%% Custom Environments
% 
% Here is an attempt to create a theorem environment via Mako
% (for counting theorems) and comment lines to help replacing lines in
% the |.tex| by proper begin-end LaTeX environments for theorems.
% Should look nice in most formats!
% 
% % begin theorem
% 
% *Theorem 5.* Let $a=1$ and $b=2$. Then $c=3$.
% % end theorem
% 
% % begin proof
% *Proof.* Since $c=a+b$, the result follows from straightforward addition.
% $\Diamond$
% % end proof
% 
% As we see, the proof of Theorem 5 is a modest
% achievement.
% 
%% Tables
% 
% % index with comma could fool sphinx
% 
% Let us take this table from the manual:
% 
% <table class="table" border="1">
% <thead>
% <tr><th align="center">time</th> <th align="center">velocity</th> <th align="center">acceleration</th> </tr>
% </thead>
% <tbody>
% <tr><td align="left">   0.0     </td> <td align="right">   1.4186      </td> <td align="right">   -5.01           </td> </tr>
% <tr><td align="left">   2.0     </td> <td align="right">   1.376512    </td> <td align="right">   11.919          </td> </tr>
% <tr><td align="left">   4.0     </td> <td align="right">   1.1E+1      </td> <td align="right">   14.717624       </td> </tr>
% </tbody>
% </table>
% The DocOnce source code reads
%  
%    |--------------------------------|
%    |time  | velocity | acceleration |
%    |--l--------r-----------r--------|
%    | 0.0  | 1.4186   | -5.01        |
%    | 2.0  | 1.376512 | 11.919       |
%    | 4.0  | 1.1E+1   | 14.717624    |
%    |--------------------------------|
%  
% 
% Here is yet another table to test that we can handle more than
% one table:
% 
% <table class="table" border="1">
% <thead>
% <tr><th align="left">time</th> <th align="left">velocity</th> <th align="left">acceleration</th> </tr>
% </thead>
% <tbody>
% <tr><td align="left">   0.0     </td> <td align="left">   1.4186      </td> <td align="left">   -5.01           </td> </tr>
% <tr><td align="left">   1.0     </td> <td align="left">   1.376512    </td> <td align="left">   11.919          </td> </tr>
% <tr><td align="left">   3.0     </td> <td align="left">   1.1E+1      </td> <td align="left">   14.717624       </td> </tr>
% </tbody>
% </table>
% And one with math headings (that are expanded and must be treated
% accordingly), verbatim heading and entry, and no space around the pipe
% symbol:
% 
% <table class="table" border="1">
% <thead>
% <tr><th align="center">$i$</th> <th align="center">$h_i$ </th> <th align="center">$\bar T_i$</th> <th align="center">|L_i|</th> </tr>
% </thead>
% <tbody>
% <tr><td align="left">   0      </td> <td align="right">   0         </td> <td align="right">   288           </td> <td align="right">   -0.0065        </td> </tr>
% <tr><td align="left">   1      </td> <td align="right">   11,000    </td> <td align="right">   216           </td> <td align="right">   0.0            </td> </tr>
% <tr><td align="left">   2      </td> <td align="right">   20,000    </td> <td align="right">   216           </td> <td align="right">   0.001          </td> </tr>
% <tr><td align="left">   3      </td> <td align="right">   32,000    </td> <td align="right">   228           </td> <td align="right">   0.0028         </td> </tr>
% <tr><td align="left">   4      </td> <td align="right">   47,000    </td> <td align="right">   270           </td> <td align="right">   0.0            </td> </tr>
% <tr><td align="left">   5      </td> <td align="right">   51,000    </td> <td align="right">   270           </td> <td align="right">   -0.0028        </td> </tr>
% <tr><td align="left">   6      </td> <td align="right">   71,000    </td> <td align="right">   214           </td> <td align="right">   |NaN|    </td> </tr>
% </tbody>
% </table>
% And add one with verbatim headings (with underscores),
% and rows starting with ||-| because of a negative number,
% and ||| right before and after verbatim word (with no space):
% 
% <table class="table" border="1">
% <thead>
% <tr><th align="center">exact</th> <th align="center">|v_1|</th> <th align="center">$a_i$ + |v_2|</th> <th align="center">|verb_3_|</th> </tr>
% </thead>
% <tbody>
% <tr><td align="right">   9        </td> <td align="right">   9.62           </td> <td align="right">   5.57                   </td> <td align="right">   8.98               </td> </tr>
% <tr><td align="right">   -20      </td> <td align="right">   -23.39         </td> <td align="right">   -7.65                  </td> <td align="right">   -19.93             </td> </tr>
% <tr><td align="right">   10       </td> <td align="right">   17.74          </td> <td align="right">   -4.50                  </td> <td align="right">   9.96               </td> </tr>
% <tr><td align="right">   0        </td> <td align="right">   -9.19          </td> <td align="right">   4.13                   </td> <td align="right">   -0.26              </td> </tr>
% </tbody>
% </table>
% Pipe symbols in verbatim and math text in tables used to pose difficulties,
% but not
% anymore (except for plain text and matlabnb).
% 
% Here is a table with X alignment:
% 
% <table class="table" border="1">
% <thead>
% <tr><th align="center"> Type</th> <th align="center">                                                                                                           Description                                                                                                            </th> </tr>
% </thead>
% <tbody>
% <tr><td align="center">   X        </td> <td align="left">   Alignment character that is used for specifying a potentially very long text in a column in a table. It makes use of the |tabularx| package in LaTeX, otherwise (for other formats) it means |l| (centered alignment).    </td> </tr>
% <tr><td align="center">   l,r,c    </td> <td align="left">   standard alignment characters                                                                                                                                                                                                         </td> </tr>
% </tbody>
% </table>
% Finally, a table with math
% and URLs.
% 
% % Mako code to expand URLs in the table
% % (These types of tables did not work before Jan 2014)
% 
% <table class="table" border="1">
% <tr></tr>
% <tbody>
% <tr><td align="center">   $\mathcal{L}=0$            </td> <td align="center">   080 <../doc/src/manual/mov/wave_frames/frame_0080.png>    </td> <td align="center">   085 <../doc/src/manual/mov/wave_frames/frame_0085.png>    </td> </tr>
% <tr><td align="center">   $a=b$                      </td> <td align="center">   090 <../doc/src/manual/mov/wave_frames/frame_0090.png>    </td> <td align="center">   095 <../doc/src/manual/mov/wave_frames/frame_0095.png>    </td> </tr>
% <tr><td align="center">   $\nabla\cdot\bm{u} =0 $    </td> <td align="center">   100 <../doc/src/manual/mov/wave_frames/frame_0100.png>    </td> <td align="center">   105 <../doc/src/manual/mov/wave_frames/frame_0105.png>    </td> </tr>
% </tbody>
% </table>
%% A test of verbatim words in heading with subscript $a_i$: |my_file_v1| and |my_file_v2|
% 
% *Paragraph with verbatim and math: |my_file_v1.py| and |my_file_v2.py| define some math $a_{i-1}$.* Here is more |__verbatim__| code and
% some plain text on a new line.
% 
% % Test various types of headlines
%% *Just bold*
% 
% Some text.
% 
%% _Just emphasize_
% 
% Some text.
% 
%% |Just verbatim|
% 
% Some text.
% 
%% *Bold* beginning
% 
% Some text.
% 
%% _Emphasize_ beginning
% 
% Some text.
% 
%% |Verbatim| beginning
% 
% Some text.
% 
%% Maybe *bold end*
% 
% Some text.
% 
%% Maybe _emphasize end_
% 
% Some text.
% 
%% Maybe |verbatim end|
% 
% Some text.
% 
%% The middle has *bold* word
% 
% Some text.
% 
%% The middle has _emphasize_ word
% 
% Some text.
% 
%% The middle has |verbatim| word
% 
% Some text.
% 
% *_Just emphasize_.* Some text.
% 
% *|Just verbatim|.* Some text.
% 
% *_Emphasize_ beginning.* Some text.
% 
% *|Verbatim beginning|.* Some text.
% 
% *Maybe _emphasize end_.* Some text.
% 
% *Maybe |verbatim end|.* Some text.
% 
% *The middle has _emphasize_ word.* Some text.
% 
% *The middle has |verbatim| word.* Some text.
% 
% *Ampersand.* We can test Hennes & Mauritz, often abbreviated H&M, but written
% as |Hennes & Mauritz| and |H & M|.
% A sole |&| must also work.
% % Note: substitutions must not occur inside verbatim, just in ordinary text.
% 
!bc
%  # Just to check that ampersand works in code blocks:
%  c = a & b
% 
% *Quotes.* Let us also add a test of quotes such as "double quotes, with numbers
% like 3.14 and newline/comma and hyphen (as in double-quote)"; written
% in the standard LaTeX-style that gives correct LaTeX formatting and
% ordinary double quotes for all non-LaTeX formats.  Here is another
% sentence that "caused" a bug in the past because double backtick
% quotes could imply verbatim text up to a verbatim word starting with
% period, like |.txt|.
% 
% More quotes to be tested for spellcheck:
% ("with parenthesis"), "with newline"
% and "with comma", "hyphen"-wise, and "period".
% 
%% Bibliography test
% 
% Here is an example: [1] discussed propagation of
% large destructive water waves, [2] gave
% an overview of numerical methods for solving the Navier - Stokes equations,
% while the use of Backward Kolmogorov equations for analyzing
% random vibrations was investigated in [3].
% The book chapter [4] contains information on
% C++ software tools for programming multigrid methods. A real retro
% reference is [5] about a big FORTRAN package.
% Multiple references are also possible, e.g., see
% [1] [4].
% 
% We need to cite more than 10 papers to reproduce an old formatting
% problem with blanks in the keys in reST format:
% [6] [3] [7] [1]
% and
% [2] [8] [9] [10] [11] [12] [13]
% and all the work of
% [14] [4] [15] as well as
% old work [5] and [16], and the
% talk [17].
% Langtangen also had two thesis [18] [16]
% back in the days.
% More retro citations are
% the old ME-IN323 book [19] and the
% [20] OONSKI '94 paper.
% 
% % --- begin exercise ---
% 
%% Example 1: Examples can be typeset as exercises
% 
% Examples can start with a subsection heading starting with |Example:|
% and then, with the command-line option |--examples_as_exercises| be
% typeset as exercises. This is useful if one has solution
% environments as part of the example.
% 
% % --- begin subexercise ---
% *a)* State some problem.
% 
% *Solution.* The answer to this subproblem can be written here.
% 
% % --- end subexercise ---
% 
% % --- begin subexercise ---
% *b)* State some other problem.
% 
% *Hint 1.* A hint can be given.
% 
% *Hint 2.* Maybe even another hint?
% 
% *Solution.* The answer to this other subproblem goes here,
% maybe over multiple doconce input lines.
% 
% % --- end subexercise ---
% 
% % --- end exercise ---
% 
%% User-defined environments
% 
% The example in the section "Example 1: A test function" demonstrates how to write a test function.
% That is, a special test function for a function |add| appears in
% the example in the section "Example 1: A test function".
% 
%% Example 1: A test function
% 
% Suppose we want to write a test function for checking the
% implementation of a Python function for addition.
% 
%  def add(a, b):
%      return a + b
%  
%  def test_add():
%      a = 1; b = 1
%      expected = a + b
%      computed = add(a, b)
%      assert expected == computed
% 
%% Example 2: Addition
% 
% We have
% 
% $$1 + 1 = 2$$
% or in tabular form:
% 
% <table class="table" border="1">
% <thead>
% <tr><th align="center">Problem</th> <th align="center">Result</th> </tr>
% </thead>
% <tbody>
% <tr><td align="center">   $1+1$      </td> <td align="center">   $2$       </td> </tr>
% </tbody>
% </table>
% !bnotice Highlight box!
% This environment is used to highlight something:
% 
% $$E = mc^2$$
% !enotice
% 
%% URLs
% 
% Testing of URLs: hpl's home page hpl <https://folk.uio.no/hpl>, or
% the entire URL if desired, <https://folk.uio.no/hpl>.  Here is a
% plain file link <testdoc.do.txt>, or <testdoc.do.txt>, or
% <testdoc.do.txt> or <testdoc.do.txt> or a link with
% newline <testdoc.do.txt>. Can test spaces with the link with word
% too: hpl <https://folk.uio.no/hpl> or hpl <https://folk.uio.no/hpl>. Also |file:///| works: link to a
% file <file:///home/hpl/vc/doconce/doc/demos/manual/manual.html> is
% fine to have. Moreover, "loose" URLs work, i.e., no quotes, just
% the plain URL as in <https://folk.uio.no/hpl>, if followed by space, comma,
% colon, semi-colon, question mark, exclamation mark, but not a period
% (which gets confused with the periods inside the URL).
% 
% Mail addresses can also be used: hpl@simula.no <mailto:hpl@simula.no>, or just a mail link <mailto:hpl@simula.no>, or a raw <mailto:hpl@simula.no>.
% 
% Here are some tough tests of URLs, especially for the |latex| format:
% Newton-Cotes <https://en.wikipedia.org/wiki/Newton%E2%80%93Cotes_formulas> formulas
% and a good book <https://www.springer.com/mathematics/computational+science+%26+engineering/book/978-3-642-23098-1>. Need to test
% Newton-Cotes with percentage in URL too:
% <https://en.wikipedia.org/wiki/Newton%E2%80%93Cotes_formulas>
% and <https://en.wikipedia.org/wiki/Newton-Cotes#Open_Newton.E2.80.93Cotes_formulae> which has a shebang.
% 
% For the |--device=paper| option it is important to test that URLs with
% monospace font link text get a footnote
% (unless the |--latex_no_program_footnotelink|
% is used), as in this reference to
% decay_mod <https://github.com/hplgit/INF5620/tree/gh-pages/src/decay/experiments/decay_mod.py>, ball1.py <https://tinyurl.com/pwyasaa/formulas.ball1.py>,
% and ball2.py <https://tinyurl.com/pwyasaa/formulas.ball2.py>.
% 
% % Comments should be inserted outside paragraphs (because in the rst
% % format extra blanks make a paragraph break).
% 
% % Note that when there is no https: or file:, it can be a file link
% % if the link name is URL, url, "URL", or "url". Such files should,
% % if rst output is desired, but placed in a |_static*| folder.
% 
% More tough tests: repeated URLs whose footnotes when using the
% |--device=paper| option must be correct. We have
% google <https://google.com>, google <https://google.com>, and
% google <https://google.com>, which should result in exactly three
% footnotes.
% 
% % !split and check if these extra words are included properly in the comment
% 
%% LaTeX Mathematics
% 
% Here is an equation without label using backslash-bracket environment:
% $$a = b + c$$
% 
% or with number and label, as in Equation (my:eq1), using the equation environment:
% 
% $${\partial u\over\partial t} = \nabla^2 u$$
% 
% We can refer to this equation by Equation (my:eq1).
% 
% Here is a system without equation numbers, using the align-asterisk environment:
% 
% $$\begin{align*} \pmb{a} &= \pmb{q}\times\pmb{n} \\  b &= \nabla^2 u + \nabla^4 v \end{align*}$$
% 
% More mathematical typesetting is demonstrated in the coming exercises.
% 
% Below, we have "Problem 2: Flip a Coin" and "Project 4: Compute a Probability",
% as well as "Project 5: Explore Distributions of Random Circles" and "Project 11: References to Project ref{demo:ex:2} in a heading works for matlabnb", and in
% between there we have "Exercise 10: Make references to projects and problems".
% 
%% Exercises
% 
% % --- begin exercise ---
% 
%% Problem 2: Flip a Coin
% 
% % keywords = random numbers; Monte Carlo simulation; ipynb
% 
% % Torture tests
% 
% % --- begin subexercise ---
% *a)* Make a program that simulates flipping a coin $N$ times.
% Print out "tail" or "head" for each flip and
% let the program count the number of heads.
% 
% % --- begin hint in exercise ---
% 
% *Hint 1.* Use |r = random.random()| and define head as |r <= 0.5|.
% 
% % --- end hint in exercise ---
% 
% % --- begin hint in exercise ---
% 
% *Hint 2.* Draw an integer among $\{1,2\}$ with
% |r = random.randint(1,2)| and define head when |r| is 1.
% 
% % --- end hint in exercise ---
% 
% % --- begin answer of exercise ---
% *Answer.* If the |random.random()| function returns a number $<1/2$, let it be
% head, otherwise tail. Repeat this $N$ number of times.
% % --- end answer of exercise ---
% 
% % --- begin solution of exercise ---
*Solution.*
%  import sys, random
%  N = int(sys.argv[1])
%  heads = 0
%  for i in range(N):
%      r = random.random()
%      if r <= 0.5:
%          heads += 1
%  print('Flipping a coin %d times gave %d heads' % (N, heads))
% % --- end solution of exercise ---
% 
% % --- end subexercise ---
% 
% % --- begin subexercise ---
% *b)* Vectorize the code in a) using boolean indexing.
% 
% Vectorized code can be written in many ways.
% Sometimes the code is less intuitive, sometimes not.
% At least there is not much to find in the section "Section 1".
% 
% % --- end subexercise ---
% 
% % --- begin subexercise ---
% *c)* Vectorize the code in a) using |numpy.sum|.
% 
% % --- begin answer of exercise ---
% *Answer.* |np.sum(np.where(r <= 0.5, 1, 0))| or |np.sum(r <= 0.5)|.
% % --- end answer of exercise ---
% 
% In this latter subexercise, we have an
% example where the code is easy to read.
% 
%% My remarks
% Remarks with such a subsubsection is treated as more text
% after the last subexercise. Test a list too:
% 
% # Mark 1.
% 
% # Mark 2.
% 
% % --- end subexercise ---
% 
% Filenames: |flip_coin.py|, |flip_coin.pdf|.
% 
% % Closing remarks for this Problem
% 
%% Remarks
% These are the exercise remarks, appearing at the very end.
% 
% % solution files: mysol.txt, mysol_flip_coin.py, yet_another.file
% 
% % --- end exercise ---
% 
%% Not an exercise
% 
% Should be possible to stick a normal section in the middle of many
% exercises.
% 
% % --- begin exercise ---
% 
%% Exercise 3: Test of plain text exercise
% 
% Very short exercise. What is the capital
% of Norway?
% Filename: |myexer1|.
% 
% % --- end exercise ---
% 
% % --- begin exercise ---
% 
%% Project 4: Compute a Probability
% 
% % Minimalistic exercise
% 
% What is the probability of getting a number between 0.5 and 0.6 when
% drawing uniformly distributed random numbers from the interval $[0,1)$?
% 
% At the end we have a list because that caused problems in LaTeX
% in previous DocOnce versions:
% 
% # item1
% 
% # item2
% 
% % --- begin hint in exercise ---
% 
% *Hint.* To answer this question empirically, let a program
% draw $N$ such random numbers using Python's standard |random| module,
% count how many of them, $M$, that fall in the interval $(0.5,0.6)$, and
% compute the probability as $M/N$.
% 
% % --- end hint in exercise ---
% 
% % --- end exercise ---
% 
% % --- begin exercise ---
% 
%% Project 5: Explore Distributions of Random Circles
% 
% % keywords = ipynb
% 
% The formula for a circle is given by
% 
% $$x &= x_0 + R\cos 2\pi t, \\  y &= y_0 + R\sin 2\pi t,$$
% where $R$ is the radius of the circle, $(x_0,y_0)$ is the
% center point, and $t$ is a parameter in the unit interval $[0,1]$.
% For any $t$, $(x,y)$ computed from Equations (circle:x)-(circle:y)
% is a point on the circle.
% The formula can be used to generate |n| points on a circle:
% 
%  import numpy as np
%  
%  def circle(R, x0, y0, n=501):
%      t = np.linspace(0, 1, n)
%      x = x0 + R*np.cos(2*np.pi*t)
%      y = y0 + R*np.sin(2*np.pi*t)
%      return x, y
%  
%  x, y = circle(2.0, 0, 0)
% 
% % Often in an exercise we have some comments about the solution
% % which we normally want to keep where they are.
% 
% The goal of this project is to draw $N$ circles with random
% center and radius. Plot each circle using the |circle| function
% above.
% 
% % --- begin subexercise ---
% *a)* Let $R$ be normally distributed and $(x_0,y_0)$ uniformly distributed.
% 
% % --- begin hint in exercise ---
% 
% *Hint.* Use the |numpy.random| module to draw the
% $x_0$, $y_0$, and $R$ quantities.
% 
% % --- end hint in exercise ---
% 
% % --- begin answer of exercise ---
% *Answer.* Here goes the short answer to part a).
% % --- end answer of exercise ---
% 
% % --- begin solution of exercise ---
% *Solution.* Here goes a full solution to part a).
% % --- end solution of exercise ---
% 
% % --- end subexercise ---
% 
% % --- begin subexercise ---
% *b)* Let $R$ be uniformly distributed and $(x_0,y_0)$ normally distributed.
% Filename: |norm|.
% 
% % --- end subexercise ---
% 
% % --- begin subexercise ---
% *c)* Let $R$ and $(x_0,y_0)$ be normally distributed.
% 
% % --- end subexercise ---
% 
% Filename: |circles|.
% 
% % Closing remarks for this Project
% 
%% Remarks
% At the very end of the exercise it may be appropriate to summarize
% and give some perspectives.
% 
% % --- end exercise ---
% 
% % --- begin exercise ---
% 
%% Exercise 6: Determine some Distance
% 
% Intro to this exercise. Questions are in subexercises below.
% 
% % --- begin solution of exercise ---
% *Solution.* Here goes a full solution of the whole exercise.
% With some math $a=b$ in this solution:
% $$\hbox{math in solution: } a = b$$
% And code |a=b| in this solution:
!bc
%  a = b  # code in solution
% End of solution is here.
% 
% % --- end solution of exercise ---
% 
% % --- begin subexercise ---
% *a)* Subexercises are numbered a), b), etc.
% 
% % --- begin hint in exercise ---
% 
% *Hint 1.* First hint to subexercise a).
% With math $a=b$ in hint:
% 
% $$a=b.$$
% And with code (in plain verbatim) returning $x+1$ in hint:
% 
!bc
%  def func(x):
%      return x + 1  # with code in hint
% 
% % --- end hint in exercise ---
% 
% % --- begin hint in exercise ---
% 
% *Hint 2.* Second hint to subexercise a).
% 
% Test list in hint:
% 
% # item1
% 
% # item2
% 
% % --- end hint in exercise ---
% Filename: |subexer_a.pdf|.
% 
% % --- begin answer of exercise ---
% *Answer.* Short answer to subexercise a).
% With math in answer: $a=b$.
% % --- end answer of exercise ---
% 
% % --- end subexercise ---
% 
% % --- begin subexercise ---
% *b)* Here goes the text for subexercise b).
% 
% Some math $\cos^2 x + \sin^2 x = 1$ written one a single line:
% 
% $$\cos^2 x + \sin^2 x = 1 \thinspace .$$
% 
% % --- begin hint in exercise ---
% 
% *Hint.* A hint for this subexercise.
% 
% % --- end hint in exercise ---
% Filename: |subexer_b.pdf|.
% 
% % --- begin solution of exercise ---
% *Solution.* Here goes the solution of this subexercise.
% % --- end solution of exercise ---
% 
% % No meaning in this weired test example:
% The text here belongs to the main (intro) part of the exercise. Need
% closing remarks to have text after subexercises.
% 
% Test list in exercise:
% 
% # item1
% 
% # item2
% 
% % --- end subexercise ---
% 
% % Closing remarks for this Exercise
% 
%% Remarks
% Some final closing remarks, e.g., summarizing the main findings
% and their implications in other problems can be made. These
% remarks will appear at the end of the typeset exercise.
% 
% % --- end exercise ---
% 
% % --- begin exercise ---
% 
%% Some exercise without the "Exercise:" prefix
% 
% % Another minimalistic exercise
% 
% Just some text. And some math saying that $e^0=1$ on a single line,
% to test that math block insertion is correct:
% 
% $$\exp{(0)} = 1$$
% 
% And a test that the code |lambda x: x+2| is correctly placed here:
% 
!bc
%  lambda x: x+2
% 
% % Have some comments at the end of the exercise to see that
% % the Filename: ... is written correctly.
% % --- end exercise ---
% 
% % --- begin exercise ---
% 
%% Exercise 8: Solution of differential equation
% 
% % --- begin quiz ---
% % --- quiz heading: SOlution of differential equation
% % --- previous heading type: exercise
% % --- keywords: ['derivatives', 'exponential function', 'equation, differential', 'differential equation']
% 
% % --- begin quiz question ---
% Given
% 
% $$\frac{dy}{dx} = -y(x),\quad y(0)=1$$
% What is the solution of this equation?
% % --- end quiz question ---
% % --- label: quiz:diff:eq1
% 
% % --- begin quiz choice 1 (right) ---
% $y=e^{-y}$
% % --- end quiz choice 1 (right) ---
% 
% % --- begin quiz choice 2 (wrong) ---
% $y=e^{y}$
% % --- end quiz choice 2 (wrong) ---
% 
% % --- begin explanation of choice 2 ---
% Almost, but the sign is wrong (note the minus!).
% % --- end explanation of choice 2 ---
% 
% % --- begin quiz choice 3 (wrong) ---
%  from math import exp
%  def f(x):
%      return exp(x)
% % --- end quiz choice 3 (wrong) ---
% 
% % --- begin explanation of choice 3 ---
% Ooops, forgot a minus: |exp(-x)|, otherwise this Python code
% must be considered as a good answer. It is more natural,
% though, to write the solution to the problem
% in mathematical notation:
% 
% $$y(x) = e^{-y}.$$
% % --- end explanation of choice 3 ---
% 
% % --- begin quiz choice 4 (wrong) ---
% The solution cannot be found because there is a derivative in the equation.
% % --- end quiz choice 4 (wrong) ---
% 
% % --- begin explanation of choice 4 ---
% Equations with derivatives can be solved;
% they are termed _differential
% equations_.
% % --- end explanation of choice 4 ---
% 
% % --- begin quiz choice 5 (wrong) ---
% The equation is meaningless: an equation must be an equation
% for $x$ or $y$, not a function $y(x)$.
% % --- end quiz choice 5 (wrong) ---
% 
% % --- begin explanation of choice 5 ---
% Equations where the unknown is a function, as $y(x)$
% here, are called _differential equations_, and are solved by
% special techniques.
% % --- end explanation of choice 5 ---
% % --- end quiz ---
% 
% % --- end exercise ---
% 
% % --- begin exercise ---
% 
%% Example 9: Just an example
% 
% % This example needs the --examples_as_exercises option, otherwise
% % it is just typeset as it is written.
% 
% % --- begin subexercise ---
% *a)* What is the capital of Norway?
% 
% *Answer.* Oslo.
% 
% % --- end subexercise ---
% 
% % --- end exercise ---
% 
%% Here goes another section
% 
% With some text, before we continue with exercises.
% 
%% More Exercises
% 
% % --- begin exercise ---
% 
%% Exercise 10: Make references to projects and problems
% 
% % Test comments not at the end only
% Pick a statement from "Project 5: Explore Distributions of Random Circles" or "Problem 2: Flip a Coin"
% and verify it.
% 
% Test list at the end of an exercise without other elements (like subexercise,
% hint, etc.):
% 
% # item1
% 
% # item2
% 
% Filename: |verify_formula.py|.
% 
% % --- end exercise ---
% 
% % --- begin exercise ---
% 
%% Project 11: References to "Project 4: Compute a Probability" in a heading works for matlabnb
% 
% Refer to the previous exercise as "Exercise 10: Make references to projects and problems",
% the two before that as "Project 4: Compute a Probability" and "Project 5: Explore Distributions of Random Circles",
% and this one as "Project 11: References to Project ref{demo:ex:2} in a heading works for matlabnb".
% Filename: |selc_composed.pdf|.
% 
% % --- end exercise ---
% 
%% References
% 
%  # *H. P. Langtangen and G. Pedersen*.  Propagation of Large Destructive Waves, _International Journal of Applied Mechanics and Engineering_, 7(1), pp. 187-204, 2002.
% 
%  # *H. P. Langtangen, K.-A. Mardal and R. Winther*.  Numerical Methods for Incompressible Viscous Flow, _Advances in Water Resources_, 25, pp. 1125-1146, 2002.
% 
%  # *H. P. Langtangen*.  Numerical Solution of First Passage Problems in Random Vibrations, _SIAM Journal of Scientific and Statistical Computing_, 15, pp. 997-996, 1994.
% 
%  # *K.-A. Mardal, G. W. Zumbusch and H. P. Langtangen*.  Software Tools for Multigrid Methods, _Advanced Topics in Computational Partial Differential Equations -- Numerical Methods and Diffpack Programming_, edited by *H. P. Langtangen and A. Tveito*, Springer, 2003, Edited book, <http://some.where.org>.
% 
%  # *H. P. Langtangen*.  The FEMDEQS Program System, _Department of Mathematics, University of Oslo_, 1989, <http://www.math.uio.no/old/days/hpl/femdeqs.pdf>.
% 
%  # *H. P. Langtangen*.  Stochastic Breakthrough Time Analysis of an Enhanced Oil Recovery Process, _SIAM Journal on Scientific Computing_, 13, pp. 1394-1417, 1992.
% 
%  # *M. Mortensen, H. P. Langtangen and G. N. Wells*.  A FEniCS-Based Programming Framework for Modeling Turbulent Flow by the Reynolds-Averaged Navier-Stokes Equations, _Advances in Water Resources_, 34(9), doi: 10.1016/j.advwatres.2011.02.013 <https://dx.doi.org/10.1016/j.advwatres.2011.02.013>, 2011.
% 
%  # *S. Glimsdal, G. Pedersen, K. Atakan, C. B. Harbitz, H. P. Langtangen and F. L\ovholt*.  Propagation of the Dec. 26, 2004 Indian Ocean Tsunami: Effects of Dispersion and Source Characteristics, _International Journal of Fluid Mechanics Research_, 33(1), pp. 15-43, 2006.
% 
%  # *S. Rahman, J. Gorman, C. H. W. Barnes, D. A. Williams and H. P. Langtangen*.  Numerical Investigation of a Piezoelectric Surface Acoustic Wave Interaction With a One-Dimensional Channel, _Physical Review B: Condensed Matter and Materials Physics_, 74, 2006, 035308.
% 
% # *J. B. Haga, H. Osnes and H. P. Langtangen*.  On the Causes of Pressure Oscillations in Low-Permeable and Low-Compressible Porous Media, _International Journal of Analytical and Numerical Methods in Geomechanics_, doi: 10.1002/nag.1062 <https://dx.doi.org/10.1002/nag.1062>, 2011, <http://onlinelibrary.wiley.com/doi/10.1002/nag.1062/abstract>.
% 
% # *H. P. Langtangen*.  _Computational Partial Differential Equations - Numerical Methods and Diffpack Programming_, second edition, _Texts in Computational Science and Engineering_, Springer, 2003.
% 
% # *H. P. Langtangen*.  _Python Scripting for Computational Science_, third edition, _Texts in Computational Science and Engineering_, Springer, 2008.
% 
% # *H. P. Langtangen and G. Pedersen*.  Finite Elements for the Boussinesq Wave Equations, Waves and Non-linear Processes in Hydrodynamics, edited by *J. Grue, B. Gjevik and J. E. Weber*, Kluwer Academic Publishers, pp. pp. 117-126, 1995, <http://www.amazon.ca/Waves-Nonlinear-Processes-Hydrodynamics-John/dp/0792340310>.
% 
% # *H. P. Langtangen*.  _A Primer on Scientific Programming With Python_, third edition, _Texts in Computational Science and Engineering_, Springer, 2012.
% 
% # *P. V. Jeberg, H. P. Langtangen and C. B. Terp*.  Optimization With Diffpack: Practical Example From Welding, _Simula Research Laboratory_, 2004, Internal report.
% 
% # *H. P. Langtangen*.  Computational Methods for Two-Phase Flow in Oil Reservoirs, Ph.D. Thesis, Mechanics Division, Department of Mathematics, University of Oslo, 1989, Dr. Scient. thesis..
% 
% # *H. P. Langtangen*.  Computational Modeling of Huge Tsunamis From Asteroid Impacts, 2007, Invited keynote lecture at the \emphInternational conference on Computational Science 2007 (ICCS'07), Beijing, China.
% 
% # *H. P. Langtangen*.  Solution of the Navier-Stokes Equations With the Finite Element Method in Two and Three Dimensions, M.Sc. Thesis, Mechanics Division, Department of Mathematics, University of Oslo, 1985, Cand.Scient. thesis.
% 
% # *H. P. Langtangen and A. Tveito*.  Numerical Methods in Continuum Mechanics, _Center for Industrial Research_, 1991, Lecture notes for a course (ME-IN 324). 286 pages..
% 
% # *H. P. Langtangen*.  Diffpack: Software for Partial Differential Equations, _Proceedings of the Second Annual Object-Oriented Numerics Conference (OON-SKI'94), Sunriver, Oregon, USA_, edited by *A. Vermeulen*, 1994.
% 
%% Appendix: Just for testing; part I
% 
% This is the first appendix.
% 
%% A subsection within an appendix
% 
% Some text.
% 
%% Appendix: Just for testing; part II
% 
% This is more stuff for an appendix.
% 
%% Appendix: Testing identical titles
% 
% Without label.
% 
%% Appendix: Testing identical titles
% 
% With label.
% 
%% Appendix: Testing identical titles
% 
% What about inserting a quiz?
% 
% % --- begin quiz ---
% % --- new quiz page: Test of quizzes
% % --- quiz heading: Capital of Norway
% % --- previous heading type: subsection
% % --- keywords: ['capitals', 'basic intelligence', 'geography']
% 
% % --- begin quiz question ---
% [Fundamental test:] What is the capital of Norway?
% % --- end quiz question ---
% 
% % --- begin quiz choice 1 (wrong) ---
% [Answer 1:] Stockholm
% % --- end quiz choice 1 (wrong) ---
% 
% % --- begin explanation of choice 1 ---
% Stockholm is the capital of Sweden.
% % --- end explanation of choice 1 ---
% 
% % --- begin quiz choice 2 (wrong) ---
% [Answer 2:] London
% % --- end quiz choice 2 (wrong) ---
% 
% % --- begin quiz choice 3 (right) ---
% [Answer 3:] Oslo
% % --- end quiz choice 3 (right) ---
% 
% % --- begin quiz choice 4 (wrong) ---
% Bergen
% % --- end quiz choice 4 (wrong) ---
% 
% % --- begin explanation of choice 4 ---
% Those from Bergen would claim so, but nobody else.
% % --- end explanation of choice 4 ---
% % --- end quiz ---
% 
%% Appendix: Testing identical titles
% 
% Without label.
% 
% !bnotice Tip
% Here is a tip or hint box, typeset as a notice box.
% !enotice
% 
% Need a lot of text to surround the summary box.
% Version control systems allow you to record the history of files
% and share files among several computers and collaborators in a
% professional way. File changes on one computer are updated or
% merged with changes on another computer. Especially when working
% with programs or technical reports it is essential
% to have changes documented and to
% ensure that every computer and person involved in the project
% have the latest updates of the files.
% Greg Wilson' excellent Script for Introduction to Version Control <https://software-carpentry.org/2010/07/script-for-introduction-to-version-control/> provides a more detailed motivation why you will benefit greatly
% from using version control systems.
% 
% !bsummary
% *Bold remark:* Make some text with this summary.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% Much testing in this document, otherwise stupid content.
% !esummary
% 
% Projects that you want to share among several computers or project
% workers are today most conveniently stored at some web site "in the
% cloud" and updated through communication with that site. I strongly
% recommend you to use such sites for all serious programming and
% scientific writing work - and all other important files.
% 
% The simplest services for hosting project files are Dropbox <https://dropbox.com> and Google Drive <https://drive.google.com>.
% It is very easy to get started with these systems, and they allow you
% to share files among laptops and mobile units with as many users as
% you want. The systems offer a kind of version control in that the
% files are stored frequently (several times per minute), and you can go
% back to previous versions for the last 30 days. However, it is
% challenging  to find the right version from the past when there are
% so many of them.
% 
% More seriously, when several people may edit files simultaneously, it
% can be difficult detect who did what when, roll back to previous
% versions, and to manually merge the edits when these are
% incompatible. Then one needs more sophisticated tools than Dropbox or
% Google Drive: project hosting services with true version control
% systems.  The following text aims at providing you with the minimum
% information to started with such systems. Numerous other tutorials
% contain more comprehensive material and in-depth explanations of the
% concepts and tools.
% 
% The idea with project hosting services is that you have the files
% associated with a project in the cloud. Many people may share these
% files.  Every time you want to work on the project you explicitly
% update your version of the files, edit the files as you like, and
% synchronize the files with the "master version" at the site where the
% project is hosted.  If you at some point need to go back to a
% version of the files at some particular point in the past,
% this is an easy operation. You can also use tools to see
% what various people have done with the files in the various versions.
% 
% All these services are very similar. Below we describe how you get
% started with Bitbucket, GitHub, and Googlecode. Launchpad works very
% similarly to the latter three. All the project hosting services have
% excellent introductions available at their web sites, but the recipes
% below are much shorter and aim at getting you started as quickly as
% possible by concentrating on the most important need-to-know steps.
% The Git tutorials we refer to later in this document contain more
% detailed information and constitute of course very valuable readings
% when you use version control systems every day. The point now is
% to get started.
% 
%% Appendix: Testing inline comments
% 
% % Names can be [ A-Za-z0-9_'+-]+
% 
% Projects that you want to share among several computers or project
% workers are today most conveniently stored at some web site "in the
% cloud" and updated through communication with that
% site. [hpl's semi opinion 1: not sure if in the cloud is
% understood by
% all.] I strongly recommend you to use such sites for all serious
% programming and scientific writing work - and all other important
% files.
% 
% The simplest services for hosting project files is Dropbox. [mp 2: Simply go to <https://dropbox.com> and watch the video. It explains
% how files, like |myfile.py|, perhaps containing much math, like
% $\partial u/\partial t$, are easily communicated between machines.] It
% is very easy to get started with Dropbox, and it allows you to share
% files among [hpl 3: laptops and mobile units -> computers, tablets,
% and phones].
% 
% % Test horizontal rule
% 
% ------
% 
% % Coments for editing
% 
% First[add 4: ,] consider a quantity $Q$. [edit 5: To this end, -> We note that]
% $Q>0$, because [del 6: a] negative [edit 7: quantity is -> quantities
% are] [del 8: just] negative. [add 9: This comes as no surprise.]
% 
% % Test tailored latex figure references with page number
% Let us refer to Figure ref{fig:impact} again.
% 
% Test references in a list:
% 
%  * "Section 1"
% 
%  * "Subsection 1"
% 
%  * ref{fig:impact}
% 
%% Appendix: Testing headings ending with |verbatim inline|
% 
% The point here is to test 1) |verbatim| code in headings, and 2)
% ending a heading with verbatim code as this triggers a special
% case in LaTeX.
% 
% We also test mdash---used as alternative to hyphen without spaces around,
% or in quotes:
% 
% !bquote
% _Fun is fun_.---Unknown.
% !equote
% 
% The ndash should also be tested - as in the Hanson - Nilson equations
% on page 277 - 278.
% 
% And finally, what about admons, quotes, and boxes? They are tested
% in a separate document: |admon.do.txt|.
% 
% [^example-of-the-third-footnote]: Not much to add here, but the footnote
% is at the end with only one newline.
