# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performer_put_ok(taxi_crowd_integration):
    response = await taxi_crowd_integration.get(
        '/v1/yang/performer', params={'id': 'yang_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {'staff_login': 'StaffLogin1'}

    response = await taxi_crowd_integration.put(
        '/v1/yang/performer',
        params={'id': 'yang_id_1', 'staff_login': 'login1'},
    )
    assert response.status_code == 200

    response = await taxi_crowd_integration.get(
        '/v1/yang/performer', params={'id': 'yang_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {'staff_login': 'login1'}


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performer_set_ok(taxi_crowd_integration):
    response = await taxi_crowd_integration.get(
        '/v1/yang/performer', params={'id': 'yang_id_7'},
    )
    assert response.status_code == 404

    response = await taxi_crowd_integration.put(
        '/v1/yang/performer',
        params={'id': 'yang_id_7', 'staff_login': 'StaffLogin7'},
    )
    assert response.status_code == 200

    response = await taxi_crowd_integration.get(
        '/v1/yang/performer', params={'id': 'yang_id_7'},
    )
    assert response.status_code == 200
    assert response.json() == {'staff_login': 'StaffLogin7'}


@pytest.mark.pgsql('crowd_integration', files=['performers.sql'])
async def test_v1_yang_performer_push_ok(taxi_crowd_integration):
    response = await taxi_crowd_integration.post(
        '/v1/yang/performers', {'ids': ['yang_id1', 'yang_id_1', 'yang_id_2']},
    )
    assert response.status_code == 200
    assert response.json() == {
        'found': ['StaffLogin1', 'StaffLogin2'],
        'not_found': ['yang_id1'],
    }

    response = await taxi_crowd_integration.post(
        '/v1/yang/performers/push',
        {
            'performers': [
                {'id': 'yang_id1', 'staff_login': 'login1'},
                {'id': 'yang_id_2', 'staff_login': 'login2'},
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_crowd_integration.post(
        '/v1/yang/performers', {'ids': ['yang_id1', 'yang_id_1', 'yang_id_2']},
    )
    assert response.status_code == 200
    assert response.json() == {'found': ['login1', 'StaffLogin1', 'login2']}
