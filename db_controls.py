import sqlite3
import datetime

class JobEntries:
    """
    Class for creating and updating an sqlite database of job entries. The
    database will store for each job entry a unique id, related search term, 
    name of site containing job ad, job title, url to job ad and a column for  
    possible additional information. 
    """
    db_filename = ""
    conn = None
 
    def __init__(self, filename):
        self.db_filename = filename

    def set_db(self):
        """
        Opens a connection to the database and creates a table for job entries 
        unless one already exists.
        """
        if (self.db_filename != ""):
            self.conn = sqlite3.connect(self.db_filename)
            c = self.conn.cursor()
            if (c.execute("""SELECT * FROM sqlite_master WHERE name='JobEntries';""")
                .fetchone() == None):
                c.execute("""CREATE TABLE JobEntries (site varchar(255), 
                             searchterm varchar(255), id varchar(255) PRIMARY KEY, 
                             title varchar(255), url varchar(1000), 
                             description varchar(1000), date date,
                             language varchar(100), relevant integer,
                             recommendation integer);""")

    def set_new_entries(self, new_job_entries, site, search_term):
        """ 
        Stores new job entries into the data base. Each job entry will
        contain a unique id, related search term, name of site containing job ad, 
        job title, url to job ad and a column for possible additional  information.

        new_job_entries - Dictionary of new job entries, {id : [title, url, description]}
        site            - Name of site job ad was found on.
        search_term     - Search term which found the job ad.
        """
        if(self.conn == None):
            self.conn = sqlite3.connect(self.db_filename)
        for_db = [(site, search_term, job_entry, new_job_entries[job_entry][0], 
                   new_job_entries[job_entry][1], new_job_entries[job_entry][2],
                   datetime.date.today()) for job_entry in new_job_entries] 
        for db_entry in for_db:
            c = self.conn.cursor()
            c.execute("""
            INSERT OR IGNORE INTO JobEntries
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            (db_entry[0], db_entry[1], db_entry[2], db_entry[3], 
             db_entry[4], db_entry[5], db_entry[6]), None, None, None)
        self.conn.commit()

    def update_w_dict(self, job_entries_dict):
        """
        Updates database with dictionary containing complete information of 
        entries.

        job_entries_dict - Dictionary of new job entries, 
                           {id : [site, search term, id, title, url, description, 
                                  date, language, relevant, recommendation]}
        """
        if(self.conn == None):
            self.conn = sqlite3.connect(self.db_filename)

        for key in job_entries_dict:
            c = self.conn.cursor()
            c.execute("""
            INSERT OR REPLACE INTO JobEntries
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            tuple(job_entries_dict[key]))
        self.conn.commit()

    def get_entries(self, date_1, date_2):
        """ 
        Returns cursor with all job entries between the provided dates. 
        If date_1 is None, all entries up until date_2 are returned. If date_2
        is None, all entries newer than date_1 are returned. If both are None,
        all entries are returned. 
        """
        if(self.conn == None):
            self.conn = sqlite3.connect(self.db_filename)
        c = self.conn.cursor()
        if (date_1 == None and date_2 == None):
            c.execute("""SELECT * FROM JobEntries""")
        elif(date_1 == None):
            c.execute("""SELECT * FROM JobEntries WHERE date <= ? """, (date_2,)) 
        elif(date_2 == None):
            c.execute("""SELECT * FROM JobEntries WHERE date >= ? """, (date_1,)) 
        else:
            c.execute("""SELECT * FROM JobEntries WHERE date >= ? AND date <= ? """,
                      (date_1,date_2,)) 
        return c

    def generate_HTML_table(self, db_entries):
        """
        Generates an HTML table of job entries from the database.
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
                <th class="relevant">Recomenndation</th>
                <th></th>
            </tr>"""
        for db_entry in db_entries.fetchall():
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
                db_entry[1], db_entry[0], row_number, db_entry[1], db_entry[0], 
                db_entry[3], db_entry[5], db_entry[6], db_entry[4], db_entry[7], 
                db_entry[8], db_entry[9], row_number)
            html_start = html_start + html_entry
            row_number = row_number + 1;
        html_start = html_start + "</table></body></html>"
        return html_start


