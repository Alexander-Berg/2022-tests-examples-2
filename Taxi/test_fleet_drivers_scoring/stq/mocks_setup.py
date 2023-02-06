DRIVER_PROFILE1 = {
    'driver_license': 'licence_pd',
    'profiles': [
        {
            'data': {'park_id': 'park1', 'car_id': 'car1', 'uuid': 'driver1'},
            'revision': '0_1234567_4',
            'park_driver_profile_id': 'park1_driver1',
        },
        {
            'data': {'park_id': 'park2', 'uuid': 'driver2'},
            'revision': '0_1234567_4',
            'park_driver_profile_id': 'park2_driver2',
        },
    ],
}

UNIQUE_DRIVERS_RESPONSE_OK = {
    'uniques': [
        {
            'park_driver_profile_id': 'park1_driver1',
            'data': {'unique_driver_id': 'udid1'},
        },
        {
            'park_driver_profile_id': 'park2_driver2',
            'data': {'unique_driver_id': 'udid1'},
        },
    ],
}

FLEET_PARKS_RESPONSE = [
    {
        'parks': [
            {
                'id': 'park1',
                'login': 'login1',
                'name': 'super_park1',
                'is_active': True,
                'city_id': 'city1',
                'locale': 'locale1',
                'is_billing_enabled': False,
                'is_franchising_enabled': False,
                'demo_mode': False,
                'country_id': 'rus',
                'provider_config': {'clid': 'clid1', 'type': 'production'},
                'tz_offset': 3,
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            },
            {
                'id': 'park2',
                'login': 'login2',
                'name': 'super_park2',
                'is_active': True,
                'city_id': 'city2',
                'locale': 'locale2',
                'is_billing_enabled': False,
                'is_franchising_enabled': False,
                'demo_mode': False,
                'country_id': 'rus',
                'provider_config': {'clid': 'clid2', 'type': 'production'},
                'tz_offset': 3,
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            },
        ],
    },
]

BILLING_REPLICATION_RESPONSE = [
    {
        'ID': 1234,
        'EXTERNAL_ID': '334699/19',
        'PERSON_ID': 8976460,
        'IS_ACTIVE': 1,
        'IS_SIGNED': 1,
        'IS_SUSPENDED': 0,
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'NETTING_PCT': '100',
        'LINK_CONTRACT_ID': None,
        'SERVICES': [128, 605, 626, 111, 124, 125],
        'NDS_FOR_RECEIPT': -1,
        'OFFER_ACCEPTED': 1,
        'NDS': None,
        'PAYMENT_TYPE': 2,
        'PARTNER_COMMISSION_PCT': None,
        'PARTNER_COMMISSION_PCT2': None,
        'IND_BEL_NDS_PERCENT': None,
        'END_DT': None,
        'FINISH_DT': None,
        'DT': '2019-07-15 00:00:00',
        'CONTRACT_TYPE': 9,
        'IND_BEL_NDS': None,
        'COUNTRY': None,
        'IS_FAXED': None,
        'IS_DEACTIVATED': None,
        'IS_CANCELLED': None,
    },
]

PARKS_REPLICA_RESPONSE = {'billing_client_id': 'bill_clid'}

TARIFFS_RESPONSE = {
    'zones': [
        {
            'name': 'spb',
            'time_zone': 'Europe/Moscow',
            'country': 'rus',
            'translation': 'Санкт-Петербург',
        },
    ],
}

AGGLOMERATIONS_RESPONSE = {'oebs_mvp_id': 'ASKc'}

RESPONSE_TERRITORIES = {'_id': 'rus', 'currency': 'RUB'}

BILLING_ORDERS_RESPONSE = {
    'orders': [
        {
            'topic': 'taxi/partner_scoring/park_id/park_id_check_id',
            'external_ref': '1',
            'doc_id': 100500,
        },
    ],
}

PARKS_ACTIVATION_RESPONSE = {
    'parks_activation': [
        {
            'revision': 221206,
            'last_modified': '2019-11-21T12:12:29.602',
            'park_id': '100500',
            'city_id': 'Москва',
            'data': {
                'deactivated': False,
                'can_cash': True,
                'can_card': True,
                'can_corp': True,
                'can_coupon': True,
            },
        },
    ],
}

FLEET_PAYOUTS_RESPONSE = {'fleet_version': 'simple'}

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'brand': 'BMW',
                'cert_verification': True,
                'model': 'X6',
                'number': 'AA001777',
                'number_normalized': 'AA001777',
                'registration_cert': 'XW8ED45J7DK123456',
            },
            'park_id_car_id': 'park1_car1',
        },
    ],
}

FLEET_VEHICLES_RESPONSE_BY_NUMBER = {
    'cars': [
        {
            'car_number_normalized': 'AA001777',
            'cars': [
                {
                    'data': {'car_id': 'car1', 'park_id': 'park1'},
                    'park_id_car_id': 'park1_car1',
                },
                {
                    'data': {'car_id': 'car2', 'park_id': 'park2'},
                    'park_id_car_id': 'park2_car2',
                },
            ],
        },
    ],
}

DRIVER_ORDERS_RESPONSE = {
    'park1': {
        'orders': [
            {
                'id': 'order_id',
                'short_id': 1,
                'status': 'complete',
                'created_at': '2020-08-07T08:27:41.157339+00:00',
                'booked_at': '2020-08-07T08:32:00+00:00',
                'provider': 'platform',
                'amenities': [],
                'address_from': {
                    'address': 'Москва, Садовническая улица, 78с1',
                    'lat': 55.7379065844,
                    'lon': 37.6417814247,
                },
                'driver_profile': {
                    'id': 'driver1',
                    'name': 'Иванов Иван Иваныч',
                },
                'route_points': [],
                'events': [],
            },
        ],
        'limit': 1,
    },
    'park2': {
        'orders': [
            {
                'id': 'order_id',
                'short_id': 1,
                'status': 'complete',
                'created_at': '2020-08-07T08:27:41.157339+00:00',
                'booked_at': '2020-08-07T08:32:00+00:00',
                'provider': 'platform',
                'amenities': [],
                'address_from': {
                    'address': 'Москва, Садовническая улица, 78с1',
                    'lat': 55.7379065844,
                    'lon': 37.6417814247,
                },
                'driver_profile': {
                    'id': 'driver2',
                    'name': 'Иванов Иван Иваныч',
                },
                'route_points': [],
                'events': [],
            },
        ],
        'limit': 1,
    },
}


def setup_mocks(
        _mock_driver_profiles,
        _mock_unique_drivers,
        _mock_fleet_parks,
        _mock_billing_replication,
        _mock_parks_replica,
        _mock_tariffs,
        _mock_agglomerations,
        _mock_billing_orders,
        _mock_territories,
        _mock_parks_activation,
        _mock_fleet_payouts,
        _mock_fleet_vehicles=None,
        _mock_driver_orders=None,
        driver_profiles_response=None,
        unique_drivers_response=None,
        fleet_parks_response=None,
        billing_replication_response=None,
        parks_replica_response=None,
        tariffs_response=None,
        agglomerations_response=None,
        billing_orders_response=None,
        territories_response=None,
        parks_activation_response=None,
        fleet_payouts_response=None,
        fleet_vehicles_response=None,
        fleet_vehicles_response_by_number=None,
        driver_orders_response=None,
):
    _mock_driver_profiles.set_retrieve_by_license_resp(
        driver_profiles_response or {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        unique_drivers_response or UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_fleet_parks.set_parks_list_responses(
        fleet_parks_response or FLEET_PARKS_RESPONSE,
    )
    _mock_billing_replication.set_billing_replication_resp(
        billing_replication_response or BILLING_REPLICATION_RESPONSE,
    )
    _mock_parks_replica.set_parks_replica_response(
        parks_replica_response or PARKS_REPLICA_RESPONSE,
    )
    _mock_tariffs.set_tariffs_response(tariffs_response or TARIFFS_RESPONSE)
    _mock_agglomerations.set_agglomerations_response(
        agglomerations_response or AGGLOMERATIONS_RESPONSE,
    )
    _mock_billing_orders.set_billing_orders_response(
        billing_orders_response or BILLING_ORDERS_RESPONSE,
    )
    _mock_territories.set_countries_retrieve_response(
        territories_response or RESPONSE_TERRITORIES,
    )
    _mock_parks_activation.set_parks_activation_response(
        parks_activation_response or PARKS_ACTIVATION_RESPONSE,
    )
    _mock_fleet_payouts.set_fleet_version_response(
        fleet_payouts_response or FLEET_PAYOUTS_RESPONSE,
    )
    if _mock_fleet_vehicles:
        _mock_fleet_vehicles.set_vehicles_retrieve_response(
            fleet_vehicles_response or FLEET_VEHICLES_RESPONSE,
        )
        _mock_fleet_vehicles.set_retrieve_by_number_resp(
            fleet_vehicles_response_by_number
            or FLEET_VEHICLES_RESPONSE_BY_NUMBER,
        )
    if _mock_driver_orders:
        _mock_driver_orders.set_orders_resp(
            driver_orders_response or DRIVER_ORDERS_RESPONSE,
        )
