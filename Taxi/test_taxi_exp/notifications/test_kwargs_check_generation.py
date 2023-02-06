import pytest

from taxi_exp.lib.notifications import lost_kwargs_check
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


CLAUSES = [
    {
        'predicate': {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'arg_name': 'driver_id',
                            'arg_type': 'string',
                            'salt': '0',
                        },
                        'type': 'eq',
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
]


@pytest.mark.parametrize(
    'consumers, clauses, expected',
    [
        pytest.param(
            experiment.make_consumers('launch'),
            CLAUSES,
            {
                'notification_type': 'kwargs_warning',
                'details': [
                    {
                        'consumer': 'launch',
                        'extra_kwargs': ['driver_id'],
                        'consumer_type': 'without_registered_kwargs',
                    },
                ],
            },
            id='error if exp use consumer without kwargs',
        ),
        pytest.param(
            experiment.make_consumers('launch'),
            [],
            None,
            id='no error without args',
        ),
        pytest.param(
            experiment.make_consumers('ignored_consumer'),
            CLAUSES,
            {
                'notification_type': 'kwargs_warning',
                'details': [
                    {
                        'consumer': 'ignored_consumer',
                        'extra_kwargs': ['driver_id'],
                        'consumer_type': 'exp3_matcher',
                    },
                ],
            },
            id='None if consumer for exp3-matcher',
        ),
        pytest.param(
            experiment.make_consumers('launch', 'ignored_consumer'),
            CLAUSES,
            {
                'notification_type': 'kwargs_warning',
                'details': [
                    {
                        'consumer': 'launch',
                        'extra_kwargs': ['driver_id'],
                        'consumer_type': 'without_registered_kwargs',
                    },
                    {
                        'consumer': 'ignored_consumer',
                        'extra_kwargs': ['driver_id'],
                        'consumer_type': 'exp3_matcher',
                    },
                ],
            },
            id='warning if exp has two consumers',
        ),
        pytest.param(
            experiment.make_consumers('launch', 'z-launch'),
            CLAUSES,
            {
                'notification_type': 'kwargs_warning',
                'details': [
                    {
                        'consumer': 'launch',
                        'extra_kwargs': ['driver_id'],
                        'consumer_type': 'without_registered_kwargs',
                    },
                ],
            },
            id='warning if exp has two consumers and partial',
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'backend': {
                'fill_notifications': True,
                'kwargs_check': True,
                'check_exp3_matcher_consumers': True,
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
        db.ADD_CONSUMER.format('z-launch'),
        db.ADD_KWARGS.format(
            consumer='launch', kwargs='[]', metadata='{}', library_version='1',
        ),
        db.ADD_KWARGS.format(
            consumer='z-launch',
            kwargs="""
[{"name":"driver_id", "type":"string"},{"name":"phone_id", "type":"string"}]
""",
            metadata='{}',
            library_version='1',
        ),
    ],
)
async def test(taxi_exp_client, consumers, clauses, expected):
    await taxi_exp_client.app.ctx.kwargs_cache.refresh_cache()

    data = experiment.generate(
        consumers=consumers,
        schema="""type: object
additionalProperties: false""",
        clauses=clauses,
    )

    result = lost_kwargs_check.Checker(taxi_exp_client.app, data).check()
    assert result == expected
