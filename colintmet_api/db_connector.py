from pymongo import MongoClient
URL = 'mongodb://127.0.0.1:27017'
DB_NAME = 'colintmet_db'


def establish_db_connection(url, database_name):
    client = MongoClient(url)
    return client[database_name]


def insert_new_user(db_connection, user):
    users_collection = db_connection['users']
    try:
     users_collection.insert_one(user)
    except:
        raise Exception("Error trying to insert user {user}")

