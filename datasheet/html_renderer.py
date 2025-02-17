from dataclasses import dataclass
from pathlib import Path
from typing import List
import re
from importlib.resources import files

from markdown import markdown
from pandas import DataFrame
from yattag import Doc, indent

from .types import *


markdown_extensions = [
    'markdown.extensions.extra',
    'markdown.extensions.abbr',
    'markdown.extensions.attr_list',
    'markdown.extensions.def_list',
    'markdown.extensions.fenced_code',
    'markdown.extensions.footnotes',
    'markdown.extensions.tables',
    'markdown.extensions.admonition',
    'markdown.extensions.codehilite',
    'markdown.extensions.meta',
    'markdown.extensions.sane_lists',
    'markdown.extensions.smarty',
    'markdown.extensions.toc',
    'markdown.extensions.wikilinks'
]

def _print_to_html(s):
    doc, tag, text = Doc().tagtext()
    with tag("pre"):
        text(s)
    return doc.getvalue()


def _figure_to_html(fig: Figure):
    doc = Doc()
    if fig.rel_save_path:
        doc.stag("img", src=fig.rel_save_path, width=f"{fig.scale * 100}%")
    else:
        doc.stag('img', src=f'data:image/{fig.extension};base64,{fig.content}')
    return doc.getvalue()


def _render_multicell(cell, transformers):
    doc, tag, text = Doc().tagtext()
    with tag("div",
             style="display: flex; flex-direction: row; margin: 10px 0;"):
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
                or max_index_len == 0 else\
                (line[level: max_index_len - 3] + "...")
            doc.line("a", link_text, href=f"#{i}")
    return indent(doc.getvalue())


def _layout_to_html(transformers, layout):
    doc, tag, text = Doc().tagtext()

    def inner(elems):
        if len(elems) == 0:
            return indent(doc.getvalue())
        entry = elems[0]
        if _is_single_line_md_heading(entry):
            doc.asis(transformers[type(entry)](entry))
            with tag('div', klass='collapsable'):
                doc.asis(_layout_to_html(transformers, VLayout(elems[1])))
            return inner(elems[2:])
        elif isinstance(entry, Layout):
            with tag('div', klass=type(entry).__name__):
                doc.asis(_layout_to_html(transformers, entry))
        else:
            with tag('div', klass='entry'):
                doc.asis(transformers[type(entry)](entry))
        return inner(elems[1:])

    return inner(layout.elems)


def _get_h_indention_lvl(s: str) -> int:
    return re.search(r"[^#]", s).start()


@dataclass
class _MDHeaderMaker:
    counter = 0

    def get_header(self, entry):
        doc = Doc()
        line = entry.content.strip()
        level = _get_h_indention_lvl(line)
        text = line[level:]
        doc.line(f'h{level}', "\u2798" + text,
                 id=str(self.counter), klass='hdr')
        self.counter += 1
        return doc.getvalue()


def _group_heading_contents(entries, handled_entries):
    if len(entries) == 0:
        return handled_entries
    elif not _is_single_line_md_heading(entries[0]):
        return _group_heading_contents(entries[1:],
                                  handled_entries + [entries[0]])
    else:
        try:
            current_lvl = _get_h_indention_lvl(entries[0].content.strip())
            next_header_idx = next(i for i, e in enumerate(entries[1:])
                                    if _is_single_line_md_heading(e)
                                    and _get_h_indention_lvl(e.content.strip())
                                        == current_lvl) + 1
            content = entries[1:next_header_idx]
            tail = entries[next_header_idx:]
        except StopIteration:
            content = entries[1:]
            tail = []

        return _group_heading_contents(tail, handled_entries + [entries[0]] +
                                  [_group_heading_contents(content, [])])


class HTMLRenderer:
    """The Default renderer, that renders to HTML"""
    default_file = 'index.html'
    extension = 'html'

    @staticmethod
    def render(entries: Layout, out_file: Path, 
               style_sheet: str = "default.css", max_index_len: int = 25):
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
            MD: lambda s: header_parser.get_header(s)
                if _is_single_line_md_heading(s)
                else markdown(s.content, extensions=markdown_extensions),
            Repr: lambda s: _print_to_html(repr(s.content)),
            Str: lambda s: _print_to_html(s.content)
        }

        doc, tag, text, line = Doc().ttl()
        with tag('html'):
            with tag('head'):
                line("title", out_file.stem)
                doc.stag("meta", charset="UTF-8")
                with tag('style'):
                    doc.asis(read_text('datasheet.data', style_sheet))

            with tag('body'):
                with tag('div', id="toc"):
                    line("div", "Contents", id="toc_header")
                    doc.asis(_make_toc(entries, max_index_len))
                with tag('div', id='container'):
                    doc.asis(_layout_to_html(
                        _transformers,
                        VLayout(_group_heading_contents(entries.elems, []))))
                with tag('script'):
                    doc.asis(read_text('datasheet.data', 'collapse.js'))
        Path(out_file).write_text(indent(doc.getvalue()))

def read_text(mod, file):
    return (files(mod) / file).read_text('utf-8')
    
