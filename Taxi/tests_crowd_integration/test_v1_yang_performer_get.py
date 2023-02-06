# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performer_get_ok(taxi_crowd_integration):
    response = await taxi_crowd_integration.get(
        '/v1/yang/performer', params={'id': 'yang_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {'staff_login': 'StaffLogin1'}


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performer_get_not_found(taxi_crowd_integration):
    response = await taxi_crowd_integration.get(
        '/v1/yang/performer', params={'id': 'yang_id1'},
    )
    assert response.status_code == 404


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performers_post_ok(taxi_crowd_integration):
    response = await taxi_crowd_integration.post(
        '/v1/yang/performers', {'ids': ['yang_id1', 'yang_id_1', 'yang_id_2']},
    )
    assert response.status_code == 200
    assert response.json() == {
        'found': ['StaffLogin1', 'StaffLogin2'],
        'not_found': ['yang_id1'],
    }


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performers_post_ok_all_found(taxi_crowd_integration):
    response = await taxi_crowd_integration.post(
        '/v1/yang/performers', {'ids': ['yang_id_1', 'yang_id_2']},
    )
    assert response.status_code == 200
    assert response.json() == {'found': ['StaffLogin1', 'StaffLogin2']}


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performers_post_ok_all_not_found(
        taxi_crowd_integration,
):
    response = await taxi_crowd_integration.post(
        '/v1/yang/performers', {'ids': ['yang_id1', 'yang_id2']},
    )
    assert response.status_code == 200
    assert response.json() == {'not_found': ['yang_id1', 'yang_id2']}
