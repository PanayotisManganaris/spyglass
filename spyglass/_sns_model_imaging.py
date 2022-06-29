import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import mplcursors
import seaborn as sns

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

    **kwargs are passed to the seaborn FacetGrid

    Rapidly evaluate a regression model in an array of parity plots
    The main offer is interactivity in the plot.

    The data is also returned for optionally more in-depth plotting.
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

    p = sns.relplot(data=data, x="true", y="pred", **kwargs)
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

    return p, data
