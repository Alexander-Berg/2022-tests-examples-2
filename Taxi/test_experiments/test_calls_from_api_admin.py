import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

MDS_ID = '98c8bfce5f404cf6b479ed34a988efcd'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_experiment_removing': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_use_alternate_header(taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    await db.add_or_update_file(taxi_exp_app, 'file_1.txt', mds_id=MDS_ID)

    await taxi_exp_app.s3_client.upload_content(MDS_ID, body=b'')

    data = experiment.generate(
        match_predicate=experiment.infile_predicate(MDS_ID),
    )

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': 'test_name'},
        json=data,
    )
    assert response.status == 200

    # deleting second experiment
    response = await taxi_exp_client.delete(
        '/v1/experiments/',
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': 'test_name', 'last_modified_at': 1},
        json={},
    )
    assert response.status == 200
