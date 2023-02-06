import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'map_style'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'backend': {
                'check_exp3_matcher_consumers': True,
                'fill_notifications': True,
                'kwargs_check': True,
            },
        },
    },
    EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=['ignored_consumer'],
)
@pytest.mark.pgsql(
    'taxi_exp',
    queries=[
        db.ADD_CONSUMER.format('ignored_consumer'),
        db.ADD_CONSUMER.format('launch'),
        db.ADD_KWARGS.format(
            consumer='launch', kwargs='[]', metadata='{}', library_version='1',
        ),
    ],
)
async def test_experiments(taxi_exp_client):
    await taxi_exp_client.app.ctx.kwargs_cache.refresh_cache()
    data = experiment.generate(
        consumers=[{'name': 'ignored_consumer'}, {'name': 'launch'}],
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

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=data,
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'include_meta': 'true'},
    )
    assert response.status == 200, await response.text()
    get_body = await response.json()

    assert get_body['notifications'] == [
        {
            'notification_type': 'segmentation_info',
            'details': {
                'key_sets': [
                    {
                        'keyset': {'arg_names': ['driver_id'], 'salt': '0'},
                        'segments': [
                            {
                                'range_from': 0.0,
                                'range_to': 100.0,
                                'title': 'first',
                            },
                        ],
                    },
                ],
            },
        },
        {
            'notification_type': 'kwargs_warning',
            'details': [
                {
                    'consumer': 'ignored_consumer',
                    'extra_kwargs': ['driver_id'],
                    'consumer_type': 'exp3_matcher',
                },
                {
                    'consumer': 'launch',
                    'extra_kwargs': ['driver_id'],
                    'consumer_type': 'without_registered_kwargs',
                },
            ],
        },
    ]
