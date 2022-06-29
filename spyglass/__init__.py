__version__ = '0.1.2'

import pkg_resources

installed = [pkg.key for pkg in pkg_resources.working_set]

if 'plotly' in installed:
    from ._plotly_model_imaging import parityplot
else:
    from ._sns_model_imaging import parityplot
    
#consider moving all of this to a dedicated Backend subpackage? see hvplot package?
# from spyglass.spyglass.plotmodule import (
#     PlotModule,
#     GraphModule,
# )
# # for full api compliance, a selection of modules should be supplied, including:
# #    deregister,
# #    register,

# #for linting? static type checkers?
# if TYPE_CHECKING:
#     from pandas.plotting._matplotlib.core import MPLPlot

# PLOT_CLASSES: dict[str, type[MPLPlot]] = {
#     "line": LinePlot,
#     "bar": BarPlot,
#     "barh": BarhPlot,
#     "box": BoxPlot,
#     "hist": HistPlot,
#     "kde": KdePlot,
#     "area": AreaPlot,
#     "pie": PiePlot,
#     "scatter": ScatterPlot,
#     "hexbin": HexBinPlot,
# }

# #public plot method provides spyglass as pandas plotting backend
# def plot(data, kind, **kwargs):
#     # Importing pyplot at the top of the file (before the converters are
#     # registered) causes problems in matplotlib 2 (converters seem to not
#     # work)
#     import matplotlib.pyplot as plt

#     if kwargs.pop("reuse_plot", False):
#         ax = kwargs.get("ax")
#         if ax is None and len(plt.get_fignums()) > 0:
#             with plt.rc_context():
#                 ax = plt.gca()
#             kwargs["ax"] = getattr(ax, "left_ax", ax)
#     plot_obj = PLOT_CLASSES[kind](data, **kwargs)
#     plot_obj.generate()
#     plot_obj.draw()
#     return plot_obj.result

# __all__ = [
#     "plot", #what's this? the accessor?, the public method?
#     "PlotModule",
#     "GraphModule", #? or keys?
# ]
