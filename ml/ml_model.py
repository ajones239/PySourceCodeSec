from abc import ABC
from ml.status import ModelStatus
from threading import Lock
from threading import Thread
from pandas import read_csv


class MLModel(ABC):

    def __init__(self, datafile):
        self.__dataset = read_csv(dataset)
        self.__status = ModelStatus.NOT_CREATED
        self.__status_lock = Lock()
        self.__trainingThread = Thread(target=self.__train())

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

    def train(self):
        '''
        train starts a thread to train the model, sets status, and then returns control
        '''
        self.__set_status(ModelStatus.TRAINING)
        self.__trainingThread.start()

    @abstractmethod
    def __train(self):
        pass

    @abstractmethod
    def get_metrics(self):
        pass

    @abstractmethod
    def get_model(self):
        '''
        get_model should return a file-writable summary of the model/model parameters
        '''
        pass

    @abstractmethod
    def load_model(self):
        '''
        load_model takes the summary created by get_model to load an already created model
        '''
        pass

    @abstractmethod
    def classify(self, features):
        '''
        classify takes a list of features and uses the existing model to classify the data
        '''
        pass

