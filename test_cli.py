import logging
import sys
from threading import Lock

log_file = 'testevents.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Initialized logging")

from ml.ml_manager import *
import argparse
parser = argparse.ArgumentParser(description='Algorithm Testing Interface')

algo = sys.argv[2]
target_file = sys.argv[3]

def main():
    print(algo, target_file)

    ml_manager = MLManager()
    #ml_manager.load_models() need config file
    print(ml_manager.algorithms)

    


if __name__ == '__main__':
    main()