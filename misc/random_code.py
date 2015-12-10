import sqlite3
import urllib
import re
import datetime

import db_controls

class DBTests:
    """Various tests for the database class JobAdsDB
    """
    
    filename = ":memory:"
    db = None
    job_ads = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
          "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
          "description":"the absolutely best job"}, 
               {"site" : "worst job ads site", "searchterm" : "worst jobs",
          "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
          "description":"the absolutely worst job"}]
    job_ads_garbage = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
          "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
          "description":"the absolutely best job", "falsekey" : "garbage"}, 
               {"site" : "worst job ads site", "searchterm" : "worst jobs",
          "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
          "description":"the absolutely worst job", "falsekey" : "garbage"}]
    job_ads_classified = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
          "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
          "description":"the absolutely best job", "date" : datetime.date.today(), 
          "language" : "English", "relevant": 1, "recommendation" : None}, 
               {"site" : "worst job ads site", "searchterm" : "worst jobs",
          "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
          "description":"the absolutely worst job", "date" : datetime.date.today(), 
          "language" : "English", "relevant": 0, "recommendation" : None}]
    def create_db_class_test(self):
        """Test class is created properly
        """
        self.db = db_controls.JobAdsDB(self.filename)
        if not isinstance(self.db, db_controls.JobAdsDB):
            raise ValueError("Failed to create JobAdsDB instance.")

    def connect_db_test(self):
        """Test database connection is properly established.
        """
        self.db.connect_db()
        if not isinstance(self.db.conn, db_controls.sqlite3.Connection):
            raise ValueError("Failed to connect to database %s." % self.filename)

    def store_job_ads_test(self):
        """Tests store_job_ads().
        """
        #store entries
        self.db.store_job_ads(self.job_ads)
        #check entries exist and are stored correctly
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())
        i = 0
        for ret_job_ad in ret_job_ads:
            for job_ad in self.job_ads:
                if ret_job_ad["id"] == job_ad["id"]:
                    i = i + 1
                    for key in job_ad:
                        if ret_job_ad[key] != job_ad[key]:
                            raise ValueError("Wrong information in database (%s, %s)." %
                                             (job_ad[key], ret_job_ad[key]))
        if i < len(self.job_ads):
            raise ValueError("Did not find all job ads in database.")
        if i > len(self.job_ads):
            raise ValueError("Found too many job ads in database.")

        #try storing again
        self.db.store_job_ads(self.job_ads)
        #check no duplicate entries
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())
        i = 0
        for ret_job_ad in ret_job_ads:
            for job_ad in self.job_ads:
                if ret_job_ad["id"] == job_ad["id"]:
                    i = i + 1
                    for key in job_ad:
                        if ret_job_ad[key] != job_ad[key]:
                            raise ValueError("Wrong information in database (%s, %s)." %
                                             (job_ad[key], ret_job_ad[key]))
        if i < len(self.job_ads):
            raise ValueError("Did not find all job ads in database.")
        if i > len(self.job_ads):
            raise ValueError("Found too many job ads in database.")
        #reset db (works since db is only in memory)
        self.db.conn.close()
        self.connect_db_test()
        #test storing entries with garbage keys
        #store entries
        self.db.store_job_ads(self.job_ads_garbage)
        #check entries exist and are stored correctly
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())
        i = 0
        for ret_job_ad in ret_job_ads:
            for job_ad in self.job_ads:
                if ret_job_ad["id"] == job_ad["id"]:
                    i = i + 1
                    for key in ret_job_ad:
                        if key == "falsekey":
                            raise ValueError("Garbage information in database (%s, %s)." %
                                             (job_ad[key], ret_job_ad[key]))
                        if key not in ["date", "language", "relevant", "recommendation", ] and \
                                      ret_job_ad[key] != job_ad[key]:
                            raise ValueError("Wrong information in database (%s, %s)." %
                                             (job_ad[key], ret_job_ad[key]))
        if i < len(self.job_ads):
            raise ValueError("Did not find all job ads in database.")
        if i > len(self.job_ads):
            raise ValueError("Found too many job ads in database.")
        self.db.conn.close()

    def update_ads_test(self):
        """Tests update_ads()
        """
        #store unclassified entries
        self.connect_db_test()
        self.db.store_job_ads(self.job_ads)
        #update entries
        self.db.update_ads(self.job_ads_classified)
        #confirm entries have been updated
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())
        i = 0
        for ret_job_ad in ret_job_ads:
            for job_ad in self.job_ads_classified:
                if ret_job_ad["id"] == job_ad["id"]:
                    i = i + 1
                    for key in job_ad:
                        if ret_job_ad[key] != job_ad[key] and str(ret_job_ad[key]) != str(job_ad[key]):
                            raise ValueError("Wrong information in database (%s, %s)." %
                                             (job_ad[key], ret_job_ad[key]))
        if i < len(self.job_ads_classified):
            raise ValueError("Did not find all job ads in database.")
        if i > len(self.job_ads_classified):
            raise ValueError("Found too many job ads in database.")

    def get_classified_ads_test(self):
        #store unclassified ads
        self.connect_db_test()
        self.db.store_job_ads(self.job_ads)
        #check no classified ads are returned
        ret_job_ads = self.db.get_classified_ads(all_columns=0)
        if len(ret_job_ads) > 0:
            raise ValueError("Classified ads returned even though none have been entered!")
        ret_job_ads = self.db.get_classified_ads(all_columns=1)
        if len(ret_job_ads) > 0:
            raise ValueError("Classified ads returned even though none have been entered!")
        #update entries
        self.db.update_ads(self.job_ads_classified)
        #check classified entries with all columns
        ret_job_ads = self.db.get_classified_ads(all_columns=1)
        i = 0
        for ret_job_ad in ret_job_ads:
            for job_ad in self.job_ads_classified:
                if ret_job_ad["id"] == job_ad["id"]:
                    i = i + 1
                    for key in job_ad:
                        if ret_job_ad[key] != job_ad[key] and str(ret_job_ad[key]) != str(job_ad[key]):
                            raise ValueError("Wrong information in database (%s, %s)." %
                                             (job_ad[key], ret_job_ad[key]))
        if i != len(self.job_ads_classified):
            raise ValueError("Wrong amount of classified job ads in database!")
        #check classified entries with only classification columns
        ret_job_ads = self.db.get_classified_ads(all_columns=1)
        i = 0
        for ret_job_ad in ret_job_ads:
            for job_ad in self.job_ads_classified:
                if ret_job_ad["id"] == job_ad["id"]:
                    i = i + 1
                    for key in ["searchterm" , "title", "description", "language", "relevant"]:
                        if ret_job_ad[key] != job_ad[key] and str(ret_job_ad[key]) != str(job_ad[key]):
                            raise ValueError("Wrong information in database (%s, %s)." %
                                             (job_ad[key], ret_job_ad[key]))
        if i != len(self.job_ads_classified):
            raise ValueError("Wrong amount of classified job ads in database!")

if __name__ == "__main__":
    test = DBTests()
    test.create_db_class_test()
    test.connect_db_test()
    test.store_job_ads_test()
    test.update_ads_test()
    test.get_classified_ads_test()