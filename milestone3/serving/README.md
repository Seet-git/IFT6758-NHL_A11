# Installer les package

créer un environement a partir d'un des 2 fichiers requirements (j'ai mis deux versions, une pour conda et une autre pour python)

# deifnitino des variables d'environement

créer un fichier .env dans le repertoire serving et y ajouter 
la variable WANDB_API_KEY=your_wand_db_api

# Lancer le serveur

waitress-serve --listen=localhost:5000 app:app

# Tester un call HTTP

dans un jupyter notebook ou un fichier python, executer:

WANDB_PROJECT_NAME = "IFT6758.2024-A11"
WANDB_TEAM_NAME = "youry-macius-universite-de-montreal"

data = {
    "project_name": WANDB_PROJECT_NAME,
    "entity_name": WANDB_TEAM_NAME,
    "model_name": "LogisticRegression_Distance_Angle", # valeurs possibles : LogisticRegression_Distance_Angle, LogisticRegression_Distance
}

r = requests.post("http://127.0.0.1:5000/download_registry_model", json=data)   


