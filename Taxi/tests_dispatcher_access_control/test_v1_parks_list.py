import pytest

from testsuite.utils import ordered_object

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/users/parks/list'

TEST_YANDEX_PARAMS = [{}, {'query': {}}, {'query': {'park': {}}}]


@pytest.mark.redis_store(
    [
        'hmset',
        'USER:BYUID:100',
        {'park_valid1': 'user1', 'park_valid2': 'user2'},
    ],
)
@pytest.mark.parametrize('payload', TEST_YANDEX_PARAMS)
async def test_yandex_valid(
        taxi_dispatcher_access_control, blackbox_service, payload,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={
            'X-Ya-User-Ticket': 'ticket_valid1',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    expected_response = {'parks': ['park_valid1', 'park_valid2']}

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_response, ['parks'])


@pytest.mark.redis_store(
    [
        'hmset',
        'USER:BYUID:100',
        {
            'park_valid1': 'user1',
            'park_valid2': 'user2',
            'park_valid3': 'user3',
        },
    ],
)
async def test_with_ids(taxi_dispatcher_access_control, blackbox_service):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    payload = {'query': {'park': {'ids': ['park_valid2']}}}

    expected_response = {'parks': ['park_valid2']}

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={
            'X-Ya-User-Ticket': 'ticket_valid1',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_response, ['parks'])


TEST_YANDEX_TEAM_PARAMS = [
    (
        {'query': {'park': {'ids': ['park_valid1']}}},
        {'parks': ['park_valid1']},
    ),
]


@pytest.mark.parametrize('payload, expected_response', TEST_YANDEX_TEAM_PARAMS)
async def test_yandex_team_valid(
        taxi_dispatcher_access_control,
        blackbox_service,
        payload,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={
            'X-Ya-User-Ticket': 'ticket_valid1',
            'X-Ya-User-Ticket-Provider': 'yandex_team',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == 200
    assert response.json() == expected_response


async def test_ticket_invalid(
        taxi_dispatcher_access_control, blackbox_service,
):
    payload = {'query': {'park': {}}}

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={
            'X-Ya-User-Ticket': 'ticket_invalid1',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'User ticket is invalid',
    }


async def test_yteam_empty_ids(
        taxi_dispatcher_access_control, blackbox_service,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    payload = {'query': {'park': {}}}

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={
            'X-Ya-User-Ticket': 'ticket_valid1',
            'X-Ya-User-Ticket-Provider': 'yandex_team',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Not supported empty ids for yandex team',
    }


TEST_INVALID_PARAMS = [
    (
        {'query': {'park': {'ids': []}}},
        {
            'code': '400',
            'message': (
                'Value of \'query.park.ids\': incorrect size,'
                ' must be 1 (limit) <= 0 (value)'
            ),
        },
    ),
    (
        {'query': {'park': {'ids': ['park_valid1', 'park_valid2']}}},
        {
            'code': '400',
            'message': (
                'Value of \'query.park.ids\': incorrect size,'
                ' must be 1 (limit) >= 2 (value)'
            ),
        },
    ),
    (
        {'query': {'park': {'ids': ['']}}},
        {
            'code': '400',
            'message': (
                'Value of \'query.park.ids[0]\': incorrect size, '
                'must be 1 (limit) <= 0 (value)'
            ),
        },
    ),
]


@pytest.mark.parametrize('payload, expected_response', TEST_INVALID_PARAMS)
async def test_empty_ids(
        taxi_dispatcher_access_control,
        blackbox_service,
        payload,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', uid='100', login='test1',
    )

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={
            'X-Ya-User-Ticket': 'ticket_valid1',
            'X-Ya-User-Ticket-Provider': 'yandex_team',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'
