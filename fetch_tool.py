import os
import base64
import requests
from github import Github
from threading import Thread
from threading import Lock

from pysourcecodesec import logger
from pysourcecodesec import raw_dir
from pysourcecodesec import github_credentials


default_search_term = "python"

# Given a Github.Repository.Repository, returns True if the license is MIT, False otherwise
# MIT is one of the most permissive licenses, so there are no requirements using their code
def license_is_MIT(repo):
    try:
        mit_txt = base64.b64decode(repo.get_license().content.encode()).decode()[:3]
    except:
        mit_txt = None
    return mit_txt == "MIT"
 

class FetchTool(Thread):

    def __init__(self):
        self.__load_github_credentials()
        self.stop_lock = Lock()
        self.running = False
        self.search_term = default_search_term
        super().__init__(target=self.__run_fetch_tool)


    def start(self):
        logger.info("Starting sample fetch tool...")
        self.running = True
        super().start()
        logger.info("Sample fetch tool successfully started.")


    def stop(self):
        logger.info("Stopping sample fetch tool...")
        self.stop_lock.acquire()
        self.running = False
        self.stop_lock.release()
        self.join()
        logger.info("Sample fetch tool successfully stopped.")


    def set_search_term(self, new_search_term):
        logger.info("Updating fetch tool search term from {} to {}".format(self.search_term, new_search_term))
        self.stop()
        self.search_term = new_search_term
        self.start()


    # This method first checks creds.conf located in the project directory. If it is unable to load GitHub credentials from
    # creds.conf, it then checks for the file ~/.git-credentials. Neither exist, GitHub API calls are unauthenticated which 
    # result in a limited number of allowed API calls per IP address.
    #
    # Each line in '~/.git-credentials' contains credentials to a website for hosting git repos (GitHub,
    # BitBucket, etc). 
    # Format: 'https://<user>:<password>@<website>'
    # Note: spaces in password are replaced with '%20'. Other specials characters *may* be subsituted by 
    # a special escape sequence as well.
    def __load_github_credentials(self):
        user = None
        pwd = None
        # try loading from creds.conf
        if os.path.isfile(github_credentials):
            with open(github_credentials, 'r') as f:
                for l in f.readlines():
                    if l[0] == '#':
                        continue
                    elif l[:4] == "user":
                        user = l[5:]
                    elif l[:3] == "pwd":
                        pwd = l[4:]
                    else:
                        logger.warning("Unknown line in creds.conf")
        # otherwise try ~/.git-credentials
        elif user == None and pwd == None:
            logger.warning("Unable to load GitHub credentials from creds.conf, trying ~/.git-credentials")
            try:
                with open(os.environ['HOME'] + "/.git-credentials", 'r') as credfile:
                    for l in credfile.readlines():
                        if l[len(l) - 11:] != "github.com\n":
                            continue
                        else:
                            l = l.split('//')[1].split('@')[0]
                            user = l.split(':')[0]
                            pwd = l.split(':')[1].replace("%20", " ")
            except FileNotFoundError:
                logger.warning("~/.git-credentials does not exist")
        if user == None and pwd == None:
            logger.warning("No credentials found, using unauthenticated API may result in less API calls allowed from this IP address.")
        else:
            logger.info("GitHub credentials found for user {}".format(user))
        self.githubAPI = Github(user,pwd)


    # Searches GitHub for 'python' and saves all files with a MIT license to data/raw
    # Iterates over all repos found with this search, or until API access times out
    def __collect_python_files(self):
        for repo in githubAPI.search_repositories(self.search_term):
            if license_is_MIT(repo):
                for content in repo.get_contents(""):
                    split_content = content.name.split(".")
                    if split_content[len(split_content) - 1] == "py":
                        req = requests.get(content.download_url)
                        fname = raw_dir + repo.name + "_" + content.name
                        if not os.path.isfile(fname):
                            with open(fname, 'wb') as f:
                                f.write(req.content)


    def __run_fetch_tool(self):
        done = False
        while not done:

            self.stop_lock.acquire()
            if not self.running:
                done = True
            self.stop_lock.release()

