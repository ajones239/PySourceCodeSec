import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

from pysourcecodesec import logger
from ml.status import ModelStatus
from ml.ml_model import MLModel

class LogisticRegressionModel(MLModel):

    def __init__(self, datafile):
        super().__init__(datafile)
        X = dataset[['num_of_strings', 'cred_vars_present', 'wordcount', 'open_present', 'popen_present', 'system_present', 'exec_present', 'eval_present', 'input_present', 'hardcoded_address_present', 'parses_yaml', 'is_conditional', 'num_of_invocations']]
        Y = dataset[['vulnerability']]
        X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=0) 

    def __train(self):
        pass

    def get_model(self):
        '''
        get_model should return a file-writable summary of the model/model parameters
        '''
        pass

    def load_model(self):
        '''
        load_model takes the summary created by get_model to load an already created model
        '''
        pass

    def classify(self, features):
        '''
        classify takes a list of features and uses the existing model to classify the data
        '''
        pass

