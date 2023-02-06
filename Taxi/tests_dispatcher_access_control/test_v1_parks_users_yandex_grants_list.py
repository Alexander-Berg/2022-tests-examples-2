# pylint: disable=too-many-lines
import json

import pytest

from testsuite.utils import ordered_object

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/users/yandex/grants/list'

QUERY_PARK1 = {'query': {'park': {'id': 'park_valid1'}}}
QUERY_PARK2 = {'query': {'park': {'id': 'park_valid2'}}}
QUERY_PARK3 = {'query': {'park': {'id': 'park_valid3'}}}

QUERY_PARK_INVALID = {'query': {'park': {'id': 'park_invalid'}}}


async def common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={
            'X-Ya-User-Ticket': user_ticket,
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )
    assert response.status_code == code
    ordered_object.assert_eq(response.json(), expected_response, ['grants'])


TEST_INVALID_PARAMS = [
    (
        'ticket_invalid',
        QUERY_PARK_INVALID,
        403,
        {'code': '403', 'message': 'User ticket is invalid'},
    ),
    (
        'ticket_valid1',
        QUERY_PARK_INVALID,
        400,
        {'code': '400', 'message': 'Park not found'},
    ),
    ('ticket_valid2', QUERY_PARK1, 200, {'grants': []}),
]


@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_INVALID_PARAMS,
)
async def test_invalid_request(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid2', uid='101', login='test2',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_PARAMS = [
    (
        'ticket_valid100',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('driver_read_common'),
                utils.make_grant('park_contacts_read'),
                utils.make_grant('park_contacts_write'),
                utils.make_grant('driver_write_common'),
                utils.make_grant('driver_add_money'),
                utils.make_grant('driver_withdraw_money'),
                utils.make_grant('driver_scoring_read'),
                utils.make_grant('users'),
                utils.make_grant('users_grants'),
                utils.make_grant('car_read_common'),
                utils.make_grant('car_write_common'),
                utils.make_grant('reports'),
                utils.make_grant('settings'),
                utils.make_grant('payments_groups'),
                utils.make_grant('tariffs'),
                utils.make_grant('drivers_messages'),
                utils.make_grant('news'),
                utils.make_grant('support'),
                utils.make_grant('fines'),
                utils.make_grant('service_pay_system'),
                utils.make_grant('report_cash'),
                utils.make_grant('orders'),
                utils.make_grant('segments'),
                utils.make_grant('legal_entities'),
                utils.make_grant('gas'),
                utils.make_grant('map'),
                utils.make_grant('support_chat_read'),
                utils.make_grant('support_chat_write'),
                utils.make_grant('recurring_payments_read'),
                utils.make_grant('recurring_payments_write'),
                utils.make_grant('work_rules_write'),
            ],
        },
    ),
    ('ticket_valid101', QUERY_PARK1, 200, {'grants': []}),
    ('ticket_valid100', QUERY_PARK2, 200, {'grants': []}),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1disabled': json.dumps(
                {
                    'Enable': False,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '101',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1emptyenabled': json.dumps(
                {'Name': 'Name1', 'Group': 'Group1', 'YandexUid': '102'},
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_PARAMS,
)
async def test_get_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid100', uid='100', login='test100',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid101', uid='101', login='test101',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid102', uid='102', login='test102',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_MENU_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('reports'),
                utils.make_grant('settings'),
                utils.make_grant('payments_groups'),
                utils.make_grant('drivers_messages'),
                utils.make_grant('news'),
                utils.make_grant('support'),
                utils.make_grant('fines'),
                utils.make_grant('service_pay_system'),
                utils.make_grant('report_cash'),
                utils.make_grant('gas'),
                utils.make_grant('map'),
                utils.make_grant('segments'),
                utils.make_grant('legal_entities'),
            ],
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '21',
                        '72',
                        '24',
                        '71',
                        'parks',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_MENU_PARAMS,
)
async def test_menu_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_CAR_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('car_read_common'),
                utils.make_grant('car_write_common'),
            ],
        },
    ),
    (
        'ticket_valid',
        QUERY_PARK2,
        200,
        {'grants': [utils.make_grant('car_read_common')]},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Car': json.dumps({'enableDelete': True}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Car': json.dumps(
                {
                    'tabdrivers': True,
                    'tabdocuments': True,
                    'tabaccess': True,
                    'disableDocumentAdd': True,
                    'disableDocumentDelete': True,
                    'disableLicense': True,
                    'disableEdit': True,
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_CAR_PARAMS,
)
async def test_car_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_DRIVER_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('driver_add_money'),
                utils.make_grant('driver_read_common'),
                utils.make_grant('driver_scoring_buy'),
                utils.make_grant('driver_scoring_read'),
                utils.make_grant('driver_withdraw_money'),
                utils.make_grant('driver_write_common'),
            ],
        },
    ),
    (
        'ticket_valid',
        QUERY_PARK2,
        200,
        {
            'grants': [
                utils.make_grant('driver_read_common'),
                utils.make_grant('driver_write_common'),
            ],
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '55',
                        '53',
                        '41',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        'carriers',
                        'parks',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Driver': json.dumps(
                {'enableDelete': True, 'enableScoringBuy': True},
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '55',
                        '53',
                        '41',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        'carriers',
                        'parks',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Driver': json.dumps(
                {
                    'tabtaximeter': True,
                    'tabbalance': True,
                    'tabstatus': True,
                    'tabgps': True,
                    'tabrating': True,
                    'tabrobot': True,
                    'tabhistory': True,
                    'tabcomplaints': True,
                    'tabdocuments': True,
                    'tabrecords': True,
                    'tabaccess': True,
                    'tabcheckcar': True,
                    'disableLimit': True,
                    'disableFIO': True,
                    'disableLicense': True,
                    'disablePriority': True,
                    'disablePhone': True,
                    'disableAlhoritm': True,
                    'disableChangeCar': True,
                    'disableChangeStatus': True,
                    'disableProvider': True,
                    'disableRobot': True,
                    'disableBalancePlus': True,
                    'disableBalanceMinus': True,
                    'disableDocumentAdd': True,
                    'disableDocumentDelete': True,
                    'disableScoringRead': True,
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_DRIVER_PARAMS,
)
async def test_driver_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_MARKETPLACE_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {'grants': [utils.make_grant('read_company_postings')]},
    ),
    (
        'ticket_valid',
        QUERY_PARK2,
        200,
        {'grants': [utils.make_grant('read_company_postings')]},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '61',
                        '75',
                        '56',
                        '71',
                        '72',
                        '32',
                        '12',
                        'parks',
                        'carriers',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Marketplace': json.dumps({}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '61',
                        '75',
                        '56',
                        '71',
                        '72',
                        '32',
                        '12',
                        '13',
                        'parks',
                        'carriers',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Marketplace': json.dumps(
                {
                    'deny_write_company_postings': True,
                    'deny_update_posting': True,
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_MARKETPLACE_PARAMS,
)
async def test_marketplace_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        taxi_config,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    taxi_config.set_values(
        dict(
            TAXIMETER_MARKETPLACE={
                'enable': True,
                'cities': [],
                'countries': [],
                'dbs': [],
                'home_url': '',
            },
        ),
    )

    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_USER_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('users'),
                utils.make_grant('users_grants'),
            ],
        },
    ),
    (
        'ticket_valid',
        QUERY_PARK2,
        200,
        {'grants': [utils.make_grant('users')]},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '24',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'User': json.dumps({}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '24',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'User': json.dumps({'disableEdit': True}),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_USER_PARAMS,
)
async def test_user_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_SUPERUSER_GRANTS_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('aggregator'),
                utils.make_grant('api'),
                utils.make_grant('billing'),
                utils.make_grant('cashbox'),
                utils.make_grant('dashboard_read_common'),
                utils.make_grant('finance_statements_read'),
                utils.make_grant('finance_statements_run'),
                utils.make_grant('finance_statements_write'),
                utils.make_grant('instant_payouts_read'),
                utils.make_grant('report_orders'),
                utils.make_grant('report_orders_download'),
                utils.make_grant('report_orders_moderation'),
                utils.make_grant('report_payouts'),
                utils.make_grant('report_quality'),
                utils.make_grant('report_summary'),
                utils.make_grant('report_summary_download'),
            ],
        },
    ),
    ('ticket_valid', QUERY_PARK2, 200, {'grants': []}),
    (
        'ticket_valid',
        QUERY_PARK3,
        200,
        {
            'grants': [
                utils.make_grant('aggregator'),
                utils.make_grant('api'),
                utils.make_grant('billing'),
                utils.make_grant('car_read_common'),
                utils.make_grant('car_write_common'),
                utils.make_grant('cars_list_download'),
                utils.make_grant('cashbox'),
                utils.make_grant('dashboard_read_common'),
                utils.make_grant('driver_add_money'),
                utils.make_grant('driver_read_common'),
                utils.make_grant('driver_scoring_buy'),
                utils.make_grant('driver_scoring_read'),
                utils.make_grant('driver_withdraw_money'),
                utils.make_grant('driver_write_common'),
                utils.make_grant('drivers_list_download'),
                utils.make_grant('drivers_messages'),
                utils.make_grant('finance_statements_read'),
                utils.make_grant('finance_statements_run'),
                utils.make_grant('finance_statements_write'),
                utils.make_grant('fines'),
                utils.make_grant('gas'),
                utils.make_grant('instant_payouts_read'),
                utils.make_grant('legal_entities'),
                utils.make_grant('map'),
                utils.make_grant('news'),
                utils.make_grant('orders'),
                utils.make_grant('park_contacts_read'),
                utils.make_grant('park_contacts_write'),
                utils.make_grant('payments_groups'),
                utils.make_grant('recurring_payments_read'),
                utils.make_grant('recurring_payments_write'),
                utils.make_grant('report_cash'),
                utils.make_grant('report_cash_download'),
                utils.make_grant('report_orders'),
                utils.make_grant('report_orders_download'),
                utils.make_grant('report_orders_moderation'),
                utils.make_grant('report_payouts'),
                utils.make_grant('report_quality'),
                utils.make_grant('report_summary'),
                utils.make_grant('report_summary_download'),
                utils.make_grant('reports'),
                utils.make_grant('segments'),
                utils.make_grant('segments_download'),
                utils.make_grant('service_pay_system'),
                utils.make_grant('settings'),
                utils.make_grant('support'),
                utils.make_grant('support_chat_read'),
                utils.make_grant('support_chat_write'),
                utils.make_grant('tariffs'),
                utils.make_grant('users'),
                utils.make_grant('users_grants'),
                utils.make_grant('work_rules_write'),
            ],
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid3',
        {
            'user3': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name3',
                    'Group': 'Group3',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1', 'IsSuper': True})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid3',
        {'Group3': json.dumps({'Name': 'Group2', 'IsSuper': True})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '24',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        '72',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '55',
                        '41',
                        '53',
                        '24',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        '72',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_SUPERUSER_GRANTS_PARAMS,
)
async def test_superuser_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_PARK_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('park_contacts_read'),
                utils.make_grant('park_contacts_write'),
            ],
        },
    ),
    (
        'ticket_valid',
        QUERY_PARK2,
        200,
        {'grants': [utils.make_grant('park_contacts_read')]},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '55',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Park': json.dumps({'enableDelete': True}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '55',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'Park': json.dumps({'disableEdit': True}),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_PARK_PARAMS,
)
async def test_park_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_RECURRING_PAYMENTS_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('recurring_payments_read'),
                utils.make_grant('recurring_payments_write'),
            ],
        },
    ),
    (
        'ticket_valid',
        QUERY_PARK2,
        200,
        {'grants': [utils.make_grant('recurring_payments_read')]},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '55',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'parks',
                        'supportChats',
                    ],
                },
            ),
            'RecurringPayments': json.dumps({'disableEdit': False}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '55',
                        'carriers',
                        '71',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'parks',
                        'supportChats',
                    ],
                },
            ),
            'RecurringPayments': json.dumps({'disableEdit': True}),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_RECURRING_PAYMENTS_PARAMS,
)
async def test_recurring_payments_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_RULE_WORK_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK1,
        200,
        {
            'grants': [
                utils.make_grant('tariffs'),
                utils.make_grant('work_rules_write'),
            ],
        },
    ),
    (
        'ticket_valid',
        QUERY_PARK2,
        200,
        {'grants': [utils.make_grant('tariffs')]},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name1',
                    'Group': 'Group1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    [
        'hmset',
        'User:Items:park_valid2',
        {
            'user2': json.dumps(
                {
                    'Enable': True,
                    'Name': 'Name2',
                    'Group': 'Group2',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'Group1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid2',
        {'Group2': json.dumps({'Name': 'Group2'})},
    ],
    [
        'hmset',
        'Access:park_valid1:Group1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '55',
                        'carriers',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'parks',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'RuleWork': json.dumps({'disableEdit': False}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid2:Group2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '52',
                        '41',
                        '53',
                        '72',
                        '24',
                        '61',
                        '75',
                        '56',
                        '55',
                        'carriers',
                        '32',
                        '12',
                        '13',
                        '33',
                        '76',
                        '77',
                        '23',
                        '22',
                        '42',
                        '43',
                        '21',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'parks',
                        'supportChats',
                        'recurringPayments',
                    ],
                },
            ),
            'RuleWork': json.dumps({'disableEdit': True}),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_RULE_WORK_PARAMS,
)
async def test_rule_work_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )
