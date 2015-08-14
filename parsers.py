from html.parser import HTMLParser
import urllib.request
from urllib.parse import urlparse

class URLGenerator:
    """ Generates URLs based on provided search term for different sites. """
    def Indeed_URL(search_term):
        return "http://www.indeed.fi/jobs?as_and=%s&as_phr=&as_any=&as_not=&as_ttl=&as_cmp=&jt=all&st=&radius=50&l=Helsinki&fromage=any&limit=50&sort=date&psf=advsrch" % search_term
    def Monster_URL(search_term):
        return "http://hae.monster.fi/ty%%C3%%B6paikkoja/?q=%s&cy=fi" % search_term
    def Duunitori_URL(search_term):
        return "http://duunitori.fi/tyopaikat/?haku=%s&alue=" % search_term
    


class IndeedParser(HTMLParser):
    """HTML parser for Indeed.fi job searches. Saves results in an object dictionary 
    as {id: [title, url]}, where id is taken from the webpage. """
    job = 0
    add = 0
    job_entries = {}
    id = ""
    title = ""
    url = ""
    additional = ""

    def __init__(self):
        super(IndeedParser, self).__init__(convert_charrefs=True)

    def save_job_entry(self, id, title, url, additional):
        """Saves job entries parsed from html in object's dictionary. """
        self.job_entries[id] = [title.replace("\\r\\n", "\r\n"), url, additional.replace("\\r\\n", "\r\n")]

    def get_job_entries(self):
        """Returns the object's dictionary of job entries."""
        return self.job_entries

    def handle_starttag(self, tag, attrs):
        if (tag == "h2" and ('class', 'jobtitle') in attrs):
            self.job = 1
            for entry in attrs:
                if entry[0] == "id":
                    self.id = entry[1]
        elif (self.job == 1 and tag == "a"):
            for entry in attrs:
                if entry[0] == "href":
                    self.url = "http://www.indeed.fi" + entry[1]
        elif (self.add == 1 and tag == "div" and ('class', "result-link-bar-container") in attrs):
            self.add = 0
            self.save_job_entry(self.id, self.title, self.url, self.additional)
            self.id = ""
            self.title = ""
            self.url = ""
            self.additional = ""

    def handle_endtag(self, tag):
        if (self.job == 1 and tag == "h2"):
            self.add = 1
            self.job = 0

    def handle_data(self, data):
         if (self.job == 1):
            self.title = self.title + " " + data.encode().decode('unicode_escape').encode('latin-1').decode('utf-8').strip()
         elif (self.add == 1):
            self.additional = self.additional + " " + data.encode().decode('unicode_escape').encode('latin-1').decode('utf-8').strip()

    def parse_URL(self, URL):
        url_req = urllib.request.urlopen(URL)
        self.feed(str(url_req.read()).replace('\\n', ' ').strip())


class MonsterParser(HTMLParser):
    """HTML parser for Monster.fi job searches. Saves results in an object dictionary 
    as {id: [title, url]}, where id is taken from the webpage. """
    job = 0
    add = 0
    job_entries = {}
    id = ""
    title = ""
    url = ""
    additional = ""

    def __init__(self):
        super(MonsterParser, self).__init__(convert_charrefs=True)

    def save_job_entry(self, id, title, url, additional):
        """Saves job entries parsed from html in object's dictionary. """
        self.job_entries[id] = [title.replace("\\r\\n", "\r\n").replace("\\n","\n"), url, additional.replace("\\r\\n", "\r\n").replace("\\n","\n")]

    def get_job_entries(self):
        """Returns the object's dictionary of job entries."""
        return self.job_entries

    def handle_starttag(self, tag, attrs):
        if (self.job != 1 and tag == "div" and ('class', 'jobTitleContainer') in attrs):
            self.job = 1
        elif (self.job != 1 and tag == "div" and ('class', 'companyContainer') in attrs):
            self.add = 1
        elif (self.job != 1 and self.add == 1 and tag == "div" and ('class', 'companyLogo') in attrs):
            self.save_job_entry(self.id, self.title, self.url, self.additional)
            self.add = 0
            self.id = ""
            self.title = ""
            self.url = ""
            self.additional = ""
        elif (self.job == 1 and tag == "a"):
            for entry in attrs:
                if entry[0] == "href":
                    self.url = entry[1].strip()
                elif entry[0] == "name":
                    self.id = entry[1].strip()

    def handle_endtag(self, tag):
        if (self.job == 1 and tag == "div"):
            self.job = 0

    def handle_data(self, data):
         if (self.job == 1):
             self.title = self.title + " " + data.encode().decode('unicode_escape').encode('latin-1').decode('utf-8').strip()
         elif (self.add == 1):
             self.additional = self.additional + " " + data.encode().decode('unicode_escape').encode('latin-1').decode('utf-8').strip()

    def parse_URL(self, URL):
        url_req = urllib.request.urlopen(URL)
        self.feed(str(url_req.read()).replace('\\r\\n', ' ').strip())

class DuunitoriParser(HTMLParser):
    """HTML parser for Duunitori.fi job searches. Saves results in an object dictionary 
    as {id: [title, url]}, where id is taken from the webpage. """
    job = 0
    a_data = 0
    title_added = 0
    job_list = 0
    job_entries = {}
    id = ""
    title = ""
    url = "" 
    additional = ""
    
    def __init__(self):
        super(DuunitoriParser, self).__init__(convert_charrefs=True)

    def save_job_entry(self, id, title, url, additional):
        """Saves job entries parsed from html in object's dictionary. """
        self.job_entries[id] = [title.replace("\\r\\n", "\r\n").replace("\\n","\n"), url, additional.replace("\\r\\n", "\r\n").replace("\\n","\n")]

    def get_job_entries(self):
        """Returns the object's dictionary of job entries."""
        return self.job_entries

    def handle_starttag(self, tag, attrs):
        if (tag == "div" and ('id', 'jobentry-list') in attrs):
            self.job_list = 1
        elif (self.job_list == 1 and tag == "div" and ('id', 'bottom-pagination') in attrs):
            self.job_list = 0
        elif (self.job_list == 1 and tag == "article" and ('class', 'jobentry-item') in attrs):
            self.job = 1
            for entry in attrs:
                if entry[0] == 'data-id':
                    self.id = entry[1]
            print(self.id)
        elif (self.job_list == 1 and tag == "a" and self.job == 1 and ('class', 'jobentry-link') in attrs):
            self.a_data = 1
            for entry in attrs:
                if entry[0] == "href":
                    self.url = "http://www.duunitori.fi/" + entry[1].strip()

    def handle_endtag(self, tag):
        if (self.job_list == 1 and tag == "a" and self.a_data == 1):
            self.title_added = 1
            self.a_data = 0 
            self.job = 0
        elif(self.job_list == 1 and self.title_added == 1 and tag == "article"):
            self.save_job_entry(self.id, self.title, self.url, self.additional)
            self.title_added = 0
            self.title = ""
            self.id = ""
            self.url = ""
            self.additional = ""
            
    def handle_data(self, data):
        if (self.job_list == 1 and self.job == 1 and self.a_data == 1):
            self.title = self.title + " " + data.encode().decode('unicode_escape').encode('latin-1').decode('utf-8').strip()
        elif(self.job_list == 1 and self.title_added == 1):
            self.additional = self.additional + " " + data.encode().decode('unicode_escape').encode('latin-1').decode('utf-8').strip()

    def parse_URL(self, URL):
        url_req = urllib.request.urlopen(URL)
        self.feed(str(url_req.read()).replace('\\r\\n', ' ').strip())