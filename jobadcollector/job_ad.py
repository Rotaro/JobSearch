
class JobAd(dict):
    """Job ad container.

    Subclass of dictionary which only accepts as keys the following (description
    in parentheses):
    
    - site (name of job ad site)
    - searchterm (searchterm which found ad)
    - id (unique id)
    - title (job ad title)
    - url (url to job ad)
    - description (job ad description / additional information)
    - date (datetime instance of when job ad was)
    - language (language of job ad)
    - relevant (relevance of job ad, set by user if desired)
    - recommendation (recommendation for job ad, provided by machine learning 
      model)

    """

    def __init__(self):
        super(JobAd, self).__init__()
        self['site'] = None
        self['searchterm'] = None
        self['id'] = None
        self['title'] = None
        self['url'] = None
        self['description'] = None
        self['date'] = None
        self['language'] = None
        self['language'] = None
        self['language'] = None
        self['relevant'] = None
        self['recommendation'] = None



