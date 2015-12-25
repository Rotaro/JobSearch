import unittest
from jobadcollector import parsers
import urllib.parse

class ParsersTestCase(unittest.TestCase):
    """Class for testing parsers.
    """

    def setUp(self):
        self.dtp = parsers.DuunitoriParser()
        self.mp = parsers.MonsterParser()
        self.ip = parsers.IndeedParser()
        self.search_terms = [("analyst", "analyst"), 
                             ("osa-aikainen", "osa-aikainen"),
                             ("työhyvinvointi", "ty%C3%B6hyvinvointi")]
        self.job_ad_keys = ["id", "title", "url", "description"]

    def test_Duunitori_URLGenerator(self):
        """Test proper Duunitori URL is generated.
        """
        for search_term in self.search_terms:
            url = self.dtp._generate_URL(search_term[0])
            self.assertEqual(url, "http://duunitori.fi/tyopaikat/?haku="+ search_term[1] + "&alue=")
           
    def test_Monster_URLGenerator(self):
        """Test proper Monster URL is generated.
        """
        for search_term in self.search_terms:
            url = self.mp._generate_URL(search_term[0])
            self.assertEqual(url, "http://hae.monster.fi/ty%C3%B6paikkoja/?q=" + search_term[1] + "&cy=fi")

    def test_Indeed_URLGenerator(self):
        """Test proper Indeed URL is generated.
        """
        for search_term in self.search_terms:
            url = self.ip._generate_URL(search_term[0])
            self.assertEqual(url, "http://www.indeed.fi/jobs?as_and=" +  search_term[1] + 
                                  "&as_phr=&as_any=&as_not=&as_ttl=&as_cmp=&jt=all&st=&radius=" +
                                  "50&l=Helsinki&fromage=any&limit=50&sort=date&psf=advsrch")
        
    def test_Duunitoriparser(self):
        """Test Duunitori parser produces the correct fields.
        """
        self.dtp.parse(self.search_terms[0][0])
        results = self.dtp.get_job_ads()
        if len(results) == 0:
            raise AssertionError("No job ads parsed.")
        i = 0
        for ad in results:
            for key in self.job_ad_keys:
                self.assertIn(key, ad.keys())
                self.assertIsInstance(ad[key], str)
                self.assertTrue(ad[key] != "")
                par_url = urllib.parse.urlparse(ad["url"])
                self.assertIn("duunitori", par_url.netloc)
            if i == 0:
                #print example of job ad parsed
                i = i + 1
                print(str([ad[key] for key in self.job_ad_keys]).encode("unicode_escape"))
        
            
    def test_Monsterparser(self):
        """Test Monster parser produces the correct fields.
        """
        self.mp.parse(self.search_terms[0][0])
        results = self.mp.get_job_ads()
        if len(results) == 0:
            raise AssertionError("No job ads parsed.")
        i = 0
        for ad in results:
            for key in self.job_ad_keys:
                self.assertIn(key, ad.keys())
                self.assertIsInstance(ad[key], str)
                self.assertTrue(ad[key] != "")
                par_url = urllib.parse.urlparse(ad["url"])
                self.assertIn("monster", par_url.netloc)
            if i == 0:
                #print example of job ad parsed
                i = i + 1
                print(str([ad[key] for key in self.job_ad_keys]).encode("unicode_escape"))

    def test_Indeedparser(self):
        """Test Indeed parser produces the correct fields.
        """
        self.ip.parse(self.search_terms[0][0])
        results = self.ip.get_job_ads()
        if len(results) == 0:
            raise AssertionError("No job ads parsed.")
        i = 0
        for ad in results:
            for key in self.job_ad_keys:
                self.assertIn(key, ad.keys())
                self.assertIsInstance(ad[key], str)
                self.assertTrue(ad[key] != "")
                par_url = urllib.parse.urlparse(ad["url"])
                self.assertIn("indeed", par_url.netloc)
            if i == 0:
                #print example of job ad parsed
                i = i + 1
                print(str([ad[key] for key in self.job_ad_keys]).encode("unicode_escape"))

if __name__ == '__main__':
    unittest.main()