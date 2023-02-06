# pylint: disable=C5521
import pytest

from .utils import select_table_named


@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
async def test_get_empty_settings(taxi_reposition_api):
    response = await taxi_reposition_api.get(
        '/v1/admin/zones/tags?zone=__default__',
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.pgsql('reposition')
async def test_get_zone_not_found(taxi_reposition_api):
    response = await taxi_reposition_api.get(
        '/v1/admin/zones/tags?zone=__default__',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Zone \'__default__\' is not found',
    }


@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'submodes_home.sql',
        'zone_default.sql',
        'simple_tags_assignments.sql',
    ],
)
async def test_get(taxi_reposition_api):
    response = await taxi_reposition_api.get(
        '/v1/admin/zones/tags?zone=__default__',
    )
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


@pytest.mark.parametrize('submode', [False, True])
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'submodes_home.sql'])
async def test_put_zone_not_found(taxi_reposition_api, submode):
    request_add = '&submode=fast' if submode is True else ''
    response = await taxi_reposition_api.put(
        f'/v1/admin/zones/tags?zone=__default__&mode=home{request_add}',
        {
            'session': {'tags': ['default_home_tag']},
            'completed': {'tags': ['default_home_end_tag']},
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Zone \'__default__\' is not found',
    }


@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
async def test_put_mode_not_found(taxi_reposition_api):
    response = await taxi_reposition_api.put(
        '/v1/admin/zones/tags?zone=__default__&mode=home',
        {
            'session': {'tags': ['default_home_tag']},
            'completed': {'tags': ['default_home_end_tag']},
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Mode \'home\' is not found',
    }


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_default.sql'])
async def test_put_submode_not_found(taxi_reposition_api):
    response = await taxi_reposition_api.put(
        '/v1/admin/zones/tags?zone=__default__&mode=home&submode=fast',
        {
            'session': {'tags': ['default_home_tag']},
            'completed': {'tags': ['default_home_end_tag']},
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Submode \'fast\' for mode \'home\' is not found',
    }


@pytest.mark.parametrize(
    'zone, submode, session_tags, completed_tags',
    [
        ('__default__', False, None, None),
        ('moscow', True, [], []),
        ('moscow', False, ['session_tag1'], ['completed_tag1']),
        ('__default__', True, ['session_tag1'], []),
        ('__default__', False, [], ['completed_tag1']),
    ],
)
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
async def test_put(
        taxi_reposition_api,
        pgsql,
        zone,
        submode,
        session_tags,
        completed_tags,
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

    response = await taxi_reposition_api.put(
        f'/v1/admin/zones/tags?zone={zone}&mode=home{request_add}', request,
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


@pytest.mark.pgsql('reposition', files=['mode_home.sql'])
async def test_delete_zone_not_found(taxi_reposition_api):
    response = await taxi_reposition_api.get(
        '/v1/admin/zones/tags?zone=__default__&mode=home',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Zone \'__default__\' is not found',
    }


@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
async def test_delete_mode_not_found(taxi_reposition_api):
    response = await taxi_reposition_api.delete(
        '/v1/admin/zones/tags?zone=__default__&mode=home',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Mode \'home\' is not found',
    }


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'zone_default.sql'])
async def test_delete_non_existent(taxi_reposition_api):
    response = await taxi_reposition_api.delete(
        '/v1/admin/zones/tags?zone=__default__&mode=home',
    )
    assert response.status_code == 200


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
async def test_delete(taxi_reposition_api, pgsql, submode):
    request_add = '&submode=fast' if submode is True else ''
    response = await taxi_reposition_api.delete(
        f'/v1/admin/zones/tags?zone=__default__&mode=home{request_add}',
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


@pytest.mark.parametrize(
    'submode,load_modes,load_submodes,load_zones,is_delete',
    [
        (False, False, False, False, False),
        (True, True, True, True, True),
        (True, True, True, True, False),
        (False, True, False, True, False),
        (False, False, False, True, False),
        (False, False, False, False, True),
    ],
)
async def test_check(
        taxi_reposition_api,
        pgsql,
        load,
        submode,
        load_modes,
        load_submodes,
        load_zones,
        is_delete,
):
    zone_not_found_response = {
        'code': '404',
        'message': 'Zone \'__default__\' is not found',
    }
    mode_not_found_response = {
        'code': '404',
        'message': 'Mode \'home\' is not found',
    }
    submode_not_found_response = {
        'code': '404',
        'message': 'Submode \'fast\' for mode \'home\' is not found',
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

    response = await (
        taxi_reposition_api.put(
            '/v1/admin/zones/tags/check?'
            f'zone=__default__&mode=home{request_add}',
            request_data,
        )
        if not is_delete
        else taxi_reposition_api.delete(
            '/v1/admin/zones/tags/check?'
            f'zone=__default__&mode=home{request_add}',
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
    # changed behavior, delete doesn't send 'data' field
