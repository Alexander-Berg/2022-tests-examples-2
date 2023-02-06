import datetime

from tests_cashbox_integration import utils


def initialize():
    return (
        'park_id_1',
        'order_id_1',
        datetime.datetime.fromisoformat('2019-10-01T10:05:00+03:00'),
    )


def create_expected_receipt(
        status, fail_message=None, url=None, details=None, failure_id=None,
):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    external_id = 'uuid_1'
    created_at = datetime.datetime.fromisoformat('2019-10-01T10:05:00+03:00')
    order_price = 250.00
    task_uuid = 'uuid_1'
    order_end = datetime.datetime.fromisoformat('2019-10-01T10:10:00+03:00')

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


def enable_periodic_task(taxi_config):
    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 1,
            },
        },
    )


async def test_get_not_ready_receipt(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-orange-data/api/v2/documents/0123456/status/uuid_1',
    )
    def od_get_status(request):
        return mockserver.make_response(content_type='text/html', status=202)

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    assert od_get_status.times_called >= 1

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(status='wait_status')

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] == updated_at


async def test_get_ready_receipt(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    details = {
        'id': 'uuid_1',
        'deviceSN': '0000000000001234',
        'deviceRN': '0000000000000456',
        'fsNumber': '0000000000000789',
        'ofdName': 'ООО Тест',
        'ofdWebsite': 'www.ofd-ya.ru',
        'ofdinn': '123456789012',
        'fnsWebsite': 'www.nalog.ru',
        'companyINN': '0123456',
        'companyName': 'TEST',
        'documentNumber': 123,
        'shiftNumber': 77,
        'documentIndex': 7,
        'processedAt': '2019-10-01T10:10:00',
        'change': 10.0,
        'fp': '0123456789',
    }

    @mockserver.json_handler(
        'cashbox-orange-data/api/v2/documents/0123456/status/uuid_1',
    )
    def od_get_status(request):
        return mockserver.make_response(json=details, status=200)

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    assert od_get_status.times_called >= 1

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='complete',
        url='https://cheques-od.taxcom.ru/0123456/uuid_1',
        details=details,
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] != updated_at


async def test_id_not_found(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-orange-data/api/v2/documents/0123456/status/uuid_1',
    )
    def od_get_status(request):
        return mockserver.make_response(
            json={'errors': ['чек с указанным идентификатором не найден']},
            status=400,
        )

    park_id, order_id, updated_at = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    assert od_get_status.times_called >= 1

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    fail_message = (
        'Orange Data bad request: чек с указанным идентификатором не найден'
    )
    expected_receipt = create_expected_receipt(
        status='wait_status',
        fail_message=fail_message,
        failure_id='kUuidNotFound',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] == updated_at
