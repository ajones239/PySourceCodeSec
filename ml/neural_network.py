import pandas
import numpy
from keras.models import Sequential
from keras.layers import Dense
from sklearn import metrics
from sklearn.model_selection import train_test_split
from threading import Thread, Lock

from pysourcecodesec import logger
from ml.status import ModelStatus
from ml.ml_model import MLModel
from ml.ml_exception import MLException
from labeller.features import num_of_features
from labeller.features import classes

class KerasNeuralNetworkModel(MLModel):

    def __init__(self, datafile=None):
        super().__init__()
        self.datafile = datafile
        self.models = list()
        self.name = "Keras neural network"
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
        dataset = pandas.read_csv(self.datafile, header=0).values
        X = dataset[:,0:13].astype(float)
        Y = dataset[:, 13]
        for c in range(len(classes)):
            if c == 0:
                continue
            Y_t = Y.copy()
            for i in range(len(Y_t)):
                if Y_t[i] == classes[c]:
                    Y_t[i] = 1
                else:
                    Y_t[i] = 0
            Y_t = numpy.ravel(Y_t.astype(float))
            model = Sequential()
            model.add(Dense(20, input_dim=13, activation='relu'))
            model.add(Dense(13, activation='relu'))
            model.add(Dense(1, activation='sigmoid'))
            model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
            model.fit(X, Y_t, epochs=500, batch_size=10, verbose=0)
            self.models.append((classes[c], model))

            self.__set_status(ModelStatus.COMPLETED)

    def train(self):
        '''
        train starts a thread to train the model and sets status appropriately
        '''
        self.__set_status(ModelStatus.TRAINING)
        logger.info("training started")
        self.__trainingThread.start()

    def __save_model(self):
        for i in range(len(models)):
            self.models[i].save('.nn_model_'+str(i+1)+'.h5')

    def get_model(self):
        '''
        get_model returns string summary of all models
            summary is the amount of models saved
            each saved model is saved as the file '.nn_model_i.h5' where i is the ith model saved (1-n)
        '''
        self.__save_model()
        return str(len(self.models))

    def load_model(self, count):
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
            raise MLException("Cannot classify. No neural network has been created or loaded.")
        elif self.get_status() == ModelStatus.TRAINING:
            raise MLException("Cannot classify: The neural network is being created.")
        ret = list()
        for model in self.models:
            predictions = model[1].predict(numpy.array([features]))
            ret.append((model[0], predictions[0]))
        return ret

