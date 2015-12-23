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
    Results are stored in a sqlite database Job ads can be classified as relevant
    or not, which allows for a random forest model to be trained to predict the
    relevancy of new job ads. Entries in the database can be output as an HTML or
    CSV file.

    Arguments
    ----------
    search_terms : list 
        Search terms. Can be left empty if not needed.
    db_name : str
        Filename of local sqlite database. A new one will be created if file
    doesn't exist.
    Keyword Arguments
    ----------
    classification : bool 
        Classification support. rpy2 is only imported if set to True.
    Rlibpath : str
        Path to local R libraries. Only needed if classification is True.
    """

    def __init__(self, search_terms, db_name, classification=CLASSIFICATION, 
                 Rlibpath="C:/Users/SuperSSD/Documents/R/win-library/3.2"):
        if (not isinstance(search_terms, list) or db_name == ""):
            raise ValueError("Invalid arguments for JobAdCollector, search_terms \
                              should be a list or db_name missing.")
        self.search_terms = search_terms
        self.db_name = db_name
        self.classification = classification
        self.sites = ['indeed', 'duunitori', 'monster']
        self.Rlibpath = ""
        if classification == True:
            self.Rlibpath = Rlibpath

    def start_search(self, search_term=None):
        """Starts search for job advertisements using provided search term(s). 

        HTML requests are randomly delayed by 3 to 5 seconds. 

        Keyword Arguments
        ----------
        search_term : list
            Search term(s) to use. If None, instance variable search_terms,
        set during initialization, is used.
        """
        random.seed(1222)
        datab = db_controls.JobAdDB(self.db_name)
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

        All job ads between argument dates are included in the output.
  
        Arguments
        ----------
        date_start : :class:`datetime`
             Earliest date of job ads. If None, all job ads since the start 
             of the database are output.
        date_end : :class:`datetime`
            Latest date of job ads. If None, all job ads until end of database
            are output. If both date_start and date_end are None, all job ads 
            in the database are output.
        output_name : str
            Name of the file to output results to.
        output_type : str
            Type of output file, "csv" or "html" possible.
        """
        
        datab = db_controls.JobAdDB(self.db_name)
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

        All job ads between argument dates are included in the output.

        Keyword Arguments
        ----------
        date_start : :class:`datetime`
            Earliest date of job ads. Default is start of 2015.
        date_end : :class:`datetime`
            Latest date of job ads. Default is present day.
        language : str
            Language of classified jobs ads to output.
        output_name : str
            Name of the file to output results to. 
        output_type : str
            Type of output file, "csv" or "html"
        """
        
        datab = db_controls.JobAdDB(self.db_name)
        ads = datab.get_classified_ads(date_start, date_end, language, 1)
        print("Writing to %s from %s." % (output_name, self.db_name))
        if (output_type == "html"):
            datab.write_CSV_file(ads, output_name)
        elif (output_type == "csv"):
            datab.write_CSV_file(ads, output_name)

    def classify_data(self, date_start, date_end):
        """Starts GUI for classifying database entries between given dates.
        
        All job ads between argument dates are included for classification. 

        Arguments
        ----------
        date_start : :class:`datetime`
            Earliest date of job ads. If None, all job ads since the start of
            the database are included.
        date_end : :class:`datetime`
            Latest date of job ads. If None, all job ads after date_start are 
            included. If both date_start and date_end are None, all job ads in 
            the database are included.
        """
        datab = db_controls.JobAdDB(self.db_name)

        gui = db_gui.JobAdGUI(datab.get_ads(date_start, date_end))
        gui.mainloop()
        new_data = gui.ad_storage #dictionary with ids as keys
        new_data_dict = [dict(zip(gui.db_data_columns, new_data[id])) for id in new_data]
        
        datab.update_ads(new_data_dict)

    def train_model(self, language, date_start=datetime.datetime.strptime(
                                        "01-01-2015", "%d-%m-%Y"), 
                               date_end=datetime.date.today()):
        """Trains random forest model on classified job ads.

        All job ads between argument dates are included in the training. 

        Arguments
        ----------
        language : str
            Language of job ads to train on. Needed for proper stemming and 
            removal of stopwords.
        date_start : :class:`datetime`
            Earliest date of job ads. Default is start of 2015.
        date_end : :class:`datetime`
            Latest date of job ads. Default is present day. 

        Returns
        ----------
        JAC : :class:`JobAdClassification` 
            :class:`JobAdClassification`  instance with language, model,
            search_terms and sites set.
        """
        if (self.classification == False):
            raise EnvironmentError("Classification not enabled in JobAdCollector")
        
        JAC = classification.JobAdClassification(self.Rlibpath, self.search_terms, 
                                               self.sites, language)
        datab = db_controls.JobAdDB(self.db_name)
        RFmodel = JAC.train_model(
                  datab.get_classified_ads(date_start, date_end, language, 1), language)
        
        datab.disconnect_db()

        return JAC

    def det_lang_store_ads(self, date_start, date_end):
        """Attempts to determine language of job ads.
       
        The languages of all job ads between argument dates are determined 
        and stored in the database. Classification has to be enabled in
        JobAdCollector instance.

        Arguments
        ----------
        date_start : :class:`datetime`
            Earliest date of job ads. If None, all job ads since the start of
            the database are included.
        date_end : :class:`datetime`
            Latest date of job ads. If None, all job ads after date_start are 
            included. If both date_start and date_end are None, all job ads in 
            the database are included.
        """
        if (self.classification == False):
            raise EnvironmentError("Classification not enabled in JobAdCollector")
                                    
        datab = db_controls.JobAdDB(self.db_name)
        JAC = classification.JobAdClassification(self.Rlibpath, [], [], "")

        ads = datab.get_ads(date_start, date_end)
        lang_ads = JAC.det_lang_ads(ads)
        datab.update_ads_language(lang_ads)
        datab.disconnect_db()

    def recomm_store_ads(self, JAC, language, date_start, date_end):
        """Classifies ads using provided model.
       
        All job ads between argument dates of argument language are
        classified. The results are stored under the recommendation
        column in the database.

        Arguments
        ----------
        JAC : :class:`JobAdClassification`  
            Has to have model set.
        language : str
            Language of model and job ads to provide recommendations for.
        date_start : :class:`datetime`
            Earliest date of job ads. If None, all job ads since the start of
            the database are included.
        date_end : :class:`datetime`
            Latest date of job ads. If None, all job ads after date_start are 
            included. If both date_start and date_end are None, all job ads in 
            the database are included.
        """
                                      
        datab = db_controls.JobAdDB(self.db_name)

        ads = datab.get_ads(date_start, date_end, language)
        rec_ads = JAC.classify_ads(ads, language)
        datab.update_ads_recommendation(rec_ads)
        datab.disconnect_db()
        
    def save_model(self, JAC, filename):
        """Saves provided model to file.

        The file is saved using R's save function.

        Arguments
        ----------
        JAC : :class:`JobAdClassification` 
            Has to have model set.
        filename : str
            Name of file to save model in. Existing files are overwritten.
        """

        JAC.save_model(filename)

    def load_model(self, language, filename):
        """Loads model from file.

        Arguments
        ----------
        language : str
            Language of model and job ads to provide recommendations for.
        filename : str
            Name of file to load model from.
        Returns
        ----------
        :class:`JobAdClassification`  :
            :class:`JobAdClassification` instance with model set.    
        """
        JAC = classification.JobAdClassification(self.Rlibpath, 
                                               self.search_terms, self.sites, language)
        JAC.load_model(filename)

        return JAC


