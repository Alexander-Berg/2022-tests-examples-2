import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

MDS_ID = '98c8bfce5f404cf6b479ed34a988efcd'


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_not_predicate(taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    await db.add_or_update_file(taxi_exp_app, 'file_1.txt', mds_id=MDS_ID)

    await taxi_exp_app.s3_client.upload_content(MDS_ID, body=b'')

    data = experiment.generate(
        match_predicate={
            'type': 'not',
            'init': {'predicate': experiment.infile_predicate(MDS_ID)},
        },
    )

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name'},
        json=data,
    )
    assert response.status == 200
