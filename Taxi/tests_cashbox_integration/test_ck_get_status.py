import base64

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
        order_end_point,
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
    assert receipt['order_end_point'] == order_end_point
    assert receipt['fail_message'] == fail_message
    assert receipt['failure_id'] == failure_id


def check_receipt_detail(
        receipt_detail, uuid, amount, date_time, ofd, ofd_receipt_url,
):
    assert receipt_detail['Id'] == uuid
    assert receipt_detail['Amount'] == amount
    assert receipt_detail['DateTime'] == date_time
    assert receipt_detail['Ofd'] == ofd
    assert receipt_detail['OfdReceiptUrl'] == ofd_receipt_url


def check_request(request, uuid):
    assert uuid == request['request'].json['Id']


def create_credentials(public_id, api_secret):
    credentials = f'{public_id}:{api_secret}'
    encoded_credentials = base64.b64encode(credentials.encode())
    string_credentials = encoded_credentials.decode('utf-8')
    return f'Basic {string_credentials}'


async def test_get_not_ready_receipt(
        taxi_cashbox_integration,
        cloud_kassir_service,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    credentials = create_credentials('super_park', 'passw0rd')
    uuid = 'uuid_1'
    is_ready = False
    cloud_kassir_service.set_data_for_get_receipt(credentials, uuid, is_ready)

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    assert cloud_kassir_service.receipt_status_handler.times_called >= 1
    assert cloud_kassir_service.get_receipt_handler.times_called == 0

    request = cloud_kassir_service.receipt_status_handler.next_call()
    check_request(request, uuid)

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
        '(10.01,20.01)',
        failure_id=None,
    )


async def test_get_ready_receipt(
        taxi_cashbox_integration,
        cloud_kassir_service,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    credentials = create_credentials('super_park', 'passw0rd')
    uuid = 'uuid_1'
    is_ready = True
    cloud_kassir_service.set_data_for_get_receipt(credentials, uuid, is_ready)

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 1,
            },
        },
    )
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    assert cloud_kassir_service.receipt_status_handler.times_called >= 1
    assert cloud_kassir_service.get_receipt_handler.times_called >= 1

    request = cloud_kassir_service.receipt_status_handler.next_call()
    check_request(request, uuid)

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_1', 'order_id_1')
    check_receipt(
        receipt,
        'park_id_1',
        'order_id_1',
        'complete',
        'driver_id_1',
        'idempotency_key_1',
        250.00,
        uuid,
        '(10.01,20.01)',
        failure_id=None,
    )
    check_receipt_detail(
        receipt['details'],
        'uuid_1',
        250.00,
        '2019-10-01T10:11:00',
        'OOO Тест',
        'https://demo.ofd.ru/rec/123',
    )


async def test_id_not_found(
        taxi_cashbox_integration,
        cloud_kassir_service,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    credentials = create_credentials('super_park', 'passw0rd')
    is_ready = True
    cloud_kassir_service.set_data_for_get_receipt(
        credentials, 'wrong_uuid', is_ready,
    )

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    assert cloud_kassir_service.receipt_status_handler.times_called >= 1

    uuid = 'uuid_1'
    request = cloud_kassir_service.receipt_status_handler.next_call()
    check_request(request, uuid)

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_1', 'order_id_1')
    check_receipt(
        receipt,
        'park_id_1',
        'order_id_1',
        'fail',
        'driver_id_1',
        'idempotency_key_1',
        250.00,
        uuid,
        '(10.01,20.01)',
        failure_id='kUuidNotFound',
        fail_message='receipt not found',
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
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    assert cloud_kassir_service.receipt_status_handler.times_called >= 1

    uuid = 'uuid_1'
    request = cloud_kassir_service.receipt_status_handler.next_call()
    check_request(request, uuid)

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
        '(10.01,20.01)',
        failure_id='kWrongPublicIdOrApiSecret',
        fail_message='Cloud kassir get receipt status: unauthorized',
    )
