import sqlite3
import datetime

class JobEntries:
    """Class for creating and updating databases of job entries."""

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
        html_start = """<html><head></head><body><table>"""
        html_start = html_start + """<tr>
        <td>Search term</td>
        <td>Site</td>
        <td>Job title</td>
        <td>Description</td>
        <td>Date</td>
        <td>URL</td>
        </tr>"""
        for db_entry in db_entries.fetchall():
            html_entry = """<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a href="%s">Link</a></td></tr>""" % (
                db_entry[1], db_entry[0], db_entry[3], db_entry[5], db_entry[6], db_entry[4])
            html_start = html_start + html_entry
        html_start = html_start + "</table></body></html>"
        return html_start


