import pytest


@pytest.mark.yt(
    schemas=['yt_setcar_dyn_schema.yaml'],
    dyn_table_data=['yt_setcar_dyn_data.yaml'],
)
@pytest.mark.parametrize(
    'order_id,expected',
    [
        (
            {'order_id': '383e1b2cfeb03093accea972389eb8f4'},
            {'items': [{'driver_id': 1}]},
        ),
        ({'order_id': 'notfound'}, {'items': []}),
    ],
)
async def test_ok(yt_apply, taxi_driver_order_misc, order_id, expected):
    response = await taxi_driver_order_misc.post(
        '/internal/driver-order-misc/v1/fetch-setcar', json=order_id,
    )
    assert response.status_code == 200
    assert response.json() == expected
