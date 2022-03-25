"""generally useful functions for the rest of the mypeye visualization tools"""
import io
import pickle

import matplotlib.pyplot as plt

def get_cmap(n, name='hsv'):
    """
    Returns a function that maps each index in 0, 1, ..., n-1 to a
    distinct RGB color; the keyword argument name must be a standard
    mpl colormap name.
    """
    return plt.cm.get_cmap(name, n)

def recolumn(df_columns):
    """"
    applys _0+=1 to each redundant column label in 
    a DataFrame.columns object: df_columns

    use as a list generator

    adopted from Veedrac on stackoverflow
    """
    seen = set()
    for item in df_columns:
        increment = 1
        newitem = item
        while newitem in seen:
            increment += 1
            newitem = "{}_{}".format(item, increment)
        yield newitem
        seen.add(newitem)

def pickle_paste(fig):
    """
    copies the passed figure object heirarchy as raw data
    the raw data is loaded so to preserve it's heirarchy
    this is used to redisplay the figure
    should work for any kind of figure
    """
    if not fig:
        fig = plt.gcf()
    buf = io.BytesIO()
    pickle.dump(fig, buf)
    buf.seek(0)
    figcp = pickle.load(buf)
    return figcp

def redraw(ax):
    """displays the axis passed on the current figure"""
    fig = plt.gcf()
    ax.figure.canvas.draw_idle() #force re-draw

class Easel():
    """
    Figure and axis configuration convenience functions

    likely to move to the spyglass library
    """
    @staticmethod
    def match_labels(p_cols, e_cols):
        matched = []
        for e_col in e_cols:
            for p_col in p_cols:
                if p_col[2::] == e_col:
                    matched.append(e_col)
                    matched.append(p_col)
        return matched

    @staticmethod
    def pvse(df):
        allcol = df.columns.to_list()
        p_cols = [col for col in allcol if "p_" in col]
        e_cols = [col for col in allcol if "p_" not in col]
        match = match_labels(p_cols, e_cols)
        pvse_df = df[match]
        return pvse_df

    @staticmethod    
    def makegrid(df):
        plotl = df.columns.to_list()
        nplot = len(plotl)
        #aim for 3 for now
        if nplot / 3 <= 1:
            ncol = nplot
            nrow = 1
        else:
            ncol = (nplot - (nplot % 3))/3
            nrow = ncol+1
        return [int(ncol), int(nrow)]
