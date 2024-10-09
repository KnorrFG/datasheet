Datasheet
---------

Datasheet is a Python package that attempts to provide the advantages of a Jupyter Notebook
without the disadvantages. It generates html files that look somewhat similar to
a notebook without the code in it. You can add matplotlib graphs, markdown text, pandas tables
and nifti images with a single line, and get a nice output. For everything else the :code:`repr()`
function is used. Additionally, some simple layouting is supported.

The documentation, which includes an example of a generated report can be found 
`here <https://datasheet.readthedocs.io>`_

Changelog
---------

* Version 1.2.2
	* Removes nifti support, as browsers don't permit loading it anymore without a server,
	  which defeats the purpose
	* Updates the example
	* adds jinja2 dependency as this appears to be neccessary now
* Version 1.2.1
    * Fixes a bug, that caused a crash if an empty string was provided as md
* Version 1.2.0
   * Adds a new Feature: Headings (only those that also show up in the
	TOC) can now be clicked to hide their contents
* Version 1.1.3
   * Automatically creates containing folder on instantiation
* Version 1.1.2
   * Has a new css template for pathfinder
* Version 1.1.1
   * Fixes a bug in gated cache, that wasn't caught by a test before (sorry)
* Version 1.1.0
    * Changes the default CSS to look way nicer, borrowed from 
        https://gist.github.com/killercup/5917178
    * adds stand alone mode
    * adds Layout classes.
    * Removes tuple interpretation by Sheet.__lshift__, use the Layouts instead
* Version 1.0.1
    * set matplotlibs rendering back-end to agg before importing pyplot, so that 
        the library does not depend on tkinter
* Version 1.0 - release
