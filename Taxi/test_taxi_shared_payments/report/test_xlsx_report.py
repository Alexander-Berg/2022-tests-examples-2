import datetime

import pytest
import xlrd

from taxi_shared_payments.utils import xlsx_report

_NOW = datetime.datetime.utcnow()


class SampleHeaderWidget(xlsx_report.HeaderWidget):
    def __init__(self, *, account, **kwargs):
        super().__init__(**kwargs)
        self.account = account

    @xlsx_report.header_formatter('order.name')
    def format_name(self):
        return self.account.get('name', xlsx_report.BLANK_CELL)

    @xlsx_report.header_formatter('order.age')
    def format_age(self):
        return self.account.get('age', xlsx_report.BLANK_CELL)


class SampleTableWidget(xlsx_report.TableWidget):
    def __init__(self, *, rows, **kwargs):
        super().__init__(**kwargs)
        self.rows = rows

    @staticmethod
    @xlsx_report.table_formatter('order.due_data', 12, xlsx_report.BASE_FORMAT)
    def format_due_date(_, key_translate, order):
        return order.get('due_date', xlsx_report.BLANK_CELL)

    @staticmethod
    @xlsx_report.table_formatter('order.cost', 12, xlsx_report.BASE_FORMAT)
    def format_cost(_, key_translate, order):
        return order.get('cost', xlsx_report.BLANK_CELL)


class OrderReport(xlsx_report.BaseReport):
    def __init__(self, translations, locale, account, orders):
        self.translations = translations
        self.locale = locale
        self.account = account
        self.orders = orders

    def key_translate(self, tanker_key: str, keyset: str = None) -> str:
        return self.translations.reports.get_string(tanker_key, self.locale)

    def get_widgets(self):
        header = SampleHeaderWidget(
            account=self.account, title_size=1, value_size=1,
        )
        table = SampleTableWidget(rows=self.orders, top=header.height + 1)
        return [header, table]


@pytest.mark.translations(
    reports={
        'order.title': {'ru': 'Отчет'},
        'order.age': {'ru': 'Возраст'},
        'order.name': {'ru': 'Имя'},
        'order.due_data': {'ru': 'Дата'},
        'order.cost': {'ru': 'Цена'},
    },
)
def test_order_report(cron_context):
    report = OrderReport(
        cron_context.translations,
        'ru',
        {'name': 'X', 'age': 42},
        [
            {'due_date': _NOW.isoformat(), 'cost': 150.5},
            {
                'due_date': (_NOW - datetime.timedelta(hours=5)).isoformat(),
                'cost': 150.5,
            },
        ],
    )
    data = report.to_xlsx()

    book = xlrd.open_workbook(file_contents=data)
    sheet = book.sheet_by_index(0)
    actual_content = [
        tuple(col.value for col in row if col.value)
        for row in sheet.get_rows()
    ]
    assert actual_content == [
        ('Имя', 'X'),
        ('Возраст', 42.0),
        (),
        ('Дата', 'Цена'),
        (_NOW.isoformat(), 150.5),
        ((_NOW - datetime.timedelta(hours=5)).isoformat(), 150.5),
    ]
