# Import statements - bringing tools from the toolbox
import os  # Tool for file/folder operations
import sys  # Tool for system info (like when errors happen)
from src.exception import CustomException  # Custom error message maker from our own code
from src.logger import logging  # Recorder that writes what happened to a file
import pandas as pd  # Tool for handling data in spreadsheets (pd is a shortcut)
from sklearn.model_selection import train_test_split  # Tool that cuts data into training and testing pieces
from dataclasses import dataclass  # Decorator that auto-makes constructors for simple data-holder classes
from src.components.data_transformation import Datatransformation
from src.components.data_transformation import DatatransformationConfig
# Config class - a simple box that holds three file paths
# Think of it as labels: "where to save training data", "where to save test data", "where to save raw data"
@dataclass
class DataIngestionConfig:
    train_data_path: str=os.path.join('artifacts','train.csv')  # Path to save training data
    test_data_path: str=os.path.join('artifacts','test.csv')    # Path to save test data
    raw_data_path: str=os.path.join('artifacts','raw.csv')      # Path to save raw data    

# DataIngestion class - handles all data loading and splitting tasks
class DataIngestion:
    def __init__(self):
        # When you create a DataIngestion object, it automatically creates a config box inside it
        # So every object knows where the files should go
        self.ingestion_config=DataIngestionConfig()

    def initiatedataingestion(self):
        # This method does the actual work. It starts by writing to the log.
        logging.info("Entered data ingetion method")
        # try: means "try to do this, and if it breaks, handle it below"
        try:
            # Load the CSV file (a spreadsheet) into a pandas dataframe
            df = pd.read_csv("notebook/data/stud.csv")
            # Log that you successfully read the dataset
            logging.info("read the dataset")

            # Create the 'artifacts' folder if it doesn't exist
            # exist_ok=True means don't complain if it's already there
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)
            # Save the entire dataframe as a CSV file to the raw data path
            df.to_csv(self.ingestion_config.raw_data_path,header=True,index=False)

            # Log that you're starting to split the data
            logging.info("train test split initiated")
            # Cut the data into two pieces: 80% for training, 20% for testing
            # random_state=42 makes it reproducible (same split every time)
            train_set,test_set = train_test_split(df,test_size=0.2,random_state=42)
            # Save the training piece to artifacts/train.csv
            train_set.to_csv(self.ingestion_config.train_data_path,index=False,header=True)
            # Save the test piece to artifacts/test.csv
            test_set.to_csv(self.ingestion_config.test_data_path,index=False,header=True)    
            # Log that you're done
            logging.info("ingestion of data completed")

            # Send back the two file paths so whoever called this knows where the data was saved
            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        # If anything broke above, catch the error
        except Exception as e:
            # Wrap it in your custom error class and raise it (throw it back to the caller)
            raise CustomException(e,sys)
        
    
# Run the pipeline only when this file is executed directly.
if __name__=="__main__":
    # Create the ingestion object.
    obj = DataIngestion()

    # Split the raw data into train and test files.
    train_data,test_data = obj.initiatedataingestion()

    # Transform the split data and save the preprocessor.
    data_transformation = Datatransformation()
    data_transformation.initiate_datatransformation(train_data,test_data)
