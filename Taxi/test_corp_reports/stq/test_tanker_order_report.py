# pylint: disable=redefined-outer-name
import datetime

import dateutil.parser
import pytest
import xlrd

from corp_reports.internal.orders.common import structs
from corp_reports.internal.orders.tanker import report

TRANSLATIONS = {
    'corp': {
        'report.company': {'ru': 'Компания'},
        'report.period': {'ru': 'Период'},
        'report.tanker_orders_count': {
            'ru': 'Количество заказов в отчётном периоде',
        },
        'report.total_cost_with_vat': {'ru': 'Общая стоимость с НДС'},
        'report.result': {'ru': 'Итого'},
        'report.report': {'ru': 'Отчет'},
        'report.report.tanker': {'ru': 'Заправки'},
        'report.due_data': {'ru': 'Дата заказа'},
        'report.created_time': {'ru': 'Время заказа'},
        'report.user_fullname': {'ru': 'Имя пользователя'},
        'report.user_email': {'ru': 'Электронная почта'},
        'report.user_phone': {'ru': 'Телефон'},
        'report.user_class': {'ru': 'Группа'},
        'report.department': {'ru': 'Подразделение'},
        'report.old_department': {'ru': 'Подразделение (во время заказа)'},
        'report.department_path': {'ru': 'Цепочка подразделений'},
        'report.order_id': {'ru': 'Идентификатор заказа'},
        'report.fuel_station_name': {'ru': 'АЗС'},
        'report.fuel_station_address': {'ru': 'Адрес'},
        'report.fuel_station_pump': {'ru': 'Колонка'},
        'report.fuel_type': {'ru': 'Топливо'},
        'report.fuel_requested': {'ru': 'Запрос'},
        'report.fuel_filled': {'ru': 'Залито'},
        'report.status': {'ru': 'Статус'},
        'report.status.completed': {'ru': 'Завершен'},
        'report.payment_method': {'ru': 'Способ оплаты'},
        'report.payment_method.corp': {'ru': 'Кошелек'},
        'report.payment_method.card': {'ru': 'Карта'},
        'report.price_per_liter': {'ru': 'Цена за литр'},
        'report.price_without_discount': {'ru': 'Стоимость без учёта скидки'},
        'report.discount': {'ru': 'Скидка'},
        'report.price': {'ru': 'Стоимость'},
    },
}


REPORT_COLUMN_HEADERS_KEYS = (
    'report.due_data',
    'report.created_time',
    'report.user_fullname',
    'report.user_email',
    'report.user_phone',
    'report.user_class',
    'report.department',
    'report.old_department',
    'report.department_path',
    'report.order_id',
    'report.fuel_station_name',
    'report.fuel_station_address',
    'report.fuel_station_pump',
    'report.fuel_type',
    'report.fuel_requested',
    'report.fuel_filled',
    'report.status',
    'report.payment_method',
    'report.price_per_liter',
    'report.price_without_discount',
    'report.discount',
    'report.price',
)
REPORT_COLUMN_HEADERS = tuple(
    TRANSLATIONS['corp'][key]['ru'] for key in REPORT_COLUMN_HEADERS_KEYS
)


AFTER_HEADER_BLANK_COLUMNS_QTY = 18
SEPARATOR_LINE_COLUMNS_QTY = 22
TOTAL_STRING_BLANK_COLUMNS_QTY = 20
CONTENT_TYPE = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
ORDER_ROW_1 = (
    '30.11.2021',
    '10:30:00',
    'good user',
    'svyat@yandex-team.ru',
    '+79654646546',
    'role.others_name',
    'department 1',
    'department 1',
    'department 1',
    'order_id_3',
    'Тестировочная №1',
    'Кремлевская наб. 1',
    '3',
    'АИ-100 Ultimate',
    14.11,
    24.04,
    'Завершен',
    'Кошелек',
    71.34,
    950.96,
    32.75,
    2537.30,
)
ORDER_ROW_2 = (
    '30.11.2021',
    '10:30:00',
    'good user',
    'svyat@yandex-team.ru',
    '+79654646546',
    'role.others_name',
    'department 1',
    'department 1',
    'department 1',
    'order_id_1',
    'Тестировочная №1',
    'Кремлевская наб. 1',
    '3',
    'АИ-100 Ultimate',
    14.11,
    24.04,
    'Завершен',
    'Карта',
    60.23,
    849.85,
    21.64,
    1426.29,
)
TOTAL_COST = 3963.59


def _expected_content():
    return [
        (
            TRANSLATIONS['corp']['report.company']['ru'],
            '',
            '',
            'OOO Company 3',
            *[''] * AFTER_HEADER_BLANK_COLUMNS_QTY,
        ),
        (
            TRANSLATIONS['corp']['report.department']['ru'],
            '',
            '',
            'department 1',
            *[''] * AFTER_HEADER_BLANK_COLUMNS_QTY,
        ),
        (
            TRANSLATIONS['corp']['report.department_path']['ru'],
            '',
            '',
            'department 1',
            *[''] * AFTER_HEADER_BLANK_COLUMNS_QTY,
        ),
        (
            TRANSLATIONS['corp']['report.period']['ru'],
            '',
            '',
            '19.10.2021 - 26.12.2021',
            *[''] * AFTER_HEADER_BLANK_COLUMNS_QTY,
        ),
        (
            TRANSLATIONS['corp']['report.tanker_orders_count']['ru'],
            '',
            '',
            2.0,
            *[''] * AFTER_HEADER_BLANK_COLUMNS_QTY,
        ),
        (
            TRANSLATIONS['corp']['report.total_cost_with_vat']['ru'],
            '',
            '',
            TOTAL_COST,
            *[''] * AFTER_HEADER_BLANK_COLUMNS_QTY,
        ),
        tuple([''] * SEPARATOR_LINE_COLUMNS_QTY),
        REPORT_COLUMN_HEADERS,
        ORDER_ROW_1,
        ORDER_ROW_2,
        (
            *[''] * TOTAL_STRING_BLANK_COLUMNS_QTY,
            TRANSLATIONS['corp']['report.result']['ru'],
            TOTAL_COST,
        ),
    ]


@pytest.mark.parametrize(
    ['client_id', 'locale', 'since_date', 'till_date', 'expected_content'],
    [
        pytest.param(
            'client3',
            'ru',
            '2021-10-19',
            '2021-12-25',
            _expected_content(),
            id='tanker report',
        ),
    ],
)
@pytest.mark.translations(**TRANSLATIONS)
async def test_general_tanker_order_report(
        stq3_context,
        patch,
        mockserver,
        autotranslations,
        load_json,
        client_id,
        locale,
        since_date,
        till_date,
        expected_content,
):
    @mockserver.json_handler('/user_api-api/user_phones/get_bulk')
    async def _get_phones_bulk(request):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return {
            'items': [
                {'id': _id, 'phone': hex_to_phone(_id)}
                for _id in request.json['ids']
            ],
        }

    @mockserver.json_handler('/corp-orders/v1/orders/tanker/find')
    async def _get_tanker_orders(request):
        params = request.query
        limit = int(params.get('limit', 50))
        offset = int(params.get('offset', 0))
        orders = load_json('corp_orders_response.json')
        return {'orders': orders[offset : offset + limit]}

    @mockserver.json_handler('/corp-discounts/v1/admin/client/links/list')
    async def _get_client_links(request):
        return {'items': []}

    report_request = structs.OrdersReportParams(
        client_id=client_id,
        department_id='dep1',
        since=dateutil.parser.parse(since_date),
        till=dateutil.parser.parse(till_date) + datetime.timedelta(days=1),
        locale=locale,
        requested_by_ip='127.0.0.1',
    )

    report_generator = report.TankerReport(stq3_context)
    report_view_xlsx = await report_generator.generate(report_request)

    book = xlrd.open_workbook(file_contents=report_view_xlsx.to_xlsx())
    sheet = book.sheet_by_index(0)
    actual_content = [
        tuple(col.value for col in row) for row in sheet.get_rows()
    ]
    assert actual_content == expected_content
