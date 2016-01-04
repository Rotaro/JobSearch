.. overview:

Program Structure
==================

Class Descriptions
------------------------------------

Job ads are wrapped in instances of the JobAd class. Each functionality of the program 
is wrapped in its own class.

- :class:`JobAd`

  - Provides a wrapper for job ads, with fields for id, date, search term, site, url, title,
    description, language, relevant and recommendation.
  - Stored in the module job_ad.py.

- :class:`JobAdParser`

  - Responsible for parsing web sites and storing ads in JobAd instances.
  - Each site uses its own subclass of :class:`JobAdParser`.
  - Stored in the module parsers.py.

- :class:`JobAdDB`

  - Responsible for storing and retrieving :class:`JobAd` instances. These are stored in a local
    sql database (sqlite3), with columns for every :class:`JobAd` field.
  - Responsible for outputting job ads in the database as an html or CSV table.
  - Stored in the module db_controls.py.

- :class:`JobAdClassification`

  - Responsible for training machine learning models, providing recommendations and
    automatically determining languages of job ads.
  - Stored in the module classification.py.

- :class:`JobAdGUI`

  - Responsible for allowing users to manually classify job ads in the database.
  - Stored in the module db_gui.py.

- :class:`JobAdCollector`

  - The "main" class of the program, responsible for integrating all the components
    into a single working unit. 
  - Provides methods for running searches for multiple terms on all sites, classifying, viewing
    and determining languages of job ads in the database as well as training, saving and loading
    models.
  - Stored in the module jobadcollector.py.
  
Class Diagram
------------------

.. figure:: /Jobadcollector.png
   :alt: Class diagram of JobAdCollector.
   
   Class diagram of JobAdCollector. The command line interface is not included.

