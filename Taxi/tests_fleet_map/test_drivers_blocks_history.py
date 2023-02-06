import pytest

ENDPOINT = '/fleet/map/v1/drivers/blocks-history'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park_id1',
}

SERVICE_REQUEST = {'driver_id': 'driver_id1'}

EMPTY_BLOCKLIST_RESPONSE = {'events': [], 'blocks': {}}  # type: dict

BLOCKLIST_RESPONSE_1 = {
    'events': [
        {
            'block_id': 'block_id1',
            'entity_id': 'trother555',
            'entity_name': 'Blacklist(Old)',
            'entity_type': 'support',
            'action': 'add',
            'created': '2021-12-01T14:40:20.936177+00:00',
            'comment': 'PARK_ID BLOCK_2',
        },
        {
            'block_id': 'block_id2',
            'entity_name': 'driver-work-modes',
            'entity_type': 'service',
            'action': 'add',
            'created': '2021-12-02T13:19:36.142574+00:00',
            'comment': '',
        },
        {
            'block_id': 'block_id2',
            'entity_name': 'driver-work-modes',
            'entity_type': 'service',
            'action': 'add',
            'created': '2021-12-02T13:24:36.142574+00:00',
            'comment': '',
        },
        {
            'block_id': 'block_id2',
            'entity_name': 'driver-work-modes',
            'entity_type': 'service',
            'action': 'remove',
            'created': '2021-12-02T15:19:36.142574+00:00',
            'comment': '',
        },
        {
            'block_id': 'block_id2',
            'entity_name': 'driver-work-modes',
            'entity_type': 'service',
            'action': 'remove',
            'created': '2021-12-02T15:24:36.142574+00:00',
            'comment': '',
        },
    ],
    'blocks': {
        'block_id1': {
            'block_id': 'block_id1',
            'predicate_id': '9b3294fe-ea19-471c-890e-1977a18f0a61',
            'kwargs': {'park_id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'},
            'status': 'inactive',
            'meta': {
                'Old_Ticket': 'dasd',
                'park_id': '7ad36bc7560449998acbe2c57a75c293',
                'Old_Date': '2020-10-03T10:53:37Z',
            },
            'till': '2021-12-02T14:41:03.172312+00:00',
            'text': 'Доступ к заказам ограничен',
            'designation': 'blocklist_predicate_designation_default',
            'mechanics': 'taximeter',
        },
        'block_id2': {
            'block_id': 'block_id2',
            'predicate_id': '44444444-4444-4444-4444-444444444444',
            'kwargs': {
                'park_id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                'license_id': '4d9e36f93d9e41b28b01703d453a1a15',
            },
            'status': 'inactive',
            'text': 'Временно заблокирован парком',
            'designation': 'park_license_id',
            'till': '2021-02-15T13:49:32+00:00',
            'mechanics': 'yango_temporary_block',
        },
    },
    'cursor': 'some_cursor',
}

BLOCKLIST_RESPONSE_2 = {
    'events': [
        {
            'block_id': 'block_id3',
            'entity_name': 'driver-work-modes',
            'entity_type': 'service',
            'action': 'add',
            'created': '2021-12-02T20:19:36.142574+00:00',
            'comment': '',
        },
        {
            'block_id': 'block_id4',
            'entity_name': 'driver-work-modes',
            'entity_type': 'service',
            'action': 'add',
            'created': '2021-12-01T10:19:36.142574+00:00',
            'comment': '',
        },
        {
            'block_id': 'block_id5',
            'entity_name': 'driver-work-modes',
            'entity_type': 'service',
            'action': 'add',
            'created': '2021-11-01T10:19:36.142574+00:00',
            'comment': '',
        },
    ],
    'blocks': {
        'block_id3': {
            'block_id': 'block_id3',
            'predicate_id': '44444444-4444-4444-4444-444444444444',
            'kwargs': {
                'park_id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                'license_id': '4d9e36f93d9e41b28b01703d453a1a15',
            },
            'status': 'active',
            'text': 'Временно заблокирован парком',
            'designation': 'park_license_id',
            'mechanics': 'block_mechanics_1',
        },
        'block_id4': {
            'block_id': 'block_id4',
            'predicate_id': '44444444-4444-4444-4444-444444444444',
            'kwargs': {
                'park_id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                'license_id': '4d9e36f93d9e41b28b01703d453a1a15',
            },
            'status': 'active',
            'text': 'Временно заблокирован парком',
            'designation': 'park_license_id',
            'till': '2021-12-15T13:49:32+00:00',
            'mechanics': 'block_mechanics_2',
        },
        'block_id5': {
            'block_id': 'block_id5',
            'predicate_id': '44444444-4444-4444-4444-444444444444',
            'kwargs': {
                'park_id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                'license_id': '4d9e36f93d9e41b28b01703d453a1a15',
            },
            'status': 'active',
            'text': 'Временно заблокирован парком',
            'designation': 'park_license_id',
            'till': '2021-11-15T13:49:32+00:00',
            'mechanics': 'block_mechanics_2',
        },
    },
}


@pytest.mark.now('2021-12-03T13:34:26+00:00')
@pytest.mark.parametrize(
    ['empty_blocklist_response', 'expected_response'],
    [
        pytest.param(True, {'items': []}),
        pytest.param(
            False,
            {
                'items': [
                    {
                        'from': '2021-12-01T10:19:36.142574+00:00',
                        'to': '2021-12-15T13:49:32+00:00',
                    },
                ],
            },
        ),
        pytest.param(
            False,
            {
                'items': [
                    {
                        'from': '2021-12-02T13:19:36.142574+00:00',
                        'to': '2021-12-02T15:19:36.142574+00:00',
                    },
                ],
            },
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['yango_temporary_block'],
            ),
        ),
        pytest.param(
            False,
            {
                'items': [
                    {
                        'from': '2021-12-01T14:40:20.936177+00:00',
                        'to': '2021-12-02T15:19:36.142574+00:00',
                    },
                ],
            },
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=[
                    'yango_temporary_block',
                    'taximeter',
                ],
            ),
        ),
        pytest.param(
            False,
            {'items': []},
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['non_existing_mechanics'],
            ),
        ),
        pytest.param(
            False,
            {
                'items': [
                    {
                        'from': '2021-12-01T14:40:20.936177+00:00',
                        'to': '2021-12-02T15:19:36.142574+00:00',
                    },
                    {'from': '2021-12-02T20:19:36.142574+00:00'},
                ],
            },
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=[
                    'yango_temporary_block',
                    'taximeter',
                    'block_mechanics_1',
                ],
            ),
        ),
    ],
)
async def test_blocks_history(
        taxi_fleet_map,
        mockserver,
        empty_blocklist_response,
        expected_response,
):
    @mockserver.json_handler(
        '/blocklist/admin/blocklist/v1/contractor/blocks/history',
    )
    def _events(request):
        assert request.json in [
            {'park_contractor_profile_id': 'park_id1_driver_id1'},
            {
                'cursor': 'some_cursor',
                'park_contractor_profile_id': 'park_id1_driver_id1',
            },
        ]
        if empty_blocklist_response:
            return EMPTY_BLOCKLIST_RESPONSE
        return (
            BLOCKLIST_RESPONSE_2
            if 'cursor' in request.json.keys()
            else BLOCKLIST_RESPONSE_1
        )

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == expected_response
