import datetime
import json

from tests_cashbox_integration import utils


def initialize():
    return (
        'park_id_1',
        'order_id_1',
        datetime.datetime.fromisoformat('2019-10-01T10:05:00+03:00'),
    )


def enable_periodic_task(taxi_config):
    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 1,
            },
        },
    )


def create_expected_receipt(
        status, failure_id, fail_message=None, url=None, details=None,
):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    external_id = 'idempotency_key_1'
    created_at = datetime.datetime.fromisoformat('2019-10-01T10:05:00+03:00')
    order_price = 250.00
    task_uuid = 'uuid_1'
    order_end = datetime.datetime.fromisoformat('2019-10-01T10:05:00+03:00')

    receipt = utils.create_receipt(
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
        url=url,
        details=details,
        failure_id=failure_id,
    )
    receipt['created_at'] = created_at
    return receipt


def check_request_get_token(request):
    assert request['request'].method == 'POST'
    assert json.loads(request['request'].get_data()) == {
        'login': 'login_1',
        'pass': 'password_1',
    }


def check_report_receipt(request):
    assert request['request'].method == 'GET'
    assert request['request'].headers['Token'] == 'token_1'


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

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    check_request_get_token(atol_get_token.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    fail_message = (
        'Service Atol for request \'GetToken\' returned error code '
        '\'12\' and error text \'invalid login or password\''
    )
    expected_receipt = create_expected_receipt(
        status='wait_status',
        fail_message=fail_message,
        failure_id='kWrongLoginOrPassword',
    )
    expected_receipt['updated_at'] = updated_at

    utils.compare_receipt(receipt, expected_receipt)


async def test_wait_status(
        atol_get_token,
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
    def atol_report_receipt(request):
        return {
            'timestamp': '123',
            'error': {
                'error_id': 'error_id_1',
                'code': 34,
                'text': 'not found',
                'type': 'system',
            },
            'status': 'wait',
        }

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_report_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_report_receipt(atol_report_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status', fail_message=None, failure_id=None,
    )
    expected_receipt['updated_at'] = updated_at

    utils.compare_receipt(receipt, expected_receipt)


async def test_get_receipt(
        atol_get_token,
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    details = {
        'total': 200,
        'fns_site': 'site',
        'fn_number': 'fn_number',
        'shift_number': 23,
        'receipt_datetime': 'time',
        'fiscal_receipt_number': 6,
        'fiscal_document_number': 133,
        'ecr_registration_number': 'ecr_number',
        'fiscal_document_attribute': 155,
        'ofd_receipt_url': 'link',
    }

    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
    def atol_report_receipt(request):
        return {
            'timestamp': '123',
            'uuid': 'uuid_1',
            'error': None,
            'status': 'done',
            'payload': details,
        }

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_report_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_report_receipt(atol_report_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='complete',
        fail_message=None,
        failure_id=None,
        url=details['ofd_receipt_url'],
        details=details,
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] != updated_at


async def test_token_not_found(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
    def atol_report_receipt(request):
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

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_report_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_report_receipt(atol_report_receipt.next_call())

    fail_message = (
        'Service Atol for request \'Report\' returned '
        'error code \'10\' and error text \'invalid token\''
    )
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status',
        fail_message=fail_message,
        failure_id='kMissingToken',
    )
    expected_receipt['updated_at'] = updated_at

    utils.compare_receipt(receipt, expected_receipt)


async def test_expired_token(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
    def atol_report_receipt(request):
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

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_report_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_report_receipt(atol_report_receipt.next_call())

    fail_message = (
        'Service Atol for request \'Report\' returned error code '
        '\'11\' and error text \'expired token\''
    )
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status',
        fail_message=fail_message,
        failure_id='kExpiredToken',
    )
    expected_receipt['updated_at'] = updated_at

    utils.compare_receipt(receipt, expected_receipt)


async def test_fail_receipt(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
    def atol_report_receipt(request):
        return {
            'timestamp': '123',
            'uuid': 'uuid_1',
            'error': {'code': 123, 'text': 'document invalid'},
            'status': 'fail',
        }

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_report_receipt.times_called >= 1

    check_request_get_token(atol_get_token.next_call())
    check_report_receipt(atol_report_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='fail',
        fail_message='Atol: document invalid',
        failure_id='kUnknownReceiptError',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] != updated_at


async def test_update_invalid_token(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
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
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 2,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1
    check_request_get_token(atol_get_token.next_call())

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

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
    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
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
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 3,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1
    check_request_get_token(atol_get_token.next_call())

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1
    check_request_get_token(atol_get_token.next_call())


async def test_timeout_error(
        mockserver,
        taxi_cashbox_integration,
        atol_get_token,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-atol/possystem/v4/group-code-1/report/uuid_1',
    )
    def atol_sell_receipt(request):
        return {
            'timestamp': '123',
            'uuid': 'uuid_1',
            'error': {'code': 1, 'error_id': 'error_id_1', 'text': 'timeout'},
            'status': 'fail',
        }

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    assert atol_get_token.times_called >= 1
    assert atol_sell_receipt.times_called >= 1

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    expected_receipt = create_expected_receipt(
        status='push_to_cashbox', failure_id=None, fail_message=None,
    )
    expected_receipt['task_uuid'] = None
    prev_external_id = expected_receipt.pop('external_id')

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] != updated_at
    assert receipt['external_id'] != prev_external_id
