import pandas as pd
import numpy as np
import re

from ._utils import _build_frame, _grouper
from ._fig_library import _make_parity_fig, _make_biplot

def parityplot(estimator, *args, **kwargs):
    """
    Qualitatively evaluate a regression model using array of parity plots

    args:
    1. the estimator to explore
    2. *args holds arbitrarily many triplets of:
       - X :: a domain
       - Y :: a co-domain
       - name :: a partition name
    to form and check predictions at different partitions.

    incomplete triplets are ignored

    **kwargs are passed to underlying plot library API:
    - plotly if available
    - seaborn otherwise

    The data is also returned for further plotting or tabulation.
    """
    index_items=[v for k,v in kwargs.items() if isinstance(v, (pd.DataFrame, pd.Series))]
    ldata = []
    for triplet in _grouper(args, 3):
        if hasattr(estimator, "predict"):
            y_pred = estimator.predict(triplet[0])
        #elif hasattr(estimator, "decision_function"):
        #    y_pred = estimator.decision_function(X)
        #elif hasattr(estimator, "predict_proba"):
        #    y_pred = estimator.predict_proba(X)
        else:
            raise AttributeError("'estimator' does not have predict method")
        ldata.append(
            _build_frame(y_pred, triplet[1])
            .reset_index(level='comparison')
            .assign(partition=triplet[2])
        )
    data = pd.concat(ldata, axis=0)

    if index_items:
        data = data.reindex(index=index_items[0].index)

    p = _make_parity_fig(data,
                         x='true', y='pred',
                         facet_col="comparison", **kwargs)
    return p, data

def biplot(data, pcaxis, **kwargs):
    """
    Takes data for PCA transformation and a fitted PCA estimator.

    'x' and 'y' kwargs can be used to specify the PCA cross-section to
    draw, name the principal components by their numerical index.
    Defaults to 0 and 1.

    Handles transforming the data and plotting the resulting
    projection with indicated loadings.

    the pcadata is also returned for further plotting if desired.
    """
    pcs = pcaxis.get_feature_names_out()
    x = kwargs.get('x', 0)
    y = kwargs.get('y', 1)
    if isinstance(x, str) or isinstance(y, str):
        x = int(re.search(r'[0-9]+', str(x))[0])
        y = int(re.search(r'[0-9]+', str(y))[0])
        kwargs['x'] = x
        kwargs['y'] = y
    pcadata = pcaxis.transform(data)
    try:
        features = pcaxis.feature_names_in_
    except AttributeError:
        features = np.array([f'x{i}' for i in range(pcaxis.n_features_in_)])
    loadings = pcaxis.components_.T * np.sqrt(pcaxis.explained_variance_)
    #postmultiply with data to get pcadata
    loadings = loadings[:, (x,y)]
    labels = pcs[(x,y),]
    p = _make_biplot(data=pcadata,
                     features=features,
                     loadings=loadings,
                     labels=labels,
                     **kwargs)
    return p, pcadata
