import sys
import argparse
import datetime
import os

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
    #Set up main command line argument parser
    argparser = argparse.ArgumentParser(description=
        """Commandline user interface for JobAdCollector. 

        Allows for parsing, viewing, classifying and recommending job ads 
        using simple command line arguments.
        """)
    #Parse for database name
    argparser.add_argument("db_name", type=str, 
        help="""Name of sqlite database. If one doesn't exist, an empty one is 
                created.""")

    #Set up parser for modes (search, view, classify, Rfunc)
    subparsers = argparser.add_subparsers(dest='mode')

    #mode - search
    search_parser = subparsers.add_parser("search", help="Search for job ads.")
    search_parser.add_argument("-search_term", type=str,
        help="""Optional search term. If not provided, the my_search_terms 
                variable is used.""")

    #mode - view
    view_parser = subparsers.add_parser("view", help="View entries in db.")
    view_parser.add_argument("start", 
        help="""Include ads from this date forward (%%d-%%m-%%Y).""")
    view_parser.add_argument("-end", 
        help="""Last date of ads (%%d-%%m-%%Y). If not provided, the present date 
                is used.""")
    view_parser.add_argument("output_name", 
        help="""Name of file to output ads to.""")
    view_parser.add_argument("-output_type", 
        help="""Type of output file, html or csv. If not provided, html is used.""", 
        default="html")

    #mode - classify
    class_parser = subparsers.add_parser("classify", 
        help="""User classification of ad relevancy. Done in clumsy 
                tkinter GUI.""")
    class_parser.add_argument("start", help="First date of ads (%%d-%%m-%%Y).")
    class_parser.add_argument("-end", 
        help="""Last date of ads (%%d-%%m-%%Y). If not provided, the present 
                date is used.""")

    #mode - Rfunc 
    R_func_parser = subparsers.add_parser("Rfunc", 
        help="""Enables use of R functions. Requires both R and 
                rpy2 to be installed.""")

    #new subparser for Rfunc modes (detlang, train, recomm, search)
    R_func_subparsers = R_func_parser.add_subparsers(dest='Rfunmode')

    #Rfunc - detlang
    R_fun_detlang = R_func_subparsers.add_parser("detlang", 
        help="""Determine language of job ads and store results in database.""")
    R_fun_detlang.add_argument("start", help="First date of ads (%%d-%%m-%%Y).")
    R_fun_detlang.add_argument("end", 
        help="""Last date of ads (%%d-%%m-%%Y). If not provided, 
                the present date is used.""")

    #Rfunc - classify
    R_fun_train = R_func_subparsers.add_parser("train",
        help="""Trains classification model on job ads.""")
    R_fun_train.add_argument("-start", 
        help="""First date of ads (%%d-%%m-%%Y). If not provided, all ads 
                since start of database are used.""")
    R_fun_train.add_argument("-end", 
        help="""Last date of ads (%%d-%%m-%%Y). If not provided, 
                the present date is used.""")
    R_fun_train.add_argument("language", 
        help="Language of ads (English or Finnish).")
    R_fun_train.add_argument("output_name", 
        help="""Name of file to store trained model in.""")

    #Rfunc - recomm
    R_fun_train = R_func_subparsers.add_parser("recomm",
        help="""Recommends job ads using saved classification model.""")
    R_fun_train.add_argument("language", 
        help="Language of ads (English or Finnish).")
    R_fun_train.add_argument("input_name", 
        help="Name of file model is stored in.")
    R_fun_train.add_argument("start", 
        help="""First date of ads (%%d-%%m-%%Y). If not provided, all ads 
                since start of database are used.""")
    R_fun_train.add_argument("end", 
        help="""Last date of ads (%%d-%%m-%%Y). If not provided, 
                the present date is used.""")

    #Rfunc - search
    R_fun_search = R_func_subparsers.add_parser("search",
        help="""Searches for new job ads and classifies them using 
                specified model.""")
    R_fun_search.add_argument("language", 
        help="Language of ads to classify (English or Finnish).")
    R_fun_search.add_argument("input_name", 
        help="Name of file model is stored in.")
    
    parsed_argv = argparser.parse_args()

    print("Command line arguments detected: ")
    print(parsed_argv)

    #Execute command line arguments
    #Set dates (always same keyword)
    if "start" in parsed_argv and parsed_argv.start != None:
        start = datetime.datetime.strptime(parsed_argv.start, "%d-%m-%Y")
    else:
        start = datetime.datetime.strptime("01-01-2015", "%d-%m-%Y")
    if "end" in parsed_argv and parsed_argv.end != None:
        end = datetime.datetime.strptime(parsed_argv.end, "%d-%m-%Y")
    else:
        end = datetime.date.today()

    if parsed_argv.mode == "Rfunc":
        jac = jobadcollector.JobAdCollector(my_search_terms, 
            parsed_argv.db_name, classification = True)
        if parsed_argv.Rfunmode == "detlang":
            jac.det_lang_store_ads(start, end)
        if parsed_argv.Rfunmode == "train":
            RFC = jac.train_model(parsed_argv.language, start, end)
            jac.save_model(RFC, parsed_argv.output_name)
        if parsed_argv.Rfunmode == "recomm":
            RFC = jac.load_model(parsed_argv.language, parsed_argv.input_name)
            jac.recomm_store_ads(RFC, parsed_argv.language, start, end)
        if parsed_argv.Rfunmode == "search":
            start = datetime.datetime.today() - datetime.timedelta(days=1)
            end = datetime.datetime.today()
            jac.start_search()
            jac.det_lang_store_ads(start, end)
            RFC = jac.load_model(parsed_argv.language, parsed_argv.input_name)
            jac.recomm_store_ads(RFC, parsed_argv.language, start, end)

    else:
        jac = jobadcollector.JobAdCollector(my_search_terms, 
                                            parsed_argv.db_name)
        if parsed_argv.mode == "view":
            jac.output_results(start, end, parsed_argv.output_name, 
                               parsed_argv.output_type)
        elif parsed_argv.mode == "classify":
            jac.classify_ads_GUI(start, end)
        elif parsed_argv.mode == "search":
            if ("search_term" in parsed_argv):
                jac.start_search(parsed_argv.search_term)

if (__name__ == "__main__"):
    main(sys.argv)