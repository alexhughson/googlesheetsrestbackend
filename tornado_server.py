from collections import defaultdict
import json

import tornado.ioloop
import tornado.web

from googlesheetsrestbackend.exceptions import NoSuchObjectException
from test.test_gspread_handler import FakeGspread
from googlesheetsrestbackend.sheets_api_handler import GoogleSheetsRESTHandler


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, data_handler):
        self.data_handler = data_handler

    def get(self, object_type, id_val=None):
        if id_val is not None:
            try:
                id_val = int(id_val)
            except ValueError:
                id_val = None
        try:
            data_returned = self.data_handler.get(object_type, id_val)
        except NoSuchObjectException:
            self.set_status(404)
            return
        self.write(json.dumps(data_returned))

    def post(self, object_type, *args):
        data = self.request.body
        parsed_data = json.loads(data)
        self.data_handler.post(object_type, parsed_data)


def make_app(data_handler):
    return tornado.web.Application([
        (r'/(.*)/(.*)?', MainHandler, dict(data_handler=data_handler)),
    ])

if __name__ == '__main__':
    app = make_app(GoogleSheetsRESTHandler(FakeGspread()))
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()