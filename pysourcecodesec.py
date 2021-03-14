import logging

import fetch_tool 

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
    while True:
        cmd = input("cmd: ")
        if cmd == "f":
            sample_fetcher.start()
        elif cmd == "s":
            sample_fetcher.stop()
            

if __name__ == '__main__':
    main()
