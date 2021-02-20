#import requests
import os
import base64
import requests
from pprint import pprint
from github import Github

from pysourcecodesec import logger


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
        logger.warning("Failed to load credentials: '~/.git-credentials' does not exist")
        user = None
        pwd = None
    finally:
        return (user,pwd)

# Given a Github.Repository.Repository, returns True if the license is MIT, False otherwise
# MIT is one of the most permissive licenses, so there are no requirements using their code
def license_is_MIT(repo):
    try:
        mit_txt = base64.b64decode(repo.get_license().content.encode()).decode()[:3]
    except:
        mit_txt = None
    return mit_txt == "MIT"
    
creds = load_github_credentials()
g = Github(creds[0], creds[1])
for repo in g.search_repositories("python"):
    if license_is_MIT(repo):
        for content in repo.get_contents(""):
            split_content = content.name.split(".")
            if split_content[len(split_content) - 1] == "py":
                req = requests.get(content.download_url)
                fname = raw_dir + repo.name + "_" + content.name
                if not os.path.isfile(fname):
                    with open(fname, 'wb') as f:
                        f.write(req.content)

