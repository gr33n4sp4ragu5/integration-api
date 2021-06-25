from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from . import utils

class Login(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        access_token, refresh_token = utils.generate_tokens(request.user)

        if access_token is None or refresh_token is None:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = {
            'access_token': access_token,
            'token_expires_in': 3600,
            'token_type': "bearer",
            'refresh_token': refresh_token,
            'refresh_expires_in': 48*3600
        }

        return Response(response)
