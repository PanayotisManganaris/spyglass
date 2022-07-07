import pkg_resources

installed = [pkg.key for pkg in pkg_resources.working_set]

if 'plotly' in installed:
    from ._plotly_fig_library import _make_parity_fig
else: #or import error
    from ._sns_fig_library import _make_parity_fig

__all__ = ['_make_parity_fig']
