import os
import time
from threading import Thread
from threading import Lock

from pysourcecodesec import logger
from pysourcecodesec import raw_dir
from pysourcecodesec import processed_file
from pysourcecodesec import raw_lock
from pysourcecodesec import raw_write_file
from labeller.features import features
from labeller.features import csv_header
from labeller.features import bandit_cmd
from labeller.features import labels

class Labeller():

    def __init__(self):
        self.name = "sample labeller"
        self._processed_files = set()
        self._stop_lock = Lock()
        self._running = False
        if not os.path.isfile(processed_file):
            with open(processed_file, 'x') as f:
                f.write(csv_header + '\n')
        else:
            with open(processed_file,'r+') as f:
                content = f.read()
                if content.split('\n')[0] != csv_header:
                    f.seek(0,0)
                    f.write(csv_header + '\n' + content)
        self._label_thread = Thread(target=self._run_labeller)

    
    def start(self):
        logger.info("Starting labeller...")
        self._running = True
        self._label_thread.start()
        logger.info("Labeller successfully started.")


    def stop(self):
        logger.info("Stopping labeller...")
        self._stop_lock.acquire()
        self._running = False
        self._stop_lock.release()
        if self._label_thread.is_alive():
            self._label_thread.join()
            self._label_thread = Thread(target=self._run_labeller) #Reinitialize thread
        logger.info("Labeller successfully stopped.")


    def status(self):
        if self._running:
            print("Sample labeller is running")
        else:
            print("Sample labeller is stopped")

    def _select_file(self):
        '''
        Selects a given file from a project to scan for vulnerabilities.
        '''
        var = None
        raw_lock.acquire()
        for f in os.listdir(raw_dir):
            if f not in self._processed_files and f != raw_write_file:
                self._processed_files.add(f)
                var = f
                break
        raw_lock.release()
        return var

    def _write_to_csv(self, src, label):
        '''
        Writes the labeled vulnerabilities to a targeted CSV file for review and analysis.
        '''
        out = ""
        for feature in features:
            out += str(features[feature](src)) + ","
        out += label + "\n"
        with open(processed_file, 'a') as f:
            f.write(out)

    def _is_white_space(self, line):
        if len(line) == 0:
            return True
        for c in line:
            if c != " " and c != "\t":
                return False
        return True

    def _run_labeller(self):
        '''
        Takes the given files and labels any vulnerabilities found inside, based on the list of 
        Bandit test modules. Uploads the results to a CSV via _write_to_csv.
        '''
        done = False
        while not done:
            fname = self._select_file()
            if fname is None:
                time.sleep(2) # if no files in data/raw are unprocessed, wait and try again
                continue
            with open(raw_dir + fname) as r_file:
                try:
                    data = r_file.readlines()
                except:
                    continue
                bandit_output = os.popen(bandit_cmd + " " + raw_dir + fname).read().split('\n') # this likely will not work on windows
            for i in range(len(data)):                                                              # because raw_dir likely uses '/' over '\'
                if self._is_white_space(data[i]):
                    continue
                vuln_code = "none"
                for vuln in bandit_output:
                    try:
                        if int(vuln.split(':')[1]) == i+1:
                            vuln_code = vuln.split(':')[2]
                            break
                    except IndexError:
                        continue
                self._write_to_csv(data[i], labels[vuln_code])
            self._stop_lock.acquire()
            if not self._running:
                done = True
            self._stop_lock.release()

