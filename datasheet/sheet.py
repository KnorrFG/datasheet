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

    def _store_if_has_save_dir(self, obj):
        if hasattr(obj, "save_to_dir"):
            obj.save_to_dir(self.outdir)

    def __lshift__(self, obj):
        if type(obj) in (MultiCell, tuple):
            objs = obj.content if type(obj) == MultiCell else obj
            wrapped_obj = MultiCell(tuple(map(Sheet._wrap_obj, objs)))
            for obj in wrapped_obj.content:
                self._store_if_has_save_dir(obj)
        else:
            wrapped_obj = Sheet._wrap_obj(obj)

        self._store_if_has_save_dir(wrapped_obj)
        self.entries.append(wrapped_obj)

    def render(self, renderer=render_html):
        renderer(self.entries, self.outdir)

    def cache(self, func):
        return self._mem.cache(func)
