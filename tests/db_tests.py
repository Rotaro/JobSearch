import sqlite3
import datetime
import sys
import unittest


import jobadcollector.db_controls as db_controls


class JobsAdDBTestCase(unittest.TestCase):
    """Various tests for JobAdsDB class.
    """

    def setUp(self):
        self.filename = ":memory:"
        self.db = db_controls.JobAdsDB(self.filename)
        self.db_columns = [("site", "varchar(255)", 0), 
                         ("searchterm", "varchar(255)", 0), 
                         ("id", "varchar(255)", 1), 
                         ("title", "varchar(255)", 0),
                         ("url", "varchar(1000)", 0),
                         ("description", "varchar(1000)", 0),
                         ("date", "date", 0),
                         ("language", "varchar(100)", 0),
                         ("relevant", "integer", 0),
                         ("recommendation", "integer", 0)]
        self.job_ads = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
            "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
            "description":"the absolutely best job"}, 
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
            "description":"the absolutely worst job"}]
        self.job_ads_garbage = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
            "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
            "description":"the absolutely best job", "falsekey" : "garbage"}, 
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
            "description":"the absolutely worst job", "falsekey" : "garbage"}]
        self.job_ads_classified = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
            "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
            "description":"the absolutely best job", "date" : datetime.date.today(), 
            "language" : "English", "relevant": 1, "recommendation" : None}, 
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
            "description":"the absolutely worst job", "date" : datetime.date.today(), 
            "language" : "English", "relevant": 0, "recommendation" : None}]
     

    def test_class_creation(self):
        """Test class is created and initialized properly.
        """
        self.assertIsInstance(self.db, db_controls.JobAdsDB)
        self.assertEqual(self.db.db_filename, self.filename)


    def test_connect_db(self):
        """Test database connection is established and JobEntries table created properly.
        """
        self.db.connect_db()
        self.assertIsInstance(self.db.conn, db_controls.sqlite3.Connection)
        c = self.db.conn.cursor()
        table = c.execute("""SELECT * FROM sqlite_master 
                               WHERE type = 'table' and name = 'JobEntries'""")
        self.assertEqual(len(table.fetchall()), 1)
        columns = c.execute("""PRAGMA table_info(JobEntries)""")
        columns = [(column[1], column[2], column[5]) for column in columns]
        self.assertEqual(len(columns), len(self.db_columns))
        for i in range(0, len(columns)):
            self.assertEqual(len(columns[i]), len(self.db_columns[i]))
            for j in range(0, len(columns[i])):
                self.assertEqual(columns[i][j], self.db_columns[i][j])
        
    def test_disconnect_db(self):
        """Test database connection is properly disconnected.
        """
        self.db.connect_db()
        self.db.disconnect_db()
        self.assertRaises(sqlite3.ProgrammingError, self.db.conn.cursor)

    #def store_ads_test(self):
    #    """Tests store_ads().
    #    """
    #    #store entries
    #    self.db.store_ads(self.job_ads)
    #    #check entries exist and are stored correctly
    #    ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
    #                                  datetime.date.today())
    #    i = 0
    #    for ret_job_ad in ret_job_ads:
    #        for job_ad in self.job_ads:
    #            if ret_job_ad["id"] == job_ad["id"]:
    #                i = i + 1
    #                for key in job_ad:
    #                    if ret_job_ad[key] != job_ad[key]:
    #                        raise ValueError("Wrong information in database (%s, %s)." %
    #                                         (job_ad[key], ret_job_ad[key]))
    #    if i < len(self.job_ads):
    #        raise ValueError("Did not find all job ads in database.")
    #    if i > len(self.job_ads):
    #        raise ValueError("Found too many job ads in database.")

    #    #try storing again
    #    self.db.store_ads(self.job_ads)
    #    #check no duplicate entries
    #    ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
    #                                  datetime.date.today())
    #    i = 0
    #    for ret_job_ad in ret_job_ads:
    #        for job_ad in self.job_ads:
    #            if ret_job_ad["id"] == job_ad["id"]:
    #                i = i + 1
    #                for key in job_ad:
    #                    if ret_job_ad[key] != job_ad[key]:
    #                        raise ValueError("Wrong information in database (%s, %s)." %
    #                                         (job_ad[key], ret_job_ad[key]))
    #    if i < len(self.job_ads):
    #        raise ValueError("Did not find all job ads in database.")
    #    if i > len(self.job_ads):
    #        raise ValueError("Found too many job ads in database.")
    #    #reset db (works since db is only in memory)
    #    self.db.conn.close()
    #    self.connect_db_test()
    #    #test storing entries with garbage keys
    #    #store entries
    #    self.db.store_ads(self.job_ads_garbage)
    #    #check entries exist and are stored correctly
    #    ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
    #                                  datetime.date.today())
    #    i = 0
    #    for ret_job_ad in ret_job_ads:
    #        for job_ad in self.job_ads:
    #            if ret_job_ad["id"] == job_ad["id"]:
    #                i = i + 1
    #                for key in ret_job_ad:
    #                    if key == "falsekey":
    #                        raise ValueError("Garbage information in database (%s, %s)." %
    #                                         (job_ad[key], ret_job_ad[key]))
    #                    if key not in ["date", "language", "relevant", "recommendation", ] and \
    #                                  ret_job_ad[key] != job_ad[key]:
    #                        raise ValueError("Wrong information in database (%s, %s)." %
    #                                         (job_ad[key], ret_job_ad[key]))
    #    if i < len(self.job_ads):
    #        raise ValueError("Did not find all job ads in database.")
    #    if i > len(self.job_ads):
    #        raise ValueError("Found too many job ads in database.")
    #    self.db.conn.close()

    #def update_ads_test(self):
    #    """Tests update_ads()
    #    """
    #    #store unclassified entries
    #    self.connect_db_test()
    #    self.db.store_ads(self.job_ads)
    #    #update entries
    #    self.db.update_ads(self.job_ads_classified)
    #    #confirm entries have been updated
    #    ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
    #                                  datetime.date.today())
    #    i = 0
    #    for ret_job_ad in ret_job_ads:
    #        for job_ad in self.job_ads_classified:
    #            if ret_job_ad["id"] == job_ad["id"]:
    #                i = i + 1
    #                for key in job_ad:
    #                    if ret_job_ad[key] != job_ad[key] and str(ret_job_ad[key]) != str(job_ad[key]):
    #                        raise ValueError("Wrong information in database (%s, %s)." %
    #                                         (job_ad[key], ret_job_ad[key]))
    #    if i < len(self.job_ads_classified):
    #        raise ValueError("Did not find all job ads in database.")
    #    if i > len(self.job_ads_classified):
    #        raise ValueError("Found too many job ads in database.")

    #def get_classified_ads_test(self):
    #    #store unclassified ads
    #    self.connect_db_test()
    #    self.db.store_ads(self.job_ads)
    #    #check no classified ads are returned
    #    ret_job_ads = self.db.get_classified_ads(all_columns=0)
    #    if len(ret_job_ads) > 0:
    #        raise ValueError("Classified ads returned even though none have been entered!")
    #    ret_job_ads = self.db.get_classified_ads(all_columns=1)
    #    if len(ret_job_ads) > 0:
    #        raise ValueError("Classified ads returned even though none have been entered!")
    #    #update entries
    #    self.db.update_ads(self.job_ads_classified)
    #    #check classified entries with all columns
    #    ret_job_ads = self.db.get_classified_ads(all_columns=1)
    #    i = 0
    #    for ret_job_ad in ret_job_ads:
    #        for job_ad in self.job_ads_classified:
    #            if ret_job_ad["id"] == job_ad["id"]:
    #                i = i + 1
    #                for key in job_ad:
    #                    if ret_job_ad[key] != job_ad[key] and str(ret_job_ad[key]) != str(job_ad[key]):
    #                        raise ValueError("Wrong information in database (%s, %s)." %
    #                                         (job_ad[key], ret_job_ad[key]))
    #    if i != len(self.job_ads_classified):
    #        raise ValueError("Wrong amount of classified job ads in database!")
    #    #check classified entries with only classification columns
    #    ret_job_ads = self.db.get_classified_ads(all_columns=1)
    #    i = 0
    #    for ret_job_ad in ret_job_ads:
    #        for job_ad in self.job_ads_classified:
    #            if ret_job_ad["id"] == job_ad["id"]:
    #                i = i + 1
    #                for key in ["searchterm" , "title", "description", "language", "relevant"]:
    #                    if ret_job_ad[key] != job_ad[key] and str(ret_job_ad[key]) != str(job_ad[key]):
    #                        raise ValueError("Wrong information in database (%s, %s)." %
    #                                         (job_ad[key], ret_job_ad[key]))
    #    if i != len(self.job_ads_classified):
    #        raise ValueError("Wrong amount of classified job ads in database!")

if __name__ == "__main__":
    unittest.main()