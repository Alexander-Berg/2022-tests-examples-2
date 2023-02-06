import datetime
import json

import pytest
import pytz

from tests_cashbox_integration import utils


def initialize():
    return (
        'park_id_1',
        'order_id_1',
        datetime.datetime.now(pytz.timezone('Europe/Moscow')),
        'uuid_1',
    )


def enable_periodic_task(taxi_config):
    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )


def create_expected_receipt(status, task_uuid, fail_message, failure_id):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    external_id = 'idempotency_key_1'
    order_price = 250.00
    order_end = datetime.datetime.fromisoformat('2019-10-01T10:10:00+03:00')

    return utils.create_receipt(
        park_id=park_id,
        driver_id=driver_id,
        order_id=order_id,
        cashbox_id=cashbox_id,
        external_id=external_id,
        status=status,
        order_price=order_price,
        order_end=order_end,
        task_uuid=task_uuid,
        fail_message=fail_message,
        failure_id=failure_id,
    )


def check_request_get_token(request):
    assert request['request'].method == 'POST'
    assert json.loads(request['request'].get_data()) == {
        'login': 'login_1',
        'pass': 'password_1',
    }


def check_request_push(request):
    assert request['request'].method == 'POST'
    assert request['request'].headers['Token'] == 'token_1'
    assert json.loads(request['request'].get_data()) == {
        'external_id': 'idempotency_key_1',
        'timestamp': '01-10-2019 07:10:00',
        'receipt': {
            'client': {'email': ' '},
            'company': {
                'email': ' ',
                'inn': '0123456',
                'payment_address': 'https://v4.online.atol.ru',
                'sno': 'usn_income',
            },
            'items': [
                {
                    'name': 'Перевозка пассажиров и багажа',
                    'price': 250.0,
                    'quantity': 1.0,
                    'sum': 250.0,
                    'payment_method': 'full_payment',
                    'payment_object': 'service',
                    'vat': {'type': 'none'},
                },
            ],
            'payments': [{'type': 0, 'sum': 250.0}],
            'total': 250.0,
        },
    }


async def test_invalid_credentials(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/getToken')
    def atol_get_token(request):
        return mockserver.make_response(
            json={
                'timestamp': '123',
                'error': {
                    'code': 12,
                    'error_id': 'error_id_1',
                    'text': 'invalid login or password',
                    'type': 'system',
                },
            },
            status=401,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    check_request_get_token(atol_get_token.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    fail_message = (
        'Service Atol for request \'GetToken\' returned error code '
        '\'12\' and error text \'invalid login or password\''
    )
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=fail_message,
        failure_id='kWrongLoginOrPassword',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_invalid_credentials_pattern_mismatch(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/getToken')
    def atol_get_token(request):
        return mockserver.make_response(
            json={
                'timestamp': '123',
                'error': {
                    'code': 32,
                    'error_id': 'error_id_1',
                    'text': 'invalid Login or Password',
                    'type': 'system',
                },
            },
            status=400,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    check_request_get_token(atol_get_token.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    fail_message = (
        'Service Atol for request \'GetToken\' returned error code \'32\' '
        'and error text \'invalid Login or Password\''
    )
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=fail_message,
        failure_id='kWrongLoginOrPassword',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_wrong_group_code(
        atol_get_token,
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return mockserver.make_response(
            json={
                'timestamp': '123',
                'error': {
                    'code': 20,
                    'error_id': 'error_id_1',
                    'text': 'group code and token dont match',
                    'type': 'system',
                },
            },
            status=401,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_request_push(atol_sell_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    fail_message = (
        'Service Atol for request \'SellReceipt\' returned '
        'error code \'20\' and error text \'group code and token dont match\''
    )
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=fail_message,
        failure_id='kGroupCodeAndTokenDontMatch',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_add_task(
        atol_get_token,
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return {
            'timestamp': '123',
            'uuid': 'uuid_1',
            'error': None,
            'status': 'wait',
        }

    park_id, order_id, updated_at, task_uuid = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_request_push(atol_sell_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status',
        task_uuid=task_uuid,
        fail_message=None,
        failure_id=None,
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] > updated_at


async def test_invalid_token(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return mockserver.make_response(
            json={
                'timestamp': '123',
                'error': {
                    'code': 10,
                    'error_id': 'error_id_1',
                    'text': 'invalid token',
                    'type': 'system',
                },
            },
            status=401,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_request_push(atol_sell_receipt.next_call())

    fail_message = (
        'Service Atol for request \'SellReceipt\' returned '
        'error code \'10\' and error text \'invalid token\''
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=fail_message,
        failure_id='kMissingToken',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_expired_token(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return mockserver.make_response(
            json={
                'timestamp': '123',
                'error': {
                    'code': 11,
                    'error_id': 'error_id_1',
                    'text': 'expired token',
                    'type': 'system',
                },
            },
            status=401,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_request_push(atol_sell_receipt.next_call())

    fail_message = (
        'Service Atol for request \'SellReceipt\' returned '
        'error code \'11\' and error text \'expired token\''
    )
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=fail_message,
        failure_id='kExpiredToken',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_add_exists_task(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return {
            'timestamp': '123',
            'status': 'wait',
            'uuid': 'uuid_1',
            'error': {
                'code': 33,
                'error_id': 'error_id_1',
                'text': 'the task is exists',
            },
        }

    park_id, order_id, updated_at, task_uuid = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_request_push(atol_sell_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status',
        task_uuid=task_uuid,
        fail_message=None,
        failure_id=None,
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] > updated_at


async def test_tin_not_found(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return {
            'uuid': '12345',
            'timestamp': '11.11.2019 10:00:00',
            'status': 'fail',
            'error': {'code': 2, 'text': 'tax not found', 'type': 'agent'},
        }

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='fail',
        task_uuid=None,
        fail_message='Atol: tax not found',
        failure_id='kUnknownInn',
    )

    check_request_get_token(atol_get_token.next_call())
    check_request_push(atol_sell_receipt.next_call())

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] > updated_at


async def test_update_invalid_token(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return mockserver.make_response(
            json={
                'timestamp': '123',
                'error': {
                    'code': 10,
                    'error_id': 'error_id_1',
                    'text': 'invalid token',
                    'type': 'system',
                },
            },
            status=401,
        )

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 2,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1
    check_request_get_token(atol_get_token.next_call())

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1
    check_request_get_token(atol_get_token.next_call())


async def test_update_expired_token(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return mockserver.make_response(
            json={
                'timestamp': '123',
                'error': {
                    'code': 11,
                    'error_id': 'error_id_1',
                    'text': 'expired token',
                    'type': 'system',
                },
            },
            status=401,
        )

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 2,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1
    check_request_get_token(atol_get_token.next_call())

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1
    check_request_get_token(atol_get_token.next_call())


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        """
        INSERT INTO cashbox_integration.receipts(
            park_id,
            driver_id,
            order_id,
            cashbox_id,
            external_id,
            status,
            created_at,
            updated_at,
            order_price,
            order_end,
            fail_message,
            failure_id
        )
        VALUES (
            'park_id_1',
            'driver_id_1',
            'order_id_1',
            'cashbox_id_1',
            'idempotency_key_1',
            'push_to_cashbox',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            '250.00',
            '2019-10-01T10:10:00',
            'fail_message',
            'kWrongLoginOrPassword'
        );
        """,
        """
        INSERT INTO cashbox_integration.cashboxes(
            park_id,
            id,
            idempotency_token,
            date_created,
            date_updated,
            state,
            is_current,
            cashbox_type,
            details,
            secrets
        )
        VALUES (
            'park_id_1',
            'cashbox_id_1',
            'idemp_1',
            '2019-06-22 19:10:25-07',
            '2019-06-22 19:10:25-07',
            'valid',
            'TRUE',
            'atol_online',
            '{
                "tin_pd_id": "0123456789",
                "tax_scheme_type": "simple_income",
                "group_code": "group-code-1"
            }',
            '{
                "login": "N9Ih+w8vaAoBkF3PpUxXnw==",
                "password": "8Ay7OVs/82E0EnKqEKqKqw=="
            }'
        );
        """,
    ],
)
async def test_update_failed_fileds(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-atol/possystem/v4/group-code-1/sell')
    def atol_sell_receipt(request):
        return {
            'timestamp': '123',
            'uuid': 'uuid_1',
            'error': None,
            'status': 'wait',
        }

    park_id, order_id, updated_at, task_uuid = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_request_push(atol_sell_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status',
        task_uuid=task_uuid,
        fail_message=None,
        failure_id=None,
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] != updated_at
