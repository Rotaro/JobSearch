import parsers
import db_controls
import datetime
import time
import random
import codecs

class JobSearch:
    """ Class for operating job searches. Searches for job ads from Indeed.fi, Duunitori.fi 
    and Monster.fi. Results are stored in a sqlite database named during initiation. Entries
    in the database can be output as an HTML table. """
    db_name = ""
    search_terms = []

    def __init__(self, search_terms, db_name):
        if (len(search_terms) == 0 or db_name == ""):
            raise ValueError("Invalid arguments for JobSearch")
        self.search_terms = search_terms
        self.db_name = db_name

    def start_search(self):
        """ Starts search for job advertisements for the given search terms. 
        HTML requests are randomly spread out by 3 to 5 seconds. """

        random.seed(1222)
        datab = db_controls.JobEntries(self.db_name)
        datab.set_db()
        for search_term in self.search_terms:
            print("Searching for \"%s\"." % search_term)
            time.sleep(random.randint(3,5))
            monster_parser = parsers.MonsterParser()
            indeed_parser = parsers.IndeedParser()
            duunitori_parser = parsers.DuunitoriParser()
            indeed_parser.parse_URL(parsers.URLGenerator.Indeed_URL(search_term))
            monster_parser.parse_URL(parsers.URLGenerator.Monster_URL(search_term))
            duunitori_parser.parse_URL(parsers.URLGenerator.Duunitori_URL(search_term))
            datab.set_new_entries(indeed_parser.get_job_entries(), 'indeed', search_term)
            datab.set_new_entries(monster_parser.get_job_entries(), 'monster', search_term)
            datab.set_new_entries(duunitori_parser.get_job_entries(), 'duunitori', search_term)

    def output_results_HTML(self, date, outputname):
        """ Outputs job ads from the database as an HTML table. Job ads newer than the provided
        date are included. If no date is provided, all job ads are taken from the database.
        
        date       - datetime.date object corresponding to a date. Job ads in the database which 
                     are newer than this date are included in the output.
        outputname - name of the file to store results in. 
        """
        
        datab = db_controls.JobEntries(self.db_name)
        datab.set_db()

        print("Writing to %s from %s." % (outputname, self.db_name))
        file = codecs.open(outputname, "w", encoding="utf-8")
        file.write(datab.generate_HTML_table(datab.get_entries(date)))
        file.close()


search_terms = [
    'Analyytikko',
    'Analyst',
    'Physics',
    'Fysiikka',
    'Fyysikko',
    'Science',
    'M.Sc',
    'FM',
    'Entry',
    'First',
    'Graduate',
    'Associate',
    'Matlab',
    'Tohtorikoulutettava',
    'Doctoral',
    'Materials',
    'Materiaali',
    'Diplomi']



tod = datetime.date.today()
yes = tod - datetime.timedelta(days=1)
dayyes = tod - datetime.timedelta(days=2)

js = JobSearch(search_terms, "tmp.db")
js.start_search()
js.output_results_HTML(yes, "test.html")