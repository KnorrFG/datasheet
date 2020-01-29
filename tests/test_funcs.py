from datasheet import html_renderer as hr
from datasheet import types as t

def test_grouping():
    h1, ts, h2, h12, t2 = t.MD("# H1"), t.MD('Test String'), t.MD('##H2'),\
        t.MD('# H12'), t.MD('foo')
    entries = [h1, ts, h2, h12, t2]
    folded_entries = hr._group_heading_contents(entries, [])
    assert folded_entries == [h1, [ts, h2, []], h12, [t2]]
