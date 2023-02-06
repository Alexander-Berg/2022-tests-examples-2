from datetime import datetime

import pytest

from .reposition_select import select_named
from .reposition_select import select_table


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_get_empty(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/forbidden')
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'zone_moscow.sql', 'forbidden_home_moscow.sql'],
)
def test_get(taxi_reposition, pgsql):
    response = taxi_reposition.get('/v1/settings/zones/forbidden')
    assert response.status_code == 200
    assert response.json() == {'home': {'moscow': 'deny_default'}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_put_mode_not_found(taxi_reposition):
    response = taxi_reposition.put(
        '/v1/settings/zones/forbidden?mode=home', json={'svo': 'deny_default'},
    )
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql'])
def test_put_zone_not_found(taxi_reposition):
    response = taxi_reposition.put(
        '/v1/settings/zones/forbidden?mode=home', json={'svo': 'deny_default'},
    )
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Zone \'svo\' not found'}}


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_moscow.sql'])
def test_put(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/zones/forbidden?mode=home',
        json={'moscow': 'deny_default'},
    )
    assert response.status_code == 200
    rows = select_table(
        'config.forbidden_zones', 'zone_id', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0] == (1, 2, 'deny_default')

    upd_requests = select_named(
        'SELECT update_state, update_modes, update_offered_modes, created_at,'
        'started_at, finished_at, cancelled FROM etag_data.update_requests',
        pgsql['reposition'],
    )

    assert upd_requests == [
        {
            'update_state': True,
            'update_modes': True,
            'update_offered_modes': False,
            'created_at': datetime(2018, 10, 15, 18, 18, 46),
            'started_at': None,
            'finished_at': None,
            'cancelled': False,
        },
    ]


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition', files=['mode_home.sql', 'zone_moscow.sql', 'zone_svo.sql'],
)
def test_put_override(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/zones/forbidden?mode=home',
        json={'moscow': 'deny_default'},
    )
    assert response.status_code == 200
    rows = select_table(
        'config.forbidden_zones', 'zone_id', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0] == (1, 2, 'deny_default')

    response = taxi_reposition.put(
        '/v1/settings/zones/forbidden?mode=home', json={'svo': 'deny_default'},
    )
    assert response.status_code == 200
    rows = select_table(
        'config.forbidden_zones', 'zone_id', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0] == (1, 3, 'deny_default')

    response = taxi_reposition.put(
        '/v1/settings/zones/forbidden?mode=home',
        json={'moscow': 'default', 'svo': 'deny'},
    )
    assert response.status_code == 200
    rows = select_table(
        'config.forbidden_zones', 'zone_id', pgsql['reposition'],
    )
    assert len(rows) == 2
    assert rows[0] == (1, 2, 'default')
    assert rows[1] == (1, 3, 'deny')


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql'])
def test_delete_non_existent(taxi_reposition, pgsql):
    response = taxi_reposition.delete('/v1/settings/zones/forbidden?mode=home')
    assert response.status_code == 200

    rows = select_table(
        'etag_data.update_requests', 'update_request_id', pgsql['reposition'],
    )
    assert rows == []


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_delete_mode_not_found(taxi_reposition):
    response = taxi_reposition.delete('/v1/settings/zones/forbidden?mode=home')
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'zone_moscow.sql', 'forbidden_home_moscow.sql'],
)
def test_delete(taxi_reposition, pgsql):
    response = taxi_reposition.delete('/v1/settings/zones/forbidden?mode=home')
    assert response.status_code == 200
    rows = select_table(
        'config.forbidden_zones', 'zone_id', pgsql['reposition'],
    )
    assert len(rows) == 0

    upd_requests = select_named(
        'SELECT update_state, update_modes, update_offered_modes, created_at,'
        'started_at, finished_at, cancelled FROM etag_data.update_requests',
        pgsql['reposition'],
    )

    assert upd_requests == [
        {
            'update_state': True,
            'update_modes': True,
            'update_offered_modes': False,
            'created_at': datetime(2018, 10, 15, 18, 18, 46),
            'started_at': None,
            'finished_at': None,
            'cancelled': False,
        },
    ]
