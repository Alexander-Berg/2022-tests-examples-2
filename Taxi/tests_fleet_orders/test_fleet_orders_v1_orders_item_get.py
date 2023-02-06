import pytest


ENDPOINT = 'fleet/fleet-orders/v1/orders/item'


@pytest.fixture(name='personal_phones_retrieve')
def _mock_personal_phones_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock(request):
        assert request.json['id']
        return {'id': request.json['id'], 'value': request.json['id'][3:]}

    return _mock


@pytest.fixture(name='fleet_parks_list')
def _mock_fleet_parks_lis(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock(request):
        assert request.json['query']['park']['ids'] == ['another_park']
        return {
            'parks': [
                {
                    'id': 'another_park',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'another park name',
                    'org_name': 'some park org name',
                    'geodata': {'lat': 12, 'lon': 3, 'zoom': 10},
                },
            ],
        }

    return _mock


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


@pytest.mark.parametrize(
    'park_id, order_id, ordercore_respponse, expected_response',
    [
        pytest.param(
            'some_park',
            'order_id1',
            '1_order_core_404.json',
            '1_404.json',
            id='order not found',
        ),
        pytest.param(
            'some_order',
            'order_id2',
            '2_not_wl_order_core.json',
            '1_404.json',
            id='not wl',
        ),
        pytest.param(
            'some_park',
            'order_id3',
            '3_pending_order_core.json',
            '3_pending_your.json',
            id='search your park',
        ),
        pytest.param(
            'some_park',
            'order_id4',
            '4_finished_no_contractor_order_core.json',
            '4_finished_no_contractor_your.json',
            id='cancelled your park',
        ),
        pytest.param(
            'some_park',
            'order_id2',
            '4_finished_no_contractor_order_core.json',
            '4_finished_no_contractor_your_expired.json',
            id='expired',
        ),
        pytest.param(
            'another_park',
            'order_id3',
            '3_pending_order_core.json',
            '1_404.json',
            id='foreign order without your candidates',
        ),
        pytest.param(
            'another_park',
            'order_id4',
            '4_finished_no_contractor_order_core.json',
            '1_404.json',
            id='foreign order without candidates',
        ),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_no_contractor(
        mockserver,
        taxi_fleet_orders,
        load_json,
        personal_phones_retrieve,
        park_id,
        order_id,
        ordercore_respponse,
        expected_response,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        response_and_code = load_json(ordercore_respponse)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    response = await taxi_fleet_orders.get(
        ENDPOINT, params={'id': order_id}, headers=build_headers(park_id),
    )

    response_and_code = load_json(expected_response)
    assert response.status == response_and_code['status_code']
    assert response.json() == response_and_code['body']


@pytest.mark.parametrize(
    'park_id, order_id, ordercore_respponse,'
    'driver_orders_response, fleet_transactions_api_response,'
    'driver_profiles_response, personal_response, udriver_photos_response,'
    'expected_response',
    [
        pytest.param(
            'some_park',
            'order_id5',
            '5_finished_with_your_contractor_order_core.json',
            '5_finished_driver_orders.json',
            '5_finished_fleet_transactions_api.json',
            '5_finished_driver_profiles.json',
            '5_finished_personal.json',
            '5_finished_udriver_photos.json',
            '5_finished_your_you.json',
            id='completed your you',
        ),
        pytest.param(
            'another_park',
            'order_id6',
            '5_finished_with_your_contractor_order_core.json',
            '6_cancelled_by_driver_driver_orders.json',
            '6_cancelled_by_driver_fleet_transactions_api.json',
            '5_finished_driver_profiles.json',
            '5_finished_personal.json',
            '5_finished_udriver_photos.json',
            '6_cancelled_by_driver_foreign.json',
            id='cancelled_by_driver foreign your',
        ),
        pytest.param(
            'some_park',
            'order_id7',
            '7_cancelled_by_another_order_core.json',
            '6_cancelled_by_driver_driver_orders.json',
            '6_cancelled_by_driver_fleet_transactions_api.json',
            '5_finished_driver_profiles.json',
            '5_finished_personal.json',
            '5_finished_udriver_photos.json',
            '7_cancelled_by_driver_your_another.json',
            id='cancelled_by_driver your another',
        ),
        pytest.param(
            'another_park',
            'order_id6',
            '8_pending_with_previous_another_contracor_order_core.json',
            '6_cancelled_by_driver_driver_orders.json',
            '6_cancelled_by_driver_fleet_transactions_api.json',
            '5_finished_driver_profiles.json',
            '5_finished_personal.json',
            '5_finished_udriver_photos.json',
            '6_cancelled_by_driver_foreign.json',
            id='cancelled_by_driver your another(order-core pending)',
        ),
        pytest.param(
            'some_park',
            'order_id10',
            '10_finished_with_another_contractor_order_core.json',
            '5_finished_driver_orders.json',
            '5_finished_fleet_transactions_api.json',
            '5_finished_driver_profiles.json',
            '5_finished_personal.json',
            '5_finished_udriver_photos.json',
            '10_finished_your_another.json',
            id='finished your another',
        ),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_with_contractor(
        mockserver,
        taxi_fleet_orders,
        load_json,
        personal_phones_retrieve,
        fleet_parks_list,
        park_id,
        order_id,
        ordercore_respponse,
        driver_orders_response,
        fleet_transactions_api_response,
        driver_profiles_response,
        personal_response,
        udriver_photos_response,
        expected_response,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        response_and_code = load_json(ordercore_respponse)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _mock_driver_orders_track(request):
        response_and_code = load_json(driver_orders_response)
        return mockserver.make_response(
            json=response_and_code['response_track']['body'],
            status=response_and_code['response_track']['status_code'],
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _mock_driver_orders(request):
        response_and_code = load_json(driver_orders_response)
        return mockserver.make_response(
            json=response_and_code['response_bulk_retrieve']['body'],
            status=response_and_code['response_bulk_retrieve']['status_code'],
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _mock_fleet_transactions_api(request):
        response_and_code = load_json(fleet_transactions_api_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        response_and_code = load_json(driver_profiles_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _mock_personal(request):
        response_and_code = load_json(personal_response)
        return mockserver.make_response(
            json=response_and_code['driver_licenses']['body'],
            status=response_and_code['driver_licenses']['status_code'],
        )

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    def _mock_udriver_photos(request):
        response_and_code = load_json(udriver_photos_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    response = await taxi_fleet_orders.get(
        ENDPOINT, params={'id': order_id}, headers=build_headers(park_id),
    )

    response_and_code = load_json(expected_response)
    assert response.status == response_and_code['status_code']
    assert response.json() == response_and_code['body']


UDRIVER_PHOTOS_MOCK_FILE = '5_finished_udriver_photos.json'

DRIVER_ORDERS_MOCK_FILE = 'preorders_driver_orders_response.json'

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'brand': 'brand',
                'car_id': 'car_id',
                'model': 'model',
                'number': 'number',
            },
            'park_id_car_id': 'park_car_id',
        },
    ],
}


@pytest.mark.parametrize(
    'park_id, order_id, ordercore_response, driver_profiles_response,'
    'expected_response',
    [
        pytest.param(
            'park',
            'order',
            'preorders_order_core_with_forced_performer.json',
            'preorders_driver_profiles_response.json',
            'preorders_response_with_forced_contractor.json',
            id='before assignment',
        ),
        pytest.param(
            'park',
            'order',
            'preorders_order_core_with_forced_performer.json',
            'preorders_driver_profiles_response_without_car_id.json',
            'preorders_response_with_forced_contractor_without_vehicle.json',
            id='before assignment without vehicle',
        ),
        pytest.param(
            'park',
            'order',
            'preorders_order_core_with_forced_performer.json',
            'preorders_driver_profiles_response_empty.json',
            'preorders_response_without_forced_contractor.json',
            id='before assignment without driver',
        ),
        pytest.param(
            'park',
            'order',
            'preorders_order_core_with_forced_performer_with_contractor.json',
            'preorders_driver_profiles_response.json',
            'preorders_response_with_contractor.json',
            id='after assignment',
        ),
        pytest.param(
            'park',
            'order',
            'preorders_order_core_with_forced_performer_another_park.json',
            'preorders_driver_profiles_response.json',
            'preorders_response_with_contractor_from_another_park.json',
            id='after assignment with contractor from another park',
        ),
        pytest.param(
            'park',
            'order',
            'preorders_order_core_with_forced_performer_no_saas.json',
            'preorders_driver_profiles_response.json',
            'preorders_response_with_forced_contractor_no_saas.json',
            id='before assignment no saas',
        ),
        pytest.param(
            'another_park',
            'order',
            'preorders_order_core_with_forced_performer_no_saas.json',
            'preorders_driver_profiles_response.json',
            'preorders_response_with_forced_contractor_no_saas_another_park'
            '.json',
            id='before assignment no saas another park',
        ),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_preorders_order_with_forced_contractor(
        mockserver,
        taxi_fleet_orders,
        load_json,
        personal_phones_retrieve,
        fleet_parks_list,
        park_id,
        order_id,
        ordercore_response,
        driver_profiles_response,
        expected_response,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        response_and_code = load_json(ordercore_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        response_and_code = load_json(driver_profiles_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _mock_personal(request):
        return mockserver.make_response(
            json={'id': 'license_pd_id_0', 'value': 'license_number_0'},
            status=200,
        )

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    def _mock_udriver_photos(request):
        response_and_code = load_json(UDRIVER_PHOTOS_MOCK_FILE)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _mock_fleet_vehicles(request):
        return mockserver.make_response(
            json=FLEET_VEHICLES_RESPONSE, status=200,
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _mock_driver_orders(request):
        response_and_code = load_json(DRIVER_ORDERS_MOCK_FILE)
        return mockserver.make_response(
            json=response_and_code['response_bulk_retrieve']['body'],
            status=response_and_code['response_bulk_retrieve']['status_code'],
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _mock_driver_orders_track(request):
        response_and_code = load_json(DRIVER_ORDERS_MOCK_FILE)
        return mockserver.make_response(
            json=response_and_code['response_track']['body'],
            status=response_and_code['response_track']['status_code'],
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _mock_fleet_transactions_api(request):
        return mockserver.make_response(json={'transactions': []}, status=200)

    response = await taxi_fleet_orders.get(
        ENDPOINT, params={'id': order_id}, headers=build_headers(park_id),
    )

    response_and_code = load_json(expected_response)
    assert response.status == response_and_code['status_code']
    assert response.json() == response_and_code['body']


@pytest.mark.parametrize(
    'fleet_parks_response, voiceforwarding_driver, voiceforwarding_dispatcher,'
    'expected_response',
    [
        pytest.param(
            'fleet_parks_response_success.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher_no_number.xml',
            'soft_switch_no_number.json',
            id='no_number_soft_switch_for_dispatcher',
        ),
        pytest.param(
            'fleet_parks_response_success.json',
            'voiceforwarding_driver_no_ext.xml',
            'voiceforwarding_dispatcher_no_ext.xml',
            'soft_switch_use_personal_number.json',
            id='no_soft_switch_use_personal_number',
        ),
        pytest.param(
            'fleet_parks_response_success.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher_no_ext.xml',
            'soft_switch_no_ext.json',
            id='no_ext_soft_switch_for_dispatcher',
        ),
        pytest.param(
            'fleet_parks_response_success.json',
            'voiceforwarding_driver_no_number.xml',
            'voiceforwarding_dispatcher_no_number.xml',
            'soft_switch_none.json',
            id='no_ext_soft_switch_for_dispatcher2',
        ),
        pytest.param(
            'fleet_parks_response_no_provider_config.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher.xml',
            'soft_switch_none.json',
            id='no_provider_config_from_fleet-parks',
        ),
        pytest.param(
            'fleet_parks_response_no_provider_config.json',
            'voiceforwarding_driver.xml',
            'voiceforwarding_dispatcher_empty.xml',
            'soft_switch_none.json',
            id='no_clid_from_fleet-parks',
        ),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_soft_switch(
        mockserver,
        taxi_fleet_orders,
        load_json,
        load,
        fleet_parks_response,
        voiceforwarding_driver,
        voiceforwarding_dispatcher,
        expected_response,
):
    park_id = 'some_park'
    order_id = 'order_id5'
    driver_orders_response = 'soft_switch_finished_driver_orders.json'
    ordercore_respponse = 'soft_switch_finished_order_core.json'

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        response_and_code = load_json(ordercore_respponse)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _mock_driver_orders(request):
        response_and_code = load_json(driver_orders_response)
        return mockserver.make_response(
            json=response_and_code['response_bulk_retrieve']['body'],
            status=response_and_code['response_bulk_retrieve']['status_code'],
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _mock_fleet_transactions_api(request):
        return mockserver.make_response(json={}, status=429)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return mockserver.make_response(json={}, status=503)

    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_fleet_parks(request):
        assert request.query['park_id'] == 'some_park'
        response_and_code = load_json(fleet_parks_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/taximeter-api/1.x/voiceforwarding')
    def _mock_taximter_api(request):
        assert request.query['for'] in {'driver', 'dispatcher'}
        if request.query['for'] == 'driver':
            return mockserver.make_response(
                load(voiceforwarding_driver), content_type='application/xml',
            )
        return mockserver.make_response(
            load(voiceforwarding_dispatcher), content_type='application/xml',
        )

    response = await taxi_fleet_orders.get(
        ENDPOINT, params={'id': order_id}, headers=build_headers(park_id),
    )

    response_and_code = load_json(expected_response)
    assert response.status == response_and_code['status_code']
    assert response.json() == response_and_code['body']


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_your_order_with_404_from_taxi_fleet(
        mockserver, taxi_fleet_orders, personal_phones_retrieve, load_json,
):
    park_id = 'some_park'
    ordercore_respponse = '7_cancelled_by_another_order_core.json'
    expected_response = '4_finished_no_contractor_your.json'

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        response_and_code = load_json(ordercore_respponse)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/taxi-fleet/internal/v1/cards/orders/details')
    def _mock_taxi_fleet(request):
        return mockserver.make_response(
            json={'code': 'ORDER_NOT_FOUND', 'message': ''}, status=404,
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _mock_driver_orders(request):
        return mockserver.make_response(
            json={'code': '400', 'message': ''}, status=400,
        )

    response = await taxi_fleet_orders.get(
        ENDPOINT, params={'id': 'order_id4'}, headers=build_headers(park_id),
    )

    response_and_code = load_json(expected_response)
    assert response.status == response_and_code['status_code']
    assert response.json() == response_and_code['body']


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_foreign_order_with_404_from_taxi_fleet(
        mockserver, taxi_fleet_orders, personal_phones_retrieve, load_json,
):
    park_id = 'another_park'
    ordercore_respponse = '9_cancelled_by_another_twice_order_core.json'
    expected_response = '6_cancelled_by_driver_foreign.json'
    driver_orders_ok_response = '6_cancelled_by_driver_driver_orders.json'
    fleet_transactions_api_ok_resp = (
        '6_cancelled_by_driver_fleet_transactions_api.json'
    )

    driver_profiles_ok_response = '5_finished_driver_profiles.json'
    personal_ok_response = '5_finished_personal.json'
    udriver_photos_ok_response = '5_finished_udriver_photos.json'

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        response_and_code = load_json(ordercore_respponse)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _mock_driver_orders_track(request):
        if request.query['order_id'] == 'not_saved_in_taximeter_orders':
            return mockserver.make_response(
                json={'code': '404', 'message': 'not found'}, status=404,
            )
        if request.query['order_id'] == 'saved_in_taximeter_orders':
            response_and_code = load_json(driver_orders_ok_response)
            return mockserver.make_response(
                json=response_and_code['response_track']['body'],
                status=response_and_code['response_track']['status_code'],
            )
        assert False
        return None

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _mock_fleet_transactions_api(request):
        response_and_code = load_json(fleet_transactions_api_ok_resp)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _mock_driver_orders(request):
        if (
                request.json['query']['park']['order']['ids'][0]
                == 'not_saved_in_taximeter_orders'
        ):
            return mockserver.make_response(
                json={'code': '400', 'message': ''}, status=400,
            )
        if (
                request.json['query']['park']['order']['ids'][0]
                == 'saved_in_taximeter_orders'
        ):
            return mockserver.make_response(
                json=load_json('6_cancelled_by_driver_driver_orders.json')[
                    'response_bulk_retrieve'
                ]['body'],
                status=200,
            )
        assert False
        return None

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        response_and_code = load_json(driver_profiles_ok_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _mock_personal(request):
        response_and_code = load_json(personal_ok_response)
        return mockserver.make_response(
            json=response_and_code['driver_licenses']['body'],
            status=response_and_code['driver_licenses']['status_code'],
        )

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    def _mock_udriver_photos(request):
        response_and_code = load_json(udriver_photos_ok_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    response = await taxi_fleet_orders.get(
        ENDPOINT, params={'id': 'order_id6'}, headers=build_headers(park_id),
    )

    response_and_code = load_json(expected_response)
    assert response.status == response_and_code['status_code']
    assert response.json() == response_and_code['body']
