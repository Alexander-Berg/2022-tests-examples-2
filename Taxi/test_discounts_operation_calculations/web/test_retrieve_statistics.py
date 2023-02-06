import pytest

CONTROL_SHARE = 10
TEST_SHARE = (100 - CONTROL_SHARE) / 100


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_segment_stats.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
async def test_retrieve_statistics(web_app_client):
    response = await web_app_client.post(
        '/v1/statistics',
        json=[
            {
                'discounts_city': 'test_city',
                'algorithm_id': 'kt',
                'fixed_discounts': [
                    {'segment': 'control', 'discount_value': 0},
                ],
            },
        ],
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['charts']) == 3
    assert content['charts'][0]['plot']['data'][:10] == [
        [pytest.approx(678100.9147137001), pytest.approx(286.2135)],
        [pytest.approx(858759.7709637), pytest.approx(351.78975)],
        [pytest.approx(1648840.6532448), pytest.approx(638.00325)],
        [pytest.approx(1854707.7219948), pytest.approx(703.5794999999999)],
        [pytest.approx(2756768.5718433), pytest.approx(989.7929999999999)],
        [pytest.approx(2987843.8530933), pytest.approx(1055.36925)],
        [pytest.approx(4001884.6705091996), pytest.approx(1341.58275)],
        [pytest.approx(7306700.13018675), pytest.approx(2254.65525)],
        [pytest.approx(7562983.62393675), pytest.approx(2320.2315)],
        [pytest.approx(8689004.408920052), pytest.approx(2606.4449999999997)],
    ]
