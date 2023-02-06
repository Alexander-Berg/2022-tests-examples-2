import enum
import json

import pytest

SELFREG_HEADERS = {
    'User-Agent': 'Taximeter 9.77 (456)',
    'Accept-Language': 'ru',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

SELFREG_PARAMS_SCHEDULE = {
    'selfreg_token': 'selfreg_token',
    'lat': '55.733863',
    'lon': '37.590533',
}

SELFREG_PARAMS_STATUS = {
    'selfreg_token': 'selfreg_token',
    'lat': '55.733863',
    'lon': '37.590533',
    'subventions_id': '_id/subvention_1',
}

SELFREG_PARAMS_NMFG = {'selfreg_token': 'selfreg_token'}

SELFREG_BODY_NMFG = {
    'lat': 55.733863,
    'lon': 37.590533,
    'from': '2018-09-23',
    'to': '2018-09-24',
    'types': ['daily_guarantee'],
}


class HandleType(enum.Enum):
    GET = 1
    POST = 2


async def _make_request(
        handle_type,
        handle_params,
        handle_path,
        taxi_subvention_view,
        body=None,
):
    if handle_type is HandleType.GET:
        return await taxi_subvention_view.get(
            handle_path, params=handle_params, headers=SELFREG_HEADERS,
        )
    if handle_type is HandleType.POST:
        return await taxi_subvention_view.post(
            handle_path,
            params=handle_params,
            headers=SELFREG_HEADERS,
            json=body,
        )


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'selfreg_type,selfreg_tags,expected_tags,expected_tariffs',
    [
        ('driver', None, ['selfreg_v2_driver_unreg'], ['econom']),
        (
            'courier',
            None,
            ['selfreg_v2_courier_unreg'],
            ['courier', 'express'],
        ),
        (
            None,
            None,
            ['selfreg_v2_profi_unreg'],
            ['courier', 'econom', 'express'],
        ),
        (
            None,
            ['selfreg_v2_profi_unreg'],
            ['selfreg_v2_profi_unreg'],
            ['courier', 'econom', 'express'],
        ),
        (
            'driver',
            ['selfreg_v2_driver_unreg', 'some_tag1'],
            ['selfreg_v2_driver_unreg', 'some_tag1'],
            ['econom'],
        ),
        (
            'courier',
            ['selfreg_v2_courier_unreg', 'some_tag2'],
            ['selfreg_v2_courier_unreg', 'some_tag2'],
            ['courier', 'express'],
        ),
    ],
)
async def test_selfreg_type(
        taxi_subvention_view,
        mockserver,
        bss,
        load_json,
        selfreg,
        selfreg_type,
        selfreg_tags,
        expected_tags,
        expected_tariffs,
):
    bss.add_rules(load_json('geobooking_rule_moscow_with_tags.json'))
    selfreg.set_selfreg(selfreg_type=selfreg_type, mock_tags=selfreg_tags)

    response = await _make_request(
        HandleType.GET,
        SELFREG_PARAMS_SCHEDULE,
        '/v1/schedule',
        taxi_subvention_view,
    )
    assert response.status_code == 200
    bss_requests = bss.rules_select_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1

    expected_bss_request = {
        'is_personal': False,
        'limit': 1000,
        'types': ['geo_booking', 'goal'],
        'driver_branding': 'no_branding',
        'profile_tags': expected_tags,
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2017-07-13T11:15:16+00:00',
            'start': '2017-07-06T11:15:16+00:00',
        },
    }
    assert json.loads(bss_requests[0]) == expected_bss_request
    bss.clean_rules()
    response = await _make_request(
        HandleType.GET,
        SELFREG_PARAMS_STATUS,
        '/v1/status',
        taxi_subvention_view,
    )
    assert response.status_code == 200

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def _mock_bs_rules_select(request):
        content = json.loads(request.get_data())
        expected_request = {
            'is_personal': False,
            'status': 'enabled',
            'tariff_zone': 'moscow',
            'time_range': {
                'start': '2018-09-22T21:00:00+00:00',
                'end': '2018-09-23T21:00:00+00:00',
            },
            'driver_branding': 'no_branding',
            'profile_tariff_classes': expected_tariffs,
            'order_tariff_classes': expected_tariffs,
            'profile_tags': expected_tags,
            'types': ['daily_guarantee'],
            'limit': 1000,
        }
        assert content == expected_request
        return {'subventions': load_json('bs/rules_select.json')}

    response = await _make_request(
        HandleType.POST,
        SELFREG_PARAMS_NMFG,
        '/v1/nmfg/status',
        taxi_subvention_view,
        SELFREG_BODY_NMFG,
    )
    assert response.status_code == 200


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_selfreg_error(taxi_subvention_view, bss, load_json, selfreg):
    bss.add_rules(load_json('geobooking_rule_moscow_with_tags.json'))
    selfreg.set_error_code(500)

    response = await _make_request(
        HandleType.GET,
        SELFREG_PARAMS_SCHEDULE,
        '/v1/schedule',
        taxi_subvention_view,
    )
    assert response.status_code == 403
    response = await _make_request(
        HandleType.GET,
        SELFREG_PARAMS_STATUS,
        '/v1/status',
        taxi_subvention_view,
    )
    assert response.status_code == 403
    response = await _make_request(
        HandleType.POST,
        SELFREG_PARAMS_NMFG,
        '/v1/nmfg/status',
        taxi_subvention_view,
        SELFREG_BODY_NMFG,
    )
    assert response.status_code == 403
