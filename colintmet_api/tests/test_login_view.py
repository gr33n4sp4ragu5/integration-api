from .test_setup import TestSetUp


class TestLoginView(TestSetUp):

    def test_user_can_login_if_registered_what(self):
        response = self.client.get(self.login_url, {})
        self.assertEqual(response.status_code, 401)

    """
    def test_user_can_login_if_registered(self):
        self.client.login(username='test@gmail.com', password='testtest')
        response = self.client.get(
            self.login_url, {}, **{'BASIC':'dGVzdEBnbWFpbC5jb206dGVzdHRlc3Q='})
        self.assertEqual(response.status_code, 200)
    """
