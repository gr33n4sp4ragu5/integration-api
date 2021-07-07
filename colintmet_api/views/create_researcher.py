from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth.hashers import make_password
from colintmet_api.authentication import ColintmetTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import logging

DATABASE_NAME = 'colintmet-db'
DATABASE_URL = 'some-mongo'
DATABASE_PORT = 27017

class RegisterResearcher(APIView):
    authentication_classes = (ColintmetTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        required_params = ['email', 'password', 'username']
        if request.user.is_superuser:
            try:
                data = request.data
                if all(key in data for key in required_params):
                    try:
                        email = self.validate_required_input(
                            required_params[0], data[required_params[0]])
                        password = self.validate_required_input(
                            required_params[1], data[required_params[1]])
                    except ValidationError as err:
                        return Response(
                            {"error": str(err.messages[0])}, status = status.HTTP_400_BAD_REQUEST)
                    try:
                        new_user = User()
                        new_user.email = email
                        new_user.username = email
                        new_user.password = make_password(password)
                        new_user.is_staff = True
                        new_user.save()
                        return Response({"status": "Successfully registered"}, status = status.HTTP_201_CREATED)
                    except Exception as exp:
                        print("Unexpected exception occurred: "+str(exp))
                        return Response({"error": "An error occurred while registering the researcher"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({"error": "Required param(s) missing, Please include and retry again"},
                                    status=status.HTTP_400_BAD_REQUEST)
            except Exception as exp:
                print("Unexpected exception occurred: "+str(exp))
                return Response({"error": "Unexpected error occurred, please report this to Admin"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(
                {"error": "Not Authorized, you are not an administrator"},
                status=status.HTTP_403_FORBIDDEN
            )


    @staticmethod
    def validate_required_input(param, value):
        if param == 'password':
            if value is not None and type(value) == str and len(value) >= 8:
                return value
            else:
                raise ValidationError('Invalid Password, password should be at least 8 characters long')

        elif param == 'email':
            if value is not None and type(value) == str and len(value) > 0:
                try:
                    validate_email(value)
                except ValidationError:
                    raise ValidationError('Invalid Email')
                else:
                    if User.objects.filter(email=value).exists():
                        raise ValidationError('E-mail already in use, please try logging in instead')
                    return value
            else:
                raise ValidationError('Invalid Email')

        else:
            raise ValidationError('Invalid Input Param Passed')
