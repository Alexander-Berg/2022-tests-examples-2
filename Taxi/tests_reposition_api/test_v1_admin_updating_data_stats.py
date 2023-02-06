import pytest


def force_analyze(db):
    db.conn.cursor().execute('ANALYZE etag_data.drivers_update_state')


@pytest.mark.now('2019-11-05T12:00:00')
async def test_empty_db(taxi_reposition_api, pgsql):
    force_analyze(pgsql['reposition'])

    response = await taxi_reposition_api.get('/v1/admin/updating_data_stats')

    assert response.status_code == 200
    assert response.json() == {
        'data_fullness': {'drivers_completed': 0, 'drivers_total': 0},
        'update_stat': {'updates': []},
    }


@pytest.mark.now('2019-11-05T12:00:00')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'etag_data_fullness_part.sql'],
)
async def test_fullness_progress_part(taxi_reposition_api, pgsql):
    force_analyze(pgsql['reposition'])

    response = await taxi_reposition_api.get('/v1/admin/updating_data_stats')

    assert response.status_code == 200
    assert response.json() == {
        'data_fullness': {'drivers_completed': 5, 'drivers_total': 12},
        'update_stat': {'updates': []},
    }


@pytest.mark.now('2019-11-05T12:00:00')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'etag_data_fullness_full.sql'],
)
async def test_fullness_progress_full(taxi_reposition_api, pgsql):
    force_analyze(pgsql['reposition'])

    response = await taxi_reposition_api.get('/v1/admin/updating_data_stats')

    assert response.status_code == 200
    assert response.json() == {
        'data_fullness': {'drivers_completed': 12, 'drivers_total': 12},
        'update_stat': {'updates': []},
    }


@pytest.mark.now('2019-11-05T12:02:30')
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'update_requests.sql'])
async def test_updates(taxi_reposition_api, pgsql):
    def _make_stable(json):
        for update in json['update_stat']['updates']:
            if 'data_to_update' in update:
                update['data_to_update'].sort()
        if 'archived_updates' not in json:
            return

        for update in json['archived_updates']:
            update['data_to_update'].sort()

    force_analyze(pgsql['reposition'])

    response = await taxi_reposition_api.get('/v1/admin/updating_data_stats')
    assert response.status_code == 200
    response_json = response.json()
    _make_stable(response_json)
    assert response_json == {
        'data_fullness': {'drivers_completed': 12, 'drivers_total': 12},
        'update_stat': {
            'drivers_completed': 5,
            'drivers_total': 12,
            'updates': [
                {
                    'data_to_update': ['offered_modes', 'state', 'user_modes'],
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

    response = await taxi_reposition_api.get(
        '/v1/admin/updating_data_stats?archive_count=50',
    )
    assert response.status_code == 200
    response_json = response.json()
    _make_stable(response_json)
    assert response_json['archived_updates'] == [
        {
            'data_to_update': ['user_modes'],
            'created_at': '2019-11-05T11:35:00+00:00',
            'started_at': '2019-11-05T11:40:00+00:00',
            'finished_at': '2019-11-05T11:55:00+00:00',
        },
        {
            'data_to_update': ['offered_modes', 'state', 'user_modes'],
            'created_at': '2019-11-05T11:00:00+00:00',
            'started_at': '2019-11-05T11:05:00+00:00',
            'finished_at': '2019-11-05T11:30:00+00:00',
        },
    ]


async def test_bad_request(taxi_reposition_api):
    response = await taxi_reposition_api.get(
        '/v1/admin/updating_data_stats?archive_count=0',
    )

    assert response.status_code == 400
