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
from sklearn.metrics import r2_score



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


# ---------------------------------------------------------------------------
# evaluate_model
# ---------------------------------------------------------------------------
# Trains each candidate model, evaluates it on the held-out test set, and
# returns a score map keyed by model name.
#
# Flow:
#   1. Loop through every model in the supplied dictionary.
#   2. Fit the model on the training features and target.
#   3. Predict on the test features.
#   4. Compute the test R2 score for each model.
#   5. Store the score in a report dictionary and return it.
#
# Args:
#     X_train (array-like): Training features.
#     Y_train (array-like): Training target values.
#     X_test  (array-like): Test features.
#     Y_test  (array-like): Test target values.
#     models  (dict): Model name -> unfitted estimator.
#
# Returns:
#     dict[str, float]: Mapping of model name to test R2 score.
# ---------------------------------------------------------------------------
def evaluate_model(X_train,Y_train,X_test,Y_test,models):
    try:
        model_report = {} 

        for i in range(len(list(models))):
            model = list(models.values())[i]
            model.fit(X_train,Y_train)
            Y_train_pred = model.predict(X_train)
            Y_test_pred = model.predict(X_test)
            test_model_score = r2_score(Y_test, Y_test_pred)
            model_report[list(models.keys())[i]] = test_model_score

        return model_report
    except Exception as e:
        raise CustomException(e, sys)