import json

import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import filters


@pytest.mark.parametrize(
    'scenario,expected_history',
    (
        (
            [
                (
                    {
                        'consumer': 'test_consumer',
                        'kwargs': [],
                        'metadata': {
                            'supported_features': ['geozone_matching'],
                        },
                    },
                    200,
                ),
            ],
            [
                {
                    'consumer': 'test_consumer',
                    'history': {
                        'kwargs': [],
                        'library_version': None,
                        'metadata': {
                            'supported_features': ['geozone_matching'],
                        },
                    },
                },
            ],
        ),
        pytest.param(
            [
                (
                    {
                        'consumer': 'test_consumer',
                        'metadata': {
                            'supported_features': ['geozone_matching'],
                        },
                    },
                    200,
                ),
            ],
            [
                {
                    'consumer': 'test_consumer',
                    'history': {
                        'kwargs': [],
                        'library_version': None,
                        'metadata': {
                            'supported_features': ['geozone_matching'],
                        },
                    },
                },
            ],
            id='without_kwargs',
        ),
        pytest.param(
            [
                (
                    {
                        'consumer': 'test_consumer',
                        'kwargs': [
                            {
                                'name': 'phone_id',
                                'type': 'string',
                                'is_mandatory': True,
                            },
                            {
                                'name': 'zone_id',
                                'type': 'string',
                                'is_mandatory': False,
                            },
                            {'name': 'login', 'type': 'string'},
                        ],
                    },
                    200,
                ),
            ],
            [
                {
                    'consumer': 'test_consumer',
                    'history': {
                        'kwargs': [
                            {
                                'name': 'phone_id',
                                'type': 'string',
                                'is_mandatory': True,
                            },
                            {
                                'name': 'zone_id',
                                'type': 'string',
                                'is_mandatory': False,
                            },
                            {'name': 'login', 'type': 'string'},
                        ],
                        'library_version': None,
                        'metadata': {},
                    },
                },
            ],
        ),
        pytest.param(
            [
                (
                    {
                        'consumer': 'market_consumer',
                        'namespace': 'market',
                        'kwargs': [
                            {
                                'name': 'phone_id',
                                'type': 'string',
                                'is_mandatory': True,
                            },
                            {
                                'name': 'zone_id',
                                'type': 'string',
                                'is_mandatory': False,
                            },
                            {'name': 'login', 'type': 'string'},
                        ],
                    },
                    200,
                ),
            ],
            [
                {
                    'consumer': 'market_consumer',
                    'history': {
                        'kwargs': [
                            {
                                'name': 'phone_id',
                                'type': 'string',
                                'is_mandatory': True,
                            },
                            {
                                'name': 'zone_id',
                                'type': 'string',
                                'is_mandatory': False,
                            },
                            {'name': 'login', 'type': 'string'},
                        ],
                        'library_version': None,
                        'metadata': {},
                    },
                },
            ],
            id='create_consumer_with_kwargs_and_namespace',
        ),
        pytest.param(
            [
                ({'consumer': 'test_consumer', 'kwargs': []}, 200),
                (
                    {
                        'consumer': 'test_consumer',
                        'kwargs': [{'name': 'zone', 'type': 'string'}],
                    },
                    200,
                ),
            ],
            [
                {
                    'consumer': 'test_consumer',
                    'history': {
                        'kwargs': [],
                        'library_version': None,
                        'metadata': {},
                    },
                },
                {
                    'consumer': 'test_consumer',
                    'history': {
                        'kwargs': [{'name': 'zone', 'type': 'string'}],
                        'library_version': None,
                        'metadata': {},
                    },
                },
            ],
        ),
        pytest.param(
            [
                ({'consumer': 'unknown_consumer', 'kwargs': []}, 200),
                ({'consumer': 'bad+unknown+consumer', 'kwargs': []}, 400),
            ],
            [
                {
                    'consumer': 'unknown_consumer',
                    'history': {
                        'kwargs': [],
                        'library_version': None,
                        'metadata': {},
                    },
                },
            ],
        ),
        pytest.param(
            [
                ({'consumer': 'test_consumer', 'kwargs': {}}, 400),
                (
                    {'consumer': 'test_consumer', 'kwargs': [{'name': '1'}]},
                    400,
                ),
                ({'consumer': 'test_consumer', 'kwargs': [{'name': 1}]}, 400),
                ({'consumer': 'test_consumer', 'kwargs': [{}]}, 400),
                (
                    {
                        'consumer': 'test_consumer',
                        'kwargs': [],
                        'metadata': False,
                    },
                    400,
                ),
            ],
            [],
        ),
    ),
)
@pytest.mark.now('2019-01-09T12:00:00')
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_adding_kwargs(scenario, expected_history, taxi_exp_client):
    for index, case in enumerate(scenario):
        data, code = case
        response = await taxi_exp_client.post(
            '/v1/consumers/kwargs/',
            headers={'X-Ya-Service-Ticket': '123'},
            json=data,
        )
        assert response.status == code, f'Fail step: {index+1}'
        if code == 200:
            namespace = (
                data['namespace']
                if 'namespace' in data
                else filters.DEFAULT_NAMESPACE
            )
            consumer_data = [
                item
                for item in await filters.get_consumers(
                    taxi_exp_client, namespace=namespace,
                )
                if item['name'] == data['consumer']
            ]
            assert consumer_data

    current_history = await db.get_kwargs_history(taxi_exp_client.app)
    assert len(current_history) == len(expected_history)

    for current, expected in zip(current_history, expected_history):
        assert current['consumer'] == expected['consumer']
        assert 'updation_time' in current

        history = json.loads(current['history'])
        assert 'updated' in history

        ehistory = expected['history']
        assert history['kwargs'] == ehistory['kwargs']
        assert history['metadata'] == ehistory['metadata']
        assert history['library_version'] == ehistory['library_version']
