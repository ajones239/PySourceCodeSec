import csv
from sklearn import linear_model
from numpy import array,delete,ravel
from threading import Thread, Lock

from pysourcecodesec import logger
from ml.status import ModelStatus
from ml.ml_model import MLModel
from ml.ml_exception import MLException
from labeller.features import num_of_features
from labeller.features import classes

class LogisticRegressionModel(MLModel):

    def __init__(self, datafile=None):
        super().__init__()
        self.datafile = datafile
        self.models = list() # list of ("name", model) tuples
        self.name = "logistic regression"
        self.__status = ModelStatus.NOT_CREATED
        self.__status_lock = Lock()
        self.__trainingThread = Thread(target=self.__train)

    def get_status(self):
        '''
        get_status returns the current status of the model
        '''
        self.__status_lock.acquire()
        x = self.__status
        self.__status_lock.release()
        return x
    
    def __set_status(self, status):
        self.__status_lock.acquire()
        self.__status = status
        self.__status_lock.release()

    def __train(self):
        '''
        __train is where the actual creation of the models happens
        for each class, a binary logistic regression model is created
        self.models is set to a list of (class as string, linear_model.LogisticRegression objects)
        '''
        logger.info("opening file")
        with open(self.datafile) as f:
            dataset = array(list(csv.reader(f, delimiter=',')))
        logger.info("1")
        dataset = delete(dataset,0,0)
        logger.info("2")
        x = delete(dataset,0,1)
        logger.info("3")
        y = delete(dataset, range(num_of_features), 1)
        logger.info("4")
        del(dataset)
        for i in range(len(x)):
            for j in range(len(x[0])):
                try:
                    t = float(x[i][j])
                except ValueError:
                    x[i][j] = '0'
        for c in classes: # does binary logistic regression for each class/label
            if c == "none":
                continue
            logger.info("Creating logistic regression model for class " + c)
            model = linear_model.LogisticRegression()
            y_t = y.copy()
            logger.info("copied")
            allZeroes = True
            for i in range(len(y_t)):
                if y_t[i] == c:
                    y_t[i] = "1"
                    allZeroes = False
                else:
                    y_t[i] = "0"
            logger.info("formatted y_t")
            if not allZeroes:
                model.fit(x, ravel(y_t))
                self.models.append((c, model))
                self.__set_status(ModelStatus.COMPLETED)
            else:
                logger.error("No data points in class " + c)

    def train(self):
        '''
        train starts a thread to train the model and sets status appropriately
        '''
        self.__set_status(ModelStatus.TRAINING)
        logger.info("training started")
        self.__trainingThread.start()

    def get_model(self):
        '''
        get_model returns string summary of all models
            format: number of models:model 1:model 2:...:modeln
            model i: class name,coeficient 1,coeficient 2,...,coeficient k,bias,
            k is the number of features in the model
        '''
        if len(self.models) == 0:
            return "0:"
        r = str(len(self.models)) + ":"
        for model in self.models:
            for val in model[1].coef_[0]:
                r += str(val) + ","
            r += model[1].intercept_ + ":"
        return r

    def load_model(self, st):
        '''
        load_model loads an already created model
        takes the string created by get_model as a parameter
        '''
        # sets self.models to a list of model parameters of type float
        #    model parameter format: name, coeficients (one per feature), bias/intercept
        models = st.split(':')
        if models[0] == "0": # loading 0 models, nothing to do
            return
        for model in models:
            m = model.split(',')
            self.models.append(m[0])
            for i in range(1, len(m)):
                m[i] = float(m[i])
            self.models.append(m)
            self.__set_status(ModelStatus.COMPLETED)

    def classify(self, features):
        '''
        classifies a set of features
        takes a list of features (number type) in the order they appear in the dataset 
        returns a list of model labels/classes (type string) that apply to the given features
        raises MLException when no models have been loaded or created, or when the model is currently being trained
        '''
        if self.get_status() == ModelStatus.NOT_CREATED:
            raise MLException("Cannot classify. No logistic regression models have been created or loaded.")
        elif self.get_status() == ModelStatus.TRAINING:
            raise MLException("Cannot classify: The logistic regression model is being created.")
        ret = list()
        if type(self.models[0]) == type(list()): # case where models were loaded. model format is name,coeficients,bias
            for model in self.models:
                s = model[len(model) - 1] # bias
                for i in range(1, len(features) - 1):
                    s += model[i+1] * features[i] # model is i+1 b/c model[0] is its class
                if s > 0.5:
                    ret.append(model[0])
        else: # case where models were created. models are type linear_model.LogisticRegression
            for model in self.models:
                s = model[1].intercept_
                for i in range(len(model[1].coef_[0])):
                    s += model[1].coef_[0][i] * features[i]
                if s > 0.5:
                    ret.append(model[0])
        return ret
