import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

TEXT = {
    'name': 'new_segment1',
    'last_modified_at': 439340,
    'removed': False,
    'closed': False,
    'description': 'Описание для "new_experiment"',
    'owners': ['bitsoyeva'],
    'watchers': [],
    'self_ok': False,
    'is_technical': False,
    'enable_debug': False,
    'trait_tags': [],
    'st_tickets': [],
    'biz_revision': 1,
    'match': {
        'enabled': False,
        'schema': (
            'description: "test value"\ntype: object\n'
            'properties:\n  enabled:\n    type: boolean\n'
            'additionalProperties: false\n'
        ),
        'action_time': {
            'from': '2021-03-30T13:29:46+03:00',
            'to': '2021-03-30T13:29:46+03:00',
        },
        'consumers': [{'name': '/launch'}],
        'applications': [{'name': 'iphone', 'version_range': {}}],
        'predicate': {'type': 'true', 'init': {}},
    },
    'default_value': None,
    'clauses': [
        {
            'title': 'Условие modSha1WithSalt',
            'value': {},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'init': {
                    'salt': '5eed9732-dadb-41e6-9c96-32327315ff5f',
                    'divisor': 100,
                    'arg_name': 'phone_id',
                    'range_to': 50,
                    'range_from': 0,
                },
                'type': 'segmentation',
            },
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'nastya_segment',
            'value': {},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'init': {
                    'salt': 'new_experiment',
                    'divisor': 100,
                    'arg_name': 'zone',
                    'range_to': 30,
                    'range_from': 0,
                },
                'type': 'segmentation',
            },
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
    ],
    'department': 'common',
}


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'enable_save_salts': True,
                'enable_write_segmentation_for_new_salts': True,
                'enable_segmentation_for_front': True,
            },
        },
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
@pytest.mark.pgsql(
    'taxi_exp',
    queries=[
        db.ADD_CONSUMER.format('/launch'),
        db.ADD_APPLICATION.format('taximeter'),
        db.ADD_APPLICATION.format('iphone'),
        db.ADD_SALT.format(
            '5eed9732-dadb-41e6-9c96-32327315ff5f', 'mod_sha1_with_salt',
        ),
    ],
)
async def test(taxi_exp_client, taxi_config):
    TEXT['match']['action_time'] = experiment.DEFAULT_ACTION_TIME
    response = await helpers.init_exp(taxi_exp_client, TEXT)
    predicates = [
        clause['predicate']['type'] for clause in response['clauses']
    ]
    assert all(
        predicate == 'mod_sha1_with_salt' for predicate in predicates
    ), predicates
