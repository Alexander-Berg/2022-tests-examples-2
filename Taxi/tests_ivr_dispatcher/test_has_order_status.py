import pytest

from tests_ivr_dispatcher import utils


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
@pytest.mark.parametrize('has_order', [False, True])
async def test_has_order_status(
        taxi_ivr_dispatcher,
        mock_personal,
        mock_user_api,
        mock_int_authproxy,
        mockserver,
        has_order,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        if has_order:
            return {
                'orders': [
                    {
                        'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                        'status': 'driving',
                    },
                ],
            }

        return {'orders': []}

    request = {
        'call_guid': 'some_call_guid',
        'origin_called_number': utils.DEFAULT_TAXI_PHONE,
        'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
    }

    response = await taxi_ivr_dispatcher.post(
        '/has_order_status', json=request,
    )

    assert response.status == 200
    assert response.json() == {'has_order_status': has_order}


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': 'arm_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
async def test_has_order_application_prohibition(
        taxi_ivr_dispatcher,
        mock_personal,
        mock_user_api,
        mock_int_authproxy,
        mockserver,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == 'arm_call_center'
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    request = {
        'call_guid': 'some_call_guid',
        'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
        'origin_called_number': utils.DEFAULT_TAXI_PHONE,
    }
    response = await taxi_ivr_dispatcher.post(
        '/has_order_status', json=request,
    )

    assert response.status == 200
    assert response.json() == {'has_order_status': False}


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
@pytest.mark.parametrize(
    'status', ['driving', 'search', 'transporting', 'waiting'],
)
async def test_different_statuses(
        taxi_ivr_dispatcher,
        mock_int_authproxy,
        mock_user_api,
        mock_personal,
        mockserver,
        status,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': status,
                },
            ],
        }

    request = {
        'call_guid': 'some_call_guid',
        'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
        'origin_called_number': utils.DEFAULT_TAXI_PHONE,
    }
    response = await taxi_ivr_dispatcher.post(
        '/has_order_status', json=request,
    )

    assert response.status == 200
    assert response.json() == {'has_order_status': True}


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
@pytest.mark.parametrize(
    'user_api_user_id', [utils.DEFAULT_USER_ID, 'other_user_id', None, 'fail'],
)
async def test_user_api_int_api_difference(
        taxi_ivr_dispatcher,
        mock_personal,
        mock_user_api,
        mock_int_authproxy,
        mockserver,
        user_api_user_id,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_users_search(request, *args, **kwargs):
        if user_api_user_id is None:
            return {'items': []}
        if user_api_user_id == 'fail':
            return mockserver.make_response(status=500)
        return {'items': [{'id': user_api_user_id}]}

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_orders_search(request, *args, **kwargs):
        # Assert use user_id from int-api/v1/profile
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    request = {
        'call_guid': 'some_call_guid',
        'origin_called_number': utils.DEFAULT_TAXI_PHONE,
        'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
    }

    response = await taxi_ivr_dispatcher.post(
        '/has_order_status', json=request,
    )

    assert response.status == 200
    assert response.json() == {'has_order_status': True}


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': '7220_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
async def test_with_another_application(
        taxi_ivr_dispatcher,
        mock_personal,
        mock_user_api,
        mock_int_authproxy,
        mockserver,
):
    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _mock_profile(request, *args, **kwargs):
        assert request.headers.get('User-Agent') == '7220_call_center'
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': 'Name',
            'personal_phone_id': request.json['user']['personal_phone_id'],
            'user_id': utils.DEFAULT_USER_ID,
        }

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        assert request.json['applications'] == ['7220_call_center']
        return {
            'items': [
                {
                    'id': utils.DEFAULT_USER_ID,
                    'created': '2020-08-19T13:30:44.388+0000',
                    'updated': '2020-08-19T13:30:44.4+0000',
                    'phone_id': utils.DEFAULT_PHONE_ID,
                    'application': utils.DEFAULT_APPLICATION,
                    'application_version': '1',
                },
            ],
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == '7220_call_center'
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    request = {
        'call_guid': 'some_call_guid',
        'origin_called_number': utils.DEFAULT_TAXI_PHONE,
        'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
    }

    response = await taxi_ivr_dispatcher.post(
        '/has_order_status', json=request,
    )

    assert response.status == 200
    assert response.json() == {'has_order_status': True}


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
)
@pytest.mark.parametrize(
    'choose_user_api',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                IVR_DISPATCHER_CHOOSE_SERVICE_FOR_USER_ID=False,
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                IVR_DISPATCHER_CHOOSE_SERVICE_FOR_USER_ID=True,
            ),
        ),
    ],
)
async def test_choose_user_id_service_config(
        taxi_ivr_dispatcher,
        mock_personal,
        mock_user_api,
        mock_int_authproxy,
        mockserver,
        choose_user_api,
):
    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _mock_profile(request, *args, **kwargs):
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': 'Name',
            'personal_phone_id': request.json['user']['personal_phone_id'],
            'user_id': 'user_id_from_int-api',
        }

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        return {
            'items': [
                {
                    'id': 'user_id_from_user-api',
                    'created': '2020-08-19T13:30:44.388+0000',
                    'updated': '2020-08-19T13:30:44.4+0000',
                    'phone_id': utils.DEFAULT_PHONE_ID,
                    'application': utils.DEFAULT_APPLICATION,
                    'application_version': '1',
                },
            ],
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        if request.json['user']['user_id'] == 'user_id_from_user-api':
            return {
                'orders': [
                    {
                        'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                        'status': 'driving',
                    },
                ],
            }
        assert request.json['user']['user_id'] == 'user_id_from_int-api'
        return {'orders': []}

    request = {
        'call_guid': 'some_call_guid',
        'origin_called_number': utils.DEFAULT_TAXI_PHONE,
        'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
    }

    response = await taxi_ivr_dispatcher.post(
        '/has_order_status', json=request,
    )

    assert response.status == 200
    assert response.json() == {'has_order_status': choose_user_api}
