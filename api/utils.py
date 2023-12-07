import os
from decouple import Config
import jwt
import environ

env = environ.Env()
environ.Env.read_env()

current_directory = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_directory, '.env')

config = Config(env_file_path)


# Vue qui génère le token
def generate_jwt_token(utilisateur_id, username):
    secret_key = config('SECRET_KEY')

    payload = {
        'utilisateur_id': utilisateur_id,
        'username': username,
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


# Vue qui valide le token
def validate_jwt_token(token):
    try:
        secret_key = config('SECRET_KEY')

        payload = jwt.decode(token, secret_key, algorithms=['HS256'])

        utilisateur_id = payload['utilisateur_id']
        username = payload['username']
        print('utilisateur', utilisateur_id, 'username : ', username)
        return utilisateur_id, username

    except jwt.ExpiredSignatureError:
        return None
    except jwt.DecodeError:
        return None
