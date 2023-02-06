import copy

import pytest

from tests_fleet_orders_manager import common

ENDPOINT = 'fleet/fleet-orders-manager/v1/orders/draft'
REQUEST_BODY = {
    'class_id': 'econom',
    'phone_pd_id': 'id_+7123',
    'route': [{'geopoint': [1.0, 12.0]}, {'geopoint': [2.0, 13.0]}],
    'due': '2021-04-29T07:48:47.487+0000',
    'preorder_request_id': '93abc040204dfe',
    'forced_fixprice': '100.0',
    'performer_id': 'driver_id1',
    'comment': 'comment1',
}
COMPENSATIONS_DEFAULT = {'__default__': {'kind': 'percent', 'value': '5.00'}}
COMPENSATIONS_PARK_FIX = {
    '__default__': {'kind': 'percent', 'value': '5.00'},
    'park_id': {'kind': 'fix', 'value': '2.0000'},
}
EXPECTED_REQUEST = {
    'callcenter': {'personal_phone_id': 'id_+7123'},
    'class': ['econom'],
    'id': 'user_id_id_+7123',
    'parks': [],
    'payment': {'type': 'cash'},
    'requirements': {},
    'route': [
        {'fullname': 'point 0', 'geopoint': [1.0, 12.0]},
        {'fullname': 'point 1', 'geopoint': [2.0, 13.0]},
    ],
    'white_label_requirements': {
        'dispatch_requirement': 'only_source_park',
        'source_park_id': 'park_id',
        'forced_fixprice': 100.0,
    },
    'due': '2021-04-29T07:48:47.487+00:00',
    'preorder_request_id': '93abc040204dfe',
    'dispatch_type': 'forced_performer',
    'lookup_extra': {'performer_id': 'park_id_driver_id1', 'intent': 'yango'},
    'comment': 'comment1',
}


@pytest.fixture(name='orders_draft')
def _mock_orders_draft(mockserver):
    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _mock(request):
        return {'orderid': 'order_id'}

    return _mock


@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_PARK_FIX,
)
async def test_ok(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        orders_draft,
):
    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': 'order_id'}

    assert orders_draft.times_called == 1
    orders_draft_request = orders_draft.next_call()['request']
    expected = copy.deepcopy(EXPECTED_REQUEST)
    expected['white_label_requirements'].update(
        {'park_performer_compensation_fix': 2.0},
    )
    assert orders_draft_request.json == expected
    assert (
        orders_draft_request.headers['User-Agent']
        == 'whitelabel/superweb/label_id'
    )
    assert orders_draft_request.headers['Accept-Language'] == 'de'


ZONEINFO_MOCK_DEFAULT = {
    'max_tariffs': [
        {
            'class': 'econom',
            'name': 'Ökonom',
            'supported_requirements': [
                {
                    'label': 'Treffen mit dem Schild',
                    'name': 'meeting_arriving',
                    'type': 'boolean',
                },
                {
                    'label': 'Medizinischer Transport',
                    'name': 'medical_transport',
                    'type': 'boolean',
                },
            ],
        },
    ],
    'supported_feedback_choices': {'cancelled_reason': []},
    'tz': '+0300',
}


@pytest.mark.parametrize(
    'comment, requirements, int_api_requirements, result_comment',
    [
        (
            'order comment',
            [
                {
                    'id': 'meeting_arriving',
                    'type': 'text',
                    'text': 'Murtaza Gubaidulovich Rahimov',
                },
            ],
            {'meeting_arriving': True},
            'order comment\n'
            'Treffen mit dem Schild: Murtaza Gubaidulovich Rahimov.',
        ),
        (
            '',
            [
                {
                    'id': 'meeting_arriving',
                    'type': 'text',
                    'text': 'Murtaza Gubaidulovich Rahimov',
                },
            ],
            {'meeting_arriving': True},
            'Treffen mit dem Schild: Murtaza Gubaidulovich Rahimov.',
        ),
        (
            None,
            [
                {
                    'id': 'meeting_arriving',
                    'type': 'text',
                    'text': 'Murtaza Gubaidulovich Rahimov',
                },
            ],
            {'meeting_arriving': True},
            'Treffen mit dem Schild: Murtaza Gubaidulovich Rahimov.',
        ),
        (
            'order comment',
            [{'id': 'medical_transport', 'type': 'boolean'}],
            {'medical_transport': True},
            'order comment',
        ),
        (
            '',
            [{'id': 'medical_transport', 'type': 'boolean'}],
            {'medical_transport': True},
            '',
        ),
        (
            None,
            [{'id': 'medical_transport', 'type': 'boolean'}],
            {'medical_transport': True},
            '',
        ),
        (
            'order comment',
            [
                {
                    'id': 'meeting_arriving',
                    'type': 'text',
                    'text': 'Murtaza Gubaidulovich Rahimov',
                },
                {'id': 'medical_transport', 'type': 'boolean'},
            ],
            {'meeting_arriving': True, 'medical_transport': True},
            'order comment\n'
            'Treffen mit dem Schild: Murtaza Gubaidulovich Rahimov.',
        ),
    ],
)
@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_PARK_FIX,
)
async def test_ok_requirements(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        mockserver,
        orders_draft,
        comment,
        requirements,
        int_api_requirements,
        result_comment,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _zoneinfo_mock(request):
        assert request.json == {'point': [1.0, 12.0]}
        assert request.headers['Accept-Language'] == 'de'
        return ZONEINFO_MOCK_DEFAULT

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = copy.deepcopy(REQUEST_BODY)
    request['comment'] = comment
    request['requirements'] = requirements
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': 'order_id'}

    assert orders_draft.times_called == 1
    orders_draft_request = orders_draft.next_call()['request'].json

    assert orders_draft_request['requirements'] == int_api_requirements
    assert orders_draft_request['comment'] == result_comment


@pytest.mark.parametrize(
    'requirements, message_response',
    [
        (
            [
                {'id': 'medical_transport', 'type': 'boolean'},
                {'id': 'medical_transport', 'type': 'boolean'},
            ],
            'Duplicate requirements: medical_transport',
        ),
        (
            [
                {
                    'id': 'meeting_arriving',
                    'type': 'text',
                    'text': 'Murtaza Gubaidulovich Rahimov',
                },
                {
                    'id': 'meeting_arriving',
                    'type': 'text',
                    'text': 'Murtaza Gubaidulovich Rahimov',
                },
            ],
            'Duplicate requirements: meeting_arriving',
        ),
    ],
)
@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_PARK_FIX,
)
async def test_failed_requirements_duplicate_requirements(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        mockserver,
        orders_draft,
        requirements,
        message_response,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _zoneinfo_mock(request):
        assert request.json == {'point': [1.0, 12.0]}
        assert request.headers['Accept-Language'] == 'de'
        return ZONEINFO_MOCK_DEFAULT

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = copy.deepcopy(REQUEST_BODY)
    request['requirements'] = requirements
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'DUPLICATE_REQUIREMENTS',
        'message': message_response,
    }
    assert orders_draft.times_called == 0


@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_PARK_FIX,
)
async def test_failed_requirements_not_supported_requirements(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        mockserver,
        orders_draft,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _zoneinfo_mock(request):
        assert request.json == {'point': [1.0, 12.0]}
        assert request.headers['Accept-Language'] == 'de'
        return ZONEINFO_MOCK_DEFAULT

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = copy.deepcopy(REQUEST_BODY)
    request['requirements'] = [
        {'id': 'not_supported_requirement', 'type': 'boolean'},
    ]
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'NOT_SUPPORTED_REQUIREMENT',
        'message': (
            'Requirement not_supported_requirement is not suported '
            'in this zone and tariff'
        ),
    }
    assert orders_draft.times_called == 0


@pytest.mark.parametrize(
    'requirements, message_response',
    [
        (
            [{'id': 'medical_transport', 'type': 'text', 'text': 'text'}],
            'Invalid type of requirement medical_transport',
        ),
        (
            [
                {
                    'id': 'meeting_arriving',
                    'type': 'text',
                    'text': 'Murtaza Gubaidulovich Rahimov',
                },
                {'id': 'medical_transport', 'type': 'text', 'text': 'text,'},
            ],
            'Invalid type of requirement medical_transport',
        ),
        (
            [{'id': 'meeting_arriving', 'type': 'boolean'}],
            'Invalid type of requirement meeting_arriving',
        ),
        (
            [
                {'id': 'medical_transport', 'type': 'boolean'},
                {'id': 'meeting_arriving', 'type': 'boolean'},
            ],
            'Invalid type of requirement meeting_arriving',
        ),
    ],
)
@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_PARK_FIX,
)
async def test_failed_requirements_invalid_requirement_type(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        mockserver,
        orders_draft,
        requirements,
        message_response,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _zoneinfo_mock(request):
        assert request.json == {'point': [1.0, 12.0]}
        assert request.headers['Accept-Language'] == 'de'
        return ZONEINFO_MOCK_DEFAULT

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = copy.deepcopy(REQUEST_BODY)
    request['requirements'] = requirements
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'INVALID_REQUIREMENT_TYPE',
        'message': message_response,
    }
    assert orders_draft.times_called == 0


@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_PARK_FIX,
)
async def test_failed_requirements_tariff_not_found(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        mockserver,
        orders_draft,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _zoneinfo_mock(request):
        assert request.json == {'point': [1.0, 12.0]}
        assert request.headers['Accept-Language'] == 'de'
        return {
            'max_tariffs': [],
            'supported_feedback_choices': {'cancelled_reason': []},
            'tz': '+0300',
        }

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = copy.deepcopy(REQUEST_BODY)
    request['requirements'] = [{'id': 'medical_transport', 'type': 'boolean'}]
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'TARIFF_NOT_FOUND',
        'message': 'Tariff econom not found in zone',
    }
    assert orders_draft.times_called == 0


@pytest.mark.parametrize(
    'status, error_code',
    [
        (401, 'UNAUTHORIZED_ACCESS'),
        (404, 'ZONE_NOT_FOUND'),
        (429, 'TOO_MANY_REQUESTS'),
    ],
)
@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_PARK_FIX,
)
async def test_failed_requirements_int_api_errors(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        mockserver,
        orders_draft,
        status,
        error_code,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _zoneinfo_mock(request):
        assert request.json == {'point': [1.0, 12.0]}
        assert request.headers['Accept-Language'] == 'de'
        return mockserver.make_response(status=status)

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    request = copy.deepcopy(REQUEST_BODY)
    request['requirements'] = [{'id': 'medical_transport', 'type': 'boolean'}]
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {'code': error_code, 'message': error_code}
    assert orders_draft.times_called == 0


@pytest.mark.config(
    FLEET_ORDERS_MANAGER_PARK_PERFORMER_COMPENSATION=COMPENSATIONS_DEFAULT,
)
async def test_ok_default_compensation(
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        personal_phones_store,
        v1_profile,
        orders_draft,
):
    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': 'order_id'}

    assert orders_draft.times_called == 1
    orders_draft_request = orders_draft.next_call()['request']
    expected = copy.deepcopy(EXPECTED_REQUEST)
    expected['white_label_requirements'].update(
        {'park_performer_compensation_percent': 5.0},
    )
    assert orders_draft_request.json == expected
    assert (
        orders_draft_request.headers['User-Agent']
        == 'whitelabel/superweb/label_id'
    )
    assert orders_draft_request.headers['Accept-Language'] == 'de'


REQUEST_BODY_BAD_PRICE = {
    'phone_pd_id': 'id_+7123',
    'class_id': 'econom',
    'route': [{'geopoint': [1.0, 12.0]}, {'geopoint': [2.0, 13.0]}],
    'due': '2021-04-29T07:48:47.487+0000',
    'preorder_request_id': '93abc040204dfe',
    'forced_fixprice': 'non_numeric',
}


async def test_non_numeric_forced_fixprice(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
):
    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY_BAD_PRICE, headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'NON_NUMERIC_FORCED_FIXPRICE',
        'message': 'NON_NUMERIC_FORCED_FIXPRICE',
    }


@pytest.mark.parametrize(
    'orders_draft_response, expected_code, expected_body',
    [
        pytest.param(
            {'json': {'error': {'text': 'Not Acceptable'}}, 'status': 406},
            400,
            {
                'code': 'IMPOSSIBLE_REQUIREMENTS',
                'message': 'IMPOSSIBLE_REQUIREMENTS',
            },
            id='406',
        ),
        pytest.param(
            {'json': {}, 'status': 429},
            400,
            {
                'code': 'TOO_MANY_CONCURRENT_ORDERS',
                'message': 'TOO_MANY_CONCURRENT_ORDERS',
            },
            id='429',
        ),
    ],
)
async def test_4xx_from_draft(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        orders_draft_response,
        expected_code,
        expected_body,
):
    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _mock_orders_draft(request):
        return mockserver.make_response(**orders_draft_response)

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_body
