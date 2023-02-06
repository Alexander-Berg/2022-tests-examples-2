import pytest

from taxi.clients import taxi_exp as taxi_exp_outer_client

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'map_style'


@pytest.fixture
async def mock_service(taxi_exp_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    async def _mock_taxi_exp(request):
        response = None
        if request.method == 'GET':
            response = await taxi_exp_client.get(
                '/v1/experiments/',
                headers=request.headers,
                params=request.args,
            )
        elif request.method == 'POST':
            response = await taxi_exp_client.post(
                '/v1/experiments/',
                headers=request.headers,
                params=request.args,
                json=request.json,
            )
        if response is None:
            raise Exception('?????')
        return await response.json()


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={'features': {'backend': {'fill_notifications': True}}},
    TAXI_EXP_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'request_timeout_ms': 500,
                'num_retries': 0,
                'retry_delay_ms': [50],
            },
        },
    },
)
@pytest.mark.usefixtures('mock_service')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_experiments(taxi_exp_client):
    data = experiment.generate(
        schema="""type: object
additionalProperties: false""",
        clauses=[
            {
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'driver_id',
                                    'divisor': 100,
                                    'range_from': 0,
                                    'range_to': 100,
                                    'salt': '0',
                                },
                                'type': 'mod_sha1_with_salt',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'title': 'first',
                'value': {},
            },
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'second',
                'value': {},
            },
        ],
    )

    client = taxi_exp_outer_client.TaxiExpClient(
        session=taxi_exp_client.app.session,
        config=taxi_exp_client.app.config,
        service_name='taxi_exp',
        tvm_client=taxi_exp_client.app.tvm,
    )

    response = await client.create_exp(name=NAME, data=data)
    assert response == {}

    response = await client.get_exp(name=NAME, include_meta=False)
    assert 'notifications' not in response, response['notifications']

    response = await client.get_exp(name=NAME, include_meta=True)
    assert response['notifications'] == [
        {
            'notification_type': 'segmentation_info',
            'details': {
                'key_sets': [
                    {
                        'segments': [
                            {
                                'range_from': 0.0,
                                'range_to': 100.0,
                                'title': 'first',
                            },
                        ],
                        'keyset': {'arg_names': ['driver_id'], 'salt': '0'},
                    },
                ],
            },
        },
    ]
