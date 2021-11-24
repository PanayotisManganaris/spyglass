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

register_projection(interaxes)
