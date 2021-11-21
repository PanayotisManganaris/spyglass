"""generally useful functions for the rest of the mypeye visualization tools"""
import io
import pickle

import matplotlib.pyplot as plt

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
