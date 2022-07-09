import pandas as pd
import numpy as np

import plotly.express as px

def _make_parity_fig(data:pd.DataFrame, x:str, y:str, **kwargs):
    """
    plot an array of figures with an line of slope=1 overlaid onto
    each one
    """
    p = px.scatter(data, x=x, y=y, **kwargs)
    xlims = min(data[x]), max(data[y])
    ylims = min(data[y]), max(data[y])
    p.add_scatter(x = [min(xlims+ylims), max(xlims+ylims)],
                  y = [min(xlims+ylims), max(xlims+ylims)],
                  mode='lines', name="parity", marker={"color":"black"},
                  row='all', col='all')
    return p

def _make_biplot(*, data:pd.DataFrame,
                 loadings:np.ndarray,
                 features:np.ndarray,
                 **kwargs):
    """
    Project PCA data onto plane. annotate the major components
    contributing to the plane axes
    """
    p = px.scatter(data=data, **kwargs)
    for i, feature in enumerate(features):
        p.add_shape(
            type='line',
            x0=0, y0=0,
            x1=loadings[i, 0],
            y1=loadings[i, 1],
        )
        p.add_annotation(
            x=loadings[i, 0],
            y=loadings[i, 1],
            ax=0, ay=0,
            xanchor="center",
            yanchor="bottom",
            text=feature,
        )
    return p
