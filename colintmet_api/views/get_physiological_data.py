from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from colintmet_api.db_connector import (
    establish_db_connection, get_physiological_data)
from colintmet_api.exceptions import FilteringByDateException
from colintmet_api.authentication import ColintmetTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import logging
import datetime

DATABASE_NAME = 'colintmet-db'
DATABASE_URL = 'some-mongo'
DATABASE_PORT = 27017


class GetPhysiologicalData(APIView):
    authentication_classes = (ColintmetTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.is_staff:

            try:
                db_connection = establish_db_connection(
                    DATABASE_URL, DATABASE_PORT, DATABASE_NAME)
                raw_user_id = request.query_params.get('selected_user_id')
                raw_start_date = request.query_params.get('start_date')
                raw_end_date = request.query_params.get('end_date')
                skip = request.query_params.get('skip')
                limit = request.query_params.get('limit')

                data_type = request.query_params.get('data_type')
                selected_user_id = int(raw_user_id) if raw_user_id else None
                start_date = datetime.datetime.strptime(
                    raw_start_date, "%Y-%m-%dT%H:%M:%S") if raw_start_date else None
                end_date = datetime.datetime.strptime(
                    raw_end_date, "%Y-%m-%dT%H:%M:%S") if raw_end_date else None

                filtering_params = get_filtering_params(
                    data_type, selected_user_id, start_date, end_date)

                physiological_data = get_physiological_data(
                    db_connection, filtering_params, skip=int(skip),
                     limit=int(limit)) if skip is not None and limit is not None else get_physiological_data(
                    db_connection, filtering_params)
                return Response(
                    {"data": physiological_data},
                    status=status.HTTP_200_OK)
            except FilteringByDateException as error:
                logging.error(
                    "Error while retrieving physiological data. Error is \n%s",
                    error)
                return Response(
                    {"status": error.message},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as error:
                logging.error(
                    "Error while retrieving physiological data. Error is \n%s",
                    error)
                return Response(
                    {"status": "Something went wrong"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(
               {"error": "Not Authorized, you are not an investigator"},
               status=status.HTTP_400_BAD_REQUEST
            )


def get_filtering_params(data_type, selected_user_id, start_date, end_date):
    if(data_type and selected_user_id and start_date and end_date):
        return {"user": selected_user_id,
                "data": {'$elemMatch':
                         {"date_from": {'$gte': start_date, '$lte': end_date},
                          "type": {'$eq': data_type}}}}
    elif(data_type and start_date and end_date):
        return {"data": {'$elemMatch':
                         {"date_from": {'$gte': start_date, '$lte': end_date},
                          "type": {'$eq': data_type}}}}
    elif(data_type and selected_user_id):
        return {"user": selected_user_id,
                "data": {'$elemMatch': {"type": {'$eq': data_type}}}}
    elif(selected_user_id and start_date and end_date):
        return {"user": selected_user_id,
                "data":
                {'$elemMatch':
                 {"date_from": {'$gte': start_date, '$lte': end_date}}}}
    elif(data_type):
        return {"data": {'$elemMatch': {"type": {'$eq': data_type}}}}
    elif(selected_user_id):
        return {"user": selected_user_id}
    elif(start_date and end_date):
        return {"data":
                {'$elemMatch':
                 {"date_from": {'$gte': start_date, '$lte': end_date}}}}
    elif(data_type is None and selected_user_id is None and start_date is None and end_date is None):
        return {}
    else:
        raise FilteringByDateException(
         "You must especify both start and end time if you want to filter by time")
