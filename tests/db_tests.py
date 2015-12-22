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
        self.db.connect_db()
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
        self.job_ads_stored = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
            "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
            "description":"the absolutely best job", "date" : datetime.date.today(), 
            "language" : None, "relevant": None, "recommendation" : None},
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
            "description":"the absolutely worst job", "date" : datetime.date.today(), 
            "language" : None, "relevant": None, "recommendation" : None}]
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
        self.job_ads_classified_less = [{"site" : "best job ads site", 
            "searchterm" : "greatest jobs", "title" : "Great Job", 
            "description":"the absolutely best job", "language" : "English", "relevant": 1}, 
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "title" : "Bad Job", "description":"the absolutely worst job", 
            "language" : "English", "relevant": 0}]


    def tearDown(self):
        self.db.disconnect_db()

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
        self.assertCountEqual(columns, self.db_columns)

    def test_disconnect_db(self):
        """Test database connection is properly disconnected.
        """
        self.db.connect_db()
        self.db.disconnect_db()
        self.assertRaises(sqlite3.ProgrammingError, self.db.conn.cursor)

    def test_store_get_ads(self):
        """Test ads are stored and retrieved correctly.
        """
        #store entries
        self.db.store_ads(self.job_ads)
        #retrieve stored ads
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())
        #check job ads remain intact
        self.assertEqual(len(ret_job_ads), len(self.job_ads_stored))
        for ret_ad in ret_job_ads:
            for sto_ad in self.job_ads_stored:
                if (sto_ad["id"] == ret_ad["id"]):
                    self.assertCountEqual(ret_ad, sto_ad)
        #try storing again
        self.db.store_ads(self.job_ads)
        #check no duplicate entries
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())
        self.assertEqual(len(ret_job_ads), len(self.job_ads_stored))
        for ret_ad in ret_job_ads:
            for sto_ad in self.job_ads_stored:
                if (sto_ad["id"] == ret_ad["id"]):
                    self.assertCountEqual(ret_ad, sto_ad)
        #reset db (works since db is in memory)
        self.db.disconnect_db()
        self.db.connect_db()
        #test storing entries with garbage keys
        self.db.store_ads(self.job_ads_garbage)
        #check entries exist and are stored correctly
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())
        self.assertEqual(len(ret_job_ads), len(self.job_ads_stored))
        for ret_ad in ret_job_ads:
            for sto_ad in self.job_ads_stored:
                if (sto_ad["id"] == ret_ad["id"]):
                    self.assertCountEqual(ret_ad, sto_ad)

    def test_update_ads(self):
        """Test ads are updated correctly.
        """
        #store unclassified entries
        self.db.store_ads(self.job_ads)
        #update entries
        self.db.update_ads(self.job_ads_classified)
        #confirm entries have been updated
        ret_job_ads = self.db.get_ads(datetime.date.today()-datetime.timedelta(1),
                                      datetime.date.today())

        self.assertEqual(len(ret_job_ads), len(self.job_ads_classified))
        for ret_ad in ret_job_ads:
            for class_ad in self.job_ads_classified:
                if (class_ad["id"] == ret_ad["id"]):
                    self.assertCountEqual(ret_ad, class_ad)

    def test_get_classified_ads(self):
        """Test classified ads are retrieved correctly.
        """
        #store unclassified ads
        self.db.store_ads(self.job_ads)
        #check no classified ads are returned
        ret_job_ads = self.db.get_classified_ads(all_columns=0)
        self.assertEqual(len(ret_job_ads), 0)
        ret_job_ads = self.db.get_classified_ads(all_columns=1)
        self.assertEqual(len(ret_job_ads), 0)
        #update entries
        self.db.update_ads(self.job_ads_classified)
        #check classified entries with all columns
        ret_job_ads = self.db.get_classified_ads(all_columns=1)
        self.assertEqual(len(ret_job_ads), len(self.job_ads_classified))
        for ret_ad in ret_job_ads:
            for class_ad in self.job_ads_classified:
                if (class_ad["id"] == ret_ad["id"]):
                    self.assertCountEqual(ret_ad, class_ad)

        #check classified entries with only classification columns
        ret_job_ads = self.db.get_classified_ads(all_columns=0)
        self.assertEqual(len(ret_job_ads), len(self.job_ads_classified_less))
        for ret_ad in ret_job_ads:
            #no id when all columns aren't present, have to rely on 
            #data being in the same order as when entered
            for class_ad in self.job_ads_classified_less:
                    self.assertCountEqual(ret_ad, class_ad)

    def test_update_ads_recommendation(self):
        """Tests recommendation column is properly updated.
        """
        #store ads without recommendation
        self.db.store_ads(self.job_ads)
        #update recommendations
        id_recomm = [{"id": ad["id"], "recommendation": 1} 
                     for ad in self.job_ads_classified]
        self.db.update_ads_recommendation(id_recomm)
        ret_id_recomm = [{"id": ad["id"], 
                          "recommendation": ad["recommendation"]} 
                         for ad in self.db.get_ads(
                             datetime.date.today()-datetime.timedelta(1),
                             datetime.date.today())]
        self.assertCountEqual(id_recomm, ret_id_recomm)

    def test_update_ads_language(self):
        """Tests language column is properly updated.
        """
        #store ads without recommendation
        self.db.store_ads(self.job_ads)
        #update recommendations
        id_lang = [{"id": ad["id"], "language": "Russian"} 
                     for ad in self.job_ads_classified]
        self.db.update_ads_language(id_lang)
        ret_id_lang = [{"id": ad["id"], "language": ad["language"]} 
                         for ad in self.db.get_ads(
                             datetime.date.today()-datetime.timedelta(1),
                             datetime.date.today())]
        self.assertCountEqual(id_lang, ret_id_lang)
            

if __name__ == "__main__":
    unittest.main()

