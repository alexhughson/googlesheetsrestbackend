from excpts import NoSuchObjectException
from blanks import _blank, _allblank

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
