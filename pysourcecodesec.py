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
processed_file = "data/processed.csv"
raw_write_file = ""
raw_lock = Lock()
processed_lock = Lock()

from labeller.labeller import *
from fetch_tool.fetch_tool import *


def main():
    sample_fetcher = FetchTool()
    sample_labeller = Labeller()
    cmds = {
        "1": fetch_tool_prompt,
        "2": labeller_prompt,
    }
    args = {
        "1": sample_fetcher,
        "2": sample_labeller
    }
    while True:
        main_prompt()
        cmd = input("cmd: ")
        if cmd == "q":
            print("quiting...")
            sample_fetcher.stop()
            break
        try:
            cmds[cmd](args[cmd])
        except KeyError:
            print("Sorry, {} does not correspond to a valid command.\n".format(cmd))

        '''
        if cmd == "f":
            sample_fetcher.start()
        elif cmd == "s":
            sample_fetcher.stop()
        '''


def update_fetch_tool_search_term(fetcher):
    new_term = input("Enter new search term: ")
    fetcher.set_search_term(new_term)
    
    
def fetch_tool_prompt(fetcher):
    while True:
        print("\nSample Fetch Tool")
        print("(1) start")
        print("(2) stop")
        print("(3) status")
        print("(4) update search term")
        print("(5) back")
        cmds = {
            "1": fetcher.start,
            "2": fetcher.stop,
            "3": fetcher.status,
            "4": update_fetch_tool_search_term
        }
        try:
            cmd = input("cmd: ")
            cmd = cmd.strip()
            if cmd == "4":
                cmds[cmd](fetcher)
            else:
                cmds[cmd]()
        except KeyError:
            if cmd == "b":
                break
            print("Sorry, {} does not correspond to a valid command.".format(cmd))
    print()


def labeller_prompt(labeller):
    while True:
        print("\nSample Labeller")
        print("(1) start")
        print("(2) stop")
        print("(3) status")
        print("(4) back")
        cmds = {
            "1": labeller.start,
            "2": labeller.stop,
            "3": labeller.status
        }
        try:
            cmd = input("cmd: ")
            cmds[cmd]()
        except KeyError:
            if cmd == "4":
                break
            print("Sorry, {} does not correspond to a valid command.".format(cmd))
    print()
            

#def machine_learning_prompt():
#    print("\nWhich model would you like to manage?")
#    print("(1) logistic regression")
#    cmds = {
#        "1": 
#    }

 
def main_prompt():
    print("What would you like to manage?")
    print("(1) sample fetch tool")
    print("(2) sample labeller")
    print("(3) machine learning models")
    print("(q) quit")

if __name__ == '__main__':
    main()
