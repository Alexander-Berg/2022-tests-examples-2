import pytest

from . import utils


@pytest.mark.pgsql(
    'driver_promocodes', files=['series.sql', 'promocodes_to_activate.sql'],
)
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'request_body,attempts,response_list_after',
    [
        (
            {
                'usages': [
                    {'order_id': 'order1', 'promocode_id': 'promocode_ok'},
                    {
                        'order_id': 'order1',
                        'promocode_id': 'promocode_activated',
                    },
                    {
                        'order_id': 'order2',
                        'promocode_id': 'promocode_activated',
                    },
                ],
            },
            3,
            'response_list_after.json',
        ),
    ],
)
async def test_add_order_usage(
        taxi_driver_promocodes,
        pgsql,
        load_json,
        request_body,
        attempts,
        response_list_after,
):

    for _ in range(attempts):
        response = await taxi_driver_promocodes.post(
            'internal/v1/promocodes/add-order-usage', json=request_body,
        )
        assert response.status_code == 200

    response = await taxi_driver_promocodes.get(
        'admin/v1/promocodes/list', params={'entity_id': 'park_0_driver_0'},
    )
    assert utils.remove_not_testable_promocodes(
        response.json(),
    ) == utils.remove_not_testable_promocodes(load_json(response_list_after))

    cursor = pgsql['driver_promocodes'].cursor()
    cursor.execute(
        f"""SELECT used_for_orders FROM
        promocodes.promocodes
        WHERE id = '{request_body['usages'][0]['promocode_id']}'""",
    )
    used_for_orders = list(row for row in cursor)[0][0]
    cursor.close()
    assert len(used_for_orders) == 1
