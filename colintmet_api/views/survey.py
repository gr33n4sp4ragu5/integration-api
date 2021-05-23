from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from colintmet_api.db_connector import *
from colintmet_api.authentication import ColintmetTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import logging

DATABASE_NAME = 'colintmet-db'
DATABASE_URL = 'some-mongo'
DATABASE_PORT = 27017

class PostSurveyAnswer(APIView):
    authentication_classes = (ColintmetTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        survey_response = data
        try:
            db_connection = establish_db_connection(DATABASE_URL, DATABASE_PORT, DATABASE_NAME)
            insert_survey_response(db_connection, survey_response)
            return Response({"status": "Successfully registered"}, status = status.HTTP_201_CREATED)
        except Exception as error:
            logging.error("Error while adding survey response. Error is \n %s", error)
