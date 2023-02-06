import dateutil
import pytest


NOW = '2020-01-01T20:00:00+03:00'

PARKS_REQ_FIELDS = {
    'driver_profile': ['id', 'last_name', 'first_name', 'middle_name'],
}
PARKS_REQ_SORT_ORDER = [
    {'direction': 'asc', 'field': 'driver_profile.last_name'},
    {'direction': 'asc', 'field': 'driver_profile.first_name'},
    {'direction': 'asc', 'field': 'driver_profile.middle_name'},
]


async def test_get_contractor_rule_list__empty(fleet_v2, mock_api):
    response = await fleet_v2.get_contractor_rule_list(park_id='PARK-XX')
    assert response.status_code == 200, response.text
    assert response.json() == {'items': []}

    mock = mock_api['parks']['/driver-profiles/list']
    assert mock.times_called == 1
    json = mock.next_call()['request'].json
    assert json == {
        'fields': PARKS_REQ_FIELDS,
        'offset': 0,
        'limit': 250,
        'query': {'park': {'id': 'PARK-XX'}},
        'sort_order': PARKS_REQ_SORT_ORDER,
    }


async def test_get_contractor_rule_list__default(fleet_v2, mock_api):
    response = await fleet_v2.get_contractor_rule_list(
        park_id='PARK-01', cursor='1', limit=3,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {
                'contractor_id': 'CONTRACTOR-02',
                'contractor_name': {
                    'first': 'Contractor 2',
                    'middle': '',
                    'last': '',
                },
            },
            {
                'contractor_id': 'CONTRACTOR-03',
                'contractor_name': {
                    'first': 'Contractor 3',
                    'middle': '',
                    'last': '',
                },
                'rule_id': '00000000-0000-0000-0000-000000000001',
                'rule_name': 'Rule 1',
            },
            {
                'contractor_id': 'CONTRACTOR-04',
                'contractor_name': {
                    'first': 'Contractor 4',
                    'middle': '',
                    'last': '',
                },
            },
        ],
        'next_cursor': '4',
    }

    mock = mock_api['parks']['/driver-profiles/list']
    assert mock.times_called == 1
    json = mock.next_call()['request'].json
    assert json == {
        'fields': PARKS_REQ_FIELDS,
        'offset': 1,
        'limit': 3,
        'query': {'park': {'id': 'PARK-01'}},
        'sort_order': PARKS_REQ_SORT_ORDER,
    }


async def test_get_contractor_rule_list__inclusive(fleet_v2, mock_api):
    response = await fleet_v2.get_contractor_rule_list(
        park_id='PARK-01',
        cursor='1',
        limit=1,
        rule_id='00000000-0000-0000-0000-000000000001',
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {
                'contractor_id': 'CONTRACTOR-03',
                'contractor_name': {
                    'first': 'Contractor 3',
                    'middle': '',
                    'last': '',
                },
                'rule_id': '00000000-0000-0000-0000-000000000001',
                'rule_name': 'Rule 1',
            },
        ],
    }

    mock = mock_api['parks']['/driver-profiles/list']
    assert mock.times_called == 1
    json = mock.next_call()['request'].json
    assert json == {
        'fields': PARKS_REQ_FIELDS,
        'offset': 1,
        'limit': 1,
        'query': {
            'park': {
                'id': 'PARK-01',
                'driver_profile': {'id': ['CONTRACTOR-01', 'CONTRACTOR-03']},
            },
        },
        'sort_order': PARKS_REQ_SORT_ORDER,
    }


@pytest.mark.now(NOW)
async def test_set_contractor_rule__set(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.set_contractor_rule(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-05',
        json={'rule_id': '00000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 204, response.text

    mock = mock_api['driver-profiles']['/v1/driver/profiles/retrieve']
    assert mock.times_called == 1

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_contractor_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule_target': {
            **pg_initial['rule_target'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-05',
                False,
            ),
        },
        'rule_target_change_log': {
            **pg_initial['rule_target_change_log'],
            (1, 0): (1, dateutil.parser.parse(NOW), None, False),
        },
    }


@pytest.mark.now(NOW)
async def test_set_contractor_rule__reset(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.set_contractor_rule(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-01',
        json={'rule_id': '00000000-0000-0000-0000-000000000002'},
    )
    assert response.status_code == 204, response.text

    mock = mock_api['driver-profiles']['/v1/driver/profiles/retrieve']
    assert mock.times_called == 1

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_contractor_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule_target': {
            **pg_initial['rule_target'],
            101: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-01',
                True,
            ),
            102: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000002',
                'CONTRACTOR-01',
                False,
            ),
        },
        'rule_target_change_log': {
            **pg_initial['rule_target_change_log'],
            (101, 1): (1, dateutil.parser.parse(NOW), False, True),
            (102, 1): (1, dateutil.parser.parse(NOW), True, False),
        },
    }


@pytest.mark.now(NOW)
async def test_set_contractor_rule__unset(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.set_contractor_rule(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-01',
        json={'rule_id': None},
    )
    assert response.status_code == 204, response.text

    mock = mock_api['driver-profiles']['/v1/driver/profiles/retrieve']
    assert mock.times_called == 1

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_contractor_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule_target': {
            **pg_initial['rule_target'],
            101: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                'CONTRACTOR-01',
                True,
            ),
        },
        'rule_target_change_log': {
            **pg_initial['rule_target_change_log'],
            (101, 1): (1, dateutil.parser.parse(NOW), False, True),
        },
    }


@pytest.mark.now(NOW)
async def test_set_contractor_rule__idempotency(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.set_contractor_rule(
        park_id='PARK-01',
        contractor_id='CONTRACTOR-01',
        json={'rule_id': '00000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 204, response.text

    mock = mock_api['driver-profiles']['/v1/driver/profiles/retrieve']
    assert mock.times_called == 1

    assert pg_dump() == pg_initial, 'Nothing was expected to change'
