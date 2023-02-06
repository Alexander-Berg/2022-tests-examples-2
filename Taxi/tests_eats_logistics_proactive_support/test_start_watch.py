import pytest

import tests_eats_logistics_proactive_support.common as common


async def test_200(taxi_eats_logistics_proactive_support, pgsql):
    pg_result = common.select_deliveries(pgsql)
    assert pg_result == []
    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/start-watch', json=common.DEFAULT_DELIVERY,
    )

    assert response.status_code == 200

    pg_result = common.select_deliveries(pgsql)
    assert len(pg_result) == 1


@pytest.mark.parametrize(
    'test_data',
    [
        common.modify_delivery(
            {'delivery_id': '00000000000000000000000000000000001'},
        ),
    ],
)
async def test_500(taxi_eats_logistics_proactive_support, test_data):

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/start-watch', json=test_data,
    )

    assert response.status_code == 500


async def test_409(taxi_eats_logistics_proactive_support):

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/start-watch', json=common.DEFAULT_DELIVERY,
    )

    assert response.status_code == 200

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/start-watch', json=common.DEFAULT_DELIVERY,
    )

    assert response.status_code == 409


@pytest.mark.pgsql(
    'eats_logistics_proactive_support', files=['fill_deliveries.sql'],
)
async def test_non_empty(taxi_eats_logistics_proactive_support, pgsql):
    pg_result = common.select_deliveries(pgsql)
    assert pg_result == common.DELIVERIES_DATA
    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/start-watch', json=common.DEFAULT_DELIVERY,
    )

    assert response.status_code == 200

    pg_result = common.select_deliveries(pgsql)
    assert len(pg_result) == len(common.DELIVERIES_DATA) + 1
    expected_result = [common.RAW_DELIVERY] + common.DELIVERIES_DATA
    assert sorted(expected_result, key=lambda tup: tup[0]) == sorted(
        pg_result, key=lambda tup: tup[0],
    )
