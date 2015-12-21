import datetime
import random
import time
from . import parsers, db_controls, db_gui

try: 
    CLASSIFICATION = True
    from . import classification
except ImportError:
    CLASSIFICATION = False
    print("""Classification module import failed. Classification functions are disabled.""")

class JobAdCollector:
    """Class for operating job ad collections.
    Searches for job ads from Indeed.fi, Duunitori.fi and Monster.fi. 
    Results are stored in a sqlite database named during initiation. Job ads
    can be classified as relevant or not, which allows for a random forest model 
    to be trained to predict the relevancy of new job ads. Entries in the database 
    can be output as an HTML or CSV file.

    Arguments:
    search_terms   - List of search terms to use. Can be left empty.
    db_name        - Filename of local sqlite database. A new one will be created 
                     if file doesn't exist.
    classification - Boolean, allows classification of job ads. rpy2 is only imported 
                     if set to True (to allow for use of the program without R and 
                     rpy2 installed).
    Rlibpath       - ONLY if classification is True. Path to local R libraries.
    """
    db_name = ""
    search_terms = []
    sites = ['indeed', 'duunitori', 'monster']
    Rlibpath = ""

    def __init__(self, search_terms, db_name, classification=CLASSIFICATION, 
                 Rlibpath="C:/Users/SuperSSD/Documents/R/win-library/3.2"):
        if (not isinstance(search_terms, list) or db_name == ""):
            raise ValueError("Invalid arguments for JobAdCollector, search_terms \
                              should be a list or db_name missing.")
        self.search_terms = search_terms
        self.db_name = db_name
        self.classification = classification
        if classification == True:
            self.Rlibpath = Rlibpath

    def start_search(self, search_term=None):
        """Starts search for job advertisements using provided search term(s). 

        HTML requests are randomly delayed by 3 to 5 seconds. 

        search_term - Search term to use. If None, instance variable search_terms,
                      set during initialization, is used.
        """
        random.seed(1222)
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()
        if (search_term != None):
            searchables = [search_term]
        else:
            searchables = self.search_terms
        if isinstance(searchables, list):
            for search_term in searchables:
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
                #add site and search term to job ads (modifies parser instance!)
                for job_ad in indeed_parser.get_job_ads():
                    job_ad.update({'site': 'indeed', 'searchterm': search_term}) 
                datab.store_ads(indeed_parser.get_job_ads())
                for job_ad in monster_parser.get_job_ads():
                    job_ad.update({'site': 'monster', 'searchterm': search_term}) 
                datab.store_ads(monster_parser.get_job_ads())
                for job_ad in duunitori_parser.get_job_ads():
                    job_ad.update({'site': 'duunitori', 'searchterm': search_term}) 
                datab.store_ads(duunitori_parser.get_job_ads())

    def output_results(self, date_start, date_end, output_name, output_type):
        """Outputs job ads from database as an HTML or CSV file.
  
        Arguments:
        date_start  - Datetime instance. If None, all job ads since the
                      start of the database are output.
        date_end    - Datetime instance. If None, all job ads until
                      end of database are output.
        If both date_start and date_end are None, all job ads in the 
        database are output.
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

    def output_classified_results(self, 
                                  date_start=datetime.datetime.strptime(
                                        "01-01-2015", "%d-%m-%Y"), 
                               date_end=datetime.date.today(), language="English", 
                               output_name="class.csv", output_type="csv"):
        """Outputs classified job ads from the database as an HTML or CSV file. 

        Arguments:
        date_start  - Datetime instance of earliest date of job ads. 
        date_end    - Datetime instance of latest date of job ads. 
        language    - Language of classified jobs ads to output.
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
        """Starts GUI for classifying database entries between given dates.
        
        date_start  - Datetime instance. If None, all job ads since the
                      start of the databbase are output.
        date_end    - Datetime instance. If None, all job ads after 
                      date_start are output. 
        If both date_start and date_end are None, all job ads in the 
        database are output.
        """
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()

        gui = db_gui.JobAdGUI(datab.get_ads(date_start, date_end))
        gui.mainloop()
        new_data = gui.ad_storage #dictionary with ids as keys
        new_data_dict = [dict(zip(gui.db_data_columns, new_data[id])) for id in new_data]
        
        datab.update_ads(new_data_dict)

    def train_model(self, language, date_start=datetime.datetime.strptime(
                                        "01-01-2015", "%d-%m-%Y"), 
                               date_end=datetime.date.today()):
        """Trains random forest model on classified job ads.

        All job ads between provided dates are included in the training. 

        Returns RRFClassification instance with model, search_terms and sites set.
        Model can be found under RFmodel.

        Arguments:
        language    - Language of job ads to train on. Needed for proper stemming and
                      removal of stopwords.
        date_start  - Datetime instance. Default is start of 2015 (i.e. before db creation).
        date_end    - Datetime instance. Default is today.
        If both date_start and date_end are None, all job ads in the database
        are included.
        """
        if (self.classification == False):
            raise EnvironmentError("Classification not enabled in JobAdCollector")
        
        RFC = classification.RRFClassification(self.Rlibpath, self.search_terms, 
                                               self.sites, language)
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()
        RFmodel = RFC.train_model(
                  datab.get_classified_ads(date_start, date_end, language, 1), language)
        
        datab.disconnect_db()

        return RFC

    def det_lang_store_ads(self, date_start, date_end):
        """Attempts to determine language of job ads and stores results
        in database. Needs classification to be enabled.

        Arguments:
        date_start  - Datetime instance. If None, all job ads since the
                      start of the database are included.
        date_end    - Datetime instance. If None, all job ads until
                      end of database are included.
        If both date_start and date_end are None, all job ads in the database
        are included.
        """
        if (self.classification == False):
            raise EnvironmentError("Classification not enabled in JobAdCollector")
                                    
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()
        RFC = classification.RRFClassification(self.Rlibpath, [], [], "")

        ads = datab.get_ads(date_start, date_end)
        lang_ads = RFC.det_lang_ads(ads)
        datab.update_ads_language(lang_ads)
        datab.disconnect_db()

    def recomm_store_ads(self, RFC, language, date_start, date_end):
        """Classifies ads using provided model and stores the recommendations
        in the database.

        Arguments:
        RFC         - RRFClassification instance. Use train_model or load_model
                      for initialization.
        language    - Language of ads.
        date_start  - Datetime instance. If None, all job ads since the
                      start of the database are included.
        date_end    - Datetime instance. If None, all job ads until
                      end of database are included.
        If both date_start and date_end are None, all job ads in the database
        are included.
        """
                                      
        datab = db_controls.JobAdsDB(self.db_name)
        datab.connect_db()

        ads = datab.get_ads(date_start, date_end, language)
        rec_ads = RFC.classify_ads(ads, language)
        datab.update_ads_recommendation(rec_ads)
        datab.disconnect_db()
        
    def save_model(self, RFC, filename):
        """Saves provided model to file.

        The file is saved using R's save function.

        Arguments:
        RFC      - RRFClassification instance. Use train_model or load_model
                   for initialization. 
        filename - Name of file to save model in. Existing files are overwritten.
        """

        RFC.save_model(filename)

    def load_model(self, language, filename):
        """Loads model from file.

        The file is saved using R's save function.

        Arguments:
        RFC      - RRFClassification instance. Use train_model or load_model
                   for initialization. 
        filename - Name of file to save model in. Existing files are overwritten.
        """
        RFC = classification.RRFClassification(self.Rlibpath, 
                                               self.search_terms, self.sites, language)
        RFC.load_model(filename)

        return RFC


