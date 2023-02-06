import datetime

import pytest

NOW = datetime.datetime(2019, 4, 9, 12, 35, 55, tzinfo=datetime.timezone.utc)
ONE_DAY_AGO = NOW - datetime.timedelta(days=1)
ONE_YEAR_AGO = NOW - datetime.timedelta(days=365)


# pylint: disable=too-many-arguments
@pytest.mark.config(TVM_ENABLED=True)
async def test_not_authorized(support_info_client):
    response = await support_info_client.get(
        '/v1/info/driver/park_id/driver_id',
        headers={'Content-Type': 'application/json; charset=utf-8'},
    )
    assert response.status == 403
    # utils.reformat_response made it
    assert await response.json() == {
        'error': (
            '{"status": "error", "message": "TVM header missing", '
            '"code": "tvm-auth-error"}'
        ),
        'status': 'error',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(
    client_messages={
        'feedback_choice.badge_label.comfort_ride': {
            'ru': 'комфорт',
            'en': 'сomfort',
        },
        'feedback_choice.badge_label.mood': {'ru': 'настроение', 'en': 'mood'},
    },
)
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'filters': {},
                'label': 'feedback_choice.badge_label.comfort_ride',
                'name': 'comfort_ride',
            },
            {
                'filters': {},
                'label': 'feedback_choice.badge_label.mood',
                'name': 'mood',
            },
            {
                'filters': {},
                'label': 'feedback_choice.badge_label.music',
                'name': 'music',
            },
        ],
        'feedback_rating_mapping': [],
    },
)
@pytest.mark.parametrize(
    [
        'park_id',
        'driver_id',
        'driver_license',
        'profiles_request',
        'profiles_response',
        'orders_requests',
        'orders_responses',
        'expected_code',
        'expected_result',
    ],
    [
        (
            'park_id',
            'driver_id',
            '1234',
            {
                'id_in_set': ['park_id_driver_id'],
                'projection': [
                    'data.license_driver_birth_date',
                    'data.license',
                ],
            },
            {'profiles': []},
            [],
            [],
            404,
            {},
        ),
        (
            'park_id',
            'driver_id',
            '12345',
            {
                'id_in_set': ['park_id_driver_id'],
                'projection': [
                    'data.license_driver_birth_date',
                    'data.license',
                ],
            },
            {
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_id_driver_id',
                        'data': {
                            'license_driver_birth_date': (
                                '1970-01-15T06:56:07.000'
                            ),
                            'license': {'pd_id': 'pd_id', 'country': 'rus'},
                        },
                    },
                ],
            },
            [],
            [],
            404,
            {},
        ),
        (
            'park_id',
            'driver_id',
            '1234',
            {
                'id_in_set': ['park_id_driver_id'],
                'projection': [
                    'data.license_driver_birth_date',
                    'data.license',
                ],
            },
            {
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_id_driver_id',
                        'data': {
                            'license_driver_birth_date': (
                                '1970-01-15T06:56:07.000'
                            ),
                            'license': {'pd_id': 'pd_id', 'country': 'rus'},
                        },
                    },
                ],
            },
            [
                {
                    'query': {
                        'park': {
                            'id': 'park_id',
                            'order': {
                                'booked_at': {
                                    'from': '2019-03-10T15:35:55+0300',
                                    'to': '2019-04-09T15:35:55+0300',
                                },
                            },
                            'driver_profile': {'id': 'driver_id'},
                        },
                    },
                    'limit': 500,
                },
            ],
            [
                {
                    'orders': [{'id': 'order_id'}, {'id': 'order_id'}],
                    'limit': 500,
                    'cursor': 'cursor_id',
                },
            ],
            200,
            {
                'driver': {
                    'general': {
                        'birth_date': '1970-01-15T06:56:07.000',
                        'license_issue_country': 'rus',
                        'total_orders': 25,
                        'monthly_orders': 2,
                    },
                    'support': {
                        'badges': [
                            {
                                'badge_key': 'comfort_ride',
                                'badge_name': 'комфорт',
                                'count': 25,
                            },
                            {
                                'badge_key': 'mood',
                                'badge_name': 'настроение',
                                'count': 10,
                            },
                            {
                                'badge_key': 'music',
                                'badge_name': 'music',
                                'count': 15,
                            },
                        ],
                    },
                },
            },
        ),
        (
            'park_id',
            'driver_id',
            '123',
            {
                'id_in_set': ['park_id_driver_id'],
                'projection': [
                    'data.license_driver_birth_date',
                    'data.license',
                ],
            },
            {
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_id_driver_id',
                        'data': {
                            'license_driver_birth_date': (
                                '1970-01-15T06:56:07.000'
                            ),
                            'license': {'pd_id': 'pd_id', 'country': 'rus'},
                        },
                    },
                ],
            },
            [
                {
                    'query': {
                        'park': {
                            'id': 'park_id',
                            'order': {
                                'booked_at': {
                                    'from': '2019-03-10T15:35:55+0300',
                                    'to': '2019-04-09T15:35:55+0300',
                                },
                            },
                            'driver_profile': {'id': 'driver_id'},
                        },
                    },
                    'limit': 500,
                },
                {
                    'query': {
                        'park': {
                            'id': 'park_id',
                            'order': {
                                'booked_at': {
                                    'from': '2019-03-10T15:35:55+0300',
                                    'to': '2019-04-09T15:35:55+0300',
                                },
                            },
                            'driver_profile': {'id': 'driver_id'},
                        },
                    },
                    'limit': 500,
                    'cursor': 'cursor_id',
                },
            ],
            [
                {
                    'orders': [{'id': 'order_id'} for i in range(500)],
                    'limit': 500,
                    'cursor': 'cursor_id',
                },
                {
                    'orders': [{'id': 'order_id'} for i in range(10)],
                    'limit': 500,
                    'cursor': 'cursor_id',
                },
            ],
            200,
            {
                'driver': {
                    'general': {
                        'birth_date': '1970-01-15T06:56:07.000',
                        'license_issue_country': 'rus',
                        'total_orders': 0,
                        'monthly_orders': 510,
                    },
                    'support': {
                        'badges': [
                            {
                                'badge_key': 'mood',
                                'badge_name': 'настроение',
                                'count': 25,
                            },
                        ],
                    },
                },
            },
        ),
    ],
)
async def test_driver_info(
        mock_personal_single_response,
        support_info_client,
        park_id,
        driver_id,
        driver_license,
        profiles_request,
        profiles_response,
        orders_requests,
        orders_responses,
        expected_code,
        expected_result,
        mockserver,
):
    @mockserver.json_handler('driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert request.json == profiles_request
        return profiles_response

    orders_counter = 0

    @mockserver.json_handler('driver-orders/v1/parks/orders/list')
    def _driver_orders(request):
        nonlocal orders_counter
        assert request.json == orders_requests[orders_counter]
        orders_response = orders_responses[orders_counter]
        orders_counter += 1
        return orders_response

    mock_personal_single_response(driver_license)
    response = await support_info_client.get(
        '/v1/info/driver/{}/{}'.format(park_id, driver_id),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Ya-Service-Ticket': 'TVM_key',
        },
    )
    assert response.status == expected_code
    if expected_code == 200:
        result = await response.json()
        result['driver']['support']['badges'] = sorted(
            result['driver']['support']['badges'],
            key=lambda v: v['badge_key'],
        )
        assert result == expected_result
