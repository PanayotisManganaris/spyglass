"""visualization tools for evaluating the performance of regression models"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class click_fig():
    def __init__():

    def annotate(axis, label, labelx, labely, x, y):
        """create and add text to figure axes"""
        text_annotation = Annotation(label, xy=(x, y), xytext=(labelx, labely),
                                     xycoords='data',
                                     textcoords="offset points",
                                     bbox=dict(boxstyle="round", fc="w"), #what style
                                     arrowprops=dict(arrowstyle="->")) #at what style
        axis.add_artist(text_annotation)
        #alternative for less imports?
        #axis.annotate(label, xy=(x,y), xytext=xy, #what, at what, where
        #             xycooords='data', #textcoords="offset points", #at what reference, where reference
        
    def onclickdot(event):
        """
        define the click on dot behavior
        Notice: Data labels must be ordered with data cordinates for meaningful assignment
        """
        ind = event.ind #get index of picked coords -- conveninent
        #save clicked coordinates to position text
        annotx = event.mouseevent.xdata
        annoty = event.mouseevent.ydata
        #save dot coordinates to point arrow
        dotx = xy[ind, 0]
        doty = xy[ind, 1]
        # initialize offset to use in adjusting annotation position
        offset = 0
        # if dots overlap, matplotlib returns returns a list of clicked indicies.
        # parse the list:
        for i in ind:
            #Assign a label to its corresponding data point
            label = labels[i]
            #log if needed
            # add the text annotation to the axes
            annotate(ax, label,
                     annotx + offset,
                     annoty + offset,
                     dotx,
                     doty
                     )
            ax.figure.canvas.draw_idle() #force re-draw
            offset += 0.01 # in case of list, alter offset 
        
    def onclickclear(event):
        """ define the "clear all" behavior """
        ax.cla() #clear artist objects from axes
        redraw(axcp)

    def annotscatplot(x, y, labels, ax=None):
        if not ax:
            ax = plt.gca()
        #add a clear all button to the low left corner
        ax_clear_all = plt.axes([0.0, 0.0, 0.1, 0.05])
        button_clear_all = Button(ax_clear_all, 'Clear all')
        #link event handler function to the button
        button_clear_all.on_clicked(onclickclear)
        
        #plot data
        ax.scatter(x, y, picker=True)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid()
        #link event handler function to the scatterplot
        fig.canvas.mpl_connect('pick_event', onclickdot)

        figcp = pickle_paste(fig)
        axcp = figcp.axes

        return [ax, button_clear_all]
