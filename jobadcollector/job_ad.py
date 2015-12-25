
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
    
    _cols = ["site", "searchterm", "id", "title", "url", "description", "date",
             "language", "relevant", "recommendation"]

    def __init__(self):
        super(JobAd, self).__init__()
        for key in self._cols:
            self[key] = None

    def __setitem__(self, key, val):
        if key not in self._cols:
            raise KeyError("Key not supported by JobAd.")
        return super().__setitem__(key, val)

    def __delitem__(self, key):
        if key in self._cols:
            self[key] = None
        else:
            return super().__delitem__(key)

