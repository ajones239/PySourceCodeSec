import os
import logging
import sys
from threading import Lock

log_file = 'events.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Initialized logging")

# contains GitHub login credentials. Comments start with '#' and must be the first character on the line, 
#   must define 'user' and 'pwd'. Don't include quotes or leading/trailing spaces
#   Ex)
#   user=myusername
#   pwd=my password
github_credentials = 'creds.conf' 

# raw_dir specifies the directory to load raw unformatted Python sample files fetched from the fetch_tool
raw_dir = "data/raw/" 
processed_file = "/home/user/dev/PySourceCodeSec/data/processed.csv"
raw_write_file = ""
raw_lock = Lock()


def main():
    '''
    Displays the main menu to select a given tool for use.
    '''
    flags = {       # flags are either true or false
        "-i": False, # interactive mode
        "-h": False, # display help
        "-c": False, # create model
        "-e": False, # load saved models
        "-s": False, # save created models to disk
        "-l": False, # start labeller
        "-t": False, # start fetch tool
        "-r": False  # recursively scan files in a directory
    }
    options = {     # options have an argument passed after the option flag
        "-a": None, # algorithm 
        "-f": None # file to analyze
    }

    if len(sys.argv) == 1:
        flags["-h"] = True
    skip = False
    for i in range(len(sys.argv)):
        if i == 0 or skip:
            skip = False
            continue
        if sys.argv[i] in flags:
            flags[sys.argv[i]] = True
        elif sys.argv[i] in options:
            options[sys.argv[i]] = sys.argv[i+1]
            skip = True
        else:
            err = sys.argv[i] + " is not a valid option"
            logger.error(err)
            print(err)
            sys.exit(1)

    if flags["-h"]:
        print("USAGE: ./pysourcecodesec.sh [options]")
        print("\t-i\tinteractive mode")
        print("\t-h\tdisplay this message and exit")
        print("\t-c\tcreate new model")
        print("\t-e\tload existing saved models")
        print("\t-s\tsave created models to disk")
        print("\t-l\tstart sample labeller")
        print("\t-t\tstart sample fetch tool")
        print("\t-r\tscan directories recursively")
        print("\t-a <algorithm>\talgorithm should be one of: nn (for Keras neural network), lr (for logistic regression). Default is nn")
        print("\t-f <path>\tpath to file or directory to scan")
        print("Note: certain options are incompatible with others. '-h' supersedes any other options. '-i' supersedes all but '-h'.")
        print("\tIf both '-e' and '-c' are passed, models are loaded if they exist. If not, new ones are created.")
        print("PYTHON_ENV environment variable can be set to specify which Python executable to use. Default is system version.")
        sys.exit(0)
    if flags["-i"]:
        main_prompt()
        sys.exit(0)
    bgtools = list()
    if flags["-l"]:
        from labeller.labeller import Labeller
        bgtools.append(Labeller())
    if flags["-t"]:
        from fetch_tool.fetch_tool import FetchTool       
        bgtools.append(FetchTool())
    try:
        if flags["-e"] or flags["-c"] or flags["-s"] or options["-f"] != None:
            from ml.ml_manager import MLManager
            from ml.status import ModelStatus
            from ml.ml_exception import MLException
            manager = MLManager()
            if options["-a"] == "lr":
                algorithm = "logistic regression"
            elif options["-a"] == "nn" or options["-a"] == None:
                algorithm = "Keras neural network"
            else:
                print(options["-a"] + " is not a valid algorithm")
                sys.exit(1)
            if flags["-c"]:
                print("Creating " + algorithm + " model...")
                manager.create_model(algorithm)
                if flags["-s"]:
                    while manager.status(algorithm) != ModelStatus.COMPLETED:
                        pass
                    manager.save_models(algorithm)
            if flags["-e"]:
                try:
                    manager.load_models()
                except MLException:
                    print("Error: unable to load models")
            if options["-f"] != None:
                try:
                    files = list()
                    if os.path.isdir(options["-f"]):
                        files = collect_file_paths(options["-f"], flags["-r"])
                    elif os.path.isfile(options["-f"]):
                        print("2")
                        files.append(options["-f"])
                    else:
                        print("Error: no such file or directory: " + options["-f"])
                    for f in files:
                        analyze_file_or_directory(manager, f, algorithm)
                except MLException:
                    print("Error: no model exists. Try running with '-e' to load existing models or '-c' to create a new one")
        if len(bgtools) != 0:
            for tool in bgtools:
                print("Starting " + tool.name + "...")
                tool.start()
            print("Running...Ctrl-c to quit")
            while True:
                pass
    except KeyboardInterrupt: 
        for tool in bgtools:
            print("Stopping " + tool.name + "...")
            tool.stop()
       
def collect_file_paths(path, recurse):
    ret = list()
    for f in os.listdir(path):
        if os.path.isdir(path + "/" + f):
            if recurse:
                dat = collect_file_paths(path + "/" + f, True)
                for val in dat:
                    ret.append(val)
        elif f.split('.')[-1] == "py":
            ret.append(path + "/" + f)
    return ret

def main_prompt():
    from fetch_tool.fetch_tool import FetchTool
    from labeller.labeller import Labeller
    from ml.ml_manager import MLManager

    sample_fetcher = FetchTool()
    sample_labeller = Labeller()
    ml_manager = MLManager()
    cmds = {
        "1": fetch_tool_prompt,
        "2": labeller_prompt,
        "3": ml_prompt
    }
    args = {
        "1": sample_fetcher,
        "2": sample_labeller,
        "3": ml_manager
    }
    while True:
        print("What would you like to manage?")
        print("(1) sample fetch tool")
        print("(2) sample labeller")
        print("(3) machine learning models")
        print("(q) quit")
        cmd = input("cmd: ")
        cmd = cmd.strip()
        if cmd == "q":
            print("quiting...")
            sample_fetcher.stop()
            sample_labeller.stop()
            ml_manager.stop()
            break
        try:
            cmds[cmd](args[cmd])
        except KeyError:
            print("Sorry, {} does not correspond to a valid command.\n".format(cmd))


def fetch_tool_prompt(fetcher):
    '''
    Shows commands for use with the project fetch tool.
    '''
    cmds = {
        "1": fetcher.start,
        "2": fetcher.stop,
        "3": fetcher.status,
        "4": lambda : fetcher.set_search_term(input("Enter new search term: ")),
        "5": lambda : print("Current search term: " + fetcher.search_term)
    }
    while True:
        print("\nSample Fetch Tool")
        print("(1) start")
        print("(2) stop")
        print("(3) status")
        print("(4) update search term")
        print("(5) print current search term")
        print("(6) back")
        try:
            cmd = input("cmd: ")
            cmd = cmd.strip()
            cmds[cmd]()
        except KeyError:
            if cmd == "6":
                break
            print("Sorry, {} does not correspond to a valid command.".format(cmd))
    print()


def labeller_prompt(labeller):
    '''
    Shows commands for use with the labeller tool.
    '''
    cmds = {
        "1": labeller.start,
        "2": labeller.stop,
        "3": labeller.status
    }
    while True:
        print("\nSample Labeller")
        print("(1) start")
        print("(2) stop")
        print("(3) status")
        print("(4) back")
        try:
            cmd = input("cmd: ")
            cmd = cmd.strip()
            cmds[cmd]()
        except KeyError:
            if cmd == "4":
                break
            print("Sorry, {} does not correspond to a valid command.".format(cmd))
    print()
            
def analyze_file_or_directory(ml_manager, path, algorithm):
    from ml.ml_exception import MLException
    output = {
        "calling_external_function":"command injection",
        "hardcoded_information":"hardcoded credential"
    }
    try:
        files = list()
        if os.path.isdir(path):
            for f in collect_file_paths(path, True):
                files.append(f)
        else:
            files.append(path)
        for f in files:
            print("Analyzing " + f)
            results = ml_manager.analyze_file_with_model(f, algorithm)
            found = False
            for i in range(len(results)):
                if len(results[i]) != 0:
                    found = True
                    for vuln in results[i]:
                        print("Possible {} vulnerability on line {}".format(output[vuln], i))
            if not found:
                print("No vulnerabilities found in " + f)
    except MLException:
        err = "Cannot analyze file: there is no existing model"
        print(err)
        logger.error(err)
        return
    except FileNotFoundError:
        err = "Can not open file: no such file or directory"
        print(err)
        logger.error(err)
        return


def algorithm_prompt(ml_manager, algorithm):
    '''
    Shows commands for use with the ML model training tool.
    '''
    cmds = {
        "1": ml_manager.status,
        "2": ml_manager.create_model,
        "3": analyze_file_or_directory
    }
    while True:
        print("\n{} model".format(algorithm))
        print("(1) status")
        print("(2) create model")
        print("(3) analyze file or directory")
        print("(4) back")
        try:
            cmd = input("cmd: ")
            cmd = cmd.strip()
            if cmd == "3":
                f = input("Enter file or directory: ")
                analyze_file_or_directory(ml_manager, f, algorithm)
            elif cmd == "4":
                break
            else:
                cmds[cmd](algorithm)
        except KeyError:
            print("Sorry, {} does not correspond to a valid command.".format(cmd))


def ml_prompt(ml_manager):
    '''
    Commands for managing machine learning models.
    '''
    from ml.ml_manager import algorithms
    cmds = {
        "1": algorithm_prompt,
        "2": algorithm_prompt,
        "3": ml_manager.save_models,
        "4": ml_manager.load_models
    }
    while True:
        print("\nWhich model would you like to manage?")
        print("(1) logistic regression")
        print("(2) Keras neural network")
        print("(3) Save existing models to disk")
        print("(4) Load saved models")
        print("(5) back")
        try:
            cmd = input("cmd: ")
            cmd = cmd.strip()
            if cmd == "3" or cmd == "4":
                cmds[cmd]()
            else:
                cmds[cmd](ml_manager, algorithms[int(cmd) - 1])
        except RecursionError:
            print("FDFDS")
        # except KeyError:
        #     if cmd == "5":
        #         break
        #     print("Sorry, {} does not correspond to a valid command.".format(cmd))
        # except ValueError:
        #      print("Sorry, {} does not correspond to a valid command.".format(cmd))           
    print()
 

 

if __name__ == '__main__':
    main()
