from .test_setup import TestSetUp


class TestRegisterView(TestSetUp):
    def test_user_cannot_register_without_data(self):
        response = self.client.post(self.register_url)
        self.assertEqual(response.status_code, 400)

    def test_user_cannot_register_with_invalid_email(self):
        custom_user_data = self.user_data
        custom_user_data['email'] = 'invalid_email'
        response = self.client.post(self.register_url, custom_user_data)
        self.assertEqual(response.status_code, 400)

    def test_user_cannot_register_with_short_password(self):
        custom_user_data = self.user_data
        custom_user_data['password'] = '1234567'
        response = self.client.post(self.register_url, custom_user_data)
        self.assertEqual(response.status_code, 400)
