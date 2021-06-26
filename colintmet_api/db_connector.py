from pymongo import MongoClient
import logging
import datetime


def establish_db_connection(database_url, database_port, database_name):
    try:
        client = MongoClient(database_url, database_port,
                             username='root', password='example')
        return client[database_name]
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(
            """It failed trying to get the
            connection to the mongo db""") from error


def insert_new_user(db_connection, user):
    users_collection = db_connection['users']
    try:
        users_collection.insert_one(serialize_user(user))

    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(
            f"""Error trying to insert user {user}
            and error is {error}""") from error


def serialize_user(user):
    latest_physiological_upload = datetime.datetime.now()
    return {'email': user['email'], 'gender': user['gender'],
            'birthdate': user['birthdate'], 'name': user['name'],
            'surnames': user['surnames'],
            'latest_physiological_upload': latest_physiological_upload}


def insert_survey_response(db_connection, survey_response, user_id, user_email):
    surveys_response_collection = db_connection['surveys-response']
    users_collection = db_connection['users']
    surveys_collection = db_connection['surveys']
    groups_collection = db_connection['groups']

    try:
        survey_identifier = survey_response['survey']['identifier']
        survey_data = surveys_collection.find_one(
            {"survey_identifier": survey_identifier})
        project_id = survey_data["project_id"] if survey_data else ""
        print(f"""project id is {project_id} """)

        survey_id = survey_data["_id"] if survey_data else ""
        print(f"""survey id is {survey_id} """)

        group_data = groups_collection.find_one(
            {"project_id": project_id, "members": user_id}
        )
        print(f"""group data is {group_data} """)
        group_id = group_data["_id"] if group_data else ""
        group_name = group_data["group_name"] if group_data else ""
        surveys_response_collection.insert_one(
            serialize_survey_response(
                survey_response, user_id, group_id,
                group_name, project_id, survey_id))
        users_collection.update(
            {'email': user_email},
            {'$push': {
                'finished_surveys': survey_identifier
            }}
        )
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(f"""Error trying to insert survey response
                            {survey_response} of type {type(survey_response)}
                            and error is:\n {error}""") from error


def serialize_survey_response(
        survey_response, user_id, group_id,
        group_name, project_id, generated_survey_id):
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
            'group_id': group_id, 'group_name': group_name,
            'survey_id': generated_survey_id,
            'project_id': project_id,
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
    results = [{'answer': raw_results[question_id]['results']['answer'],
               'question_id': question_id} for question_id in question_ids]
    return results


def serialize_forms(raw_results, form_ids):
    results = [{
        'form_id': raw_results[form_id]['identifier'],
        'form_title': raw_results[form_id]['question_title'],
        'results': serialize_final_questions(raw_results[form_id]['results'])}
        for form_id in form_ids]
    return results


def insert_physiological_data(db_connection, physiological_data,
                              user_id, user_email):
    physiological_data_collection = db_connection['physiological-data']
    users_collection = db_connection['users']
    try:
        max_date = [datetime.datetime(1900, 1, 1)]
        physiological_data_collection.insert_one(
            serialize_physiological_data(physiological_data, user_id, max_date))
        updated = {"latest_physiological_upload": max_date[0]}
        users_collection.update_one(
        {'email': user_email}, {'$set': updated})
    except Exception as error:
        logging.error("Couldn't update database. Error:\n%s", error)
        raise Exception(
            f"""Error trying to insert physiological data
                {physiological_data} of type {type(physiological_data)}
                and error is:\n {error}""") from error


def serialize_physiological_data(physiological_data, user_id, max_date):
    raw_data = physiological_data["formatted_result"]

    formatted_data = [format_raw_data(data, max_date) for data in raw_data]

    return {'user': user_id, 'data': formatted_data}

def format_raw_data(raw_data, max_date):
    date_to = datetime.datetime.strptime(raw_data['date_to'], '%Y-%m-%d %H:%M:%S.%f')
    if (max_date[0] < date_to):
        max_date[0] = date_to
    return {
                "unit": raw_data['unit'],
                "value": raw_data['value'],
                "date_from": datetime.datetime.strptime(raw_data['date_from'], '%Y-%m-%d %H:%M:%S.%f'),
                "date_to": date_to,
                "type":  raw_data['type'],
                "device_id": raw_data['device_id'],
                "platform": raw_data['platform']
    }

def get_profile_data(db_connection, user_email):
    profile_collection = db_connection['users']
    profile_data = profile_collection.find({"email": user_email})
    return serialize_profile_response(profile_data[0])


def serialize_profile_response(profile):
    return {'email': profile['email'], 'name': profile['name'],
            'surnames': profile['surnames'],
            'birthdate': profile['birthdate'], 'gender': profile['gender'],
            'latest_physiological_upload': profile['latest_physiological_upload']}


def modify_profile_data(db_connection, user_email, modified_data):
    profile_collection = db_connection['users']
    result = profile_collection.update_one(
        {'email': user_email}, {'$set': modified_data})

    return result.modified_count == 1


def get_finished_surveys(db_connection, user_email):
    user_collection = db_connection['users']
    user_data = user_collection.find({"email": user_email})
    return serialize_finished_surveys_response(user_data[0])


def serialize_finished_surveys_response(user_data):
    logging.info(user_data)
    logging.info("resultado")
    resul = {'finished_surveys': user_data["finished_surveys"]
                 if user_data.get("finished_surveys") else []}
    logging.info(resul)
    return {'finished_surveys': user_data["finished_surveys"]
                if user_data.get("finished_surveys") else []}

