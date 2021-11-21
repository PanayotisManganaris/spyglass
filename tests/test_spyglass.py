from spyglass import __version__


def test_version():
    assert __version__ == '0.1.0'

def test_annotfig():
    xy = np.random.random((10,2))
    labels = ["Label for instance #{0}".format(i) for i in np.arange(xy.shape[0])]
    fig, ax = plt.subplots()

    scfig = testplot(xy[:, 0], xy[:, 1], labels, ax=ax)

    plt.show()

    assert True
    
