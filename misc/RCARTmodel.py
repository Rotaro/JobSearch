import re
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.vectors import StrVector
from rpy2.robjects.packages import importr
import rpy2.robjects.packages as rpackages
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage as STAP 
import db_controls
import sqlite3

class R_environment:
    """
    Class for training and running a CART model in R.
    """

    #R function for cleaning text
    R_functions_str = """ 
        cleanText <- function(text, lang) {
            corpus = Corpus(VectorSource(text), 
                     readerControl = list(language=lang))
            corpus = tm_map(corpus, tolower)
            corpus = tm_map(corpus, PlainTextDocument)
            corpus = tm_map(corpus, removePunctuation)
            corpus = tm_map(corpus, removeWords, stopwords(lang))
            corpus = tm_map(corpus, stemDocument)
            return (DocumentTermMatrix(corpus))}
        CARTmodel <- function(train_data, minbucket=6) 
            {return (rpart(relevant ~ ., data=train_data, method='class', 
                     minbucket=minbucket))}
        RFmodel <- function(train_data) 
            {return (randomForest(relevant ~ ., data=train_data))}
        CVCARTmodel <- function(train_data) {
            colnames(train_data) = make.names(colnames(train_data))
            train_data$relevant = as.factor(make.names(train_data$relevant))
            tc = trainControl(method="cv", number=10, repeats=10, classProbs = TRUE,
                              summaryFunction = twoClassSummary)
            cpGrid = expand.grid(.cp=seq(0.01, 0.5, 0.01))
            return (train(relevant ~ ., data=train_data, method="rpart", 
                    trControl=tc, metric="ROC")) }
        CARTpredict <- function(CART_model, test_data) {
            colnames(test_data) = make.names(colnames(test_data))
            return (predict(CART_model, newdata=test_data))}
        confusionMatrix <- function(true_results, predictions, threshold) 
            {return (table(true_results, predictions >= threshold))}
        confusionMatrixClass <- function(true_results, predictions) 
            {return (table(true_results, as.data.frame(predictions) == "X1"))}
        splitTerms <- function(terms_data, bool) 
            {return (terms_data == bool)}
        """

    CARTmodel = None

    def __init__(self):
        #base R assets
        self.utils = rpackages.importr('utils')
        self.utils.chooseCRANmirror(ind=5)
        self.base = rpackages.importr('base')
        #local library path
        self.base._libPaths("C:/Users/SuperSSD/Documents/R/win-library/3.2")
        #change locale or R uses windows-1252 encoding for r_repr()
        robjects.r['Sys.setlocale']("LC_CTYPE", "C") 
        
        # import needed packages
        # words pre-processing:
        # tm           - Framework for text mining.
        # SnowballC    - Stemming.
        # textcat      - Determine language of text.
        # CART model:
        # rpart        - "Recursive partitioning for classification, regression and 
        #                survival trees."
        # rpart.plot   - Plotting of CART trees.
        # randomForest - Random forest method.
        # caret        - Classification And REgression Training. Used for cross
        #                validation.
        # proc         - UMM
        # Additional:
        # caTools      - Splitting data into training and test sets intelligently.
        needed_packages = ["tm", "SnowballC", "rpart", "rpart.plot", "caTools", 
                           "randomForest", "textcat", "caret", "pROC"]
        needed_packages = [x for x in needed_packages if not rpackages.isinstalled(x)]
        if len(needed_packages) > 0:
            self.utils.install_packages(StrVector(needed_packages))
        self.tm = rpackages.importr("tm")
        self.SnowballC = rpackages.importr("SnowballC")
        self.caTools = rpackages.importr("caTools")
        self.rpart= rpackages.importr("rpart")
        self.rpart_plot = rpackages.importr("rpart.plot")
        self.grDevices = rpackages.importr("grDevices")
        self.randomForest = rpackages.importr("randomForest")
        self.textcat = rpackages.importr("textcat")
        self.caret = rpackages.importr("caret")
        self.caret = rpackages.importr("pROC")
        self.R_functions = STAP(self.R_functions_str, "R_functions")


    def pre_process_words(self, text_list, language):
        """
        Cleans up text and calculates the frequency of words for use in 
        the CART model. Returns the results as a DocumentTermMatrix (R object).

        text_list   - List of strings containing words.
        language    - Language of text, needed to remove stop words.
        """
        dtm = self.R_functions.cleanText(StrVector(text_list), language)


        return dtm

    def determine_lang(self, title, description):
        """
        Tries to determine which language a text is using the textcat package. 
        Only differentiates between Finnish and English. Returns English if another
        language is recognized.

        document    - List of strings containing words.
        """
        language_both = self.textcat.textcat(
            " ".join([title, description])).r_repr().replace("\"", "")
        language_title = self.textcat.textcat(title).r_repr().replace("\"", "")
        language_descrip = self.textcat.textcat(
            description).r_repr().replace("\"", "")

        #English job titles with Finnish text is sometimes mistaken
        false_finnish = ["danish", "frisian", "middle_frisian"]

        if (language_both == "english" or language_both == "finnish"):
            return language_both
        elif (language_title == "english" or language_title == "finnish"):
            return language_title
        elif (language_descrip == "english" or language_descrip == "finnish"):
            return language_descrip
        elif (language_both in false_finnish or language_title in false_finnish or
                language_descrip in false_finnish):
            return "Finnish"
        else:
            return "English"

    def create_CART_model(self, dtm, relevant, low_freq=1, ad_part=1, split_ratio=0.7):
        """
        Creates CART model based on provided document term matrix. Data is split into 
        training and test set according to split_ratio. Returns the accuracy of the model
        and also the accuracy of a baseline model of the most common relevancy. 

        dtm         - Document term matrix (R Object) to create CART model for.
        low_freq    - Minimum amount of times words need to appear to be included
                      in the model.
        ad_part     - In how large a part of job ads included words have to appear. 
        split_ratio - Ratio used to split data into training and testing sets.
        """
        if ad_part != 1.0 and ad_part != 0.0:
            sparse_terms = self.tm.removeSparseTerms(dtm, ad_part)
        else:
            sparse_terms = dtm

        #need to create data frame with columns for each word and relevant.
        #rows are job ads
        #as.data.frame(as.matrix(sparse_terms))
        sparse_terms = robjects.r['as.matrix'](sparse_terms)
        sparse_terms = robjects.r['as.data.frame'](sparse_terms)
        print(robjects.r['rownames'](sparse_terms.r_repr()))
        #add classification column to data frame
        sparse_terms = robjects.r.cbind(sparse_terms, relevant=robjects.IntVector(relevant))
        #split into training and test
        #robjects.r['set.seed'](123)
        split = robjects.r['sample.split'](sparse_terms.rx2('relevant'), split_ratio)
        train = robjects.r['subset'](sparse_terms, self.R_functions.splitTerms(split, 'TRUE'))
        test = robjects.r['subset'](sparse_terms, self.R_functions.splitTerms(split, 'FALSE'))
        #create model
        #self.CARTmodel = self.R_functions.CARTmodel(train, 15) 
        self.CARTmodel = self.R_functions.CVCARTmodel(train)
        #self.CARTmodel = self.R_functions.RFmodel(train) 
        print(self.CARTmodel.r_repr())

        #self.grDevices.png(file="C:/Users/SuperSSD/Documents/R/file.png", width=512, height=512)
        #robjects.r['prp'](self.CARTmodel)
        #self.grDevices.dev_off()
        #try model on test set
        pred = self.R_functions.CARTpredict(self.CARTmodel, test)
        print(pred.r_repr())
        #conf_matrix = self.R_functions.confusionMatrix(test.rx2('relevant'), pred, 0.4)
        conf_matrix = self.R_functions.confusionMatrixClass(test.rx2('relevant'), pred)
        accuracy = (conf_matrix[0]+conf_matrix[3]) / (conf_matrix[0] + 
                        conf_matrix[1] + conf_matrix[2] + conf_matrix[3])
        baseline_accuracy = (conf_matrix[0]+conf_matrix[1]) / (conf_matrix[0] + 
                        conf_matrix[1] + conf_matrix[2] + conf_matrix[3])
        sensitivity = conf_matrix[3] / (conf_matrix[2] + conf_matrix[3])
        print("\tFALSE\tTRUE")
        print("0\t", conf_matrix[0], "\t", conf_matrix[1])
        print("1\t", conf_matrix[2], "\t", conf_matrix[3])
        print("model accuracy:\t\t%.2f" % accuracy)
        print("baseline accuracy:\t%.2f" % baseline_accuracy)
        print("sensitivity:\t\t%.2f" % sensitivity)
                    
if(__name__ == "__main__"):
    r = R_environment()
    db = db_controls.JobAdsDB("tmp.db")

    class_entries = db.get_classified_ads(language="English")

    entries_relevancy = []
    entries_title_descrip = []

    for class_entry in class_entries:
        
        title_description = " ".join(class_entry[0:3])
        title_description = re.sub("[Ää]","a", title_description)
        title_description = re.sub("[Öö]","o", title_description)
        title_description = re.sub("[Åå]","å", title_description)
        entries_relevancy.append(class_entry[4])
        entries_title_descrip.append(title_description)
        
    dtm = r.pre_process_words(entries_title_descrip, "English")
    r.create_CART_model(dtm, entries_relevancy, ad_part=1,split_ratio=0.8)
