import uuid

import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT = 'advert_on_map'
FILES_METADATA = {
    'first': {
        'experiment_name': EXPERIMENT,
        'file_type': 'string',
        'mds_id': uuid.uuid4().hex,
        'file_size': 100,
    },
    'second': {
        'experiment_name': EXPERIMENT,
        'file_type': 'string',
        'mds_id': uuid.uuid4().hex,
        'file_size': 100,
    },
    'third': {
        'experiment_name': EXPERIMENT,
        'file_type': 'string',
        'mds_id': uuid.uuid4().hex,
        'file_size': 100,
    },
}


@pytest.fixture
async def _add_files_metadata(taxi_exp_client):
    for name, metadata in FILES_METADATA.items():
        await db.add_or_update_file(taxi_exp_client.app, name, **metadata)


@pytest.mark.parametrize(
    'files,expected_answer',
    [
        (
            ['first', 'second'],
            {
                'change_doc_id': 'experiment_advert_on_map',
                'data': {
                    'department': 'common',
                    'experiment': {
                        'name': 'advert_on_map',
                        'description': 'Description for advert_on_map',
                        'match': {
                            'enabled': True,
                            'schema': (
                                '\ndescription: \'default schema'
                                '\'\nadditionalProperties: true\n    '
                            ),
                            'action_time': {
                                'from': experiment.FROM_TIME,
                                'to': experiment.TO_TIME,
                            },
                            'consumers': [{'name': 'test_consumer'}],
                            'predicate': {'type': 'true'},
                        },
                        'closed': False,
                        'clauses': [
                            {
                                'title': 'first',
                                'value': {},
                                'predicate': {
                                    'type': 'in_file',
                                    'init': {
                                        'file': FILES_METADATA['first'][
                                            'mds_id'
                                        ],
                                        'arg_name': 'phone_id',
                                        'set_elem_type': 'string',
                                    },
                                },
                            },
                            {
                                'title': 'second',
                                'value': {},
                                'predicate': {
                                    'type': 'in_file',
                                    'init': {
                                        'file': FILES_METADATA['second'][
                                            'mds_id'
                                        ],
                                        'arg_name': 'phone_id',
                                        'set_elem_type': 'string',
                                    },
                                },
                            },
                        ],
                        'default_value': None,
                        'department': 'common',
                        'self_ok': False,
                        'financial': True,
                        'enable_debug': False,
                        'shutdown_mode': 'instant_shutdown',
                        'trait_tags': [],
                        'st_tickets': [],
                    },
                },
            },
        ),
        (
            ['first', 'second', 'third'],
            {
                'code': 'DRAFT_CHECKING_ERROR_FOR_FILES',
                'message': 'total files size is too big: 300 > 200',
            },
        ),
        pytest.param(
            ['first', 'second', 'third'],
            {
                'change_doc_id': 'experiment_advert_on_map',
                'data': {
                    'department': 'common',
                    'experiment': {
                        'name': 'advert_on_map',
                        'description': 'Description for advert_on_map',
                        'match': {
                            'enabled': True,
                            'schema': (
                                '\ndescription: \'default schema'
                                '\'\nadditionalProperties: true\n    '
                            ),
                            'action_time': {
                                'from': experiment.FROM_TIME,
                                'to': experiment.TO_TIME,
                            },
                            'consumers': [{'name': 'test_consumer'}],
                            'predicate': {'type': 'true'},
                        },
                        'closed': False,
                        'clauses': [
                            {
                                'title': 'first',
                                'value': {},
                                'predicate': {
                                    'type': 'in_file',
                                    'init': {
                                        'file': FILES_METADATA['first'][
                                            'mds_id'
                                        ],
                                        'arg_name': 'phone_id',
                                        'set_elem_type': 'string',
                                    },
                                },
                            },
                            {
                                'title': 'second',
                                'value': {},
                                'predicate': {
                                    'type': 'in_file',
                                    'init': {
                                        'file': FILES_METADATA['second'][
                                            'mds_id'
                                        ],
                                        'arg_name': 'phone_id',
                                        'set_elem_type': 'string',
                                    },
                                },
                            },
                            {
                                'title': 'third',
                                'value': {},
                                'predicate': {
                                    'type': 'in_file',
                                    'init': {
                                        'file': FILES_METADATA['third'][
                                            'mds_id'
                                        ],
                                        'arg_name': 'phone_id',
                                        'set_elem_type': 'string',
                                    },
                                },
                            },
                        ],
                        'default_value': None,
                        'department': 'common',
                        'self_ok': False,
                        'financial': True,
                        'enable_debug': False,
                        'shutdown_mode': 'instant_shutdown',
                        'trait_tags': [],
                        'st_tickets': [],
                    },
                },
            },
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={'settings': {'backend': {}}},
            ),
            id='if_config_disabled',
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {'backend': {'files_size_by_experiment': 200}},
    },
    EXP_EXTENDED_DRAFTS=[
        {'DRAFT_NAME': '__default__', 'NEED_CHECKING_FILES': True},
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.usefixtures('_add_files_metadata')
async def test_file_restrictions(taxi_exp_client, files, expected_answer):
    body = experiment.generate(
        EXPERIMENT,
        clauses=[
            experiment.make_clause(
                file,
                experiment.infile_predicate(FILES_METADATA[file]['mds_id']),
            )
            for file in files
        ],
        department='common',
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT},
        json=body,
    )
    response_body = await response.json()
    assert response_body == expected_answer, response.status
