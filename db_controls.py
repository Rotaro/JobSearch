import sqlite3
import datetime

class JobEntries:
    """Class for creating and updating an sqlite database of job entries. The
    database will store for each job entry a unique id, related search term, 
    name of site containing job ad, job title, url to job ad and a column for  
    possible additional  information. """

    db_filename = ""
    conn = None
 
    def __init__(self, filename):
        self.db_filename = filename

    def set_db(self):
        """ Opens a connection to the database and creates a table for job entries 
        unless one already exists """
        if (self.db_filename != ""):
            self.conn = sqlite3.connect(self.db_filename)
            c = self.conn.cursor()
            if (c.execute("""SELECT * FROM sqlite_master WHERE name='JobEntries';""").fetchone() == None):
                c.execute('''CREATE TABLE JobEntries (site varchar(255), searchterm varchar(255), id varchar(255) PRIMARY KEY, title varchar(255), url varchar(1000), additional varchar(1000), date date);''')

    def set_new_entries(self, new_job_entries, site, search_term):
        """ Stores new job entries into the data base. Each job entry will
        contain a unique id, related search term, name of site containing job ad, 
        job title, url to job ad and a column for possible additional  information.

        new_job_entries - Dictionary of new job entries, {id : [title, url, additional]}
        site            - Name of site job ad was found on.
        search_term     - Search term which found the job ad.
        """
        if(self.conn == None):
            self.conn = sqlite3.connect(self.db_filename)
        for_db = [(site, search_term, job_entry, new_job_entries[job_entry][0], new_job_entries[job_entry][1], new_job_entries[job_entry][2], datetime.date.today()) for job_entry in new_job_entries] 
        for db_entry in for_db:
            c = self.conn.cursor()
            c.execute("""
            INSERT OR IGNORE INTO JobEntries
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (db_entry[0], db_entry[1], db_entry[2], db_entry[3], db_entry[4], db_entry[5], db_entry[6]))
        self.conn.commit()

    def get_entries(self, date_1):
        """ Returns cursor with all job entries older than provided date. 
        If date is None, all entries are returned. """
        if(self.conn == None):
            self.conn = sqlite3.connect(self.db_filename)
        c = self.conn.cursor()
        if(date_1 != None):
            c.execute("""SELECT * FROM JobEntries WHERE date > ? """, (date_1,))
        else:
            c.execute("""SELECT * FROM JobEntries""")
        return c

    def generate_HTML_table(self, db_entries):
        """ Generates an HTML table of job entries from the database. """
        row_number = 0
        html_start = """<!DOCTYPE HTML><html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <script type="text/javascript">function hideRow(rownumber){document.getElementById(rownumber).style.display='none';}</script><link rel="stylesheet" href='jobsearch.css' /></head><body><table>"""
        html_start = html_start + """<tr class="headers">
        <th>Search term</th>
        <th>Site</th>
        <th>Job title</th>
        <th>Description</th>
        <th>Date</th>
        <th>URL</th>
        <td></th>
        </tr>"""
        for db_entry in db_entries.fetchall():
            html_entry = """<tr class="%s" origsite="%s" id="%d">
            <td class="searchterm">%s</td>
            <td class="site">%s</td>
            <td class="jobtitle">%s</td>
            <td class="description">%s</td>
            <td class="date">%s</td>
            <td class="url"><a href="%s">Link</a></td>
            <td class="hidebutton"><input type="button" id="hidebutton" value="Hide" onclick='hideRow("%d");' />
            </tr>""" % (
                db_entry[1], db_entry[0], row_number, db_entry[1], db_entry[0], db_entry[3], db_entry[5], db_entry[6], db_entry[4], row_number)
            html_start = html_start + html_entry
            row_number = row_number + 1;
        html_start = html_start + "</table></body></html>"
        return html_start


