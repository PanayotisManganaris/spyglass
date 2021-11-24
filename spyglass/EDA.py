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
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.projections import register_projection # proper axes patching method
from matplotlib.widgets import Button
from matplotlib.text import Annotation
from matplotlib.transforms import blended_transform_factory
from matplotlib.patches import Ellipse

from matplotlib import colormaps as cmapreg # fixed default colormaps registry

import numpy as np

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
    
class interaxes(Axes):
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
            self.boilerplate() #draw the chosen boilerplate axes
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
        trans = blended_transform_factory(x_transform=self.transAxes,
                                          y_transform=self.transData)
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

    def onclickdot(self, event): #self is not defined?!??!
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
        for i in ind:
            #Assign a label to its corresponding data point
            label = self.labels[i]
            # add the text annotation to the axes
            self.makeannotate(label,
                              annotx + offset,
                              annoty + offset)
            self.figure.canvas.draw_idle() #force re-draw
            offset += 0.05 # in case of list, alter offset 

    def activescatter(self, x, y, datalabels): #, x, y, labels, ax=None):
        """
        Test axes with interactivity. 
        Should work with subplots and interactive script syntax
        """
        #place arguments in instance namespace
        self.x = x
        self.y = y
        self.labels = datalabels
        #plot data
        def draw_activescatter():
            self.scatter(self.x, self.y, picker=True)
            self.set_xlabel("X")
            self.set_ylabel("Y")
            self.grid()
        self.boilerplate = draw_activescatter
        self.boilerplate()

    def biplot(components, PCs, transform_matrix, dim_labels=None, N_labels=[], cbar_kw={}, cbarlabel="", **kwargs):
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
        D-colummn DataFrame where each column is a principal component.
        transform_matrix
        DxD array of component weights summarizing the contribution of each dimension to
        each PC. Meant for use with PCA by sklearn.Decomposition.PCA.components_
        dim_labels
        D-length list of dimension labels corresponding the axes of the original
        data-space transformed in the PCA.
        N_labels
        Either:
        1. N-length pandas Series of unique labels to individually annotate each datapoint 
           Optionally, use cbar* args to control continuous coloration. String labels will be
           white.
        2. N-length list of nonunique labels to be annotate clusters of datapoints
           use with cbar* args to control descrete coloration
        3. None. Datapoints will be white and noninteractive
    
        Utility Args:
        -------------
        ax
        A `matplotlib.axes.Axes` instance on which the principal coordinates are scattered.
        If not provided, use current axes or create a new one.  Optional.
        cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
        cbarlabel
        The label for the colorbar.  Optional.
        ,**kwargs
        All other arguments are forwarded to `scatter`.
    
        transform_matrix is necssary for quantifying the contribution of each dimension
        to the principal components being plotted
        """
        #Number of dimensions to biplot
        n = transform_matrix.shape[0]
        #plot the plane of major variance
        xs = PCs.iloc[:,components[0]]
        ys = PCs.iloc[:,components[1]]
        scalex = 1.0/(xs.max() - xs.min())
        scaley = 1.0/(ys.max() - ys.min())
        N_labels = np.array(N_labels)
        unique = np.unique(N_labels)
        #wip:
        #color and annotate coords by discrete scale, disp scale
        if (N_labels.size > unique.size) & (unique.size > 1): 
            #TODO if scale consists of unique strings color discrete strings uniquely + label
            scatterplane = self.scatter(xs * scalex, ys * scaley, c = N_labels, **kwargs)
            cbar = self.figure.colorbar(scatterplane, ax=self, **cbar_kw)
            cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
        #color and annotate coords by continuous scale, disp scale
        elif (N_labels.size == unique.size) & (unique.size > 1):
            groups = PCs.groupby(
            #TODO if scale consists of unique strings label without color
            #if numbers, make and apply colorscale as well as label
            scatterplane = self.scatter(xs * scalex, ys * scaley, c = N_labels, **kwargs)
            cbar = self.figure.colorbar(scatterplane, ax=self, **cbar_kw)
            cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
        #quick view, no scale
        elif N_labels.size == 0:
            scatterplane = self.scatter(xs * scalex, ys * scaley, **kwargs)
        else:
            raise ValueError("N_labels badly argued. see biplot docstring")
        #plot and label projection of original dimensions on plane
        slice1 = transform_matrix[components[0]]
        slice2 = transform_matrix[components[1]]
        proj_slice_transposed = np.stack([slice1, slice2], axis=1)
        xs_weight = proj_slice_transposed[:,0]
        ys_weight = proj_slice_transposed[:,1]
        def draw_biplot():
            for i in range(n):
                ax.arrow(0, 0, xs_weight[i], ys_weight[i], color = 'r', alpha = 0.5)
                if dim_labels is None:
                    self.text(xs_weight[i] * 1.2, ys_weight[i] * 1.2,
                              "Var"+str(i+1), color = 'g', ha = 'center', va = 'center')
                else:
                    self.text(xs_weight[i] * 1.2, ys_weight[i] * 1.2,
                              dim_labels[i], color = 'g', ha = 'center', va = 'center')
                    self.set_xlabel("PC{}".format(components[0]))
                    self.set_ylabel("PC{}".format(components[1]))
                    self.grid()
        self.boiilerplate = draw_biplot
        self.draw_biplot()

    def pairplot(truths, predictions, N_labels=[], **kwargs):
        """
        modify or create and return axis containing pairity plot of
        predicted vs true values for evaluating accuracy of regression models
    
        Parameters:
        ----------
        preds
        predictions generated by a model -- make predictions both for training and testing datasets
        may be a pandas series, array, or list. preds is truncated to the length of truths.

        truths
        the labels used to guide the model training -- uses test labels to validate model accuracy
        may be a pandas series, array, or list. Should be of the same type as preds.

        N_labels
        A list equal to the length of the datapoints. Optional.
    
        Utility Args:
        -------------
        ax
        A `matplotlib.axes.Axes` instance on which the parity coordinates are scattered.
        If not provided, use current axes or create a new one.  Optional.
        ,**kwargs
        All other arguments are forwarded to `scatter`.
        """
        #intake coordinates, make as list
        N_labels = np.array(N_labels)
        unique = np.unique(N_labels)
        a = [-175,0,125]
        b = [-175,0,125]
                
        training_parity = ax.scatter(train_x, train_y, c = 'orangered', **kwargs)
        testing_parity = ax.scatter(test_x, test_y, c = 'lawngreen', **kwargs)
    
    
    
        ax1.plot(b, a, c='k', ls='-')
        ax1.xaxis.set_tick_params(labelsize=20)
        ax1.yaxis.set_tick_params(labelsize=20)
        ax1.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered',
                    marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
        ax1.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen',
                    marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
        te = '%.2f' % rmse_test_latt
        tr = '%.2f' % rmse_train_latt
        ax.text(5.96, 5.48, 'Test_rmse = ' + te + ' $\AA$', c='navy', fontsize=16)
        ax.text(5.93, 5.28, 'Train_rmse = ' + tr + ' $\AA$', c='navy', fontsize=16)
        ax.set_ylim([5.1, 7.1])
        ax.set_xlim([5.1, 7.1])
        ax.set_xticks([5.5, 6.0, 6.5, 7.0])
        ax.set_yticks([5.5, 6.0, 6.5, 7.0])
        ax.set_title('Lattice Constant ($\AA$)', c='k', fontsize=20, pad=12)
        ax.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

      
register_projection(interaxes)
