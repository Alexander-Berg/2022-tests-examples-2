# pylint: disable=C5521
import json

import pytest

from .utils import select_named
from .utils import select_table


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
async def test_put_non_existent_zone(taxi_reposition_api):
    response = await taxi_reposition_api.put(
        '/v1/admin/zones/item?zone=first', json={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Zone \'first\' doesn\'t exist in geobase',
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'parent_zone,response_json',
    [
        (
            'invalid',
            {
                'code': '400',
                'message': 'Parent zone \'invalid\' doesn\'t exist in geobase',
            },
        ),
        (
            'moscow',
            {
                'code': '400',
                'message': (
                    'Parent zone \'moscow\' to clone from doesn\'t exist'
                ),
            },
        ),
    ],
)
async def test_put_non_existent_parent_zone(
        taxi_reposition_api, parent_zone, response_json,
):
    response = await taxi_reposition_api.put(
        '/v1/admin/zones/item?zone=svo', json={'parent_zone': parent_zone},
    )
    assert response.status_code == 400
    assert response.json() == response_json


@pytest.mark.nofilldb()
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('reposition')
async def test_put(taxi_reposition_api, pgsql):
    response = await taxi_reposition_api.put(
        '/v1/admin/zones/item?zone=moscow', json={},
    )
    assert response.status_code == 200
    rows = select_named(
        'SELECT zone_id, zone_name FROM config.zones', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0] == {'zone_id': 1, 'zone_name': 'moscow'}


@pytest.mark.nofilldb()
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'zone_default.sql',
        'duration.sql',
        'tags_assignments_home.sql',
    ],
)
async def test_put_with_parent(taxi_reposition_api, pgsql):
    expected_zones_before = [{'zone_id': 1, 'zone_name': '__default__'}]
    expected_zones_after = [
        {'zone_id': 1, 'zone_name': '__default__'},
        {'zone_id': 2, 'zone_name': 'moscow'},
        {'zone_id': 3, 'zone_name': 'svo'},
    ]

    expected_check_rules = [
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': None,
            'arrival_id': None,
            'duration_id': 1,
            'immobility_id': None,
            'out_of_area_id': None,
            'route_id': None,
            'antisurge_arrival_id': None,
            'surge_arrival_id': None,
            'surge_arrival_local_id': None,
            'transporting_arrival_id': None,
        },
    ]
    expected_tags = [
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': None,
            'session_tags': ['reposition_home'],
            'completed_tags': None,
        },
    ]

    actual_zones = select_named(
        'SELECT zone_id, zone_name FROM config.zones', pgsql['reposition'],
    )
    assert actual_zones == expected_zones_before

    actual_check_rules = select_named(
        'SELECT * FROM config.check_rules', pgsql['reposition'],
    )
    assert actual_check_rules == expected_check_rules

    actual_tags = select_named(
        'SELECT * FROM config.tags_zones_assignments', pgsql['reposition'],
    )
    assert actual_tags == expected_tags

    response = await taxi_reposition_api.put(
        '/v1/admin/zones/item?zone=moscow',
        json={'parent_zone': '__default__'},
    )
    assert response.status_code == 200

    response = await taxi_reposition_api.put(
        '/v1/admin/zones/item?zone=svo', json={},
    )
    assert response.status_code == 200

    actual_zones = select_named(
        'SELECT zone_id, zone_name FROM config.zones', pgsql['reposition'],
    )
    assert actual_zones == expected_zones_after

    actual_check_rules = select_named(
        'SELECT * FROM config.check_rules', pgsql['reposition'],
    )
    assert len(actual_check_rules) == 2
    assert actual_check_rules[0]['zone_id'] != actual_check_rules[1]['zone_id']
    del actual_check_rules[0]['zone_id']
    del actual_check_rules[1]['zone_id']
    assert actual_check_rules[0] == actual_check_rules[1]

    actual_tags = select_named(
        'SELECT * FROM config.tags_zones_assignments', pgsql['reposition'],
    )
    assert len(actual_tags) == 2
    assert actual_tags[0]['zone_id'] != actual_tags[1]['zone_id']
    del actual_tags[0]['zone_id']
    del actual_tags[1]['zone_id']
    assert actual_tags[0] == actual_tags[1]


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
async def test_delete_non_existent(taxi_reposition_api):
    response = await taxi_reposition_api.delete(
        '/v1/admin/zones/item?zone=blah',
    )
    assert response.status_code == 200


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
async def test_delete(taxi_reposition_api, pgsql):
    response = await taxi_reposition_api.delete(
        '/v1/admin/zones/item?zone=__default__',
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT zone_id FROM config.zones', pgsql['reposition'],
    )
    assert not rows


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('is_invalid_zone', [False, True])
async def test_check_put(taxi_reposition_api, pgsql, load, is_invalid_zone):
    zone_to_put = 'first' if is_invalid_zone else 'moscow'

    response = await taxi_reposition_api.put(
        '/v1/admin/zones/item/check?zone={}'.format(zone_to_put), json={},
    )

    if is_invalid_zone:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': 'Zone \'first\' doesn\'t exist in geobase',
        }
    else:
        assert response.status_code == 200
        assert response.json() == {'data': {}}


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
@pytest.mark.parametrize(
    'parent_zone,status_code,response_json',
    [
        (
            'invalid',
            400,
            {
                'code': '400',
                'message': 'Parent zone \'invalid\' doesn\'t exist in geobase',
            },
        ),
        (
            'moscow',
            400,
            {
                'code': '400',
                'message': (
                    'Parent zone \'moscow\' to clone from doesn\'t exist'
                ),
            },
        ),
        ('__default__', 200, {'data': {'parent_zone': '__default__'}}),
    ],
)
async def test_check_put_with_parent(
        taxi_reposition_api, pgsql, parent_zone, status_code, response_json,
):
    response = await taxi_reposition_api.put(
        '/v1/admin/zones/item/check?zone={}'.format('svo'),
        json={'parent_zone': parent_zone},
    )

    assert response.status_code == status_code
    assert response.json() == response_json


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_moscow.sql'])
async def test_check_delete(taxi_reposition_api, pgsql, load):
    response = await taxi_reposition_api.delete(
        '/v1/admin/zones/item/check?zone={}'.format('moscow'),
    )

    assert response.status_code == 200
    assert response.json() == {'data': {}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'zone_moscow.sql', 'simple_check_rules.sql'],
)
async def test_check_delete_with_dependent_settings(
        taxi_reposition_api, pgsql, load,
):
    response = await taxi_reposition_api.delete(
        '/v1/admin/zones/item/check?zone={}'.format('moscow'),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Zone moscow still has'
            ' 1 check rules,'
            ' 0 forbidden zones,'
            ' 0 tags zones assignments'
        ),
    }


@pytest.mark.config(REPOSITION_API_ADMIN_2PC_ENABLED=True)
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('fail_services', [False, True])
@pytest.mark.parametrize('check', [False, False])
async def test_2pc_put(
        taxi_reposition_api, pgsql, load, mockserver, fail_services, check,
):
    queries = [load('zone_moscow.sql')]
    pgsql['reposition'].apply_queries(queries)

    @mockserver.json_handler('/reposition-watcher/v1/admin/zones/item')
    def _mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/zones/item')
    def _mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition-watcher/v1/admin/zones/item/check')
    def _mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/zones/item/check')
    def _mock_matcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    data = {'parent_zone': 'moscow'}
    check_part = '/check' if check else ''
    response = await taxi_reposition_api.put(
        f'/v1/admin/zones/item{check_part}?zone=cao', json=data,
    )

    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': (
                'Failed to insert zone in reposition-matcher: '
                'PUT /v1/admin/zones/item, status code 400'
            ),
        }
        return
    assert response.status_code == 200


@pytest.mark.config(REPOSITION_API_ADMIN_2PC_ENABLED=True)
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('fail_services', [False, True])
@pytest.mark.parametrize('check', [False, False])
async def test_2pc_delete(
        taxi_reposition_api, pgsql, load, mockserver, fail_services, check,
):
    queries = [load('zone_moscow.sql')]
    pgsql['reposition'].apply_queries(queries)

    @mockserver.json_handler('/reposition-watcher/v1/admin/zones/item')
    def _mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/zones/item')
    def _mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition-watcher/v1/admin/zones/item/check')
    def _mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/zones/item/check')
    def _mock_matcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    check_part = '/check' if check else ''
    response = await taxi_reposition_api.delete(
        f'/v1/admin/zones/item{check_part}?zone=moscow',
    )
    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': (
                'Failed to delete zone in reposition-matcher: '
                'DELETE /v1/admin/zones/item, status code 400'
            ),
        }
        return
    assert response.status_code == 200

    if not check:
        rows = select_table('config.zones', 'zone_id', pgsql['reposition'])
        assert rows == []
