from __future__ import print_function
import copy

from googlesheetsrestbackend.blanks import _blank, _allblank


class FakeGspread(object):
    _spreadsheet_registry = {}
    def open_by_key(self, key):
        if key not in self._spreadsheet_registry:
            self._spreadsheet_registry[key] = FakeSpreadsheet()
        return self._spreadsheet_registry[key]

class FakeSpreadsheet(object):
    _worksheets = {}

    def __init__(self):
        self._worksheets['sheet1'] = FakeWorksheet()

    def worksheets(self):
        return self._worksheets.keys()

    def worksheet(self, title):
        return self._worksheets.get(title, None)

    def add_worksheet(self, title, rows=1000, cols=26):
        self._worksheets[title] = FakeWorksheet(rows, cols)
        return self._worksheets[title]

class FakeWorksheet(object):
    def __init__(self, rows=1000, cols=26):
        a_row = [None] * cols
        self._cells = [copy.copy(a_row) for _ in xrange(rows)]

    def print_worksheet(self):
        for row in self._cells:
            print('| ', end='')
            for col in row:
                print(str(col).ljust(6), end='')
                print(' | ', end='')
            print('\n', end='')

    def row_values(self, row):
        # zero index
        row -= 1
        return self._cells[row]

    def get_all_records(self):
        return [
            {
                self._cells[0][i]: cell_val
                for i, cell_val in enumerate(cell_row)
                if not _blank(self._cells[0][i])
            }
            for cell_row in self._cells[1:]
            if not _allblank(cell_row)
        ]

    @property
    def row_count(self):
        return len(self._cells)

    @property
    def col_count(self):
        return len(self._cells[0])

    def update_cell(self, row, col, val):
        self._cells[row - 1][col - 1] = val

    def col_data(self, col):
        col -= 1
        return [
            row[col]
            for row
            in self._cells
        ]

    def insert_row(self, new_row, new_row_index):
        row_len = self.col_count

        col_difference = row_len - len(new_row)
        if col_difference < 0:
            panic()

        new_row += [None] * col_difference
        new_row_index -= 1  # zero index

        self._cells.insert(new_row_index, new_row)
