"""
Data Ingestion Module
=====================
First stage of the ML pipeline.  This module is responsible for reading the
raw student-performance dataset from disk, persisting an untouched copy as
"raw.csv", and then splitting it into train / test CSVs that downstream
components (data transformation, model training) consume.

Flow:
    raw CSV on disk  ──►  artifacts/raw.csv   (archival copy)
                     ──►  artifacts/train.csv (80 % of rows)
                     ──►  artifacts/test.csv  (20 % of rows)
"""

import os
import sys
from src.exception import CustomException
from src.logger import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
from src.components.data_transformation import DataTransformation
from src.components.data_transformation import DataTransformationConfig


# ---------------------------------------------------------------------------
# DataIngestionConfig
# ---------------------------------------------------------------------------
# Dataclass that centralises every output path the ingestion step writes to.
# Using a dataclass keeps all path definitions in one place so they are easy
# to override for testing or when the project layout changes.
# ---------------------------------------------------------------------------
@dataclass
class DataIngestionConfig:
    train_data_path: str=os.path.join('artifacts','train.csv')
    test_data_path: str=os.path.join('artifacts','test.csv')
    raw_data_path: str=os.path.join('artifacts','raw.csv')


# ---------------------------------------------------------------------------
# DataIngestion
# ---------------------------------------------------------------------------
# Orchestrates the loading and splitting of the raw dataset.
#
# Usage (standalone or called from a training script):
#     obj = DataIngestion()
#     train_data, test_data = obj.initiatedataingestion()
#
# After execution the artifacts/ directory will contain:
#     raw.csv   – full dataset exactly as it was read from the source
#     train.csv – 80 % stratified-random sample for model fitting
#     test.csv  – 20 % held-out sample for evaluation
# ---------------------------------------------------------------------------
class DataIngestion:
    def __init__(self):
        # Store the config so every method can reference output paths
        # through self.ingestion_config without hard-coding strings.
        self.ingestion_config=DataIngestionConfig()

    # -----------------------------------------------------------------------
    # initiatedataingestion
    # -----------------------------------------------------------------------
    # Reads the source CSV, saves an archival copy, splits the data into
    # train / test sets, writes both to disk, and returns their paths.
    #
    # Steps:
    #   1. Read the raw student-performance CSV into a DataFrame.
    #   2. Ensure the artifacts/ directory exists.
    #   3. Write the full DataFrame to raw.csv (archival / debugging copy).
    #   4. Split 80/20 with a fixed random seed for reproducibility.
    #   5. Write train.csv and test.csv.
    #   6. Return (train_data_path, test_data_path) so the next pipeline
    #      stage knows where to find the splits.
    #
    # Returns:
    #     tuple[str, str]: (train_data_path, test_data_path)
    # -----------------------------------------------------------------------
    def initiatedataingestion(self):
        logging.info("Entered data ingetion method")
        try:
            # --- 1. Read the source dataset ----------------------------------
            # The CSV lives under notebook/data/ and contains all student
            # records with features like gender, lunch type, test scores, etc.
            df = pd.read_csv("notebook/data/stud.csv")
            logging.info("read the dataset")

            # --- 2. Create the output directory if it doesn't exist ----------
            # os.makedirs with exist_ok=True is a no-op when the folder is
            # already present, so this is safe to call repeatedly.
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)

            # --- 3. Save an archival copy of the raw data --------------------
            # Keeping raw.csv allows us to inspect or re-split the data later
            # without re-downloading or re-generating it.
            df.to_csv(self.ingestion_config.raw_data_path,header=True,index=False)

            # --- 4. Split into train (80 %) and test (20 %) ------------------
            # random_state=42 pins the random seed so every run produces the
            # exact same split — essential for reproducibility and debugging.
            logging.info("train test split initiated")
            train_set,test_set = train_test_split(df,test_size=0.2,random_state=42)

            # --- 5. Persist both splits to disk ------------------------------
            train_set.to_csv(self.ingestion_config.train_data_path,index=False,header=True)
            test_set.to_csv(self.ingestion_config.test_data_path,index=False,header=True)    
            logging.info("ingestion of data completed")

            # --- 6. Return paths for downstream consumption ------------------
            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )

        except Exception as e:
            # Wrap the raw exception in CustomException to attach traceback
            # context (file name and line number) for easier debugging.
            raise CustomException(e,sys)
        

# ---------------------------------------------------------------------------
# Standalone execution — runs the ingestion + transformation pipeline end
# to end when this file is invoked directly (python data_ingestion.py).
# ---------------------------------------------------------------------------
if __name__=="__main__":
    obj = DataIngestion()
    train_data,test_data = obj.initiatedataingestion()

    data_transformation = DataTransformation()
    data_transformation.initiate_data_transformation(train_data,test_data)
