import csv
from sklearn import linear_model
from numpy import array,delete,ravel

# import numpy as np
# from scipy import optimize
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn import metrics

from pysourcecodesec import logger
from ml.status import ModelStatus
from ml.ml_model import MLModel
from ml.exception import 
from labeller.features import num_of_classes
from labeller.features import num_of_features
from labeller.features import classes

class LogisticRegressionModel(MLModel):

    def __init__(self, datafile=None):
        super().__init__(datafile)
        self.models = list() # list of ("name", model) tuples

    def __train(self):
        with open(self.datafile) as f:
            dataset = array(list(csv.reader(f, delimiter=',')))
        dataset = delete(dataset,0,0)
        x = delete(dataset,0,1)
        y = delete(dataset, range(num_of_features), 1)
        for c in classes: # does binary logistic regression for each class/label
            model = linear_model.LogisticRegression()
            y_t = y.copy()
            for i in range(len(y_t)):
                if y_t[i] == c:
                    y_t[i] = 1
                else:
                    y_t[i] = 0
            model.fit(x, ravel(y_t))
            self.models.append((c, model))
            self.__set_status(ModelStatus.COMPLETED)

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
        load_model takes the summary created by get_model to load an already created model
        '''
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
        classify takes a list of features (number type) in the order they appear in the dataset and uses the existing model to classify the data
        returns a list of (class name, is in class) tuples
        raises RuntimeError when no models have been loaded or created, or when the model is currently being trained
        '''
        if self.get_status() == ModelStatus.NOT_CREATED:
            raise RuntimeError("Cannot classify. No logistic regression models have been created or loaded.")
        elif self.get_status() == ModelStatus.TRAINING:
            raise RuntimeError("Cannot classify: The logistic regression model is being created.")
        ret = list()
        if type(self.models[0]) == type(list()): # case where models were loaded. format is name,coeficients,bias
            for model in self.models:
                s = model[len(model) - 1] # bias
                for i in range(1, len(features) - 1):
                    s += model[i+1] * features[i] # model is i+1 b/c model[0] is its class
                ret.append((model[0], s > 0.5))
        else: # case where models were created. format is (class, model object)
            for model in self.models:
                s = model[1].intercept_
                for i in range(len(model[1].coef_[0])):
                    s += model[1].coef_[0][i] * features[i]
                ret.append((model[0], s > 0.5))
        return ret
