"""A library to generate HTML pages containing all sorts of output"""

__version__ = "1.1.2"

from .sheet import Sheet
from .types import MD, Str, Repr, DF, Nifti, Figure, VLayout, HLayout
from .html_renderer import HTMLRenderer
