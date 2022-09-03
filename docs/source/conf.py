# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyODM'
copyright = '2022, Christopher DeGroot'
author = 'Christopher DeGroot'

import sys
import os
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../..'))
autodoc_member_order = 'bysource'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary',
    'sphinx.ext.doctest', 'sphinx.ext.coverage', 'sphinx.ext.napoleon',
    'sphinx_rtd_theme']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
