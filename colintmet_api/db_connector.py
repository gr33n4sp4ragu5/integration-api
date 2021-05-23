from pymongo import MongoClient
import logging
import datetime


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


def insert_survey_response(db_connection, survey_response, username):
    surveys_response_collection = db_connection['surveys-response']
    try:
        surveys_response_collection.insert_one(
            serialize_survey_response(survey_response, username))
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(f"""Error trying to insert survey response
                            {survey_response} of type {type(survey_response)}
                            and error is:\n {error}""")


def serialize_survey_response(survey_response, username):
    question_ids = survey_response['survey']['results'].keys()
    results = [survey_response['survey']['results'][question_id]['results'] for question_id in question_ids]
    start_date_time = datetime.datetime.strptime(survey_response['survey']['start_date'], '%Y-%m-%dT%H:%M:%S.%f')
    end_date_time = datetime.datetime.strptime(survey_response['survey']['end_date'], '%Y-%m-%dT%H:%M:%S.%f')
    survey_id = survey_response['survey']['identifier']
    return {'user': username, 'results': results, 'id': survey_id, 'start_date_time': start_date_time, 'end_date_time': end_date_time}
