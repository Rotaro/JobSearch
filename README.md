# JobSearch
A simple program to combine job search results from several job advertisement sites.

Currently the program has parsers for indeed.fi, monster.fi and duunitori.fi. 
The program gathers job advertisements from these three sites using keywords set in jobsearch.py. 
The results of the keyword searches are stored in a local sqlite database, which can be viewed as an html or csv table. The program only supports filtering database entries by date at the moment. 

The program has two modes:

- search
  - The program searches sites for job advertisements using keywords specified in jobsearch.py
  - Usage: python jobsearch.py <dbname> search
- view
  - The program displays entries in the database filtered by provided dates.
  - Usage: python jobsearch.py <dbname> view -startdate [-enddate]
  
The program is to be expanded to be able to classify job ads based on previous database entries.
The user can currently classify stored ads as relevant or not relevant. This is done using the classify option:

python jobsearch.py <dbname> classify -startdate [-enddate]

This launches a clumsy tkinter GUI which allows for the the language and relevance of entires in the database to be altered.
The program is to use classified ads as a training set for a machine learning algorithm, to be able to identify new, relevant job ads.
