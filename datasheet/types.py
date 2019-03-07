from dataclasses import dataclass, InitVar
from typing import Any, ClassVar
from pathlib import Path

def _map_lines(func, s):
    return "\n".join(map(func, s.split("\n")))


@dataclass
class ElementInterface:
    content: Any
    rel_save_path: Path = None
    save_counter: ClassVar[int] = 0

    def get_outfile(self, target_dir: Path, ext: str):
        if self.rel_save_path is None:
            ElementInterface.save_counter += 1
            self.rel_save_path = f"{ElementInterface.save_counter}.{ext}"
        return target_dir / self.rel_save_path


@dataclass
class MD(ElementInterface):
    """Markdown"""
    offset: InitVar[int] = -1

    def __post_init__(self, offset):
        if offset < 0:
            offset = min(len(line) - len(line.lstrip())
                         for line in self.content.split("\n") if len(line.strip()) > 0)
        if offset > 0:
            self.content = _map_lines(lambda s: s[offset:], self.content)

@dataclass
class Str(ElementInterface):
    """String"""

@dataclass
class Repr(ElementInterface):
    """Adds a repr() of the object"""

@dataclass
class DF(ElementInterface):
    save_format: str = "tex"

    def save_to_dir(self, target_dir):
        out_file = self.get_outfile(target_dir, self.save_format)
        if self.save_format == "tex":
            out_file.write_text(self.content.to_latex(index=False))
        elif self.save_format == "csv":
            self.content.to_csv(str(out_file))
            

@dataclass
class Nifti(ElementInterface):
    """nibabel.Nifti1Image"""

    def save_to_dir(self, target_dir):
        out_file = self.get_outfile(target_dir, "nii")
        self.content.to_filename(str(out_file))


@dataclass
class Figure(ElementInterface):
    """matplotlib.pyplot.figure"""
    dpi: int = 300
    bbox_inches: str = "tight"
    transparent: bool = True
    extension: str = "png"
    scale: float = 0.7

    def save_to_dir(self, target_dir):
        out_file = self.get_outfile(target_dir, self.extension)
        self.content.savefig(str(out_file), dpi=self.dpi, 
                             bbox_inches=self.bbox_inches,
                             transparent=self.transparent)


@dataclass
class MultiCell(ElementInterface):
    """Allows to use multiple elements in a Row. Takes a tuple as argument"""
    def __post_init__(self):
        if type(self.content) != tuple:
            raise ValueError("Content must be tuple")