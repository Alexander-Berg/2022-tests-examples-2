import pytest

from .reposition_select import select_table_named


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
def test_get_empty_settings(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/tags?zone=__default__')
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_get_zone_not_found(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/tags?zone=__default__')
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Zone \'__default__\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'submodes_home.sql',
        'zone_default.sql',
        'simple_tags_assignments.sql',
    ],
)
def test_get(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/tags?zone=__default__')
    assert response.status_code == 200
    assert response.json() == {
        'home': {
            'session': {'tags': ['tag_1']},
            'completed': {'tags': ['tag_2']},
            'submodes': {
                'fast': {
                    'session': {'tags': ['tag_3']},
                    'completed': {'tags': ['tag_4']},
                },
                'slow': {'session': {'tags': ['tag_5']}},
            },
        },
    }


@pytest.mark.nofilldb()
@pytest.mark.parametrize('submode', [False, True])
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'submodes_home.sql'])
def test_put_zone_not_found(taxi_reposition, submode):
    request_add = '&submode=fast' if submode is True else ''
    response = taxi_reposition.put(
        '/v1/settings/zones/tags?zone=__default__&mode=home' + request_add,
        {
            'session': {'tags': ['default_home_tag']},
            'completed': {'tags': ['default_home_end_tag']},
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Zone \'__default__\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
def test_put_mode_not_found(taxi_reposition):
    response = taxi_reposition.put(
        '/v1/settings/zones/tags?zone=__default__&mode=home',
        {
            'session': {'tags': ['default_home_tag']},
            'completed': {'tags': ['default_home_end_tag']},
        },
    )
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_default.sql'])
def test_put_submode_not_found(taxi_reposition):
    response = taxi_reposition.put(
        (
            '/v1/settings/zones/tags?'
            + 'zone=__default__&mode=home&submode=fast'
        ),
        {
            'session': {'tags': ['default_home_tag']},
            'completed': {'tags': ['default_home_end_tag']},
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Pair mode \'home\' and submode \'fast\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.parametrize('zone', ['__default__', 'moscow'])
@pytest.mark.parametrize('submode', [False, True])
@pytest.mark.parametrize('session_tags', [None, [], ['session_tag1']])
@pytest.mark.parametrize('completed_tags', [None, [], ['completed_tag1']])
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'submodes_home.sql',
        'zone_default.sql',
        'zone_moscow.sql',
        'default_home_tags_assignments.sql',
    ],
)
def test_put(
        taxi_reposition, pgsql, zone, submode, session_tags, completed_tags,
):
    request_add = '&submode=fast' if submode else ''
    request = {
        'session': {'tags': session_tags},
        'completed': {'tags': completed_tags},
    }

    if session_tags is None:
        del request['session']
    if completed_tags is None:
        del request['completed']

    response = taxi_reposition.put(
        '/v1/settings/zones/tags?zone=' + zone + '&mode=home' + request_add,
        request,
    )
    assert response.status_code == 200
    assert response.json() == {}

    expected_rows = [
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': None,
            'session_tags': ['tag_1'],
            'completed_tags': ['tag_2'],
        },
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': 1,
            'session_tags': ['tag_3'],
            'completed_tags': ['tag_4'],
        },
    ]

    rows = select_table_named(
        'config.tags_zones_assignments',
        'zone_id ASC, mode_id ASC, submode_id ASC NULLS FIRST',
        pgsql['reposition'],
    )

    if zone == '__default__':
        upsert_idx = 1 if submode else 0
        expected_rows[upsert_idx] = {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': 1 if submode else None,
            'session_tags': session_tags,
            'completed_tags': completed_tags,
        }
    else:
        expected_rows.append(
            {
                'zone_id': 2,
                'mode_id': 1,
                'submode_id': 1 if submode else None,
                'session_tags': session_tags,
                'completed_tags': completed_tags,
            },
        )
    assert expected_rows == rows


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql'])
def test_delete_zone_not_found(taxi_reposition):
    response = taxi_reposition.get(
        '/v1/settings/zones/tags?zone=__default__&mode=home',
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Zone \'__default__\' not found'},
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
def test_delete_mode_not_found(taxi_reposition):
    response = taxi_reposition.delete(
        '/v1/settings/zones/tags?zone=__default__&mode=home',
    )
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_default.sql'])
def test_delete_non_existent(taxi_reposition):
    response = taxi_reposition.delete(
        '/v1/settings/zones/tags?zone=__default__&mode=home',
    )
    assert response.status_code == 200


@pytest.mark.nofilldb()
@pytest.mark.parametrize('submode', [False, True])
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'submodes_home.sql',
        'zone_default.sql',
        'simple_tags_assignments.sql',
    ],
)
def test_delete(taxi_reposition, pgsql, submode):
    request_add = '&submode=fast' if submode is True else ''
    response = taxi_reposition.delete(
        '/v1/settings/zones/tags?zone=__default__&mode=home' + request_add,
    )
    assert response.status_code == 200

    expected_rows = [
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': None,
            'session_tags': ['tag_1'],
            'completed_tags': ['tag_2'],
        },
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': 1,
            'session_tags': ['tag_3'],
            'completed_tags': ['tag_4'],
        },
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': 2,
            'session_tags': ['tag_5'],
            'completed_tags': None,
        },
    ]

    rows = select_table_named(
        'config.tags_zones_assignments', 'zone_id', pgsql['reposition'],
    )
    if submode:
        del expected_rows[1]
    else:
        expected_rows = []

    assert expected_rows == rows


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'submode,load_modes,load_submodes,load_zones,is_delete',
    [
        (False, False, False, False, False),
        (False, False, False, False, True),
        (False, False, False, True, False),
        (False, False, False, True, True),
        (False, True, False, True, False),
        (False, True, False, True, True),
        (False, True, True, True, False),
        (False, True, True, True, True),
        (True, True, True, True, False),
        (True, True, True, True, True),
    ],
)
def test_check(
        taxi_reposition,
        pgsql,
        load,
        submode,
        load_modes,
        load_submodes,
        load_zones,
        is_delete,
):
    zone_not_found_response = {
        'error': {'text': 'Zone \'__default__\' not found'},
    }
    mode_not_found_response = {'error': {'text': 'Mode \'home\' not found'}}
    submode_not_found_response = {
        'error': {'text': 'Pair mode \'home\' and submode \'fast\' not found'},
    }
    queries = []
    if load_modes:
        queries.append(load('mode_home.sql'))
    if load_modes and load_submodes:
        queries.append(load('submodes_home.sql'))
    if load_zones:
        queries.append(load('zone_default.sql'))
    pgsql['reposition'].apply_queries(queries)

    request_add = '&submode=fast' if submode is True else ''
    request_data = {
        'session': {'tags': ['default_home_tag']},
        'completed': {'tags': ['default_home_end_tag']},
    }

    response = (
        taxi_reposition.put(
            '/v1/settings/zones/tags/check?zone=__default__&mode=home'
            + request_add,
            request_data,
        )
        if not is_delete
        else taxi_reposition.delete(
            '/v1/settings/zones/tags/check?zone=__default__&mode=home'
            + request_add,
        )
    )
    if not load_modes or not load_zones or (not load_submodes and submode):
        assert response.status_code == 404
    else:
        assert response.status_code == 200
    if not load_zones:
        assert response.json() == zone_not_found_response
        return
    if not load_modes:
        assert response.json() == mode_not_found_response
        return
    if not load_submodes and submode:
        assert response.json() == submode_not_found_response
        return
    if not is_delete:
        assert response.json() == {'data': request_data}
        return
    assert response.json() == {'data': {}}
