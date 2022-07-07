import pandas as pd

from ._utils import _build_frame
from ._fig_library import _make_parity_fig, _make_projection_fig

def parityplot(estimator,
               X:pd.DataFrame,
               y_true:pd.DataFrame, **kwargs):
    """
    pass the estimator, a basis and targets to compare against.

    **kwargs are passed to underlying plot library api:
    - plotly if available
    - seaborn otherwise

    Qualitatively evaluate a regression model using array of parity
    plots. Where possible, the plot will support interactive
    annotation.

    The data is also returned for further plotting or tabulation.
    """
    if hasattr(estimator, "predict"):
        y_pred = estimator.predict(X)
    #elif hasattr(estimator, "decision_function"):
    #    y_pred = estimator.decision_function(X)
    #elif hasattr(estimator, "predict_proba"):
    #    y_pred = estimator.predict_proba(X)
    else:
        raise AttributeError("'estimator' does not have predict method")
    data = _build_frame(y_pred, y_true)
    try:
        data = data.reset_index().drop("index", axis=1)
    except KeyError:
        data = data.reset_index().drop("level_0", axis=1)

    p = _make_parity_fig(data,
                         x='true', y='pred',
                         facet_col="comparison")
    return p, data

def biplot(data, *, pcaxis, **kwargs):
    """
    simple wrapper that both performs pca and plots the resulting projections
    """
    transform_matrix = pd.DataFrame(
        pcaxis.components_.T * np.sqrt(pcaxis.explained_variance_),
        index=data.columns,
        columns=data.columns
    )
    pcadata = pd.DataFrame(
        pcaxis.transform(data),
        index=data.index,
        columns=[f'pc_{i}' for i in range(pcaxis.n_components)]
    )
    p = _make_projection_fig(data=pcadata,
                             pcaxis=pcaxis,
                             **kwargs)

    return p
