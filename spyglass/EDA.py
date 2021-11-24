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
from spyglass.utils import pickle_paste

from matplotlib import colormaps as cmapreg # fixed default colormaps registry

class boilerplate(Figure):
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
        #notice this depends on the boilerplat axes being defined on
        #the figure before any additional -- this is bad.x
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
    # The projection must specify a name. This will be used by the
    # user to select the projection,
    # i.e. ``subplot(projection='custom_hammer')``
    name = 'interactive' #class attribute for index in projections registry
    #def __init__(self, *args, datalabels, **kwargs):
    #    super().__init__(*args, **kwargs) #takes all axes args, exposes
    #                                      #artists + pyplot interface
    #    self.labels = labels
    #    #passing the labels to the axes like this works but they are kwargs only!

    def __init__(self, *args, **kwargs):                             
        super().__init__(*args, **kwargs) #takes all axes args, exposes          
                                          #artists + pyplot interface            
        self.labels = []
        self.x = []
        self.y = []
        #link event handler function to the display
        self.figure.canvas.mpl_connect('pick_event', self.onclickdot)

    #No. Don't want to argue labels in fig, ax init. pass labels to ax
    #projection that knows how to handle them using scripting interface
    #so, we need a clickprocessor wrapper...

    #class annotate_marker_on_click(object):
    #    def __init__(self, datalabel):
    #        """ defines the namespalce and variable used by the callback """
    #        self.labels = datalabels
    #        #link event handler function to the display
    #        self.figure.canvas.mpl_connect('pick_event', self.onclickdot)

                        
    def onclickdot(self, event): #self is not defined?!??!
        """
        define the click on scatter plot marker behavior
        Notice: datalabels must be ordered with data coordinates for meaningful assignment
        """
        ind = event.ind #get index of picked coords -- conveninent
        #save clicked coordinates to position text
        annotx = event.mouseevent.xdata
        annoty = event.mouseevent.ydata
        #save dot coordinates to point arrow
        #dotx = xy[ind, 0]
        #doty = xy[ind, 1]
        # initialize offset to use in adjusting annotation position
        offset = 0
        #if dots overlap, matplotlib returns returns a list of clicked indicies.
        #parse the list:
        for i in ind:
            #Assign a label to its corresponding data point
            label = self.labels[i]
            #log if needed
            # add the text annotation to the axes
            self.makeannotate(label,
                              annotx + offset,
                              annoty + offset,
                              #dotx,
                              #doty
                              )
            self.figure.canvas.draw_idle() #force re-draw
            offset += 0.01 # in case of list, alter offset 

    def activescatter(self, x, y, datalabels): #, x, y, labels, ax=None):
        """
        Test axes with interactivity. 
        Should work with subplots and interactive script syntax
        """
        #plot data
        self.x.extend(x)
        self.y.extend(y)
        self.labels.extend(datalabels)
        self.scatter(x, y, picker=True)
        self.set_xlabel("X")
        self.set_ylabel("Y")
        self.grid()
        
    def makeannotate(self, label, labelx, labely):#, datax, datay):
        """ create and add text to axes """
        text_annotation = Annotation(label, xy=(labelx, labely), #xytext=(labelx, labely),
                                     xycoords='data',
                                     textcoords="offset points",
                                     bbox=dict(boxstyle="round", fc="w"), #what style
                                     arrowprops=dict(arrowstyle="->")) #at what style
        self.add_artist(text_annotation)
        #alternative for less deps?
        #axis.annotate(label, xy=(x,y), xytext=xy, #what, at what, where
        #             xycooords='data', #textcoords="offset points", #at what ref, where ref
        
    def make_onclickclear(self):
        """
        function returning a callback closure that defines the "clear all"
        widget behavior relative to this axes
        """
        def onclickclear(event):
            self.cla() #clear artist objects from axes
            #draw(self)
            self.activescatter(self.x, self.y, self.labels)
        return onclickclear
        
register_projection(interaxes)
