import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import mplcursors
import seaborn as sns

def _make_parity_fig(data:pd.DataFrame, x:str, y:str, **kwargs):
    """
    plot an array of figures with an line of slope=1 overlaid onto
    each one
    """
    p = sns.relplot(data=data, x=x, y=y, **kwargs)
    for ax in p.figure.axes:
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        ax.axline((min(xlims+ylims), min(xlims+ylims)),
                  (max(xlims+ylims), max(xlims+ylims)), color='k')
    #issue: internally plotting is done as a groupby.  then, this
    #references the absolute index of the plot marker and goes and
    #looks for the number in the full data set (values towards the end
    #are never found). simply grouping the data now can't work because
    #the indices could then mismatch. selection must be obtained with
    #consciousness of the group somehow...
    mplcursors.cursor(multiple = True).connect(
        "add", lambda sel: sel.annotation.set_text(
            #sel.index
            data["Formula"].iloc[sel.index]
        )
    )
    return p

def _make_biplot(*, data:pd.DataFrame,
                 loadings:np.ndarray,
                 features:np.ndarray,
                 **kwargs):
    """
    Project PCA data onto plane. annotate the major components
    contributing to the plane axes
    """
    p = sns.scatterplot(data=data, **kwargs)
    for i, features in enumerate(features):
        p.figure.axes[0].arrow(
            0, 0,
            loadings[i,0],
            loadings[i,1],
            color = 'r', alpha = 0.5
        )
        p.figure.axes[0].text(
            loadings[i,0],
            loadings[i,1],
            data.columns[i],
            color = 'g', ha = 'center', va = 'center'
        )

    mplcursors.cursor(multiple = True).connect(
        "add", lambda sel: sel.annotation.set_text(
            #sel.index
            pcadata.index.get_level_values(level=0)[sel.index]
        )
    )

    return p
