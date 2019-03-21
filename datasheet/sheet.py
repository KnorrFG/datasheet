import pickle
from functools import wraps

import matplotlib.figure
import matplotlib.pyplot as plt
import nibabel as nib
import pandas as pd
from joblib import Memory
from joblib.memory import MemorizedFunc

from .html_renderer import render_html
from .types import *

class Sheet:
    """Main class of the library
    
    :param str outdir: The output directory, in which all files are stored.
    :var dict type_wrap_map: Defines the mapping from input types to 
        `ElementInterface` s. It is not possible to use tuple as key, as that will be
        ignored, because it is required for the special treatment the `MultiCell`
        Interface needs
    """
    def __init__(self, outdir: str):
        self.outdir = Path(outdir)
        self.entries = []
        self._mem = Memory(outdir, verbose=0)

    type_wrap_map = {
        str: MD,
        pd.DataFrame: DF,
        nib.Nifti1Image: Nifti,
        matplotlib.figure.Figure: Figure
    }

    @staticmethod
    def _wrap_obj(obj):
        return obj if isinstance(obj, ElementInterface) \
            else Sheet.type_wrap_map.get(type(obj), Repr)(obj)

    def _store_if_has_save_dir(self, obj):
        if hasattr(obj, "save_to_dir"):
            obj.save_to_dir(self.outdir)

    def __lshift__(self, obj: Any):
        """Object adding operator, automatically wraps passed objects into
        fitting type wrappers according to Sheet.type_wrap_map"""
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
        """Renders the sheet to some sort of file(s).

        To customize render options use the renderfunction directly.
        Currently, the only existing renderer is the HTML renderer
        """
        renderer(self.entries, self.outdir)

    def cache(self, func, **cache_args)-> MemorizedFunc:
        """Datasheet automatically creates a 
        `joblib.Memory <https://joblib.readthedocs.io/en/latest/auto_examples/memory_basic_usage.html>`_
        object, with the outdir as cache dir, to have easy access to persistent
        caching. This method exposes the memory-object's cache() method."""
        return self._mem.cache(func, **cache_args)

    def gate_cache(self, func, recompute, key=None):
        """Wraps a function. The returned function will execute the wrapped function 
        and store the results, if it does not find a saved result already.
        If recompute is True the wrapped function will also be executed if a saved 
        result is found. If a stored result is found, and recompute is False the wrapped
        function will always return the stored result, independent of the calling 
        parameters, or whether the source code of the cached function changed.
        
        the key parameter determines the save file. By default the name of the wrapped
        function is used. In case of wanting to save multiple results for one function,
        it can be wrapped multiple times with different keys"""
        self.outdir.joinpath("gate_cache").mkdir(parents=True, exist_ok=True)
        save_path = self.outdir/"gate_cache"/((key or func.__name__) + ".pkl")
        @wraps(func)
        def gated_func(*args, **kwargs):
            if recompute or not save_path.exists():
                result = func(*args, **kwargs)
                with save_path.open("wb") as f:
                    pickle.dump(result, f)
                return result
            else:
                with save_path.open("rb") as f:
                    return pickle.load(f)
        return gated_func

    def add_current_figure(self, clear: bool = True, **fig_args):
        """Convinienve method to add the current figure, and optionally clear
        it afterwards.
        
        :param bool clear: whether or not to clear the figue
        :param fig_args: forwarded to `Figure`"""
        self << Figure(plt.gcf(), **fig_args)
        if clear:
            plt.clf()
