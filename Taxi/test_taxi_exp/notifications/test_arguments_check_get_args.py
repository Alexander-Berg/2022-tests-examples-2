# pylint: disable=protected-access
import pytest

from taxi_exp.lib.notifications import arguments_types_check
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'backend': {
                'fill_notifications': True,
                'kwargs_type_check': True,
                'check_exp3_matcher_consumers': True,
            },
        },
    },
    EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=['ignored_consumer'],
)
@pytest.mark.pgsql(
    'taxi_exp',
    queries=[
        db.ADD_CONSUMER.format('launch'),
        db.ADD_KWARGS.format(
            consumer='launch',
            kwargs="""[
                {"name":"uuid", "type":"string"},
                {"name":"zone", "type":"string"}
            ]""",
            metadata='{}',
            library_version='1',
        ),
    ],
)
async def test(taxi_exp_client):
    await taxi_exp_client.app.ctx.kwargs_cache.refresh_cache()

    exp_body = experiment.generate(
        consumers=experiment.make_consumers('launch'),
        match_predicate={'type': 'true'},
        clauses=[
            {
                'title': 'Бизнес: показывать главную',
                'value': {'start_screen': 'main'},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'set': [
                                        '06a45410433edc2094c42bff9c69e803',
                                    ],
                                    'arg_name': 'uuid',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'salt': 'salt_123',
                                    'divisor': 100,
                                    'arg_name': 'uuid',
                                    'range_to': 50,
                                    'range_from': 0,
                                },
                                'type': 'mod_sha1_with_salt',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
            {
                'title': 'Бизнес: показывать саммари',
                'value': {'start_screen': 'summary'},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'set': [
                                        '06a45410433edc2094c42bff9c69e803',
                                    ],
                                    'arg_name': 'uuid',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'salt': 'salt_123',
                                    'divisor': 100,
                                    'arg_name': 'uuid',
                                    'range_to': 100,
                                    'range_from': 50,
                                },
                                'type': 'mod_sha1_with_salt',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
            {
                'title': 'Плохие карты: показывать главную',
                'value': {'start_screen': 'main'},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'set': ['msk'],
                                    'arg_name': 'zone',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'salt': 'salt_123',
                                    'divisor': 100,
                                    'arg_name': 'uuid',
                                    'range_to': 50,
                                    'range_from': 0,
                                },
                                'type': 'mod_sha1_with_salt',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
            {
                'title': 'Плохие карты: показывать саммари',
                'value': {'start_screen': 'summary'},
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'set': ['msk'],
                                    'arg_name': 'zone',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'salt': 'salt_123',
                                    'divisor': 100,
                                    'arg_name': 'uuid',
                                    'range_to': 100,
                                    'range_from': 50,
                                },
                                'type': 'mod_sha1_with_salt',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
            {
                'title': 'default',
                'value': {'testing': 'test'},
                'predicate': {'type': 'true'},
            },
        ],
    )

    checker = arguments_types_check.Checker(
        context=taxi_exp_client.app, experiment=exp_body,
    )
    kwargs = checker._get_kwargs()
    assert kwargs == {
        'uuid': {'name': 'uuid', 'type': 'string'},
        'zone': {'name': 'zone', 'type': 'string'},
    }
    assert checker._get_args(kwargs) == [
        arguments_types_check.Item(
            predicate_type='in_set',
            arg_name='uuid',
            arg_type='string',
            clause_number=0,
        ),
        arguments_types_check.Item(
            predicate_type='mod_sha1_with_salt',
            arg_name='uuid',
            arg_type=None,
            clause_number=0,
        ),
        arguments_types_check.Item(
            predicate_type='in_set',
            arg_name='uuid',
            arg_type='string',
            clause_number=1,
        ),
        arguments_types_check.Item(
            predicate_type='mod_sha1_with_salt',
            arg_name='uuid',
            arg_type=None,
            clause_number=1,
        ),
        arguments_types_check.Item(
            predicate_type='in_set',
            arg_name='zone',
            arg_type='string',
            clause_number=2,
        ),
        arguments_types_check.Item(
            predicate_type='mod_sha1_with_salt',
            arg_name='uuid',
            arg_type=None,
            clause_number=2,
        ),
        arguments_types_check.Item(
            predicate_type='in_set',
            arg_name='zone',
            arg_type='string',
            clause_number=3,
        ),
        arguments_types_check.Item(
            predicate_type='mod_sha1_with_salt',
            arg_name='uuid',
            arg_type=None,
            clause_number=3,
        ),
    ]

    assert (
        checker._arguments_type_suitable_for_predicate(
            checker._get_args(kwargs), checker._get_kwargs(),
        )
        == []
    )
    assert (
        checker._check_arguments_type_is_usable_to_predicate(
            checker._get_args(kwargs), checker._get_kwargs(),
        )
        == []
    )
