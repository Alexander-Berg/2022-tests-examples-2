import pytest


QUERIES = (
    'INSERT INTO basic_sample_db.main_table '
    '	(name, action, previous_action, updated_at) '
    'VALUES (\'second\', \'walking\', \'walking\', NOW())',
)

# '.sql' files are searched in ./static/NAME-OF-THIS-FILE-WITHOUT_EXT/NAME.sql
@pytest.mark.pgsql('basic_sample_db', files=['queries_in_file.sql'])
async def test_sample_v1_action_error(taxi_userver_sample):
    json = {'id': 'DaName', 'action': 'walking'}
    response = await taxi_userver_sample.put('sample/v1/action', json=json)
    assert response.status_code == 400
    assert response.json()['code'] == 'INVALID_OPERATION'


@pytest.mark.pgsql('basic_sample_db', queries=QUERIES)
async def test_sample_v1_action_ok_psql(taxi_userver_sample):
    json = {'id': 'second', 'action': 'standing'}
    response = await taxi_userver_sample.put('sample/v1/action', json=json)
    assert response.status_code == 200
    assert response.json()['previous_action'] == 'walking'
