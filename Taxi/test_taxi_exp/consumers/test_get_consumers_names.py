import pytest

from test_taxi_exp.helpers import db


@pytest.mark.parametrize(
    'params, expected_answer',
    [
        (
            {},
            {
                'consumers': [
                    {'name': 'a_test_consumer'},
                    {'name': 'test_consumer'},
                    {'name': 'z_test_consumer'},
                ],
            },
        ),
        (
            {'limit': 1, 'offset': 1},
            {'consumers': [{'name': 'test_consumer'}]},
        ),
    ],
)
@pytest.mark.pgsql(
    'taxi_exp',
    queries=[
        db.ADD_CONSUMER.format('test_consumer'),
        db.ADD_CONSUMER.format('z_test_consumer'),
        db.ADD_CONSUMER.format('a_test_consumer'),
    ],
)
async def test_consumer_names(taxi_exp_client, params, expected_answer):
    response = await taxi_exp_client.get(
        '/v1/experiments/filters/consumers/names/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    body = await response.json()
    assert body == expected_answer
