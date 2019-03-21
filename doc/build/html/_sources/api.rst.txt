Api Documentation
=================

.. contents::
    :depth: 2

Sheet
~~~~~
The Sheet is the container holding the information, that is then accessed by 
one of the renderers. A sheet also represents an output directory in which caches and
generated files are stored

.. automodule:: datasheet.sheet
   :members:
   :special-members:
   :exclude-members: __init__, __weakref__


Types
~~~~~

Every object that is added to a Sheet is wrapped in a Type-Object, which is derived
from `ElementInterface` . These classes purpose is to carry information on their 
contained data. If a Type has a *save_to_dir* function it will be called when the
object is added to the sheet.

.. automodule:: datasheet.types
   :members:

Renderer
~~~~~~~~~~~~~
Renderers are responsible for creating a final output file. Currentrly only the 
html_renderer exists, which is automatically called by `datasheet.sheet.Sheet.render`
but to configure the render process it is also possible to call it manually like this:

.. code-block:: python

    renderer(sheet.entries, sheet.outdir, render_arg1, render_arg2)



.. automodule:: datasheet.html_renderer
   :members: