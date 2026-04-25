"""
Custom Exception Module
=======================
Provides a project-wide exception class that enriches Python's default error
messages with the exact script name and line number where the error occurred.

Every component in the pipeline (data ingestion, transformation, model
training) wraps raw exceptions inside CustomException so that log files
and terminal output contain enough context to locate the root cause quickly.

Flow:
    raw Exception  ──►  error_message_detail()  ──►  formatted string
                   ──►  CustomException.__init__  ──►  re-raised with context
"""

import sys
from types import ModuleType
from src.logger import logging


# ---------------------------------------------------------------------------
# error_message_detail
# ---------------------------------------------------------------------------
# Extracts traceback information from the current exception context and
# builds a human-readable error string.
#
# How it works:
#   1. sys.exc_info() returns (type, value, traceback) for the active
#      exception.  We only need the traceback object (exc_tb).
#   2. From exc_tb we pull:
#        - tb_frame.f_code.co_filename  → the .py file where the error fired
#        - tb_lineno                    → the exact line number
#   3. These are formatted together with the original error message into a
#      single string that is easy to grep in log files.
#
# Args:
#     error              : The original exception instance.
#     error_detail (sys) : The sys module, used to call sys.exc_info().
#
# Returns:
#     str : A formatted message like:
#           "error occured in python script [file.py], at line [42]
#            error message [division by zero]"
# ---------------------------------------------------------------------------
def error_message_detail(error, error_detail: ModuleType):
    _,_,exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = "error occured in python script [{0}], at line [{1}] error message [{2}]".format(
        file_name,exc_tb.tb_lineno,str(error)
    ) 
    return error_message


# ---------------------------------------------------------------------------
# CustomException
# ---------------------------------------------------------------------------
# Subclass of Python's built-in Exception that automatically formats the
# error with file and line context via error_message_detail().
#
# Usage (inside any try/except block in the project):
#     except Exception as e:
#         raise CustomException(e, sys)
#
# When printed or logged, the exception displays the enriched message
# instead of the raw error text, thanks to the __str__ override.
# ---------------------------------------------------------------------------
class CustomException(Exception):
    def __init__(self, error_message, error_detail: ModuleType):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)
    
    def __str__(self):
        return self.error_message 