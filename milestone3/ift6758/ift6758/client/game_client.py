import numpy as np
import requests
import os
# from src import convert_game_to_dataframe
import pandas as pd
from .game_client_utils import *

struct_model = {
    "LogisticRegression_Distance": "distance",
    "LogisticRegression_Distance_Angle": "angle"
}

class GameClient:
    def __init__(self, base_url, model_service_url, model_name):
        self.old_predictions = None
        self.base_url = base_url
        self.model_service_url = model_service_url
        self.model_name = struct_model[model_name]
        self.model_path = f'./data/predictions/{model_name}'

        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

    def _load_predictions(self, game_id):
        prediction_file = os.path.join(self.model_path, f"{game_id}_predictions.json")
        if os.path.exists(prediction_file):
            with open(prediction_file, 'r') as file:
                return pd.read_json(file, orient="records")
        return None

    def _save_predictions(self, game_id, predictions):
        if self.old_predictions is not None:
            predictions = pd.concat([self.old_predictions, predictions], axis=0, ignore_index=True)
        prediction_file = os.path.join(self.model_path, f"{game_id}_predictions.json")
        predictions.to_json(prediction_file, orient="records", indent=1)

    def fetch_game_data(self, game_id):
        try:
            response = requests.get(self.base_url + '/' + game_id + '/play-by-play')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ValueError("Fetch data error : ", e)

    def predict(self, features):
        try:
            features = features.drop('team', axis=1)
            response = requests.post(f"{self.model_service_url}/predict", json=features.to_dict(orient="list"))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ValueError("Predict data error : ", e)

    def process_game(self, game_id):
        """
        Fonction principale
        """
        #
        saved_predictions = self._load_predictions(game_id)

        # Récupérer
        data = self.fetch_game_data(game_id)
        game = convert_game_to_dataframe(data)
        game = game[["eventOwnerTeam", "shotDistance", "shotAngle"]]
        game.columns = ['team', 'distance', 'angle']
        if self.model_name == "distance":
            game = game.drop('angle', axis=1)

        # Si le fichier existe déjà
        if saved_predictions is not None:

            # S'il y a de nouveaux évènements goal et shot-on-Goal
            if len(game) > len(saved_predictions):
                print(f"Tracker updated for game {game_id}")
                self.old_predictions = saved_predictions
                game = game.drop(index=np.arange(0, len(saved_predictions)), )
                game = game.reset_index(drop=True)

            # Si rien n'a changé
            else:
                print(f"Updates not found for game {game_id}")
                return saved_predictions

        # Prédiction
        predictions = self.predict(game)
        predictions_df = pd.DataFrame(predictions)
        predictions_df = pd.concat([game, predictions_df], axis=1)
        predictions_df = predictions_df.drop('is_goal', axis=1)

        # Sauvegarde de la prédiction
        self._save_predictions(game_id, predictions_df)

        if self.old_predictions is not None:
            return pd.concat([self.old_predictions, predictions_df], axis=0, ignore_index=True)

        return predictions_df