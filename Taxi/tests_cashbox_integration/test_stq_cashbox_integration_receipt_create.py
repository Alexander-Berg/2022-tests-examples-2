import pytest

from tests_cashbox_integration import utils


def check_receipt(
        receipt,
        park_id,
        order_id,
        status,
        driver_id,
        cashbox_id,
        order_end_point=None,
):
    assert receipt['park_id'] == park_id
    assert receipt['order_id'] == order_id
    assert receipt['status'] == status
    assert receipt['driver_id'] == driver_id
    assert receipt['cashbox_id'] == cashbox_id
    assert receipt['order_end_point'] == order_end_point


async def test_create_receipt(driver_orders, pgsql, stq_runner, geotracks):
    park_id = 'park_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    driver_id = 'driver_id_1'

    await stq_runner.cashbox_integration_receipt_create.call(
        task_id='order1',
        kwargs={
            'order_id': order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
        },
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt, park_id, order_id, 'need_order_info', driver_id, cashbox_id,
    )


TEST_BAD_PARAMS = [
    ('park_id_1', 'order_???'),  # no order
    ('park_id_1', 'order_id_4'),  # not cash
    ('park_id_3', 'order_id_1'),  # no active cshbox
]


@pytest.mark.parametrize('park_id, order_id', TEST_BAD_PARAMS)
async def test_bad_request(
        pgsql,
        taxi_cashbox_integration,
        geotracks,
        driver_orders,
        park_id,
        order_id,
        stq_runner,
):
    await stq_runner.cashbox_integration_receipt_create.call(
        task_id='order1',
        kwargs={
            'order_id': order_id,
            'driver_uuid': 'driver_id_1',
            'park_id': park_id,
        },
    )

    cursor = pgsql['cashbox_integration'].cursor()
    cursor.execute(
        'SELECT * FROM cashbox_integration.receipts WHERE '
        'park_id=\'{}\' AND order_id=\'{}\''.format(park_id, order_id),
    )
    rows = utils.pg_response_to_dict(cursor)
    assert not rows


async def test_no_autocreation(pgsql, stq_runner, fleet_parks):
    park_id = 'park_id_1'
    order_id = 'order_id_1'
    driver_id = 'driver_id_2'

    await stq_runner.cashbox_integration_receipt_create.call(
        task_id='order1',
        kwargs={
            'order_id': order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
        },
    )

    cursor = pgsql['cashbox_integration'].cursor()
    cursor.execute(
        'SELECT * FROM cashbox_integration.receipts WHERE '
        'park_id=\'{}\' AND order_id=\'{}\''.format(park_id, order_id),
    )
    rows = utils.pg_response_to_dict(cursor)
    assert not rows


@pytest.mark.experiments3(filename='exp3_config.json')
async def test_autocreation_by_park_id(
        pgsql, stq_runner, fleet_parks, driver_orders, geotracks,
):
    park_id = 'park_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    driver_id = 'driver_id_2'

    await stq_runner.cashbox_integration_receipt_create.call(
        task_id='order1',
        kwargs={
            'order_id': order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
        },
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt, park_id, order_id, 'need_order_info', driver_id, cashbox_id,
    )
