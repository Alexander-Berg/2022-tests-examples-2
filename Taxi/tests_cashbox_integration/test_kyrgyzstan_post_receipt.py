import datetime

from tests_cashbox_integration import utils


def initialize():
    return ('park_id_1', 'order_id_1')


def enable_periodic_task(taxi_config):
    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )


def create_expected_receipt(status, fail_message, failure_id, url):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    external_id = 'idempotency_key_1'
    order_price = 250.00
    order_end = datetime.datetime.fromisoformat('2019-10-01T10:10:00+03:00')
    task_uuid = None

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
        url=url,
    )


async def test_ok(mockserver, taxi_cashbox_integration, pgsql, taxi_config):
    @mockserver.json_handler('cashbox-kyrgyzstan/cash-register/receipt')
    def kyrgyzstan_post_receipt(request):
        if (
                request.json
                == {
                    'fiscalDocumentId': 'idempotency_key_1',
                    'items': [
                        {
                            'cost': 25000,
                            'price': 25000,
                            'quantity': 1.0,
                            'name': 'Перевозка пассажиров и багажа',
                        },
                    ],
                    'location': 'Машина такси',
                }
                and request.headers['UUID'] == 'super_park'
        ):
            return {'receiptUrl': 'url'}

        return mockserver.make_response(status=400)

    park_id, order_id = initialize()
    enable_periodic_task(taxi_config)
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert kyrgyzstan_post_receipt.times_called == 1

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    print(receipt)

    expected_receipt = create_expected_receipt(
        status='complete', fail_message=None, failure_id=None, url='url',
    )
    utils.compare_receipt(receipt, expected_receipt)
