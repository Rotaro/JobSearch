#JobAdCollector

A simple program to combine job search results from several job advertisement sites.

Currently `JobAdCollector` has parsers for indeed.fi, monster.fi and duunitori.fi. 
The program gathers job advertisements from these sites using keywords 
provided. The results of the keyword searches are stored in a local sqlite 
database, which can be viewed as an html or csv table. Additionally, users can classify 
job ads as relevant or not, which allows `JobAdCollector` to provide recommendations for new job
ads using a machine learning model.


##Usage

A command line interface is provided for operating `JobAdCollector`. To make batch searches easier, 
the command line can parse search terms from a text file where search terms are separated by new lines
(UTF-8 encoding).


   Example of search term file:



      dream job
      great job
      ....

To access the interface, run `JobAdCollector` as a script:

      python -m jobadcollector 

The -h flag provides help for each command. All possible commands are listed below.

###Command Line Options

   
- **search**

  Searches sites for job advertisements using keywords in the file <my_search_terms> and saves 
  them in the database <db_name>.
  
  ```python -m jobadcollector <db_name> search <my_search_terms>```

- **view**

  Displays ads between dates <start_date>, <end_date> (format %d-%m-%Y) in the database <db_name> as a table. The table is       saved in the file <output_name> as <output_type> (html or csv). 

  ```python -m jobadcollector <db_name> view <start_date> [-end_date] <output_name> [-output_type]```


- **classify**
  
  Starts GUI for classifying job ads in database <db_name> between
  dates <start_date>, <end_date> (format %d-%m-%Y).

  ```python -m jobadcollector <db_name> classify <start_date> [-end_date]```
  
- **Rfunc**

  Option for using functionalities which require R and rpy2. These require all search
  terms to be provided in a file <my_search_terms>.

  - **detlang**
  
    Attempts to determine language of job ads in database <db_name> between
    dates <start_date>, <end_date> (format %d-%m-%Y).
   
    ```python -m jobadcollector <db_name> Rfunc <my_search_terms> detlang <start_date> <end_date>```
  
  - **train**
  
    Trains model on classified ads in database <db_name> between
    dates <start_date>, <end_date> (format %d-%m-%Y). Only uses ads of language <language>.
    The model is saved in the file <output_name>.

    ```python -m jobadcollector <db_name> Rfunc <my_search_terms> train <start_date> <end_date> <language> <output_name>```
  
  - **recomm**
  
    Provides recommendations for job ads in database <db_name> between dates <start_date>, <end_date> 
    (format %d-%m-%Y) using the model <input_name> of language <language>. 

    ```python -m jobadcollector <db_name> Rfunc <my_search_terms> recomm <language> <input_name> <start_date> <end_date>```
  
  - **Rfuncsearch**
  
    Searches sites for job advertisements using keywords in the file <my_search_terms> and saves 
    them in the database <db_name>. Also automatically determines languages of new job ads and provides
    recommendations using designated model <input_name> of language <language>.

    ```python -m jobadcollector <db_name> Rfunc <my_search_terms> Rfuncsearch <language> <input_name>```

