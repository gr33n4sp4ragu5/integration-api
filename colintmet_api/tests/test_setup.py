from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class TestSetUp(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')

        self.user_data = {
            'email': 'test@gmail.com',
            'password': 'testtest',
            'gender': 'Male',
            'birthdate': '1999-02',
            "name": "Alex",
            "surnames": "Smith White"
        }
        new_user = User()
        new_user.email = self.user_data['email']
        new_user.username = self.user_data['email']
        new_user.password = make_password(self.user_data['password'])
        new_user.save()

        return super().setUp()


    def tearDown(self):
        u = User.objects.get(email = 'test@gmail.com')
        u.delete()
        return super().tearDown()
