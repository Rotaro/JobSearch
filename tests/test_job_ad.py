import unittest
import jobadcollector.job_ad as job_ad

class JobAdTestCase(unittest.TestCase):

    def setUp(self):
        self.ad = job_ad.JobAd()
    
    def test_initialization(self):
        """Test initialization is done properly.
        """
        for key in self.ad:
            self.assertIsNone(self.ad[key])

    def test_add_non_ad_key(self):
        """Test keys which do not belong to job ads cannot be added.
        """
        self.assertRaises(KeyError, lambda: self.ad.__setitem__('what', 2))

    def test_add_ad_key(self):
        """Tests keys belonging to job ads are properly added.
        """
        for key in job_ad.JobAd._cols:
            self.ad[key] = key
            self.assertEqual(key, self.ad[key])

    def test_remove_ad_key(self):
        """Tests keys belonging to job ads are properly removed, i.e. set to None.
        """
        for key in job_ad.JobAd._cols:
            self.ad[key] = key
            del self.ad[key]
            self.assertIsNone(self.ad[key])

    def test_remove_non_ad_key(self):
        """Tests removing keys not belonging to job ads returns KeyError.
        """
        self.assertRaises(KeyError, lambda: self.ad.__delitem__("what"))

if __name__ == '__main__':
    unittest.main()
