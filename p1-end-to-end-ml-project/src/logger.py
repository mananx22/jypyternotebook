"""
Logging Configuration Module
=============================
Sets up a project-wide logger that writes timestamped, structured messages
to a dedicated log file.  Every other module imports `logging` from here,
so all pipeline stages (ingestion, transformation, training) share the
same log format and output directory.

Flow:
    Any module calls logging.info(msg)
        ──►  message is formatted with timestamp, line number, logger name
        ──►  written to  logs/<MM_DD_YYYY_HH_MM_SS>.log
"""

import logging
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# Log file setup
# ---------------------------------------------------------------------------
# 1. Generate a unique filename using the current timestamp down to the
#    second.  This means every time the pipeline runs, a new log file is
#    created — making it easy to compare runs or debug a specific execution.
#
# 2. Create the logs/ directory under the current working directory.
#    exist_ok=True prevents errors if the folder already exists.
#
# 3. Combine the directory and filename into the full LOG_FILE_PATH that
#    the logging module will write to.
# ---------------------------------------------------------------------------
LOG_FILE=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
logs_path = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_path,exist_ok=True) 

LOG_FILE_PATH = os.path.join(logs_path,LOG_FILE)


# ---------------------------------------------------------------------------
# Configure the root logger
# ---------------------------------------------------------------------------
# basicConfig sets up the root logger once at import time.  Parameters:
#
#   filename      – all log output goes to this file (no console output
#                   unless a StreamHandler is added separately).
#
#   format        – each line includes:
#                     %(asctime)s   → human-readable timestamp
#                     %(lineno)d    → line number where logging was called
#                     %(name)s      → logger name (usually the module name)
#                     %(levelname)s → severity (INFO, WARNING, ERROR, etc.)
#                     %(message)s   → the actual log message
#
#   level         – INFO means DEBUG messages are suppressed; everything
#                   from INFO upward (INFO, WARNING, ERROR, CRITICAL) is
#                   captured.
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)