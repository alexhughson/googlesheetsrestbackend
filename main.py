from collections import defaultdict
import json

import tornado.ioloop
import tornado.web

def _blank(val):
    return val is None or val == ''

def _allblank(test_list):
    return reduce(test_list, lambda cur, new: cur and _blank(new), False)

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
        self.gspread_connection = connection
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.gspread_connection.open_by_key(self.spreadsheet_id)

    def _header_row(self, worksheet):
        raw_data = worksheet.row_values(1)
        def gen(row):
            for header_el in row:
                if _blank(header_el):
                    raise StopIteration
                yield header_el
        return list(gen(raw_data))

    def get(self, object_type, id=None):
        worksheet = self.spreadsheet.worksheet(object_type)
        if worksheet is None:
            raise NoSuchObjectException()

        if id is None:
            objects = worksheet.get_all_records()
            return objects

        row_idx = id + 1
        if worksheet.row_count < row_idx:
            raise NoSuchObjectException()

        header_row = self._header_row(worksheet)
        obj_row = worksheet.row_values(row_idx)
        has_data = reduce(
            lambda cell, carry: carry or not _blank(cell),
            obj_row[:len(header_row)],
            False,
        )
        if not has_data:
            raise NoSuchObjectException()
        output_object = {header: obj_row[idx] for idx, header in enumerate(header_row)}

        return output_object

    def post(self, object_type, data):

        worksheet = self.spreadsheet.worksheet(object_type)
        if worksheet is None:
            worksheet = self.spreadsheet.add_worksheet(object_type, 10, 10)
            worksheet.update_cell(1,1, 'id')

        header_row = self._header_row(worksheet)
        for column in data:
            if column not in header_row:
                worksheet.update_cell(1, len(header_row) + 1, column)
                header_row.append(column)

        first_col = worksheet.col_data(1)

        i = 0
        while i < len(first_col) and not _blank(first_col[i]):
            i += 1

        data['id'] = i
        row_values = [data.get(header_col, '') for header_col in header_row]

        i += 1  # Because the array is 0 indexed
        worksheet.insert_row(row_values, i)
        return data


def make_app(data_handler):
    return tornado.web.Application([
        (r'/(.*)/(.*)?', MainHandler, dict(data_handler=data_handler)),
    ])

if __name__ == '__main__':
    app = make_app(StuffHandler())
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()