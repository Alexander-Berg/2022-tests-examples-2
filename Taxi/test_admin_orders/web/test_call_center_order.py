import json
import os

import aiohttp.web
import bson.json_util
import pytest

from admin_orders import util

CONFIGS = dict(
    TVM_RULES=[{'dst': 'archive-api', 'src': 'admin-orders'}],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    ENABLE_DRIVER_CHANGE_COST=True,
    USE_PAYMENT_EVENTS=True,
    CHATTERBOX_ANTIFRAUD_RULES_FOR_META=['flag_enabled', 'flag_disabled'],
    ADMIN_ORDERS_ENABLE_SEND_DRIVER_LICENSE_PERSONAL_ID=True,
    ADMIN_ORDERS_CHUNK_SIZE_FOR_DRIVER_METRICS=1,
)

SPECIAL_RESPONSE = {
    'complete_score_change': 2,
    'loyalty_change': 30,
    'activity_change': 0,
    'event': {
        'event_id': '86908560',
        'order_alias': '17a659ce9472282a9a2f125896f64b27',
        'datetime': '2021-11-18T15:24:19.596+00:00',
        'type': 'order',
        'order_id': '0fc10c193bbb32fa97ea5fc7cca95455',
        'extra': {
            'replace_activity_with_priority': True,
            'dtags': [],
            'rtags': None,
            'tariff_class': 'econom',
            'time_to_a': 144,
            'distance_to_a': 290,
            'dispatch_id': '619670045d7cb300482343d9',
            'sp_alpha': 1,
            'sp': 2.1,
            'driver_id': '100500_bd605df8cbd195bead5d191c974ad825',
            'activity_value': None,
        },
        'park_driver_profile_id': (
            '7ad36bc7560449998acbe2c57a75c293_bd605df8cbd195bead5d191c974ad825'
        ),
        'extra_data': '',
        'descriptor': {
            'type': 'complete',
            'tags': [
                'replace_activity_with_priority',
                'lookup_mode_dispatch-buffer',
                'tariff_econom',
                'dispatch_short',
            ],
        },
        'tariff_zone': 'moscow',
    },
    'priority_change': 2,
    'priority_absolute': 3,
}

RESPONSE_CACHE = {}

RESPONSES_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_call_center_order', 'responses',
)
for root, _, filenames in os.walk(RESPONSES_DIR):
    for filename in filenames:
        full_filename = os.path.join(root, filename)
        if filename.endswith('.bson.json'):
            with open(full_filename) as f:
                RESPONSE_CACHE[filename[:-5]] = bson.json_util.loads(f.read())
        elif filename.endswith('.json'):
            with open(full_filename) as f:
                RESPONSE_CACHE[filename] = json.load(f)


def make_json_response(resp_filename):
    try:
        response = RESPONSE_CACHE[resp_filename]
    except KeyError:
        return aiohttp.web.Response(status=404)
    return response


# request.param - list of disabled externals
@pytest.fixture(name='taxi_admin_orders_mocks')
def _taxi_admin_orders_mocks(mockserver, request, order_archive_mock):
    """Put your mocks here"""

    def _set_order_proc():
        if 'archive-api' in request.param:
            return
        if 'archive-api/order_proc' in request.param:
            return
        for resp_filename, response in RESPONSE_CACHE.items():
            if resp_filename.startswith('order_archive-order_proc-retrieve'):
                order_archive_mock.set_order_proc(response['doc'])

    _set_order_proc()

    @mockserver.handler('/archive-api/archive/', prefix=True)
    def _get_archive_order(request):
        return aiohttp.web.Response(status=404)

    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def _lookup_rows(http_request):
        if 'archive-api' in request.param:
            return aiohttp.web.Response(status=500)
        request_data = json.loads(http_request.get_data())
        all_rows = RESPONSE_CACHE['archive-api_v1_yt_lookup_rows.json']
        order_id = request_data['query'][0]['id']
        rows = []
        for row in all_rows['items']:
            if row['id'] == order_id:
                rows.append(row)
        return {'items': rows}

    @mockserver.json_handler('/replication/map_data')
    def _map_data(http_request):
        return {'items': []}

    @mockserver.json_handler('/user_api-api/users/get')
    def _users_get(http_request):
        if 'user-api' in request.param:
            return aiohttp.web.Response(status=500)
        request_json = json.loads(http_request.get_data())
        user_id = request_json['id']
        return make_json_response(f'user-api_users_get_{user_id}.json')

    @mockserver.json_handler('/user_api-api/user_phones/get')
    def _user_phones_get(http_request):
        if 'user-api' in request.param:
            return aiohttp.web.Response(status=500)
        request_json = json.loads(http_request.get_data())
        phone_id = request_json['id']
        return make_json_response(f'user-api_user_phones_get_{phone_id}.json')

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(http_request):
        if 'driver-profiles' in request.param:
            return aiohttp.web.Response(status=500)
        response_filename = 'driver-profiles_v1_driver_profiles_retrieve.json'
        responses = RESPONSE_CACHE[response_filename]
        request_json = json.loads(http_request.get_data())
        driver_ids = set(request_json['id_in_set'])
        responses = [
            profile
            for profile in responses['profiles']
            if profile['park_driver_profile_id'] in driver_ids
        ]
        return mockserver.make_response(json={'profiles': responses})

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariff_zones(http_request):
        locale = http_request.query['locale']
        zones = RESPONSE_CACHE[f'tariffs_v1_tariff_zones_{locale}.json']
        return mockserver.make_response(json=zones)

    @mockserver.handler('/parks-replica/v1/parks/retrieve')
    def _get_parks_info(http_request):
        if 'parks-replica' in request.param:
            return aiohttp.web.Response(status=500)
        request_json = json.loads(http_request.get_data())
        park_id = request_json['id_in_set'][0]
        if park_id == '643753730233':
            response_dict = RESPONSE_CACHE[
                'parks-replica_v1_parks_retrieve.json'
            ]
            return mockserver.make_response(json=response_dict)
        return mockserver.make_response(json={'parks': [{'park_id': park_id}]})

    match_mapper = {
        '5d4d016191272f03f6ab5a65': [
            'user_phone_id_tag_1',
            'user_phone_id_tag_2',
        ],
        '808d85827a454f12b856e75c60b05723': ['personal_phone_id_tag'],
        '4ae9f936b1c6dfee2b95b24ca26ea587': ['user_id_tag'],
    }

    @mockserver.handler('/passenger-tags/v3/match_single')
    def _passenger_tags_match_single(http_request):
        if 'passenger-tags' in request.param:
            return aiohttp.web.Response(status=500)
        request_match = json.loads(http_request.get_data())['match']
        response_cache = RESPONSE_CACHE['tags_v3_match_single.json']
        response_dict = {'tags': {}}
        for match in request_match:
            fields_to_get = match_mapper.get(match['value'], [])
            assert all(
                field.startswith(match['type']) for field in fields_to_get
            )
            response_dict['tags'].update(
                util.partial_dict(response_cache['tags'], fields_to_get),
            )
        return mockserver.make_response(json=response_dict)

    @mockserver.handler('/antifraud_refund-api/taxi/support')
    def _antifraud_refund(http_request):
        if 'antifraud_refund' in request.param:
            return aiohttp.web.Response(status=500)
        request_json = json.loads(http_request.get_data())
        if 'driver-profiles' in request.param:
            assert 'driver_license_personal_id' not in request_json
            request_json[
                'driver_license_personal_id'
            ] = 'ec67f442dd2e4529b00bf969047f7c50'

        response_cache = RESPONSE_CACHE['antifraud_refund.json']
        for item in response_cache['items']:
            if request_json == item['request']:
                return mockserver.make_response(json=item['response'])
        empty_response = RESPONSE_CACHE['antifraud_refund_empty_response.json']
        return mockserver.make_response(json=empty_response)


@pytest.mark.parametrize(
    [
        'order_id',
        'taxi_admin_orders_mocks',  # list of disabled externals
        'expected_status',
        'expected_filename',
        'events_processed_request_and_response',
        'body',
    ],
    [
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            [],
            200,
            'admin_orders_cc_v1_order_0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7ad36bc7560449998acbe2c57a75c293': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {'driver_uuids': ['7157111f9299427ab4be21f42c6c24ae']},
        ),
        (
            '\t0fc10c193bbb32fa97ea5fc7cca95455  ',
            [],
            200,
            'admin_orders_cc_v1_order_0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7ad36bc7560449998acbe2c57a75c293': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {'driver_uuids': ['7157111f9299427ab4be21f42c6c24ae']},
        ),
        (
            '000f0f0f0f0f0f0f0ff00f00a0a0a0a0',
            [],
            200,
            'admin_orders_cc_v1_order_000f0f0f0f0f0f0f0ff00f00a0a0a0a0',
            {},
            {},
        ),
        (
            'ef4709660a2815e9977a2e020fc50d19',
            [],
            200,
            'admin_orders_cc_v1_order_ef4709660a2815e9977a2e020fc50d19',
            {},
            {},
        ),
        (
            '7185d76182a237e296526466b81f390d',
            [],
            200,
            'admin_orders_cc_v1_order_7185d76182a237e296526466b81f390d',
            {},
            {},
        ),
        (
            'non_existing_order_id',
            [],
            404,
            'admin_orders_cc_v1_order_not_found',
            {},
            {},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            ['archive-api'],
            500,
            None,
            {},
            {'driver_uuids': ['7157111f9299427ab4be21f42c6c24ae']},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            ['archive-api/order_proc'],
            200,
            'admin_orders_cc_v1_order_0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7ad36bc7560449998acbe2c57a75c293': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {'driver_uuids': ['7157111f9299427ab4be21f42c6c24ae']},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            ['user-api'],
            200,
            'admin_orders_cc_v1_order_user_api_disabled',
            {},
            {},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            ['driver-profiles'],
            200,
            'admin_orders_cc_v1_order_driver_profiles_disabled',
            {},
            {},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            ['parks-replica'],
            200,
            'admin_orders_cc_v1_order_parks_replica_disabled',
            {},
            {},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            ['passenger-tags'],
            200,
            'admin_orders_cc_v1_order_tags_disabled',
            {},
            {},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            ['antifraud_refund'],
            200,
            'admin_orders_cc_v1_order_antifraud_refund_disabled',
            {},
            {},
        ),
        (
            'abd624e55f20350e8b95dee816a4b69b',
            [],
            200,
            'admin_orders_cc_v1_order_0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7ad36bc7560449998acbe2c57a75c293': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {'driver_uuids': ['7157111f9299427ab4be21f42c6c24ae']},
        ),
        (
            'abd624e55f20350e8b95dee816a4b69b',
            ['archive-api/order_proc'],
            404,
            'admin_orders_cc_v1_order_not_found',
            {},
            {},
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            [],
            200,
            'admin_orders_cc_v1_test_candidates_order_'
            '0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7ad36bc7560449998acbe2c57a75c293': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
                '7f74df331eb04ad78bc2ff25ff88a8f2': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {
                'driver_uuids': [
                    '7157111f9299427ab4be21f42c6c24ae',
                    '2698ee4ecaf74b78bf3320ad3e05ae76',
                ],
            },
        ),
    ],
    indirect=['taxi_admin_orders_mocks'],
)
@pytest.mark.config(**CONFIGS)
async def test_order(
        taxi_admin_orders_web,
        taxi_admin_orders_mocks,
        order_id,
        expected_status,
        expected_filename,
        events_processed_request_and_response,
        body,
        mockserver,
):
    @mockserver.handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_driver_uniques_retrieve_by_profiles(http_request):
        return mockserver.make_response(
            json={
                'uniques': [
                    {
                        'data': {'unique_driver_id': elem.split('_')[0]},
                        'park_driver_profile_id': elem,
                    }
                    for elem in http_request.json['profile_id_in_set']
                ],
            },
        )

    @mockserver.handler('/driver-metrics-storage/v3/events/processed')
    def _v3_events_processed(http_request):
        assert (
            http_request.json['unique_driver_id']
            in events_processed_request_and_response
        )
        assert (
            http_request.json['order_ids']
            == events_processed_request_and_response[
                http_request.json['unique_driver_id']
            ]['order_ids']
        )
        response = mockserver.make_response(
            json={
                'events': events_processed_request_and_response[
                    http_request.json['unique_driver_id']
                ]['response'],
            },
        )
        del events_processed_request_and_response[
            http_request.json['unique_driver_id']
        ]
        return response

    response = await taxi_admin_orders_web.post(
        f'/cc/v1/admin-orders/v1/order/?id={order_id}', json=body,
    )
    assert response.status == expected_status
    content = await response.json()
    if expected_filename:
        assert content == RESPONSE_CACHE[f'{expected_filename}.json']
    assert not events_processed_request_and_response


@pytest.mark.parametrize(
    [
        'order_id',
        'taxi_admin_orders_mocks',  # list of disabled externals
        'expected_status',
        'expected_filename',
        'events_processed_request_and_response',
        'body',
        'v1_driver_uniques_response',
    ],
    [
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            [],
            200,
            'admin_orders_cc_v1_test_candidates_order_'
            '0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7ad36bc7560449998acbe2c57a75c293': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
                '7f74df331eb04ad78bc2ff25ff88a8f2': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {
                'driver_uuids': [
                    '7157111f9299427ab4be21f42c6c24ae',
                    '2698ee4ecaf74b78bf3320ad3e05ae76',
                ],
            },
            {
                'uniques': [
                    {
                        'data': {
                            'unique_driver_id': (
                                '7ad36bc7560449998acbe2c57a75c293'
                            ),
                        },
                        'park_driver_profile_id': (
                            '7ad36bc7560449998acbe2c57a75c293'
                            '_7157111f9299427ab4be21f42c6c24ae'
                        ),
                    },
                    {
                        'data': {
                            'unique_driver_id': (
                                '7f74df331eb04ad78bc2ff25ff88a8f2'
                            ),
                        },
                        'park_driver_profile_id': (
                            '7f74df331eb04ad78bc2ff25ff88a8f2'
                            '_2698ee4ecaf74b78bf3320ad3e05ae76'
                        ),
                    },
                ],
            },
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            [],
            200,
            'admin_orders_cc_v1_test_candidates_2_order_'
            '0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7f74df331eb04ad78bc2ff25ff88a8f2': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {
                'driver_uuids': [
                    '7157111f9299427ab4be21f42c6c24ae',
                    '2698ee4ecaf74b78bf3320ad3e05ae76',
                ],
            },
            {
                'uniques': [
                    {
                        'data': None,
                        'park_driver_profile_id': (
                            '7ad36bc7560449998acbe2c57a75c293'
                            '_7157111f9299427ab4be21f42c6c24ae'
                        ),
                    },
                    {
                        'data': {
                            'unique_driver_id': (
                                '7f74df331eb04ad78bc2ff25ff88a8f2'
                            ),
                        },
                        'park_driver_profile_id': (
                            '7f74df331eb04ad78bc2ff25ff88a8f2'
                            '_2698ee4ecaf74b78bf3320ad3e05ae76'
                        ),
                    },
                ],
            },
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            [],
            200,
            'admin_orders_cc_v1_test_candidates_2_order_'
            '0fc10c193bbb32fa97ea5fc7cca95455',
            {
                '7ad36bc7560449998acbe2c57a75c293': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [],
                },
                '7f74df331eb04ad78bc2ff25ff88a8f2': {
                    'order_ids': ['0fc10c193bbb32fa97ea5fc7cca95455'],
                    'response': [SPECIAL_RESPONSE],
                },
            },
            {
                'driver_uuids': [
                    '7157111f9299427ab4be21f42c6c24ae',
                    '2698ee4ecaf74b78bf3320ad3e05ae76',
                ],
            },
            {
                'uniques': [
                    {
                        'data': {
                            'unique_driver_id': (
                                '7ad36bc7560449998acbe2c57a75c293'
                            ),
                        },
                        'park_driver_profile_id': (
                            '7ad36bc7560449998acbe2c57a75c293'
                            '_7157111f9299427ab4be21f42c6c24ae'
                        ),
                    },
                    {
                        'data': {
                            'unique_driver_id': (
                                '7f74df331eb04ad78bc2ff25ff88a8f2'
                            ),
                        },
                        'park_driver_profile_id': (
                            '7f74df331eb04ad78bc2ff25ff88a8f2'
                            '_2698ee4ecaf74b78bf3320ad3e05ae76'
                        ),
                    },
                ],
            },
        ),
    ],
    indirect=['taxi_admin_orders_mocks'],
)
@pytest.mark.config(**CONFIGS)
async def test_errors_scenarios_for_candidates(
        taxi_admin_orders_web,
        taxi_admin_orders_mocks,
        order_id,
        expected_status,
        expected_filename,
        events_processed_request_and_response,
        body,
        v1_driver_uniques_response,
        mockserver,
):
    @mockserver.handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_driver_uniques_retrieve_by_profiles(http_request):
        return mockserver.make_response(json=v1_driver_uniques_response)

    @mockserver.handler('/driver-metrics-storage/v3/events/processed')
    def _v3_events_processed(http_request):
        assert (
            http_request.json['unique_driver_id']
            in events_processed_request_and_response
        )
        assert (
            http_request.json['order_ids']
            == events_processed_request_and_response[
                http_request.json['unique_driver_id']
            ]['order_ids']
        )
        response = mockserver.make_response(
            json={
                'events': events_processed_request_and_response[
                    http_request.json['unique_driver_id']
                ]['response'],
            },
        )
        del events_processed_request_and_response[
            http_request.json['unique_driver_id']
        ]
        return response

    response = await taxi_admin_orders_web.post(
        f'/cc/v1/admin-orders/v1/order/?id={order_id}', json=body,
    )
    assert response.status == expected_status
    content = await response.json()
    if expected_filename:
        assert content == RESPONSE_CACHE[f'{expected_filename}.json']
    assert not events_processed_request_and_response
