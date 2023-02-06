import json

import pytest

from .reposition_select import select_named
from .reposition_select import select_table

# There are some bad tests: they are based on the geoarea cache,
# which seems to persist from the already run tests


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_empty(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/list')
    assert response.status_code == 200
    assert response.json() == {'zones': []}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'zone_moscow.sql', 'zone_svo.sql'],
)
def test_get(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/zones/list')
    assert response.status_code == 200
    data = response.json()['zones']
    data.sort(key=lambda x: x['zone_id'])
    assert data == [
        {'zone_id': '__default__'},
        {'zone_id': 'moscow'},
        {'zone_id': 'svo'},
    ]


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_put_non_existent_zone(taxi_reposition):
    response = taxi_reposition.put(
        '/v1/settings/zones/item?zone=first', json={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': {'text': 'Zone \'first\' doesn\'t exist in geobase!'},
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize(
    'parent_zone,response_json',
    [
        (
            'invalid',
            {
                'error': {
                    'text': (
                        'Parent zone \'invalid\' doesn\'t exist in geobase!'
                    ),
                },
            },
        ),
        (
            'moscow',
            {
                'error': {
                    'text': (
                        'Parent zone \'moscow\' to clone from doesn\'t exist!'
                    ),
                },
            },
        ),
    ],
)
def test_put_non_existent_parent_zone(
        taxi_reposition, parent_zone, response_json,
):
    response = taxi_reposition.put(
        '/v1/settings/zones/item?zone=svo', json={'parent_zone': parent_zone},
    )
    assert response.status_code == 400
    assert response.json() == response_json


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_put(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/zones/item?zone=moscow', json={},
    )
    assert response.status_code == 200
    rows = select_named(
        'SELECT zone_id, zone_name FROM config.zones', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0] == {'zone_id': 1, 'zone_name': 'moscow'}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'zone_default.sql',
        'check_rules.sql',
        'deviation_formulae_home.sql',
        'tags_assignments_home.sql',
    ],
)
def test_put_with_parent(taxi_reposition, pgsql):
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
            'arrival_id': 1,
            'duration_id': 1,
            'immobility_id': 1,
            'out_of_area_id': None,
            'route_id': None,
            'antisurge_arrival_id': None,
            'surge_arrival_id': None,
            'surge_arrival_local_id': None,
            'transporting_arrival_id': None,
        },
    ]
    expected_deviation_formulae = [
        {
            'zone_id': 1,
            'mode_id': 1,
            'submode_id': None,
            'area_mode': False,
            'completed': False,
            'destination_district_mode': None,
            'dh_time_cmp_coeff': None,
            'pass_bh_route_info': None,
            'regular_mode': '(0.99,0.949,0.1,0.7,0.9,-0.2,-0.1,2120,600)',
            'regular_offer_mode': None,
            'surge_mode': None,
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

    actual_deviation_formulae = select_named(
        'SELECT * FROM config.deviation_formulae', pgsql['reposition'],
    )
    assert actual_deviation_formulae == expected_deviation_formulae

    actual_tags = select_named(
        'SELECT * FROM config.tags_zones_assignments', pgsql['reposition'],
    )
    assert actual_tags == expected_tags

    response = taxi_reposition.put(
        '/v1/settings/zones/item?zone=moscow',
        json={'parent_zone': '__default__'},
    )
    assert response.status_code == 200

    response = taxi_reposition.put('/v1/settings/zones/item?zone=svo', json={})
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

    actual_deviation_formulae = select_named(
        'SELECT * FROM config.deviation_formulae', pgsql['reposition'],
    )
    assert len(actual_deviation_formulae) == 2
    assert (
        actual_deviation_formulae[0]['zone_id']
        != actual_deviation_formulae[1]['zone_id']
    )
    del actual_deviation_formulae[0]['zone_id']
    del actual_deviation_formulae[1]['zone_id']
    assert actual_deviation_formulae[0] == actual_deviation_formulae[1]

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
def test_delete_non_existent(taxi_reposition):
    response = taxi_reposition.delete('/v1/settings/zones/item?zone=blah')
    assert response.status_code == 200


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
def test_delete(taxi_reposition, pgsql):
    response = taxi_reposition.delete(
        '/v1/settings/zones/item?zone=__default__',
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT zone_id FROM config.zones', pgsql['reposition'],
    )
    assert len(rows) == 0


@pytest.mark.parametrize('is_invalid_zone', [False, True])
def test_check_put(taxi_reposition, pgsql, load, is_invalid_zone):
    ZONE_TO_PUT = 'first' if is_invalid_zone else 'moscow'

    response = taxi_reposition.put(
        '/v1/settings/zones/item/check?zone={}'.format(ZONE_TO_PUT), json={},
    )

    if is_invalid_zone:
        assert response.status_code == 400
        assert response.json() == {
            'error': {'text': 'Zone \'first\' doesn\'t exist in geobase!'},
        }
    else:
        assert response.status_code == 200
        assert response.json() == {'data': {}}


@pytest.mark.pgsql('reposition', files=['zone_default.sql'])
@pytest.mark.parametrize(
    'parent_zone,status_code,response_json',
    [
        (
            'invalid',
            400,
            {
                'error': {
                    'text': (
                        'Parent zone \'invalid\' doesn\'t exist in geobase!'
                    ),
                },
            },
        ),
        (
            'moscow',
            400,
            {
                'error': {
                    'text': (
                        'Parent zone \'moscow\' to clone from doesn\'t exist!'
                    ),
                },
            },
        ),
        ('__default__', 200, {'data': {'parent_zone': '__default__'}}),
    ],
)
def test_check_put_with_parent(
        taxi_reposition, pgsql, parent_zone, status_code, response_json,
):
    response = taxi_reposition.put(
        '/v1/settings/zones/item/check?zone={}'.format('svo'),
        json={'parent_zone': parent_zone},
    )

    assert response.status_code == status_code
    assert response.json() == response_json


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['zone_moscow.sql'])
def test_check_delete(taxi_reposition, pgsql, load):
    response = taxi_reposition.delete(
        '/v1/settings/zones/item/check?zone={}'.format('moscow'),
    )

    assert response.status_code == 200
    assert response.json() == {'data': {}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'zone_moscow.sql', 'simple_check_rules.sql'],
)
def test_check_delete_with_dependent_settings(taxi_reposition, pgsql, load):
    response = taxi_reposition.delete(
        '/v1/settings/zones/item/check?zone={}'.format('moscow'),
    )

    assert response.status_code == 400
    assert response.json() == {
        'error': {
            'text': (
                'Zone moscow still has'
                ' 1 check rules,'
                ' 0 deviation formulae,'
                ' 0 forbidden zones,'
                ' 0 tags zones assignments'
            ),
        },
    }


@pytest.mark.config(REPOSITION_SETTINGS_2PC_ENABLED=True)
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('fail_services', [False, True])
@pytest.mark.parametrize('check', [False, False])
def test_2pc_put(
        taxi_reposition, pgsql, load, mockserver, fail_services, check,
):
    queries = [load('zone_moscow.sql')]
    pgsql['reposition'].apply_queries(queries)

    @mockserver.json_handler('/reposition_watcher/v1/admin/zones/item')
    def mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/zones/item')
    def mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_watcher/v1/admin/zones/item/check')
    def mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/zones/item/check')
    def mock_matcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    data = {'parent_zone': 'moscow'}
    check_part = '/check' if check else ''
    response = taxi_reposition.put(
        f'/v1/settings/zones/item{check_part}?zone=cao', json=data,
    )

    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'error': {
                'text': (
                    'Failed to set zone in reposition-watcher: '
                    'got BadRequestRepositionWatcherError '
                    'service RepositionWatcher error'
                ),
            },
        }
        return
    assert response.status_code == 200


@pytest.mark.config(REPOSITION_SETTINGS_2PC_ENABLED=True)
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.parametrize('fail_services', [False, True])
@pytest.mark.parametrize('check', [False, False])
def test_2pc_delete(
        taxi_reposition, pgsql, load, mockserver, fail_services, check,
):
    queries = [load('zone_moscow.sql')]
    pgsql['reposition'].apply_queries(queries)

    @mockserver.json_handler('/reposition_watcher/v1/admin/zones/item')
    def mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/zones/item')
    def mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_watcher/v1/admin/zones/item/check')
    def mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/zones/item/check')
    def mock_matcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    check_part = '/check' if check else ''
    response = taxi_reposition.delete(
        f'/v1/settings/zones/item{check_part}?zone=moscow',
    )
    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'error': {
                'text': (
                    'Failed to delete zone in reposition-watcher: '
                    'got BadRequestRepositionWatcherError '
                    'service RepositionWatcher error'
                ),
            },
        }
        return
    assert response.status_code == 200

    if not check:
        rows = select_table('config.zones', 'zone_id', pgsql['reposition'])
        assert rows == []
