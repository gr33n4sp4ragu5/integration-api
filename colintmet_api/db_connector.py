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
    raw_results = survey_response['survey']['results']
    question_ids = raw_results.keys()
    form_ids = list(filter(
        lambda question_id: raw_results[question_id]['results'].get('answer')
        is None, question_ids))
    question_results = serialize_final_questions(raw_results)
    forms_results = serialize_forms(raw_results, form_ids) if form_ids else []
    start_date_time = datetime.datetime.strptime(
        survey_response['survey']['start_date'], '%Y-%m-%dT%H:%M:%S.%f')
    end_date_time = datetime.datetime.strptime(
        survey_response['survey']['end_date'], '%Y-%m-%dT%H:%M:%S.%f')

    survey_id = survey_response['survey']['identifier']

    return {'id': survey_id, 'start_date_time': start_date_time,
            'end_date_time': end_date_time, 'user': user_id,
            'forms': forms_results,
            'questions': question_results}


def serialize_final_questions(raw_results):
    question_ids = raw_results.keys()
    simple_question_ids = list(filter(
        lambda question_id: raw_results[question_id]['results'].get('answer')
        is not None, question_ids))
    question_results = serialize_simple_questions(
        raw_results, simple_question_ids)
    return question_results


def serialize_simple_questions(raw_results, question_ids):
    results = [{'answer':raw_results[question_id]['results']['answer'][0]['value'] if raw_results[question_id]['answer_format'].get('answer_style') == 'SingleChoice' else raw_results[question_id]['results']['answer'],
               'question_id': question_id} for question_id in question_ids]
    return results


def serialize_forms(raw_results, form_ids):
    results = [{
        'form_id': raw_results[form_id]['identifier'],
        'form_title': raw_results[form_id]['question_title'],
        'results': serialize_final_questions(raw_results[form_id]['results'])}
        for form_id in form_ids]
    return results


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
