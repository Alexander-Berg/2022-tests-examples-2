import pytest


def force_analyze(db):
    db.conn.cursor().execute('ANALYZE etag_data.drivers_update_state')


@pytest.mark.now('2019-11-05T12:00:00')
def test_empty_db(taxi_reposition, pgsql):
    force_analyze(pgsql['reposition'])

    response = taxi_reposition.get('v2/settings/etag_data_stats')

    assert response.status_code == 200
    assert response.json() == {
        'etag_data_fullness': {'drivers_completed': 0, 'drivers_total': 0},
        'etag_update_stat': {'updates': []},
    }


@pytest.mark.now('2019-11-05T12:00:00')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'etag_data_fullness_part.sql'],
)
def test_fullness_progress_part(taxi_reposition, pgsql):
    force_analyze(pgsql['reposition'])

    response = taxi_reposition.get('v2/settings/etag_data_stats')

    assert response.status_code == 200
    assert response.json() == {
        'etag_data_fullness': {'drivers_completed': 5, 'drivers_total': 12},
        'etag_update_stat': {'updates': []},
    }


@pytest.mark.now('2019-11-05T12:00:00')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'etag_data_fullness_full.sql'],
)
def test_fullness_progress_full(taxi_reposition, pgsql):
    force_analyze(pgsql['reposition'])

    response = taxi_reposition.get('v2/settings/etag_data_stats')

    assert response.status_code == 200
    assert response.json() == {
        'etag_data_fullness': {'drivers_completed': 12, 'drivers_total': 12},
        'etag_update_stat': {'updates': []},
    }


@pytest.mark.now('2019-11-05T12:02:30')
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'update_requests.sql'])
def test_updates(taxi_reposition, pgsql):
    force_analyze(pgsql['reposition'])

    response = taxi_reposition.get('v2/settings/etag_data_stats')

    assert response.status_code == 200
    assert response.json() == {
        'etag_data_fullness': {'drivers_completed': 12, 'drivers_total': 12},
        'etag_update_stat': {
            'drivers_completed': 5,
            'drivers_total': 12,
            'updates': [
                {
                    'data_to_update': ['state', 'user_modes', 'offered_modes'],
                    'created_at': '2019-11-05T11:55:00+00:00',
                    'scheduled_for': '2019-11-05T12:00:00+00:00',
                    'started_at': '2019-11-05T12:00:00+00:00',
                },
                {
                    'data_to_update': ['user_modes'],
                    'created_at': '2019-11-05T12:00:00+00:00',
                    'scheduled_for': '2019-11-05T12:05:00+00:00',
                },
            ],
        },
    }

    response = taxi_reposition.get(
        'v2/settings/etag_data_stats?archive_count=50',
    )

    assert response.status_code == 200
    assert response.json()['archived_etag_updates'] == [
        {
            'data_to_update': ['user_modes'],
            'created_at': '2019-11-05T11:35:00+00:00',
            'started_at': '2019-11-05T11:40:00+00:00',
            'finished_at': '2019-11-05T11:55:00+00:00',
        },
        {
            'data_to_update': ['state', 'user_modes', 'offered_modes'],
            'created_at': '2019-11-05T11:00:00+00:00',
            'started_at': '2019-11-05T11:05:00+00:00',
            'finished_at': '2019-11-05T11:30:00+00:00',
        },
    ]


def test_bad_request(taxi_reposition):
    response = taxi_reposition.get(
        'v2/settings/etag_data_stats?archive_count=0',
    )

    assert response.status_code == 400
