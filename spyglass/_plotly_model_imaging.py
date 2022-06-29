import pandas as pd
import numpy as np

import plotly.express as px

def _build_frame(y_pred:np.ndarray, y_true:pd.DataFrame):
    prednames = [name+"_pred" for name in y_true.columns]
    pred_label = ["pred"]*len(prednames)
    true_label = ["true"]*len(prednames)
    mc_ypred = pd.MultiIndex.from_arrays([prednames, pred_label],
                                         names=["comparison", "xy"])
    mc_ytrue = pd.MultiIndex.from_arrays([prednames, true_label],
                                         names=["comparison", "xy"])

    y_pred = pd.DataFrame(y_pred, columns=mc_ypred, index=y_true.index)
    y_true = pd.DataFrame(y_true.values, columns=mc_ytrue, index=y_true.index)
    
    data = pd.concat([y_true, y_pred], axis=1).stack("comparison")

    return data

def parityplot(estimator,
               X:pd.DataFrame,
               y_true:pd.DataFrame, **kwargs):
    """
    pass the estimator, a basis and targets to compare against.

    **kwargs are passed to plotly express scatter

    Rapidly evaluate a regression model in an array of parity plots
    The main offer is interactivity in the plot.

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

    p = px.scatter(data, x="true", y="pred", **kwargs)
    xlims = min(data.true), max(data.true)
    ylims = min(data.pred), max(data.pred)
    p.add_scatter(x = (min(xlims+ylims), max(xlims+ylims)),
                  y = (min(xlims+ylims), max(xlims+ylims)),
                  mode='lines'
                  row='all', col='all', exclude_empty_subplots=True)
    return p, data
