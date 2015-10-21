import time
import random
import codecs
import sys
import argparse
import datetime
from argparse import RawTextHelpFormatter
import parsers
import db_controls
import db_gui


class JobSearch:
    """ 
    Class for operating job searches. Searches for job ads from Indeed.fi, 
    Duunitori.fi and Monster.fi. Results are stored in a sqlite database named during 
    initiation. Entries in the database can be output as an HTML table. 
    """
    db_name = ""
    search_terms = []

    def __init__(self, search_terms, db_name):
        if (len(search_terms) == 0 or db_name == ""):
            raise ValueError("Invalid arguments for JobSearch")
        self.search_terms = search_terms
        self.db_name = db_name

    def start_search(self, search_term=None):
        """ 
        Starts search for job advertisements for the given search terms. 
        HTML requests are randomly spread out by 3 to 5 seconds. 
        """
        random.seed(1222)
        datab = db_controls.JobEntries(self.db_name)
        datab.set_db()
        if (search_term != None):
            print("Searching for \"%s\"." % search_term)
            time.sleep(random.randint(3,5))
            monster_parser = parsers.MonsterParser()
            indeed_parser = parsers.IndeedParser()
            duunitori_parser = parsers.DuunitoriParser()
            indeed_parser.parse_URL(parsers.URLGenerator.Indeed_URL(search_term))
            monster_parser.parse_URL(parsers.URLGenerator.Monster_URL(search_term))
            duunitori_parser.parse_URL(parsers.URLGenerator.Duunitori_URL(search_term))
            datab.set_new_entries(
                indeed_parser.get_job_entries(), 'indeed', search_term)
            datab.set_new_entries(
                monster_parser.get_job_entries(), 'monster', search_term)
            datab.set_new_entries(
                duunitori_parser.get_job_entries(), 'duunitori', search_term)
        else:
            for search_term in self.search_terms:
                print("Searching for \"%s\"." % search_term)
                time.sleep(random.randint(3,5))
                monster_parser = parsers.MonsterParser()
                indeed_parser = parsers.IndeedParser()
                duunitori_parser = parsers.DuunitoriParser()
                indeed_parser.parse_URL(
                    parsers.URLGenerator.Indeed_URL(search_term))
                monster_parser.parse_URL(
                    parsers.URLGenerator.Monster_URL(search_term))
                duunitori_parser.parse_URL(
                    parsers.URLGenerator.Duunitori_URL(search_term))
                datab.set_new_entries(
                    indeed_parser.get_job_entries(), 'indeed', search_term)
                datab.set_new_entries(
                    monster_parser.get_job_entries(), 'monster', search_term)
                datab.set_new_entries(
                    duunitori_parser.get_job_entries(), 'duunitori', search_term)

    def output_results(self, date_start, date_end, output_name, output_type):
        """ 
        Outputs job ads from the database as an HTML table. Job ads between
        provided dates are returned. If no dates are provided, all job ads are 
        returned from the database.
        
        date_start - datetime.date object corresponding to a date. If None, all 
                     entries since the start of the db are returned.
        date_end   - datetime.date object corresponding to a date. If None, all
                     job entries since date_start are returned.
        output_name - name of the file to store results in. 
        """
        
        datab = db_controls.JobEntries(self.db_name)
        datab.set_db()
        print("Writing to %s from %s." % (output_name, self.db_name))
        if (output_type == "html"):
            file = codecs.open(output_name, "w", encoding="utf-8")
            file.write(datab.generate_HTML_table(datab.get_entries(date_start, date_end)))
            file.close()
        elif (output_type == "csv"):
            datab.write_CSV_file(datab.get_entries(date_start, date_end), output_name)

    def classify_data(self, date_start, date_end):
        """ 
        Starts GUI for classifying database entries between given dates.
        
        date_start - datetime.date object corresponding to a date. If None, all 
                     entries since the start of the db are returned.
        date_end   - datetime.date object corresponding to a date. If None, all
                     job entries since date_start are returned.
        """
        datab = db_controls.JobEntries(self.db_name)
        datab.set_db()

        gui = db_gui.JobSearchGUI(datab.get_entries(date_start, date_end).fetchall())
        gui.mainloop()
        new_data = gui.dataStorage #dictionary with id as key
        datab.update_w_dict(new_data)


my_search_terms = [
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
    'Diplomi',
    'Machine learning',
    'Koneoppiminen']

                                
def main(argv):
    #set up command line arguments parser
    argparser = argparse.ArgumentParser(description="""
        Parses and stores job advertisements from Duunitori.fi, \
        Monster.fi and Indeed.fi in a local sqlite database. Provides the \
        possibility of classifying existing job advertisements in the \
        database and training a CART model to provide recommendations \
        for new job advertisements. The CART model uses text in job \
        advertisements to determine recommendations. 
        """)
    argparser.add_argument('db_name', type=str, 
                           help="Name of sqlite database. If nonexistant, \
                                 an empty one is created.")
    subparsers = argparser.add_subparsers(dest='mode')
    #parser for searching for job ads
    search_parser = subparsers.add_parser('search', help='Search for job ads.')
    search_parser.add_argument('-search_term', type=str,
        help="Optional search term. If not provided, the my_search_terms list \
            is used.")
    #parser for viewing entries
    view_parser = subparsers.add_parser('view', help="View entries in db.")
    view_parser.add_argument('start', help="Start date of entries (%d-%m-%Y).")
    view_parser.add_argument('-end', help="End date of entries (%d-%m-%Y). \
        If not provided, the present date is used.")
    view_parser.add_argument('output_name',
        help="Name of file to output view to. The output is in the format of \
            an HTML table.")
    view_parser.add_argument('-output_type', help="Type of output file, html-table or csv. \
        If not provided, html-table is used.", default="html")
    #parser for classifing existing entries
    class_parser = subparsers.add_parser('classify', help="Classify entries in db.")
    class_parser.add_argument('start', help="Start date of entries (%d-%m-%Y).")
    class_parser.add_argument('-end', help="End date of entries (%d-%m-%Y). \
        If not provided, the present date is used.")
    parsed_argv = argparser.parse_args()
    print(parsed_argv)
    #execute command line arguments
    js = JobSearch(my_search_terms, parsed_argv.db_name)
    if (parsed_argv.mode == "view"):
        start = datetime.datetime.strptime(parsed_argv.start, '%d-%m-%Y')
        if (parsed_argv.end):
            end = datetime.datetime.strptime(parsed_argv.end, '%d-%m-%Y')
        else:
            end = datetime.date.today()
        js.output_results(start, end, parsed_argv.output_name, parsed_argv.output_type)
    elif(parsed_argv.mode == "classify"):
        start = datetime.datetime.strptime(parsed_argv.start, '%d-%m-%Y')
        if (parsed_argv.end):
            end = datetime.datetime.strptime(parsed_argv.end, '%d-%m-%Y')
        else:
            end = datetime.date.today()
        js.classify_data(start, end)
    elif(parsed_argv.mode == "search"):
        js.start_search()


if (__name__ == "__main__"):
    main(sys.argv)