.. commandline:

Command Line Interface
==========================

What is it?
-------------
A command line interface is provided for operating the program found in the module 
jobad_cmdline.py. The interface has the following functionalities:

- Parses search terms from a text file with terms separated by new lines (UTF-8 encoding).

  .. code-block:: none
  
     search term 1
     search term 2
     ....

To access the interface, run :term:`JobAdCollector` as a script:

.. code-block:: none

   python -m jobadcollector 
   
Help can always be accessed using the -h flag. See the next section for a list of options.

Command Line Options
----------------------
   
.. option:: search
   
   Searches sites for job advertisements using keywords in the file <my_search_terms> and saves 
   them in the database <db_name>.
   
   .. code-block:: none

      python -m jobadcollector <db_name> search <my_search_terms>

.. option:: view

   Displays ads between dates <start_date>, <end_date> (format %d-%m-%Y) in the database 
   <db_name> as a table. The table is saved in the file <output_name> as <output_type> 
   (html or csv). 
   
   .. code-block:: none
   
      python -m jobadcollector <db_name> view <start_date> [-end_date] <output_name> [-output_type]

.. option:: classify
  
   Starts GUI for :term:`classifying <Classification>` job ads in database <db_name> between
   dates <start_date>, <end_date> (format %d-%m-%Y).
   
   .. code-block:: none
   
      python -m jobadcollector <db_name> classify <start_date> [-end_date]
  
.. option:: Rfunc

   Option for using functionalities which require R and rpy2. These require all search
   terms to be provided in a file <my_search_terms>.
   
   .. option::  detlang
  
      Attempts to determine language of job ads in database <db_name> between
      dates <start_date>, <end_date> (format %d-%m-%Y).
      
      .. code-block:: none
   
         python -m jobadcollector <db_name> Rfunc <my_search_terms> detlang <start_date> <end_date>
  
   .. option:: train 
  
      :term:`Trains <training model>` model on :term:`classified <Classification>` ads in database <db_name> between
      dates <start_date>, <end_date> (format %d-%m-%Y). Only uses ads of language <language>.
      The model is saved in the file <output_name>.
      
      .. code-block:: none
         
	 python -m jobadcollector <db_name> Rfunc <my_search_terms> train <start_date> <end_date> <language> <output_name>
  
   .. option:: recomm 
  
      Provides :term:`recommendations <Recommendation>` for job ads in database <db_name> between dates <start_date>, <end_date> 
      (format %d-%m-%Y) using the model <input_name> of language <language>. 
      
      .. code-block:: none
         
	 python -m jobadcollector <db_name> Rfunc <my_search_terms> recomm <language> <input_name> <start_date> <end_date>
  
   .. option:: Rfuncsearch
  
      Searches sites for job advertisements using keywords in the file <my_search_terms> and saves 
      them in the database <db_name>. Also automatically determines languages of new job ads and provides
      :term:`recommendations <Recommendation>` using designated model <input_name> of language <language>.
      
      .. code-block:: none
         
	 python -m jobadcollector <db_name> Rfunc <my_search_terms> Rfuncsearch <language> <input_name>
  
Additional help can be found by using the -h flag.
