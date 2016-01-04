.. _glossary:

Glossary
==================

.. glossary::

   JobAdCollector
	The program or the main :any:`class <jobadcollector.JobAdCollector>` of the program.

   Job ad
	Advertisement for a job on a :term:`job advertisement site <Job ad site>`.
	
   Job ad site
	Site providing job ads, possibly from many sources.
   
   Parsed job ad
	A job ad which has been processed by :term:`JobAdCollector`, i.e.
	id, title, and description have been collected.
		
   JobAd
	Class representing job ads in :term:`JobAdCollector`. A 
	:py:class:`JobAd <jobadcollector.job_ad.JobAd>` instance contains the following information:   
		                                                        
	- id (id of job ad on site)                          
	- date (date of retrieval)                           
	- search term (term used to find job ad)             
	- site (origin of job ad)                            
	- url (url to job ad)                                	
	- title (title of job ad)                            
	- description (all additional information)           
	- language (language of job ad)                      
	- :term:`relevant <Relevant>`                                           
	- :term:`recommendation <Recommendation>`     

   Relevant
	An indicator of whether the job ad was of interest 
	or not. Can be manually set with the :term:`JobAdGUI`. 
	 
   JobAdGUI
	Tkinter GUI which provides manual editing of language, 
	:term:`relevancy <Relevant>` and :term:`recommendation <Recommendation>` of job ads stored in the database. 
	Also the name of the :py:class:`class <jobadcollector.db_gui.JobAdGUI>` implementing the GUI. 

   Tkinter 
	Python standard library GUI. 

   Recommendation
	Prediction of :term:`relevancy <Relevant>` by machine learning model.

   Machine Learning Model
	Implementation of a machine learning algorithm.
	 
   Classification
	User provided :term:`relevancy <Relevant>` for job ads in database. 
		 
   Training model
	Using :term:`classified <Classification>` job ads to "teach" the machine learning model to provide :term:`recommendations <Recommendation>`. 

   Command Line Interface
        A :doc:`command line interface <commandline>` implemented in the module 
	jobad_cmdline.py which operates :term:`JobAdCollector`.