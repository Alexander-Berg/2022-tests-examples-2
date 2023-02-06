import copy
import hashlib

AUTH_HEADERS = {'X-Token': 'test'}
DEFAULT_SETTINGS = {
    'bulk_size': 1000,
    'db_timeout_ms': 500,
    'exc_period_ms': 5000,
    'period_ms': 100,
    'test_run': True,
    'ypa_timeout_ms': 1000,
}


def _get_file_sha1(filename):
    with open(filename, 'rb') as file:
        return hashlib.sha1(file.read()).hexdigest()


def _update(dict_to_update, new_values):
    for key, value in new_values.items():
        if isinstance(value, dict):
            _update(dict_to_update.setdefault(key, {}), value)
        else:
            dict_to_update[key] = value


async def test_ypa_migration(
        taxi_userplaces, mockserver, get_file_path, load_json,
):
    # Check the initial status
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/status', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'phonish_map': {'num_records_loaded': 0},
        'running': False,
        'settings': DEFAULT_SETTINGS,
    }

    # Update settings, state and load the phonish map
    settings = copy.deepcopy(DEFAULT_SETTINGS)
    settings.update({'bulk_size': 3, 'test_run': False, 'period_ms': 2000})

    phonish_map_file = str(get_file_path('phonish_map.tskv'))
    phonish_map_sha1 = _get_file_sha1(phonish_map_file)
    phonish_map_source = {
        'covers_places_created_up_to': '2022-01-01T00:00:00+0000',
        'file_name': phonish_map_file,
        'file_sha1': phonish_map_sha1,
    }

    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/update',
        json={
            'phonish_map': phonish_map_source,
            'settings': settings,
            'state': {'stats': {}, 'cursor': {}},
        },
        headers=AUTH_HEADERS,
    )
    expected_state = {
        'phonish_map': {'num_records_loaded': 4, 'source': phonish_map_source},
        'running': False,
        'settings': settings,
        'state': {
            'cursor': {},
            'done': False,
            'stats': {
                'drafted': 0,
                'not_covered': 0,
                'parse_error': 0,
                'phonish_cant_recover_uid': 0,
                'phonish_stale': 0,
                'phonish_uid_different': 0,
                'phonish_uid_match': 0,
                'phonish_uid_recovered': 0,
                'total': 0,
                'total_exported_places': 0,
                'old_format': 0,
                'impostor_phonish_uid': 0,
                'phonish_cant_recover_uid_use_existing': 0,
                'empty_locales': 0,
            },
        },
    }
    assert response.status_code == 200
    assert response.json() == expected_state

    # Start the migration
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/start', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'result': 'started'}
    expected_state['running'] = True

    # Check that it has indeed started
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/status', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_state

    # Now that the callback is set we can use periodic task control
    # But first set up a YPA mockserver handler:
    ypa_request = 0
    expected_ypa_requests = load_json('expected_ypa_requests.json')

    @mockserver.json_handler('/ya-pers-address/address/update')
    def _mock_ypa_update(request):
        nonlocal ypa_request
        assert request.query['insert'] == 'true'
        assert request.json == expected_ypa_requests[ypa_request]
        ypa_request += 1

        return {'status': 'ok'}

    # Do a migration iteration 1:
    await taxi_userplaces.run_periodic_task('ypa_migration')
    _update(
        expected_state,
        {
            'state': {
                'stats': {
                    'not_covered': 1,
                    'total': 3,
                    'drafted': 1,
                    'total_exported_places': 2,
                },
                'cursor': {
                    'last_ids': ['1a000000000000000000000000000003'],
                    'last_updated': '2021-12-13T16:53:35.281+0000',
                },
            },
        },
    )
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/status', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_state

    # Do a migration iteration 2:
    await taxi_userplaces.run_periodic_task('ypa_migration')
    _update(
        expected_state,
        {
            'state': {
                'stats': {
                    'not_covered': 1,
                    'total': 6,
                    'total_exported_places': 5,
                },
                'cursor': {
                    'last_ids': ['1a000000000000000000000000000006'],
                    'last_updated': '2021-12-13T16:53:15.187+0000',
                },
            },
        },
    )
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/status', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_state

    # Do a migration iteration 3:
    await taxi_userplaces.run_periodic_task('ypa_migration')
    _update(
        expected_state,
        {
            'state': {
                'stats': {
                    'not_covered': 1,
                    'total': 8,
                    'phonish_uid_recovered': 1,
                    'impostor_phonish_uid': 1,
                    'total_exported_places': 7,
                },
                'cursor': {
                    'last_ids': ['1a000000000000000000000000000008'],
                    'last_updated': '2021-12-13T16:53:04.166+0000',
                },
            },
        },
    )
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/status', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_state

    # Do a migration iteration 4:
    await taxi_userplaces.run_periodic_task('ypa_migration')
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/status', json={}, headers=AUTH_HEADERS,
    )
    _update(expected_state, {'state': {'done': True}})
    assert response.status_code == 200
    assert response.json() == expected_state

    # Stop the migration
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/stop', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'result': 'stopped'}
    _update(expected_state, {'running': False})

    # Check that it has indeed stopped
    response = await taxi_userplaces.post(
        '/userplaces/ypa_migration/status', json={}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_state

    assert _mock_ypa_update.times_called == 3
