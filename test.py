import json
import unittest
from mock import patch, MagicMock

import tornado.testing

import gsheetsbackedrest.test
from excpts import NoSuchObjectException
from fake_gspread import FakeGspread
import main
import sheets_api_handler


class TestGspreadHandler(unittest.TestCase):
    def setUp(self):
        self.fakeSheet = FakeGspread()
        self.handler = sheets_api_handler.GoogleSheetsRESTHandler(
            FakeGspread(), '',
        )

    def test_base_integration(self):
        self.handler.post('object', {'key': 'value'})
        # self.fakeSheet.open_by_key('').worksheet('object').print_worksheet()
        ret_val = self.handler.get('object')
        self.assertEqual(ret_val[0]['key'], 'value')
        ret_item = self.handler.get('object', 1)
        self.assertEqual(ret_item['key'], 'value')

    def test_has_new_key(self):
        posted_first = self.handler.post('object', {'key': 'value'})
        posted_second = self.handler.post('object', {'otherkey': 'othervalue'})
        expected_keys = set(['id', 'key', 'otherkey'])
        get_first = self.handler.get('object', posted_first['id'])
        self.assertEqual(expected_keys, set(get_first.keys()))

        get_second = self.handler.get('object', posted_second['id'])
        self.assertEqual(expected_keys, set(get_second.keys()))


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


if __name__ == '__main__':
    unittest.main()
