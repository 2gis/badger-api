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

    def test_get_default_settings(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.get('/api/auth/get')
        self.assertEqual(response.status_code, 200)
        content = json.loads(
            response.content.decode('utf-8', errors='replace'))
        self.assertEqual(10, content['settings']['launches_on_page'])
        self.assertEqual(25, content['settings']['testresults_on_page'])
        self.assertFalse(content['settings']['default_project'])
        self.assertEqual([], content['settings']['dashboards'])

    def test_update(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.post('/api/auth/update',
                          data=json.dumps({
                              'default_project': 1,
                              'launches_on_page': 25,
                              'testresults_on_page': 50}),
                          content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response = c.get('/api/auth/get')
        self.assertEqual(response.status_code, 200)
        content = json.loads(
            response.content.decode('utf-8', errors='replace'))
        self.assertEqual(25, content['settings']['launches_on_page'])
        self.assertEqual(50, content['settings']['testresults_on_page'])
        self.assertEqual(1, content['settings']['default_project'])
        self.assertEqual([], content['settings']['dashboards'])

    def test_update_dashboards(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.post('/api/auth/update',
                          data=json.dumps({
                              'dashboards': [{
                                  'name': 'first',
                                  'testplans': [1, 2, 3]
                              }, {
                                  'name': 'second',
                                  'testplans': [1, 2, 3]
                              }]}),
                          content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response = c.get('/api/auth/get')
        self.assertEqual(response.status_code, 200)
        content = json.loads(
            response.content.decode('utf-8', errors='replace'))
        dashboards = content['settings']['dashboards']
        self.assertEqual(2, len(dashboards))

    def test_update_dashboards_empty(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.post('/api/auth/update',
                          data=json.dumps({
                              'dashboards': []}),
                          content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response = c.get('/api/auth/get')
        self.assertEqual(response.status_code, 200)
        content = json.loads(
            response.content.decode('utf-8', errors='replace'))
        dashboards = content['settings']['dashboards']
        self.assertEqual(0, len(dashboards))

    def test_update_dashboards_empty_string(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.post('/api/auth/update',
                          data=json.dumps({
                              'dashboards': ''}),
                          content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response = c.get('/api/auth/get')
        self.assertEqual(response.status_code, 200)
        content = json.loads(
            response.content.decode('utf-8', errors='replace'))
        dashboards = content['settings']['dashboards']
        self.assertEqual(0, len(dashboards))

    def test_update_bad(self):
        c = Client()
        c.post('/api/auth/login/',
               data=json.dumps({
                   'username': self.user_login,
                   'password': self.user_plain_password}),
               content_type='application/json')

        response = c.get('/api/auth/get')
        self.assertEqual(response.status_code, 200)
        response = c.post('/api/auth/update',
                          data='', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_not_auth(self):
        c = Client()
        response = c.post('/api/auth/update',
                          data='', content_type='application/json')
        self.assertEqual(response.status_code, 401)
