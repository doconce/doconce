% How various formats can deal with LaTeX math
% **Hans Petter Langtangen** at Simula Research Laboratory and University of Oslo
% Jan 32, 2100
*Summary.* The purpose of this document is to test LaTeX math in DocOnce with
various output formats.  Most LaTeX math constructions are renedered
correctly by MathJax in plain HTML, but some combinations of
constructions may fail.  Unfortunately, only a subset of what works in
html MathJax also works in sphinx MathJax. The same is true for
markdown MathJax expresions (e.g., Jupyter notebooks).  Tests and
examples are provided to illustrate what may go wrong.

The recommendation for writing math that translates to MathJax in
html, sphinx, and markdown is to stick to the environments `\[
... \]`, `equation`, `equation*`, `align`, `align*`, `alignat`, and
`alignat*` only. Test the math with sphinx output; if it works in that
format, it should work elsewhere too.

The current version of the document is translated from DocOnce source
to the format **pandoc**.



## Test of equation environments

### Test 1: Inline math

We can get an inline equation
`$u(t)=e^{-at}$` rendered as $u(t)=e^{-at}$.

### Test 2: A single equation with label

An equation with number,


~~~
!bt
\begin{equation} u(t)=e^{-at} \label{eq1a}\end{equation}
!et
~~~

looks like

$$
\begin{equation} u(t)=e^{-at} \label{_eq1a}\end{equation}
$$
Maybe this multi-line version is what we actually prefer to write:


~~~
!bt
\begin{equation}
u(t)=e^{-at}
\label{eq1b}
\end{equation}
!et
~~~

The result is the same:

$$
\begin{equation}
u(t)=e^{-at} \label{_eq1b}
\end{equation}
$$
We can refer to this equation through its label `eq1b`: ([_eq1b](#_eq1b)).

### Test 3: Multiple, aligned equations without label and number

MathJax has historically had some problems with rendering many LaTeX
math environments, but the `align*` and `align` environments have
always worked.


~~~
!bt
\begin{align*}
u(t)&=e^{-at}\\ 
v(t) - 1 &= \frac{du}{dt}
\end{align*}
!et
~~~

Result:

$$
\begin{align*}
u(t)&=e^{-at}\\ 
v(t) - 1 &= \frac{du}{dt}
\end{align*}
$$

### Test 4: Multiple, aligned equations with label

Here, we use `align` with user-prescribed labels:


~~~
!bt
\begin{align}
u(t)&=e^{-at}
\label{eq2b}\\ 
v(t) - 1 &= \frac{du}{dt}
\label{eq3b}
\end{align}
!et
~~~

Result:

$$
\begin{align}
u(t)&=e^{-at}
\label{_eq2b}\\ 
v(t) - 1 &= \frac{du}{dt}
\label{_eq3b}
\end{align}
$$
We can refer to the last equations as the system ([_eq2b](#_eq2b))-([_eq3b](#_eq3b)).

### Test 5: Multiple, aligned equations without label

In LaTeX, equations within an `align` environment is automatically
given numbers.  To ensure that an html document with MathJax gets the
same equation numbers as its latex/pdflatex companion, DocOnce
generates labels in equations where there is no label prescribed. For
example,


~~~
!bt
\begin{align}
u(t)&=e^{-at}
\\ 
v(t) - 1 &= \frac{du}{dt}
\end{align}
!et
~~~

is edited to something like


~~~
!bt
\begin{align}
u(t)&=e^{-at}
\label{_auto5}\\ 
v(t) - 1 &= \frac{du}{dt}
\label{_auto6}
\end{align}
!et
~~~

and the output gets the two equation numbered.

$$
\begin{align}
u(t)&=e^{-at}\\ 
v(t) - 1 &= \frac{du}{dt}
\end{align}
$$

### Test 6: Multiple, aligned equations with multiple alignments

The `align` environment can be used with two `&` alignment characters, e.g.,


~~~
!bt
\begin{align}
\frac{\partial u}{\partial t} &= \nabla^2 u, & x\in (0,L),
\ t\in (0,T]\\ 
u(0,t) &= u_0(x), & x\in [0,L]
\end{align}
!et
~~~

The result in pandoc becomes

$$
\begin{align}
\frac{\partial u}{\partial t} &= \nabla^2 u, & x\in (0,L),
\ t\in (0,T]\\ 
u(0,t) &= u_0(x), & x\in [0,L]
\end{align}
$$

A better solution is usually to use an `alignat` environment:


~~~
!bt
\begin{alignat}{2}
\frac{\partial u}{\partial t} &= \nabla^2 u, & x\in (0,L),
\ t\in (0,T]\\ 
u(0,t) &= u_0(x), & x\in [0,L]
\end{alignat}
!et
~~~

with the rendered result

$$
\begin{alignat}{2}
\frac{\partial u}{\partial t} &= \nabla^2 u, & x\in (0,L),
\ t\in (0,T]\\ 
u(0,t) &= u_0(x), & x\in [0,L]
\end{alignat}
$$

If DocOnce had not rewritten the above equations, they would be
rendered in pandoc as

$$
\begin{alignat}{2}
\frac{\partial u}{\partial t} &= \nabla^2 u, & x\in (0,L),
\ t\in (0,T]\\ 
u(0,t) &= u_0(x), & x\in [0,L]
\end{alignat}
$$

### Test 7: Multiple, aligned eqnarray equations without label

Let us try the old `eqnarray*` environment.


~~~
!bt
\begin{eqnarray*}
u(t)&=& e^{-at}\\ 
v(t) - 1 &=& \frac{du}{dt}
\end{eqnarray*}
!et
~~~

which results in

$$
\begin{eqnarray*}
u(t)&=& e^{-at}\\ 
v(t) - 1 &=& \frac{du}{dt}
\end{eqnarray*}
$$

### Test 8: Multiple, eqnarrayed equations with label

Here we use `eqnarray` with labels:


~~~
!bt
\begin{eqnarray}
u(t)&=& e^{-at}
\label{eq2c}\\ 
v(t) - 1 &=& \frac{du}{dt}
\label{eq3c}
\end{eqnarray}
!et
~~~

which results in

$$
\begin{eqnarray}
u(t)&=& e^{-at} \label{_eq2c}\\ 
v(t) - 1 &=& \frac{du}{dt} \label{_eq3c}
\end{eqnarray}
$$
Can we refer to the last equations as the system ([_eq2c](#_eq2c))-([_eq3c](#_eq3c))
in the pandoc format?

### Test 9: The `multiline` environment with label and number

The LaTeX code


~~~
!bt
\begin{multline}
\int_a^b f(x)dx = \sum_{j=0}^{n} \frac{1}{2} h(f(a+jh) +
f(a+(j+1)h)) \\ 
=\frac{h}{2}f(a) + \frac{h}{2}f(b) + \sum_{j=1}^n f(a+jh)
\label{multiline:eq1}
\end{multline}
!et
~~~

gets rendered as

$$
\begin{multline}
\int_a^b f(x)dx = \sum_{j=0}^{n} \frac{1}{2} h(f(a+jh) +
f(a+(j+1)h)) \\ 
=\frac{h}{2}f(a) + \frac{h}{2}f(b) + \sum_{j=1}^n f(a+jh)
\label{_multiline:eq1}
\end{multline}
$$
and we can hopefully refer to the Trapezoidal rule
as the formula ([_multiline:eq1](#_multiline:eq1)).

### Test 10: Splitting equations using a split environment

Although `align` can be used to split too long equations, a more obvious
command is `split`:


~~~
!bt
\begin{equation}
\begin{split}
\int_a^b f(x)dx = \sum_{j=0}^{n} \frac{1}{2} h(f(a+jh) +
f(a+(j+1)h)) \\ 
=\frac{h}{2}f(a) + \frac{h}{2}f(b) + \sum_{j=1}^n f(a+jh)
\end{split}
\end{equation}
!et
~~~

The result becomes

$$
\begin{equation}
\begin{split}
\int_a^b f(x)dx = \sum_{j=0}^{n} \frac{1}{2} h(f(a+jh) +
f(a+(j+1)h)) \\ 
=\frac{h}{2}f(a) + \frac{h}{2}f(b) + \sum_{j=1}^n f(a+jh)
\end{split}
\end{equation}
$$

### Test 11: Newcommands and boldface bm vs pmb

First we use the plain old pmb package for bold math. The formula


~~~
!bt
\[ \frac{\partial\u}{\partial t} +
\u\cdot\nabla\u = \nu\nabla^2\u -
\frac{1}{\varrho}\nabla p,\]
!et
~~~

and the inline expression `$\nabla\pmb{u} (\pmb{x})\cdot\pmb{n}$`
(with suitable newcommands using pmb)
get rendered as

$$
 \frac{\partial\pmb{u}}{\partial t} +
\pmb{u}\cdot\nabla\pmb{u} = \nu\nabla^2\pmb{u} -
\frac{1}{\varrho}\nabla p,
$$
and $\nabla\pmb{u} (\pmb{x})\cdot\pmb{n}$.

Somewhat nicer fonts may appear with the more modern `\bm` command:


~~~
!bt
\[ \frac{\partial\ubm}{\partial t} +
\ubm\cdot\nabla\ubm = \nu\nabla^2\ubm -
\frac{1}{\varrho}\nabla p,\]
!et
~~~

(backslash `ubm` is a newcommand for bold math $u$), for which we get

$$
 \frac{\partial\boldsymbol{u}}{\partial t} +
\boldsymbol{u}\cdot\nabla\boldsymbol{u} = \nu\nabla^2\boldsymbol{u} -
\frac{1}{\varrho}\nabla p.
$$
Moreover,


~~~
$\nabla\boldsymbol{u}(\boldsymbol{x})\cdot\boldsymbol{n}$
~~~

becomes $\nabla\boldsymbol{u}(\boldsymbol{x})\cdot\boldsymbol{n}$.

*Warning.* 
Note: for the pandoc format, `\bm` was substituted by DocOnce
to `\boldsymbol`.



## Problematic equations

Finally, we collect some problematic formulas in MathJax. They all work
fine in LaTeX. Most of them look fine in html too, but some fail in
sphinx, ipynb, or markdown.

### Colored terms in equations

The LaTeX code


~~~
!bt
\[ {\color{blue}\frac{\partial\u}{\partial t}} +
\nabla\cdot\nabla\u = \nu\nabla^2\u -
\frac{1}{\varrho}\nabla p,\]
!et
~~~

results in

$$
 {\color{blue}\frac{\partial\pmb{u}}{\partial t}} +
\nabla\cdot\nabla\pmb{u} = \nu\nabla^2\pmb{u} -
\frac{1}{\varrho}\nabla p,
$$

### Bar over symbols

Sometimes one must be extra careful with the LaTeX syntax to get sphinx MathJax
to render a formula correctly. Consider the combination of a bar over a
bold math symbol:


~~~
!bt
\[ \bar\f = f_c^{-1}\f,\]
!et
~~~

which for pandoc output results in

$$
 \bar\boldsymbol{f} = f_c^{-1}\boldsymbol{f}.
$$

With sphinx, this formula is not rendered. However, using curly braces for the bar,


~~~
!bt
\[ \bar{\f} = f_c^{-1}\f,\]
!et
~~~

makes the output correct also for sphinx:

$$
 \bar{\boldsymbol{f}} = f_c^{-1}\boldsymbol{f},
$$

### Matrix formulas

Here is an `align` environment with a label and the `pmatrix`
environment for matrices and vectors in LaTeX.


~~~
!bt
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
+ \cdots
\label{mymatrixeq}\\ 
\begin{pmatrix}
C_5 + C_6 & -C_6 & 0 & 0 \\ 
-C_6 & C_6 & 0 & 0 \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0
\end{pmatrix}
\frac{d}{dt} &=
\begin{pmatrix}
v_1 \\ 
v_2 \\ 
v_3 \\ 
v_4
\end{pmatrix} =
\begin{pmatrix}
0 \\ 
0 \\ 
0 \\ 
-i_0
\end{pmatrix}
\end{align}
!et
~~~

which becomes

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
+ \cdots
\label{_mymatrixeq}\\ 
\begin{pmatrix}
C_5 + C_6 & -C_6 & 0 & 0 \\ 
-C_6 & C_6 & 0 & 0 \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0
\end{pmatrix}
\frac{d}{dt} &=
\begin{pmatrix}
v_1 \\ 
v_2 \\ 
v_3 \\ 
v_4
\end{pmatrix} =
\begin{pmatrix}
0 \\ 
0 \\ 
0 \\ 
-i_0
\end{pmatrix}
\end{align}
$$

The same matrices without labels in an `align*` environment:


~~~
!bt
\begin{align*}
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
\frac{d}{dt} &=
\begin{pmatrix}
v_1 \\ 
v_2 \\ 
v_3 \\ 
v_4
\end{pmatrix} =
\begin{pmatrix}
0 \\ 
0 \\ 
0 \\ 
-i_0
\end{pmatrix}
\end{align*}
!et
~~~

The rendered result becomes

$$
\begin{align*}
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
\frac{d}{dt} &=
\begin{pmatrix}
v_1 \\ 
v_2 \\ 
v_3 \\ 
v_4
\end{pmatrix} =
\begin{pmatrix}
0 \\ 
0 \\ 
0 \\ 
-i_0
\end{pmatrix}
\end{align*}
$$

