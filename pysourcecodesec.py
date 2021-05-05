import logging
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
processed_file = "data/processed_small.csv"
raw_write_file = ""
raw_lock = Lock()

from fetch_tool.fetch_tool import *
from labeller.labeller import *
from ml.ml_manager import *

def main():
    '''
    Displays the main menu to select a given tool for use.
    '''
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
            

def algorithm_prompt(ml_manager, algorithm):
    '''
    Shows commands for use with the ML model training tool.
    '''
    cmds = {
        "1": ml_manager.status,
        "2": ml_manager.create_model,
        "3": lambda manager : manager.analyze_file_with_model(input("Enter filename: ").strip(), algorithm)
    }
    while True:
        print("\n{} model".format(algorithm))
        print("(1) status")
        print("(2) create model")
        print("(3) analyze (file or directory")
        print("(4) back")
        try:
            cmd = input("cmd: ")
            cmd = cmd.strip()
            if cmd == "1" or cmd == "2":
                cmds[cmd](algorithm)
            else:
                cmds[cmd](ml_manager)
        except KeyError:
            if cmd == "4":
                break
            print("Sorry, {} does not correspond to a valid command.".format(cmd))


def ml_prompt(ml_manager):
    '''
    Commands for managing machine learning models.
    '''
    cmds = {
        "1": algorithm_prompt,
        "2": algorithm_prompt
    }
    while True:
        print("\nWhich model would you like to manage?")
        print("(1) logistic regression")
        print("(2) Keras neural network")
        print("(3) back")
        try:
            cmd = input("cmd: ")
            cmd = cmd.strip()
            cmds[cmd](ml_manager, algorithms[int(cmd) - 1])
        except KeyError:
            if cmd == "3":
                break
            print("Sorry, {} does not correspond to a valid command.".format(cmd))
        except ValueError:
             print("Sorry, {} does not correspond to a valid command.".format(cmd))           
    print()
 

 

if __name__ == '__main__':
    main()
