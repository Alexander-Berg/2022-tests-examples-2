import pytest

from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'check_map_style'


@pytest.mark.parametrize(
    'status, expected',
    [
        pytest.param(
            409,
            {
                'code': 'DRAFT_CHECKING_ERROR_FOR_APPS',
                'message': (
                    'check_map_style need non-existed applications: '
                    '[\'unknown-app\']'
                ),
            },
            marks=pytest.mark.config(
                EXP_EXTENDED_DRAFTS=[
                    {
                        'DRAFT_NAME': '__default__',
                        'NEED_CHECKING_FILES': True,
                        'NEED_CHECKING_BODY': True,
                        'NEED_CHECKING_APPS': True,
                    },
                ],
            ),
        ),
        pytest.param(
            200,
            {
                'change_doc_id': f'update_experiment_{EXPERIMENT_NAME}',
                'data': {
                    'experiment': {
                        'name': 'check_map_style',
                        'trait_tags': [],
                        'st_tickets': [],
                        'description': 'Description for check_map_style',
                        'department': 'common',
                        'financial': True,
                        'match': {
                            'enabled': True,
                            'schema': (
                                '\ndescription: \'default schema\''
                                '\nadditionalProperties: true\n    '
                            ),
                            'action_time': {
                                'from': '2000-01-01T00:00:00+03:00',
                                'to': '2022-12-31T23:59:59+03:00',
                            },
                            'consumers': [{'name': 'test_consumer'}],
                            'applications': [
                                {
                                    'name': 'unknown-app',
                                    'version_range': {
                                        'from': '0.0.0',
                                        'to': '99.99.99',
                                    },
                                },
                            ],
                            'predicate': {'type': 'true'},
                        },
                        'closed': False,
                        'clauses': [
                            {
                                'title': 'default',
                                'predicate': {'type': 'true'},
                                'value': {},
                            },
                        ],
                        'self_ok': False,
                        'shutdown_mode': 'manual_shutdown_only',
                        'enable_debug': False,
                    },
                    'hash': (
                        '48461730910f474b756959f69ebe5636'
                        '3c883a5504dea51bd9ffb203b3cc8a57'
                    ),
                    'status_biz_revision': 'no_change',
                    'self_ok': False,
                },
                'diff': {
                    'current': {
                        'name': 'check_map_style',
                        'trait_tags': [],
                        'st_tickets': [],
                        'closed': False,
                        'removed': False,
                        'self_ok': False,
                        'shutdown_mode': 'instant_shutdown',
                        'enable_debug': False,
                        'financial': True,
                        'clauses': [],
                        'last_modified_at': 1,
                        'biz_revision': 1,
                        'description': 'DESCRIPTION',
                        'owners': [],
                        'watchers': [],
                        'match': {
                            'action_time': {
                                'from': '2020-05-13T04:06:47+03:00',
                                'to': '2020-05-13T04:06:47+03:00',
                            },
                            'consumers': [],
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'schema': '',
                        },
                    },
                    'new': {
                        'name': 'check_map_style',
                        'trait_tags': [],
                        'st_tickets': [],
                        'closed': False,
                        'self_ok': False,
                        'financial': True,
                        'shutdown_mode': 'manual_shutdown_only',
                        'enable_debug': False,
                        'department': 'common',
                        'owners': [],
                        'watchers': [],
                        'clauses': [
                            {
                                'title': 'default',
                                'predicate': {'type': 'true'},
                                'value': {},
                            },
                        ],
                        'description': 'Description for check_map_style',
                        'match': {
                            'applications': [
                                {
                                    'name': 'unknown-app',
                                    'version_range': {
                                        'from': '0.0.0',
                                        'to': '99.99.99',
                                    },
                                },
                            ],
                            'action_time': {
                                'from': '2000-01-01T00:00:00+03:00',
                                'to': '2022-12-31T23:59:59+03:00',
                            },
                            'consumers': [{'name': 'test_consumer'}],
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'schema': (
                                '\ndescription: \'default schema\'\n'
                                'additionalProperties: true\n    '
                            ),
                        },
                    },
                },
            },
            marks=pytest.mark.config(
                EXP_EXTENDED_DRAFTS=[
                    {
                        'DRAFT_NAME': '__default__',
                        'NEED_CHECKING_FILES': True,
                        'NEED_CHECKING_BODY': True,
                        'NEED_CHECKING_APPS': False,
                    },
                ],
            ),
        ),
    ],
)
@pytest.mark.pgsql(
    'taxi_exp', files=('default.sql', 'experiment_for_apps.sql'),
)
async def test_need_checking_apps(status, expected, taxi_exp_client):
    experiment_body = experiment.generate(
        EXPERIMENT_NAME,
        applications=[
            {
                'name': 'unknown-app',
                'version_range': {'from': '0.0.0', 'to': '99.99.99'},
            },
        ],
        action_time={
            'from': '2000-01-01T00:00:00+03:00',
            'to': '2022-12-31T23:59:59+03:00',
        },
        shutdown_mode='manual_shutdown_only',
    )

    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=experiment_body,
    )
    assert response.status == status
    body = await response.json()
    assert body == expected
