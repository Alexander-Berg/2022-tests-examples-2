import pytest

PARK_ID = 'park_1'
DRIVER_ID = 'driver_uuid1'
DRIVER_ID_2 = 'driver_uuid2'
DRIVER_NO_EXP = 'driver_no_exp'

SELFREG_ID = 'selfreg_1'
SELFREG_PHONE = 'selfreg_phone'

POSITION_MOSCOW = {'lon': 37.590533, 'lat': 55.733863}
POSITION_MINSK = {'lon': 27.561481, 'lat': 53.902512}

VERSION_OLD_ICON = '9.56 (1234)'
VERSION_NEW_ICON = '9.57 (1234)'  # supports 'title_icon' type

SELFREG_DEEPLINK_KEY = (
    'onboarding.promo_guarantees.final_motivation.button_enter_info.deeplink'
)
SELFREG_DEEPLINK_PATH = 'screen/selfreg_start_profile_filling'

DEFAULT_HEADERS = {
    'Accept-Language': 'ru',
    'X-Request-Application': 'taximeter',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


def prepare_headers(
        park_id, driver_id, *, new_icon=False, is_uberdriver=False,
):
    result = dict(DEFAULT_HEADERS)

    result['X-YaTaxi-Park-Id'] = park_id
    result['X-YaTaxi-Driver-Profile-Id'] = driver_id
    result['X-Request-Application-Version'] = (
        VERSION_NEW_ICON if new_icon else VERSION_OLD_ICON
    )
    if is_uberdriver:
        result['X-Request-Application'] = 'uberdriver'
        result['X-Request-Version-Type'] = 'uber'
    return result


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'disabled': [],
            'feature_support': {'constructor_title_icon': '9.57'},
            'min': '10.00',
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_onboarding.json')
@pytest.mark.parametrize('new_icon', [True, False])
@pytest.mark.parametrize(
    'is_new_driver, driver_id, position, expect_ok',
    [
        (False, DRIVER_ID, None, False),
        (True, DRIVER_NO_EXP, None, False),
        (True, DRIVER_ID, POSITION_MINSK, False),
        (True, DRIVER_ID, POSITION_MOSCOW, True),
        (True, DRIVER_ID, None, True),  # fallback to trackstory
    ],
)
async def test_onboarding_promo_retrieve(
        taxi_driver_tutorials,
        mockserver,
        load_json,
        mock_fleet_parks_list,
        mock_driver_trackstory,
        new_icon,
        is_new_driver,
        driver_id,
        position,
        expect_ok,
):
    @mockserver.json_handler('/driver-orders/v1/driver/orders/has-finished')
    def _driver_orders(request):
        return {'has_finished': not is_new_driver}

    headers = prepare_headers(PARK_ID, driver_id, new_icon=new_icon)
    body = {'position': position}
    response = await taxi_driver_tutorials.post(
        '/driver/v1/tutorials/v1/onboarding/retrieve',
        headers=headers,
        json=body,
    )
    assert response.status_code == 200
    assert mock_fleet_parks_list.times_called == 1

    resp_body = response.json()
    etag = resp_body['etag']
    if expect_ok:
        recieved_body = resp_body['info']
        expected_body = load_json('response_promo.json')
        if new_icon:
            # replace header icon type for every page in expected response
            for page in expected_body['ui_pages']:
                page['header'][0]['type'] = 'title_icon'

        assert recieved_body == expected_body
    else:
        assert 'info' not in resp_body
    assert etag

    new_body = {'if_none_match': etag, **body}

    response = await taxi_driver_tutorials.post(
        '/driver/v1/tutorials/v1/onboarding/retrieve',
        headers=headers,
        json=new_body,
    )
    assert response.status_code == 304
    assert mock_fleet_parks_list.times_called == 2


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_onboarding.json')
async def test_onboarding_promo_zone_overrides(
        taxi_driver_tutorials, mockserver, load_json, mock_fleet_parks_list,
):
    @mockserver.json_handler('/driver-orders/v1/driver/orders/has-finished')
    def _driver_orders(request):
        return {'has_finished': False}

    headers = prepare_headers(PARK_ID, DRIVER_ID_2)
    body = {'position': POSITION_MOSCOW}
    response = await taxi_driver_tutorials.post(
        '/driver/v1/tutorials/v1/onboarding/retrieve',
        headers=headers,
        json=body,
    )
    assert response.status_code == 200
    assert mock_fleet_parks_list.times_called == 1
    resp_body = response.json()
    assert resp_body['etag']
    assert resp_body['info'] == load_json('response_promo_moscow.json')


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        SELFREG_DEEPLINK_KEY: {'ru': f'taximeter://{SELFREG_DEEPLINK_PATH}'},
    },
    override_uberdriver={
        SELFREG_DEEPLINK_KEY: {
            'ru': f'taximeteruber://{SELFREG_DEEPLINK_PATH}',
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_onboarding_selfreg.json')
@pytest.mark.parametrize(
    'token, selfreg_called, is_uberdriver, expect_code',
    [
        ('', False, False, 401),
        ('token_bad', True, False, 401),
        ('token_ok', True, False, 200),
        ('token_ok', True, True, 200),
    ],
)
async def test_onboarding_promo_selfreg(
        taxi_driver_tutorials,
        mockserver,
        load_json,
        token,
        selfreg_called,
        is_uberdriver,
        expect_code,
):
    @mockserver.json_handler('/selfreg/internal/selfreg/v1/validate')
    def mock_selfreg(request):
        assert 'token' in request.query
        if request.query['token'] == 'token_bad':
            return mockserver.make_response(status=404)
        return {
            'selfreg_id': SELFREG_ID,
            'phone_pd_id': SELFREG_PHONE,
            'city_id': 'Москва',
            'country_id': 'rus',
        }

    headers = prepare_headers(None, None, is_uberdriver=is_uberdriver)
    params = {}
    if token:
        params['selfreg_token'] = token
    body = {'position': POSITION_MOSCOW}
    response = await taxi_driver_tutorials.post(
        '/driver/v1/tutorials/v1/onboarding/retrieve',
        headers=headers,
        params=params,
        json=body,
    )

    assert response.status_code == expect_code
    assert mock_selfreg.times_called == selfreg_called
    if expect_code == 200:
        resp_body = response.json()
        etag = resp_body['etag']
        assert etag

        expected_response_info = load_json('response_promo.json')

        # in selfreg, 3rd page has no button
        del expected_response_info['ui_pages'][2]['body'][1]

        # but there is 4th page with button
        fourth_page = load_json('final_motivation_page.json')

        if is_uberdriver:
            # special deeplink
            fourth_page['body'][1]['payload']['url'].replace(
                'taximeter://', 'taximeteruber://',
            )
        expected_response_info['ui_pages'].append(fourth_page)

        if is_uberdriver:
            for page in expected_response_info['ui_pages']:
                # special color for an icon
                page['header'][0]['icon']['tint_color'] = '#181819'

        assert resp_body['info'] == expected_response_info
