from collections import defaultdict
import json

import tornado.ioloop
import tornado.web

class NoSuchObjectException(Exception):
    pass

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



class MemoryBasedRESTHandler(object):
    repo = defaultdict(dict)

    object_structs = defaultdict(lambda: ['id'])

    def get(self, object_type, id=None):
        if not object_type in repo.keys():
            raise NoSuchObjectException()
        objects = repo[object_type]
        if id is not None:
            filtered = filter(objects, lambda obj: obj['id'] == id)
            assert len(filtered) in [0, 1]
            if len(filtered) == 0:
                raise NoSuchObjectException()
            else:
                return filtered[0]
        return objects

    def post(self, object, dict):
        pass

    def patch(self, object, id, dict):
        pass

    def delete(self, object, id):
        pass

class GoogleSheetsRESTHandler(object):
    def __init__(self, connection, spreadsheet_id):
        self.gspread_connection = connect
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.gspread_connection.open_by_key(self.spreadsheet_id)

    def get(self, object_type, id=None):
        worksheet = self.spreadsheet.worksheet(object_type)
        if worksheet is None:
            raise NoSuchObjectException()

        objects = worksheet.get_all_records()

        if id is not None:
            filtered = filter(objects, lambda obj: obj['id'] == id)
            assert len(filtered) in [0, 1]
            if len(filtered) == 0:
                raise NoSuchObjectException()
            else:
                return filtered[0]

        return objects






def make_app(data_handler):
    return tornado.web.Application([
        (r'/(.*)/(.*)?', MainHandler, dict(data_handler=data_handler)),
    ])

if __name__ == '__main__':
    app = make_app(StuffHandler())
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()