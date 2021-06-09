from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from colintmet_api.db_connector import (
    establish_db_connection,
    get_profile_data
)
from colintmet_api.authentication import ColintmetTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import logging

DATABASE_NAME = 'colintmet-db'
DATABASE_URL = 'some-mongo'
DATABASE_PORT = 27017


class Profile(APIView):
    authentication_classes = (ColintmetTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            db_connection = establish_db_connection(
                DATABASE_URL, DATABASE_PORT, DATABASE_NAME)
            profile_data = get_profile_data(
                db_connection, request.user.email)
            return Response(
                {"profile_data": profile_data},
                status=status.HTTP_200_OK)
        except Exception as error:
            logging.error(
                "Error while retrieving profile data. Error is \n %s", error)
            return Response(
                {"status": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
