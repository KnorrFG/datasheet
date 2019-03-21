.. data-sheet documentation master file, created by
   sphinx-quickstart on Thu Mar 21 10:26:31 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to datasheet's documentation!
======================================

Datasheet is a small library that aims to make it as easy as possible
to generate nice, usable output files containing all sorts of information
that might fall out of a scientific python script.
The output is stored as html page. To a sheet you can easily add

* Strings containing Markdown "code"
* Pandas DataFrames
* Nibabel nifti images
* Matplotlib figures

with a single line. Think jupyter without source-code. To give a similar
developing speed as you have in jupyter datasheet has two cache-functions, which will
cache the results of a function call. The first one,
`datasheet.sheet.Sheet.cache` is a wrapper around `joblib.Memory
<https://joblib.readthedocs.io/en/latest/auto_examples/memory_basic_usage.html>`_
The second one, `datasheet.sheet.Sheet.gate_cache` is pretty stupid, which can
be handy too. The joblib cache is aware of the functions source-code and the
arguments, and will rerun the function if one of these things changes. But it
might very well be the case, that you want to change a thing in your source
without instantly rerunning everything for very time consuming computations.
The gated cache will ignore everything as long as there is already a stored
result, and only recompute if it is explicitly told to do so.

After you added everything you want in your output file you simply call
:code:`sheet.render()` and an html file will be generated.

Here is an example:

.. code-block:: python

    from datasheet import Sheet, Repr, Str, MD
    import pandas as pd
    import matplotlib.pyplot as plt
    import nibabel as nib
    import numpy as np


    def main():
        sheet = Sheet("./test_out")
        sheet << "# Test Title"
        sheet << """
        The Reason that the title wasn't added as part of this
        multiline string is that if you add a sinle line string which 
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
        sheet << "With a little demonstration of caching."
        table = sheet.cache(compute_table)(20)
        sheet << (table.head(), 
            """ 
            And Some *nice* MD comments Next to it.
            
            This can be achieved by adding a tuple.
            
            Btw. There also is another caching-method,  
            the gated cache, which can be usefull if you want to   
            prevent some recomputations that will happen with the  
            normal cache""")
        sheet << "### The Latex code:"
        sheet << Str(table.to_latex(index=False))
        sheet << "## A Matplotlib figure"
        plt.plot(table.x, table["x-sq"])
        sheet.add_current_figure()
        sheet << "## We even have a nifti viewer"
        sheet << make_nifti()
        sheet.render()


    def compute_table(x):
        return pd.DataFrame({
            "x": list(range(x)),
            "x-sq": [x**2 for x in range(x)]
        })
        

    def gaussian(x, mu, sig):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


    def make_nifti():
        shape = np.array((50, 50, 50))
        dists = np.ones(shape)
        center = np.array((25, 25, 25))
        for index in np.ndindex(*shape):
            dists[index] = np.sqrt(np.sum((index - center) ** 2))
        return nib.Nifti1Image(gaussian(dists, 0, 10), np.eye(4))


    if __name__ == "__main__":
        main()




You can find the details in the `api`

