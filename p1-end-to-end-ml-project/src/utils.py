"""
Utility Module
==============
Shared helper functions used across multiple pipeline stages.  Currently
contains a single function — save_obj — that serialises any Python object
to a .pkl file using dill.

What is serialising?
    Serialising means converting a live Python object (sitting in RAM) into
    a stream of bytes that can be saved to a file on disk.  For example,
    when you fit a preprocessor, it learns column medians, category lists,
    and scaler means/stds — all stored in memory.  The moment your script
    ends, that data is gone.

    Serialising (dill.dump) freezes the object into a .pkl file.  Later,
    during prediction, you deserialise it (dill.load) to get the exact same
    object back — with all learned values intact — without re-fitting.

        Training time:    fitted_preprocessor ──► dill.dump ──► preprocessor.pkl
        Prediction time:  preprocessor.pkl    ──► dill.load ──► fitted_preprocessor (identical)

    In short: serialise = save to disk, deserialise = load from disk.

Why dill instead of pickle?
    dill extends pickle to handle a wider range of Python objects (lambdas,
    nested functions, dynamically defined classes).  This makes it safer for
    serialising complex scikit-learn pipelines that may contain custom
    transformers or closures.

Flow:
    fitted object (e.g. preprocessor)
        ──►  save_obj(file_path, obj)
        ──►  creates parent directories if needed
        ──►  writes binary .pkl file via dill.dump
"""

import os
import sys
import numpy as np
import pandas as pd
import src.logger
from src.exception import CustomException
import dill


# ---------------------------------------------------------------------------
# save_obj
# ---------------------------------------------------------------------------
# Serialises a Python object to a binary file at the given path.
#
# Steps:
#   1. Extract the directory portion of file_path and create it if it
#      doesn't exist (os.makedirs with exist_ok=True).
#   2. Open the file in write-binary mode ("wb") — dill produces bytes.
#   3. Dump the object using dill.dump, which writes the serialised bytes.
#   4. If anything fails, wrap the exception in CustomException so the
#      caller receives file/line context for debugging.
#
# Args:
#     file_path (str) : Destination path for the .pkl file
#                       (e.g. "artifacts/preprocessor.pkl").
#     obj       (Any) : The Python object to serialise (fitted transformer,
#                       trained model, etc.).
#
# Raises:
#     CustomException : On any I/O or serialisation error.
# ---------------------------------------------------------------------------
def save_obj(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj,file_obj)
    except Exception as e:
        raise CustomException(e,sys)