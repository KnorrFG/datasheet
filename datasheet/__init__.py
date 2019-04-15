"""A library to generate HTML pages containing all sorts of output"""

__version__ = "1.0"

from .sheet import Sheet
from .types import MD, Str, Repr, DF, Nifti, Figure, MultiCell
from .html_renderer import render_html