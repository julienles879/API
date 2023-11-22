import pymysql
import environ


env = environ.Env()
environ.Env.read_env()

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