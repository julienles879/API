import pymysql
import environ

env = environ.Env()
environ.Env.read_env()

from datetime import datetime, timedelta
from decouple import Config
import os
import jwt

current_directory = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_directory, '.env')

config = Config(env_file_path)  

def generate_jwt_token(utilisateur_id, username):
    secret_key = config('SECRET_KEY')

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
        print('utilisateur', utilisateur_id, 'username : ', username)
        return utilisateur_id, username

    except jwt.ExpiredSignatureError:
        return None
    except jwt.DecodeError:
        return None

class DatabaseConnexion:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnexion, cls).__new__(cls)
            cls._instance.connection = pymysql.connect(
                user=env('DATABASES_USER'),
                password=env('DATABASES_PASSWORD'),
                host=env('DATABASES_HOST'),
                db=env('DATABASES_NAME'),
                cursorclass=pymysql.cursors.DictCursor
            )
        return cls._instance

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor
