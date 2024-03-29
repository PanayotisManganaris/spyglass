"""
visualization tools for rapidly exploring common kinds of data visualization

Spyglass will never force a backend on the user.
Use matplotlib.use(qt) or, in notebooks, the better ipython line magic:
%matplotlib qt
or
%matplotlib widget
to set an interactive backend

use matplotlib.use(Agg) or %matplotlib inline to receive hard-copy figure files
"""
from spyglass.utils import recolumn
from spyglass.utils import get_cmap

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.projections import register_projection # proper axes patching method
from matplotlib.widgets import Button
from matplotlib.text import Annotation
from matplotlib.transforms import blended_transform_factory
from matplotlib.patches import Ellipse

import numpy as np
import pandas as pd

class EDAFigure(Figure):
    """
    matplotlib.figure.Figure subclass containing methods configuring
    the figure display for Exploratory Data Analysis.

    methods automate adding pre-configured axes using the
    figure.add_axes() syntax

    interactivity methods come from sibling classes defining
    custom projections
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    def add_button(self, button_text = None):
        #could call button class methods in future -- see notes on README
        if not button_text:
            button_text = "Clear\nAnnotations"
        ax_clear_all = self.add_axes([0.0, 0.0, 0.1, 0.05], facecolor='r')
        #add a clear all button to the low left corner
        self.button_clear_all = Button(ax_clear_all, button_text)
        #link event handler function to the button
        callback = self.axes[0].make_onclickclear()
        #notice this depends on the boilerplate axes being defined on
        #the figure before any additional -- this is bad.
        self.button_clear_all.on_clicked(callback)
    
 class Interaxes(Axes):
    """
    matplotlib.axes.Axes class containing methods defining user
    annotate on click actions on member artist objects. It also
    contains methods defining interaction with any accompanying
    interactive widgets -- though these widget methods might be split
    into their own class in the future to allow mixing and matching.

    Annotations appear when plot markers are clicked on an
    interactive backend display canvas.
    """
    name = 'interactive'
    # The projection must specify a name. This will be used by the
    # user to select the projection,
    # i.e. ``subplot(projection='custom_hammer')``
    def __init__(self, *args, **kwargs):                             
        super().__init__(*args, **kwargs) #takes all axes args, exposes          
                                          #artists + pyplot interface            
        #link event handler function to the display
        self.figure.canvas.mpl_connect('pick_event', self.onclickdot)

    def make_onclickclear(self):
        """
        function returning a callback closure that defines the "clear all"
        widget behavior relative to this axes
        """
        def onclickclear(event):
            self.cla() #clear artist objects from axes
            self.drawself() #draw the chosen boilerplate axes
        return onclickclear
            
    def makeannotate(self, label, labelx, labely):
        """ create and add text to axes """
        el = Ellipse((0, 0), 10, 20, facecolor="0.8", alpha=0.5)
        bboxspec = dict(boxstyle="round", fc="0.8", ec="none")
        arrowspec = dict(arrowstyle="wedge,tail_width=1.",
                         fc="0.8", ec="none",
                         patchA=None,
                         patchB=el,
                         relpos=(0.8,0.5))
        # trans = blended_transform_factory(x_transform=self.transAxes,
        #                                   y_transform=self.transData)
        text_annotation = Annotation(label, xy=(labelx, labely),  #what, at what
                                     xytext=(labelx, labely), #where
                                     xycoords=trans, #x-position adaptive
                                     textcoords="offset points",
                                     bbox=bboxspec, #what style
                                     arrowprops=arrowspec) #at what style
        self.add_artist(text_annotation)
        #alternative for less deps?
        #axis.annotate(label, xy=(x,y), xytext=xy,
        #             xycooords='data', #textcoords="offset points", #at what ref, where ref

    def onclickdot(self, event):
        """
        define the click on scatter plot marker behavior
        Notice: datalabels must be ordered with data coordinates for meaningful assignment
        """
        ind = event.ind #get index of picked marker coords -- convenient
        #save clicked coordinates to position text
        annotx = event.mouseevent.xdata
        annoty = event.mouseevent.ydata
        # initialize offset to use in adjusting annotation position
        offset = 0
        #if dots overlap, matplotlib returns returns a list of clicked indices.
        #parse the list:
        if isinstance(self.labels, pd.DataFrame):
            labels = self.labels.values.tolist()
        else:
            labels = self.labels
            
        for i in ind:
            #Assign a label to its corresponding data point
            label = labels[i]
            # add the text annotation to the axes
            self.makeannotate(label,
                              annotx + offset,
                              annoty + offset)
            self.figure.canvas.draw_idle() #force re-draw
            offset += 0.05 # in case of list, alter offset 

    def activescatter(self, x, y, datalabels, *args, **kwargs):
        """
        axes scatter plot with interactivity. 
        Should work with subplots and pyplot interactive script syntax as an axis projection
        """
        #place arguments in instance namespace
        self.x=x
        self.y=y
        self.labels=datalabels
        #plot data
        def draw_activescatter(): #draw functions may be called out of their defining function scope on_click_clear
            self.scatter(self.x, self.y, *args, picker=True, **kwargs)
            self.set_xlabel("X")
            self.set_ylabel("Y")
            self.grid()
        self.drawself = draw_activescatter
        self.drawself()

    def biplot(self, components, PCs, transform_matrix, dim_labels=None,
               dataspan=None, cbar_kw={}, cbarlabel="", **kwargs):
        """
        modify or create and return axis containing cross-section of pca space as
        scatter plot with projection of orignal dimensions onto the plane of major
        variance
    
        Parameters:
        ----------    
        components
        2-length list of integers from 0 to D-1. Selects 2 components to be scatter
        plotted against each other.
        PCs
        D+L-colummn DataFrame where each column from 0 to D is a principal component.
        If L is greater than zero, D+1 to L are used as marker labels.
        transform_matrix
        DxD array of component weights summarizing the contribution of each dimension to
        each PC. Meant for use with PCA by sklearn.Decomposition.PCA.components_
        dim_labels
        D-length list of dimension labels corresponding the axes of the original
        data-space transformed in the PCA.
        dataspan
        a range of indices written as a slice object representing the columns of the
        passed PCs DataFrame that are actual data. example: (PCs 0 to 11) is slice(0:12).
        The inverse of the slice identifies columns used as labels. If None biplot uses
        PCs.index as marker labels.

        Utility Args:
        -------------
        cbar_kw
        A dictionary with arguments to matplotlib.Figure.colorbar.  Optional.
        cbarlabel
        The label for the colorbar.  Optional.
        ,**kwargs
        All other arguments are forwarded to scatter.

        transform_matrix is necessary for quantifying the contribution of each dimension
        to the principal components being plotted. if not available, don't use this.
        """
        # Number of dimensions to biplot
        n = transform_matrix.shape[0]
        # ensure PCs are uniquely labeled (in case of augmented pcadf)
        PCs.columns = pd.Series(recolumn(PCs.columns))
        # pass labels to interaxes
        # If using augmented pcdf -- make sure no non-numeric columns are passed
        if not dataspan:
            PCdata = PCs
            self.labels = PCs.index
        else:
            PCdata = PCs.iloc[:, dataspan]
            self.labels = PCs.loc[:, ~PCs.columns.isin(PCs.columns[dataspan])] #make this a series!!!!
        # compute normalized coords about zero on plane of major variance
        scalePCdata = PCdata/(PCdata.max()-PCdata.min())
        self.scalexy = scalePCdata.iloc[:, [components[0], components[1]]]
        # use for determining cluster color or unique color behavior
        self.uniqL = self.labels.drop_duplicates()
        # compute projections of original dimensions on plane
        slice1 = transform_matrix[components[0]]
        slice2 = transform_matrix[components[1]]
        proj_slice_transposed = np.stack([slice1, slice2], axis=1)
        xs_weight = proj_slice_transposed[:,0]
        ys_weight = proj_slice_transposed[:,1]
        #todo: if multiiple label columns exist, merge them into a single \n separated column
        def draw_biplot():
            #color and annotate coords by discrete scale, disp scale
            if (self.labels.size > self.uniqL.size) & (self.uniqL.size > 1): 
                clusterxy = pd.concat([self.scalexy, self.labels], axis=1)
                groups = clusterxy.groupby(self.labels.columns.values[0])
                for name, group in groups:
                    self.scatter(group.iloc[:, 0], group.iloc[:, 1],
                                 label = name, picker=True, **kwargs)
                self.legend()
                #cbar = self.figure.colorbar(self, **cbar_kw)
                #cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
            #color and annotate coords by continuous scale, disp scale
            elif (self.labels.size == self.uniqL.size) & (self.uniqL.size > 1):
                #if labels consists of unique strings label without color
                if isinstance(self.labels.dtype, object): #dtype for series (index) dtypes or dataframe
                    self.scatter(self.scalexy.iloc[:, 0], self.scalexy.iloc[:, 1],
                                 picker=True, **kwargs)
                else: #if numbers, make and apply colorscale as well as label
                    self.scatter(self.scalexy.iloc[:, 0], self.scalexy.iloc[:, 1],
                                 c=self.labels, picker=True, **kwargs)
                    cbar = self.figure.colorbar(self, **cbar_kw)
                    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
            else:
                raise ValueError("datalabels badly argued. see biplot docstring")
            #plot and label the original dimension projections
            for i in range(n):
                self.arrow(0, 0, xs_weight[i], ys_weight[i], color = 'r', alpha = 0.5)
                if dim_labels is None:
                    self.text(xs_weight[i] * 1.2, ys_weight[i] * 1.2,
                              "Var"+str(i+1), color = 'g', ha = 'center', va = 'center')
                else:
                    self.text(xs_weight[i] * 1.2, ys_weight[i] * 1.2,
                              dim_labels[i], color = 'g', ha = 'center', va = 'center')
            #set decorations
            self.set_xlabel("PC{}".format(components[0]))
            self.set_ylabel("PC{}".format(components[1]))
            self.grid()
        self.drawself = draw_biplot
        self.drawself()
        
    def pairplot(self, all_truths, all_pred, test_truths, test_pred, labels, **kwargs): #something broken?
        """
        Construct parity plot of predicted vs true values for evaluating accuracy of
        regression models

        Parameters:
        ----------
        all_truths
        the targets the model aimed for in training + the test truths.

        all_pred
        Results of applying model to both training and testing datasets.

        test_truths
        the test truths alone. Technically, could be any secondary set of values. Optional.

        test_pred
        the test predictions alone. Again, flexible. Optional.
        
        labels
        A list equal to the length of all_datapoints. Optional.
    
        Utility Args:
        -------------
        **kwargs
        All other arguments are forwarded to scatter.
        """
        if not datalabels:
            datalabels = xy.index
        #intake coordinates, make as list
        self.labels = np.array(datalabels)
        #self.uniqL = np.self.uniqL(datalabels)
        
        def draw_pairplot():
            self.xselfis.set_tick_params(labelsize=20)
            self.yselfis.set_tick_params(labelsize=20)
            self.axline((0,0), slope=1, ls='-')
            self.activescatter(x=self.test_targets, y=self.test_pred, labels=self.test_labels,
                               c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9,
                               grouplabel='Test', **kwargs)
            self.activescatter(x=self.all_targets, y=self.all_pred, labels=self.test_labels,
                               c='lawngreen', marker='x', s=60, edgecolors='dimgrey', alpha=0.9,
                               grouplabel='Training', **kwargs)
            #self.set_xlim([self.get_xlim()[0],self.get_xlim()[1]])
            #self.set_ylim([self.get_ylim()[0],self.get_ylim()[1]])
            self.set_xlabel("Prediction")
            self.set_ylabel("True value")            
            self.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})
        self.drawself = draw_pairplot
        self.draw_pairplot()
      
register_projection(Interaxes)
