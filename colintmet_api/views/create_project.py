from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from colintmet_api.db_connector import (
    establish_db_connection, create_new_project
)
from colintmet_api.authentication import ColintmetTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import logging

DATABASE_NAME = 'colintmet-db'
DATABASE_URL = 'some-mongo'
DATABASE_PORT = 27017


class PostNewProject(APIView):
    authentication_classes = (ColintmetTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        if request.user.is_staff:
            try:
                project_name = data["project_name"]
                survey_ids = data["survey_ids"]
                db_connection = establish_db_connection(
                    DATABASE_URL, DATABASE_PORT, DATABASE_NAME)
                create_new_project(
                    db_connection, project_name, survey_ids)
                return Response(
                    {"status": "Successfully created new project"},
                    status=status.HTTP_201_CREATED)
            except Exception as error:
                logging.error(
                    "Error while creating project. Error is \n %s", error)
                return Response(
                    {"status": "Something went wrong"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(
                {"error": "Not Authorized, you are not a researcher"},
                status=status.HTTP_403_FORBIDDEN
            )
