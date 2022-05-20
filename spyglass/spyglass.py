#cmcl's "high-level plotting api"
#immature, future versions of this concept will be implemented in a standalone library
#for more versatility and improved pandas integration

import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mplcursors

def biplot(*args, pcaxis, data, **kwargs):
    """
    simple wrapper that both performs pca and plots the resulting projections
    """
    #data = kwargs.get("data", None)
    transform_matrix = pd.DataFrame(
        pcaxis.components_.T * np.sqrt(pcaxis.explained_variance_),
        index=data.columns,
        columns=data.columns
    )
    pcadata = pd.DataFrame(
        pcaxis.transform(data),
        index=data.index,
        columns=['pc_%i' % i for i in range(pcaxis.n_components)]
    )
    #pcadata = pcadata.reset_index()
    p = sns.scatterplot(data = pcadata, **kwargs)
    for i in range(pcaxis.n_components):
        p.figure.axes[0].arrow(0, 0,
                               transform_matrix.iloc[i, 0],
                               transform_matrix.iloc[i, 1],
                               color = 'r', alpha = 0.5)
        p.figure.axes[0].text(transform_matrix.iloc[i, 0],
                              transform_matrix.iloc[i, 1],
                              data.columns[i],
                              color = 'g', ha = 'center', va = 'center')

    mplcursors.cursor(multiple = True).connect(
        "add", lambda sel: sel.annotation.set_text(
            #sel.index
            pcadata.index.get_level_values("Formula")[sel.index]
        )
    )

    return p
