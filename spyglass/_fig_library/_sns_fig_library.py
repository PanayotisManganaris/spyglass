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

def _make_projection_fig(data, *, pcaxis, **kwargs):
    """
    Project PCA data onto plane. annotate the major components
    contributing to the plane axes
    """
    p = sns.scatterplot(data = data, **kwargs)
    xlim = min(map(abs,p.figure.axes[0].get_xlim()))
    ylim = min(map(abs,p.figure.axes[0].get_ylim()))
    xscaler = xlim if xlim > 1 else 1.0
    yscaler = ylim if ylim > 1 else 1.0
    for i in range(pcaxis.n_components):
        p.figure.axes[0].arrow(0, 0,
                               transform_matrix.iloc[i, 0] * xscaler,
                               transform_matrix.iloc[i, 1] * yscaler,
                               color = 'r', alpha = 0.5)
        p.figure.axes[0].text(transform_matrix.iloc[i, 0] * xscaler,
                              transform_matrix.iloc[i, 1] * yscaler,
                              data.columns[i],
                              color = 'g', ha = 'center', va = 'center')

    mplcursors.cursor(multiple = True).connect(
        "add", lambda sel: sel.annotation.set_text(
            #sel.index
            pcadata.index.get_level_values(level=0)[sel.index]
        )
    )

    return p
