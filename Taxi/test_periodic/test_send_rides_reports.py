import aiohttp.web
import pytest

from testsuite.utils import http

DEFAULT_JOB_CONFIG = {
    'is_enabled': True,
    'aggregation_delay_seconds': 300,
    'min_ride_start_date': '2010-07-01T12:08:48.372+02:00',
    'service_fee_entries': [
        {'agreement_id': 'taxi/park_ride', 'sub_accounts': ['payment/cash']},
    ],
    'commission_entries': [
        {
            'agreement_id': 'taxi/park_ride',
            'sub_accounts': ['total/commission'],
        },
    ],
    'sub_account_payment_type_mapping': {'payment/cash': 'cash'},
    'eds_client_id': 'latvia-eds-client-id',
    'order_data_aggregation_limit_seconds': 172800,
    'driver_license_removable_prefixes': ['LAT'],
}


@pytest.fixture
async def _common_data_aggregation(mockserver):
    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    async def _get_order(request: http.Request):
        assert request.json == {
            'query': {
                'park': {
                    'id': 'p2',
                    'order': {
                        'ids': ['order2'],
                        'cut_hidden_fields': False,
                        'return_is_partially_hidden': False,
                    },
                },
            },
        }
        return {
            'orders': [
                {
                    'id': 'order2',
                    'order': {
                        'short_id': 2,
                        'status': 'complete',
                        'created_at': '2020-06-01T11:00:00+00:00',
                        'booked_at': '2020-06-01T11:00:00+00:00',
                        'transporting_at': '2020-06-01T11:30:00+00:00',
                        'ended_at': '2020-06-01T11:55:00+00:00',
                        'provider': 'platform',
                        'mileage': '1000.0',
                        'driver_profile': {'id': 'c2'},
                        'vehicle': {'id': 'v2'},
                    },
                },
            ],
        }

    @mockserver.json_handler('/latvia-eds/api/taxi/auth')
    async def _auth(request: http.Request):
        assert request.json == {
            'grant_type': 'client_credentials',
            'client_id': 'latvia-eds-client-id',
            'client_secret': 'SecRet',
        }
        return {
            'access_token': 'access_token',
            'token_type': 'bearer',
            'expires_in': 100500,
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    async def _get_vehicle(request: http.Request):
        assert request.json == {
            'id_in_set': ['p2_v2'],
            'projection': [
                'park_id_car_id',
                'data.number_normalized',
                'data.number',
                'data.carrier_permit_owner_id',
            ],
        }
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'p2_v2',
                    'data': {
                        'number': 'NUM-1234',
                        'carrier_permit_owner_id': 'CPOI2',
                    },
                },
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _get_contractor(request: http.Request):
        assert request.json == {
            'id_in_set': ['p2_c2'],
            'projection': [
                'park_driver_profile_id',
                'data.license.pd_id',
                'data.tax_identification_number_pd_id',
            ],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'p2_c2',
                    'data': {
                        'license': {'pd_id': 'DL_PD_ID2'},
                        'tax_identification_number_pd_id': 'TIN_PD_ID2',
                    },
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    async def _get_personal_dl(request: http.Request):
        assert request.json == {'id': 'DL_PD_ID2', 'primary_replica': False}
        return {'id': 'DL_PD_ID2', 'value': 'LATAA112233'}

    @mockserver.json_handler('/personal/v1/tins/retrieve')
    async def _get_personal_tin(request: http.Request):
        assert request.json == {'id': 'TIN_PD_ID2', 'primary_replica': False}
        return {'id': 'TIN_PD_ID2', 'value': '01234567890'}

    @mockserver.json_handler('/parks/legal-entities')
    async def _get_legal_entity(request: http.Request):
        assert dict(request.query) == {'id': 'CPOI2', 'park_id': 'p2'}
        return {
            'id': 'CPOI2',
            'park_id': 'p2',
            'registration_number': '12345678901',
            'address': 'address',
            'legal_type': 'legal',
            'name': 'name',
            'type': 'carrier_permit_owner',
            'work_hours': 'work_hours',
        }


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['income_events.sql'])
@pytest.mark.config(LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG=DEFAULT_JOB_CONFIG)
async def test_send_rides_reports(
        taxi_latvia_rides_reports, mockserver, pgsql, _common_data_aggregation,
):
    @mockserver.json_handler('/latvia-eds/api/taxi/carriage')
    async def _carriage(request: http.Request):
        assert request.json == {
            'CarriersTaxpayerCode': '12345678901',
            'DriversPersonCode': '01234567890',
            'NumberPlate': 'NUM1234',
            'StartDateTime': '2020-06-01T11:30:00+00:00',
            'EndDateTime': '2020-06-01T11:55:00+00:00',
            'Distance': 1.0,
            'ServiceFee': 20.0,
            'PaymentType': 'cash',
            'Commission': 5.000001,
        }
        return aiohttp.web.Response(status=201)

    await taxi_latvia_rides_reports.run_task('send-rides-reports')

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """SELECT entry_id, state
        FROM latvia_rides_reports.order_income_events
        ORDER BY entry_id
        """,
    )
    result = list(cursor)
    assert result == [
        (1, 'FAILED'),
        (2, 'SENT_AS_SERVICE_FEE'),
        (3, 'SENT_AS_COMMISSION'),
        (4, 'IGNORED_BY_CONFIG'),
        (10, 'NEW'),
    ]

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """
        SELECT park_id, order_id, payment_type
        FROM latvia_rides_reports.reports
        """,
    )
    assert list(cursor) == [('p2', 'order2', 'cash')]


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['income_events.sql'])
@pytest.mark.config(LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG=DEFAULT_JOB_CONFIG)
async def test_send_rides_reports_no_tin_fallback(
        taxi_latvia_rides_reports, mockserver, pgsql, _common_data_aggregation,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _get_contractor(request: http.Request):
        assert request.json == {
            'id_in_set': ['p2_c2'],
            'projection': [
                'park_driver_profile_id',
                'data.license.pd_id',
                'data.tax_identification_number_pd_id',
            ],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'p2_c2',
                    'data': {'license': {'pd_id': 'DL_PD_ID2'}},
                },
            ],
        }

    @mockserver.json_handler('/latvia-eds/api/taxi/carriage')
    async def _carriage(request: http.Request):
        assert request.json == {
            'CarriersTaxpayerCode': '12345678901',
            'DriversPersonCode': 'AA112233000',
            'NumberPlate': 'NUM1234',
            'StartDateTime': '2020-06-01T11:30:00+00:00',
            'EndDateTime': '2020-06-01T11:55:00+00:00',
            'Distance': 1.0,
            'ServiceFee': 20.0,
            'PaymentType': 'cash',
            'Commission': 5.000001,
        }
        return aiohttp.web.Response(status=201)

    await taxi_latvia_rides_reports.run_task('send-rides-reports')

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """SELECT entry_id, state
        FROM latvia_rides_reports.order_income_events
        ORDER BY entry_id
        """,
    )
    result = list(cursor)
    assert result == [
        (1, 'FAILED'),
        (2, 'SENT_AS_SERVICE_FEE'),
        (3, 'SENT_AS_COMMISSION'),
        (4, 'IGNORED_BY_CONFIG'),
        (10, 'NEW'),
    ]

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        'SELECT park_id, order_id FROM latvia_rides_reports.reports',
    )
    assert list(cursor) == [('p2', 'order2')]


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['income_events.sql'])
@pytest.mark.config(LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG=DEFAULT_JOB_CONFIG)
async def test_send_report_dublicate(
        taxi_latvia_rides_reports, mockserver, pgsql, _common_data_aggregation,
):
    @mockserver.json_handler('/latvia-eds/api/taxi/carriage')
    async def _carriage(request: http.Request):
        assert request.json == {
            'CarriersTaxpayerCode': '12345678901',
            'DriversPersonCode': '01234567890',
            'NumberPlate': 'NUM1234',
            'StartDateTime': '2020-06-01T11:30:00+00:00',
            'EndDateTime': '2020-06-01T11:55:00+00:00',
            'Distance': 1.0,
            'ServiceFee': 20.0,
            'PaymentType': 'cash',
            'Commission': 5.000001,
        }
        return aiohttp.web.json_response(
            {'Message': 'Ieraksts ar identiskiem datiem jau izveidots.'},
            status=409,
        )

    await taxi_latvia_rides_reports.run_task('send-rides-reports')

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """SELECT entry_id, state
        FROM latvia_rides_reports.order_income_events
        ORDER BY entry_id
        """,
    )
    result = list(cursor)
    assert result == [
        (1, 'FAILED'),
        (2, 'SENT_AS_SERVICE_FEE'),
        (3, 'SENT_AS_COMMISSION'),
        (4, 'IGNORED_BY_CONFIG'),
        (10, 'NEW'),
    ]

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        'SELECT park_id, order_id FROM latvia_rides_reports.reports',
    )
    assert list(cursor) == [('p2', 'order2')]


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['income_events.sql'])
@pytest.mark.config(LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG=DEFAULT_JOB_CONFIG)
async def test_send_report_invalid(
        taxi_latvia_rides_reports, mockserver, pgsql, _common_data_aggregation,
):
    @mockserver.json_handler('/latvia-eds/api/taxi/carriage')
    async def _carriage(request: http.Request):
        assert request.json == {
            'CarriersTaxpayerCode': '12345678901',
            'DriversPersonCode': '01234567890',
            'NumberPlate': 'NUM1234',
            'StartDateTime': '2020-06-01T11:30:00+00:00',
            'EndDateTime': '2020-06-01T11:55:00+00:00',
            'Distance': 1.0,
            'ServiceFee': 20.0,
            'PaymentType': 'cash',
            'Commission': 5.000001,
        }
        return aiohttp.web.json_response(
            {
                'Message': 'The request is invalid.',
                'ModelState': {
                    'value.ServiceFee': [
                        (
                            'Lauka "ServiceFee" vērtībai jābūt '
                            'robežās no 0 līdz 1000000000.'
                        ),
                    ],
                },
            },
            status=400,
        )

    await taxi_latvia_rides_reports.run_task('send-rides-reports')

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """SELECT entry_id, state
        FROM latvia_rides_reports.order_income_events
        ORDER BY entry_id
        """,
    )
    result = list(cursor)
    assert result == [
        (1, 'FAILED'),
        (2, 'FAILED'),
        (3, 'FAILED'),
        (4, 'FAILED'),
        (10, 'NEW'),
    ]

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        'SELECT park_id, order_id FROM latvia_rides_reports.reports',
    )
    assert list(cursor) == []


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['stale_income_events.sql'])
@pytest.mark.config(
    LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG={
        'is_enabled': True,
        'aggregation_delay_seconds': 300,
        'min_ride_start_date': '2010-07-01T12:08:48.372+02:00',
        'service_fee_entries': [
            {
                'agreement_id': 'taxi/park_ride',
                'sub_accounts': ['payment/cash'],
            },
        ],
        'commission_entries': [
            {
                'agreement_id': 'taxi/park_ride',
                'sub_accounts': ['total/commission'],
            },
        ],
        'sub_account_payment_type_mapping': {'payment/cash': 'cash'},
        'eds_client_id': 'latvia-eds-client-id',
        'order_data_aggregation_limit_seconds': 10,
    },
)
async def test_fail_if_no_order_data(
        taxi_latvia_rides_reports, mockserver, pgsql,
):
    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    async def _get_order(request: http.Request):
        assert request.json == {
            'query': {
                'park': {
                    'id': 'p1',
                    'order': {
                        'ids': ['order1'],
                        'cut_hidden_fields': False,
                        'return_is_partially_hidden': False,
                    },
                },
            },
        }
        return {'orders': [{'id': 'order1'}]}

    @mockserver.json_handler('/latvia-eds/api/taxi/auth')
    async def _auth(request: http.Request):
        assert request.json == {
            'grant_type': 'client_credentials',
            'client_id': 'latvia-eds-client-id',
            'client_secret': 'SecRet',
        }
        return {
            'access_token': 'access_token',
            'token_type': 'bearer',
            'expires_in': 100500,
        }

    await taxi_latvia_rides_reports.run_task('send-rides-reports')

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """SELECT entry_id, state
        FROM latvia_rides_reports.order_income_events
        ORDER BY entry_id
        """,
    )
    result = list(cursor)
    assert result == [(1, 'FAILED')]


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['income_events.sql'])
@pytest.mark.config(LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG=DEFAULT_JOB_CONFIG)
async def test_fail_if_broken_order_data(
        taxi_latvia_rides_reports, mockserver, pgsql,
):
    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    async def _get_order(request: http.Request):
        assert request.json == {
            'query': {
                'park': {
                    'id': 'p2',
                    'order': {
                        'ids': ['order2'],
                        'cut_hidden_fields': False,
                        'return_is_partially_hidden': False,
                    },
                },
            },
        }
        return {
            'orders': [
                {
                    'id': 'order2',
                    'order': {
                        'short_id': 2,
                        'status': 'complete',
                        'created_at': '2020-06-01T11:00:00+00:00',
                        'booked_at': '2020-06-01T11:00:00+00:00',
                        'transporting_at': '2020-06-01T11:30:00+00:00',
                        'ended_at': '2020-06-01T11:55:00+00:00',
                        'provider': 'platform',
                        'mileage': '1000.0',
                        'driver_profile': {'id': 'd2'},
                        'vehicle': {'id': ''},
                    },
                },
            ],
        }

    @mockserver.json_handler('/latvia-eds/api/taxi/auth')
    async def _auth(request: http.Request):
        assert request.json == {
            'grant_type': 'client_credentials',
            'client_id': 'latvia-eds-client-id',
            'client_secret': 'SecRet',
        }
        return {
            'access_token': 'access_token',
            'token_type': 'bearer',
            'expires_in': 100500,
        }

    await taxi_latvia_rides_reports.run_task('send-rides-reports')

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """SELECT entry_id, state
        FROM latvia_rides_reports.order_income_events
        ORDER BY entry_id
        """,
    )
    result = list(cursor)
    assert result == [
        (1, 'FAILED'),
        (2, 'FAILED'),
        (3, 'FAILED'),
        (4, 'FAILED'),
        (10, 'NEW'),
    ]


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['income_events.sql'])
@pytest.mark.config(LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG=DEFAULT_JOB_CONFIG)
async def test_send_rides_reports_network_fail(
        taxi_latvia_rides_reports, mockserver, pgsql, _common_data_aggregation,
):
    @mockserver.json_handler('/latvia-eds/api/taxi/carriage')
    async def _carriage(request: http.Request):
        return aiohttp.web.Response(status=429)

    await taxi_latvia_rides_reports.run_task('send-rides-reports')


@pytest.mark.now('2020-06-01T12:00:00')
@pytest.mark.pgsql('latvia_rides_reports', files=['expired_event.sql'])
@pytest.mark.config(
    LATVIA_RIDES_REPORTS_SEND_REPORTS_CFG={
        'is_enabled': True,
        'aggregation_delay_seconds': 300,
        'min_ride_start_date': '2021-07-01T12:08:48.372+02:00',  # test this
        'service_fee_entries': [
            {
                'agreement_id': 'taxi/park_ride',
                'sub_accounts': ['payment/cash'],
            },
        ],
        'commission_entries': [
            {
                'agreement_id': 'taxi/park_ride',
                'sub_accounts': ['total/commission'],
            },
        ],
        'sub_account_payment_type_mapping': {'payment/cash': 'cash'},
        'eds_client_id': 'latvia-eds-client-id',
        'order_data_aggregation_limit_seconds': 17222,
    },
)
async def test_send_rides_reports_expired_event(
        taxi_latvia_rides_reports, mockserver, pgsql, _common_data_aggregation,
):
    await taxi_latvia_rides_reports.run_task('send-rides-reports')

    cursor = pgsql['latvia_rides_reports'].cursor()
    cursor.execute(
        """SELECT entry_id, state
        FROM latvia_rides_reports.order_income_events
        ORDER BY entry_id
        """,
    )
    result = list(cursor)
    assert result == [(2, 'IGNORED_BY_CONFIG')]
