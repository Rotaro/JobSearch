import unittest
import datetime
import jobadcollector.classification as classification
import os

class JobAdClassificationTestCase(unittest.TestCase):
    """Class for testing classification of job ads. Rlibpath needs to be manually updated.
    """
    def setUp(self):
        self.Rlibpath = "C:/Users/SuperSSD/Documents/R/win-library/3.2" # SET RLIBPATH HERE
        self.job_ads_classified = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
            "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
            "description":"the absolutely best job synergy", "date" : datetime.date.today(), 
            "language" : "English", "relevant": 1, "recommendation" : None}, 
            {"site" : "best job ads site", "searchterm" : "greatest jobs",
            "id": "fesdaw", "title" : "Greater Job", "url" :"http://www.great.zyx",
            "description":"the absolutely bestest job integration", "date" : datetime.date.today(), 
            "language" : "English", "relevant": 1, "recommendation" : None}, 
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
            "description":"the absolutely worst job distance", "date" : datetime.date.today(), 
            "language" : "English", "relevant": 0, "recommendation" : None},
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "id": "dsfewf32", "title" : "Worse Job", "url" :"http://www.poor.zyx",
            "description":"the absolutely worstest job matrix", "date" : datetime.date.today(), 
            "language" : "English", "relevant": 0, "recommendation" : None}]
        self.sites = ["best job ads site", "worst job ads site"]
        self.search_terms = ["greatest jobs", "worst jobs"]
        self.class_columns = ["id", "site", "searchterm", "title", "description", "relevant"]
        self.JAC = classification.JobAdClassification(self.Rlibpath, self.search_terms,
                                                      self.sites, "English")
    def tearDown(self):
        if "tempmodel.dat" in os.listdir():
            os.remove("tempmodel.dat")

    def test_remove_diacritics(self):
        """Tests Swedish diacritics are properly removed from strings.
        """
        testing_string = [("åäöÅÄÖ", "aaoAAO"), 
                          ("iåiäiöiÅiÄiÖi", "iaiaioiAiAiOi")]
        for test_string in testing_string:
            self.assertEqual(self.JAC._remove_diacritics(test_string[0]), 
                            test_string[1])
        
    def test_create_dataframe(self):
        """Tests data frame is correctly created.
        """
        df = self.JAC._create_R_dataframe(
                self.job_ads_classified, self.class_columns)
        for col in self.class_columns:
            df_col = iter(df.rx2(col))
            for ad in self.job_ads_classified:
                self.assertEqual(df_col.__next__(), ad[col])

    def test_train_model(self):
        """Tests model is trained properly.
        """
        self.JAC.train_model(self.job_ads_classified)
        self.assertIsNotNone(self.JAC._RFmodel)

    def test_save_model(self):
        """Tests model is saved properly.
        """
        self.JAC.train_model(self.job_ads_classified)
        self.JAC.save_model("tempmodel.dat")
        self.assertIn("tempmodel.dat", os.listdir())

    def test_load_model(self):
        """Tests model is loaded properly.
        """
        self.JAC.train_model(self.job_ads_classified)
        self.JAC.save_model("tempmodel.dat")
        RFmodelcp = self.JAC._RFmodel
        self.JAC._RFmodel = None
        self.JAC.load_model("tempmodel.dat")
        self.assertIsNotNone(self.JAC._RFmodel)
        self.assertEqual(RFmodelcp.r_repr(), self.JAC._RFmodel.r_repr())
    
    def test_classify_ads(self):
        """Tests ads are classified properly using provided model.
        """
        self.JAC._splitratio = 1.0 #no testing set, i.e. recommendation must be
                                   #the same as the original classification
        self.JAC.train_model(self.job_ads_classified)
        class_ads = self.JAC.classify_ads(self.job_ads_classified)
        for class_ad in class_ads:
            self.assertIsNotNone(class_ad["recommendation"])
            for ad in self.job_ads_classified:
                if class_ad["id"] == ad["id"]:
                    self.assertEqual(class_ad["recommendation"], ad["relevant"])

    def test_determine_lang(self):
        """Tests language determination works properly.
        """
        lang_test = [("English title", """This is a long English sentence with a proper
                       structure. This sentence should easily be recognized as English.""",
                       "English"),
                     ("Suomenkielinen nimike", """Tämä on suomenkielinen lause, jolla
                      on kieliopillisesti järkevä rakenne. Ohjelman pitäisi helposti 
                      tunnistaa tämä lause suomenkieliseksi.""", "Finnish"),
                      ("Business Analyst töihin Vantaalle", """Tämä on suomenkielinen 
                      lause, jolla on kieliopillisesti järkevä rakenne. Ohjelman pitäisi 
                      helposti tunnistaa tämä lause suomenkieliseksi.""", "Finnish")]
        for test in lang_test:
            self.assertEqual(self.JAC._determine_lang(test[0],test[1]), test[2])



if __name__ == '__main__':
    unittest.main()
