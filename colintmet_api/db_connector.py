from pymongo import MongoClient
from bson.objectid import ObjectId
from colintmet_api.encoder import JSONEncoder
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


def insert_survey_response(db_connection, survey_response, user_id,
                           user_email):
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
            serialize_physiological_data(
                physiological_data, user_id, max_date))
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
    date_to = datetime.datetime.strptime(
        raw_data['date_to'], '%Y-%m-%d %H:%M:%S.%f')
    if (max_date[0] < date_to):
        max_date[0] = date_to
    return {
                "unit": raw_data['unit'],
                "value": raw_data['value'],
                "date_from": datetime.datetime.strptime(
                    raw_data['date_from'], '%Y-%m-%d %H:%M:%S.%f'),
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
            'latest_physiological_upload':
            profile['latest_physiological_upload']}


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


def get_physiological_data(db_connection, query_params, skip=0, limit=10000000):
    physiological_data_collection = db_connection['physiological-data']
    all_physiological_data = physiological_data_collection.find(
        query_params, {'_id': 0}).skip(skip).limit(limit)
    result = serialize_physiological_data_many(all_physiological_data)
    return result


def serialize_physiological_data_many(cursor):
    return list(cursor)


def format_query_params(query_params):
    result = {key: query_params[key] for key in query_params.keys
              if query_params[key] is not None}
    return result


def create_new_project(db_connection, project_name, survey_ids):
    projects_collections = db_connection['projects']
    insertion_result = projects_collections.insert_one(
        serialize_project(project_name, survey_ids))
    return JSONEncoder().encode(insertion_result.inserted_id)


def serialize_project(project_name, survey_ids):
    survey_ids_formatted = survey_ids.split(",")
    return {"name": project_name, "survey_ids": survey_ids_formatted}


def create_new_group(db_connection, group_name, members_ids, project_id):
    groups_collection = db_connection['groups']
    inserted_group = groups_collection.insert_one(
        serialize_new_group(group_name, members_ids, project_id))
    project_collection = db_connection['projects']
    project_collection.update(
        {"_id": ObjectId(project_id)},
        {"$push": {"group_ids": inserted_group.inserted_id}})


def serialize_new_group(group_name, members_ids, project_id):
    return {"group_name": group_name,
            "members": members_ids, "project_id": ObjectId(project_id)}


def perform_query(db_connection, collection_name, query):
    collection = db_connection[collection_name]
    return JSONEncoder().encode(list(collection.find(query)))


def get_activated_surveys(db_connection, user_id):
    groups_collection = db_connection['groups']
    projects_collection = db_connection['projects']

    project_query = groups_collection.find(
        {'members': user_id}, {'project_id': 1, '_id': 0})

    project_ids = [project['project_id'] for project in project_query]
    print(f"Printing the list of project ids associated to the user {user_id}")
    print(JSONEncoder().encode(project_ids))

    surveys_activated = projects_collection.find(
        {'_id': {'$in': project_ids}}, {'survey_ids': 1, '_id': 0})

    return {'activated_surveys': format_activated_surveys_response(
        surveys_activated)}


def format_activated_surveys_response(surveys_activated):
    list_of_lists = [survey['survey_ids'] for survey in surveys_activated]
    flattened_list = [y for x in list_of_lists for y in x]
    list_without_duplicates = list(set(flattened_list))
    return list_without_duplicates
