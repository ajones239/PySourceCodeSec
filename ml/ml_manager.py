from ml.status import ModelStatus
import os
from pysourcecodesec import logger
from pysourcecodesec import processed_file
from ml.logistic_regression import LogisticRegressionModel
from ml.neural_network import KerasNeuralNetworkModel
from ml.ml_model import MLModel
from ml.ml_exception import MLException
from labeller.features import features

saveFile = ".ml_algorithms.save"
algorithms = ["logistic regression", "Keras neural network"]

class MLManager():
    
    def __init__(self):
        self.algorithms = {
            "logistic regression":LogisticRegressionModel,
            "Keras neural network":KerasNeuralNetworkModel
        }

    def _has_algorithm(self, alg):
        '''
        returns true self.algorithms[alg] is not None
        raises MLException if self.algorithms[alg] does not exist
        '''
        try:
            if isinstance(self.algorithms[alg], MLModel):
                return True
            else:
                return False
        except KeyError:
            raise MLException("There is no algorithm with the name " + alg)

    def create_model(self, alg):
        '''
        generates a model of using the algorithm passed as a parameter
        '''
        if self._has_algorithm(alg):
            err = alg + " model already exists"
            logger.error(err)
            print(err)
        else:
            logger.info("Creating model using algorithm " + alg)
            self.algorithms[alg] = self.algorithms[alg](processed_file)
            logger.info("Beginning training")
            self.algorithms[alg].train()

    def load_models(self):
        '''
        attempts to load models from previous sessions that were saved
        '''
        try:
            with open(saveFile, 'r') as f:
                saved = f.readlines()
            for line in saved:
                name = line.split(';')[0]
                config = line.split(';')[1]
                logger.info("Loading " + name + " model")
                try:
                    if self._has_algorithm(name):
                        logger.error("Can not load " + name + " model, there is already a model of this algorithm.")
                    else:
                        self.algorithms[name] = self.algorithms[name]()
                        self.algorithms[name].load_model(config)
                        logger.info(name + " model successfully loaded")
                except MLException:
                    logger.error("Can not load model: " + name + " does not correspond to a valid model name. Has the config been tampered with?")
        except FileNotFoundError:
            raise MLException("Unable to load the saved model config file.")
    
    def save_models(self):
        '''
        saves models in a config file on the filesystem
        '''
        from ml.ml_model import MLModel
        if not os.path.isfile(saveFile):
            f_t = open(saveFile, 'x')
            f_t.close()
        with open(saveFile, 'r+') as f:
            for alg in algorithms:
                if isinstance(self.algorithms[alg], MLModel):
                    f.write(alg + ';' + self.algorithms[alg].get_model()+'\n')
            f.truncate()
            
    def analyze_file_with_model(self, fname, model):
        '''
        analyzes a file using the given model
        takes name (string) of the file to analyze
        takes model (string) to use
        returns a dict of form {line number: list of labels for that line}
        '''
        if not isinstance(self.algorithms[model], MLModel):
            raise MLException(model + " model does not exist")
        with open(fname) as f:
            lines = f.readlines()
        ret = dict()
        for i in range(len(lines)):
            featureValues = list()
            for j in range(len(features)):
                featureValues.append(features[j](lines[i]))
            ret[i] = self.algorithms[model].classify(featureValues)
        return ret

    def analyze_file(self, fname):
        '''
        analyzes a file with every available model
        takes the name (string) of the file to analyze
        returns a dict of form {algorithm name: dict of form {line number, list of labels}}
        '''
        ret = dict()
        for a in algorithms:
            ret[a] = self.analyze_file_with_model(fname, a)
        return ret
            

    def status(self, algorithm, display=True):
        if self._has_algorithm(algorithm):
            status = self.algorithms[algorithm].get_status()
            if status == ModelStatus.NOT_CREATED:
                msg = algorithm + " model is not created"
            elif status == ModelStatus.TRAINING:
                msg = algorithm + " model is training"
            elif status == ModelStatus.COMPLETED:
                msg = algorithm + " model is completed"
        else:
            status = None
            msg = "There is no " + algorithm + " model"
        if display:
            print(msg)
        return status
