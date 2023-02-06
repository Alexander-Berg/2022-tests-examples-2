import pytest
import xlrd

from . import test_user_report_util as util


@pytest.mark.now('2018-9-17T12:40')
@pytest.mark.parametrize(
    'file_format, content_type',
    [
        pytest.param('xls', 'application/vnd.ms-excel', id='xls format'),
        pytest.param(
            'xlsx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml'
            '.sheet',
            id='xls format',
        ),
    ],
)
@pytest.mark.parametrize(
    ['passport_mock', 'url', 'status', 'expected_content'],
    [
        pytest.param(
            'client1',
            '/1.0/client/client1/user',
            200,
            util.get_headers_cells(util.HEADERS + util.HEADERS_NEW_CC)
            + [
                (
                    'Moe',
                    '+79291112202',
                    'moe@mail.com',
                    'Prince',
                    'MoeCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Эконом, Комфорт',
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'KKK666',
                    '+79291112206',
                    'KKK666@mail.com',
                    'Prince666',
                    'KKKCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    util.EMPTY_CELL,  # no limit in absent role
                    util.EMPTY_CELL,
                    '',  # no tariff in absent role
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'KKK',
                    '+79291112205',
                    'KKK@mail.com',
                    'Prince',
                    'KKKCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Эконом, Комфорт',
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'Zoe',
                    '+79291112201',
                    'zoe@mail.com',
                    'ZoeTheCoolest',
                    'ZoeCostCenter',
                    'Активен',
                    'sales',
                    5000.0,
                    12345.67,
                    'Эконом',
                )
                + util.empty_cells(2)
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'Joe',
                    '+79291112203',
                    'joe@mail.com',
                    util.EMPTY_CELL,
                    'test_cost_center',
                    'Неактивен',
                    'sales',
                    5000.0,
                    util.EMPTY_CELL,
                    'Эконом',
                    'd1_1',
                    'd1 → d1_1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'ivan',
                    '+79291112204',
                    'ivan@mail.com',
                    util.EMPTY_CELL,
                    util.EMPTY_CELL,
                    'Активен',
                    'Без права самостоятельного заказа',
                    0,
                    util.EMPTY_CELL,
                    'Комфорт, Эконом, Старт',
                )
                + util.empty_cells(2)
                + util.OTHER_CC_COLUMN_VALUES,
            ],
            id='common case with ru locale',
        ),
        pytest.param(
            'client1',
            '/1.0/client/client1/user?lang=en',
            200,
            util.get_headers_cells(
                util.HEADERS_EN + util.HEADERS_NEW_CC_EN, locale='en',
            )
            + [
                (
                    'Moe',
                    '+79291112202',
                    'moe@mail.com',
                    'Prince',
                    'MoeCostCenter',
                    'Active',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Econom, Comfort',
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES_EN,
                (
                    'KKK666',
                    '+79291112206',
                    'KKK666@mail.com',
                    'Prince666',
                    'KKKCostCenter',
                    'Active',
                    util.EMPTY_CELL,
                    util.EMPTY_CELL,  # no limit in absent role
                    util.EMPTY_CELL,
                    '',  # no tariff in absent role
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES_EN,
                (
                    'KKK',
                    '+79291112205',
                    'KKK@mail.com',
                    'Prince',
                    'KKKCostCenter',
                    'Active',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Econom, Comfort',
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES_EN,
                (
                    'Zoe',
                    '+79291112201',
                    'zoe@mail.com',
                    'ZoeTheCoolest',
                    'ZoeCostCenter',
                    'Active',
                    'sales',
                    5000.0,
                    12345.67,
                    'Econom',
                )
                + util.empty_cells(2)
                + util.DEFAULT_CC_COLUMN_VALUES_EN,
                (
                    'Joe',
                    '+79291112203',
                    'joe@mail.com',
                    util.EMPTY_CELL,
                    'test_cost_center',
                    'Inactive',
                    'sales',
                    5000.0,
                    util.EMPTY_CELL,
                    'Econom',
                    'd1_1',
                    'd1 → d1_1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES_EN,
                (
                    'ivan',
                    '+79291112204',
                    'ivan@mail.com',
                    util.EMPTY_CELL,
                    util.EMPTY_CELL,
                    'Active',
                    'Without ordering privileges',
                    0,
                    util.EMPTY_CELL,
                    'Comfort, Econom, Start',
                )
                + util.empty_cells(2)
                + util.OTHER_CC_COLUMN_VALUES_EN,
            ],
            id='common case with en locale',
        ),
        pytest.param(
            'manager1',
            '/1.0/client/client1/user?department_id=d1_1',
            200,
            util.get_headers_cells(
                util.HEADERS + util.HEADERS_NEW_CC,
                department='d1_1',
                department_path='d1 → d1_1',
            )
            + [
                (
                    'Joe',
                    '+79291112203',
                    'joe@mail.com',
                    util.EMPTY_CELL,
                    'test_cost_center',
                    'Неактивен',
                    'sales',
                    5000.0,
                    util.EMPTY_CELL,
                    'Эконом',
                    'd1_1',
                    'd1 → d1_1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
            ],
            id='case with 200: manager has access to department d1_1',
        ),
        pytest.param(
            'client1',
            '/1.0/client/client1/user?department_id=d1',
            200,
            util.get_headers_cells(
                util.HEADERS + util.HEADERS_NEW_CC,
                department='d1',
                department_path='d1',
            )
            + [
                (
                    'Moe',
                    '+79291112202',
                    'moe@mail.com',
                    'Prince',
                    'MoeCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Эконом, Комфорт',
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'KKK666',
                    '+79291112206',
                    'KKK666@mail.com',
                    'Prince666',
                    'KKKCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    util.EMPTY_CELL,  # no limit in absent role
                    util.EMPTY_CELL,
                    '',  # no tariff in absent role
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'KKK',
                    '+79291112205',
                    'KKK@mail.com',
                    'Prince',
                    'KKKCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Эконом, Комфорт',
                    'd1',
                    'd1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'Joe',
                    '+79291112203',
                    'joe@mail.com',
                    util.EMPTY_CELL,
                    'test_cost_center',
                    'Неактивен',
                    'sales',
                    5000.0,
                    util.EMPTY_CELL,
                    'Эконом',
                    'd1_1',
                    'd1 → d1_1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
            ],
            id='case with department d1',
        ),
        pytest.param(
            'manager1',
            '/1.0/client/client1/user?department_id=d1',
            403,
            None,
            id='case with 403: manager has no access to department d1',
        ),
        pytest.param(
            'client1',
            '/1.0/client/client1/user?department_id=d1_2',
            200,
            util.get_headers_cells(
                util.HEADERS + util.HEADERS_NEW_CC,
                department='d1_2',
                department_path='d1 → d1_2',
            ),
            id='case with department d1_2',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.translations(
    corp=util.CORP_TRANSLATIONS, tariff=util.TARIFF_TRANSLATIONS,
)
@pytest.mark.config(
    LOCALES_CORP_SUPPORTED=['ru', 'en'],
    CORP_CATEGORIES={
        '__default__': {
            'econom': 'econom',
            'start': 'start',
            'business': 'business',
        },
    },
)
async def test_general_get_xls(
        taxi_corp_real_auth_client,
        patch,
        file_format,
        content_type,
        passport_mock,
        url,
        status,
        expected_content,
):
    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_phones_bulk(passed_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [{'id': _id, 'phone': hex_to_phone(_id)} for _id in passed_ids]

    response = await taxi_corp_real_auth_client.get(
        url, params={'format': file_format},
    )

    assert response.status == status
    if status != 200:
        return

    assert response.headers.get('Content-Type') == content_type

    book = xlrd.open_workbook(file_contents=await response.read())
    sheet = book.sheet_by_index(0)
    actual_content = [
        tuple(col.value for col in row) for row in sheet.get_rows()
    ]
    assert actual_content == expected_content


@pytest.mark.now('2018-9-17T12:40')
@pytest.mark.parametrize(
    ['passport_mock', 'url', 'cost_centers_enabled', 'expected_content'],
    [
        pytest.param(
            'manager1',
            '/1.0/client/client1/user?department_id=d1_1',
            False,
            util.get_headers_cells(
                util.HEADERS + util.HEADERS_NEW_CC,
                department='d1_1',
                department_path='d1 → d1_1',
            )
            + [
                (
                    'Joe',
                    '+79291112203',
                    'joe@mail.com',
                    util.EMPTY_CELL,
                    'test_cost_center',
                    'Неактивен',
                    'sales',
                    5000.0,
                    util.EMPTY_CELL,
                    'Эконом',
                    'd1_1',
                    'd1 → d1_1',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
            ],
            id='cost_centers_disabled',
        ),
        pytest.param(
            'manager1',
            '/1.0/client/client1/user?department_id=d1_1',
            True,
            util.get_headers_cells(
                util.HEADERS + util.HEADERS_OLD_CC + util.HEADERS_NEW_CC,
                department='d1_1',
                department_path='d1 → d1_1',
            )
            + [
                (
                    'Joe',
                    '+79291112203',
                    'joe@mail.com',
                    util.EMPTY_CELL,
                    'test_cost_center',
                    'Неактивен',
                    'sales',
                    5000.0,
                    util.EMPTY_CELL,
                    'Эконом',
                    'd1_1',
                    'd1 → d1_1',
                    'смешанный, обязателен',
                    'да',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
            ],
            id='cost_centers_enabled-by-department-id',
        ),
        pytest.param(
            'client1',
            '/1.0/client/client1/user',
            True,
            util.get_headers_cells(
                util.HEADERS + util.HEADERS_OLD_CC + util.HEADERS_NEW_CC,
            )
            + [
                (
                    'Moe',
                    '+79291112202',
                    'moe@mail.com',
                    'Prince',
                    'MoeCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Эконом, Комфорт',
                    'd1',
                    'd1',
                )
                + util.empty_cells(2)
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'KKK666',
                    '+79291112206',
                    'KKK666@mail.com',
                    'Prince666',
                    'KKKCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    util.EMPTY_CELL,  # no limit in absent role
                    util.EMPTY_CELL,
                    '',  # no tariff in absent role
                    'd1',
                    'd1',
                )
                + util.empty_cells(2)
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'KKK',
                    '+79291112205',
                    'KKK@mail.com',
                    'Prince',
                    'KKKCostCenter',
                    'Активен',
                    util.EMPTY_CELL,
                    10000.0,
                    util.EMPTY_CELL,
                    'Эконом, Комфорт',
                    'd1',
                    'd1',
                )
                + util.empty_cells(2)
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'Zoe',
                    '+79291112201',
                    'zoe@mail.com',
                    'ZoeTheCoolest',
                    'ZoeCostCenter',
                    'Активен',
                    'sales',
                    5000.0,
                    12345.67,
                    'Эконом',
                )
                + util.empty_cells(4)
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'Joe',
                    '+79291112203',
                    'joe@mail.com',
                    util.EMPTY_CELL,
                    'test_cost_center',
                    'Неактивен',
                    'sales',
                    5000.0,
                    util.EMPTY_CELL,
                    'Эконом',
                    'd1_1',
                    'd1 → d1_1',
                    'смешанный, обязателен',
                    'да',
                )
                + util.DEFAULT_CC_COLUMN_VALUES,
                (
                    'ivan',
                    '+79291112204',
                    'ivan@mail.com',
                    util.EMPTY_CELL,
                    util.EMPTY_CELL,
                    'Активен',
                    'Без права самостоятельного заказа',
                    0,
                    util.EMPTY_CELL,
                    'Комфорт, Эконом, Старт',
                )
                + util.empty_cells(4)
                + util.OTHER_CC_COLUMN_VALUES,
            ],
            id='cost_centers_enabled',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.translations(
    corp=util.CORP_TRANSLATIONS, tariff=util.TARIFF_TRANSLATIONS,
)
@pytest.mark.config(
    LOCALES_CORP_SUPPORTED=['ru', 'en'],
    CORP_CATEGORIES={
        '__default__': {
            'econom': 'econom',
            'start': 'start',
            'business': 'business',
        },
    },
)
async def test_cost_centers_rules(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        url,
        cost_centers_enabled,
        expected_content,
):
    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_phones_bulk(passed_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [{'id': _id, 'phone': hex_to_phone(_id)} for _id in passed_ids]

    config = taxi_corp_real_auth_client.server.app.config
    config.COST_CENTERS_ENABLED = cost_centers_enabled

    response = await taxi_corp_real_auth_client.get(
        url, params={'format': 'xlsx'},
    )

    assert response.status == 200

    book = xlrd.open_workbook(file_contents=await response.read())
    sheet = book.sheet_by_index(0)
    actual_content = [
        tuple(col.value for col in row) for row in sheet.get_rows()
    ]
    assert actual_content == expected_content
