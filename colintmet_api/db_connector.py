from pymongo import MongoClient
import logging
import datetime
import copy


def establish_db_connection(database_url, database_port, database_name):
    try:
        client = MongoClient(database_url, database_port, username='root', password='example')
        return client[database_name]
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception("It failed trying to get the connection to the mongo db")


def insert_new_user(db_connection, user):
    users_collection = db_connection['users']
    try:
        users_collection.insert_one(serialize_user(user))

    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(f"""Error trying to insert user {user} and error is {error}""")


def serialize_user(user):
    return {'email': user['email'], 'gender': user['gender'],
            'birthdate': user['birthdate'], 'name': user['name'],
            'surnames': user['surnames']}


def insert_survey_response(db_connection, survey_response, user_id):
    surveys_response_collection = db_connection['surveys-response']
    try:
        surveys_response_collection.insert_one(
            serialize_survey_response(survey_response, user_id))
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(f"""Error trying to insert survey response
                            {survey_response} of type {type(survey_response)}
                            and error is:\n {error}""")


def serialize_survey_response(survey_response, user_id):
    question_ids = survey_response['survey']['results'].keys()
    raw_results = survey_response['survey']['results']
    results = [{'answer': raw_results[question_id]['results']['answer'],
               'question_id': question_id} for question_id in question_ids]

    return {'user': user_id, 'results': results}


def insert_physiological_data(db_connection, physiological_data, user_id):
    physiological_data_collection = db_connection['physiological-data']
    try:
        physiological_data_collection.insert_one(
            serialize_physiological_data(physiological_data, user_id))
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(f"""Error trying to insert physiological data
                            {physiological_data} of type {type(physiological_data)}
                            and error is:\n {error}""")


def serialize_physiological_data(physiological_data, user_id):
    return {'user': user_id, 'data': physiological_data}
