from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from colintmet_api.db_connector import (
    establish_db_connection, get_physiological_data)
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

                data_type = request.query_params.get('data_type')
                selected_user_id = int(request.query_params.get('selected_user_id'))
                start_date = datetime.datetime.strptime(request.query_params.get('start_date'), "%Y-%m-%dT%H:%M:%S")
                end_date = datetime.datetime.strptime(request.query_params.get('end_date'), "%Y-%m-%dT%H:%M:%S")
                """
                query_params = {
                    "data.type": {"$eq": data_type} if data_type,
                    "user": selected_user_id if selected_user_id,
                    "data.date_from": ,
                    "end_date": strptime(request.query_params.get('end_date'), "YYYY-MM-DD HH:MM:SS")
                }
                """
                test_params = {"user": selected_user_id, "data": {'$elemMatch': {"date_from": {'$gte': start_date, '$lte': end_date}, "type": {'$eq': data_type}}}}
                #test_params = {"user": 29, "data": {'$elemMatch': {"type": {'$eq': "STEPS"}}}}

                physiological_data = get_physiological_data(db_connection, test_params)
                return Response(
                    {"data": physiological_data},
                    status=status.HTTP_200_OK)
            except Exception as error:
                logging.error(
                    "Error while retrieving physiological data. Error is \n %s", error)
                return Response(
                    {"status": "Something went wrong"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(
               {"error": "Not Authorized, you are not an investigator"},
               status=status.HTTP_400_BAD_REQUEST
            )
