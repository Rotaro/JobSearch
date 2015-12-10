import time
import random
import codecs
import sys
import argparse
import datetime
from argparse import RawTextHelpFormatter
import jobadcollector

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
    js = jobadcollector.JobAdCollector(my_search_terms, parsed_argv.db_name)
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