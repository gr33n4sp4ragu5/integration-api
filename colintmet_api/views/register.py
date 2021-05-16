from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth.hashers import make_password
from colintmet_api.db_connector import *

class Register(APIView):
    def post(self, request):
        required_params = ['email', 'password', 'name', 'surnames', 'birthdate', 'gender']
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
                        {"error": str(err.messages[0])}, status = status.HTTP_404_BAD_REQUEST)

                new_user = User()
                new_user.email = email
                new_user.username = email
                new_user.password = make_password(password)

                new_user.save()
                try:
                    db_connection = establish_db_connection(colintmet_api.db_connector.URL, 'colintmet_db')
                    insert_new_user(db_connection, data)
                except Exceptions as exp:
                    print("Unexpected exception occurred: "+str(exp))
                    return Response({"error": "An error occurred while trying to write in mongodb"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({"status": "Success"}, status = status.HTTP_201_CREATED)
            else:
                return Response({"error": "Required param(s) missing, Please include and retry again"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as exp:
            print("Unexpected exception occurred: "+str(exp))
            return Response({"error": "Unexpected error occurred, please report this to Admin"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
