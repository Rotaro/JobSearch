from html.parser import HTMLParser
import urllib.request
from urllib.parse import urlparse, quote_plus
import abc
import re

from .job_ad import JobAd

class JobAdParser(HTMLParser, metaclass=abc.ABCMeta):
    """Abstract :class:`HTMLParser` subclass for parsing job ad sites.

    Contains functions for starting search and returning parsed :class:`JobAd` instances. 
    :class:`JobAdParser` is further subclassed for implementation of parsing 
    logic for particular sites. The implementation should do the following:

    - Produce id, title, url and additional information (e.g. short description)
      for each job ad. 
    - Once parsed, the information should be stored in the instance variables _id,
      _title, _url, _additional. 
    - Once an ad has been fully parsed, the instance function _save_job_ad()
      should be called.

    """

    parsers_impl = ['indeed', 'duunitori', 'monster']

    def __init__(self):
        super(JobAdParser, self).__init__(convert_charrefs=True)
        #storage place for job ads
        self._job_ads = []
        #temporary storage of ad data during parsing
        self._id = ""
        self._title = ""
        self._url = "" 
        self._additional = ""

    def parse(self, search_term):
        """Performs search on job ad site for search term.

        Arguments
        ----------
        search_term : str
            Search term for job ad site.
        """
        url = self._generate_URL(search_term)
        url_req = urllib.request.urlopen(url)
        encoding = url_req.headers.get_content_charset()
        url_req_text = re.sub("\s+", " ", url_req.read().decode(encoding))
        url_req_text = re.sub("(&nbsp;)+", " ", url_req_text)
        self.feed(url_req_text)
   
    def get_job_ads(self):
        """Returns parsed job ads. 
       
        Job ads are stored as a list of dictionaries. Each dictionary has keys
        for database columns id, title, url and description (see :class:`JobAdDB` 
        description for details).

        Returns
        ----------
        job_ads : list
            List of :class:`JobAd` instances.
        """
        return self._job_ads

    def _save_job_ad(self):
        """Saves parsed job in instance. 

        Should only be called once parsing of ad is complete.  
        """
        self._job_ads.append(
            JobAd.create({
                "id" : self._id,
                "title" : re.sub("\s{2,}", " ", self._title.strip()), 
                "url" : self._url, 
                "description" : re.sub("\s{2,}", " ", self._additional.strip())}))

    @abc.abstractmethod
    def _generate_URL(self, search_term):
        """Generates URL for search term.

        Arguments
        ----------
        search_term : str
            Search term to generate URL for.
        """
        return self


class IndeedParser(JobAdParser):
    """Subclass of :class:`JobAdParser`. Implementation of parsing for Indeed.fi.
    """

    def __init__(self):
        super(IndeedParser, self).__init__()
        self._job = 0 #inside job ad
        self._add = 0 #parsing done

    def _generate_URL(self, search_term):
        """Generates URL for search term for indeed.fi.

        Arguments
        ----------
        search_term : str
            Search term to generate URL for.
        """
        search_term = search_term.replace(" ", "%20")

        return "http://www.indeed.fi/jobs?as_and=%s&as_phr=&as_any=&as_not=&as_ttl=&as_cmp=&jt=all&st=&radius=50&l=Helsinki&fromage=any&limit=50&sort=date&psf=advsrch" % quote_plus(search_term)

    def handle_starttag(self, tag, attrs):
        if (tag == "h2" and ('class', 'jobtitle') in attrs):
            self._job = 1
            for entry in attrs:
                if entry[0] == "id":
                    self._id = entry[1]
        elif (self._job == 1 and tag == "a"):
            for entry in attrs:
                if entry[0] == "href":
                    self._url = "http://www.indeed.fi" + entry[1]
        elif (self._add == 1 and tag == "div" and 
              ('class', "result-link-bar-container") in attrs):
            #parsing complete, reset temporary storage
            self._add = 0
            self._save_job_ad()
            self._id = ""
            self._title = ""
            self._url = ""
            self._additional = ""

    def handle_endtag(self, tag):
        if (self._job == 1 and tag == "h2"):
            self._add = 1
            self._job = 0

    def handle_data(self, data):
         if (self._job == 1):
            self._title = self._title + " " +  data.strip()
         elif (self._add == 1):
            self._additional = self._additional + " " + data.strip()

class MonsterParser(JobAdParser):
    """Subclass of :class:`JobAdParser`. Implementation of parsing for Monster.fi.
    """
    
    def __init__(self):
        super(MonsterParser, self).__init__()
        self._job = 0 #inside job ad
        self._add = 0 #parsing done

    def _generate_URL(self, search_term):
        """Generates URL for search term for monster.fi.

        Arguments
        ----------
        search_term : str
            Search term to generate URL for.
        """
        return "http://hae.monster.fi/ty%%C3%%B6paikkoja/?q=%s&cy=fi" % quote_plus(search_term)

    def handle_starttag(self, tag, attrs):
        if (self._job != 1 and tag == "div" and ('class', 'jobTitleContainer') in attrs):
            self._job = 1
        elif (self._job != 1 and tag == "div" and ('class', 'companyContainer') in attrs):
            self._add = 1
        elif (self._job != 1 and self._add == 1 and tag == "div" and 
              ('class', 'companyLogo') in attrs):
            #parsing done, reset temporary storage
            self._save_job_ad()
            self._add = 0
            self._id = ""
            self._title = ""
            self._url = ""
            self._additional = ""
        elif (self._job == 1 and tag == "a"):
            for entry in attrs:
                if entry[0] == "href":
                    self._url = entry[1].strip()
                elif entry[0] == "name":
                    self._id = entry[1].strip()

    def handle_endtag(self, tag):
        if (self._job == 1 and tag == "div"):
            self._job = 0

    def handle_data(self, data):
         if (self._job == 1):
             self._title = self._title + " " + data.strip()
         elif (self._add == 1):
             self._additional = self._additional + " " + data.strip()


class DuunitoriParser(JobAdParser):
    """Subclass of :class:`JobAdParser`. Implementation of parsing for Duunitori.fi.
    """
      
    def __init__(self):
        super(DuunitoriParser, self).__init__()
        self._job = 0           #inside job ad
        self._job_list = 1      #inside search results
        self._title_stat = 0    #inside title element
        self._title_added = 0   #title has been added

    def _generate_URL(self, search_term):
        """Generates URL for search term for duunitori.fi.

        Arguments
        ----------
        search_term : str
            Search term to generate URL for.
        """
        return "http://duunitori.fi/tyopaikat/?haku=%s&alue=" % quote_plus(search_term)

    def handle_starttag(self, tag, attrs):
        if (tag == "section" and ('class', 'setion--secondary') in attrs):
            self._job_list = 0 #no longer in main job list
        elif (self._job_list == 1 and tag == "a" and 
              ('class', 'jobentry--item') in attrs):
            self._job = 1 #start of job ad
            for entry in attrs:
                if entry[0] == "href":
                    self._url = "http://www.duunitori.fi/" + entry[1].strip()
                    self._id = entry[1].strip().split("-")[-1]
        elif (self._job == 1 and tag == "h3" and 
              ('itemprop', 'title') in attrs):
            self._title_stat = 1 #start of title element

    def handle_endtag(self, tag):
        if (self._job_list == 1 and self._job == 1 and self._title_stat == 1
            and tag == "h3"):
            self._title_stat = 0 #end of title element
        elif(self._job_list == 1 and self._job == 1 and self._title_stat == 0 and
             tag == "a"):
            #parsing complete, reset temporary storage
            self._save_job_ad()
            self._job = 0
            self._title = ""
            self._id = ""
            self._url = ""
            self._additional = ""
            
    def handle_data(self, data):
        if (self._job_list == 1 and self._job == 1 and self._title_stat == 1):
            self._title = self._title + " " + data.strip()
        elif(self._job_list == 1 and self._job == 1 and self._title_added == 0):
            self._additional = self._additional + " " + data.strip()

