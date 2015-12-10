import datetime
from . import parsers, db_controls, db_gui


class JobAdCollector:
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
        Starts search for job advertisements using provided search terms. 
        HTML requests are randomly delayed by 3 to 5 seconds. 
        """
        random.seed(1222)
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()
        if (search_term != None):
            print("Searching for \"%s\"." % search_term)
            time.sleep(random.randint(3,5))
            monster_parser = parsers.MonsterParser()
            indeed_parser = parsers.IndeedParser()
            duunitori_parser = parsers.DuunitoriParser()
            indeed_parser.parse_URL(parsers.URLGenerator.Indeed_URL(search_term))
            monster_parser.parse_URL(parsers.URLGenerator.Monster_URL(search_term))
            duunitori_parser.parse_URL(parsers.URLGenerator.Duunitori_URL(search_term))
            datab.store_job_ads(indeed_parser.get_job_ads().copy().update(
                        {'site': 'indeed', 'search_term' :search_term}))
            datab.store_job_ads(monster_parser.get_job_ads().copy().update(
                        {'site': 'monster', 'search_term' :search_term}))
            datab.store_job_ads(duunitori_parser.get_job_ads().copy().update(
                        {'site': 'duunitori', 'search_term' :search_term}))
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
                #add site and search term to job ads (modified parser instance!)
                [job_ad.update({'site': 'indeed', 'searchterm': search_term}) 
                for job_ad in indeed_parser.get_job_ads()]
                datab.store_job_ads(indeed_parser.get_job_ads())
                [job_ad.update({'site': 'monster', 'searchterm': search_term}) 
                for job_ad in monster_parser.get_job_ads()]
                datab.store_job_ads(monster_parser.get_job_ads())
                [job_ad.update({'site': 'duunitori', 'searchterm': search_term}) 
                for job_ad in duunitori_parser.get_job_ads()]
                datab.store_job_ads(duunitori_parser.get_job_ads())

    def output_results(self, date_start, date_end, output_name, output_type):
        """ 
        Outputs job ads from the database as an HTML or CSV file.
        
        Filters by date. If no dates are provided, all job ads in the database
        are included.
        
        Arguments:
        date_start  - datetime.date object corresponding to a date. If None, all 
                      entries since the start of the db are returned.
        date_end    - datetime.date object corresponding to a date. If None, all
                      job entries since date_start are returned.
        output_name - Name of the file to output results to. 
        output_type - Type of output file, "csv" or "html"
        """
        
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()
        print("Writing to %s from %s." % (output_name, self.db_name))
        if (output_type == "html"):
            datab.write_HTML_file(datab.get_ads(date_start, date_end), output_name)
        elif (output_type == "csv"):
            datab.write_CSV_file(datab.get_ads(date_start, date_end), output_name)

    def output_classified_results(self, date_start=datetime.datetime.strptime(
                                        "01-01-2015", "%d-%m-%Y"), 
                               date_end=datetime.date.today(), language="English", 
                               output_name="class.csv", output_type="csv"):
        """ 
        Outputs classified job ads from the database as an HTML or CSV file. 

        Filters by date. If no dates are provided, all job ads in the database
        are included.
        
        Arguments:
        date_start  - datetime.date object corresponding to a date. If None, all 
                      entries since the start of the db are returned.
        date_end    - datetime.date object corresponding to a date. If None, all
                      job entries since date_start are returned.
        language    - Language of classified jobs ads to use.
        output_name - Name of the file to output results to. 
        output_type - Type of output file, "csv" or "html"

        """
        
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()
        ads = datab.get_classified_ads(date_start, date_end, language, 1)
        print("Writing to %s from %s." % (output_name, self.db_name))
        if (output_type == "html"):
            datab.write_CSV_file(ads, output_name)
        elif (output_type == "csv"):
            datab.write_CSV_file(ads, output_name)

    def classify_data(self, date_start, date_end):
        """ 
        Starts GUI for classifying database entries between given dates.
        
        date_start - datetime.date object corresponding to a date. If None, all 
                     entries since the start of the db are returned.
        date_end   - datetime.date object corresponding to a date. If None, all
                     job entries since date_start are returned.
        """
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()

        gui = db_gui.JobSearchGUI(datab.get_ads(date_start, date_end))
        gui.mainloop()
        new_data = gui.dataStorage #dictionary with ids as keys
        new_data_dict = [dict(zip(gui.db_data_columns, new_data[id])) for id in new_data]
        
        datab.update_ads(new_data_dict)
