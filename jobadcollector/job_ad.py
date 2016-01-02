import datetime


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
    #columns allowed in JobAd instance
    _cols = ["site", "searchterm", "id", "title", "url", "description", "date",
             "language", "relevant", "recommendation"]

    def __init__(self):
        super(JobAd, self).__init__()
        for key in self._cols:
            self[key] = None
        self["date"] = datetime.date.today()

    def __setitem__(self, key, val):
        if key not in self._cols:
            raise KeyError("Key not column in JobAd.")
        return super().__setitem__(key, val)

    def __delitem__(self, key):
        if key in self._cols:
            self[key] = None
        else:
            return super().__delitem__(key)

    @classmethod
    def create(cls, dictionary):
        """Creates :class:`JobAd` instance from dictionary.

        Removes keys not belonging to JobAd.

        Arguments
        ----------
        dictionary : dict
            Dictionary with :class:`JobAd` columns as keys.

        Returns
        ----------
        job_ad : JobAd
            :class:`JobAd` instance with column values from dictionary.

        """
        job_ad = JobAd()
        for key in dictionary:
            if key in cls._cols:
                job_ad[key] = dictionary[key]

        return job_ad


    def columns_not_none(self, columns):
        """Checks that values of columns are not none.
        
        Arguments
        ----------
        columns : list[str]
            List of column names. 

        Returns
        ----------
        not_none : bool
            Whether columns are not none.
        """
        not_none = True
        for col in columns:
            if self[col] == None:
                return 0

        return not_none

