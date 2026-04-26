"""
Model Trainer Module
====================
This module handles the final training stage of the ML pipeline.  It takes
the transformed train / test NumPy arrays from the data-transformation step,
trains several candidate regressors, compares their test scores, and saves
the best performing model as a .pkl artifact.

Flow:
    train_arr / test_arr  ──►  split into X and y
                         ──►  train multiple regression models
                         ──►  evaluate each model on the test set
                         ──►  pick the best model by R2 score
                         ──►  artifacts/model.pkl (trained estimator)
"""

import os
import sys
from dataclasses import dataclass

from catboost import CatBoostRegressor
from sklearn.ensemble import AdaBoostRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging
from src.utils import evaluate_model, save_obj


# ---------------------------------------------------------------------------
# ModelTrainerConfig
# ---------------------------------------------------------------------------
# Dataclass that centralises the output path for the fitted model artifact.
# Keeping the path in a config object makes it easy to update later without
# touching the training logic itself.
# ---------------------------------------------------------------------------
@dataclass
class ModelTrainerConfig:
    train_model_filepath = os.path.join("artifacts", "model.pkl")


# ---------------------------------------------------------------------------
# ModelTrainer
# ---------------------------------------------------------------------------
# Core class that fits candidate models, compares their scores, and persists
# the best estimator to disk for later prediction use.
# ---------------------------------------------------------------------------
class ModelTrainer:
    def __init__(self):
        # Store the config so all file paths are accessible through the
        # instance instead of hard-coded throughout the method body.
        self.modeltrainerconfig = ModelTrainerConfig()

    # -----------------------------------------------------------------------
    # initiate_model_trainer
    # -----------------------------------------------------------------------
    # End-to-end training method that:
    #   1. Splits the transformed arrays into features and target values.
    #   2. Builds a dictionary of candidate regression models.
    #   3. Evaluates each model using the shared evaluate_model helper.
    #   4. Selects the model with the highest test R2 score.
    #   5. Serialises the selected model to artifacts/model.pkl.
    #
    # Args:
    #     train_Array (np.ndarray): Transformed training data where the last
    #         column is the target value.
    #     test_Array (np.ndarray): Transformed test data where the last
    #         column is the target value.
    #
    # Returns:
    #     tuple: (best_model, best_model_score)
    #         - best_model: The fitted estimator with the highest test score.
    #         - best_model_score: The corresponding test R2 score.
    # -----------------------------------------------------------------------
    def initiate_model_trainer(self,train_Array,test_Array):
        try:
            # --- 1. Split arrays into features and target -------------------
            # The transformed arrays are expected to have the target value in
            # the final column, so slicing with :-1 and -1 gives us X and y.
            logging.info("splitting training and testing data")
            X_train,Y_train,X_test,Y_test=(
                train_Array[:,:-1],
                train_Array[:,-1],
                test_Array[:,:-1],
                test_Array[:,-1]
            )

            # --- 2. Define candidate models ---------------------------------
            # Each entry maps a human-readable model name to an unfitted
            # estimator.  These are the models evaluated against the same
            # train/test split so their scores are directly comparable.
            models = {
                "random forest regressor" : RandomForestRegressor(),
                "decision tree" : DecisionTreeRegressor(),
                "linear regressor": LinearRegression(),
                "k Neighbour regressor": KNeighborsRegressor(),
                "adaboost" : AdaBoostRegressor(),
                "gradient boost" : GradientBoostingRegressor(),
                "catboost" : CatBoostRegressor(verbose=False),
                "xgboost": XGBRegressor()
            }

            # --- 3. Evaluate each candidate model ---------------------------
            # The helper returns a dictionary of model name -> test R2 score.
            model_report :dict = evaluate_model(X_train,Y_train,X_test,Y_test,models)

            # --- 4. Select the best model -----------------------------------
            # Highest R2 score wins; the model name is then used to fetch the
            # corresponding fitted estimator from the models dictionary.
            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]

            # --- 5. Persist the winning estimator ---------------------------
            # Saving the trained model allows the prediction pipeline to load
            # and reuse exactly the same fitted estimator later on.
            save_obj(file_path=self.modeltrainerconfig.train_model_filepath, obj=best_model)
            return best_model,best_model_score
        except Exception as e:
            raise CustomException(e,sys)
