import rpy2.robjects as robjects
from rpy2.robjects.vectors import StrVector, FloatVector, IntVector
import rpy2.robjects.packages as rpackages
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage as STAP 
import datetime


class RRFClassification:
    """
    Class for classifying job ads as relevant or not.

    This class can train a random forest model to predict the relevancy of 
    new job ads. The model can be stored in a file for later use.

    Arguments:
    Rlibpath       - Path to local R libraries.
    search_terms   - All search terms used. Needed to include all factor
                     levels in the model.
    sites          - All possible job ad sites. Needed to include all factor
                     levels in the model.
    language       - Language of ads to train on / classify.
    """

    #Functions which were easier to implement in pure R than using rpy2.
    R_functions_str = """ 
        cleanJobAds <- function(class_data, search_terms, sites) {
            # Cleans and transforms job ads.
            # More precisely:
            # - Joins title and description columns
            # - Removes rows with empty column(s), removes extra whitespaces
            # - Removes duplicates 
            # - Adds all factor levels to search terms and sites
            #
            # Returns a data frame with only site, search
            #
            # Arguments:
            # class_data   - dataframe with columns for site, title, description,
            #                searchterm and relevant.
            # search_terms - Character vector of all search terms used, needed for 
            #                factor levels.
            # sites        - Character vector of all job ad sites, needed for 
            #                factor levels.
            class_data$description <- paste(class_data$title, class_data$description)
            class_data$title <- NULL
            #get rid of rows with empty column(s)
            for (col in colnames(class_data)) {
                class_data <- class_data[!(class_data[col] == ""),]
                class_data <- class_data[!is.na(class_data[col]),]
            }
            class_data <- unique(class_data)
            #get rid of extra whitespace in description
            class_data$description <- str_trim(class_data$description)
            class_data$description <- gsub("\\\\s+", " ", class_data$description)
            #assign proper factor levels
            class_data$site <- as.factor(class_data$site)
            levels(class_data$site) <- 
                 c(levels(class_data$site), sites[!(sites %in% levels(class_data$site))])
            print(summary(class_data$site))
            class_data$searchterm <- as.factor(class_data$searchterm)
            levels(class_data$searchterm) <- 
                 c(levels(class_data$searchterm), search_terms[!(search_terms %in% levels(class_data$searchterm))])
            print(summary(class_data$searchterm))

            return(class_data)
        }      
        createJoinDTM <- function(class_data, lang) {
            # Transforms and parses the description column for words.
            # Words are cleaned and stemmed, and finally added as columns 
            # to the dataframe.
            #
            # Returns dataframe with columns for all parsed words in the description
            # column. The description column itself is removed.
            #
            # Arguments:
            # class_data - Dataframe of cleaned job ads using R_function cleanJobAds.
            # lang       - Language of job ads, needed for stemming and removing 
            #              stopwords.
            
            #create corpus from descriptions
            corpus <- Corpus(VectorSource(class_data$description))
            #cleaning and stemming operations applied to corpus
            corpus <- tm_map(corpus, tolower)
            corpus <- tm_map(corpus, PlainTextDocument) #need to convert after tolower
            corpus <- tm_map(corpus, removePunctuation)
            corpus <- tm_map(corpus, removeWords, stopwords(lang))
            corpus <- tm_map(corpus, stemDocument, lang)
            #create document term matrix and remove sparse terms
            dtm <- DocumentTermMatrix(corpus)
            dtm <- removeSparseTerms(dtm, 0.98)
            dtm <- as.data.frame(as.matrix(dtm))
            class_data <- cbind(class_data, dtm)
            class_data$description <- NULL
            colnames(class_data) <- make.names(colnames(class_data))
            return (class_data)
        }
        RFmodel <- function(train_data, cutoff) {
            # Trains random forest binary classification model using the provided
            # cutoffs.
            #
            # Returns model.
            #
            # Arguments:
            # train_data - Dataframe containing parsed words from job ads. 
            # cutoff     - Threshold for determining whether relevant or not.
            train_data$relevant <- as.factor(train_data$relevant)
            RFmodel <- randomForest(relevant ~ ., data=train_data, cutoff = cutoff)
            return(RFmodel)}
        RFpred <- function(RFmodel, test_data) {
             # Classifies job ads as relevant or not using provided model.
             # 
             # Returns factor of classifications.
             #
             # Arguments: 
             # RFmodel   - Model to use.
             # test_data - Dataframe containing parsed words from job ads as columns. 
             #
            return(predict(RFmodel, newdata=test_data))}
        splitTerms <- function(terms_data, bool) {
            #Helper function for splitting data into training and testing sets.
            return (terms_data == bool)
            }
        model_eval <- function(predictions, actual, thold, printb=0) {
              # Calculates and optionally prints characteristics of model.
              # Returns the following in a column vector:
              # accuracy, sensitivity, RMSE, 
              # true positives, true negatives, 
              # false positives, false negatives, 
              # fscore
              #
              predictions <- as.numeric(predictions)
              actual <- as.numeric(actual)
              if (thold != -1) {
                preds <- predictions >= thold
              }
              if (max(predictions) == 2) {
                    preds <- predictions-1
              }
              
              TP <- sum(actual + preds == 2)
              TN <- sum(actual + preds == 0)
              FP <- sum(actual - preds == -1)
              FN <- sum(actual - preds == 1)

              #accuracy
              acc <- (TP + TN) / (TP + TN + FP + FN)
              #sensitivity
              sens <- (TP / (TP + FN))
              #fscore
              fscore <- 2*TP/(2*TP+FP+FN)
  
              #error measure
              err <- sum((actual - preds)^2)
              if (printb == 1) {
                cat("Accuracy", acc, "\n")
                cat("Sensitivity", sens, "\n")
                cat("Fscore", fscore, "\n")
                cat("Error (RMSE)", err, "\n")
              }
              return(c(acc, sens, err, TP, TN, FP, FN, fscore))
            }
        prepNewAds <- function(RFmodel, new_ads) {
              #Prepares new ads for classification by model. 
              #Looks for words used by model and discards 
              #words not in model.
  
              model_columns <- as.character(attr(RFmodel$terms, "variables"))
              new_ads <- new_ads[(names(new_ads) %in% model_columns)]
              for (col in model_columns[!(model_columns %in% names(new_ads))]) {
                new_ads[col] <- rep(0, nrow(new_ads))
              }
              return(new_ads)
            }
        saveFile <- function(object, filename) {
            save(object, file=filename)
        }
        """
    #columns needed for training model
    train_columns = ["site", "searchterm", "title", "description", "relevant"]
    #columns needed for classifying new job ads
    class_columns = ["id", "site", "searchterm", "title", "description"]

    language = ""
    RFmodel = None

    def __init__(self, Rlibpath, search_terms, sites, language):
        self.language = language
        #factor levels
        self.search_terms = search_terms
        self.sites = sites
        #base R assets
        self.utils = rpackages.importr('utils')
        self.utils.chooseCRANmirror(ind=5) #randomly chosen mirror
        self.base = rpackages.importr('base')
        #local library path
        self.base._libPaths(Rlibpath)
        #change locale or R uses windows-1252 encoding for r_repr()
        robjects.r['Sys.setlocale']("LC_CTYPE", "C") 
        
        # import needed packages
        # words pre-processing:
        # tm           - Framework for text mining.
        # SnowballC    - Stemming.
        # textcat      - Determining language of text.
        #
        # randomForest - Random forest.
        # caret        - Classification And REgression Training. Used for cross
        #                validation.
        # Additional:
        # caTools      - Splitting data into training and test sets intelligently.
        needed_packages = ["tm", "SnowballC", "caTools", "randomForest", "textcat", 
                           "caret", "stringr"]
        needed_packages = [package for package in needed_packages 
                           if not rpackages.isinstalled(package)]
        load_packages = ["tm", "SnowballC", "caTools", "randomForest", "textcat", 
                         "caret", "stringr", "grDevices"]
        #load and install
        if len(needed_packages) > 0:
            self.utils.install_packages(StrVector(needed_packages))

        self.loaded_packages = [rpackages.importr(package) 
                                for package in load_packages]
        self.loaded_packages = dict(zip(load_packages, self.loaded_packages))

        self.R_functions = STAP(self.R_functions_str, "R_functions")


    def remove_diacritics(self, string):
        """Removes all Swedish (Finnish) diacritics from a string.
        """
        if isinstance(string, str):
            diacr = ["Ä", "ä", "Ö", "ö", "Å", "å"]
            replc = ["A", "a", "O", "o", "A", "a"]
            for i in range(0, len(diacr)):
                string = string.replace(diacr[i], replc[i])
    
        return string
    
    def create_R_dataframe(self, class_ads, include_columns):
        """Converts structure used in the local sqlite (see JobAdsDB class) to
        an R dataframe.

        Arguments:
        class_ads       - Job ads from the local database as a list of dictionaries.
        include_columns - Columns which are included in the dataframe. Each column
                          has to have a corresponding key in the job ad dictionaries.    
        """

        #modify structure to type {column:[rows]}
        
        class_ads_dataf = {}
        for column in include_columns:
            class_ads_dataf[column] = [self.remove_diacritics(ad[column]) 
                                       for ad in class_ads]
            if (column == "relevant"):
                class_ads_dataf[column] = IntVector(class_ads_dataf[column])
            else:
                class_ads_dataf[column] = self.base.I(StrVector(class_ads_dataf[column]))
             
        return robjects.DataFrame(class_ads_dataf)

    def train_model(self, class_ads, language, search_terms=None, sites=None):
        """Trains a random forest model for classification of job ad relevance.

        The model is stored in the RRFClassification instance variable RFmodel.

        Arguments:
        class_ads    - Classified ads used to the train the model. Ads should be
                       a list of dictionaries with keys for site, searchterm, 
                       title, description and relevant. See the JobAdsDB class for
                       details.
        language     - Language of job ads. Needed for proper stemming and removal 
                       of stopwords.
        search_terms - List of ALL search terms used, even if no ads were found
                       with them. These are needed to have all necessary factor
                       levels in the model.
        sites        - List of ALL sites searched, even if no ads were found on 
                       on the sites. These are needed to have all necessary factor
                       levels in the model.
        
        """
        if language == None:
            language = self.language
        if search_terms == None:
            search_terms = self.search_terms
        if sites == None:
            sites = self.sites
        print(search_terms)
        print(sites)
        ##parameters during training
        #typical value
        splitratio = 0.7
        #gave best F-score during parameter sweeping
        threshold = 0.3

        #convert to dataframe and clean ads
        dataf = self.create_R_dataframe(class_ads, self.train_columns)
        dataf = self.R_functions.cleanJobAds(dataf, StrVector(search_terms), StrVector(sites))
        dataf = self.R_functions.createJoinDTM(dataf, language.lower())

        #create training and testing data sets
        split = robjects.r['sample.split'](dataf.rx2('relevant'), splitratio)
        train = robjects.r['subset'](dataf, self.R_functions.splitTerms(split, 'TRUE'))
        test = robjects.r['subset'](dataf, self.R_functions.splitTerms(split, 'FALSE'))

        #train model
        self.RFmodel = self.R_functions.RFmodel(train, FloatVector([1-threshold, threshold])) 
        #test on testing set
        pred = self.R_functions.RFpred(self.RFmodel, test)
        conf_matrix = self.R_functions.model_eval(pred, test.rx2('relevant'), -1, 1)

    def save_model(self, filename):
        """Saves instance model to file for later use.

        Arguments:
        filename   - Name of file to save model in.
        """

        self.R_functions.saveFile(self.RFmodel, filename)
        
    def load_model(self, filename):
        """Loads random forest classification model from file.

        Arguments:
        filename   - Name of file to load model from.
        """

        self.RFmodel = robjects.r['get'](robjects.r['load'](filename))


    def classify_ads(self, ads, language=None,
                     search_terms=None, sites=None):
        """Classifies ads using instance model.

        Returns list of dictionaries containing with keys for id and classification 
        (i.e. prediction of relevancy).

        Arguments:
        ads          - Ads to classify. Needs to be a list of dictionaries with
                       keys for id, site, searchterm, title, description.
        language     - Language of ads to classify.
        search_terms - Search terms used in model (not needed if model factor levels
                       are the same as the instance search_terms variable).
        sites        - Sites used in model (not needed if model factor levels
                       are the same as the instance sites variable).
        """
        if language == None:
            language = self.language
        if search_terms == None:
            search_terms = self.search_terms
        if sites == None:
            sites = self.sites

        print(search_terms)
        print(sites)
        #convert to dataframe and clean ads
        dataf = self.create_R_dataframe(ads, self.class_columns)
        ids = dataf.rx2('id') 
        dataf = self.R_functions.cleanJobAds(dataf, StrVector(search_terms), StrVector(sites))
        dataf = self.R_functions.createJoinDTM(dataf, language.lower())
        dataf = self.R_functions.prepNewAds(self.RFmodel, dataf)

        #classify ads
        pred = self.R_functions.RFpred(self.RFmodel, dataf)

        #combine results in list of dictionaries
        results = [{"id" : ids[i], "recommendation": int(pred[i])-1} 
                   for i in range(0, robjects.r['length'](ids)[0])]
                           
        return results
        

    def determine_lang(self, title, description):
        """
        Tries to determine which language a job ad is using the textcat package. 
        Only differentiates between Finnish and English; returns English if another
        language is recognized.

        title       - Title of job ad.
        description - Description of job ad.
        """
        language_both = self.loaded_packages["textcat"].textcat(
            " ".join([title, description])).r_repr().replace("\"", "")
        language_title = self.loaded_packages["textcat"].textcat(title).r_repr().replace("\"", "")
        language_descrip = self.loaded_packages["textcat"].textcat(
            description).r_repr().replace("\"", "")

        #English job titles with Finnish text is sometimes mistaken
        #as danish, frisian or middle_frisian
        false_finnish = ["danish", "frisian", "middle_frisian"]

        if (language_both == "english" or language_both == "finnish"):
            return language_both[0].upper() + language_both[1:]
        elif (language_title == "english" or language_title == "finnish"):
            return language_title[0].upper() + language_title[1:]
        elif (language_descrip == "english" or language_descrip == "finnish"):
            return language_descrip[0].upper() + language_descrip[1:]
        elif (language_both in false_finnish or language_title in false_finnish or
                language_descrip in false_finnish):
            return "Finnish"
        else:
            return "English"

    def det_lang_ads(self, ads):
        """Attempts to determine language of a list of job ads.

        Returns list of dictionaries containing keys for id and 
        language.

        Arguments:
        ads - List of dictionaries representing job ads. Should contain
              keys for id, title and description.
        """

        results = [{"id": ad["id"], 
                    "language": self.determine_lang(ad["title"], ad["description"])}
                   for ad in ads]

        return results


if(__name__ == "__main__"):
    import db_controls
    search_terms = ['Analyytikko',
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
    sites = ['duunitori', 'monster', 'indeed']
    r = RRFClassification("C:/Users/SuperSSD/Documents/R/win-library/3.2", search_terms, sites)
    db = db_controls.JobAdsDB("tmp.db")
    #clean and transform data for creation of R dataframe
    class_ads = db.get_classified_ads(language="English", all_columns=1)

    RFmodel = r.train_model(class_ads, "English", search_terms, sites)
    r.save_model(RFmodel, "wutwut.test")
    RFmodel2 = r.load_model("wutwut.test")

    ads = db.get_ads(datetime.datetime.strptime("01-12-2015", "%d-%m-%Y"), 
                     datetime.datetime.strptime("05-12-2015", "%d-%m-%Y"))
    ##create dataframe 
    pred = r.classify_ads(ads, RFmodel, "English")
    pred2 = r.classify_ads(ads, RFmodel2, "English")
    ##print(pred.r_repr().encode("unicode_escape"))
    for i in range(0, len(pred)):
        print(pred[i] == pred2[i])

    #for i in range(0, len(ads)):
    #    print(i, len(ads))
    #    print(str(ads[i]['title']).encode("unicode_escape"), 
    #          float(pred[i]) >= 0.3)
              
    #conf_matrix = r.R_functions.model_eval(pred, new_dataf.rx2('relevant'), 0.3, 1)
    #print(conf_matrix.r_repr())

    #RFmodel2 = robjects.r['load']('randomForestModel.dat')
    #RFmodel2 = robjects.r['get'](RFmodel2)
    #pred = r.R_functions.RFpred(RFmodel2, test)
    #conf_matrix = r.R_functions.model_eval(pred, test.rx2('relevant'), 0.3, 1)
    #print(conf_matrix.r_repr())
