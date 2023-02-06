import pytest

from tests_fleet_tutorials import utils

ENDPOINT = '/v1/groups/tutorials/list'
FLEET_ENDPOINT = '/fleet/tutorials/v1/groups/tutorials/list'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]


def build_params(endpoint, group_id, park_id='park_id_1'):
    params = {'group_id': group_id}
    if endpoint == ENDPOINT:
        params['park_id'] = park_id
    return params


def build_headers(endpoint, park_id='park_id_1', headers=None):
    if headers is None:
        headers = utils.HEADERS
    if endpoint == ENDPOINT:
        return headers
    return {**headers, 'X-Park-ID': park_id}


OK_PARAMS = [
    (
        'group_1',
        [
            {
                'description': 'description_1',
                'params': {'color': 'color_1', 'icon': 'icon_1'},
                'title': 'title_1',
                'tutorial_id': 'tutorial_1',
            },
        ],
    ),
    (
        'group_2',
        [
            {
                'description': 'description_2_1',
                'params': {'color': 'color_2_1', 'icon': 'icon_2_1'},
                'title': 'title_2_1',
                'tutorial_id': 'tutorial_2_1',
            },
        ],
    ),
    ('group_3', []),
]


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('group_id, expected_tutorials', OK_PARAMS)
async def test_ok(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
        group_id,
        expected_tutorials,
):
    response = await taxi_fleet_tutorials.get(
        endpoint,
        params=build_params(endpoint=endpoint, group_id=group_id),
        headers=build_headers(endpoint=endpoint),
    )

    assert response.status_code == 200
    assert response.json() == {'tutorials': expected_tutorials}


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_park_not_found(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
):
    mock_feeds.set_feeds([])

    response = await taxi_fleet_tutorials.get(
        endpoint,
        params=build_params(
            endpoint=endpoint, park_id='invalid', group_id='group_1',
        ),
        headers=build_headers(endpoint=endpoint, park_id='invalid'),
    )

    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Park not found'}


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_group_not_found(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
):
    mock_feeds.set_feeds([])

    response = await taxi_fleet_tutorials.get(
        endpoint,
        params=build_params(endpoint=endpoint, group_id='invalid'),
        headers=build_headers(endpoint=endpoint),
    )

    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Group not found'}


BAD_HEADERS_PARAMS = [
    (
        {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
        401,
        {
            'code': '401',
            'message': 'missing or empty X-Ya-User-Ticket-Provider header',
        },
    ),
    (
        {
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
        403,
        {'code': '403', 'message': 'missing or empty X-Yandex-UID header'},
    ),
]


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize(
    'bad_headers, expected_code, expected_response', BAD_HEADERS_PARAMS,
)
async def test_no_user_ticket(
        taxi_fleet_tutorials,
        endpoint,
        bad_headers,
        expected_code,
        expected_response,
):

    response = await taxi_fleet_tutorials.get(
        endpoint,
        params=build_params(endpoint=endpoint, group_id='group_1'),
        headers=build_headers(endpoint=endpoint, headers=bad_headers),
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response
