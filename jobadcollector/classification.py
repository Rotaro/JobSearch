import rpy2.robjects as robjects
from rpy2.robjects.vectors import StrVector, FloatVector, IntVector
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage as STAP, importr
import datetime
import time

class JobAdClassification:
    """Classification of job ads using R and rpy2.

    This class provides training of a machine learning model for 
    recommendations for new job ads. The class also provides classification
    of languages 

    Arguments
    ---------
    Rlibpath : str 
        Path to local R libraries.
    search_terms : list
        All search terms used in job ad collections. Needed to include all factor
        levels in the machine learning model.
    sites : list
        All job sites used in job ad collections. Needed to include all factor
        levels in the model.
    language : str
        Language of job ads / machine learning model. Currently only Finnish and
        English supported.
    """

    #Functions which were easier to implement in pure R than using rpy2.
    __R_functions_str = """ 
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
        self._train_columns = ["site", "searchterm", "title", "description", 
                               "relevant"]
        #columns needed for classifying new job ads
        self._class_columns = ["id", "site", "searchterm", "title", "description"]
        #random forest model parameters
        self._threshold = 0.3
        self._splitratio = 0.7
        #base R assets
        self._utils = robjects.packages.importr("utils")
        self._utils.chooseCRANmirror(ind=5) #randomly chosen mirror
        self._base = robjects.packages.importr("base")
        #local library path
        self._base._libPaths(Rlibpath)
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
            self._utils.install_packages(StrVector(to_install))
        #load packages
        self._loaded_packages = [robjects.packages.importr(package) 
                                for package in needed_packages]
        self._loaded_packages = dict(zip(needed_packages,  self._loaded_packages))
        #load R functions
        self._R_functions = STAP(
                self.__R_functions_str, "R_functions")

    def _remove_diacritics(self, string):
        """Removes all Swedish (Finnish) diacritics from a string.

        Arguments
        ----------
        string : str
            String to remove diacritics from.
        Returns
        ----------
        clean_string : str
            String without diacritics.
        """
        if isinstance(string, str):
            diacr = ["Ä", "ä", "Ö", "ö", "Å", "å"]
            replc = ["A", "a", "O", "o", "A", "a"]
            for i in range(0, len(diacr)):
                string = string.replace(diacr[i], replc[i])
    
        return string
    
    def create_R_dataframe(self, job_ads, include_columns):
        """Converts job ads to R dataframe.

        Arguments
        ----------
        job_ads : list
            List of dictionaries of job ads. Each dictionary should have keys for 
            all database columns (see :class:`JobAdDB` description for details).
        include_columns : list
            List of strings. Defines which columns are included in the dataframe. 
            Each column has to have a corresponding key in the job ad dictionaries.    
        Returns
        ----------
        dataf : :class:`robjects.DataFrame`
            :class:`robjects.DataFrame` representing job ads.
        """
        
        #modify structure to type {column:[rows]}   
        job_ads_dataf = {}
        for column in include_columns:
            job_ads_dataf[column] = [self._remove_diacritics(ad[column]) 
                                       for ad in job_ads]
            if (column == "relevant"):
                job_ads_dataf[column] = IntVector(job_ads_dataf[column])
            else:
                job_ads_dataf[column] = self._base.I(StrVector(job_ads_dataf[column]))
             
        return robjects.DataFrame(job_ads_dataf)

    def train_model(self, class_ads):
        """Trains a random forest model for classification of job ad relevance.

        Model is stored in the :class:`JobAdClassification` instance.

        Arguments
        ----------
        class_ads : list
            List of dictionaries of job ads, used to train model. Each dictionary
            should have keys for site, searchterm, title, description and relevant.
            See the :class:`JobAdsDB` class for details.
        """
        ##parameters for training
        #typical value
        splitratio = self._splitratio
        #gave best F-score during parameter sweeping
        threshold = self._threshold

        #convert to dataframe and clean ads
        dataf = self.create_R_dataframe(class_ads, self._train_columns)
        dataf = self._R_functions.cleanJobAds(dataf, StrVector(self._search_terms),
                                              StrVector(self._sites))
        dataf = self._R_functions.createJoinDTM(dataf, self._language.lower())

        #create training and testing data sets
        if (splitratio != 1.0):
            split = robjects.r['sample.split'](dataf.rx2('relevant'), splitratio)
            train = robjects.r['subset'](dataf, self._R_functions.splitTerms(split, 'TRUE'))
            test = robjects.r['subset'](dataf, self._R_functions.splitTerms(split, 'FALSE'))
        else:
            train = dataf
        #train model
        self._RFmodel = self._R_functions.RFmodel(train, FloatVector([1-threshold, threshold])) 
        #test on testing set
        if (splitratio != 1.0):
            pred = self._R_functions.RFpred(self._RFmodel, test)
            conf_matrix = self._R_functions.model_eval(pred, test.rx2('relevant'), -1, 1)

    def save_model(self, filename):
        """Saves :class:`JobAdClassification` instance model to file for later use.

        Arguments
        ----------
        filename : str
            Name of file to save model in.
        """

        self._R_functions.saveFile(self._RFmodel, filename)
        
    def load_model(self, filename):
        """Loads random forest classification model from file.

        Model is stored in :class:`JobAdClassification` instance.

        Arguments
        ----------
        filename : str
            Name of file to load model from.
        """

        self._RFmodel = robjects.r['get'](robjects.r['load'](filename))


    def classify_ads(self, job_ads):
        """Provides recommendations for ads using instance model.

        Arguments
        ----------
        ads : list
            List of dictionaries of job ads. Each dictionary should contain
            keys for id, site, searchterm, title, description (see :class:`JobAdDB`
            description for details).

        Returns
        ----------
        results : list
            List of dictionaries of job ads. Each ad contains keys for id and
            recommendation.
        """
        #convert to dataframe and clean ads
        dataf = self.create_R_dataframe(job_ads, self._class_columns)
        ids = dataf.rx2('id') 
        dataf = self._R_functions.cleanJobAds(dataf, StrVector(self._search_terms), 
                                              StrVector(self._sites))
        dataf = self._R_functions.createJoinDTM(dataf, self._language.lower())
        dataf = self._R_functions.prepNewAds(self._RFmodel, dataf)

        #classify ads
        pred = self._R_functions.RFpred(self._RFmodel, dataf)

        #combine predictions with ids in a list of dictionaries
        results = [{"id" : ids[i], "recommendation": int(pred[i])-1} 
                   for i in range(0, robjects.r['length'](ids)[0])]
                           
        return results
        

    def _determine_lang(self, title, description):
        """
        Tries to determine which language a job ad is using the textcat package. 
        Only differentiates between Finnish and English; returns English if another
        language is recognized.

        Arguments
        ----------
        title : str
            Title of job ad.
        description : str
            Description of job ad.
        Returns
        ----------
        language : str
            Determined language of job ad.
        """
        language_both = self._loaded_packages["textcat"].textcat(
            " ".join([title, description])).r_repr().replace("\"", "")
        language_title = self._loaded_packages["textcat"].textcat(title).r_repr().replace("\"", "")
        language_descrip = self._loaded_packages["textcat"].textcat(
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

        Arguments
        ----------
        ads : list
            List of dictionaries of job ads. Each dictionary should contain 
            keys for id, title and description.
        Returns
        ----------
        results : list
            List of dictionaries of job ads. Each ad contains keys for id and
            language.
        """

        results = [{"id": ad["id"], 
                    "language": self._determine_lang(ad["title"], ad["description"])}
                   for ad in ads]

        return results

