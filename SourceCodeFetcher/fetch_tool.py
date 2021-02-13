#import requests
import os
import logging
from pprint import pprint
from github import Github

logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)

# Loading GitHub credentials works on Linux, may work on Mac, definitely will not work on Windows.
# Each line in '~/.git-credentials' contains credentials to a website for hosting git repos (GitHub,
# BitBucket, etc). 
# Format: 'https://<user>:<password>@<website>'
# Note: spaces in password are replaced with '%20'. Other specials characters *may* be subsituted by 
# a special escape sequence as well.
def load_github_credentials():
    try:
        credfile = open(os.environ['HOME'] + "/.git-credentials")
        for l in credfile.readlines():
            if l[len(l) - 11:] != "github.com\n":
                continue
            else:
                l = l.split('//')[1].split('@')[0]
                user = l.split(':')[0]
                pwd = l.split(':')[1].replace("%20", " ")
        credfile.close()
    except FileNotFoundError:
        log.warning("Failed to load credentials: '~/.git-credentials' does not exist")
        user = None
        pwd = None
    finally:
        return (user,pwd)
    
creds = load_github_credentials()
g = Github(creds[0], creds[1])
for repo in g.search_repositories("python"):
    print(repo)
