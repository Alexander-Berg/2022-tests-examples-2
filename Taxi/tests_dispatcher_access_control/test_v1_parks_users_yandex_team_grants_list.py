import json

import pytest

from testsuite.utils import ordered_object

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/users/yandex-team/grants/list'

CHATTERBOX_TICKET_ID = '0cf94043629526419e77b82e'

QUERY_PARK1 = {'query': {'park': {'id': 'park_valid1'}}}

QUERY_PARK2 = {'query': {'park': {'id': 'park_valid2'}}}


async def common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_grants,
):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        params={'chatterbox_ticket_id': CHATTERBOX_TICKET_ID},
        headers={
            'X-Remote-IP': '127.0.0.1',
            'X-Ya-User-Ticket': user_ticket,
            'X-Ya-User-Ticket-Provider': 'yandex_team',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == code, response.text
    expected_response = {
        'grants': [
            utils.make_grant(grant) for grant in expected_grants['grants']
        ],
    }

    ordered_object.assert_eq(response.json(), expected_response, ['grants'])


TEST_USER_PARAMS = [  # type: ignore
    ('ticket_valid1', QUERY_PARK1, 200, {'grants': []}),
    ('ticket_valid2', QUERY_PARK2, 200, {'grants': []}),
]


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:Assessor', 'test2'],
    ['sadd', 'admin:rolemembers:SpamSender', 'test2'],
    ['sadd', 'admin:rolemembers:PassengerSupport', 'test2'],
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


TEST_ADMIN_PARAMS = [
    (
        'ticket_valid1',
        QUERY_PARK1,
        200,
        {
            'grants': [
                'support_chat_read',
                'support_chat_write',
                'recurring_payments_read',
                'recurring_payments_write',
                'driver_read_common',
                'driver_read_taximeter',
                'driver_read_balance',
                'driver_read_status',
                'driver_read_gps',
                'driver_read_rating',
                'driver_read_robot',
                'driver_read_orders',
                'driver_read_complaints',
                'driver_read_documents',
                'driver_read_records',
                'driver_read_edits',
                'driver_read_qc',
                'driver_write_common',
                'driver_write_balance_limit',
                'driver_write_priority',
                'driver_write_phone',
                'driver_write_rule_work',
                'driver_write_car',
                'driver_write_work_status',
                'driver_write_provider',
                'driver_write_robot',
                'driver_add_money',
                'driver_withdraw_money',
                'driver_add_documents',
                'driver_delete_documents',
                'driver_delete',
                'driver_transaction_read',
                'driver_transaction_write',
                'driver_transaction_revert',
                'driver_scoring_read',
                'driver_scoring_buy',
                'company_read',
                'company_write',
                'company_delete',
                'users',
                'park_contacts_read',
                'park_contacts_write',
                'users_grants',
                'car_read_common',
                'car_read_drivers',
                'car_read_documents',
                'car_read_edits',
                'car_write_common',
                'car_write_permit',
                'car_add_documents',
                'car_delete_documents',
                'car_delete',
                'reports',
                'orders_moderation',
                'settings',
                'payments_groups',
                'tariffs',
                'drivers_messages',
                'news',
                'support',
                'fines',
                'cabinet_taxi',
                'waybills',
                'legal_list',
                'shifts',
                'service_pay_system',
                'report_cash',
                'cashbox',
                'api',
                'carriers',
                'orders',
                'segments',
                'legal_entities',
                'gas',
                'map',
                'work_rules_write',
            ],
        },
    ),
]


@pytest.mark.redis_store(['sadd', 'admin:rolemembers:Admin', 'test1'])
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_ADMIN_PARAMS,
)
async def test_admin_grants(
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

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


READ_ONLY_GRANTS = {
    'grants': [
        'driver_read_common',
        'driver_read_taximeter',
        'driver_read_balance',
        'driver_read_status',
        'driver_read_gps',
        'driver_read_rating',
        'driver_read_robot',
        'driver_read_orders',
        'driver_read_complaints',
        'driver_read_documents',
        'driver_read_records',
        'driver_read_edits',
        'driver_read_qc',
        'driver_scoring_read',
        'driver_transaction_read',
        'company_read',
        'users',
        'park_contacts_read',
        'car_read_common',
        'car_read_drivers',
        'car_read_documents',
        'car_read_edits',
        'reports',
        'settings',
        'payments_groups',
        'recurring_payments_read',
        'tariffs',
        'drivers_messages',
        'news',
        'support',
        'fines',
        'cabinet_taxi',
        'legal_list',
        'waybills',
        'shifts',
        'service_pay_system',
        'report_cash',
        'cashbox',
        'api',
        'carriers',
        'orders',
        'segments',
        'legal_entities',
        'gas',
        'map',
        'users_grants',
    ],
}

TEST_READ_ONLY_PARAMS = [
    ('ticket_valid1', QUERY_PARK1, 200, READ_ONLY_GRANTS),
    ('ticket_valid2', QUERY_PARK1, 200, READ_ONLY_GRANTS),
    ('ticket_valid3', QUERY_PARK1, 200, READ_ONLY_GRANTS),
    ('ticket_valid4', QUERY_PARK1, 200, READ_ONLY_GRANTS),
    ('ticket_valid5', QUERY_PARK1, 200, READ_ONLY_GRANTS),
    ('ticket_valid6', QUERY_PARK1, 200, READ_ONLY_GRANTS),
    ('ticket_valid7', QUERY_PARK1, 200, READ_ONLY_GRANTS),
    ('ticket_valid8', QUERY_PARK1, 200, READ_ONLY_GRANTS),
]


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:ReadOnly', 'test1'],
    ['sadd', 'admin:rolemembers:Basic', 'test2'],
    ['sadd', 'admin:rolemembers:RegionalManager', 'test3'],
    ['sadd', 'admin:rolemembers:Aggregators', 'test4'],
    ['sadd', 'admin:rolemembers:QualityServiceManager', 'test5'],
    ['sadd', 'admin:rolemembers:DriverExperiments', 'test6'],
    ['sadd', 'admin:rolemembers:CategoriesManager', 'test7'],
    ['sadd', 'admin:rolemembers:LinkReadOnly', 'test8'],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_READ_ONLY_PARAMS,
)
async def test_read_only_grants(
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
    blackbox_service.set_user_ticket_info(
        'ticket_valid3', uid='100', login='test3',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid4', uid='100', login='test4',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid5', uid='100', login='test5',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid6', uid='100', login='test6',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid7', uid='100', login='test7',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid8', uid='100', login='test8',
    )

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_HIRE_DRIVERS_PARAMS = [
    (
        'ticket_valid1',
        QUERY_PARK1,
        200,
        {
            'grants': [
                'driver_read_common',
                'driver_read_taximeter',
                'driver_read_balance',
                'driver_read_status',
                'driver_read_gps',
                'driver_read_rating',
                'driver_read_robot',
                'driver_read_orders',
                'driver_read_complaints',
                'driver_read_documents',
                'driver_read_records',
                'driver_read_edits',
                'driver_read_qc',
                'driver_write_common',
                'driver_write_balance_limit',
                'driver_write_priority',
                'driver_write_phone',
                'driver_write_rule_work',
                'driver_write_car',
                'driver_write_work_status',
                'driver_write_provider',
                'driver_write_robot',
                'driver_add_documents',
                'driver_delete_documents',
                'driver_delete',
                'driver_transaction_read',
                'company_read',
                'users',
                'park_contacts_read',
                'park_contacts_write',
                'car_read_common',
                'car_read_drivers',
                'car_read_documents',
                'car_read_edits',
                'car_write_common',
                'car_write_permit',
                'car_add_documents',
                'car_delete_documents',
                'car_delete',
                'reports',
                'orders_moderation',
                'settings',
                'payments_groups',
                'tariffs',
                'drivers_messages',
                'news',
                'support',
                'fines',
                'cabinet_taxi',
                'legal_list',
                'waybills',
                'shifts',
                'service_pay_system',
                'report_cash',
                'cashbox',
                'api',
                'carriers',
                'orders',
                'segments',
                'legal_entities',
                'gas',
                'map',
            ],
        },
    ),
]


@pytest.mark.redis_store(['sadd', 'admin:rolemembers:HireDrivers', 'test1'])
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response', TEST_HIRE_DRIVERS_PARAMS,
)
async def test_hire_drivers_grants(
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

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


DRIVER_SUPPORT_GRANTS = {
    'grants': [
        'driver_read_common',
        'driver_read_taximeter',
        'driver_read_balance',
        'driver_read_status',
        'driver_read_gps',
        'driver_read_rating',
        'driver_read_robot',
        'driver_read_orders',
        'driver_read_complaints',
        'driver_read_documents',
        'driver_read_records',
        'driver_read_edits',
        'driver_read_qc',
        'driver_transaction_read',
        'company_read',
        'users',
        'waybills',
        'park_contacts_read',
        'park_contacts_write',
        'car_read_common',
        'car_read_drivers',
        'car_read_documents',
        'car_read_edits',
        'car_write_common',
        'car_write_permit',
        'car_add_documents',
        'car_delete_documents',
        'car_delete',
        'reports',
        'orders_moderation',
        'settings',
        'payments_groups',
        'tariffs',
        'drivers_messages',
        'news',
        'support',
        'fines',
        'cabinet_taxi',
        'legal_list',
        'shifts',
        'service_pay_system',
        'report_cash',
        'cashbox',
        'api',
        'carriers',
        'orders',
        'segments',
        'legal_entities',
        'gas',
        'map',
    ],
}

TEST_DRIVER_SUPPORT_PARAMS = [
    ('ticket_valid1', QUERY_PARK1, 200, DRIVER_SUPPORT_GRANTS),
    ('ticket_valid2', QUERY_PARK2, 200, DRIVER_SUPPORT_GRANTS),
]


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:DriverSupport', 'test1'],
    ['sadd', 'admin:rolemembers:DriverSupportBasic', 'test2'],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_DRIVER_SUPPORT_PARAMS,
)
async def test_driver_support_grants(
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


TEST_PARTNER_SUPPORT_PARAMS = [
    (
        'ticket_valid1',
        QUERY_PARK1,
        200,
        {
            'grants': [
                'driver_read_common',
                'driver_read_taximeter',
                'driver_read_balance',
                'driver_read_status',
                'driver_read_gps',
                'driver_read_rating',
                'driver_read_robot',
                'park_contacts_read',
                'park_contacts_write',
                'driver_read_orders',
                'driver_read_complaints',
                'driver_read_documents',
                'driver_read_records',
                'driver_read_edits',
                'driver_read_qc',
                'driver_transaction_read',
                'company_read',
                'users',
                'waybills',
                'users_grants',
                'car_read_common',
                'car_read_drivers',
                'car_read_documents',
                'car_read_edits',
                'reports',
                'orders_moderation',
                'settings',
                'payments_groups',
                'tariffs',
                'drivers_messages',
                'news',
                'support',
                'fines',
                'cabinet_taxi',
                'legal_list',
                'shifts',
                'service_pay_system',
                'report_cash',
                'cashbox',
                'api',
                'carriers',
                'orders',
                'segments',
                'legal_entities',
                'gas',
                'map',
            ],
        },
    ),
]


@pytest.mark.redis_store(['sadd', 'admin:rolemembers:PartnerSupport', 'test1'])
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_PARTNER_SUPPORT_PARAMS,
)
async def test_partner_support_grants(
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

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_L1_DRIVER_SUPPORT_PARAMS = [
    (
        'ticket_valid1',
        QUERY_PARK1,
        200,
        {
            'grants': [
                'driver_read_common',
                'car_add_documents',
                'car_delete_documents',
                'car_read_common',
                'car_delete',
                'car_read_drivers',
                'car_read_edits',
                'car_write_common',
                'car_write_permit',
                'driver_add_documents',
                'driver_delete',
                'driver_delete_documents',
                'driver_read_balance',
                'driver_read_complaints',
                'driver_read_documents',
                'driver_read_edits',
                'driver_read_gps',
                'driver_read_orders',
                'driver_read_qc',
                'driver_read_rating',
                'driver_read_records',
                'driver_read_robot',
                'driver_read_status',
                'driver_read_taximeter',
                'driver_write_balance_limit',
                'driver_write_car',
                'driver_write_common',
                'driver_write_phone',
                'driver_write_priority',
                'driver_write_provider',
                'driver_write_robot',
                'driver_write_rule_work',
                'driver_write_work_status',
                'report_cash',
                'reports',
                'orders_moderation',
                'orders',
                'car_read_documents',
            ],
        },
    ),
]


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:L1DriverSupport', 'test1'],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_L1_DRIVER_SUPPORT_PARAMS,
)
async def test_l1_support_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/chatterbox/v1/user/check_data_access')
    def mock_chatterbox(request):
        assert all(
            [
                request.headers['X-Ya-User-Ticket'],
                request.headers['X-Yandex-UID'],
                request.headers['X-Real-IP'],
            ],
        )
        assert request.method == 'POST'

        assert json.loads(request.get_data()) == {
            'chatterbox_id': CHATTERBOX_TICKET_ID,
            'meta_info': {'park_db_id': 'park_valid1'},
        }

        return {'access_status': 'permitted'}

    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )

    assert mock_chatterbox.times_called == 1


TEST_REGIONAL_CHAT_MANAGER_GRANTS = [
    ('ticket_valid1', QUERY_PARK1, 200, {'grants': ['support_chat_read']}),
]


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:RegionalChatManager', 'test1'],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_REGIONAL_CHAT_MANAGER_GRANTS,
)
async def test_regional_chat_manager_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
        mockserver,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )


TEST_L1_SUPPORT_WITH_CHAT_GRANTS = [
    (
        'ticket_valid1',
        QUERY_PARK1,
        200,
        {
            'grants': [
                'support_chat_read',
                'driver_read_common',
                'car_add_documents',
                'car_delete_documents',
                'car_read_common',
                'car_delete',
                'car_read_drivers',
                'car_read_edits',
                'car_write_common',
                'car_write_permit',
                'driver_add_documents',
                'driver_delete',
                'driver_delete_documents',
                'driver_read_balance',
                'driver_read_complaints',
                'driver_read_documents',
                'driver_read_edits',
                'driver_read_gps',
                'driver_read_orders',
                'driver_read_qc',
                'driver_read_rating',
                'driver_read_records',
                'driver_read_robot',
                'driver_read_status',
                'driver_read_taximeter',
                'driver_write_balance_limit',
                'driver_write_car',
                'driver_write_common',
                'driver_write_phone',
                'driver_write_priority',
                'driver_write_provider',
                'driver_write_robot',
                'driver_write_rule_work',
                'driver_write_work_status',
                'report_cash',
                'reports',
                'orders_moderation',
                'orders',
                'car_read_documents',
            ],
        },
    ),
]


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:L1DriverSupport', 'test1'],
    ['sadd', 'admin:rolemembers:RegionalChatManager', 'test1'],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_L1_SUPPORT_WITH_CHAT_GRANTS,
)
async def test_l1_support_with_chat_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        user_ticket,
        payload,
        code,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/chatterbox/v1/user/check_data_access')
    def mock_chatterbox(request):
        assert all(
            [
                request.headers['X-Ya-User-Ticket'],
                request.headers['X-Yandex-UID'],
                request.headers['X-Real-IP'],
            ],
        )
        assert request.method == 'POST'

        assert json.loads(request.get_data()) == {
            'chatterbox_id': CHATTERBOX_TICKET_ID,
            'meta_info': {'park_db_id': 'park_valid1'},
        }

        return {'access_status': 'permitted'}

    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )

    assert mock_chatterbox.times_called == 1


TEST_BALANCE_EDIT_SUPPORT_PARAMS = [
    (
        'ticket_valid1',
        QUERY_PARK1,
        200,
        {'grants': ['driver_add_money', 'driver_withdraw_money']},
    ),
]


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:BalanceEditSupport', 'test1'],
)
@pytest.mark.parametrize(
    'user_ticket, payload, code, expected_response',
    TEST_BALANCE_EDIT_SUPPORT_PARAMS,
)
async def test_balance_edit_support(
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

    await common_request(
        taxi_dispatcher_access_control,
        user_ticket,
        payload,
        code,
        expected_response,
    )
