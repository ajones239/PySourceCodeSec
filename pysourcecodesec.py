import logging

import fetch_tool 
import labeller

# raw_dir specifies the directory to load raw unformatted Python sample files fetched from the fetch_tool
raw_dir = "data/raw/" 
processed_dir = "data/processed"

# contains GitHub login credentials. Comments start with '#' and must be the first character on the line, 
#   must define 'user' and 'pwd'. Don't include quotes or leading/trailing spaces
#   Ex)
#   user=myusername
#   pwd=my password
github_credentials = 'creds.conf' 

log_file = 'events.log'

logging.basicConfig(filename=log_file,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Initialized logging")


def main():
    sample_fetcher = fetch_tool.FetchTool()
    sample_labeller = labeller.Labeller()
    cmds = {
        "1": fetch_tool_prompt,
        "2": labeller_prompt,
    }
    args = {
        "1": sample_fetcher,
        "2": labeller
    }
    while True:
        main_prompt()
        cmd = input("cmd: ")
        if cmd is "q":
            print("quiting...")
            break
        try:
            cmds[cmd](args[cmd])
        except KeyError:
            print("Sorry, {} does not correspond to a valid command.".format(cmd))

        '''
        if cmd == "f":
            sample_fetcher.start()
        elif cmd == "s":
            sample_fetcher.stop()
        '''


def fetch_tool_prompt(fetcher):
    print("\n(1) start")
    print("(2) stop")
    print("(3) status")
    cmds = {
        "1": fetcher.start,
        "2": fetcher.stop,
        "3": fetcher.is_running
    }
    try:
        cmd = input("Command: ")
        cmds[cmd]()
    except KeyError:
        print("Sorry, {} does not correspond to a valid command.".format(cmd))


def labeller_prompt(labeller):
    print("here2")
            

def main_prompt():
    print("What would you like to manage?")
    print("(1) sample fetch tool")
    print("(2) sample labeller")
    print("(3) neural network trainer")
    print("(q) quit")

if __name__ == '__main__':
    main()
