import unittest
from django.test import TestCase, Client

class DjangoPluginTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_thing(self):
        resp = self.client.get('/object')
        self.assertEqual(resp.status_code, 200)

