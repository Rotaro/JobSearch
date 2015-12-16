import jobadcollector.test as test
import datetime

#run tests
dbtests = test.DBTests()
dbtests.create_db_class_test()
dbtests.connect_db_test()
dbtests.store_ads_test()
dbtests.update_ads_test()
dbtests.get_classified_ads_test()


#test classification
import jobadcollector

my_search_terms = [
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
    'Diplomi',
    'Machine learning',
    'Koneoppiminen']

js = jobadcollector.JobAdCollector(my_search_terms, "tmp.db", classification=True)
#js.det_lang_store_ads(datetime.datetime.strptime("20-10-2015", "%d-%m-%Y"), 
#                      datetime.datetime.strptime("01-11-2015", "%d-%m-%Y"))
#RFC = js.train_model(language="English")
#js.recomm_store_ads(RFC, "English", 
#                      datetime.datetime.strptime("20-10-2015", "%d-%m-%Y"), 
#                      datetime.datetime.strptime("01-11-2015", "%d-%m-%Y"))
RFC = js.train_model(language="Finnish")
js.recomm_store_ads(RFC, "Finnish", 
                      datetime.datetime.strptime("20-10-2015", "%d-%m-%Y"), 
                      datetime.datetime.strptime("01-11-2015", "%d-%m-%Y"))


js.output_results(datetime.datetime.strptime("20-10-2015", "%d-%m-%Y"), 
                  datetime.datetime.strptime("01-11-2015", "%d-%m-%Y"),
                  "test.html", "html")

