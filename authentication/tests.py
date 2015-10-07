from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

import json


class TestsBase(TestCase):
    correct_codes = [200, 201]
    user = None
    user_login = 'user'
    user_plain_password = 'qweqwe'

    def setUp(self):
        self.user = User.objects.create_user(self.user_login,
                                             'user@domain.tld',
                                             self.user_plain_password)
        self.user.save()

    def tearDown(self):
        self.user.delete()


class AuthTests(TestsBase):

    def test_login(self):
        c = Client()
        response = c.post('/api/auth/login/',
                          data=json.dumps({
                              'username': self.user_login,
                              'password': self.user_plain_password}),
                          content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        c = Client()
        response = c.post('/api/auth/login/',
                          data=json.dumps({
                              'username': self.user_login,
                              'password': 'wrong_password'}),
                          content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_get(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.get('/api/auth/get')
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.get('/api/auth/logout/')
        self.assertEqual(response.status_code, 200)
