# pylint: disable=protected-access

import pytest


from mia.crontasks.extra_fetcher import extra_fetcher_eda
from mia.crontasks.formatter import formatter_eda


@pytest.mark.parametrize(
    'test',
    [
        {'request': {'payment_method_id': 0}, 'expected': 'Наличный расчёт'},
        {
            'request': {'payment_method_id': 1},
            'expected': 'Безналичный расчёт',
        },
    ],
)
async def test_format_payment_method(test):
    request = test['request']
    expected = test['expected']

    payment_method_id = request['payment_method_id']

    result = formatter_eda.FormatterEda._format_payment_method(
        payment_method_id,
    )

    assert result == expected


@pytest.mark.parametrize(
    'test',
    [
        {'request': {'status': 4}, 'expected': 'Доставлен'},
        {'request': {'status': 5}, 'expected': 'Отменён'},
        {'request': {'status': 1}, 'expected': 'Не доставлен'},
    ],
)
async def test_format_status(test):
    request = test['request']
    expected = test['expected']

    status = request['status']

    result = formatter_eda.FormatterEda._format_status(status)

    assert result == expected


@pytest.mark.parametrize(
    'test',
    [
        {
            'request': {
                'row': {
                    'id': 123,
                    'order_nr': 'test_order_nr',
                    'created_at': 1581669341,
                    'finished_at': 1591669341,
                    'status': 4,
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_city': 'test_address_city',
                    'address_street': 'test_address_street',
                    'address_house': 'test_address_house',
                    'address_comment': 'test_comment',
                    'couriers_source': 'not virtual',
                    'courier_username': 'test_courier_username',
                    'phone_number': 'test_user_phone',
                    'order_type': 'native',
                },
                'order': {
                    'payment_method_id': 1,
                    'address_full': 'test_address',
                },
                'courier_service': {
                    'id': 3,
                    'inn': 'test_inn_3',
                    'address': 'test_address_3',
                    'name': 'courier_service_name',
                    'phone_number': 'test_phone_number_3',
                },
                'courier_personal_data': {'phone_number': 'courier_phone'},
                'place': {
                    'id': 1,
                    'name': 'test_name_1',
                    'address_full': 'test_address_full_1',
                },
                'user': {
                    'id': 2,
                    'first_name': 'test_first_name_2',
                    'email': 'test_email_2',
                },
                'order_revision': {
                    'id': 1,
                    'cost_for_customer': 11,
                    'cost_for_place': 111,
                    'items_cost': 1111,
                    'delivery_cost': 11111,
                },
                'order_refunds': [
                    {'id': 3, 'order_id': 1, 'amount': 33},
                    {'id': 4, 'order_id': 1, 'amount': 44},
                    {'id': 7, 'order_id': 1, 'amount': 77},
                ],
                'phone_numbers': [
                    {'id': 1, 'place_id': 2, 'phone_number': 'test_number'},
                ],
                'order_items': [
                    {'name': 'name_1', 'quantity': 1, 'id': 1},
                    {'name': 'name_2', 'quantity': 2, 'id': 2},
                    {'name': 'name_3', 'quantity': 3, 'id': 3},
                ],
                'order_items_options': [
                    {
                        'name': 'option_1',
                        'group_name': 'group_1',
                        'item_id': 1,
                        'quantity': 1,
                    },
                    {
                        'name': 'option_2',
                        'group_name': 'group_2',
                        'item_id': 2,
                        'quantity': 2,
                    },
                    {
                        'name': 'option_3',
                        'group_name': 'group_3',
                        'item_id': 2,
                        'quantity': 3,
                    },
                ],
                'taxi_performer_info': None,
                'park': None,
            },
            'expected': {
                'order_id': 123,
                'order_nr': 'test_order_nr',
                'user_phone': 'test_user_phone',
                'order_type': 'native',
                'address_office': 'test_address_office',
                'finished_at': '09.06.2020 05:22:21+0300',
                'address_entrance': 'test_address_entrance',
                'address_city': 'test_address_city',
                'address_street': 'test_address_street',
                'address_house': 'test_address_house',
                'address_comment': 'test_comment',
                'is_virtual': False,
                'cost_for_customer': 11,
                'cost_for_place': 111,
                'courier_name': 'test_courier_username',
                'deliverer_type': 'Курьерская служба',
                'deliverer_address': 'test_address_3',
                'deliverer_name': 'courier_service_name',
                'deliverer_inn': 'test_inn_3',
                'deliverer_phone_number': 'test_phone_number_3',
                'created_at': '14.02.2020 11:35:41+0300',
                'delivery_cost': 11111,
                'items_cost': 1111,
                'order_refunds': [
                    {'amount': 33, 'id': 3, 'order_id': 1},
                    {'amount': 44, 'id': 4, 'order_id': 1},
                    {'amount': 77, 'id': 7, 'order_id': 1},
                ],
                'order_items': [
                    'name_1 x1 (group_1: option_1 x1)',
                    'name_2 x2 (group_2: option_2 x2; group_3: option_3 x3)',
                    'name_3 x3',
                ],
                'order_status': 'Доставлен',
                'payment_method': 'Безналичный расчёт',
                'place_address': 'test_address_full_1',
                'place_phone_numbers': ['test_number'],
                'place_name': 'test_name_1',
                'user_email': 'test_email_2',
                'user_first_name': 'test_first_name_2',
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'payment_time': '-',
                'courier_phone': 'courier_phone',
            },
        },
        {
            'request': {
                'row': {
                    'id': 123,
                    'order_nr': 'test_order_nr',
                    'created_at': 1581669341,
                    'finished_at': 1581569341,
                    'status': 4,
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_city': 'test_address_city',
                    'address_street': 'test_address_street',
                    'address_house': 'test_address_house',
                    'address_comment': 'test_comment',
                    'couriers_source': 'virtual',
                    'courier_username': 'test_courier_username',
                    'phone_number': 'test_user_phone',
                    'order_type': 'native',
                    'masked_pan': 'test_masked_pan',
                    'rrn': 'test_rrn',
                    'approval_code': 'test_approval_code',
                    'payment_time': 1554660420,
                },
                'order': {
                    'payment_method_id': 1,
                    'address_full': 'test_address',
                },
                'courier_service': {
                    'id': 3,
                    'inn': 'test_inn_3',
                    'address': 'test_address_3',
                    'name': 'courier_service_name',
                    'phone_number': 'test_phone_number_3',
                },
                'courier_personal_data': {},
                'place': {
                    'id': 1,
                    'name': 'test_name_1',
                    'address_full': 'test_address_full_1',
                },
                'user': {
                    'id': 2,
                    'first_name': 'test_first_name_2',
                    'email': 'test_email_2',
                },
                'order_revision': {
                    'id': 1,
                    'cost_for_customer': 11,
                    'cost_for_place': 111,
                    'items_cost': 1111,
                    'delivery_cost': 11111,
                },
                'order_refunds': [
                    {'id': 3, 'order_id': 1, 'amount': 33},
                    {'id': 4, 'order_id': 1, 'amount': 44},
                    {'id': 7, 'order_id': 1, 'amount': 77},
                ],
                'phone_numbers': [
                    {'id': 1, 'place_id': 2, 'phone_number': 'test_number'},
                ],
                'order_items': [
                    {'name': 'name_1', 'quantity': 1, 'id': 1},
                    {'name': 'name_2', 'quantity': 2, 'id': 2},
                    {'name': 'name_3', 'quantity': 3, 'id': 3},
                ],
                'order_items_options': [
                    {
                        'name': 'option_1',
                        'group_name': 'group_1',
                        'item_id': 1,
                        'quantity': 1,
                    },
                    {
                        'name': 'option_2',
                        'group_name': 'group_2',
                        'item_id': 2,
                        'quantity': 2,
                    },
                    {
                        'name': 'option_3',
                        'group_name': 'group_3',
                        'item_id': 2,
                        'quantity': 3,
                    },
                ],
                'taxi_performer_info': {
                    'name': 'performer_name',
                    'phone': 'performer_phone',
                },
                'park': {
                    'account_details_inn': 'inn',
                    'account_details_legal_address': 'address',
                    'name': 'park_name',
                    'phone': 'park_phone',
                },
            },
            'expected': {
                'order_id': 123,
                'order_nr': 'test_order_nr',
                'user_phone': 'test_user_phone',
                'order_type': 'native',
                'finished_at': '13.02.2020 07:49:01+0300',
                'address_office': 'test_address_office',
                'address_entrance': 'test_address_entrance',
                'address_comment': 'test_comment',
                'address_city': 'test_address_city',
                'address_street': 'test_address_street',
                'address_house': 'test_address_house',
                'is_virtual': True,
                'cost_for_customer': 11,
                'cost_for_place': 111,
                'deliverer_type': 'Курьер такси',
                'courier_name': 'performer_name',
                'deliverer_address': 'address',
                'deliverer_name': 'park_name',
                'deliverer_inn': 'inn',
                'deliverer_phone_number': 'park_phone',
                'created_at': '14.02.2020 11:35:41+0300',
                'delivery_cost': 11111,
                'items_cost': 1111,
                'order_refunds': [
                    {'amount': 33, 'id': 3, 'order_id': 1},
                    {'amount': 44, 'id': 4, 'order_id': 1},
                    {'amount': 77, 'id': 7, 'order_id': 1},
                ],
                'order_items': [
                    'name_1 x1 (group_1: option_1 x1)',
                    'name_2 x2 (group_2: option_2 x2; group_3: option_3 x3)',
                    'name_3 x3',
                ],
                'order_status': 'Доставлен',
                'payment_method': 'Безналичный расчёт',
                'place_address': 'test_address_full_1',
                'place_phone_numbers': ['test_number'],
                'place_name': 'test_name_1',
                'user_email': 'test_email_2',
                'user_first_name': 'test_first_name_2',
                'masked_pan': 'test_masked_pan',
                'rrn': 'test_rrn',
                'approval_code': 'test_approval_code',
                'payment_time': '07.04.2019 21:07:00+0300',
                'courier_phone': 'performer_phone',
            },
        },
        {
            'request': {
                'row': {
                    'id': 1000,
                    'created_idx': 1578225600,
                    'created_at': 1578225600.123,
                    'latest_revision_id': 1000,
                    'courier_id': 1000,
                    'user_id': 1000,
                    'place_id': 1000,
                    'finished_at': 1578225601,
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_city': 'test_address_city',
                    'address_street': 'test_address_street',
                    'address_house': 'test_address_house',
                    'address_comment': 'test_comment',
                    'couriers_source': 'not virtual',
                    'courier_username': 'test_courier_username',
                    'phone_number': 'test_user_phone',
                    'order_type': 'native',
                    'status': 4,
                },
                'order': {'id': 1000, 'payment_method_id': 1},
                'courier_personal_data': {
                    'id': 1000,
                    'inn': None,
                    'address': None,
                    'phone_number': None,
                },
                'courier_service': {},
                'place': {},
                'user': {},
                'order_revision': {
                    'id': 1000,
                    'cost_for_customer': 11,
                    'cost_for_place': 111,
                    'items_cost': 1111,
                    'delivery_cost': 11111,
                    'composition_id': 1000,
                },
                'order_refunds': [],
                'phone_numbers': [],
                'order_items': [],
                'order_items_options': [],
                'taxi_performer_info': None,
                'park': None,
            },
            'expected': {
                'address_city': 'test_address_city',
                'address_comment': 'test_comment',
                'address_entrance': 'test_address_entrance',
                'address_house': 'test_address_house',
                'address_office': 'test_address_office',
                'address_street': 'test_address_street',
                'cost_for_customer': 11,
                'cost_for_place': 111,
                'courier_name': 'test_courier_username',
                'created_at': '05.01.2020 15:00:00+0300',
                'deliverer_address': '-',
                'deliverer_inn': '-',
                'deliverer_name': '-',
                'deliverer_phone_number': '-',
                'deliverer_type': 'Курьерская служба',
                'delivery_cost': 11111,
                'finished_at': '05.01.2020 15:00:01+0300',
                'is_virtual': False,
                'items_cost': 1111,
                'masked_pan': '-',
                'rrn': '-',
                'approval_code': '-',
                'order_id': 1000,
                'order_items': [],
                'order_nr': None,
                'order_refunds': [],
                'order_status': 'Доставлен',
                'order_type': 'native',
                'payment_method': 'Безналичный расчёт',
                'payment_time': '-',
                'place_address': None,
                'place_name': None,
                'place_phone_numbers': [],
                'user_email': None,
                'user_first_name': None,
                'user_phone': 'test_user_phone',
                'courier_phone': None,
            },
        },
    ],
)
async def test_format_row(test):
    request = test['request']
    expected = test['expected']

    formatter = formatter_eda.FormatterEda()

    row_with_extra = extra_fetcher_eda.RowWithExtraEda(
        row=request['row'],
        order=request['order'],
        user=request['user'],
        place=request['place'],
        courier_service=request['courier_service'],
        courier_personal_data=request['courier_personal_data'],
        order_revision=request['order_revision'],
        order_refunds=request['order_refunds'],
        phone_numbers=request['phone_numbers'],
        order_items=request['order_items'],
        order_items_options=request['order_items_options'],
        taxi_performer_info=request['taxi_performer_info'],
        park=request['park'],
    )

    result = await formatter._format_row(row_with_extra)

    assert result == expected


@pytest.mark.parametrize(
    'test',
    [
        {
            'input': {
                'is_virtual': True,
                'order_type': 'abacaba',
                'courier_service_id': 123123,
            },
            'expected_result': 'Курьер такси',
        },
        {
            'input': {
                'is_virtual': False,
                'order_type': 'marketplace',
                'courier_service_id': 123123,
            },
            'expected_result': 'Курьер ресторана',
        },
        {
            'input': {
                'is_virtual': False,
                'order_type': 'abacaba',
                'courier_service_id': 116,
            },
            'expected_result': 'Самозанятый',
        },
        {
            'input': {
                'is_virtual': False,
                'order_type': 'abacaba',
                'courier_service_id': 123123,
            },
            'expected_result': 'Курьерская служба',
        },
    ],
)
def test_format_deliverer_type(test):
    formatter = formatter_eda.FormatterEda()
    result = formatter._format_deliverer_type(**test['input'])
    assert result == test['expected_result']


@pytest.mark.parametrize(
    'test',
    [
        {
            'input': {
                'courier_service': {
                    'id': 116,
                    'inn': 'test_cs_inn',
                    'address': 'test_cs_address',
                    'name': 'courier_service_name',
                    'phone_number': 'test_cs_phone_number',
                },
                'courier_personal_data': {
                    'inn': 'test_inn',
                    'address': 'test_address',
                    'phone_number': 'test_phone_number',
                },
                'courier_username': 'courier_username',
            },
            'expected_result': {
                'inn': 'test_inn',
                'address': 'test_address',
                'phone_number': 'test_phone_number',
                'name': 'courier_username',
            },
        },
        {
            'input': {
                'courier_service': {
                    'id': 116,
                    'inn': 'test_cs_inn',
                    'address': 'test_cs_address',
                    'name': 'courier_service_name',
                    'phone_number': 'test_cs_phone_number',
                },
                'courier_personal_data': {},
                'courier_username': '-',
            },
            'expected_result': {
                'inn': '-',
                'address': '-',
                'phone_number': '-',
                'name': '-',
            },
        },
        {
            'input': {
                'courier_service': {
                    'id': 116,
                    'inn': 'test_cs_inn',
                    'address': 'test_cs_address',
                    'name': 'courier_service_name',
                    'phone_number': 'test_cs_phone_number',
                },
                'courier_personal_data': None,
                'courier_username': None,
            },
            'expected_result': {
                'inn': '-',
                'address': '-',
                'phone_number': '-',
                'name': '-',
            },
        },
        {
            'input': {
                'courier_service': {
                    'id': 1,
                    'inn': 'test_cs_inn',
                    'address': 'test_cs_address',
                    'name': 'courier_service_name',
                    'phone_number': 'test_cs_phone_number',
                },
                'courier_personal_data': {
                    'inn': 'test_inn',
                    'address': 'test_address',
                    'phone_number': 'test_phone_number',
                },
                'courier_username': 'courier_username',
            },
            'expected_result': {
                'inn': 'test_cs_inn',
                'address': 'test_cs_address',
                'phone_number': 'test_cs_phone_number',
                'name': 'courier_service_name',
            },
        },
        {
            'input': {
                'courier_service': {'id': 1},
                'courier_personal_data': {
                    'inn': 'test_inn',
                    'address': 'test_address',
                    'phone_number': 'test_phone_number',
                },
                'courier_username': 'courier_username',
            },
            'expected_result': {
                'inn': '-',
                'address': '-',
                'phone_number': '-',
                'name': '-',
            },
        },
        {
            'input': {
                'courier_service': None,
                'courier_personal_data': {
                    'inn': 'test_inn',
                    'address': 'test_address',
                    'phone_number': 'test_phone_number',
                },
                'courier_username': 'courier_username',
            },
            'expected_result': {
                'inn': '-',
                'address': '-',
                'phone_number': '-',
                'name': '-',
            },
        },
    ],
)
def test_format_deliverer_data(test):
    formatter = formatter_eda.FormatterEda()
    result = formatter.format_deliverer_data(**test['input'])
    assert result == test['expected_result']


@pytest.mark.parametrize(
    'test',
    [
        {
            'input': {'order_items': [], 'order_items_options': []},
            'expected_result': [],
        },
        {
            'input': {
                'order_items': [
                    {'name': 'name_1', 'quantity': 1, 'id': 1},
                    {'name': 'name_2', 'quantity': 2, 'id': 2},
                    {'name': 'name_3', 'quantity': 3, 'id': 3},
                ],
                'order_items_options': [
                    {
                        'name': 'option_1',
                        'group_name': 'group_1',
                        'item_id': 1,
                        'quantity': 1,
                    },
                    {
                        'name': 'option_2',
                        'group_name': 'group_2',
                        'item_id': 2,
                        'quantity': 2,
                    },
                    {
                        'name': 'option_3',
                        'group_name': 'group_3',
                        'item_id': 2,
                        'quantity': 3,
                    },
                ],
            },
            'expected_result': [
                'name_1 x1 (group_1: option_1 x1)',
                'name_2 x2 (group_2: option_2 x2; group_3: option_3 x3)',
                'name_3 x3',
            ],
        },
    ],
)
def test_format_order_items(test):
    formatter = formatter_eda.FormatterEda()
    result = formatter._format_order_items(**test['input'])
    assert result == test['expected_result']


@pytest.mark.parametrize(
    'test',
    [
        {
            'park': {},
            'expected': {
                'inn': '-',
                'address': '-',
                'phone_number': '-',
                'name': '-',
            },
        },
        {
            'park': {
                'account_details_inn': 'inn',
                'account_details_legal_address': 'address',
                'name': 'park_name',
                'phone': 'phone',
            },
            'expected': {
                'inn': 'inn',
                'address': 'address',
                'phone_number': 'phone',
                'name': 'park_name',
            },
        },
    ],
)
def test_taxi_deliverer_data(test):
    formatter = formatter_eda.FormatterEda()
    result = formatter.taxi_deliverer_data(test['park'])
    assert result == test['expected']
