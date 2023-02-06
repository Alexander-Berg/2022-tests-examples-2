import copy

import pytest

DEFAULT_HEADERS = {
    'X-Request-Application': (
        'app_name=android,app_ver1=1,app_ver2=2,app_ver3=4'
    ),
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-Yandex-UID': 'yauid',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-AppMetrica-UUID': 'appmetrica_uid',
    'X-AppMetrica-DeviceId': 'device_id',
}

DEFAULT_REQUEST = {
    'position': [37.211375, 55.477065],
    'bbox': [37.211375, 55.477065, 38.022770, 55.983040],
    'cache_bbox': [37.211375, 55.477065, 38.022770, 55.983040],
    'location': [37.211375, 55.477065],
}

DEFAULT_RESPONSE = {
    'objects': [
        {
            'id': 'published_promo_on_map_id',
            'geometry': [37.56, 55.77],
            'image_tag': 'image_tag2',
            'action': {
                'type': 'show_screen_promo_action',
                'deeplink': 'deeplink',
                'promotion_id': 'promotion_id',
            },
            'bubble': {
                'id': 'bubble_id',
                'hide_after_tap': True,
                'max_per_session': 1,
                'max_per_user': 10,
                'components': [{'type': 'text', 'value': 'text on bubble'}],
            },
            'cache': {'distance': 1000},
        },
    ],
}


@pytest.fixture(autouse=True)
def _yaga_adjust(mockserver):
    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_yaga_adjust(request):
        return {
            'adjusted': [
                {'longitude': 37.56, 'latitude': 55.77, 'geo_distance': 100},
            ],
        }


@pytest.fixture(name='promotions_simple')
def _mock_promotions_simple(mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_simple.json')

    return _mock_promotions


@pytest.mark.parametrize(
    ('promotions_response',),
    [
        ('promotions_simple.json',),
        ('promotions_promo_on_map_without_experiment.json',),
    ],
)
@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
async def test_ok(
        taxi_inapp_communications, mockserver, load_json, promotions_response,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(promotions_response)

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    resp = copy.deepcopy(DEFAULT_RESPONSE)
    assert response.json() == resp


@pytest.mark.translations(
    backend_promotions={'text on bubble': {'ru': 'текст', 'en': 'text'}},
)
@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
async def test_translations(taxi_inapp_communications, mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_promo_on_map_tanker_key.json')

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    resp = copy.deepcopy(DEFAULT_RESPONSE)
    resp['objects'][0]['bubble']['components'][0]['value'] = 'текст'
    assert response.json() == resp


@pytest.mark.experiments3(filename='exp3_promos_on_map_empty.json')
async def test_no_experiments(taxi_inapp_communications, promotions_simple):
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()['objects']


@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
async def test_no_attract(taxi_inapp_communications, mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_do_not_attract.json')

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()


@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
async def test_invalid_response(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_no_experiment.json')

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert not response.json()['objects']


@pytest.mark.experiments3(filename='exp3_promos_on_map_time_and_tags.json')
async def test_ok_exp_matching(
        mockserver, taxi_inapp_communications, promotions_simple,
):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == DEFAULT_RESPONSE


async def _check_promos_on_map(
        taxi_inapp_communications,
        request=copy.deepcopy(DEFAULT_REQUEST),
        resp=copy.deepcopy(DEFAULT_RESPONSE),
):
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == resp


@pytest.mark.pgsql(
    'dbinappcommunications', files=['dbinappcommunications_default.sql'],
)
@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
@pytest.mark.config(INAPP_CACHE_PROMOS_ON_MAP_ENABLED=True)
async def test_promos_get_from_cache(
        taxi_inapp_communications, promotions_simple,
):
    await _check_promos_on_map(taxi_inapp_communications)


@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
@pytest.mark.config(INAPP_CACHE_PROMOS_ON_MAP_ENABLED=True)
async def test_promos_cache_cycle(
        taxi_inapp_communications, pgsql, mockserver, promotions_simple,
):
    class CallsCounter:
        calls = 0

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_yaga_adjust(request):
        CallsCounter.calls += 1

        return {
            'adjusted': [
                {'longitude': 37.56, 'latitude': 55.77, 'geo_distance': 100},
            ],
        }

    await _check_promos_on_map(taxi_inapp_communications)
    await _check_promos_on_map(taxi_inapp_communications)

    db = pgsql['dbinappcommunications']
    cursor = db.cursor()
    cursor.execute(
        'SELECT longitude, latitude, promos_on_map '
        'FROM inapp_communications.promos_on_map_cache '
        'WHERE '
        f'yandex_uid = \'yauid\'',
    )

    res = cursor.fetchone()
    assert res[0] == 37.211375
    assert res[1] == 55.477065
    assert res[2]['objects'][0]['latitude'] == 55.77

    assert CallsCounter.calls == 1


@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
@pytest.mark.config(INAPP_CACHE_PROMOS_ON_MAP_ENABLED=True)
async def test_promos_cache_no_unneccessary_using(
        taxi_inapp_communications, pgsql,
):
    resp = {'objects': []}
    await _check_promos_on_map(taxi_inapp_communications, resp=resp)
    db = pgsql['dbinappcommunications']
    cursor = db.cursor()
    cursor.execute('SELECT *  FROM inapp_communications.promos_on_map_cache ')

    assert not cursor.fetchall()


@pytest.mark.pgsql(
    'dbinappcommunications', files=['dbinappcommunications_default.sql'],
)
@pytest.mark.experiments3(filename='exp3_promos_on_map.json')
@pytest.mark.config(INAPP_CACHE_PROMOS_ON_MAP_ENABLED=True)
async def test_promos_cache_too_far(
        taxi_inapp_communications, mockserver, promotions_simple,
):
    class CallsCounter:
        calls = 0

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_yaga_adjust(request):
        CallsCounter.calls += 1

        return {
            'adjusted': [
                {
                    'longitude': 37.56,
                    'latitude': 55.88 if CallsCounter.calls == 1 else 55.89,
                    'geo_distance': 100,
                },
            ],
        }

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['position'] = [37.211375, 55.577065]
    resp = copy.deepcopy(DEFAULT_RESPONSE)
    resp['objects'][0]['geometry'][1] = 55.88
    # preserving of resp means uniqueness of generation
    await _check_promos_on_map(
        taxi_inapp_communications, request=request, resp=resp,
    )
    await _check_promos_on_map(
        taxi_inapp_communications, request=request, resp=resp,
    )

    assert CallsCounter.calls == 1


@pytest.mark.parametrize(('use_promotion_id',), [(True,), (False,)])
@pytest.mark.experiments3(filename='exp3_promos_on_map_deeplink_action.json')
async def test_deeplink_action_exp(
        taxi_inapp_communications, mockserver, load_json, use_promotion_id,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        resp = load_json('promotions_simple.json')
        if not use_promotion_id:
            del resp['promos_on_map'][0]['action']['promotion_id']
        return resp

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_yaga_adjust(request):
        return {
            'adjusted': [
                {'longitude': 37.56, 'latitude': 55.77, 'geo_distance': 100},
            ],
        }

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    resp = copy.deepcopy(DEFAULT_RESPONSE)
    if not use_promotion_id:
        resp['objects'][0]['action'].update({'type': 'deeplink'})
        del resp['objects'][0]['action']['promotion_id']
    assert response.json() == resp


@pytest.mark.parametrize(
    'phone_id, is_in_test',
    [('phone_id_1', True), ('phone_id_not_in_test_publish', False)],
)
@pytest.mark.experiments3(filename='exp3_test_publish.json')
async def test_test_publish(
        taxi_inapp_communications, phone_id, is_in_test, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-YaTaxi-PhoneId'] = phone_id
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        json=DEFAULT_REQUEST,
        headers=headers,
    )

    assert response.status == 200, response.text
    objects = response.json()['objects']
    assert len(objects) == (1 if is_in_test else 0)


@pytest.mark.parametrize('is_extended_request', [(True,), (False,)])
@pytest.mark.experiments3(filename='exp3_promos_on_map_subscription_id.json')
async def test_subscription_id(
        taxi_inapp_communications,
        experiments3,
        mockserver,
        load_json,
        is_extended_request,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_simple.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    if is_extended_request:
        request.update(
            {
                'plus_subscription_info': {
                    'available_subscription_id': 'testing_subscription_id',
                },
            },
        )
    exp_name = 'subscription_id_testing'
    api_url = '/inapp-communications/v1/promos-on-map'

    exp3_recorder = experiments3.record_match_tries(exp_name)

    await taxi_inapp_communications.post(
        api_url, json=request, headers=DEFAULT_HEADERS,
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    if is_extended_request:
        match_tries[0].ensure_matched_with_clause('test_match_subscription_id')
    else:
        match_tries[0].ensure_no_match()


@pytest.mark.parametrize('bank_account', [True, False])
@pytest.mark.experiments3(filename='exp3_bank_account.json')
async def test_bank_account(
        taxi_inapp_communications, bank_account, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    if bank_account:
        headers['X-YaTaxi-Pass-Flags'] = 'bank-account'
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        json=DEFAULT_REQUEST,
        headers=headers,
    )

    assert response.status == 200, response.text
    objects = response.json()['objects']
    assert len(objects) == (1 if bank_account else 0)


@pytest.mark.experiments3(
    filename='exp3_promotions_promo_on_map_zone_msk.json',
)
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.parametrize(
    'position, objects_count',
    [([37.5, 55.8], 1), ([30.29, 59.95], 0)],  # [moscow , spb]
)
async def test_zone(
        taxi_inapp_communications,
        mockserver,
        load_json,
        position,
        objects_count,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_simple.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['position'] = position

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    objects = response.json()['objects']
    assert len(objects) == objects_count
