from dataclasses import dataclass, InitVar
from typing import Any, ClassVar, List
from pathlib import Path

from io import BytesIO
import base64

def _map_lines(func, s):
    return "\n".join(map(func, s.split("\n")))


@dataclass
class Layout:
    '''Base class for Layouts'''
    elems: List[any]

    def save_to_dir(self, out_dir):
        for e in self.elems:
            e.save_to_dir(out_dir)

    def __iter__(self):
        for elem in self.elems:
            if isinstance(elem, Layout):
                yield from elem
            else:
                yield elem


@dataclass
class ElementInterface:
    """Base class for all other Interfaces.

    To add an interface, 3 steps are neccessary:
    
    1. Define a class for it, which is derived from ElementInterface.
        If it has a method named '_save_to_dir' which takes one argument: the
        output directory, it will be called during 
        `datasheet.sheet.Sheet.__lshift__`. This way it
        is possible to save files, that can be used in the render-handlers.
    2. Optionally define a mapping for a type to be wrapped automatically with
       your new interface by 
       `datasheet.sheet.Sheet.__lshift__` in :code:`Sheet.type_wrap_map`
    
    :param Any content: the actual element
    :param Path rel_save_path: the output path in case a file should be stored,
        if not set, it can be assigned automatically using 
        `ElementInterface.get_outfile`
    """
    content: Any
    rel_save_path: Path = None
    _save_counter: ClassVar[int] = 0
    dont_save: bool = False

    def get_outfile(self, target_dir: Path, ext: str):
        """returns a path for a file, that was not yet used.

        :param Path target_dir: The output directory
        :param str ext: The file extension"""
        if self.rel_save_path is None:
            ElementInterface._save_counter += 1
            self.rel_save_path = f"{ElementInterface._save_counter}.{ext}"
        return target_dir / self.rel_save_path

    def save_to_dir(self, out_dir):
        if hasattr(self, '_save_to_dir') and not self.dont_save:
            self._save_to_dir(out_dir)



@dataclass
class MD(ElementInterface):
    """Markdown
    
    :param offset: the ammount of characters to strip of the left of each line.
        Determined automatically if set to -1.
    """
    offset: InitVar[int] = -1

    def __post_init__(self, offset):
        if self.content == "":
            return 

        if offset < 0:
            offset = min(len(line) - len(line.lstrip())
                         for line in self.content.split("\n") if len(line.strip()) > 0)
        if offset > 0:
            self.content = _map_lines(lambda s: s[offset:], self.content)

@dataclass
class Str(ElementInterface):
    """String. Use this if you want add a string that is not interpreted as Markdown."""

@dataclass
class Repr(ElementInterface):
    """Adds a repr() of the object"""

@dataclass
class DF(ElementInterface):
    """Pandas.DataFrame

    :param str save_format: supports to either save the dataframe as latex-table
        or csv-file. Valid values are "tex" and "csv"
    """
    save_format: str = "tex"

    def _save_to_dir(self, target_dir):
        out_file = self.get_outfile(target_dir, self.save_format)
        if self.save_format == "tex":
            out_file.write_text(self.content.to_latex(index=False))
        elif self.save_format == "csv":
            self.content.to_csv(str(out_file))
            

@dataclass
class Nifti(ElementInterface):
    """nibabel.Nifti1Image"""

    def _save_to_dir(self, target_dir):
        out_file = self.get_outfile(target_dir, "nii")
        self.content.to_filename(str(out_file))
    
    def __post_init__(self):
        if self.dont_save:
            raise RuntimeError(
                "Niftis cannot be used without saving, "
                + "i.e. standalone cannot be used together with niftis")


@dataclass
class Figure(ElementInterface):
    """matplotlib.pyplot.figure
    
    All arguments except scale are passed to matplotlib.figure.Figure.save_fig.
    
    :param float scale: can be used by the renderer as a relative size
    """
    dpi: int = 300
    bbox_inches: str = "tight"
    transparent: bool = False
    extension: str = "png"
    scale: float = 0.7

    def _save_to_dir(self, target_dir):
        out_file = self.get_outfile(target_dir, self.extension)
        self.content.savefig(str(out_file), dpi=self.dpi, 
                             bbox_inches=self.bbox_inches,
                             transparent=self.transparent)

    def __post_init__(self):
        if not self.dont_save:
            return
        buffer = BytesIO()
        self.content.savefig(buffer, dpi=self.dpi, 
                             bbox_inches=self.bbox_inches,
                             transparent=self.transparent,
                             format=self.extension)
        buffer.seek(0)
        self.content = base64.b64encode(buffer.read()).decode()

@dataclass
class HLayout(Layout):
    """Allows to use multiple elements in a Row. Takes a tuple as argument"""


@dataclass
class VLayout(Layout):
    '''Allows to add multiple elements in a column.
    Useful within a HLayout'''
