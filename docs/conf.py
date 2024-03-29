# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pkg_resources
sys.path.insert(0, os.path.abspath('../'))


# -- Project information -----------------------------------------------------

project = 'perceptivo'
copyright = '2021, Jonny L Saunders, Avinash Singh Bala'
author = 'Jonny L Saunders, Avinash Singh Bala'

# The full version, including alpha/beta/rc tags
release = pkg_resources.get_distribution('perceptivo').version



# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'myst_parser',
    'sphinxcontrib.bibtex',
    'matplotlib.sphinxext.plot_directive',
    'sphinxcontrib.autodoc_pydantic'
]

# --------------------------------------------------
# Napoleon config
# --------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_use_param = False
napoleon_use_ivar = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True

# --------------------------------------------------
# Autosummary & Autodoc config
# --------------------------------------------------

autoclass_content = "both"
autodoc_member_order = "bysource"
autodata_content = "both"
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'private-members': False,
    'show-inheritance': False,
    'toctree': True,
    'undoc-members': True,
    'autosummary': True
}

autodoc_mock_imports = ['autopilot', 'PySide6', 'pyqtgraph', 'pyzmq', 'zmq', 'soundcard']

autosummary_generate = False

# --------------------------------------------------
# MyST
# --------------------------------------------------

myst_enable_extensions = [
    'tasklist'
]

# --------------------------------------------------
# intersphinx
# --------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'autopilot': ('https://docs.auto-pi-lot.com/en/dev', None),
    'skimage': ('https://scikit-image.org/docs/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable', None)
}


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

bibtex_bibfiles=['perceptivo.bib']


# show source code in ..plot directive calls
plot_include_source = True