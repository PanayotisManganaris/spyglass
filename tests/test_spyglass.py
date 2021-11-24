from spyglass import __version__
import spyglass
import spyglass
import numpy as np

def test_version():
    assert __version__ == '0.1.0'

def test_annotfig():
    eda = spyglass.EDA.EDAFigure

    xy = np.random.random((10,2))
    labels = ["Label for instance #{0}".format(i) for i in np.arange(xy.shape[0])]

    fig, ax = plt.subplots(1,1, FigureClass=eda, subplot_kw={'projection':'interactive'})
    fig.add_button()
    ax.activescatter(xy[:,0], xy[:,1], labels)

    assert True
    
