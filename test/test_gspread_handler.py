import unittest

from .mock_gspread import FakeGspread
from googlesheetsrestbackend import sheets_api_handler


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