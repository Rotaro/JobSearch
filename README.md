# JobSearch
Simple program to combine job search results from several job advertisement sites.

Currently the program has parsers for indeed.fi, monster.fi and duunitori.fi. 
The program gathers job advertisements from these sites based on keywords provided in jobsearch.py. 
The results are stored in a local sqlite database. The entries in the database can viewed in a locally stored html 
table. Filtering entries can only be done by date at the moment.

The program has two modes:

- search
  - The program searches the sites for job advertisements using keywords specified in jobsearch.py
  - Usage: python jobsearch.py <dbname> search
- view
  - The program displays entries in the database filtered by provided dates.
  - Usage: python jobsearch.py <dbname> view -startdate [-enddate]
  
The program is to be expanded to be able to detect relevant job ads. 
The user can currently classify stored ads as relevant or non relevant. This is done using the classify option:

python jobsearch.py <dbname> classify -startdate [-enddate]


This launches a clumsy tkinter GUI used to classify job entries. 
The idea is for the program to use these classified ads as a training set for a machine learning algorithm, 
and then be able to mark job ads as relevant or not.
