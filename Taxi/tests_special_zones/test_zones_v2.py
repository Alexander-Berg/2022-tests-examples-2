import datetime

import pytest


AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Request-Application': 'app_name=iphone',
    'X-Request-Language': 'ru',
    'X-AppMetrica-UUID': 'UUID',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-Remote-IP': '10.10.10.10',
}

DISABLE_HELICOPTER_CONFIG = [
    {
        'experiment': 'enable_helicopter',
        'mode': 'helicopter',
        'zone_activation': {
            'point_image_tag': 'custom_pp_icons_helicopter',
            'point_title': 'helicopter.pickuppoint_name',
            'zone_type': 'helicopter',
        },
    },
]


def _multiple_luzha_responses_template(response_for_request_with_actual_time):
    return [
        (
            datetime.datetime(2018, 5, 19),
            'expected_zones_answer_no_zones.json',
        ),
        (
            datetime.datetime(2018, 5, 20),
            'expected_zones_answer_no_zones.json',
        ),
        (
            datetime.datetime(2018, 5, 20, 6, 59),
            'expected_zones_answer_no_zones.json',
        ),
        (
            datetime.datetime(2018, 5, 20, 7, 00),
            response_for_request_with_actual_time,
        ),
        (
            datetime.datetime(2018, 5, 20, 15, 00),
            response_for_request_with_actual_time,
        ),
    ]


@pytest.mark.config(MODES=DISABLE_HELICOPTER_CONFIG)
@pytest.mark.parametrize(
    'time_now, answer',
    _multiple_luzha_responses_template(
        'expected_zones_answer_point_within_p4.json',
    ),
)
async def test_schedule(
        time_now,
        answer,
        taxi_special_zones,
        taxi_config,
        mocked_time,
        load_json,
):
    mocked_time.set(time_now)
    await taxi_special_zones.invalidate_caches()
    cache_config = taxi_config.get('SPECIAL_ZONES_CACHE')
    assert cache_config['use_fast_geohash']
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(answer)


@pytest.mark.parametrize(
    'time_now, answer',
    _multiple_luzha_responses_template('expected_zones_answer_no_zones.json'),
)
@pytest.mark.filldb(pickup_zone_items='disabled_zone')
async def test_disabled_zone(
        time_now, answer, taxi_special_zones, mocked_time, load_json,
):
    mocked_time.set(time_now)
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(answer)


@pytest.mark.parametrize(
    'time_now, answer',
    _multiple_luzha_responses_template(
        'expected_zones_answer_point_p4_disabled_matched_to_p3.json',
    ),
)
@pytest.mark.filldb(pickup_zone_items='disabled_point')
async def test_disabled_point(
        time_now, answer, taxi_special_zones, mocked_time, load_json,
):
    mocked_time.set(time_now)
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(answer)


@pytest.mark.config(MODES=DISABLE_HELICOPTER_CONFIG)
@pytest.mark.now('2018-05-20T15:00:00+0300')
@pytest.mark.filldb(pickup_zone_types='non_default_properties')
async def test_non_default_properties(
        taxi_special_zones, mocked_time, load_json,
):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_zones_non_default_properties.json',
    )


@pytest.mark.config(MODES=DISABLE_HELICOPTER_CONFIG)
@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'geopoint, answer',
    [
        ([37.554483, 55.715741], 'expected_zones_answer_no_zones.json'),
        ([37.546672, 55.725769], 'expected_zones_answer_point_within_p4.json'),
        ([37.575201, 55.714786], 'expected_zones_answer_point_within_p1.json'),
        ([37.577744, 55.715488], 'expected_zones_answer_point_near.json'),
        ([37.578109, 55.715670], 'expected_zones_answer_no_zones.json'),
        ([37.578109, 55.715670], 'expected_zones_answer_no_zones.json'),
    ],
)
async def test_geometry(geopoint, answer, taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': geopoint,
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(answer)


@pytest.mark.parametrize(
    'request_json',
    [
        {},
        {
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'bbox': [0.0, 1.0, 2.0, 3.0, 4.0],
            'geopoint': [37.554483, 55.715741],
            'type': 'a',
        },
        {
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'bbox': [0.0, 1.0, 2.0, 3.0, 4.0],
            'type': 'a',
        },
    ],
)
async def test_bad_request(taxi_special_zones, request_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones', json=request_json,
    )
    assert response.status_code == 400


@pytest.mark.now('2018-05-27T11:00:00+0300')
async def test_localization(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.577744, 55.715488],
            'type': 'a',
        },
        headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
    )

    assert response.status_code == 200
    expected_answer = load_json('expected_zones_answer_point_near_ru.json')
    assert response.json() == expected_answer


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='with_choice')
async def test_choice(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.575201, 55.714786],
            'type': 'a',
        },
        headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_zones_answer_point_within_p1_choice.json',
    )


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='with_choice_hidden')
async def test_choice_hidden(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.575201, 55.714786],
            'type': 'a',
        },
        headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_zones_answer_point_within_p1_choice_hidden.json',
    )


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'type_, answer',
    [
        ('a', 'expected_zones_answer_point_within_p1_universal.json'),
        ('b', 'expected_zones_answer_point_within_p1_dropoff.json'),
        ('any', 'expected_zones_answer_point_within_p1_any.json'),
    ],
)
@pytest.mark.filldb(pickup_zone_items='universal_points')
async def test_point_types(taxi_special_zones, load_json, type_, answer):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.575201, 55.714786],
            'type': type_,
        },
        headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(answer)


@pytest.mark.config(MODES=DISABLE_HELICOPTER_CONFIG)
@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'excluded_zones, allowed_ids, answer',
    [
        (['fan_zone'], [], 'expected_zones_answer_no_zones.json'),
        ([], [], 'expected_zones_answer_point_within_p4.json'),
        ([], ['luzha'], 'expected_zones_answer_point_within_p4.json'),
        ([], ['some_id'], 'expected_zones_answer_no_zones.json'),
        (None, None, 'expected_zones_answer_point_within_p4.json'),
        (None, ['some_id'], 'expected_zones_answer_no_zones.json'),
    ],
)
async def test_excluded_zones(
        excluded_zones, allowed_ids, answer, taxi_special_zones, load_json,
):
    payload = {
        'id': '0a8a55832e7b4621afddfc7239b24ee4',
        'geopoint': [37.546672, 55.725769],
        'type': 'a',
    }
    if excluded_zones is not None:
        payload['filter'] = {'excluded_zone_types': excluded_zones}

    if allowed_ids is not None:
        filter_ = payload.get('filter', {})
        filter_['allowed_ids'] = allowed_ids
        payload['filter'] = filter_

    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json=payload,
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(answer)


@pytest.mark.config(MODES=DISABLE_HELICOPTER_CONFIG)
@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'persistent, answer',
    [
        (None, 'expected_zones_answer_point_within_p4.json'),
        (False, 'expected_zones_answer_point_within_p4.json'),
        (True, 'expected_zones_answer_no_zones.json'),
    ],
)
async def test_no_persistent_zones(
        persistent, answer, taxi_special_zones, load_json,
):
    payload = {
        'id': '0a8a55832e7b4621afddfc7239b24ee4',
        'geopoint': [37.546672, 55.725769],
        'type': 'a',
    }
    if persistent is not None:
        payload['filter'] = {'persistent_only': persistent}

    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json=payload,
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(answer)


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='with_persistent')
async def test_persistent_zones(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
            'filter': {'persistent_only': True},
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_zones_answer_point_within_p4_persistent.json',
    )


# it is monday, so we should not get the first zone
# and should not get the point from the second
@pytest.mark.now('2019-06-11T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='weekdays_filter')
async def test_weekdays_filter(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_zones_answer_weekdays_filtered.json',
    )


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'bbox, answer',
    [
        (
            [37.5403, 55.7117, 37.5513, 55.7172],
            'expected_zones_answer_point_within_p4.json',
        ),
        (
            [37.5403, 55.7172, 37.5513, 55.7117],
            'expected_zones_answer_point_within_p4.json',
        ),
        ([0.0, 0.0, 10.0, 10.0], 'expected_zones_answer_no_zones.json'),
    ],
)
async def test_geohash_search(taxi_special_zones, load_json, bbox, answer):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'bbox': bbox,
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    answer_json = load_json(answer)
    answer_json.pop('pin_zone_id', None)
    answer_json.pop('pin_point_id', None)
    assert response.json() == answer_json


@pytest.mark.parametrize(
    'point_type, alert',
    [
        (
            'a',
            {
                'button_text': 'OK a',
                'content': 'Get out a',
                'title': 'WC 2018 a',
            },
        ),
        (
            'b',
            {
                'button_text': 'OK b',
                'content': 'Get out b',
                'title': 'WC 2018 b',
            },
        ),
        (
            'any',
            {'button_text': 'OK', 'content': 'Get out', 'title': 'WC 2018'},
        ),
    ],
)
@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_types='custom_alerts')
async def test_custom_alert(taxi_special_zones, point_type, alert):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.577744, 55.715488],
            'type': point_type,
        },
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    resp_data = response.json()
    zone = resp_data['zones'][0]
    assert zone['properties']['alert'] == alert


@pytest.mark.parametrize('point_type', ['a', 'b', 'any'])
@pytest.mark.now('2018-05-27T11:00:00+0300')
async def test_default_alert(taxi_special_zones, point_type):
    alert = {'button_text': 'OK', 'content': 'Get out', 'title': 'WC 2018'}
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.577744, 55.715488],
            'type': point_type,
        },
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    resp_data = response.json()
    zone = resp_data['zones'][0]
    assert zone['properties']['alert'] == alert


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='priority')
async def test_zone_priority(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.575201, 55.714786],
            'type': 'any',
        },
    )

    assert response.status_code == 200
    test_json = response.json()
    assert test_json['pin_zone_id'] == 'luzha_high'
    assert test_json['pin_point_id'] == 'p1'


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='tariffs_in_pp')
async def test_zone_tariffs_in_pp(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.575201, 55.714786],
            'type': 'any',
        },
    )

    assert response.status_code == 200
    test_json = response.json()
    points = test_json['zones'][0]['points']
    for point in points:
        if point['id'] == 'p1':
            assert point['supported_tariffs'] == ['vip', 'business']
            continue
        if point['id'] == 'p2':
            assert point['supported_tariffs'] == ['cargo']
            continue
        assert point.get('supported_tariffs') is None


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='tariffs_in_pp')
@pytest.mark.parametrize(
    ['tariff', 'expected_point_ids'],
    [
        ('vip', ['p1', 'p0', 'p3', 'p4']),
        ('business', ['p1', 'p0', 'p3', 'p4']),
        ('cargo', ['p2', 'p0', 'p3', 'p4']),
        ('ololo', ['p0', 'p3', 'p4']),
    ],
)
async def test_zone_filter_by_tariff(
        taxi_special_zones, load_json, tariff, expected_point_ids,
):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.575201, 55.714786],
            'type': 'any',
            'filter': {'selected_tariff': tariff},
        },
    )

    assert response.status_code == 200
    test_json = response.json()
    point_ids = [point['id'] for point in test_json['zones'][0]['points']]
    assert set(point_ids) == set(expected_point_ids)


@pytest.mark.config(MODES=DISABLE_HELICOPTER_CONFIG)
@pytest.mark.now('2018-05-20T15:00:00+0300')
@pytest.mark.filldb(pickup_zone_types='non_default_properties')
@pytest.mark.experiments3(filename='exp_hide_points.json')
async def test_filtered_points(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={
            'id': '0a8a55832e7b4621afddfc7239b24ee4',
            'geopoint': [37.546672, 55.725769],
            'type': 'a',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_zones_with_filtered_points.json',
    )


@pytest.mark.now('2018-05-20T15:00:00+0300')
@pytest.mark.experiments3(filename='exp_zones_visibility.json')
@pytest.mark.experiments3(filename='exp_enabling_zones.json')
@pytest.mark.parametrize(
    'point,found_zones',
    [
        # enable_exp doesn't match (kremlin)
        ([37.615965, 55.752262], []),
        # enable_exp matches (luzha)
        ([37.559299, 55.718943], ['luzha']),
        # no enable_exp in config (mipt is NOT visible by default)
        ([37.521171, 55.929846], []),
        # no rule for sdc type (yasenevo is visible by default)
        ([37.534146308898926, 55.6060630738532], ['yasenevo']),
    ],
)
async def test_visibility(taxi_special_zones, point, found_zones):
    response = await taxi_special_zones.post(
        'special-zones/v1/zones',
        json={'geopoint': point, 'type': 'a'},
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    assert [zone['id'] for zone in response.json()['zones']] == found_zones
