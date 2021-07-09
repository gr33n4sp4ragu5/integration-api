from rest_framework.test import APITestCase
from django.urls import reverse

class TestSetUp(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')

        self.user_data = {
            'email': 'test@gmail.com',
            'password': 'testtest',
            'gender': 'Male',
            'birthdate': '1999-02',
            "name": "Alex",
            "surnames": "Smith White"
        }
        return super().setUp()


    def tearDown(self):
        return super().tearDown()
