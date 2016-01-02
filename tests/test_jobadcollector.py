import unittest
import os
import sqlite3
import datetime

import jobadcollector



class JobAdCollectorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.search_terms = ["analyst", "programmer"]
        cls.db_name = "test_db.db"
        cls.output_name = "test_output.dat"
        cls.sites = jobadcollector.parsers.JobAdParser.parsers_impl
        cls.coll = jobadcollector.JobAdCollector(cls.search_terms, cls.db_name)   
        cls.coll.start_search()
        cls.JAC = None

    @classmethod
    def tearDownClass(cls):
        if cls.db_name in os.listdir():
            os.remove(cls.db_name)
        if cls.output_name in os.listdir():
            os.remove(cls.output_name)
    
    def _test_initialization(self):
        """Test JobAdCollector is initialized correctly.
        """
        self.assertEqual(self.coll._search_terms, self.search_terms)
        self.assertEqual(self.coll._db_name, self.db_name)
        self.assertEqual(self.coll._classification, True)


    def test_complete_suite(self):
        """Correct order of tests to avoid having to reset database constantly.
        """
        self._test_initialization()
        self._test_start_search()
        self._test_output_results()
        self._test_det_lang_store_ads()
        self._test_train_model()
        self._test_save_model()
        self._test_load_model()

    def _test_start_search(self):
        """Test search results are stored in database.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        db_entries = c.execute("SELECT * FROM JobEntries").fetchall()
        self.assertTrue(len(db_entries) > 0)
        conn.close()
        for db_entry in db_entries:
            self.assertTrue(db_entry[0] != None and db_entry[0] in self.sites )
            self.assertTrue(db_entry[1] != None and db_entry[1] in self.search_terms)
            self.assertTrue(db_entry[2] != None and db_entry[2] != "")
            self.assertTrue(db_entry[3] != None and db_entry[3] != "")
            self.assertTrue(db_entry[4] != None and db_entry[4] != "")
            self.assertTrue(db_entry[5] != None and db_entry[5] != "")
            self.assertTrue(db_entry[6] != None)

    def _test_output_results(self):
        """Check files are output. No content checks (could be done under database tests.
        """
        self.coll.output_results(datetime.date.today()-datetime.timedelta(1),
                                 datetime.date.today(), self.output_name, "html")
        self.assertTrue(self.output_name in os.listdir())
        os.remove(self.output_name)
        self.coll.output_results(datetime.date.today()-datetime.timedelta(1),
                                 datetime.date.today(), self.output_name, "csv")
        self.assertTrue(self.output_name in os.listdir())
        os.remove(self.output_name)
    
    def _test_det_lang_store_ads(self):
        """Test languages are determined on job ads.
        """
        self.coll.det_lang_store_ads(datetime.date.today()-datetime.timedelta(1),
                                datetime.date.today())
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        db_entries = c.execute("SELECT language FROM JobEntries").fetchall()
        self.assertTrue(len(db_entries) > 0)
        conn.close()
        for db_entry in db_entries:
            self.assertTrue(db_entry[0] in ["English", "Finnish"])

    def _test_train_model(self):
        """Test model is trained on classified data.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        db_entries = c.execute("UPDATE JobEntries SET relevant = 0")
        db_entries = c.execute("UPDATE JobEntries SET relevant = 1 WHERE site = 'indeed'")
        db_entries = c.execute("UPDATE JobEntries SET language = 'English'")
        conn.commit()
        conn.close()
        self.JAC = self.coll.train_model("English")
        self.assertIsInstance(self.JAC, jobadcollector.classification.JobAdClassification)
        
    def _test_save_model(self):
        """Test model file is created.
        """
        self.coll.save_model(self.JAC, self.output_name)
        self.assertTrue(self.output_name in os.listdir())
    
    def _test_load_model(self):
        """Test model file is loaded.
        """
        self.JAC = self.coll.load_model("English", self.output_name)
        self.assertIsInstance(self.JAC, jobadcollector.classification.JobAdClassification)

if __name__ == '__main__':
    unittest.main()
