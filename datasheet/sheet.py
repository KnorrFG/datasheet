import pickle
from functools import wraps

import matplotlib
matplotlib.use('agg')
import matplotlib.figure
import matplotlib.pyplot as plt
import nibabel as nib
import pandas as pd
from joblib import Memory
from joblib.memory import MemorizedFunc

from .html_renderer import HTMLRenderer
from .types import *


class Sheet:
    """Main class of the library

    :param str out: The output directory or file.
    :param bool standalone: 
        If this option is set to `True` the output will be a single file,
        In case of the HTMLRenderer that means images are encoded as base64 and
        niftis are not supported as those can't be displayed without saving them.
    :var dict type_wrap_map: Defines the mapping from input types to 
        `ElementInterface` s. It is not possible to use tuple as key, as that will be
        ignored, because it is required for the special treatment the `MultiCell`
        Interface needs
    """

    def __init__(self, out_dir_or_file: str, standalone=False):
        self.out = Path(out_dir_or_file)
        self.entries = VLayout([])
        self.standalone = standalone
        self._mem_ob = None
        
    @property
    def _mem(self):
        if self.standalone:
            raise RuntimeError(
                "Using cache methods is not supported in standalone mode")
        if not self._mem_ob:
            self._mem_ob = Memory(self.out, verbose=0)
        return self._mem_ob

    type_wrap_map = {
        str: MD,
        pd.DataFrame: DF,
        nib.Nifti1Image: Nifti,
        matplotlib.figure.Figure: Figure
    }

    def _wrap_obj(self, obj):
        if isinstance(obj, Layout):
            return type(obj)([self._wrap_obj(elem)
                              for elem in obj.elems])
        elif not isinstance(obj, ElementInterface):
            return Sheet.type_wrap_map.get(type(obj), Repr)(
                obj, dont_save = self.standalone)
        else:
            return obj

    def __lshift__(self, obj: Any):
        """Object adding operator, automatically wraps passed objects into
        fitting type wrappers according to Sheet.type_wrap_map"""
        wrapped_obj = self._wrap_obj(obj)
        wrapped_obj.save_to_dir(self.out)
        self.entries.elems.append(wrapped_obj)

    def render(self, Renderer=HTMLRenderer, **kwargs):
        """Renders the sheet to some sort of file(s).

        kwargs are passes to Renderer.render()
        Currently, the only existing renderer is the HTML renderer
        """
        if self.standalone:
            Renderer.render(self.entries, self.out.parent / 
                            (self.out.name + '.' + Renderer.extension),
                            **kwargs)
        else:
            Renderer.render(self.entries, self.out / Renderer.default_file,
                            **kwargs)

    def cache(self, func, **cache_args) -> MemorizedFunc:
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
        self.out.joinpath("gate_cache").mkdir(parents=True, exist_ok=True)
        save_path = self.out/"gate_cache"/((key or func.__name__) + ".pkl")
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
        self << Figure(plt.gcf(), dont_save=self.standalone, **fig_args)
        if clear:
            plt.clf()
