from functools import wraps

import matplotlib.figure
import nibabel as nib
import pandas as pd
from joblib import Memory

from .html_renderer import render_html
from .types import *

class Sheet:
    def __init__(self, outdir):
        self.outdir = Path(outdir)
        self.entries = []
        self._mem = Memory(outdir, verbose=0)

    _type_wrap_map = {
        str: MD,
        pd.DataFrame: DF,
        nib.Nifti1Image: Nifti,
        matplotlib.figure.Figure: Figure
    }

    @staticmethod
    def _wrap_obj(obj):
        return obj if isinstance(obj, ElementInterface) \
            else Sheet._type_wrap_map.get(type(obj), Repr)(obj)

    def __lshift__(self, obj):
        if type(obj) == MultiCell:
            wrapped_obj = MultiCell(tuple(map(Sheet._wrap_obj, obj.content)))
        else:
            wrapped_obj = Sheet._wrap_obj(obj)

        if hasattr(wrapped_obj, "save_to_dir"):
            wrapped_obj.save_to_dir(self.outdir)
        self.entries.append(wrapped_obj)

    def render(self, renderer=render_html):
        renderer(self.entries, self.outdir)

    def cache(self, func):
        return self._mem.cache(func)
