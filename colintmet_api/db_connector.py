from pymongo import MongoClient
import logging
URL = 'some-mongo' # Esto va a ser que es otra url porque dockers ya tu sabes
DB_NAME = 'colintmet_db'


def establish_db_connection(url, database_name):
    try:
        client = MongoClient('some-mongo', 27017, username='root', password='example')
        return client[database_name]
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception("It failed trying to get the connection to the mongo db")


def insert_new_user(db_connection, user):
    users_collection = db_connection['users']
    try:
        inserted = users_collection.insert_one({"nome": "alucino"}).inserted_id
        return inserted
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(f"""Error trying to insert user {user} and error is {error}""")

