import datetime

import pytz

from tests_cashbox_integration import utils


def initialize():
    return (
        'park_id_1',
        'order_id_1',
        datetime.datetime.now(pytz.timezone('Europe/Moscow')),
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


def create_expected_receipt(
        status,
        fail_message,
        order_end=datetime.datetime.fromisoformat('2019-10-01T10:10:00+03:00'),
        order_price=250.0,
):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    external_id = 'idempotency_key_1'

    return utils.create_receipt(
        park_id=park_id,
        driver_id=driver_id,
        order_id=order_id,
        cashbox_id=cashbox_id,
        external_id=external_id,
        status=status,
        fail_message=fail_message,
        order_end=order_end,
        order_price=order_price,
    )


async def test_receipt_without_price_and_end(
        taxi_cashbox_integration, pgsql, taxi_config,
):
    enable_periodic_task(taxi_config)

    park_id, order_id, updated_at = initialize()

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    expected_receipt = create_expected_receipt(
        status='invalid',
        fail_message='null date_end or client_price',
        order_end=None,
        order_price=None,
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] >= updated_at
