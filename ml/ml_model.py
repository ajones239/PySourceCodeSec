from abc import ABC,abstractmethod
from threading import Lock
from threading import Thread
from ml.status import ModelStatus

class MLModel(ABC):
# class MLModel():

    def __init__(self):
        super().__init__()

    def get_status(self):
        '''
        get_status returns the current status of the model
        '''
        pass
    
    def __set_status(self, status):
        pass

    def train(self):
        '''
        train starts a thread to train the model and sets status appropriately
        '''
        pass

    # @abstractmethod
    def __train(self):
        pass

    # @abstractmethod
    # def get_metrics(self):
    #     pass

    # @abstractmethod
    def get_model(self):
        '''
        get_model should return a file-writable summary of the model/model parameters
        '''
        pass

    # @abstractmethod
    def load_model(self, st):
        '''
        load_model loads an already created model
        takes the string created by get_model as a parameter
        '''
        pass

    # @abstractmethod
    def classify(self, features):
        '''
        classify classifies a set of features based on the current model
        takes a list of features (number type)
        '''
        pass

