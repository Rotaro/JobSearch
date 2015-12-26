import unittest
import datetime
import jobadcollector.job_ad as job_ad

class JobAdTestCase(unittest.TestCase):

    def setUp(self):
        self.ad = job_ad.JobAd()
    
    def test_initialization(self):
        """Test initialization is done properly.
        """
        for key in self.ad:
            if (key == "date"):
                self.assertIsInstance(self.ad[key], datetime.date)
            else:
                self.assertIsNone(self.ad[key])
        

    def test_add_non_ad_key(self):
        """Test keys which do not belong to job ads cannot be added.
        """
        self.assertRaises(KeyError, lambda: self.ad.__setitem__('what', 2))

    def test_add_ad_key(self):
        """Test keys belonging to job ads are properly added.
        """
        for key in job_ad.JobAd._cols:
            self.ad[key] = key
            self.assertEqual(key, self.ad[key])

    def test_remove_ad_key(self):
        """Test keys belonging to job ads are properly removed, i.e. set to None.
        """
        for key in job_ad.JobAd._cols:
            self.ad[key] = key
            del self.ad[key]
            self.assertIsNone(self.ad[key])

    def test_remove_non_ad_key(self):
        """Test removing keys not belonging to job ads returns KeyError.
        """
        self.assertRaises(KeyError, lambda: self.ad.__delitem__("what"))

    def test_columns_not_none(self):
        """Test that keys are checked for None properly.
        """
        self.assertFalse(self.ad.columns_not_none(self.ad._cols))
        self.assertTrue(self.ad.columns_not_none(["date"]))
        self.ad["title"] = "test"
        self.assertTrue(self.ad.columns_not_none(["title", "date"]))
        self.assertFalse(self.ad.columns_not_none(self.ad._cols))
        for col in self.ad._cols:
            self.ad[col] = col
        self.assertTrue(self.ad.columns_not_none(self.ad._cols))

    def test_create(self):
        """Test JobAd instances are properly created from dictionaries.
        """
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
        job_ads_complete = [{"site" : "best job ads site", "searchterm" : "greatest jobs",
            "id": "xyz412412se", "title" : "Great Job", "url" :"http://www.great.zyx",
            "description":"the absolutely best job", "date" : datetime.date.today(), 
            "language" : "English", "relevant": 1, "recommendation" : None}, 
            {"site" : "worst job ads site", "searchterm" : "worst jobs",
            "id": "dsfewf32", "title" : "Bad Job", "url" :"http://www.poor.zyx",
            "description":"the absolutely worst job", "date" : 
            datetime.datetime.strptime("01-01-2015", "%d-%m-%Y"), 
            "language" : "English", "relevant": 0, "recommendation" : None}]

        jobadslist = [job_ad.JobAd.create(ad) for ad in job_ads]
        for i in range(0, len(job_ads)):
            for key in job_ads[i]:
                self.assertEqual(jobadslist[i][key], job_ads[i][key])
        
        jobadslist = [job_ad.JobAd.create(ad) for ad in job_ads_garbage]
        for i in range(0, len(job_ads_garbage)):
            for key in job_ads_garbage[i]:
                if (key == "falsekey"):
                    self.assertRaises(KeyError, lambda: jobadslist[i][key])
                else:
                    self.assertEqual(jobadslist[i][key], job_ads_garbage[i][key])

        jobadslist = [job_ad.JobAd.create(ad) for ad in job_ads_complete]
        for i in range(0, len(job_ads_complete)):
            for key in job_ads_complete[i]:
                self.assertEqual(jobadslist[i][key], job_ads_complete[i][key])
        



if __name__ == '__main__':
    unittest.main()
