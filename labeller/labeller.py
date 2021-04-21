import os
import time
import hashlib
from threading import Thread
from threading import Lock

from pysourcecodesec import logger
from pysourcecodesec import raw_dir
from pysourcecodesec import processed_file
from pysourcecodesec import raw_lock
from pysourcecodesec import processed_lock
from pysourcecodesec import raw_write_file
from labeller.features import features
from labeller.features import csv_header
from labeller.features import bandit_cmd

class Labeller(Thread):

    def __init__(self):
        self.processed_files = set()
        self.tname = "sample labeller"
        self.stop_lock = Lock()
        self.running = False
        if not os.path.isfile(processed_file):
            with open(processed_file, 'x') as f:
                f.write(csv_header + '\n')
        else:
            with open(processed_file,'r+') as f:
                content = f.read()
                if content.split('\n')[0] != csv_header:
                    f.seek(0,0)
                    f.write(csv_header + '\n' + content)
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

    def __select_file(self):
        var = None
        raw_lock.acquire()
        for f in os.listdir(raw_dir):
            if f not in self.processed_files and f != raw_write_file:
                self.processed_files.add(f)
                var = f
                break
        raw_lock.release()
        return var

    def __write_to_csv(self, src, label):
        out = ""
        for feature in features:
            out += str(features[feature](src)) + ","
        out += label + "\n"
        processed_lock.acquire()
        with open(processed_file, 'a') as f:
            f.write(out)
        processed_lock.release()

    def __is_white_space(self, line):
        if len(line) == 0:
            return True
        for c in line:
            if c != " " and c != "\t":
                return False
        return True

    def __get_label(self, code):
        labels = {
            "none":"none",
            "B102":"calling_external_function",
            "B104":"hardcoded_information",
            "B105":"hardcoded_information",
            "B106":"hardcoded_information",
            "B107":"hardcoded_information",
            "B108":"hardcoded_information",
            "B307":"calling_external_function",
            "B404":"calling_external_function",
            "B506":"loading_yaml",
            "B602":"calling_external_function",
            "B603":"calling_external_function",
            "B604":"calling_external_function",
            "B605":"calling_external_function",
            "B606":"calling_external_function",
            "B607":"calling_external_function",
            "B609":"calling_external_function",
        }
        return labels[code]

    def __run_labeller(self):
        done = False
        while not done:
            fname = self.__select_file()
            if fname is None:
                time.sleep(2) # if no files in data/raw are unprocessed, wait and try again
                continue
            with open(raw_dir + fname) as r_file:
                data = r_file.readlines()
                bandit_output = os.popen(bandit_cmd + " " + raw_dir + fname + "2> /dev/null").read().split('\n') # this likely will not work on windows
            for i in range(len(data)):
                if self.__is_white_space(data[i]):
                    continue
                vuln_code = "none"
                for vuln in bandit_output:
                    try:
                        if int(vuln.split(':')[1]) == i+1:
                            vuln_code = vuln.split(':')[2]
                            break
                    except IndexError:
                        continue
                self.__write_to_csv(data[i], self.__get_label(vuln_code))
            self.stop_lock.acquire()
            if not self.running:
                done = True
            self.stop_lock.release()

