import pandas as pd

import matplotlib.pyplot as plt
import mplcursors
import seaborn as sns

def parityplot(estimator,
               X:pd.DataFrame,
               y_true:pd.DataFrame, **kwargs):
               #score_function, ):
    #Rapidly evaluate a regression model
    if hasattr(estimator, "predict"):
        y_pred = estimator.predict(X)
    #elif hasattr(estimator, "decision_function"):
    #    y_pred = estimator.decision_function(X)
    #elif hasattr(estimator, "predict_proba"):
    #    y_pred = estimator.predict_proba(X)
    else:
        raise AttributeError("'estimator' does not have predict method")
    prednames = [name+"_pred" for name in y_true.columns]
    y_pred = pd.DataFrame(y_pred, columns=prednames, index=y_true.index)
    data = pd.concat([y_true, y_pred], axis=1)
    
    #preferably get key names in a more direct way
    spliter = data.columns.str.contains('_pred')
    truenames = data.loc[:, ~spliter].columns
    prednames = data.loc[:, spliter].columns

    p1 = sns.relplot(kind='scatter',
                     data=data,
                     x=truenames[0],
                     y=prednames[0],
                     **kwargs)
    p1.map_dataframe(sns.lineplot,
                     x=truenames[0],
                     y=truenames[0],
                     color='k')

    

    mplcursors.cursor(multiple = True).connect(
        "add", lambda sel: sel.annotation.set_text(
            data.index.get_level_values("Formula")[sel.index])
    )

    return p1

    # f, ax = plt.subplots(1)
    # ax = sns.scatterplot(data=data,
    #                      x=truenames[0],
    #                      y=prednames[0],
    #                      ax=ax,
    #                      **kwargs)
    # #need version-robust axline tool
    # ax = sns.lineplot(data=data,
    #                   x=truenames[0],
    #                   y=truenames[0],
    #                   color='k',
    #                   ax=ax)

