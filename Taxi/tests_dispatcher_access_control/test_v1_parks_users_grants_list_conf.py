import json

import pytest

from testsuite.utils import ordered_object

from tests_dispatcher_access_control import utils

YANDEX_ENDPOINT = 'v1/parks/users/yandex/grants/list'
YANDEX_TEAM_ENDPOINT = 'v1/parks/users/yandex-team/grants/list'

QUERY_PARK = {'query': {'park': {'id': 'park_valid1'}}}


async def common_request(
        taxi_dispatcher_access_control,
        endpoint_url,
        provider,
        user_ticket,
        payload,
        code,
        expected_response,
):
    response = await taxi_dispatcher_access_control.post(
        endpoint_url,
        json=payload,
        headers={
            'X-Remote-IP': '127.0.0.1',
            'X-Ya-User-Ticket': user_ticket,
            'X-Ya-User-Ticket-Provider': provider,
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )
    assert response.status_code == code
    ordered_object.assert_eq(response.json(), expected_response, ['grants'])


TEST_MARKETPLACE_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': False,
            'cities': [],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        200,
        {'grants': []},
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': [],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        200,
        {'grants': [utils.make_grant('read_company_postings')]},
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': [],
            'countries': [],
            'dbs': ['park_valid1'],
            'home_url': '',
        },
        200,
        {'grants': [utils.make_grant('read_company_postings')]},
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': ['city1'],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        200,
        {'grants': [utils.make_grant('read_company_postings')]},
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': [],
            'countries': ['cid1'],
            'dbs': [],
            'home_url': '',
        },
        200,
        {'grants': [utils.make_grant('read_company_postings')]},
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': ['some_city'],
            'countries': ['some_country'],
            'dbs': ['some_park_id'],
            'home_url': '',
        },
        200,
        {'grants': []},
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
                        '61',
                        '75',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '71',
                        '72',
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
                        'supportChats',
                        'recurringPayments',
                        'segments',
                        '82',
                        '44',
                        'map',
                    ],
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, marketplace, code, expected_response',
    TEST_MARKETPLACE_PARAMS,
)
async def test_marketplace_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        taxi_config,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        marketplace,
        code,
        expected_response,
):
    taxi_config.set_values(dict(TAXIMETER_MARKETPLACE=marketplace))

    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        YANDEX_ENDPOINT,
        'yandex',
        user_ticket,
        payload,
        code,
        expected_response,
    )


DRIVER_NEW_GRANTS = {
    'grants': [
        utils.make_grant('driver_read_common'),
        utils.make_grant('driver_write_common'),
        utils.make_grant('driver_add_money'),
        utils.make_grant('driver_withdraw_money'),
        utils.make_grant('driver_scoring_read'),
    ],
}

DRIVER_OLD_GRANTS = {
    'grants': [
        utils.make_grant('driver_read_common'),
        utils.make_grant('driver_write_common'),
        utils.make_grant('driver_add_money'),
        utils.make_grant('driver_withdraw_money'),
        utils.make_grant('driver_scoring_read'),
    ],
}

TEST_DRIVER_PARAMS = [
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': False,
            'cities': [],
            'countries': [],
            'dbs': [],
            'grace_days': 0,
            'self_employed_partners_included': False,
        },
        200,
        DRIVER_OLD_GRANTS,
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': [],
            'countries': [],
            'dbs': [],
            'grace_days': 0,
            'self_employed_partners_included': False,
        },
        200,
        DRIVER_NEW_GRANTS,
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': [],
            'countries': [],
            'dbs': ['park_valid1'],
            'grace_days': 0,
            'self_employed_partners_included': False,
        },
        200,
        DRIVER_NEW_GRANTS,
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': ['city1'],
            'countries': [],
            'dbs': [],
            'grace_days': 0,
            'self_employed_partners_included': False,
        },
        200,
        DRIVER_NEW_GRANTS,
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': [],
            'countries': ['cid1'],
            'dbs': [],
            'grace_days': 0,
            'self_employed_partners_included': False,
        },
        200,
        DRIVER_NEW_GRANTS,
    ),
    (
        'ticket_valid',
        QUERY_PARK,
        {
            'enable': True,
            'cities': ['some_city'],
            'countries': ['some_country'],
            'dbs': ['some_park_id'],
            'grace_days': 0,
            'self_employed_partners_included': False,
        },
        200,
        DRIVER_OLD_GRANTS,
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
                        '55',
                        '41',
                        '53',
                        '61',
                        '75',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '71',
                        '72',
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
                        '24',
                        'supportChats',
                        'recurringPayments',
                        'segments',
                        '82',
                        '44',
                        'map',
                    ],
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'user_ticket, payload, deny_edit, code, expected_response',
    TEST_DRIVER_PARAMS,
)
async def test_driver_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        taxi_config,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        deny_edit,
        code,
        expected_response,
):
    taxi_config.set_values(
        dict(TAXIMETER_DENY_EDIT_DRIVER_NAME_AND_LICENSE=deny_edit),
    )

    blackbox_service.set_user_ticket_info(
        'ticket_valid', uid='100', login='test',
    )
    await common_request(
        taxi_dispatcher_access_control,
        YANDEX_ENDPOINT,
        'yandex',
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_MARKETPLACE_YATEAM_PARAMS = [
    (
        'ticket_valid1',
        QUERY_PARK,
        {
            'enable': True,
            'cities': [],
            'countries': [],
            'dbs': [],
            'home_url': '',
        },
        200,
        {
            'grants': [
                utils.make_grant('read_company_postings'),
                utils.make_grant('write_company_postings'),
                utils.make_grant('update_posting'),
                utils.make_grant('driver_read_common'),
                utils.make_grant('driver_read_taximeter'),
                utils.make_grant('driver_read_balance'),
                utils.make_grant('driver_read_status'),
                utils.make_grant('driver_read_gps'),
                utils.make_grant('driver_read_rating'),
                utils.make_grant('driver_read_robot'),
                utils.make_grant('driver_read_orders'),
                utils.make_grant('driver_read_complaints'),
                utils.make_grant('driver_read_documents'),
                utils.make_grant('driver_read_records'),
                utils.make_grant('driver_read_edits'),
                utils.make_grant('driver_read_qc'),
                utils.make_grant('driver_write_common'),
                utils.make_grant('driver_write_balance_limit'),
                utils.make_grant('driver_write_priority'),
                utils.make_grant('driver_write_phone'),
                utils.make_grant('driver_write_rule_work'),
                utils.make_grant('driver_write_car'),
                utils.make_grant('driver_write_work_status'),
                utils.make_grant('driver_write_provider'),
                utils.make_grant('driver_write_robot'),
                utils.make_grant('driver_add_money'),
                utils.make_grant('driver_withdraw_money'),
                utils.make_grant('driver_add_documents'),
                utils.make_grant('driver_delete_documents'),
                utils.make_grant('driver_delete'),
                utils.make_grant('driver_transaction_read'),
                utils.make_grant('driver_transaction_write'),
                utils.make_grant('driver_transaction_revert'),
                utils.make_grant('driver_scoring_read'),
                utils.make_grant('driver_scoring_buy'),
                utils.make_grant('company_read'),
                utils.make_grant('cashbox'),
                utils.make_grant('api'),
                utils.make_grant('carriers'),
                utils.make_grant('park_contacts_read'),
                utils.make_grant('park_contacts_write'),
                utils.make_grant('company_write'),
                utils.make_grant('company_delete'),
                utils.make_grant('users'),
                utils.make_grant('users_grants'),
                utils.make_grant('car_read_common'),
                utils.make_grant('car_read_drivers'),
                utils.make_grant('car_read_documents'),
                utils.make_grant('car_read_edits'),
                utils.make_grant('car_write_common'),
                utils.make_grant('car_write_permit'),
                utils.make_grant('car_add_documents'),
                utils.make_grant('car_delete_documents'),
                utils.make_grant('car_delete'),
                utils.make_grant('reports'),
                utils.make_grant('settings'),
                utils.make_grant('payments_groups'),
                utils.make_grant('tariffs'),
                utils.make_grant('drivers_messages'),
                utils.make_grant('news'),
                utils.make_grant('support'),
                utils.make_grant('fines'),
                utils.make_grant('cabinet_taxi'),
                utils.make_grant('legal_list'),
                utils.make_grant('waybills'),
                utils.make_grant('shifts'),
                utils.make_grant('service_pay_system'),
                utils.make_grant('report_cash'),
                utils.make_grant('orders'),
                utils.make_grant('segments'),
                utils.make_grant('legal_entities'),
                utils.make_grant('gas'),
                utils.make_grant('orders_moderation'),
                utils.make_grant('map'),
                utils.make_grant('support_chat_read'),
                utils.make_grant('support_chat_write'),
                utils.make_grant('recurring_payments_read'),
                utils.make_grant('recurring_payments_write'),
                utils.make_grant('work_rules_write'),
            ],
        },
    ),
]


@pytest.mark.redis_store(['sadd', 'admin:rolemembers:Admin', 'test1'])
@pytest.mark.parametrize(
    'user_ticket, payload, marketplace, code, expected_response',
    TEST_MARKETPLACE_YATEAM_PARAMS,
)
async def test_marketplace_yateam_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        taxi_config,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        marketplace,
        code,
        expected_response,
):
    taxi_config.set_values(dict(TAXIMETER_MARKETPLACE=marketplace))

    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    await common_request(
        taxi_dispatcher_access_control,
        YANDEX_TEAM_ENDPOINT,
        'yandex_team',
        user_ticket,
        payload,
        code,
        expected_response,
    )
