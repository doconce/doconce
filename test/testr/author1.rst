.. Automatically generated Sphinx-extended reStructuredText file from DocOnce source
   (https://github.com/doconce/doconce/)

.. Document title:

Test of one author at one institution
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:Authors: John Doe (doe at cyberspace.net)
:Date: Jan 32, 2100

.. Externaldocument: testdoc

.. _genrefs:

Generalized References
%%%%%%%%%%%%%%%%%%%%%%

Sometimes a series of individual documents may be assembled to one
large document. The assembly impacts how references to sections
are written: when referring to a section in the same document, a label
can be used, while references to sections in other documents are
written differently, sometimes involving a link (URL) and a citation.
Especially if both the individual documents and the large assembly document
are to exist side by side, a flexible way of referencing is needed.
For this purpose, DocOnce offers *generalized references* which allows
a reference to have two different formulations, one for internal
references and one for external references. Since LaTeX supports
references to labels in external documents via the ``xr`` package,
the generalized references in DocOnce has a syntax that may utilize
the ``xr`` feature in LaTeX.

The syntax of generalized references reads

.. code-block:: text

    ref[internal][cite][external]

If all standard ``ref`` references (with curly braces)
in the text ``internal`` are references
to labels in the present document, the above ``ref`` command is replaced
by the text ``internal``. Otherwise, if cite is non-empty and the format
is ``latex`` or ``pdflatex`` one assumes that the references in ``internal``
are to external documents declared by a comment line ``#
Externaldocuments: testdoc, mydoc`` (usually after the title, authors,
and date). In this case the output text is ``internal cite`` and the
LaTeX package ``xr`` is used to handle the labels in the external documents.
When referring to a complete chapter (not a section in it), which
corresponds to a complete external document, it does not make sense
to write out ``internal cite`` since the ``internal`` reference is a
chapter number. In such cases, the ``internal`` syntax can be used,
and if the label is in another LaTeX document, the output is just ``cite``.
For all
output formats other than ``latex`` and ``pdflatex``, the ``external``
text will be the output.

Here is an example on a specific generalized reference to a section
in a document:

.. code-block:: text

    As explained in
    ref[Section ref{subsec:ex}][in "Langtangen, 2012":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html#subsec:ex"
    cite{testdoc:12}][a "section":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html#subsec:ex" in
    the document "A Document for Testing DocOnce":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html"
    cite{testdoc:12}], DocOnce documents may include tables.

With ``latex`` or ``pdflatex`` as output, this translates to

.. code-block:: text

    As explained in
    Section ref{subsec:ex}, DocOnce documents may include tables.

if the label ``{subsec:ex}`` appears in the present DocOnce source, and
otherwise

.. code-block:: text

    As explained in
    Section ref{subsec:ex} in "Langtangen, 2012":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html#subsec:ex"
    cite{testdoc:12}, DocOnce documents may include tables.

In a format different from ``latex`` and ``pdflatex``, the effective DocOnce
text becomes

.. code-block:: text

    As explained in
    a "section":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html#subsec:ex" in
    the document "A Document for Testing DocOnce":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html"
    cite{testdoc:12}, DocOnce documents may include tables.

The rendered text in the current format ``sphinx`` becomes


..

    As explained in
    a `section <https://hplgit.github.io/doconce/test/demo_testdoc.html#subsec:ex>`__ in
    the document `A Document for Testing DocOnce <https://hplgit.github.io/doconce/test/demo_testdoc.html>`__
    [Ref1]_, DocOnce documents may include tables.



A reference to an entire external document, which is usually a chapter
if the reference is internal in the DocOnce source, applies the
``refch`` syntax:

.. code-block:: text

    As explained in
    refch[Chapter ref{ch:testdoc}]["Langtangen, 2012":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html"
    cite{testdoc:12}][the document
    "A Document for Testing DocOnce":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html"
    cite{testdoc:12}], DocOnce documents may include tables.

The output now if ``ch:testdoc`` is not a label in the document,
becomes in the ``latex`` and ``pdflatex`` case

.. code-block:: text

    As explained in
    "Langtangen, 2012":
    "https://hplgit.github.io/doconce/test/demo_testdoc.html"
    cite{testdoc:12}, DocOnce documents may include tables.

That is, the internal reference ``Chapter ...`` is omitted since
it is not meaningful to refer to an external document as "Chapter".
The resulting rendered text in the current format ``sphinx`` becomes


..

    As explained in
    the document
    `A Document for Testing DocOnce <https://hplgit.github.io/doconce/test/demo_testdoc.html>`__
    [Ref1]_, DocOnce documents may include tables.



Note that LaTeX cannot
have links to local files, so a complete URL on the form
``https://...`` must be used.

And here is another example with internal references only:

.. code-block:: text

    Generalized references are described in ref[Section ref{genrefs}][dummy1][
    dummy2].

The text is rendered to


..

    Generalized references are described in
    the section :ref:`genrefs`.



Test of math
%%%%%%%%%%%%

.. Here we test the chapter heading to see if latex output then has

.. book style rather than article style.

Inline math, :math:`a=b`, is the only math in this document.

.. Need BIBFILE because of cite{} examples

.. [Ref1]
   **H. P. Langtangen**. A Document for Testing Doconce,
   *Simula Research Laboratory*,
   `http://hplgit.github.io/doconce/test/demo_testdoc.html <http://hplgit.github.io/doconce/test/demo_testdoc.html>`_,

