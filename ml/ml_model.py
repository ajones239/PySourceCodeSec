from abc import ABC,abstractmethod

class MLModel(ABC):

    def _init__(self):
        super().__init__()

    @abstractmethod
    def get_status(self):
        '''
        get_status returns the current status of the model
        '''
        pass
   
    @abstractmethod
    def train(self):
        '''
        train starts a thread to train the model and sets status appropriately
        '''
        pass

    @abstractmethod
    def get_model(self):
        '''
        get_model should return a file-writable summary of the model/model parameters
        if a MLModel implements its own method for saving models, it should return a placeholder string
        '''
        pass

    @abstractmethod
    def load_model(self, st):
        '''
        load_model loads an already created model
        takes the string created by get_model as a parameter
        '''
        pass

    @abstractmethod
    def classify(self, features):
        '''
        classify classifies a set of features based on the current model
        takes a list of features (number type)
        '''
        pass

