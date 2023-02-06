import pytest


@pytest.mark.pgsql('candidate-meta', files=['test.sql'])
@pytest.mark.servicetest
async def test_get_old(taxi_candidate_meta):
    response = await taxi_candidate_meta.post(
        '/v1/candidate/meta/get',
        json={
            'order_id': 'order',
            'park_id': 'park',
            'driver_profile_id': 'uuid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'metadata': {'key': 'value'}}


@pytest.mark.pgsql('candidate-meta', files=['test.sql'])
@pytest.mark.servicetest
@pytest.mark.config(
    CANDIDATE_META_DB={
        'read-new': True,
        'write-new': False,
        'write-old': True,
    },
)
async def test_get_new(taxi_candidate_meta):
    response = await taxi_candidate_meta.post(
        '/v1/candidate/meta/get',
        json={
            'order_id': 'order-new',
            'park_id': 'park',
            'driver_profile_id': 'uuid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'metadata': {'key': 'value', 'key2': 'value2'}}
