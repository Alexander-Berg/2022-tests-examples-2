import pytest


TAXIMETER_CORE_RESPONSES = {
    'bad_request_token': {
        'status': 400,
        'json': {'error_code': '400', 'error': 'bad_request'},
    },
    'unauthorized_token': {
        'status': 401,
        'json': {'error_code': '401', 'error': 'unauthorized'},
    },
    'internal_error_token': {
        'status': 500,
        'json': {'error_code': '500', 'error': 'internal_error'},
    },
}


def make_dict_response(x, response_dict, content_type, default_response):
    resp = response_dict.get(x, default_response)
    resp['content_type'] = content_type
    return resp


def response_taximeter_core(token):
    return make_dict_response(
        token,
        TAXIMETER_CORE_RESPONSES,
        'application/json',
        {
            'status': 200,
            'json': {'park_id': 'some_park', 'driver_id': 'some_driver'},
        },
    )


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_commit_to_parks_false.json',
)
@pytest.mark.parametrize(
    'token, client_id, expected_code',
    [
        ('token1', 'selfreg-5a7581722016667706734a33', 200),
        ('unauthorized_token', 'selfreg-5a7581722016667706734a32', 401),
    ],
)
async def test_driver_create_old_way(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mongo,
        mock_fleet_parks,
        mock_tags,
        mock_taximeter_core,
        mock_client_notify,
        client_experiments3,
        token,
        client_id,
        expected_code,
):
    @mockserver.json_handler(
        '/driver-categories-api/internal/v2/allowed_driver_categories',
    )
    async def _mock_v2_allowed_driver_categories(request):
        return {'categories': ['courier', 'express', 'business', 'standart']}

    @mockserver.json_handler('/driver-categories-api/v2/driver/restrictions')
    async def _mock_v2_driver_restrictions(request):
        return {'categories': []}

    @mockserver.json_handler(
        '/driver-diagnostics/internal/driver-diagnostics/v1/categories'
        '/restrictions',
    )
    async def _mock_v1_categories_restrictions(request):
        return {
            'categories': [
                {'name': 'courier', 'is_enabled': True},
                {'name': 'express', 'is_enabled': False},
                {'name': 'business', 'is_enabled': False},
                {'name': 'standart', 'is_enabled': True},
            ],
        }

    @mock_taximeter_core('/selfreg/commit')
    async def _driver_selfreg_commit(request):
        await mongo.selfreg_profiles.update_one(
            {'token': token}, {'$set': {'is_committed': True}},
        )
        return mockserver.make_response(**response_taximeter_core(token))

    @mock_client_notify('/v1/unsubscribe')
    async def _del_token(request):
        assert request.method == 'POST'
        assert request.json == {
            'client': {'client_id': client_id},
            'service': 'taximeter',
        }
        return {}

    @mock_fleet_parks('/v1/parks/list')
    def _v1_parks_list(request):
        return {
            'parks': [
                {
                    'id': 'some_park',
                    'login': 'park_login',
                    'name': 'Sea',
                    'is_active': True,
                    'city_id': 'Gotham',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'cme',
                    'demo_mode': False,
                    'provider_config': {'type': 'none', 'clid': '555'},
                    'tz_offset': 5,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mock_tags('/v1/upload')
    def _v1_upload(request):
        body = request.json
        assert len(body['tags']) == 3
        return {}

    if expected_code == 200:
        profile = await mongo.selfreg_profiles.find_one({'token': token})
        assert 'is_committed' not in profile

    response = await taxi_selfreg.post(
        '/selfreg/v1/commit',
        params={'token': token},
        headers={'Content-Type': 'application/json'},
        json={},
    )
    assert response.status == expected_code

    if expected_code == 200:
        response_json = await response.json()
        assert response_json == {
            'park_id': 'some_park',
            'driver_id': 'some_driver',
        }
        assert _v1_parks_list.times_called == 1
        assert _v1_upload.times_called == 1
        assert _del_token.times_called == 1
        assert _driver_selfreg_commit.times_called == 1

        # check that other selfreg handles don't work with this profile anymore
        response = await taxi_selfreg.get(
            '/selfreg/v1/car', params={'token': token},
        )
        assert response.status == 401

        profile = await mongo.selfreg_profiles.find_one({'token': token})
        assert profile['is_committed']
    else:
        assert _v1_parks_list.times_called == 0
        assert _v1_upload.times_called == 0
        assert _del_token.times_called == 0


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_commit_to_parks_true.json',
)
async def test_driver_create_new_way(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mongo,
        mock_fleet_parks,
        mock_tags,
        mock_parks,
        mock_client_notify,
        client_experiments3,
):
    @mockserver.json_handler(
        '/driver-categories-api/internal/v2/allowed_driver_categories',
    )
    async def _mock_v2_allowed_driver_categories(request):
        return {'categories': ['courier', 'express', 'business', 'standart']}

    @mockserver.json_handler('/driver-categories-api/v2/driver/restrictions')
    async def _mock_v2_driver_restrictions(request):
        return {'categories': []}

    @mockserver.json_handler(
        '/driver-diagnostics/internal/driver-diagnostics/v1/categories'
        '/restrictions',
    )
    async def _mock_v1_categories_restrictions(request):
        return {
            'categories': [
                {'name': 'courier', 'is_enabled': True},
                {'name': 'express', 'is_enabled': False},
                {'name': 'business', 'is_enabled': False},
                {'name': 'standart', 'is_enabled': True},
            ],
        }

    @mock_parks('/internal/driver-profiles/create')
    async def _driver_parks_commit(request):
        return {
            'driver_profile': {
                'id': 'some_driver',
                'park_id': 'some_park',
                'first_name': 'L',
                'last_name': 'K',
                'hire_date': '2021-02-13',
                'phones': ['+70009325299'],
                'providers': ['park', 'yandex'],
                'work_status': 'working',
            },
        }

    @mock_client_notify('/v1/unsubscribe')
    async def _del_token(request):
        assert request.method == 'POST'
        assert request.json == {
            'client': {'client_id': 'selfreg-5a7581722016667706734a31'},
            'service': 'taximeter',
        }
        return {}

    @mock_fleet_parks('/v1/parks/list')
    def _v1_parks_list(request):
        return {
            'parks': [
                {
                    'id': 'some_park',
                    'login': 'park_login',
                    'name': 'Sea',
                    'is_active': True,
                    'city_id': 'Gotham',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'cme',
                    'demo_mode': False,
                    'provider_config': {'type': 'none', 'clid': '555'},
                    'tz_offset': 5,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mock_tags('/v1/upload')
    def _v1_upload(request):
        body = request.json
        assert len(body['tags']) == 3
        return {}

    profile = await mongo.selfreg_profiles.find_one({'token': 'token3'})
    assert 'is_committed' not in profile

    response = await taxi_selfreg.post(
        '/selfreg/v1/commit',
        params={'token': 'token3'},
        headers={'Content-Type': 'application/json'},
        json={},
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json == {
        'park_id': 'some_park',
        'driver_id': 'some_driver',
    }
    assert _v1_parks_list.times_called == 1
    assert _v1_upload.times_called == 1
    assert _del_token.times_called == 1
    assert _driver_parks_commit.times_called == 1

    profile = await mongo.selfreg_profiles.find_one({'token': 'token3'})
    assert profile['park_id'] == 'some_park'
    assert profile['driver_profile_id'] == 'some_driver'
    assert profile['is_committed']
