import re
from threading import Thread
from threading import Lock

from pysourcecodesec import logger
from pysourcecodesec import raw_dir
from pysourcecodesec import processed_dir

def num_of_strings(line):
    singles = 0
    doubles = 0
    for i in line:
        if i == '"':
            doubles += 1
        if i == "'":
            singles += 1
    if singles % 2 == 1:
        singles -= 1
    if doubles % 2 == 1:
        doubles -= 1
    return int(singles / 2 + doubles / 2)

def cred_vars_present(line):
    keywords = {
        "pass",
        "p@ass",
        "pwd",
        "login",
        "user",
        "acct",
        "account",
        "email",
        "e-mail",
        "name",
        "credentials"
    }
    for keyword in keywords:
        if len(keyword) > len(line):
            continue
        for i in range(0, len(line) - len(keyword) + 1):
            if line[i:i+len(keyword)].lower() == keyword:
                return 1
    return 0

def wordcount(line):
    return len(line.split())

def open_present(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "open(":
            return 1
    return 0

def popen_present(line):
    if len(line) < 7:
        return 0
    for i in range(0, len(line) - 5):
        if line[i:i+6] == "popen(":
            return 1
    return 0

def system_present(line):
    if len(line) < 8:
        return 0
    for i in range(0, len(line) - 6):
        if line[i:i+7] == "system(":
            return 1
    return 0

def exec_present(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "exec(":
            return 1
    return 0

def eval_present(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "eval(":
            return 1
    return 0

def input_present(line):
    if len(line) < 7:
        return 0
    for i in range(0, len(line) - 5):
        if line[i:i+6] == "input(":
            return 1
    return 0

def hardcoded_address_present(line):
    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
    if len(ip) > 0:
        return 1
    return 0

def parses_yaml(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "load(" or line[i:i+4] == "yaml" or line[i+1:i+5] == "yaml":
            return 1
    return 0

def is_conditional(line):
    line = line.strip()
    if line[0:2] == "if" or line[0:5] == "while" or line[0:4] == "elif" or line[0:3] == "else":
        return 1
    return 0

def num_of_invocations(line):
    inv = 0
    for i in range(len(line)):
        if line[i] == '(':
            if i == 0:
                continue
            print("here")
            if line[i-1] != ' ' and line[i-1] != '=':
                inv += 1
    return inv

features = {
    0:num_of_strings,
    1:cred_vars_present,
    2:wordcount,
    3:open_present,
    4:popen_present,
    5:system_present,
    6:exec_present,
    7:eval_present,
    8:input_present,
    9:hardcoded_address_present,
    10:parses_yaml,
    11:is_conditional,
    12:num_of_invocations
}

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

