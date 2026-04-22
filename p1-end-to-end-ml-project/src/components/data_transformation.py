# Preprocess the student performance dataset into model-ready features.
# Save the fitted transformer so training and inference use the same steps.

# Access the active exception details when wrapping errors.
import sys

# Create a lightweight container for configuration values.
from dataclasses import dataclass

# Join transformed features with the target values.
import numpy as np

# Read the train and test CSV files.
import pandas as pd

# Apply different transforms to different columns.
from sklearn.compose import ColumnTransformer

# Fill in missing values before scaling or encoding.
from sklearn.impute import SimpleImputer

# Chain preprocessing steps together.
from sklearn.pipeline import Pipeline

# Encode categories and scale numeric data.
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Raise project-specific errors with context.
from src.exception import CustomException

# Write progress messages to the project log.
from src.logger import logging

# Save fitted objects to disk.
from src.utils import save_obj

# Build filesystem paths for artifacts.
import os


# Turn the configuration container into a dataclass.
# Keep the artifact path in one dedicated place.
@dataclass
class DatatransformationConfig:
    # Save the fitted preprocessor in the artifacts folder.
    preprocessor_obj_file_path = os.path.join("artifacts", "preprocessor.pkl")


# Build and run the preprocessing workflow.
# Fit preprocessing on the train split and reuse it for the test split.
class Datatransformation():
    # Initialize the transformer with its configuration.
    # Keep artifact paths available on the instance.
    def __init__(self):
        # Create the config object for this transformer.
        self.datatransformationconfig = DatatransformationConfig()

    # Build the column-wise preprocessing pipeline.
    # Return a reusable transformer for numeric and categorical features.
    def get_data_transformer_object(self):
        # Start guarded construction so errors can be wrapped consistently.
        try:
            # List the numeric columns that will be scaled.
            numerical_columns = [
                # Scale the reading score feature.
                "reading_score",
                # Scale the writing score feature.
                "writing_score",
            ]
            # List the categorical columns that will be one-hot encoded.
            cat_columns = [
                # Encode the gender feature.
                "gender",
                # Encode the race and ethnicity feature.
                "race_ethnicity",
                # Encode the parental education feature.
                "parental_level_of_education",
                # Encode the lunch feature.
                "lunch",
                # Encode the test preparation feature.
                "test_preparation_course",
            ]

            # Create the pipeline for numeric columns.
            num_pipeline = Pipeline(
                # Define the ordered numeric preprocessing steps.
                steps=[
                    # Fill missing numeric values with the median.
                    ("imputer", SimpleImputer(strategy="median")),
                    # Standardize numeric values.
                    ("scaler", StandardScaler()),
                ]
            )

            # Create the pipeline for categorical columns.
            cat_pipeline = Pipeline(
                # Define the ordered categorical preprocessing steps.
                steps=[
                    # Fill missing categories with the most common value.
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    # Convert categories to one-hot encoded features.
                    ("one_hot_encoder", OneHotEncoder()),
                ]
            )

            # Note that the numeric and categorical encoders are ready.
            logging.info("Categorical and numerical encoding completed")

            # Combine the numeric and categorical pipelines.
            preprocessor = ColumnTransformer([
                # Apply the numeric pipeline to numeric columns.
                ("numerical_pipeline", num_pipeline, numerical_columns),
                # Apply the categorical pipeline to categorical columns.
                ("categorical_pipeline", cat_pipeline, cat_columns),
            ])

            # Return the configured preprocessing object.
            return preprocessor
        except Exception as e:
            raise CustomException(e, sys)

    # Load split data, transform features, and save the fitted preprocessor.
    # Return the transformed arrays and the saved artifact path.
    def initiate_datatransformation(self, train_path, test_path):
        # Start guarded execution so data issues are wrapped consistently.
        try:
            # Read the training split into a dataframe.
            train_df = pd.read_csv(train_path)
            # Read the test split into a dataframe.
            test_df = pd.read_csv(test_path)
            # Confirm both files were loaded.
            logging.info("train and test data read completed")
            # Note that the preprocessing object is about to be built.
            logging.info("obtaining preprocessor object")
            # Build the preprocessing pipeline.
            preprocessing_obj = self.get_data_transformer_object()

            # Identify the target column.
            target_col_name = "math_score"
            # Keep the numeric feature names available locally.
            numerical_columns = ["reading_score", "writing_score"]
            # Remove the target column from the training features.
            input_feature_train_df = train_df.drop(columns=[target_col_name], axis=1)
            # Extract the training target values.
            target_feature_train_df = train_df[target_col_name]

            # Remove the target column from the test features.
            input_feature_test_df = test_df.drop(columns=[target_col_name], axis=1)
            # Extract the test target values.
            target_feature_test_df = test_df[target_col_name]

            # Note that transformation is about to run.
            logging.info("applying preprocessing on training and test dtaset")

            # Fit on the training features and transform them.
            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            # Transform the test features with the fitted pipeline.
            input_feature_test_Arr = preprocessing_obj.transform(input_feature_test_df)

            # Combine transformed training features with the training target.
            train_arr = np.c_[
                # Convert the target series to a NumPy array before joining.
                input_feature_train_arr, np.array(target_feature_train_df)
            ]

            # Combine transformed test features with the test target.
            test_arr = np.c_[
                # Convert the target series to a NumPy array before joining.
                input_feature_test_Arr, np.array(target_feature_test_df)
            ]

            # Record that the fitted pipeline will be saved.
            logging.info("saved preprocessing objects")

            # Persist the fitted preprocessor to disk.
            save_obj(file_path=self.datatransformationconfig.preprocessor_obj_file_path, obj=preprocessing_obj)

            # Return the transformed data and artifact path.
            return(
                # Provide the transformed training data.
                train_arr,
                # Provide the transformed test data.
                test_arr,
                # Provide the saved artifact path.
                self.datatransformationconfig.preprocessor_obj_file_path,
            )
        except Exception as e:
            raise CustomException(e, sys)