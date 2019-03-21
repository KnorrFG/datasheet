from dataclasses import dataclass
from importlib.resources import read_text
from pathlib import Path
from typing import List
import re

from markdown import markdown
from pandas import DataFrame
from yattag import Doc, indent

from .types import DF, MD, Figure, Nifti, Repr, Str, MultiCell


def _print_to_html(s):
    doc, tag, text = Doc().tagtext()
    with tag("pre"):
        text(s)
    return doc.getvalue()


def _figure_to_html(fig: Figure):
    doc = Doc()
    doc.stag("img", src=fig.rel_save_path, width=f"{fig.scale * 100}%")
    return doc.getvalue()


@dataclass
class _PapayaHelper:
    niftis: List[Nifti]
    called: int = 0

    def get_papaya_header(self):
        return read_text('datasheet.data', "papaya_header.html") \
            + '<script type="text/javascript">' + ";".join(
            [f'var param{i} = {{"images": ["{nii.rel_save_path}"]}}'
            for i, nii in enumerate(self.niftis)]
            ) + '</script>' + '<script type="text/javascript">' + \
            read_text("datasheet.data", "papaya.js") + '</script>'

    def __call__(self, nii: Nifti):
        res = f'<div class="papaya" data-params="param{self.called}"></div>'
        self.called += 1
        return res
    

def _render_multicell(cell, transformers):
    doc, tag, text = Doc().tagtext()
    with tag("div", style="display: flex; flex-direction: row; margin: 10px 0;"):
        for entry in cell.content:
            with tag('div', klass='entry'):
                doc.asis(transformers[type(entry)](entry))
            doc.asis("&emsp;")
        
    return doc.getvalue()


def _is_single_line_md_heading(entry):
    return type(entry) == MD and "\n" not in entry.content \
        and entry.content.strip().startswith("#")


def _make_toc(entries, max_index_len):
    doc, tag, text = Doc().tagtext()
    for i, entry in enumerate(filter(_is_single_line_md_heading, entries)):
        line = entry.content.strip()
        level = re.search(r"[^#]", line).start()
        with tag("div", klass=f"indexindent_{level}"):
            link_text = line[level:] if len(line) < max_index_len \
                or max_index_len == 0 else (line[level: max_index_len - 3] + "...")
            doc.line("a", link_text, href=f"#{i}")
    return indent(doc.getvalue())


@dataclass
class _MDHeaderMaker:
    counter = 0

    def get_header(self, entry):
        doc = Doc()
        line = entry.content.strip()
        level = re.search(r"[^#]", line).start()
        text = line[level:]
        doc.line(f'h{level}', text, id=str(self.counter))
        self.counter += 1
        return doc.getvalue()

def render_html(entries, outdir: Path, style_sheet: str = "default.css", 
                max_index_len: int = 25):
    """ Renders a `Sheet` as HTML-page.

    :param Path outdir: The outputfolder to store the page in, usually 
        :code:`Sheet.outdir`.
    :param str style_sheet: the css file to include in the page. It is
        looked for in datasheet.data, currently this is the only valid value
        for this parameter
    :param int max_index_len: maximal number of characters a title can
        have before its index is abreviated."""
    header_parser = _MDHeaderMaker()
    _transformers = {
        DF: lambda s: s.content._repr_html_(),
        Figure: _figure_to_html,
        MD: lambda s: header_parser.get_header(s) if _is_single_line_md_heading(s)
            else markdown(s.content),
        Nifti: None,
        Repr: lambda s: _print_to_html(repr(s.content)),
        Str: lambda s: _print_to_html(s.content)
    }
    _transformers[MultiCell] = lambda s: _render_multicell(s, _transformers)

    if any(type(entry) == Nifti for entry in entries):
        papayaHelper = _PapayaHelper(
            [entry for entry in entries if type(entry) == Nifti])
        _transformers[Nifti] = papayaHelper
        has_papaya = True
    else:
        has_papaya = False

    doc, tag, text, line = Doc().ttl()
    with tag('html'):
        with tag('head'):
            line("title", outdir.name)
            doc.stag("meta", charset="UTF-8")
            with tag("script", type="text/javascript"):
                doc.asis(read_text("datasheet.data", "positions.js"))
            with tag('style'):
                doc.asis(read_text('datasheet.data', style_sheet))
                if has_papaya:
                    doc.asis(read_text("datasheet.data", "papaya_css_additions.txt"))
            if has_papaya:
                doc.asis(papayaHelper.get_papaya_header())
            
        with tag('body', onload="fixPosition();"):
            with tag('div', id="toc"):
                line("div", "Contents", id="toc_header")
                doc.asis(_make_toc(entries, max_index_len))
            with tag('div', id='container'):
                for entry in entries:
                    with tag('div', klass='entry'):
                        doc.asis(_transformers[type(entry)](entry))
    Path(outdir, "index.html").write_text(indent(doc.getvalue()))
