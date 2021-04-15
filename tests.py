import logging
from pysourcecodesec import *
logger.info("Running unit tests")
from labeller import *
from fetch_tool import *

logger.info("Running fetch_tool unit tests")
fetch_tool = FetchTool()
# fetch tool unit tests

logger.info("Running labeller unit tests")
labeller = Labeller()
# labeller unit tests

logger.info("Running integration tests")
