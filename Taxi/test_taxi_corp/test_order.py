# pylint: disable=too-many-lines
# pylint: disable=redefined-outer-name

import datetime
import typing
from unittest import mock

import bson
import pytest

from taxi.clients import archive_api
from taxi.clients import experiments3
from taxi.clients import integration_api

from taxi_corp.api.common import codes
from taxi_corp.api.common import orderinfo
from taxi_corp.internal import consts
from test_taxi_corp import request_util as util

_NOW = datetime.datetime(2016, 3, 19, 12, 40)
CLASS_EXPRESS = 'express'
CLASS_COURIER = 'courier'
NEW_COST_CENTER_VALUES = [
    {'id': 'cost_center', 'title': 'Центр затрат', 'value': 'командировка'},
]
COMBO_ORDER = {'delivery_id': 'delivery1'}


def _err400(error_obj=None, text=None, code=None):
    if code is None:
        code = error_obj.error_code
    if text is None:
        text = error_obj.text

    return {
        'errors': [{'text': text, 'code': code}],
        'message': 'Invalid input',
        'code': 'REQUEST_VALIDATION_ERROR',
        'details': {'fields': [{'message': text, 'code': code}]},
    }


def _err404(text=None, code=None):
    return {
        'errors': [{'text': text, 'code': code}],
        'message': text,
        'code': code,
    }


def hex_to_phone(hex_phone):
    phone = str(hex_phone).strip('a')
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone


@pytest.fixture
def request_mock(db, taxi_corp_auth_app, taxi_corp_auth_client):
    request_info = mock.Mock(locale='ru')
    return mock.MagicMock(
        db=db,
        app=taxi_corp_auth_app,
        cache=mock.Mock(request_info=request_info),
    )


PERIOD_SEARCH_CASES = [
    # successful cases
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_due='2016-03-19T00:00:00+0300',
            till_due='2016-03-22T00:00:00+0300',
        ),
        200,
        ['order2', 'order3', 'order4'],
        id='period-due-ok',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_due='2100-03-19T00:00:00+0300',
            till_due='2100-03-22T00:00:00+0300',
        ),
        200,
        [],
        id='period-due-in-future-ok',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_finished='2016-03-19T00:00:00+0300',
            till_finished='2016-03-22T00:00:00+0300',
        ),
        200,
        ['order4'],  # orders 2 and 3 are not finished
        id='period-finished-ok',
    ),
    # failure cases
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_due='2016-03-19T00:00:00+0300',
            till_due='2016-03-22T00:00:00',  # missing timezone
        ),
        400,
        _err400(
            codes.VALIDATE_REQUESTS_INVALID_FORMAT_FIELD,
            text='invalid format for till_due',
        ),
        id='period-due-fail-wrong-format',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(since_due='2016-03-19T00:00:00+0300'),
        400,
        _err400(
            codes.VALIDATE_REQUESTS_MUST_PROVIDE_BOTH,
            text='both since_due and till_due should be provided',
        ),
        id='period-due-fail-both-args',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(till_finished='2016-03-22T00:00:00+0300'),
        400,
        _err400(
            codes.VALIDATE_REQUESTS_MUST_PROVIDE_BOTH,
            text='both since_finished and till_finished should be provided',
        ),
        id='period-finished-fail-need-both-args',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_due='2016-03-19T00:00:00+0300',
            till_due='2016-03-22T00:00:00+0300',
            since_finished='2016-03-19T00:00:00+0300',
            till_finished='2016-03-22T00:00:00+0300',
        ),
        400,
        _err400(codes.VALIDATE_REQUESTS_MUST_CHOOSE_ONE_PERIOD),
        id='period-both-fail-choose-one-pair',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_due='2020-03-19T00:00:00+0300',
            till_due='2020-03-18T00:00:00+0300',
        ),
        400,
        _err400(
            codes.MUST_BE_LESS_THAN,
            text='since date must be less than till date',
        ),
        id='period-due-fail-since-must-be-less',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_finished='2020-03-19T00:00:00+0300',
            till_finished='2100-03-22T00:00:00+0300',
        ),
        400,
        _err400(
            codes.VALIDATE_REQUESTS_FUTURE_DATE,
            text='till_finished should not be in future',
        ),
        id='period-finished-fail-value-in-future',
    ),
    pytest.param(
        'client1',
        'client1',
        None,
        dict(
            since_due='2020-03-01T00:00:00+0300',
            till_due='2020-05-03T00:00:00+0300',
        ),
        400,
        _err400(
            codes.VALIDATE_REQUESTS_PERIOD_TOO_LARGE,
            'since date and till date should not differ for more than 31 days',
        ),
        id='period-due-fail-period-too-large',
    ),
]
SEARCH_ERROR_CASES = [
    pytest.param(
        'client1',
        'client1',
        None,
        {'search': '3'},
        400,
        _err400(codes.VALIDATE_REQUESTS_SEARCH_TOO_SHORT),
        id='search-string-too-short',
    ),
]


@pytest.mark.parametrize(
    [
        'passport_mock',
        'client_id',
        'user_id',
        'url_args',
        'expected_status',
        'expected_ids_or_errors',
    ],
    [
        (
            'client1',
            'client1',
            None,
            {},
            200,
            ['order2', 'order3', 'order1', 'order1_missedcolor', 'order4'],
        ),
        (
            'client1',
            'client1',
            'user1',
            {'due_date_to': '2016-03-24T21:00:00+00:00'},
            200,
            ['order2', 'order3', 'order4'],
        ),
        (
            'client1',
            'client1',
            None,
            {'sorting_direction': '1', 'limit': '2', 'skip': '1'},
            200,
            ['order3', 'order2'],
        ),
        ('client5', 'client5', None, {}, 200, ['order7', 'order5']),
        (
            'client1',
            'client1',
            None,
            {'department_id': 'd1'},
            200,
            ['order2', 'order3', 'order1', 'order1_missedcolor'],
        ),
        (
            'client1',
            'client1',
            None,
            {'department_id': 'd1', 'include_subdepartments': '1'},
            200,
            ['order2', 'order3', 'order1', 'order1_missedcolor', 'order4'],
        ),
        (
            'client1',
            'client1',
            None,
            {'department_id': 'not_found', 'include_subdepartments': '1'},
            404,
            _err404(text='Department not found', code='GENERAL'),
        ),
        (
            'secretary5',
            'client5',
            None,
            {'department_id': 'd5'},
            200,
            ['order5'],
        ),
        ('client3', 'client3', None, {'department_id': 'd3'}, 200, ['order8']),
        (
            'client3',
            'client3',
            None,
            {'department_id': 'd3', 'include_subdepartments': '1'},
            200,
            ['order8', 'order9'],
        ),
        (
            'client3',
            'client3',
            None,
            {'department_id': 'd3_1'},
            200,
            ['order9'],
        ),
        (
            'client3',
            'client3',
            None,
            {'department_id': 'd3_1', 'include_subdepartments': '1'},
            200,
            ['order9'],
        ),
        ('manager1', 'client1', 'user2', {}, 200, ['order4']),
        ('client1', 'client1', None, {'search': 'order2'}, 200, ['order2']),
        ('client1', 'client1', None, {'search': 'order9'}, 200, []),
        (
            'client1',
            'client1',
            None,
            {'department_id': 'd1', 'search': 'order2'},
            200,
            ['order2'],
        ),
        (
            'client1',
            'client1',
            None,
            {'department_id': 'd1', 'search': 'order9'},
            200,
            [],
        ),
        (
            'client9',
            'client9',
            None,
            {'search': 'wow_cost'},
            200,
            ['order15', 'order16', 'order17'],
        ),
        ('client9', 'client9', None, {'search': 'user_cost'}, 200, []),
        (
            'client9',
            'client9',
            None,
            {'search': 'cabinet_cost'},
            200,
            ['order18'],
        ),
    ]
    + PERIOD_SEARCH_CASES
    + SEARCH_ERROR_CASES,
    indirect=['passport_mock'],
)
@pytest.mark.config(
    CORP_DEPARTMENT_FILTER_IN_ORDER_ENABLED=True,
    CORP_SEARCH_ORDERS_BY_COSTCENTER_ENABLED=True,
)
async def test_general_get_filter(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        client_id,
        user_id,
        url_args,
        expected_status,
        expected_ids_or_errors,
):
    @patch(
        'taxi_corp.clients.corp_combo_orders.'
        'CorpComboOrdersClient.get_orders_list',
    )
    async def _get_orders_list(*args, **kwargs):
        return {'orders': [{'id': 'order4'}]}

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/{}{}/order'.format(
            client_id, '/user/%s' % user_id if user_id else '',
        ),
        params=url_args,
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
    if expected_status == 200:
        response_ids = [item['_id'] for item in response_json['items']]
        assert response_ids == expected_ids_or_errors
    else:
        assert response_json == expected_ids_or_errors


@pytest.mark.parametrize(
    ['client_id', 'expected_result'],
    [
        (
            'client1',
            {
                'amount': 5,
                'sorting_direction': -1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'due_date',
                'items': [
                    {
                        '_id': 'order2',
                        'application': 'android',
                        'application_translate': 'Мобильный телефон',
                        'status': {
                            'simple': 'active',
                            'full': 'driving',
                            'description': 'Такси приедет через 3245 мин.',
                        },
                        'due_date': '2016-03-21T18:45:17',
                        'corp_user': {'fullname': 'Zoe', 'user_id': 'user1'},
                        'cost': 690.0,
                        'cost_with_vat': '814.20',
                        'class': 'comfort',
                        'source': {
                            'fullname': (
                                'Россия, Москва, улица Тимура Фрунзе, 11к9'
                            ),
                        },
                        'destination': {
                            'fullname': (
                                'Россия, Москва, Большая Никитская улица, 14'
                            ),
                        },
                        'cost_center': 'cabinet defined cost center',
                    },
                    {
                        '_id': 'order3',
                        'application': 'corpweb',
                        'application_translate': 'Личный кабинет',
                        'status': {
                            'simple': 'active',
                            'full': 'search',
                            'description': 'Такси приедет через 1805 мин.',
                        },
                        'due_date': '2016-03-20T18:45:20',
                        'corp_user': {'fullname': 'Zoe', 'user_id': 'user1'},
                        'source': {
                            'fullname': (
                                'Россия, Москва, улица Тимура Фрунзе, 12'
                            ),
                        },
                        'class': 'econom',
                        'cost_center': 'cabinet defined cost center',
                    },
                    {
                        '_id': 'order1',
                        'application': 'iphone',
                        'application_translate': 'Мобильный телефон',
                        'status': {
                            'simple': 'finished',
                            'full': 'complete',
                            'description': '',
                        },
                        'due_date': '2016-03-24T21:37:17',
                        'finished_date': '2016-03-24T21:47:17',
                        'corp_user': {'fullname': 'Zoe', 'user_id': 'user1'},
                        'class': 'econom',
                        'cost': 540.0,
                        'cost_with_vat': '637.20',
                        'source': {
                            'fullname': (
                                'Россия, Москва, улица Тимура Фрунзе, 11к8'
                            ),
                        },
                        'destination': {
                            'fullname': (
                                'Россия, Москва, Большая Никитская улица, 13'
                            ),
                        },
                        'cost_center': 'user defined cost center',
                    },
                    {
                        '_id': 'order1_missedcolor',
                        'application': 'iphone',
                        'application_translate': 'Мобильный телефон',
                        'status': {
                            'simple': 'finished',
                            'full': 'complete',
                            'description': '',
                        },
                        'due_date': '2016-03-24T21:37:17',
                        'finished_date': '2016-03-24T21:47:17',
                        'corp_user': {'fullname': 'Zoe', 'user_id': 'user1'},
                        'class': 'econom',
                        'cost': 540.0,
                        'cost_with_vat': '637.20',
                        'source': {
                            'fullname': (
                                'Россия, Москва, улица Тимура Фрунзе, 11к8'
                            ),
                        },
                        'destination': {
                            'fullname': (
                                'Россия, Москва, Большая Никитская улица, 13'
                            ),
                        },
                        'cost_center': 'user defined cost center',
                    },
                    {
                        '_id': 'order4',
                        'application': 'callcenter',
                        'application_translate': 'КЦ',
                        'status': {
                            'full': 'complete',
                            'simple': 'finished',
                            'description': '',
                        },
                        'due_date': '2016-03-19T12:35:20',
                        'finished_date': '2016-03-19T12:55:20',
                        'corp_user': {'fullname': 'Moe', 'user_id': 'user2'},
                        'cost': 670.0,
                        'cost_with_vat': '790.60',
                        'class': 'econom',
                        'source': {
                            'fullname': (
                                'Россия, Москва, улица Льва Толстого, 16'
                            ),
                        },
                        'cost_center': '',
                    },
                ],
            },
        ),
        (
            'client8',
            {
                'amount': 2,
                'sorting_direction': -1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'due_date',
                'items': [
                    {
                        '_id': 'order14',
                        'application': 'android',
                        'application_translate': 'Мобильный телефон',
                        'status': {
                            'simple': 'active',
                            'full': 'transporting',
                            'description': 'Выполняется заказ',
                        },
                        'due_date': '2020-03-21T10:30:00',
                        'corp_user': {
                            'user_id': 'user8',
                            'fullname': 'door-to-door guy',
                        },
                        'class': 'express',
                        'source': {
                            'extra_data': {'contact_phone': '+79291112299'},
                            'fullname': (
                                'Россия, Москва, улица Тимура Фрунзе, 11к9'
                            ),
                        },
                        'destination': {
                            'extra_data': {'contact_phone': '+79290009933'},
                            'fullname': (
                                'Россия, Москва, Большая Никитская улица, 14'
                            ),
                        },
                        'cost_center': '',
                        'cost': 690.0,
                        'cost_with_vat': '814.20',
                    },
                    {
                        '_id': 'order13',
                        'application': 'android',
                        'application_translate': 'Мобильный телефон',
                        'status': {
                            'simple': 'active',
                            'full': 'transporting',
                            'description': 'Выполняется заказ',
                        },
                        'due_date': '2020-03-20T16:00:00',
                        'corp_user': {
                            'user_id': 'user8',
                            'fullname': 'door-to-door guy',
                        },
                        'class': 'express',
                        'source': {
                            'extra_data': {
                                'apartment': '2',
                                'floor': '3',
                                'comment': 'source_comment',
                                'contact_phone': '+79291112299',
                            },
                            'fullname': (
                                'Россия, Москва, улица Тимура Фрунзе, 11к9'
                            ),
                            'porchnumber': '1',
                        },
                        'destination': {
                            'extra_data': {
                                'apartment': '9',
                                'floor': '5',
                                'comment': 'dest_comment',
                                'contact_phone': '+79290009933',
                            },
                            'fullname': (
                                'Россия, Москва, Большая Никитская улица, 14'
                            ),
                            'porchnumber': '98',
                        },
                        'cost_center': '',
                        'cost_centers': NEW_COST_CENTER_VALUES,
                        'cost': 690.0,
                        'cost_with_vat': '814.20',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.translations(
    corp={
        'order.order_is_running': {'ru': 'Выполняется заказ'},
        'order.taxi_on_the_way': {'ru': 'Такси в пути'},
        'order.taxi_will_arrive_in_time': {
            'ru': 'Такси приедет через {minutes:d} мин.',
        },
        'report.app.mobile': {'ru': 'Мобильный телефон'},
        'report.app.corpweb': {'ru': 'Личный кабинет'},
        'report.app.callcenter': {'ru': 'КЦ'},
    },
)
async def test_general_get_response(
        taxi_corp_auth_client,
        acl_access_data_patch,
        patch,
        client_id,
        expected_result,
):
    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        return [
            {'id': phone_id, 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/order'.format(client_id),
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == expected_result


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['client_id', 'order_id', 'order_search', 'expected_result'],
    [
        (
            'client1',
            'order1',
            {
                'cancel_disabled': False,
                'cancel_rules': {
                    'message': 'message',
                    'state': 'free',
                    'title': 'title',
                },
            },
            {
                '_id': 'order1',
                'application': 'iphone',
                'application_translate': 'Мобильный телефон',
                'status': {
                    'simple': 'finished',
                    'full': 'complete',
                    'description': '',
                },
                'due_date': '2016-03-24T21:37:17',
                'local_due_date': '2016-03-25T00:37:17+0300',
                'finished_date': '2016-03-24T21:47:17',
                'performer': {
                    'car': (
                        'Volkswagen Caravelle коричневый_from_tanker КС67477'
                    ),
                    'fullname': 'Гарольд',
                    'phone': '',
                },
                'created': '2016-03-24T21:27:17',
                'extra_contact_phone': '+79169222964',
                'start_waiting_time': '2016-03-24T21:40:07',
                'started_date': '2016-03-24T21:40:17',
                'corp_user': {
                    'user_id': 'user1',
                    'fullname': 'Zoe',
                    'phone': '+79291112201',
                    'role_id': '9d108c92a4f5449f966c1bea0ccafc28',
                    'role_name': 'role.cabinet_only_name',
                    'nickname': 'ZoeTheCoolest',
                },
                'destination': {
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'source': {
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к8',
                    'geopoint': ['37.5887876121', '55.734141752'],
                },
                'cost': 540,
                'cost_with_vat': '637.20',
                'class': 'econom',
                'cost_center': 'user defined cost center',
                'created_by': '+79291112201',
            },
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'role.cabinet_only_name': {'ru': 'role.cabinet_only_name'},
        'report.app.mobile': {'ru': 'Мобильный телефон'},
    },
    color={'800000': {'ru': 'коричневый_from_tanker'}},
)
async def test_single_get_archive_api_timeout(
        taxi_corp_auth_client,
        patch,
        client_id,
        order_id,
        order_search,
        expected_result,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_search')
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'orders': [order_search]}, headers={},
        )

    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _get_order_by_id(*args, **kwargs):
        raise archive_api.RequestTimeoutError(
            'Request to archive-api timed out',
        )

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'id': 'phone_id', 'phone': '+79165555555'}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone')
    async def _get_user_phone(phone_id, *args, **kwargs):
        phone = hex_to_phone(phone_id)
        return {'id': bson.ObjectId(phone_id), 'phone': phone}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        return [
            {'id': phone_id, 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch('taxi_corp.internal.territories_manager.get_nearest_zone')
    async def _get_nearest_zone(*args, **kwargs):
        return 'moscow'

    @patch('taxi_corp.internal.tariffs_manager.get_tariff_settings')
    async def _get_tariff_settings(*args, **kwargs):
        return {'tz': 'Europe/Moscow'}

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/order/{}{}'.format(
            client_id,
            order_id,
            '?show_cancel_text=true' if order_search else '',
        ),
    )

    assert response.status == 200
    assert await response.json() == expected_result


@pytest.mark.parametrize(
    ['client_id', 'user_id', 'url_args', 'expected_code'],
    [('client1', 'client3', {}, 404)],
)
async def test_general_get_fail(
        taxi_corp_auth_client,
        acl_access_data_patch,
        client_id,
        user_id,
        url_args,
        expected_code,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}{}/order'.format(
            client_id, '/user/%s' % user_id if user_id else '',
        ),
        params=url_args,
    )
    response_json = await response.json()
    assert response.status == expected_code, response_json


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(corp_users='for_general_post_test')
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+7'],
            'matches': ['^7'],
        },
    ],
    CORP_ENABLE_LOOKUP_TTL_CONTROL=True,
)
@pytest.mark.parametrize(
    'client, prefix',
    [
        ('taxi_corp_real_auth_client', ''),
        ('taxi_corp_tvm_client', '/internal'),
    ],
    indirect=['client'],
)
@pytest.mark.parametrize(
    'passport_mock, client_id, post_content',
    [
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(),
            id='client_postpaid',
        ),
        pytest.param(
            'client2',
            'client2',
            util.make_order_request(),
            id='client_prepaid',
        ),
        pytest.param(
            'manager1',
            'client1',
            util.make_order_request(
                city='unknown_city_id', phone='+71231234567', zone_name=None,
            ),
            id='department_manager',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(zone_name=None),
            id='no_zone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                exclude_fields=('comment', 'requirements', 'destination'),
            ),
            id='without_comment_requirements_destination',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                phone='+70001112233',
                exclude_fields=('comment', 'requirements', 'destination'),
            ),
            id='phone_without_comment_requirements_destination',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                source=util.make_location_without('locality'),
            ),
            id='source_without_locality',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                destination=util.make_location_without('locality'),
            ),
            id='destination_without_locality',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(due='2016-03-20T15:00:00Z'),
            id='due_more_now',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                interim_destinations=[
                    util.make_location_with(country='Казахстан'),
                ],
            ),
            id='interim_destinations_one_item',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                interim_destinations=[
                    util.make_location_with(country='Казахстан'),
                    util.make_location_with(country='Узбекистан'),
                    util.make_location_with(country='Эстония'),
                ],
            ),
            id='interim_destinations_some_items',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(phone='+70000000011'),
            id='client_order',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(city=None, zone_name=None),
            id='missing_zone_and_city',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                city='unknown_city_id', zone_name='unknown_zone_name',
            ),
            id='invalid_city_and_zone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(zone_name='unknown_zone_name'),
            id='invalid_zone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(city='unknown_city_id', zone_name=None),
            id='invalid_city_missing_zone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(offer='offer_id'),
            id='test_offer',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                cost_center='123',
                phone='+70000000011',
                cost_centers={
                    'required': False,
                    'format': 'mixed',
                    'values': ['123', '456'],
                },
            ),
            id='test_cost_centers_new_user',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                phone='+70000000011',
                cost_center_values=NEW_COST_CENTER_VALUES,
                cost_centers_id='other_cc_options_id',
            ),
            id='test_new_cost_centers_for_new_user',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                phone='+70000000011',
                combo_order=COMBO_ORDER,
                created_by='client1_uid',
            ),
            id='test_combo_order_for_new_user',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(extra_contact_phone='+79169222964'),
            id='test_extra_contact_phone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                tariff_class=CLASS_EXPRESS, extra_contact_phone='+79169222964',
            ),
            id='test_express_extra_contact_phone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                tariff_class=CLASS_COURIER, extra_contact_phone='+79169222964',
            ),
            id='test_courier_extra_contact_phone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(tariff_class=CLASS_EXPRESS),
            id='test_express_without_extra_contact_phone',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                tariff_class=CLASS_EXPRESS,
                requirements={'door_to_door': True},
                source=util.make_location_with(
                    extra_data={'contact_phone': '+79819992233'},
                ),
            ),
            id='test_extra_data_apt_delivery_source',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                tariff_class=CLASS_COURIER,
                requirements={'door_to_door': True},
                source=util.make_location_with(
                    extra_data={'contact_phone': '+79819992233'},
                ),
            ),
            id='test_extra_data_apt_delivery_source',
        ),
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(
                tariff_class=CLASS_EXPRESS,
                requirements={'door_to_door': True},
                source=util.make_location_with(
                    extra_data={'contact_phone': '+79819992233'},
                ),
                destination=util.make_location_with(
                    extra_data={
                        'contact_phone': '+79819992200',
                        'floor': '1',
                        'apartment': '2',
                        'comment': 'no knock',
                    },
                ),
            ),
            id='test_extra_data_apt_delivery_source_destination',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.usefixtures('pd_patch')
async def test_create_draft(
        patch,
        db,
        load_json,
        client,
        prefix,
        passport_mock,
        client_id,
        post_content,
):
    if prefix != '/internal' and 'combo_order' in post_content:
        return  # combo_order field only in InternalOrderRequest schema

    app = client.server.app
    await app.phones.refresh_cache()

    if prefix:
        auth_login = None
        auth_uid = 'external_service'
        if 'combo_order' in post_content:
            auth_uid = post_content['created_by']
    else:
        auth_login = passport_mock + '_login'
        auth_uid = passport_mock + '_uid'

    @patch('taxi_corp.clients.protocol.ProtocolClient.geosearch')
    async def _geosearch(*args, **kwargs):
        return [
            {
                'short_text': 'short text',
                'short_text_from': 'short text from',
                'short_text_to': 'short text to',
            },
        ]

    @patch('taxi.clients.experiments3.Experiments3Client.get_config_values')
    async def _get_config_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name='corp_control_lookup_ttl',
                value={'lookup_ttl_sec': 1800, 'reason': 'thats why'},
            ),
        ]

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi.clients.integration_api.IntegrationAPIClient.profile')
    async def _order_profile(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'user_id': 'user_id'}, headers={},
        )

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_estimate')
    async def _order_estimate(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'offer': 'offer_id'}, headers={},
        )

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_draft')
    async def _order_draft(*args, **kwargs):
        request_data = kwargs['data']
        util.check_interim_request(
            post_content,
            request_data,
            cost_center='corp_cost_center',
            cost_center_values='cost_centers',
        )
        return integration_api.APIResponse(
            status=200, data={'orderid': 'SomeOrderId'}, headers={},
        )

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch(
        'taxi_corp.clients.corp_integration_api.'
        'CorpIntegrationApiClient.corp_paymentmethods',
    )
    async def _corp_paymentmethods(*args, **kwargs):
        util.check_interim_request(
            post_content, kwargs, cost_center_values='cost_centers',
        )
        return {
            'methods': [
                {
                    'id': 'corp-{}'.format(client_id),
                    'can_order': True,
                    'zone_available': True,
                },
            ],
        }

    existing_user = await db.corp_users.find_one(
        {'phone': post_content['phone']},
    )

    response = await client.post(
        f'{prefix}/1.0/client/{client_id}/order',
        json=post_content,
        headers={'X-Real-IP': '127.0.0.1', 'User-Agent': ''},
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['_id'] == 'SomeOrderId'

    db_item = await db.corp_orders.find_one({'_id': 'SomeOrderId'})
    assert db_item['_id'] == 'SomeOrderId'
    assert db_item['created_by']['uid'] == auth_uid
    assert db_item.get('updated') is not None
    if 'cost_center_values' in post_content:
        assert (
            db_item['cost_centers']['cabinet']
            == post_content['cost_center_values']
        )
    if 'cost_center' in post_content:
        assert db_item['cost_center']['cabinet'] == post_content['cost_center']

    client = await db.corp_clients.find_one(
        {'_id': client_id}, projection=['features'],
    )
    if existing_user is None:
        created_user = await db.corp_users.find_one(
            {'phone': post_content['phone']},
        )
        assert created_user is not None
        if consts.ClientFeature.NEW_LIMITS in client['features']:
            assert (
                created_user['cost_centers_id']
                == post_content['cost_centers_id']
            )
        else:
            for field in {'cost_centers', 'cost_centers_id'}:
                if field in post_content:
                    assert created_user[field] == post_content[field]

    if consts.ClientFeature.NEW_LIMITS in client['features']:
        assert len(_put.calls) == 5
    else:
        assert len(_put.calls) == 1

    if auth_login == 'manager1_login':
        db_user = await db.corp_users.find_one(
            {'_id': db_item['corp_user']['user_id']},
        )
        department_id = None
        for access_data in load_json('mock_access_data.json'):
            if access_data['yandex_uid'] == auth_uid:
                department_id = access_data['department_id']

        assert db_user.get('department_id') == department_id

        db_history = await db.corp_history.find_one({'p': auth_login})
        assert db_history['e']['_id'] == db_user['_id']

    # check experiments call
    exp3_calls = list(_get_config_values.calls)
    assert len(exp3_calls) == 1

    exp3_args_raw: typing.List[experiments3.ExperimentsArg] = (
        exp3_calls[0]['kwargs'].get('experiments_args', [])
    )

    exp3_args = {arg.name: arg.value for arg in exp3_args_raw}
    assert exp3_args == {
        'corp_client_id': client_id,
        'country': 'rus',
        'taxi_class': post_content['class'],
        'has_due': 'due' in post_content,
    }


@pytest.mark.parametrize(
    [
        'client_id',
        'post_content',
        'paymentmethods_response',
        'expected_response_codes',
        'expected_error_codes',
    ],
    [
        # 0
        (
            'client1',
            util.make_order_request(due='can\'t parse this'),
            [{}],
            [400],
            [codes.VALIDATE_ORDER_INVALID_OR_EXPIRED_DUE_DATE.error_code],
        ),
        # 1
        (
            'client1',
            util.make_order_request(
                source=util.make_location_without('country'),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 2
        (
            'client1',
            util.make_order_request(
                destination=util.make_location_without('country'),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 3
        (
            'client1',
            util.make_order_request(
                destination=util.make_location_with(country=3),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 4
        (
            'client1',
            util.make_order_request(
                destination=util.make_location_with(fullname=3),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 5
        (
            'client1',
            util.make_order_request(
                destination=util.make_location_with(locality=3),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 6
        (
            'client1',
            util.make_order_request(
                destination=util.make_location_with(geopoint='not a number'),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 7
        (
            'client1',
            util.make_order_request(
                destination=util.make_location_with(geopoint=[2]),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 8
        (
            'client1',
            util.make_order_request(
                destination=util.make_location_with(geopoint=[2, 'x']),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 9
        (
            'client1',
            util.make_order_request(phone=None),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 10
        (
            'client1',
            util.make_order_request(phone='hahaha'),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 11
        (
            'client1',
            util.make_order_request(phone='+71110002233'),
            [{'id': 'corp-unknown-client'}],
            [406],
            [codes.EMPTY_CORP_PAYMENTMETHODS.error_code],
        ),
        # 12
        (
            'client1',
            util.make_order_request(phone='+71110002233'),
            [{'id': 'corp-unknown-client'}, {'can_order': False}],
            [406],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 13 client-check: inactive client
        (
            'client4',
            util.make_order_request(),
            [{'can_order': False}],
            [406],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 14 client-check: w/o billing_id
        (
            'client3',
            util.make_order_request(),
            [{'can_order': False}],
            [406],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 15 client-check: inactive contract
        (
            'client5',
            util.make_order_request(),
            [{'can_order': False}],
            [406],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 16 client-check: prepaid+blocked
        (
            'client6',
            util.make_order_request(),
            [{'can_order': False}],
            [406],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 17 invalid tariff name - unknown class
        (
            'client1',
            util.make_order_request(tariff_class='ecomon'),
            [{'can_order': False}],
            [406],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 18 invalid tariff name - non string value
        (
            'client1',
            util.make_order_request(tariff_class=123),
            [{'can_order': False}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 19 invalid tariff name - non string value
        (
            'client1',
            util.make_order_request(tariff_class=['econom', 'vip']),
            [{'can_order': False}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 20 due < now()
        (
            'client1',
            util.make_order_request(due='2016-03-15T15:00:00Z'),
            [{}],
            [400],
            [codes.VALIDATE_ORDER_INVALID_OR_EXPIRED_DUE_DATE.error_code],
        ),
        # 21 valid interim_destinations[], but without destination
        (
            'client1',
            util.make_order_request(
                interim_destinations=[util.make_location()],
                exclude_fields=('destination',),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 22 invalid interim_destinations - non list value
        (
            'client1',
            util.make_order_request(interim_destinations=util.make_location()),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
        ),
        # 23 invalid interim_destinations values (2 invalid, 1 valid items)
        (
            'client1',
            util.make_order_request(
                interim_destinations=[
                    util.make_location_without('country'),  # invalid
                    util.make_location_without('geopoint'),  # invalid
                    util.make_location(),  # valid
                ],
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code] * 2,
        ),
        pytest.param(
            'client1',
            util.make_order_request(
                phone='+70000000011',
                cost_centers={
                    'format': 'select',
                    'required': True,
                    'values': [],
                },
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
            id='test_cost_centers',
        ),
        pytest.param(
            'client1',
            util.make_order_request(
                tariff_class=CLASS_EXPRESS,
                requirements={'door_to_door': True},
                source=util.make_location_with(extra_data={}),
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
            id='test_error_extra_data_validation',
        ),
        pytest.param(
            'client1',
            util.make_order_request(
                tariff_class=CLASS_EXPRESS,
                requirements={'door_to_door': True},
                source=util.make_location_with(
                    extra_data={'contact_phone': '+79819992200'},
                ),
                interim_destinations=[
                    util.make_location_with(
                        extra_data={'contact_phone': '+79819992200'},
                    ),
                ],
            ),
            [{}],
            [400],
            [codes.GENERAL_ERROR.error_code],
            id='test_error_extra_data_in_interim',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(corp_users='for_general_post_test')
@pytest.mark.translations(
    corp={
        'order.order_is_running': {'ru': 'Выполняется заказ'},
        'order.taxi_on_the_way': {'ru': 'Такси в пути'},
        'order.taxi_will_arrive_in_time': {
            'ru': 'Такси приедет через {minutes:d} мин.',
        },
        'error.unknown_city_error_code': {'ru': '_'},
        'error.client_doesnt_have_contract': {'ru': '_'},
        'error.empty_corp_pm_code': {'ru': '_'},
        'error.unknown_class_error': {'ru': '_'},
        'error.check_phone_length_greater_than': {'ru': '_'},
        'error.incompatible_cost_centers': {
            'ru': 'error.incompatible_cost_centers',
        },
        'error.unexpected_extra_data_in_point': {
            'ru': 'error.unexpected_extra_data_in_point',
        },
    },
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+7'],
            'matches': ['^7'],
        },
    ],
    CORP_ENABLE_LOOKUP_TTL_CONTROL=True,
)
async def test_general_post_fail(
        taxi_corp_auth_client,
        acl_access_data_patch,
        patch,
        pd_patch,
        patch_doc,
        client_id,
        post_content,
        paymentmethods_response,
        expected_response_codes,
        expected_error_codes,
):

    app = taxi_corp_auth_client.server.app
    await app.phones.refresh_cache()

    @patch('taxi.clients.experiments3.Experiments3Client.get_config_values')
    async def _get_config_values(*args, **kwargs):
        return []

    @patch('taxi.clients.integration_api.IntegrationAPIClient.profile')
    async def _order_profile(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'user_id': 'user_id'}, headers={},
        )

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi_corp.clients.protocol.ProtocolClient.geosearch')
    async def _geosearch(*args, **kwargs):
        return [
            {
                'short_text': 'short text',
                'short_text_from': 'short text from',
                'short_text_to': 'short text to',
            },
        ]

    paymentmethods = {
        'id': 'corp-{}'.format(client_id),
        'can_order': True,
        'zone_available': True,
        'order_disable_reason': '',
        'zone_disable_reason': '',
    }

    @patch(
        'taxi_corp.clients.corp_integration_api.'
        'CorpIntegrationApiClient.corp_paymentmethods',
    )
    async def _corp_paymentmethods(*args, **kwargs):
        return {
            'methods': [
                patch_doc(paymentmethods, changes)
                for changes in paymentmethods_response
            ],
        }

    response = await taxi_corp_auth_client.post(
        '/1.0/client/{}/order'.format(client_id),
        json=post_content,
        headers={'X-Real-IP': '127.0.0.1', 'User-Agent': ''},
    )
    response_json = await response.json()
    assert response.status in expected_response_codes
    error_codes = [error['code'] for error in response_json['errors']]
    assert error_codes == expected_error_codes, response_json['errors']


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['client_id', 'order_id', 'order_search', 'expected_result'],
    [
        (
            'client1',
            'order1',
            {
                'cancel_disabled': False,
                'cancel_rules': {
                    'message': 'message',
                    'state': 'free',
                    'title': 'title',
                },
            },
            {
                '_id': 'order1',
                'application': 'iphone',
                'application_translate': 'Мобильный телефон',
                'status': {
                    'simple': 'finished',
                    'full': 'complete',
                    'description': '',
                },
                'due_date': '2016-03-24T21:37:17',
                'local_due_date': '2016-03-25T00:37:17+0300',
                'finished_date': '2016-03-24T21:47:17',
                'performer': {
                    'car': (
                        'Volkswagen Caravelle коричневый_from_tanker КС67477'
                    ),
                    'fullname': 'Гарольд',
                    'phone': '+79165555555',
                },
                'created': '2016-03-24T21:27:17',
                'extra_contact_phone': '+79169222964',
                'start_waiting_time': '2016-03-24T21:40:07',
                'started_date': '2016-03-24T21:40:17',
                'corp_user': {
                    'user_id': 'user1',
                    'fullname': 'Zoe',
                    'phone': '+79291112201',
                    'role_id': '9d108c92a4f5449f966c1bea0ccafc28',
                    'role_name': 'role.cabinet_only_name',
                    'nickname': 'ZoeTheCoolest',
                },
                'destination': {
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'source': {
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к8',
                    'geopoint': ['37.5887876121', '55.734141752'],
                },
                'cost': 540,
                'cost_with_vat': '637.20',
                'class': 'econom',
                'cost_center': 'user defined cost center',
                'created_by': '+79291112201',
            },
        ),
        (
            'client1',
            'order1_missedcolor',
            {
                'cancel_disabled': False,
                'cancel_rules': {
                    'message': 'message',
                    'state': 'free',
                    'title': 'title',
                },
            },
            {
                '_id': 'order1_missedcolor',
                'application': 'iphone',
                'application_translate': 'Мобильный телефон',
                'status': {
                    'simple': 'finished',
                    'full': 'complete',
                    'description': '',
                },
                'due_date': '2016-03-24T21:37:17',
                'local_due_date': '2016-03-25T00:37:17+0300',
                'finished_date': '2016-03-24T21:47:17',
                'performer': {
                    'car': 'Volkswagen Caravelle коричневый КС67477',
                    'fullname': 'Гарольд',
                    'phone': '+79165555555',
                },
                'created': '2016-03-24T21:27:17',
                'extra_contact_phone': '+79169222964',
                'start_waiting_time': '2016-03-24T21:40:07',
                'started_date': '2016-03-24T21:40:17',
                'corp_user': {
                    'user_id': 'user1',
                    'fullname': 'Zoe',
                    'phone': '+79291112201',
                    'role_id': '9d108c92a4f5449f966c1bea0ccafc28',
                    'role_name': 'role.cabinet_only_name',
                    'nickname': 'ZoeTheCoolest',
                },
                'destination': {
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'source': {
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к8',
                    'geopoint': ['37.5887876121', '55.734141752'],
                },
                'cost': 540,
                'cost_with_vat': '637.20',
                'class': 'econom',
                'cost_center': 'user defined cost center',
                'created_by': '+79291112201',
            },
        ),
        (
            'successful_client_id',
            'successful_order_id',
            {
                'route_sharing_url': 'url',
                'cancel_disabled': False,
                'cancel_rules': {
                    'message': 'message',
                    'state': 'free',
                    'title': 'title',
                },
            },
            {
                '_id': 'successful_order_id',
                'application': 'iphone',
                'application_translate': 'Мобильный телефон',
                'route_sharing_url': 'url',
                'status': {
                    'simple': 'active',
                    'full': 'search',
                    'description': '',
                },
                'due_date': '2016-03-24T21:37:17',
                'local_due_date': '2016-03-25T00:37:17+0300',
                'created': '2016-03-24T21:27:17',
                'start_waiting_time': '2016-03-24T21:40:07',
                'started_date': '2016-03-24T21:40:17',
                'corp_user': {
                    'user_id': 'user1',
                    'fullname': 'Zoe',
                    'phone': '+79291112201',
                    'role_id': '9d108c92a4f5449f966c1bea0ccafc28',
                    'role_name': 'role.cabinet_only_name',
                    'nickname': 'ZoeTheCoolest',
                },
                'destination': {
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'source': {
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к8',
                    'geopoint': ['37.5887876121', '55.734141752'],
                },
                'class': 'econom',
                'cost_center': 'user defined cost center',
                'created_by': '+79291112201',
                'cancel_rules': {
                    'can_cancel': True,
                    'message': 'message',
                    'state': 'free',
                    'title': 'title',
                },
            },
        ),
        (
            'client1',
            'order2',
            {'cancel_disabled': True, 'time_left_raw': 1900.0},
            {
                '_id': 'order2',
                'application': 'android',
                'application_translate': 'Мобильный телефон',
                'status': {
                    'simple': 'active',
                    'full': 'driving',
                    'description': 'Такси приедет через 32 мин.',
                    'time_left_raw': 1900.0,
                },
                'due_date': '2016-03-21T18:45:17',
                'local_due_date': '2016-03-21T21:45:17+0300',
                'created': '2016-03-21T18:35:20',
                'corp_user': {
                    'user_id': 'user1',
                    'fullname': 'Zoe',
                    'phone': '+79291112201',
                    'role_id': '9d108c92a4f5449f966c1bea0ccafc28',
                    'role_name': 'role.cabinet_only_name',
                    'nickname': 'ZoeTheCoolest',
                },
                'cost': 690.0,
                'cost_with_vat': '814.20',
                'source': {
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к9',
                    'geopoint': ['37.5887876121', '55.734141752'],
                },
                'destination': {
                    'fullname': 'Россия, Москва, Большая Никитская улица, 14',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'class': 'comfort',
                'cost_center': 'cabinet defined cost center',
                'created_by': '+79291112201',
                'cancel_rules': {'can_cancel': False},
            },
        ),
        (
            'client1',
            'order12',
            {'cancel_disabled': True, 'time_left_raw': 735.0},
            {
                '_id': 'order12',
                'application': 'android',
                'application_translate': 'Мобильный телефон',
                'status': {
                    'simple': 'active',
                    'full': 'transporting',
                    'description': 'Заказ будет завершен через 12 мин.',
                    'time_left_raw': 735.0,
                },
                'due_date': '2016-03-21T18:45:17',
                'local_due_date': '2016-03-21T21:45:17+0300',
                'created': '2016-03-21T18:35:20',
                'corp_user': {
                    'user_id': 'user7',
                    'fullname': 'Zoe',
                    'phone': '+79291112202',
                    'role_id': '9d108c92a4f5449f966c1bea0ccafc28',
                    'role_name': 'role.cabinet_only_name',
                    'nickname': 'ZoeTheCoolest',
                },
                'cost': 690.0,
                'cost_with_vat': '814.20',
                'source': {
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к9',
                    'geopoint': ['37.5887876121', '55.734141752'],
                },
                'destination': {
                    'fullname': 'Россия, Москва, Большая Никитская улица, 14',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'class': 'comfort',
                'cost_center': 'cabinet defined cost center',
                'created_by': '+79291112202',
                'cancel_rules': {'can_cancel': False},
            },
        ),
        (
            'client5',
            'order7',
            None,
            {
                '_id': 'order7',
                'status': {
                    'simple': 'finished',
                    'full': 'complete',
                    'description': '',
                },
                'due_date': '2017-12-21T12:28:00',
                'local_due_date': '2017-12-21T15:28:00+0300',
                'created': '2017-12-21T12:14:42',
                'corp_user': {
                    'user_id': 'user5',
                    'fullname': 'TestUser1',
                    'phone': '+79264333315',
                    'role_id': '9d108c92a4f5449f966c1bea0ccafc28',
                    'role_name': 'role.cabinet_only_name',
                },
                'class': 'econom',
                'source': {
                    'fullname': 'Россия, Москва, улица Льва Толстого, 16',
                    'geopoint': ['37.58878761211858', '55.73414175200699'],
                },
                'destination': {
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'interim_destinations': [
                    {
                        'fullname': 'Садовническая улица, 84с7',
                        'geopoint': ['33.6', '55.1'],
                    },
                    {
                        'fullname': 'Малая Никитская улица, 43',
                        'geopoint': ['37.6', '55.7'],
                    },
                ],
                'requirements': {
                    'bicycle': True,
                    'childchair_moscow': 3,
                    'conditioner': True,
                    'nosmoking': True,
                    'yellowcarnumber': True,
                },
                'cost_center': '',
                'created_by': '+79264333315',
                'city': 'Москва',
                'cost': 670.0,
                'cost_with_vat': '790.60',
                'finished_date': '2017-12-21T13:14:00',
            },
        ),
        (
            'client8',
            'order13',
            None,
            {
                '_id': 'order13',
                'application': 'android',
                'application_translate': 'Мобильный телефон',
                'status': {
                    'simple': 'active',
                    'full': 'transporting',
                    'description': 'Выполняется заказ',
                },
                'due_date': '2020-03-20T16:00:00',
                'local_due_date': '2020-03-20T19:00:00+0300',
                'created': '2020-03-20T14:40:00',
                'corp_user': {
                    'user_id': 'user8',
                    'fullname': 'door-to-door guy',
                    'phone': '+79291112299',
                },
                'class': 'express',
                'source': {
                    'extra_data': {
                        'apartment': '2',
                        'floor': '3',
                        'comment': 'source_comment',
                        'contact_phone': '+79291112299',
                    },
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к9',
                    'geopoint': ['37.5887876121', '55.734141752'],
                    'porchnumber': '1',
                },
                'destination': {
                    'extra_data': {
                        'apartment': '9',
                        'floor': '5',
                        'comment': 'dest_comment',
                        'contact_phone': '+79290009933',
                    },
                    'fullname': 'Россия, Москва, Большая Никитская улица, 14',
                    'geopoint': ['37.600296', '55.750379'],
                    'porchnumber': '98',
                },
                'cost_center': '',
                'cost_centers': NEW_COST_CENTER_VALUES,
                'created_by': '+79291112299',
                'cost': 690.0,
                'cost_with_vat': '814.20',
            },
        ),
        (
            'client8',
            'order14',
            None,
            {
                '_id': 'order14',
                'application': 'android',
                'application_translate': 'Мобильный телефон',
                'status': {
                    'simple': 'active',
                    'full': 'transporting',
                    'description': 'Выполняется заказ',
                },
                'due_date': '2020-03-21T10:30:00',
                'local_due_date': '2020-03-21T13:30:00+0300',
                'created': '2020-03-21T09:30:00',
                'corp_user': {
                    'user_id': 'user8',
                    'fullname': 'door-to-door guy',
                    'phone': '+79291112299',
                },
                'class': 'express',
                'source': {
                    'extra_data': {'contact_phone': '+79291112299'},
                    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к9',
                    'geopoint': ['37.5887876121', '55.734141752'],
                },
                'destination': {
                    'extra_data': {'contact_phone': '+79290009933'},
                    'fullname': 'Россия, Москва, Большая Никитская улица, 14',
                    'geopoint': ['37.600296', '55.750379'],
                },
                'cost_center': '',
                'created_by': '+79291112299',
                'cost': 690.0,
                'cost_with_vat': '814.20',
            },
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'role.cabinet_only_name': {'ru': 'role.cabinet_only_name'},
        'order.order_is_running': {'ru': 'Выполняется заказ'},
        'order.taxi_on_the_way': {'ru': 'Такси в пути'},
        'order.taxi_will_arrive_in_time': {
            'ru': 'Такси приедет через {minutes:d} мин.',
        },
        'order.order_will_be_finished_in_time': {
            'ru': 'Заказ будет завершен через {minutes:d} мин.',
        },
        'report.app.mobile': {'ru': 'Мобильный телефон'},
        'report.app.corpweb': {'ru': 'Личный кабинет'},
        'report.app.callcenter': {'ru': 'КЦ'},
    },
    color={'800000': {'ru': 'коричневый_from_tanker'}},
)
async def test_single_get(
        taxi_corp_auth_client,
        patch,
        client_id,
        order_id,
        order_search,
        expected_result,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_search')
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'orders': [order_search]}, headers={},
        )

    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _get_order_by_id(*args, **kwargs):
        return {
            'candidates': [{'phone_id': 'phone_id'}],
            'performer': {'candidate_index': 0},
        }

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'id': 'phone_id', 'phone': '+79165555555'}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone')
    async def _get_user_phone(phone_id, *args, **kwargs):
        phone = hex_to_phone(phone_id)
        return {'id': bson.ObjectId(phone_id), 'phone': phone}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        return [
            {'id': phone_id, 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch('taxi_corp.internal.territories_manager.get_nearest_zone')
    async def _get_nearest_zone(*args, **kwargs):
        return 'moscow'

    @patch('taxi_corp.internal.tariffs_manager.get_tariff_settings')
    async def _get_tariff_settings(*args, **kwargs):
        return {'tz': 'Europe/Moscow'}

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/order/{}{}'.format(
            client_id,
            order_id,
            '?show_cancel_text=true' if order_search else '',
        ),
    )

    assert response.status == 200
    assert await response.json() == expected_result


@pytest.mark.parametrize(
    'passport_mock, status',
    [('client7', 200), ('manager2', 200), ('client1', 403)],
    indirect=['passport_mock'],
)
@pytest.mark.parametrize('order_id', ['order10', 'order11'])
@pytest.mark.parametrize(
    'method, postfix',
    [
        ('GET', '/{}'),
        ('GET', '/{}/progress'),
        ('POST', ''),
        ('PUT', '/{}/change'),
        ('POST', '/{}/processing'),
        ('DELETE', '/{}/processing'),
        ('POST', '/{}/cancel'),
    ],
)
async def test_access(
        meta_app_version_mock,
        access_client,
        passport_mock,
        method,
        order_id,
        postfix,
        status,
):
    response = await access_client.request(
        method, '/1.0/client/client7/order{}'.format(postfix.format(order_id)),
    )
    assert response.status == status


@pytest.mark.parametrize(
    'passport_mock', ['client7'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'countries, clients, status',
    [
        ([], [], 403),
        (['rus'], [], 200),
        (['izr'], [], 403),
        (['rus'], ['client7'], 200),
        ([], ['client7'], 200),
    ],
)
async def test_block_order(
        access_client,
        config_patcher,
        passport_mock,
        countries,
        clients,
        status,
):
    config_patcher(CORP_DELIVERY_ALLOWED_COUNTRIES=countries)
    config_patcher(CORP_DELIVERY_ALLOWED_CLIENTS=clients)
    response = await access_client.post(
        '/1.0/client/client7/order', json={'class': 'cargo'},
    )
    response_json = await response.json()
    assert response.status == status, response_json


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'client_id, order_id', [('client1', 'not_found'), ('not_found', 'order2')],
)
async def test_single_get_fail(
        taxi_corp_real_auth_client, passport_mock, client_id, order_id,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/{}/order/{}'.format(client_id, order_id),
    )
    assert response.status == 404, await response.json()


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'status, taxi_status, order_type, due_date, expected_info_status',
    [
        (
            'cancelled',
            'transporting',
            'soon',
            _NOW + datetime.timedelta(minutes=6),
            {'full': 'cancelled', 'simple': 'finished', 'description': ''},
        ),
        (
            'assigned',
            'driving',
            'soon',
            _NOW + datetime.timedelta(minutes=6),
            {
                'full': 'driving',
                'simple': 'active',
                'description': 'Такси приедет через 6 мин.',
            },
        ),
        (
            'assigned',
            'transporting',
            'soon',
            _NOW + datetime.timedelta(minutes=6),
            {
                'full': 'transporting',
                'simple': 'active',
                'description': 'Выполняется заказ',
            },
        ),
        (
            'pending',
            None,
            'exact',
            _NOW + datetime.timedelta(minutes=180),
            {
                'full': 'scheduling',
                'simple': 'delayed',
                'description': 'Такси приедет через 180 мин.',
            },
        ),
        (
            'assigned',
            'transporting',
            'exact',
            _NOW + datetime.timedelta(minutes=180),
            {
                'full': 'transporting',
                'simple': 'active',
                'description': 'Выполняется заказ',
            },
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'order.order_is_running': {'ru': 'Выполняется заказ'},
        'order.taxi_on_the_way': {'ru': 'Такси в пути'},
        'order.taxi_will_arrive_in_time': {
            'ru': 'Такси приедет через {minutes:d} мин.',
        },
    },
)
async def test_order_view_status(
        taxi_corp_auth_app,
        request_mock,
        status,
        taxi_status,
        order_type,
        due_date,
        expected_info_status,
):
    order = {
        'status': status,
        'taxi_status': taxi_status,
        '_type': order_type,
        'due_date': due_date,
    }
    info = orderinfo.OrderInfo(request_mock, order, None)
    assert info.status == expected_info_status, info.status
