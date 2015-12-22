import rpy2.robjects as robjects
from rpy2.robjects.vectors import StrVector, FloatVector, IntVector
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage as STAP, importr
import datetime
import time

class JobAdClassification:
    """Classification of job ads as relevant or not using R and rpy2.

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
            class_data$searchterm <- as.factor(class_data$searchterm)
            levels(class_data$searchterm) <- 
                 c(levels(class_data$searchterm), search_terms[!(search_terms %in% levels(class_data$searchterm))])

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
              #if factor levels are 2,1 instead of 0,1 (will fail if 
              #actual levels are 0,1 but there are no 0 predictions)
              if (max(predictions) == 2 || min(predictions) == 1) {
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
                cat("Model characteristics:", "\n")
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

    def __init__(self, Rlibpath, search_terms, sites, language):
        self._RFmodel = None
        self._language = language
        self._search_terms = search_terms
        self._sites = sites
        #columns needed for training model
        self._train_columns = ["site", "searchterm", "title", "description", "relevant"]
        #columns needed for classifying new job ads
        self._class_columns = ["id", "site", "searchterm", "title", "description"]
        #random forest model parameters
        self._threshold = 0.3
        self._splitratio = 0.7
        #base R assets
        self.utils = robjects.packages.importr("utils")
        self.utils.chooseCRANmirror(ind=5) #randomly chosen mirror
        self.base = robjects.packages.importr("base")
        #local library path
        self.base._libPaths(Rlibpath)
        #change locale to use utf-8 for r_repr()
        robjects.r['Sys.setlocale']("LC_CTYPE", "C") 
        
        # tm           - Framework for text mining.
        # SnowballC    - Stemming.
        # textcat      - Determining language of text.
        #
        # randomForest - Random forest.
        # caTools      - Splitting data into training and test sets intelligently.
        # stringr      - String manipulation
        needed_packages = ["tm", "SnowballC", "textcat", "randomForest", "caTools",
                           "stringr"]
        #install packages
        to_install = [package for package in needed_packages 
                           if not robjects.packages.isinstalled(package)]
        if len(to_install) > 0:
            self.utils.install_packages(StrVector(to_install))
        #load packages
        self.loaded_packages = [robjects.packages.importr(package) 
                                for package in needed_packages]
        self.loaded_packages = dict(zip(needed_packages,  self.loaded_packages))
        #load R functions
        self.R_functions = STAP(
                self.R_functions_str, "R_functions")

    def _remove_diacritics(self, string):
        """Removes all Swedish (Finnish) diacritics from a string.
        """
        if isinstance(string, str):
            diacr = ["Ä", "ä", "Ö", "ö", "Å", "å"]
            replc = ["A", "a", "O", "o", "A", "a"]
            for i in range(0, len(diacr)):
                string = string.replace(diacr[i], replc[i])
    
        return string
    
    def create_R_dataframe(self, class_ads, include_columns):
        """Converts job ads to R dataframe.

        Arguments:
        class_ads       - Job ads from the local database (see JobAdsDB) as a list 
                          of dictionaries.
        include_columns - Columns which are included in the dataframe. Each column
                          has to have a corresponding key in the job ad dictionaries.    
        """

        #modify structure to type {column:[rows]}   
        class_ads_dataf = {}
        for column in include_columns:
            class_ads_dataf[column] = [self._remove_diacritics(ad[column]) 
                                       for ad in class_ads]
            if (column == "relevant"):
                class_ads_dataf[column] = IntVector(class_ads_dataf[column])
            else:
                class_ads_dataf[column] = self.base.I(StrVector(class_ads_dataf[column]))
             
        return robjects.DataFrame(class_ads_dataf)

    def train_model(self, class_ads, language=None, search_terms=None, sites=None):
        """Trains a random forest model for classification of job ad relevance.

        The model is stored in the JobAdClassification instance variable _RFmodel.

        Arguments:
        class_ads    - Classified ads used to the train the model. Ads should be
                       a list of dictionaries with keys for site, searchterm, 
                       title, description and relevant. See the JobAdsDB class for
                       details.
        language     - Language of job ads. Needed for proper stemming and removal 
                       of stopwords. If None, the language specified during
                       instance creation is used.
        search_terms - List of ALL search terms used, even if no ads were found
                       with them. These are needed to have all necessary factor
                       levels in the model. If None, the search terms specified during
                       instance creation is used.
        sites        - List of ALL sites searched, even if no ads were found on 
                       on the sites. These are needed to have all necessary factor
                       levels in the model. If None, the sites specified during
                       instance creation is used.
        """
        if language == None:
            language = self._language
        if search_terms == None:
            search_terms = self._search_terms
        if sites == None:
            sites = self._sites
        ##parameters for training
        #typical value
        splitratio = self._splitratio
        #gave best F-score during parameter sweeping
        threshold = self._threshold

        #convert to dataframe and clean ads
        dataf = self.create_R_dataframe(class_ads, self._train_columns)
        dataf = self.R_functions.cleanJobAds(dataf, StrVector(search_terms), StrVector(sites))
        dataf = self.R_functions.createJoinDTM(dataf, language.lower())

        #create training and testing data sets
        if (splitratio != 1.0):
            split = robjects.r['sample.split'](dataf.rx2('relevant'), splitratio)
            train = robjects.r['subset'](dataf, self.R_functions.splitTerms(split, 'TRUE'))
            test = robjects.r['subset'](dataf, self.R_functions.splitTerms(split, 'FALSE'))
        else:
            train = dataf
        #train model
        self._RFmodel = self.R_functions.RFmodel(train, FloatVector([1-threshold, threshold])) 
        #test on testing set
        if (splitratio != 1.0):
            pred = self.R_functions.RFpred(self._RFmodel, test)
            conf_matrix = self.R_functions.model_eval(pred, test.rx2('relevant'), -1, 1)

    def save_model(self, filename):
        """Saves instance model to file for later use.

        Arguments:
        filename   - Name of file to save model in.
        """

        self.R_functions.saveFile(self._RFmodel, filename)
        
    def load_model(self, filename):
        """Loads random forest classification model from file.

        Arguments:
        filename   - Name of file to load model from.
        """

        self._RFmodel = robjects.r['get'](robjects.r['load'](filename))


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
            language = self._language
        if search_terms == None:
            search_terms = self._search_terms
        if sites == None:
            sites = self._sites

        print(search_terms)
        print(sites)
        #convert to dataframe and clean ads
        dataf = self.create_R_dataframe(ads, self._class_columns)
        ids = dataf.rx2('id') 
        dataf = self.R_functions.cleanJobAds(dataf, StrVector(search_terms), StrVector(sites))
        dataf = self.R_functions.createJoinDTM(dataf, language.lower())
        dataf = self.R_functions.prepNewAds(self._RFmodel, dataf)

        #classify ads
        pred = self.R_functions.RFpred(self._RFmodel, dataf)

        #combine results in list of dictionaries
        results = [{"id" : ids[i], "recommendation": int(pred[i])-1} 
                   for i in range(0, robjects.r['length'](ids)[0])]
                           
        return results
        

    def _determine_lang(self, title, description):
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
                    "language": self._determine_lang(ad["title"], ad["description"])}
                   for ad in ads]

        return results

