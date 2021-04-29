import os
import base64
import requests
import threading
from github import Github
from threading import Lock



from pysourcecodesec import logger
from pysourcecodesec import raw_dir
from pysourcecodesec import github_credentials
from pysourcecodesec import raw_lock
from pysourcecodesec import raw_write_file

from github import RateLimitExceededException

default_search_term = "python"

# 
def license_is_MIT(repo):
    '''
    Given a Github.Repository.Repository, returns True if the license is MIT, False otherwise
    MIT is one of the most permissive licenses, so there are no requirements using their code
    '''
    try:
        mit_txt = base64.b64decode(repo.get_license().content.encode()).decode()[:3]
    except:
        mit_txt = None
    return mit_txt == "MIT"
 

class FetchTool():

    def __init__(self):
        '''
        returns true self.algorithms[alg] is not None
        raises MLException if self.algorithms[alg] does not exist
        '''
        self.tname = "sample fetch tool"
        self.__load_github_credentials()
        self.stop_lock = Lock()
        self.running = False
        self.search_term = default_search_term
        self.fetch_thread = threading.Thread(target=self.__collect_python_files)
        


    def start(self):
        if self.running:
            logger.warning("Fetch tool is already running...")
            return
        logger.info("Starting sample fetch tool...")
        self.running = True
        self.fetch_thread.start()
        logger.info("Sample fetch tool successfully started.")


    def stop(self):
        logger.info("Stopping sample fetch tool...")
        self.stop_lock.acquire()
        self.running = False
        self.stop_lock.release()
        if self.fetch_thread.is_alive():
            self.fetch_thread.join()
            self.fetch_thread = threading.Thread(target=self.__collect_python_files) #Reinitialize thread
        logger.info("Sample fetch tool successfully stopped.")
    

    def status(self):
        if self.running:
            print("Sample fetch tool is currently running")
        else:
            print("Sample fetch tool is currently stopped")


    def set_search_term(self, new_search_term):
        logger.info("Updating fetch tool search term from {} to {}".format(self.search_term, new_search_term))
        restart = False
        if self.running:
            self.fetch_thread.stop()
            self.fetch_thread = threading.Thread(target=self.__collect_python_files)
            restart = True
        self.search_term = new_search_term
        if restart:
            self.fetch_thread.start()


    # 
    def __load_github_credentials(self):
        '''
        This method first checks creds.conf located in the project directory. If it is unable to load GitHub credentials from
        creds.conf, it then checks for the file ~/.git-credentials. Neither exist, GitHub API calls are unauthenticated which 
        result in a limited number of allowed API calls per IP address.
        Each line in '~/.git-credentials' contains credentials to a website for hosting git repos (GitHub,
        BitBucket, etc). 
        Format: 'https://<user>:<password>@<website>'
        Note: spaces in password are replaced with '%20'. Other specials characters *may* be subsituted by 
        a special escape sequence as well.
        '''
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
            except KeyError:
                logger.warning("No HOME environment variable")
        if user == None and pwd == None:
            logger.warning("No credentials found, using unauthenticated API may result in less API calls allowed from this IP address.")
        else:
            logger.info("GitHub credentials found for user {}".format(user))
        self.githubAPI = Github(user,pwd)


    def __collect_python_files(self):
        '''
        Searches GitHub for 'python' and saves all files with a MIT license to data/raw
        Iterates over all repos found with this search, or until API access times out
        '''
        done = False
        try:
            for repo in self.githubAPI.search_repositories(self.search_term):
                if license_is_MIT(repo):
                    for content in repo.get_contents(""):
                        if done:
                            break
                        split_content = content.name.split(".")
                        if split_content[len(split_content) - 1] == "py":
                            req = requests.get(content.download_url)
                            fname = raw_dir + repo.name + "_" + content.name
                            raw_lock.acquire()
                            raw_write_file = fname
                            raw_lock.release()
                            if not os.path.isfile(fname):
                                with open(fname, 'wb') as f:
                                    f.write(req.content)
                        self.stop_lock.acquire()
                        if not self.running:
                            done = True
                        self.stop_lock.release()
                    if done:
                        break
        except RateLimitExceededException:
            self.stop()
