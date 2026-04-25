"""
Data Transformation Module
==========================
This module handles the entire feature-engineering / preprocessing stage of the
student-performance ML pipeline.  It sits between data ingestion (which produces
raw train/test CSVs) and model training (which expects clean NumPy arrays).

Responsibilities:
    1. Define *which* columns are numeric vs. categorical.
    2. Build a scikit-learn ColumnTransformer that applies the right pipeline
       to each column group (imputation → encoding/scaling).
    3. Fit the transformer on the training set and apply it to both splits,
       ensuring no data leakage from test into train.
    4. Persist the fitted transformer as a .pkl artifact so that the exact
       same preprocessing can be replayed at inference time.

Flow:
    artifacts/train.csv ──►  fit_transform  ──►  train_arr (NumPy array)
    artifacts/test.csv  ──►  transform      ──►  test_arr  (NumPy array)
                                            ──►  artifacts/preprocessor.pkl (fitted transformer)
"""

import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.exception import CustomException
from src.logger import logging
from src.utils import save_obj


# ---------------------------------------------------------------------------
# DataTransformationConfig
# ---------------------------------------------------------------------------
# A lightweight dataclass that centralises every path / constant the
# transformation step needs.  Right now the only value is the output
# location for the fitted preprocessor, but keeping it in a dataclass
# makes it trivial to extend later (e.g. add a path for a feature-list
# JSON, or a flag to toggle scaling on/off).
# ---------------------------------------------------------------------------
@dataclass
class DataTransformationConfig:
    # The fitted ColumnTransformer will be serialised (pickled) to this path.
    # Other components (model trainer, prediction pipeline) load this same
    # file so that new data is transformed identically to the training data.
    preprocessor_file_path: str = os.path.join("artifacts", "preprocessor.pkl")


# ---------------------------------------------------------------------------
# DataTransformation
# ---------------------------------------------------------------------------
# Core class that wires together the preprocessing logic.
#
# Usage (called from the training pipeline):
#     transformer = DataTransformation()
#     train_arr, test_arr, pkl_path = transformer.initiate_data_transformation(
#         train_path="artifacts/train.csv",
#         test_path="artifacts/test.csv",
#     )
#
# The returned arrays have the structure:
#     [transformed_features ... | target_column]
# so they can be sliced directly into X and y for model training.
# ---------------------------------------------------------------------------
class DataTransformation:

    def __init__(self):
        # Instantiate the config dataclass and store it on the instance
        # so every method can access artifact paths via self.config.
        self.config = DataTransformationConfig()

    # -----------------------------------------------------------------------
    # get_preprocessor
    # -----------------------------------------------------------------------
    # Builds and returns a sklearn ColumnTransformer that applies separate
    # pipelines to numeric and categorical columns.
    #
    # Numeric pipeline (applied to reading_score, writing_score):
    #   Step 1 – SimpleImputer(strategy="median")
    #       Replaces missing values with the column median.  Median is chosen
    #       over mean because exam scores can have outliers (e.g. a few zeros)
    #       that would skew the mean.
    #   Step 2 – StandardScaler()
    #       Centres each column to mean=0 and std=1.  Many algorithms
    #       (linear regression, SVMs, gradient-based methods) converge faster
    #       and perform better on standardised features.
    #
    # Categorical pipeline (applied to gender, race_ethnicity, etc.):
    #   Step 1 – SimpleImputer(strategy="most_frequent")
    #       Fills missing categories with the mode (most common value).
    #   Step 2 – OneHotEncoder()
    #       Converts each categorical value into a binary column.  This is
    #       necessary because most ML models cannot consume string labels
    #       directly; one-hot encoding avoids imposing a false ordinal
    #       relationship between categories.
    #
    # Returns:
    #     sklearn.compose.ColumnTransformer – unfitted preprocessor object.
    # -----------------------------------------------------------------------
    def get_preprocessor(self):
        try:
            # --- Define column groups ----------------------------------------
            # These lists must match the column names present in the CSV files
            # produced by the data-ingestion step.  If the dataset schema
            # changes, update these lists accordingly.
            numerical_features = ["reading_score", "writing_score"]
            categorical_features = [
                "gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course",
            ]

            # --- Numeric pipeline --------------------------------------------
            # Median imputation is robust to outliers; StandardScaler then
            # normalises each feature to zero mean and unit variance.
            numerical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )

            # --- Categorical pipeline ----------------------------------------
            # Mode imputation preserves the most common category; OneHotEncoder
            # converts each category into a sparse binary vector.
            categorical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot_encoder", OneHotEncoder()),
                ]
            )

            logging.info("Numerical and categorical pipelines constructed.")

            # --- Combine into a single ColumnTransformer ---------------------
            # ColumnTransformer routes each column to the correct pipeline
            # based on the feature lists above.  Columns not listed in either
            # list are dropped by default (remainder="drop").
            preprocessor = ColumnTransformer(
                [
                    ("numerical_pipeline", numerical_pipeline, numerical_features),
                    ("categorical_pipeline", categorical_pipeline, categorical_features),
                ]
            )

            return preprocessor

        except Exception as e:
            # Wrap the raw exception in CustomException so the project-wide
            # error handler can attach file name and line number context.
            raise CustomException(e, sys)

    # -----------------------------------------------------------------------
    # initiate_data_transformation
    # -----------------------------------------------------------------------
    # End-to-end method that:
    #   1. Reads the train and test CSV files from the paths supplied by the
    #      data-ingestion component.
    #   2. Separates input features (X) from the target column (y = math_score).
    #   3. Fits the preprocessor on X_train only (to avoid data leakage),
    #      then transforms both X_train and X_test.
    #   4. Re-attaches the target column to each transformed array so the
    #      model trainer receives a single array per split.
    #   5. Serialises the fitted preprocessor to disk (as a .pkl file) so
    #      the prediction pipeline can reuse the exact same transformation.
    #
    # Args:
    #     train_path (str): Absolute or relative path to the training CSV.
    #     test_path  (str): Absolute or relative path to the test CSV.
    #
    # Returns:
    #     tuple: (train_arr, test_arr, preprocessor_file_path)
    #         - train_arr (np.ndarray): Transformed training data with target
    #           as the last column.
    #         - test_arr  (np.ndarray): Transformed test data with target
    #           as the last column.
    #         - preprocessor_file_path (str): Path where the fitted
    #           preprocessor was saved.
    # -----------------------------------------------------------------------
    def initiate_data_transformation(self, train_path, test_path):
        try:
            # --- 1. Load the raw CSV splits ----------------------------------
            # These CSVs were written by the data-ingestion step and contain
            # all original columns including the target (math_score).
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logging.info("Train and test datasets loaded successfully.")

            # --- 2. Build the preprocessor -----------------------------------
            # The preprocessor is an unfitted ColumnTransformer; it will be
            # fitted on the training features in step 4 below.
            logging.info("Building preprocessor object.")
            preprocessor = self.get_preprocessor()

            # --- 3. Separate features (X) from target (y) --------------------
            # The target variable is "math_score" — this is what the model
            # will learn to predict.  Everything else is an input feature.
            target_column = "math_score"

            X_train = train_df.drop(columns=[target_column], axis=1)
            y_train = train_df[target_column]

            X_test = test_df.drop(columns=[target_column], axis=1)
            y_test = test_df[target_column]

            # --- 4. Fit on train, transform both splits ----------------------
            # fit_transform learns statistics (medians, modes, means, stds)
            # from X_train and applies the transformation in one pass.
            # transform on X_test reuses the *same* learned statistics so there
            # is no data leakage from the test set.
            logging.info("Applying preprocessor to training and test datasets.")
            X_train_arr = preprocessor.fit_transform(X_train)
            X_test_arr = preprocessor.transform(X_test)

            # --- 5. Re-attach the target column ------------------------------
            # np.c_ column-stacks the transformed features with the target
            # so the model trainer can simply slice arr[:, :-1] for X and
            # arr[:, -1] for y.
            train_arr = np.c_[X_train_arr, np.array(y_train)]
            test_arr = np.c_[X_test_arr, np.array(y_test)]

            # --- 6. Persist the fitted preprocessor --------------------------
            # Saving the fitted object ensures the prediction pipeline applies
            # the identical transformation (same medians, modes, scaler params)
            # that was learned during training.
            logging.info("Saving fitted preprocessor object to disk.")
            save_obj(
                file_path=self.config.preprocessor_file_path,
                obj=preprocessor,
            )

            return (
                train_arr,
                test_arr,
                self.config.preprocessor_file_path,
            )

        except Exception as e:
            # Wrap and re-raise so the project-wide error handler captures
            # the full traceback with file and line number context.
            raise CustomException(e, sys)