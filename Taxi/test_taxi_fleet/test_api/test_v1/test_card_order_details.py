import aiohttp.web
import pytest

from taxi.clients import personal


API_ENDPOINT = '/api/v1/cards/orders/details'
INTERNAL_ENDPOINT = '/internal/v1/cards/orders/details'


FLEET_TRANSACTIONS_API_GROUPS = [
    {
        'group_id': 'platform_card',
        'categories': [
            {'category_id': 'card'},
            {'category_id': 'compensation'},
        ],
    },
    {'group_id': 'platform_tip', 'categories': [{'category_id': 'tip'}]},
    {'group_id': 'platform_bonus', 'categories': [{'category_id': 'bonus'}]},
    {
        'group_id': 'platform_fees',
        'categories': [
            {'category_id': 'subscription'},
            {'category_id': 'subscription_vat'},
            {'category_id': 'platform_ride_fee'},
            {'category_id': 'platform_ride_vat'},
            {'category_id': 'platform_bonus_fee'},
            {'category_id': 'platform_reposition_fee'},
        ],
    },
    {
        'group_id': 'partner_fees',
        'categories': [
            {'category_id': 'partner_subscription_fee'},
            {'category_id': 'partner_ride_fee'},
            {'category_id': 'partner_bonus_fee'},
            {'category_id': 'partner_service_transfer_commission'},
        ],
    },
]
TAXI_FLEET_ORDER_CATEGORIES = {
    'frontend': [
        'econom',
        'comfort',
        'business',
        'minivan',
        'vip',
        'wagon',
        'comfort_plus',
        'express',
        'pool',
        'start',
        'standard',
        'ultimate',
        'maybach',
        'promo',
        'premium_van',
        'premium_suv',
        'suv',
        'personal_driver',
        'cargo',
        'courier',
        'eda',
        'lavka',
    ],
}

CANCELLATION_DESCRIPTION_KEYS = {
    'reject: manual': 'reject_manual',
    'user': 'user',
}


async def _make_request(web_app_client, headers, endpoint, park_id, order_id):
    if endpoint == API_ENDPOINT:
        return await web_app_client.get(
            endpoint, headers=headers, params={'order_id': order_id},
        )
    if endpoint == INTERNAL_ENDPOINT:
        return await web_app_client.get(
            endpoint, params={'park_id': park_id, 'order_id': order_id},
        )

    assert False, 'unexpected endpoint'


async def _test_func(
        mockserver,
        web_app_client,
        headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        stub_file_name,
        patch,
        endpoint,
        is_test_soft_switch=False,
        soft_switch_response='',
        voiceforwarding_driver='voiceforwarding_driver.xml',
        voiceforwarding_dispatcher='voiceforwarding_dispatcher.xml',
        fleet_parks_response='fleet_parks_response_success.json',
):

    stub = load_json(stub_file_name)

    @mock_driver_orders('/v1/parks/orders/track')
    async def _track_list(request):
        assert request.query == stub['driver_orders']['track']['request']
        return aiohttp.web.json_response(
            stub['driver_orders']['track']['response'],
        )

    @mock_driver_orders('/v1/parks/orders/bulk_retrieve')
    async def _list_orders(request):
        assert (
            request.json == stub['driver_orders']['bulk_retrieve']['request']
        )
        return aiohttp.web.json_response(
            stub['driver_orders']['bulk_retrieve']['response'],
        )

    @mock_order_core('/v1/tc/order-fields')
    async def _order_proc_fields(request):
        assert request.json == stub['order_core']['order_fields']['request']
        return aiohttp.web.json_response(
            stub['order_core']['order_fields']['response'],
        )

    @mock_udriver_photos('/driver-photos/v1/last-not-rejected-photo')
    async def _mock_udriver_photos(request):
        assert request.query == stub['udriver_photos']['request']
        return aiohttp.web.json_response(stub['udriver_photos']['response'])

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['request']
        return aiohttp.web.json_response(stub['transactions']['response'])

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _driver_profile_retrieve(request):
        assert request.json == stub['driver_profiles']['request']
        return aiohttp.web.json_response(stub['driver_profiles']['response'])

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _personal_retrieve(data_type, request_ids):
        if data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES:
            assert request_ids == stub['personal']['license']['request_ids']
            return stub['personal']['license']['response']

        if data_type == personal.PERSONAL_TYPE_PHONES:
            assert request_ids == stub['personal']['phones']['request_ids']
            return stub['personal']['phones']['response']

        assert False

    @mock_fleet_parks('/v1/parks')
    async def _fleet_parks(request):
        arg_dict = {key: request.args[key] for key in request.args}
        assert arg_dict == {'park_id': '7ad36bc7560449998acbe2c57a75c293'}
        fleet_parks = load_json(fleet_parks_response)
        return aiohttp.web.json_response(fleet_parks['response'])

    @mockserver.json_handler('/taximeter-api/1.x/voiceforwarding')
    async def _taximter_api(request):
        arg_dict = {key: request.args[key] for key in request.args}
        assert arg_dict['for'] in {'driver', 'dispatcher'}
        if arg_dict['for'] == 'driver':
            assert arg_dict == {
                'clid': '100500',
                'apikey': 'ba4a40f6e11f46f6b20ee7fa6000565d',
                'orderid': 'f629f3c12a25346da56af55f27e8202f',
                'for': 'driver',
            }
            return mockserver.make_response(
                load(voiceforwarding_driver), content_type='application/xml',
            )
        if arg_dict['for'] == 'dispatcher':
            assert arg_dict == {
                'clid': '100500',
                'apikey': 'ba4a40f6e11f46f6b20ee7fa6000565d',
                'orderid': 'f629f3c12a25346da56af55f27e8202f',
                'for': 'dispatcher',
            }
            return mockserver.make_response(
                load(voiceforwarding_dispatcher),
                content_type='application/xml',
            )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def _unique_drivers(request):
        assert request.json == stub['unique_drivers']['request']
        return aiohttp.web.json_response(stub['unique_drivers']['response'])

    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    async def _driver_metrics_storage(request):
        assert request.json == stub['driver_metrics_storage']['request']
        return aiohttp.web.json_response(
            stub['driver_metrics_storage']['response'],
        )

    response = await _make_request(
        web_app_client,
        headers,
        endpoint,
        '7ad36bc7560449998acbe2c57a75c293',
        stub['service']['request']['order_id'],
    )
    assert response.status == stub['service']['response_code']

    if is_test_soft_switch:
        expected_client = load_json(soft_switch_response)
        stub['service']['response'] = expected_client['response']

    assert await response.json() == stub['service']['response']


@pytest.mark.now('2020-06-10T00:00:00+03:00')
@pytest.mark.config(
    FLEET_TRANSACTIONS_API_GROUPS=FLEET_TRANSACTIONS_API_GROUPS,
)
@pytest.mark.config(TAXI_FLEET_ORDER_CATEGORIES=TAXI_FLEET_ORDER_CATEGORIES)
@pytest.mark.parametrize(
    'stub_file_name',
    [
        'success.json',
        'success_partially_hidden.json',
        'success_hard_date.json',
        'success_route_changes_wrong.json',
        'not_found.json',
        'success_track.json',
    ],
)
@pytest.mark.parametrize('endpoint', [API_ENDPOINT, INTERNAL_ENDPOINT])
async def test_by_stubs(
        mockserver,
        web_app_client,
        headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        stub_file_name,
        patch,
        endpoint,
):
    await _test_func(
        mockserver,
        web_app_client,
        headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        stub_file_name,
        patch,
        endpoint,
    )


@pytest.mark.now('2019-09-16T15:00:00.000000+03:00')
@pytest.mark.config(
    FLEET_TRANSACTIONS_API_GROUPS=FLEET_TRANSACTIONS_API_GROUPS,
)
@pytest.mark.config(TAXI_FLEET_ORDER_CATEGORIES=TAXI_FLEET_ORDER_CATEGORIES)
@pytest.mark.parametrize(
    'soft_switch_response, voiceforwarding_driver,'
    'voiceforwarding_dispatcher, fleet_parks_response',
    [
        pytest.param(
            'soft_switch_no_number.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher_no_number.xml',
            'fleet_parks_response_success.json',
            id='no_number_soft_switch_for_dispatcher',
        ),
        pytest.param(
            'soft_switch_use_personal_number.json',
            'voiceforwarding_driver_no_ext.xml',
            'voiceforwarding_dispatcher_no_ext.xml',
            'fleet_parks_response_success.json',
            id='no_soft_switch_use_personal_number',
        ),
        pytest.param(
            'soft_switch_use_for_drive.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher_no_number.xml',
            'fleet_parks_response_success.json',
            id='no_soft_switch_for_dispatcher_use_for_driver',
        ),
        pytest.param(
            'soft_switch_no_ext.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher_no_ext.xml',
            'fleet_parks_response_success.json',
            id='no_ext_soft_switch_for_dispatcher',
        ),
        pytest.param(
            'soft_switch_none.json',
            'voiceforwarding_driver_no_number.xml',
            'voiceforwarding_dispatcher_no_number.xml',
            'fleet_parks_response_success.json',
            id='no_ext_soft_switch_for_dispatcher',
        ),
        pytest.param(
            'soft_switch_none.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher.xml',
            'fleet_parks_response_no_provider_config.json',
            id='no_provider_config_from_fleet-parks',
        ),
        pytest.param(
            'soft_switch_none.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher_empty.xml',
            'fleet_parks_response_no_clid.json',
            id='no_clid_from_fleet-parks',
        ),
    ],
)
@pytest.mark.parametrize('endpoint', [API_ENDPOINT, INTERNAL_ENDPOINT])
async def test_soft_switch(
        mockserver,
        web_app_client,
        headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        patch,
        endpoint,
        soft_switch_response,
        voiceforwarding_driver,
        voiceforwarding_dispatcher,
        fleet_parks_response,
):
    await _test_func(
        mockserver,
        web_app_client,
        headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        'success.json',
        patch,
        endpoint,
        True,
        soft_switch_response,
        voiceforwarding_driver,
        voiceforwarding_dispatcher,
        fleet_parks_response,
    )


@pytest.mark.now('2019-09-16T16:00:00.000000+03:00')
@pytest.mark.config(
    FLEET_TRANSACTIONS_API_GROUPS=FLEET_TRANSACTIONS_API_GROUPS,
)
@pytest.mark.config(TAXI_FLEET_ORDER_CATEGORIES=TAXI_FLEET_ORDER_CATEGORIES)
@pytest.mark.parametrize('endpoint', [API_ENDPOINT, INTERNAL_ENDPOINT])
async def test_soft_switch_more_then_hour(
        mockserver,
        web_app_client,
        headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        patch,
        endpoint,
):
    await _test_func(
        mockserver,
        web_app_client,
        headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        'success.json',
        patch,
        endpoint,
        True,
        'soft_switch_none.json',
    )


@pytest.mark.now('2019-09-16T16:00:00.000000+03:00')
@pytest.mark.config(
    FLEET_TRANSACTIONS_API_GROUPS=FLEET_TRANSACTIONS_API_GROUPS,
)
@pytest.mark.config(TAXI_FLEET_ORDER_CATEGORIES=TAXI_FLEET_ORDER_CATEGORIES)
@pytest.mark.config(
    DRIVER_ORDERS_CANCELLATION_DESCRIPTION_KEYS=CANCELLATION_DESCRIPTION_KEYS,
)
@pytest.mark.parametrize(
    'endpoint, is_support, stub_file_name',
    [
        (API_ENDPOINT, False, 'success_cancellation_description.json'),
        (API_ENDPOINT, True, 'success_cancellation_description_support.json'),
        (
            INTERNAL_ENDPOINT,
            False,
            'success_cancellation_description_internal.json',
        ),
    ],
)
async def test_cancellation_description(
        mockserver,
        web_app_client,
        headers,
        headers_support,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        stub_file_name,
        patch,
        endpoint,
        is_support,
):
    test_headers = headers_support if is_support else headers

    await _test_func(
        mockserver,
        web_app_client,
        test_headers,
        mock_driver_orders,
        mock_order_core,
        mock_fleet_transactions_api,
        mock_udriver_photos,
        mock_driver_profiles,
        mock_fleet_parks,
        load_json,
        load,
        stub_file_name,
        patch,
        endpoint,
    )
