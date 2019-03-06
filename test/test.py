from datasheet import Sheet, Repr, Str, MD
import pandas as pd
import matplotlib.pyplot as plt
import nibabel as nib

def compute_table(x):
    return pd.DataFrame({
        "x": list(range(x)),
        "x-sq": [x**2 for x in range(x)]
    })

def test_1():
    sheet = Sheet("./test_out")
    sheet << """
    # Test Title
    Some Text
        
    * With Bulletpoints
    * One more

    `And Some *RAW* MD Code`

    ## Next we have a Raw-String representation
    """
    raw_str = "Hello\nWorld"
    sheet << Repr(raw_str)
    sheet << "## And the same string printed"
    sheet << Str(raw_str)
    sheet << """
        ## A Pandas table
        With a little demonstration of caching.
        (And this will be indented identically to the last MD Code
        Because there is auto indent detection)"""
    table = sheet.cache(compute_table)(20)
    sheet << table.head()
    sheet << "### The Latex code:"
    sheet << Str(table.to_latex(index=False))
    sheet << "## A Matplotlib figure"
    plt.plot(table.x, table["x-sq"])
    sheet << plt.gcf()
    sheet << "## We even have a nifti viewer"
    sheet << nib.load("test/foo.nii")
    sheet.render()


def test_2():
    sheet = Sheet("./test_out")
    cached_func = sheet.cache(compute_table)
    cached_func.clear()


if __name__ == "__main__":
    test_1()