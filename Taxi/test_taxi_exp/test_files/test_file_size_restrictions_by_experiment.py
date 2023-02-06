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
        (['first', 'second'], {}),
        (
            ['first', 'second', 'third'],
            {
                'code': 'DATABASE_ERROR',
                'message': (
                    'database error: total files size is too big: 300 > 200'
                ),
            },
        ),
        pytest.param(
            ['first', 'second', 'third'],
            {},
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={'settings': {'backend': {}}},
            ),
            id='if_config_disabled',
        ),
        pytest.param(
            ['first', 'second', 'third'],
            {},
            marks=pytest.mark.config(
                EXP_CUSTOM_FILES_SIZE_BY_EXPERIMENT={
                    EXPERIMENT: {
                        'st_ticket': 'TAXIEXP-600',
                        'reason': 'very need',
                        'size': 300,
                    },
                },
            ),
            id='if_setup_custom_value',
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {'backend': {'files_size_by_experiment': 200}},
    },
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
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT},
        json=body,
    )
    assert (await response.json()) == expected_answer
