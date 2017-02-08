import json
from mock import MagicMock
import tornado.testing

import tornado_server as main
from googlesheetsrestbackend.exceptions import NoSuchObjectException


class TestApi(tornado.testing.AsyncHTTPTestCase):
    GET_DATA = [
        {
            'id': 1,
            'data': 'somedata'
        }
    ]
    POST_DATA = {
        'key': 'value'
    }

    def setUp(self):
        self.POST_BLOB = json.dumps(self.POST_DATA)
        super(TestApi, self).setUp()
    def get_app(self):
        self.mock_datastore = MagicMock()
        self._setup_mock_datastore()
        return main.make_app(self.mock_datastore)

    def _setup_mock_datastore(self):
        self.mock_datastore.get.return_value = self.GET_DATA

    def test_sanity(self):
        resp = self.fetch('/object/')
        self.assertEqual(resp.code, 200)
        json.loads(resp.body)

    def test_get(self):
        resp = self.fetch('/object/')
        self.assertEqual(resp.code, 200)

        self.mock_datastore.get.assert_called_once()
        self.mock_datastore.get.assert_called_with('object', None)
        json_data = json.loads(resp.body)
        self.assertEqual(json_data, self.GET_DATA)

    def test_get_id(self):
        resp = self.fetch('/object/1')
        self.assertEqual(resp.code, 200)
        self.mock_datastore.get.assert_called_once()
        self.mock_datastore.get.assert_called_with('object', 1)

    def test_get_nosuch(self):
        self.mock_datastore.get.side_effect = NoSuchObjectException
        resp = self.fetch('/object/')
        self.assertEqual(resp.code, 404)

    def test_post(self):
        resp = self.fetch('/object/', method='POST', body=self.POST_BLOB)
        self.assertEqual(resp.code, 200)
        self.mock_datastore.post.assert_called_once()
        self.mock_datastore.post.assert_called_with('object', self.POST_DATA)