from datasheet import Sheet, Repr, Str, HLayout
import pandas as pd
import matplotlib.pyplot as plt

def main():
    sheet = Sheet("./test_out")
    sheet << "# Test Title"
    sheet << """
    The reason that the title wasn't added as part of this
    multi line string is that if you add a sinle line string which
    contains a title, it will get an index entry.

    * With Bulletpoints
    * One more

    `And Some *RAW* MD Code`
    """
    sheet << "## Next we have a Raw-String representation"
    raw_str = "Hello\nWorld"
    sheet << Repr(raw_str)
    sheet << "## And the same string printed"
    sheet << Str(raw_str)
    sheet << "## A Pandas table"
    sheet << """
        With a little demonstration of caching.
        (And this will be indented identically to the last MD Code
        Because there is auto indent detection)"""
    table = sheet.cache(compute_table)(20)
    sheet << HLayout((table.head(), """
        And Some *nice* MD comments Next to it.
        There is also a second type of cache, which you can access
        vial the gated_cache() method. But it's not used here.
        It is handy if you want to prevent recomputation under certain
        circumstances"""))
    sheet << "### The Latex code:"
    sheet << Str(table.to_latex(index=False))
    sheet << "## A Matplotlib figure"
    plt.plot(table.x, table["x-sq"])
    sheet.add_current_figure()
    sheet.render()

def compute_table(x):
    return pd.DataFrame({
        "x": list(range(x)),
        "x-sq": [x**2 for x in range(x)]
    })


if __name__ == "__main__":
    main()
