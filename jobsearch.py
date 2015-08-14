# -*- coding: iso-8859-1 -*-

import parsers
import db_controls
import datetime
import time
import random
import codecs
import re

search_terms = [
    'Analyytikko',
    'Analyst',
    'Physics',
    'Fysiikka',
    'Fyysikko',
    'Science',
    'M.Sc',
    'FM',
    'Entry',
    'First',
    'Graduate',
    'Associate',
    'Matlab',
    'Tohtorikoulutettava',
    'Doctoral',
    'Materials',
    'Materiaali',
    'Diplomi']


random.seed(1222)

new_db = db_controls.JobEntries("tmp.db")
new_db.set_db()

#for search_term in search_terms:
#    print(search_term)
#    time.sleep(random.randint(3,5))
#    monster_parser = parsers.MonsterParser()
#    indeed_parser = parsers.IndeedParser()
#    duunitori_parser = parsers.DuunitoriParser()
#    indeed_parser.parse_URL(parsers.URLGenerator.Indeed_URL(search_term))
#    print('indeed')
#    monster_parser.parse_URL(parsers.URLGenerator.Monster_URL(search_term))
#    print('monster')
#    duunitori_parser.parse_URL(parsers.URLGenerator.Duunitori_URL(search_term))
#    print('duunitori')
#    job_entries = monster_parser.get_job_entries()
#    new_db.set_new_entries(indeed_parser.get_job_entries(), 'indeed', search_term)
#    new_db.set_new_entries(monster_parser.get_job_entries(), 'monster', search_term)
#    new_db.set_new_entries(duunitori_parser.get_job_entries(), 'duunitori', search_term)

tod = datetime.date.today()
yes = tod - datetime.timedelta(days=1)
dayyes = tod - datetime.timedelta(days=2)


file = codecs.open("test.html", "w", encoding="utf-8")
file.write(new_db.generate_HTML_table(new_db.get_entries(yes)))
file.close()



