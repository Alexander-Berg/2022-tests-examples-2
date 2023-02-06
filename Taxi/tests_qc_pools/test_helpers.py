import pytest


@pytest.mark.pgsql('qc_pools', files=['simple_pass_insert.sql'])
async def test_sample_get_ok_psql(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id1'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('simple_pass.json')
