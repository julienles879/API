from datetime import datetime, timedelta
from decouple import Config
import os
import jwt

# Obtenez le chemin absolu vers le fichier .env
current_directory = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_directory, '.env')

config = Config(env_file_path)  # Utilisez le chemin absolu

def generate_jwt_token(utilisateur_id, username):
    secret_key = config('SECRET_KEY')
    print(secret_key)
    payload = {
        'utilisateur_id': utilisateur_id,
        'username': username,
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def validate_jwt_token(token):
    try:
        secret_key = config('SECRET_KEY')

        payload = jwt.decode(token, secret_key, algorithms=['HS256'])

        utilisateur_id = payload['utilisateur_id']
        username = payload['username']

        return utilisateur_id, username

    except jwt.ExpiredSignatureError:
        return None
    except jwt.DecodeError:
        return None
