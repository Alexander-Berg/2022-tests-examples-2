import base64

import pytest

from tests_cashbox_integration import utils


def check_receipt(
        receipt,
        park_id,
        order_id,
        status,
        driver_id,
        external_id,
        order_price,
        task_uuid,
        failure_id,
        fail_message=None,
):
    assert receipt['park_id'] == park_id
    assert receipt['order_id'] == order_id
    assert receipt['status'] == status
    assert receipt['driver_id'] == driver_id
    assert receipt['external_id'] == external_id
    assert receipt['order_price'] == order_price
    assert receipt['task_uuid'] == task_uuid
    assert receipt['fail_message'] == fail_message
    assert receipt['failure_id'] == failure_id


def check_request(request, amount, calculation_place):
    assert (
        amount == request['request'].json['CustomerReceipt']['amounts']['cash']
    )
    assert (
        calculation_place
        == request['request'].json['CustomerReceipt']['calculationPlace']
    )
    assert len(request['request'].headers['X-Request-ID']) >= 1


def create_credentials(public_id, api_secret):
    credentials = f'{public_id}:{api_secret}'
    encoded_credentials = base64.b64encode(credentials.encode())
    string_credentials = encoded_credentials.decode('utf-8')
    return f'Basic {string_credentials}'


async def test_add_task(
        taxi_cashbox_integration,
        cloud_kassir_service,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    credentials = create_credentials('super_park', 'passw0rd')
    inn = '0123456'
    uuid = 'uuid_1'
    cloud_kassir_service.set_data_for_post_receipt(credentials, inn, uuid)

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert cloud_kassir_service.post_receipt_handler.times_called >= 1

    request = cloud_kassir_service.post_receipt_handler.next_call()
    check_request(request, 250.0, 'Машина такси')

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_1', 'order_id_1')
    check_receipt(
        receipt,
        'park_id_1',
        'order_id_1',
        'wait_status',
        'driver_id_1',
        'idempotency_key_1',
        250.00,
        uuid,
        failure_id=None,
    )


async def test_inn_not_found(
        taxi_cashbox_integration,
        cloud_kassir_service,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    credentials = create_credentials('super_park', 'passw0rd')
    inn = None
    uuid = 'uuid_1'
    cloud_kassir_service.set_data_for_post_receipt(credentials, inn, uuid)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert cloud_kassir_service.post_receipt_handler.times_called >= 1

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_1', 'order_id_1')

    fail_message = (
        'cloud kassir error: message Компания с ИНН 0123456 не найдена'
    )
    check_receipt(
        receipt,
        'park_id_1',
        'order_id_1',
        'fail',
        'driver_id_1',
        'idempotency_key_1',
        250.00,
        None,
        failure_id='kUnknownInn',
        fail_message=fail_message,
    )


async def test_wrong_credentials(
        taxi_cashbox_integration,
        cloud_kassir_service,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert cloud_kassir_service.post_receipt_handler.times_called >= 1

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_1', 'order_id_1')
    check_receipt(
        receipt,
        'park_id_1',
        'order_id_1',
        'push_to_cashbox',
        'driver_id_1',
        'idempotency_key_1',
        250.00,
        None,
        failure_id='kWrongPublicIdOrApiSecret',
        fail_message='Cloud kassir push receipt: unauthorized',
    )


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        """
        INSERT INTO cashbox_integration.receipts(
        park_id, driver_id, order_id, cashbox_id, external_id,
        status, created_at, updated_at, order_price,
        order_end, order_end_point) VALUES
        (
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
            '(10.01234567, 20.01234567)'
        )
        """,
        """
        INSERT INTO cashbox_integration.cashboxes(
        park_id, id, idempotency_token, date_created,
        date_updated, state, is_current, cashbox_type,
        details, secrets)
        VALUES
        (
            'park_id_1',
            'cashbox_id_1',
            'idemp_1',
            '2019-06-22 19:10:25-07',
            '2019-06-22 19:10:25-07',
            'valid',
            'TRUE',
            'cloud_kassir',
            '{
                "tin_pd_id": "0123456789",
                "tax_scheme_type": "simple"
            }',
            '{
                "public_id": "M5a7svvcrnA7E5axBDY2sw==",
                "api_secret": "dCKumeJhRuUkLWmKppFyPQ=="
            }'
        )
        """,
    ],
)
async def test_add_task_with_calculation_place(
        taxi_cashbox_integration,
        cloud_kassir_service,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    credentials = create_credentials('super_park', 'passw0rd')
    inn = '0123456'
    uuid = 'uuid_1'
    cloud_kassir_service.set_data_for_post_receipt(credentials, inn, uuid)

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert cloud_kassir_service.post_receipt_handler.times_called >= 1

    request = cloud_kassir_service.post_receipt_handler.next_call()
    check_request(request, 250.0, '20.0123,10.0123')

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_1', 'order_id_1')
    check_receipt(
        receipt,
        'park_id_1',
        'order_id_1',
        'wait_status',
        'driver_id_1',
        'idempotency_key_1',
        250.00,
        uuid,
        failure_id=None,
    )
