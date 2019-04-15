# first line: 6
def compute_table(x):
    return pd.DataFrame({
        "x": list(range(x)),
        "x-sq": [x**2 for x in range(x)]
    })
