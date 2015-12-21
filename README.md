# JobAdCollector
A simple program to combine job search results from several job advertisement sites.

Currently the program has parsers for indeed.fi, monster.fi and duunitori.fi. 
The program gathers job advertisements from these three sites using keywords provided. 
The results of the keyword searches are stored in a local sqlite database, which can be viewed as an html or csv table. Additionally, the program supports classifying job ads as relevant or not. The program can then train a random forest model to provide recommendations for new ads.

Included in the repository is a command line interface, jobad_cmdline.py. The interface has the following modes:

- search
  - Searches sites for job advertisements using keywords specified in jobad_cmdline.py
  - Usage: python jobad_cmdline.py <dbname> search
- view
  - Displays entries in the database in a file. Filtered by date.
  - Usage: python jobad_cmdline.py <dbname> view startdate [-enddate] output_name [-output_type]
- classify
  - GUI for classifying job ads in database as relevant or not.
  - Usage: python jobad_cmdline.py <dbname> classify startdate [-enddate]
- detlang (requires R and rpy2)
  - Attempts to determine language of stored job ads.
  - Usage: python jobad_cmdline.py <dbname> Rfunc detlang startdate enddate
- train (requires R and rpy2)
  - Trains a random forest model based on classified ads and stores it in a local file.
  - Usage: python jobad_cmdline.py <dbname> Rfunc train -startdate -enddate language output_name
- recomm (requires R and rpy2)
  - Provides recommendations for job ads using provided random forest model.
  - Usage: python jobad_cmdline.py <dbname> Rfunc recomm language input_name startdate enddate
- search (with recommendations, requries R and rpy2)
  - Searches sites for job ads and provides recommendations using provided model.
  - Usage: python jobad_cmdline.py <dbname> Rfunc search language input_name 
  
