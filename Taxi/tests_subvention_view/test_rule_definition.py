import base64
import gzip
import json

import pytest

from . import common

DEFAULT_HEADERS = {
    'X-Driver-Session': 'test_session',
    'User-Agent': 'Taximeter 9.77 (456)',
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'dbid1',
    'X-YaTaxi-Driver-Profile-Id': 'driver1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

VEHICLE_BINDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle1'},
        },
    ],
}


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.experiments3(
    match={
        'predicate': {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'arg_name': 'park_id',
                            'arg_type': 'string',
                            'value': 'dbid1',
                        },
                        'type': 'eq',
                    },
                    {
                        'init': {
                            'arg_name': 'driver_profile_id',
                            'arg_type': 'string',
                            'value': 'driver1',
                        },
                        'type': 'eq',
                    },
                ],
            },
            'type': 'all_of',
        },
        'enabled': True,
    },
    name='rule_definition_in_schedule_id',
    consumers=['subvention-view/v1/schedule'],
    clauses=[],
    default_value=True,
)
@pytest.mark.parametrize(
    'rule, lat, lon, expected_id',
    [
        (
            {
                'draft_id': '1234abcd',
                'rate': 10.0,
                'rule_id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                'tariff_class': 'comfort',
                'tariff_zone': 'moscow',
                'time_range': {
                    'from': '2020-09-13T21:00:00+00:00',
                    'to': '2020-09-21T11:15:16+00:00',
                },
            },
            '55.733863',
            '37.590533',
            {
                'end': '2020-09-21T11:15:16+00:00',
                'geoareas': [],
                'rule_id': '774ef04af438c1a15f41d1f98a973bd5',
                'start': '2020-09-13T21:00:00+00:00',
            },
        ),
        (
            {
                'draft_id': '1234abcd',
                'rate': 10.0,
                'geoarea': 'uao',
                'rule_id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                'tariff_class': 'comfort',
                'tariff_zone': 'moscow',
                'time_range': {
                    'from': '2020-09-13T21:00:00+00:00',
                    'to': '2020-09-21T11:15:16+00:00',
                },
            },
            '55.733863',
            '37.590533',
            {
                'end': '2020-09-21T11:15:16+00:00',
                'geoareas': ['uao'],
                'rule_id': '774ef04af438c1a15f41d1f98a973bd5',
                'start': '2020-09-13T21:00:00+00:00',
            },
        ),
    ],
)
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
        'match_split_by': ['zone', 'tariff_class', 'geoarea'],
    },
)
async def test_schedule(
        mockserver,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        rule,
        lat,
        lon,
        expected_id,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    @mockserver.json_handler(
        '/subvention-schedule/internal/subvention-schedule/v1/schedule',
    )
    async def _mock_sch_get(request):
        return {'schedules': [{'type': 'single_ride', 'items': [rule]}]}

    request_params = {'selfreg_token': 'selfreg_token', 'lat': lat, 'lon': lon}

    response = await taxi_subvention_view.get(
        '/v1/schedule', params=request_params, headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    response_data = response.json()
    for schedule in response_data['items_for_schedule']:
        for schedule_rule in schedule['rules']:
            enc_df = schedule_rule['id']
            assert enc_df[:5] == 'rd/1/'
            decoded = gzip.decompress(
                base64.urlsafe_b64decode(enc_df[5:] + '=='),
            )
            assert json.loads(decoded) == expected_id


ENCRYPTED_RULE_ID = base64.urlsafe_b64encode(
    gzip.compress(
        json.dumps(
            {
                'end': '2020-09-21T11:15:16+00:00',
                'geoareas': ['uao'],
                'rule_id': '774ef04af438c1a15f41d1f98a973bd5',
                'start': '2020-09-13T21:00:00+00:00',
            },
        ).encode('utf-8'),
    ),
).decode('utf-8')


@pytest.mark.now('2019-02-24T11:00:00Z')
@pytest.mark.parametrize(
    ('subventions_ids', 'current_point', 'expected_response_code'),
    [
        (['rd/invalid'], [37.6, 55.75], 400),
        (['rd/10/' + ENCRYPTED_RULE_ID], [37.6, 55.75], 400),
        (['rd/0/' + ENCRYPTED_RULE_ID], [37.6, 55.75], 400),
        (['rd//' + ENCRYPTED_RULE_ID], [37.6, 55.75], 400),
    ],
)
@pytest.mark.config(SUBVENTION_VIEW_STATUS_FETCH_SMART_SUBVENTIONS=True)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_status_errors(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        subventions_ids,
        current_point,
        expected_response_code,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)

    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)

    bss.clean_by_driver_subvention()
    bss.clean_rules()

    await taxi_subvention_view.invalidate_caches()

    assert len(current_point) == 2
    lon, lat = current_point

    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}'.format(
            lon, lat, ','.join(subventions_ids),
        ),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == expected_response_code

    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('2020-09-14T11:00:00Z')
@pytest.mark.parametrize(
    ('subventions_ids', 'current_point', 'expected_response'),
    [
        (
            # active, no area at all
            [
                {
                    'geoareas': [],
                    'rule_id': '774ef04af438c1a15f41d1f98a973bd5',
                    'start': '2020-09-13T21:00:00+00:00',
                    'end': '2020-09-21T11:15:16+00:00',
                },
            ],
            [37.6, 55.75],
            'expected_response_out_of_zone.json',
        ),
        (
            # active, in area
            [
                {
                    'geoareas': ['moscow_activation'],
                    'rule_id': '774ef04af438c1a15f41d1f98a973bd5',
                    'start': '2020-09-13T21:00:00+00:00',
                    'end': '2020-09-21T11:15:16+00:00',
                },
            ],
            [37.6, 55.75],
            'expected_response_in_zone.json',
        ),
        (
            # active, not in area
            [
                {
                    'geoareas': ['moscow'],
                    'rule_id': '774ef04af438c1a15f41d1f98a973bd5',
                    'start': '2020-09-13T21:00:00+00:00',
                    'end': '2020-09-21T11:15:16+00:00',
                },
            ],
            [37.6, 55.75],
            'expected_response_out_of_zone.json',
        ),
        (
            # inactive, in area
            [
                {
                    'geoareas': ['moscow_activation'],
                    'rule_id': '774ef04af438c1a15f41d1f98a973bd5',
                    'start': '2019-09-13T21:00:00+00:00',
                    'end': '2019-09-21T11:15:16+00:00',
                },
            ],
            [37.6, 55.75],
            'expected_response_out_of_zone.json',
        ),
    ],
)
@pytest.mark.config(SUBVENTION_VIEW_STATUS_FETCH_SMART_SUBVENTIONS=True)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_status(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        subventions_ids,
        current_point,
        expected_response,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)

    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)

    bss.clean_by_driver_subvention()
    bss.clean_rules()

    await taxi_subvention_view.invalidate_caches()

    assert len(current_point) == 2
    lon, lat = current_point

    compressed_subventions = [
        (
            'rd/1/'
            + base64.urlsafe_b64encode(
                gzip.compress(json.dumps(x).encode('utf-8')),
            ).decode('utf-8')
        )
        for x in subventions_ids
    ]

    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}'.format(
            lon, lat, ','.join(compressed_subventions),
        ),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response = response.json()

    def update_nested(in_dict):
        for key, value in in_dict.items():
            if key == 'id':
                in_dict[key] = compressed_subventions[0]
            elif isinstance(value, dict):
                update_nested(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        update_nested(item)

    expected = load_json(expected_response)
    update_nested(expected)
    assert response == expected

    bss.clean_rules()
    bss.clean_by_driver_subvention()
