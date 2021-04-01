from threading import Thread
from threading import Lock

from pysourcecodesec import logger
from pysourcecodesec import raw_dir
from pysourcecodesec import processed_dir

class Labeller(Thread):

    def __init__(self):
        self.tname = "sample labeller"
        self.stop_lock = Lock()
        self.running = False
        super().__init__(target=self.__run_labeller)

    
    def start(self):
        logger.info("Starting labeller...")
        self.running = True
        super().start()
        logger.info("Labeller successfully started.")


    def stop(self):
        logger.info("Stopping labeller...")
        self.stop_lock.acquire()
        self.running = False
        self.stop_lock.release()
        self.join()
        logger.info("Labeller successfully stopped.")


    def status(self):
        if self.running:
            print("Sample labeller is running")
        else:
            print("Sample labeller is stopped")


    def __run_labeller(self):
        done = False
        while not done:

            self.stop_lock.acquire()
            if not self.running:
                done = True
            self.stop_lock.release()

