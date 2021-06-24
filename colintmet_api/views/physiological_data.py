from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from colintmet_api.db_connector import (
    establish_db_connection, insert_physiological_data)
from colintmet_api.authentication import ColintmetTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import logging

DATABASE_NAME = 'colintmet-db'
DATABASE_URL = 'some-mongo'
DATABASE_PORT = 27017


class PostPhysiologicalData(APIView):
    authentication_classes = (ColintmetTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        physiological_data = data
        try:
            db_connection = establish_db_connection(
                DATABASE_URL, DATABASE_PORT, DATABASE_NAME)
            insert_physiological_data(
                db_connection, physiological_data, request.user.id,
                request.user.email)
            return Response(
                {"status": "Successfully added physiological data"},
                status=status.HTTP_201_CREATED)
        except Exception as error:
            logging.error(
                "Error while adding physiological data. Error is \n %s", error)
            return Response(
                {"status": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
