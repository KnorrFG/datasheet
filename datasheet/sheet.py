from dataclasses import dataclass
from functools import wraps
from typing import Any

import matplotlib.figure
import nibabel as nib
import pandas as pd
from joblib import Memory


@dataclass
class ElementInterace:
    content: Any

@dataclass
class MD(ElementInterace):
    """Markdown"""
    offset: int = -1

@dataclass
class Str(ElementInterace):
    """String"""

@dataclass
class Repr(ElementInterace):
    """Adds a repr() of the object"""

@dataclass
class DF(ElementInterace):
    """pandas DataFrame"""

@dataclass
class Nifti(ElementInterace):
    """nibabel.Nifti1Image"""

@dataclass
class Figure(ElementInterace):
    """matplotlib.pyplot.figure"""


def HTMLRenderer(entries, outdir):
    pass


class Sheet:
    def __init__(self, outdir):
        self.outdir = outdir
        self.entries = []
        self._mem = Memory(outdir)

    _type_wrap_map = {
        str: MD,
        pd.DataFrame: DF,
        nib.Nifti1Image: Nifti,
        matplotlib.figure.Figure: Figure
    }

    def __lshift__(self, obj):
        try:
            self.entries.append(obj if isinstance(obj, ElementInterace)
                                else Sheet._type_wrap_map[type(obj)](obj))
        except KeyError:
            raise ValueError(f"Type {type(obj)} not supported")

    def render(self, renderer=HTMLRenderer):
        renderer(self.entries, self.outdir)

    def cache(self, func):
        return self._mem.cache(func)
