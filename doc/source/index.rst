.. JobAdCollector documentation master file, created by
   sphinx-quickstart on Tue Dec 22 15:38:37 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

JobAdCollector
==========================================

Introduction
------------------------------------------
A simple program to combine job search results from several job advertisement sites.

Currently JobAdCollector has parsers for indeed.fi, monster.fi and duunitori.fi. 
The program gathers job advertisements from these sites using keywords 
provided. The results of the keyword searches are stored in a local sqlite 
database, which can be viewed as an html or csv table. Additionally, users can classify 
job ads as relevant or not, which allows JobAdCollector to provide recommendations for new job
ads using a machine learning model.

JobAdCollector can be run using command line arguments, see :any:`commandline` for more 
information.

Contents of Documentation
------------------------------------------

.. toctree::
   :maxdepth: 2
   
   overview.rst
   glossary_prop.rst
   commandline.rst
   modules.rst

* :ref:`genindex`

