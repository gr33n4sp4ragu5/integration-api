from .test_setup import TestSetUp
from django.contrib.auth.models import User

class TestCreateProjectView(TestSetUp):

    def test_user_without_permissions_cannot_create_project(self):
        user = User.objects.create(username='testuser2@gmail.com')
        user.set_password('longpassword3')
        user.email = "testuser2@gmail.com"
        user.save()
        #logged_in = self.client.login(username='testuser2', password='longpassword3')
        logged_in = self.client.get(
            self.login_url, {}, **{'AUTHORIZATION':'Basic dGVzdHVzZXIyQGdtYWlsLmNvbTpsb25ncGFzc3dvcmQz'})
        print(logged_in.data)
       # self.client.login(username="test@gmail.com", password="testtest")
        #token = logged_in.data['access_token']
        response = self.client.post(self.createProjectUrl, {"project_name": "test_project", "survey_ids": "TDS,surveyTaskID"})
        self.assertEqual(response.status_code, 403)
"""
    def test_user_with_permissions_can_create_project(self):
        user = User.objects.create(username='testuser@gmail.com')
        user.set_password('longpassword3')
        user.email = "testuser@gmail.com"
        user.is_staff = True
        user.save()
        #logged_in = self.client.login(username='testuser', password='longpassword3')
        logged_in = self.client.get(
            self.login_url, {}, **{'AUTHORIZATION':'Basic dGVzdHVzZXJAZ21haWwuY29tOmxvbmdwYXNzd29yZDM='})
        print(logged_in)
        token = logged_in.data['access_token']
       # self.client.login(username="test@gmail.com", password="testtest")
        response = self.client.post(self.createProjectUrl, {"project_name": "test_project", "survey_ids": "TDS,surveyTaskID"}, **{'Bearer '+ token })
        self.assertEqual(response.status_code, 500)


    def test_user_with_permissions_can_create_project(self):
        user = User.objects.create(username='testuser')
        user.set_password('longpassword3')
        user.is_staff = True
        user.save()
        logged_in = self.client.login(username='testuser', password='longpassword3')
        print(logged_in)
       # self.client.login(username="test@gmail.com", password="testtest")
        response = self.client.post(self.createProjectUrl, {"project_name": "test_project", "survey_ids": "TDS,surveyTaskID"})
        self.assertEqual(response.status_code, 201)
"""