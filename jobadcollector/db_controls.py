﻿import sqlite3
import datetime
import csv
import codecs

from .job_ad import JobAd

class JobAdDB:
    """Management of :mod:`sqlite3` database containing job ads.

    For each :class:`JobAd`, the database will store (column name in parentheses):

    - name of job ad site (site, varchar(255))
    - search term for job ad (searchterm, varchar(255))
    - a unique id (id, varchar(255) PRIMARY KEY)
    - job title (title, varchar(255))
    - url to job ad (url, varchar(1000))
    - description (description, varchar(1000))
    - date stored (date, date)
    - language (language, varchar(100))
    - relevance (relevant, integer)
    - recommendation (recommendation, integer)

    The class supports:

    - Storing fresh job ads (i.e. language, relevance, recommendation).
    - Retrieving job ads.
    - Retrieving job ads for classification.
    - Updating language and recommendation for job ads.

    Arguments
    ----------
    filename : str
        Name of database file. If file doesn't exist, a new one is created.
    """

    #columns in database
    _db_columns = ["site", "searchterm", "id", "title", "url", 
                   "description", "date", "language", "relevant",
                   "recommendation"]

    def __init__(self, filename):
        self._db_filename = filename
        self._conn = None

    def _connect_db(self):
        """Opens connection to instance database.
        
        Creates an empty table for job ads in the database if one doesn't exist.
        """
        if (self._db_filename != ""):
            self._conn = sqlite3.connect(self._db_filename)
            c = self._conn.cursor()
            if (c.execute("""SELECT * FROM sqlite_master WHERE name='JobEntries';""")
                .fetchone() == None):
                c.execute("""CREATE TABLE JobEntries (site varchar(255), 
                             searchterm varchar(255), id varchar(255) PRIMARY KEY, 
                             title varchar(255), url varchar(1000), 
                             description varchar(1000), date date,
                             language varchar(100), relevant integer,
                             recommendation integer);""")

    def disconnect_db(self):
        """Closes the database connection and frees the database file from use.
        """    
        if self._conn != None:
            self._conn.close()
            self._conn = None

    def store_ads(self, job_ads):
        """Stores NEW job ads in the database, existing ones are not updated.

        Arguments
        ----------
        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances containing job ads. Each dictionary 
            should have keys for site, searchterm, id, title, description, url. 
            See :class:'JobAdDB` description for details.
        """

        if self._conn == None:
            self._connect_db()
        c = self._conn.cursor()

        for ad in job_ads:          
            c.execute("""
            INSERT OR IGNORE INTO JobEntries
            VALUES (:site, :searchterm, :id, :title, :url, :description, :date, 
            :language, :relevant, :recommendation)""", 
            ad)

        self._conn.commit()

    def get_ads(self, date_start, date_end, language="all"):
        """Returns job ads from the database.

        Filters by date and language. Jobs ads are returned as a list of
        :class:`JobAd`.
                
        Arguments
        ----------
        date_start : :class:`datetime`
             Earliest date of job ads. If None, all job ads since the start 
             of the database are output.
        date_end : :class:`datetime`
            Latest date of job ads. If None, all job ads until end of database
            are output. If both date_start and date_end are None, all job ads 
            in the database are output.
        language : str
            Language of job ads to output.
        Returns
        ----------
        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances.
        """

        if self._conn == None:
            self._conn = sqlite3.connect(self._db_filename)
        c = self._conn.cursor()

        if language == "all":
            if (date_start == None and date_end == None):
                c.execute("""SELECT * FROM JobEntries""")
            elif(date_start == None):
                c.execute("""SELECT * FROM JobEntries WHERE date <= ? """, (date_2,)) 
            elif(date_end == None):
                c.execute("""SELECT * FROM JobEntries WHERE date >= ? """, (date_1,)) 
            else:
                c.execute("""SELECT * FROM JobEntries WHERE date >= ? AND date <= ? """,
                          (date_start,date_end,)) 
        else:
            if (date_start == None and date_end == None):
                c.execute("""SELECT * FROM JobEntries WHERE language = ?""", (language,))
            elif(date_start == None):
                c.execute("""SELECT * FROM JobEntries 
                             WHERE language = ? AND date <= ? """, (language,date_2)) 
            elif(date_end == None):
                c.execute("""SELECT * FROM JobEntries
                             WHERE language = ? AND date >= ? """, (language,date_1)) 
            else:
                c.execute("""SELECT * FROM JobEntries
                             WHERE language = ? AND date >= ? AND date <= ? """,
                          (language, date_start,date_end,)) 
        
        results =  [JobAd.create(dict(zip(self._db_columns, db_entry))) 
                for db_entry in c.fetchall()]

        return results

    def update_ads(self, job_ads):
        """Updates existing job ads.

        Arguments
        ----------
        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances.
        """
        if self._conn == None:
            self._connect_db()
        c = self._conn.cursor()

        for ad in job_ads:
            c.execute("""
            REPLACE INTO JobEntries
            VALUES (:site, :searchterm, :id, :title, :url, :description, :date, 
            :language, :relevant, :recommendation)""", 
            ad)

        self._conn.commit()

    def update_ads_recommendation(self, job_ads):
        """Updates the recommendation of job ads.

        Arguments
        ----------
        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances with id and recommendation defined.
        """
        if self._conn == None:
            self._connect_db()
        c = self._conn.cursor()

        for ad in job_ads:
            c.execute("""
            UPDATE JobEntries
            SET recommendation = :recommendation
            WHERE id = :id""",
            ad)
        
        
        self._conn.commit()

    def update_ads_language(self, job_ads):
        """Updates the language of job ads.

        Arguments
        ----------
        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances with id and language defined.
        """
        if self._conn == None:
            self._connect_db()
        c = self._conn.cursor()

        for ad in job_ads:
            c.execute("""
            UPDATE JobEntries
            SET language = :language
            WHERE id = :id""",
            ad)
        
        self._conn.commit()

    def get_classified_ads(self, 
            date_start=datetime.datetime.strptime("01-01-2015", "%d-%m-%Y"), 
            date_end=datetime.date.today(), language="English", all_columns=False):
        """Retrieves classified job ads, i.e. ads with relevant set to 0 or 1, 
        from database.
        
        Arguments
        ----------
        date_start : :class:`datetime`
            Earliest date of job ads. Default is start of 2015.
        date_end : :class:`datetime`
            Latest date of job ads. Default is present day. 
        language : str
            Language of job ads. Default is "English."
        all_columns : bool
            Specifies which columns should be retrieved. If True, all columns are
            returned (see :class:`JobAdDB` description). If False, only site, search 
            term, title, description, language and relevant are returned.
        Returns
        ----------
        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances.
        """

        if self._conn == None:
            self._conn = sqlite3.connect(self._db_filename)
        c = self._conn.cursor()

        if all_columns == 0:
            columns = ["site", "searchterm" , "title", "description", 
                       "language", "relevant"]
            entries = c.execute("""
                                SELECT site, searchterm, title, description, 
                                language, relevant
                                FROM JobEntries
                                WHERE relevant != 'None' AND language == ? 
                                      AND date >= ? AND date <= ?""",
                                (language, date_start, date_end))
        else:
            columns = self._db_columns
            entries = c.execute("""
                                SELECT * FROM JobEntries
                                WHERE relevant != 'None' AND language == ? 
                                AND date >= ? AND date <= ?""",
                                (language, date_start, date_end))

        results = [JobAd.create(dict(zip(columns, db_entry))) 
                for db_entry in c.fetchall()]

        return results

    def write_HTML_file(self, job_ads, filename):
        """Writes jobs ads to an HTML file.

        The HTML file uses a local css file, jobsearch.css, as style
        sheet.

        Arguments
        ----------
        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances.
        filename : str
            Name of file to write. Any existing file is overwritten.
        """
        row_number = 0
        html_start = """<!DOCTYPE HTML><html><head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <script type="text/javascript">function hideRow(rownumber)
            {document.getElementById(rownumber).style.display='none';}
            </script><link rel="stylesheet" href='jobsearch.css' />
            </head><body><table>"""
        html_start = html_start + """
            <tr class="headers">
                <th class="searchterm">Search term</th>
                <th class="site">Site</th>
                <th class="jobtitle">Job title</th>
                <th class="description">Description</th>
                <th class="date">Date</th>
                <th class="url">URL</th>
                <th class="language">Language</th>
                <th class="relevant">Relevant</th>
                <th class="relevant">Recommendation</th>
                <th></th>
            </tr>"""
        for ad in job_ads:
            ad_list = [ad[column] for column in self._db_columns]
            html_entry = """
            <tr class="%s" origsite="%s" id="%d">
                <td class="searchterm">%s</td>
                <td class="site">%s</td>
                <td class="jobtitle">%s</td>
                <td class="description">%s</td>
                <td class="date">%s</td>
                <td class="url"><a href="%s">Link</a></td>
                <td class="language">%s</td>
                <td class="relevant">%s</td>
                <td class="recommendation">%s</td>
                <td class="hidebutton">
                    <input type="button" id="hidebutton" value="Hide" 
                    onclick='hideRow("%d");' />
                </td>
            </tr>""" % (
                ad_list[1], ad_list[0], row_number, ad_list[1],
                ad_list[0], ad_list[3], ad_list[5], 
                ad_list[6], ad_list[4], ad_list[7], 
                ad_list[8], ad_list[9], row_number)
            html_start = html_start + html_entry
            row_number = row_number + 1;
        html_start = html_start + "</table></body></html>"
        file = codecs.open(filename, "w", encoding="utf-8")
        file.write(html_start)
        file.close()

    def write_CSV_file(self, job_ads, filename):
        """Writes jobs ads to a CSV file (Excel style).

        job_ads : list[:class:`JobAd`]
            List of :class:`JobAd` instances.
        filename : str
            Name of file to write to. Any existing file is overwritten.
        """

        headers = ["Search term", "Site", "Job title", "Description", "Date", 
                   "URL", "Language", "Relevant", "Recommendation"]
        file = codecs.open(filename, "w", encoding="utf-8")
        csv_writer = csv.writer(file, dialect=csv.excel)
        csv_writer.writerow(headers)
        for ad in job_ads:
            csv_writer.writerow([
                ad[key] for key in ["searchterm", "site", "title", "description", 
                                    "date", "url", "language", "relevant", 
                                    "recommendation"]])
        file.close()



