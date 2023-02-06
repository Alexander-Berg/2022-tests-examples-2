# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import collections
import datetime
from typing import Optional
from typing import Set
import uuid

from cargo_misc_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
def receipt():
    return {
        'items': [
            {
                'description': 'Some item',
                'quantity': '2',
                'amount': {'currency': 'RUB', 'value': '999.99'},
                'vat_code': 1,
                'payment_subject': 'commodity',
                'payment_mode': 'full_prepayment',
            },
            {
                'description': 'Some item 2',
                'quantity': '3',
                'amount': {'currency': 'USD', 'value': '999.99'},
                'vat_code': 1,
                'payment_subject': 'service',
                'payment_mode': 'full_payment',
            },
        ],
        'customer': {'phone': '70001231231'},
    }


@pytest.fixture
def mocker_cargo_claims_get(mockserver):
    def wrapper(json, status=200):
        @mockserver.json_handler('/cargo-claims/v2/claims/sharing-point')
        def get_sharing_point(request):
            result = {} if json is None else json
            return mockserver.make_response(json=result, status=status)

        return get_sharing_point

    return wrapper


@pytest.fixture
def mocker_tracker_position(mockserver):
    def wrapper(json, status=200):
        @mockserver.json_handler('/tracker/position')
        def tracker_position(request):
            result = {} if json is None else json
            return mockserver.make_response(json=result, status=status)

        return tracker_position

    return wrapper


@pytest.fixture
def mocker_driver_trackstory(mockserver):
    def wrapper(json, status=200):
        @mockserver.json_handler('/driver-trackstory/position')
        def trackstory_position(request):
            result = {} if json is None else json
            return mockserver.make_response(json=result, status=status)

        return trackstory_position

    return wrapper


@pytest.fixture
def mocker_oauth_token(mockserver):
    def wrapper(json, status=200):
        @mockserver.json_handler('/yandex-oauth/token')
        def oauth_token(request):
            assert 'Authorization' in request.headers
            assert (
                request.headers['Authorization']
                == 'Basic Y2xpZW50X2lkOnBhc3N3b3Jk'
            )
            result = {} if json is None else json
            return mockserver.make_response(json=result, status=status)

        return oauth_token

    return wrapper


@pytest.fixture
def mocker_payments_me(mockserver, default_payment_token):
    def wrapper(
            fiscalization_enabled: bool = False,
            test: bool = False,
            status: int = 200,
    ):
        @mockserver.json_handler('/yandex-checkout/v3/me')
        def checkout_me(request):
            token = default_payment_token['decrypted']
            assert 'Authorization' in request.headers
            assert request.headers['Authorization'] == f'Bearer {token}'
            if status == 200:
                json = {
                    'account_id': '123',
                    'test': test,
                    'fiscalization_enabled': fiscalization_enabled,
                    'payment_methods': ['bank_card', 'yandex_money'],
                }
            else:
                json = {
                    'type': 'error',
                    'id': 'ac3e86df-1175-4de2-b4c2-7eb94384cddb',
                    'code': 'invalid_credentials',
                    'description': 'Passport authorization details not found',
                }
            return mockserver.make_response(json=json, status=status)

        return checkout_me

    return wrapper


@pytest.fixture(name='default_payment_token')
def _default_payment_token():
    return {
        'encrypted': (
            'EdvrjuMHKiipZvMSTKClVxj3lbmKX+gvxagfzkVl63s++1tcvfwqIR'
            'qoLSF5FHTdtoDNU0VdAq9UYTa05SIkdw=='
        ),
        'decrypted': 'AQAAAACy1C6ZAAAAfa6vDLuItEy8pg-iIpnDxIs',
    }


@pytest.fixture
async def insert_payment(pgsql):
    async def wrapper(
            corp_client_id: str,
            payment_ref_id: str,
            checkout_payment_id: Optional[str] = None,
            status: str = 'pending',
            try_number: int = 1,
    ):
        if checkout_payment_id is None:
            checkout_payment_id = str(uuid.uuid4())

        cursor = pgsql['cargo_misc'].conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO cargo_misc.payments (
                corp_client_id,
                payment_ref_id,
                checkout_payment_id,
                status,
                try_number
            ) VALUES(
                '{corp_client_id}',
                '{payment_ref_id}',
                '{checkout_payment_id}',
                '{status}',
                {try_number}
            )
        """,
        )

    return wrapper


@pytest.fixture(autouse=True)
def personal_data_request(mockserver):
    def is_valid_phone(phone):
        return (
            phone
            and phone[0] == '+'
            and phone[1:].isdigit()
            and len(phone) == 12
        )

    def _store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    def _bulk_store(request, check_item=None):
        result = {'items': []}
        for i in request.json['items']:
            if check_item and check_item(i['value']):
                result['items'].append(
                    {'id': i['value'] + '_id', 'value': i['value']},
                )
        return result

    def _retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id'][:-3]}

    def _bulk_retrieve(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append({'id': i['id'], 'value': i['id'][:-3]})
        return result

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        if is_valid_phone(request.json['value']):
            return _store(request)
        return mockserver.make_response(
            status=400, json={'code': 'not-found', 'message': 'error'},
        )

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return _store(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_bulk_store(request):
        return _bulk_store(request, check_item=is_valid_phone)

    @mockserver.json_handler('/personal/v1/emails/bulk_store')
    def _emails_bulk_store(request):
        return _bulk_store(request)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _emails_retrieve(request):
        assert request.json['id'] != ''
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        return _bulk_retrieve(request)

    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _emails_bulk_retrieve(request):
        for email_id in request.json['items']:
            assert email_id['id'] != ''
        return _bulk_retrieve(request)

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _identifications_retrieve(request):
        return _retrieve(request)


@pytest.fixture
def get_default_claim_response():
    return {
        'id': 'claim_id_1',
        'emergency_contact': {
            'name': 'emergency_name',
            'phone': '+79098887777',
        },
        'items': [
            {
                'pickup_point': 1,
                'droppof_point': 2,
                'title': 'Холодильник карманный',
                'weight': 12,
                'quantity': 1,
                'cost_value': '1.2345',
                'cost_currency': 'RUR',
            },
        ],
        'route_points': [
            {
                'id': 1,
                'address': {'fullname': '', 'coordinates': [37.1, 55.1]},
                'contact': {
                    'name': 'Petya',
                    'phone': '+70009999988',
                    'email': 'email@ru',
                },
                'type': 'source',
                'visit_order': 1,
                'visit_status': 'pending',
                'visited_at': {},
            },
            {
                'id': 2,
                'address': {'fullname': '', 'coordinates': [37.2, 43.3]},
                'contact': {
                    'name': 'Petya',
                    'phone': '+70009999988',
                    'email': 'email@ru',
                },
                'type': 'destination',
                'visit_order': 2,
                'visit_status': 'pending',
                'visited_at': {},
            },
        ],
        'status': 'new',
        'version': 0,
        'pricing': {},
        'created_ts': '2020-03-31T18:35:00+00:00',
        'updated_ts': '2020-03-31T18:35:00+00:00',
    }


@pytest.fixture(autouse=True)
def mock_territories(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def mock_countries_list(request):
        request.get_data()
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'code2': 'RU',
                    'currency': 'RUB',
                    'currency_rules': {
                        'fraction': 0,
                        'short_name': 'руб.',
                        'symbol': '₽',
                    },
                    'eng': 'Russia',
                    'lang': 'ru',
                    'min_hold_amount': '1',
                    'name': 'Россия',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 12,
                    'phone_min_length': 11,
                    'promocode_max_value': 2500,
                    'region_id': 225,
                    'state_service_url': 'ффф',
                    'taximeter_lang': 'ru',
                    'updated': '2019-04-23T15:32:48+0000',
                    'vat': 12000,
                },
                {
                    '_id': 'aze',
                    'code2': 'AZ',
                    'currency': 'AZN',
                    'eng': 'Azerbaijan',
                    'lang': 'az',
                    'min_hold_amount': '1',
                    'name': 'Азербайджан',
                    'national_access_code': '0',
                    'phone_code': '994',
                    'phone_max_length': 12,
                    'phone_min_length': 12,
                    'region_id': 124,
                    'updated': '2018-06-28T10:25:36+0000',
                },
                {
                    '_id': 'blr',
                    'code2': 'BY',
                    'currency': 'BYN',
                    'eng': 'Belarus',
                    'lang': 'ru',
                    'min_hold_amount': '1',
                    'name': 'Беларусь',
                    'national_access_code': '80',
                    'phone_code': '375',
                    'phone_max_length': 12,
                    'phone_min_length': 12,
                    'region_id': 149,
                    'updated': '2021-08-09T10:25:36+0000',
                },
            ],
        }

    return mock_countries_list


@pytest.fixture(name='create_pickup_partner_point')
def _create_pickup_partner_point(pgsql):
    def _wrapper(
            service: str,
            partner_point_id: str,
            latitude: float,
            longitude: float,
            personal_phone_id: str,
            city: str = 'Москва',
    ):
        cursor = pgsql['cargo_misc'].conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO cargo_misc.pickup_partner_points (
                service,
                partner_point_id,
                latitude,
                longitude,
                personal_phone_id,
                city
            ) VALUES(
                '{service}',
                '{partner_point_id}',
                 {latitude},
                 {longitude},
                '{personal_phone_id}',
                '{city}'
            ) RETURNING
                id,
                service,
                partner_point_id,
                latitude,
                longitude,
                personal_phone_id,
                city;
            """,
        )
        row = list(cursor)[0]
        cursor.close()
        return {
            'id': row[0],
            'service': row[1],
            'partner_point_id': row[2],
            'latitude': row[3],
            'longitude': row[4],
            'personal_phone_id': row[5],
            'city': row[6],
        }

    return _wrapper


@pytest.fixture(name='create_pickup_shipment')
def _create_pickup_shipment(pgsql):
    def _wrapper(
            uuid_id: str,
            status: str,
            track_id: str,
            service: str,
            customer_personal_phone_id: str,
            customer_name: str,
            im_order_id: str,
            im_brand: str,
            expired_at: str,
            pickup_point_id: str,
            created_ts: datetime.datetime,
    ):
        cursor = pgsql['cargo_misc'].conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO cargo_misc.pickup_shipments (
                uuid_id,
                status,
                track_id,
                service,
                customer_personal_phone_id,
                customer_name,
                im_order_id,
                im_brand,
                expired_at,
                pickup_point_id,
                created_ts
            ) VALUES(
                '{uuid_id}',
                '{status}',
                '{track_id}',
                '{service}',
                '{customer_personal_phone_id}',
                '{customer_name}',
                '{im_order_id}',
                '{im_brand}',
                '{expired_at}',
                '{pickup_point_id}',
                '{str(created_ts)}'
            ) RETURNING
                id,
                uuid_id,
                status,
                track_id,
                service,
                customer_personal_phone_id,
                customer_name,
                im_order_id,
                im_brand,
                expired_at,
                pickup_point_id,
                created_ts;
            """,
        )
        row = list(cursor)[0]
        cursor.close()
        return {
            'id': row[0],
            'uuid_id': row[1],
            'status': row[2],
            'track_id': row[3],
            'service': row[4],
            'customer_personal_phone_id': row[5],
            'customer_name': row[6],
            'im_order_id': row[7],
            'im_brand': row[8],
            'expired_at': row[9],
            'pickup_point_id': row[10],
            'created_ts': row[11],
        }

    return _wrapper


@pytest.fixture(name='create_pickup_shipment_item')
def _create_pickup_shipment_item(pgsql):
    def _wrapper(
            title: str,
            size_w: int,
            size_l: int,
            size_h: int,
            weight: float,
            cost_value: float,
            cost_currency: str,
            quantity: int,
            shipment_id: int,
    ):
        cursor = pgsql['cargo_misc'].conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO cargo_misc.pickup_shipment_items (
                title,
                size_w,
                size_l,
                size_h,
                weight,
                cost_value,
                cost_currency,
                quantity,
                shipment_id
            )
            VALUES(
                '{title}',
                {size_w},
                {size_l},
                {size_h},
                {weight},
                {cost_value},
                '{cost_currency}',
                {quantity},
                {shipment_id}
            ) RETURNING
                id,
                title,
                size_w,
                size_l,
                size_h,
                weight,
                cost_value,
                cost_currency,
                quantity,
                shipment_id;
            """,
        )
        row = list(cursor)[0]
        cursor.close()
        return {
            'id': row[0],
            'title': row[1],
            'size_w': row[2],
            'size_l': row[3],
            'size_h': row[4],
            'weight': row[5],
            'cost_value': row[6],
            'cost_currency': row[7],
            'quantity': row[8],
            'shipment_id': row[9],
        }

    return _wrapper


@pytest.fixture(name='create_pickup_point_schedules')
def _create_pickup_point_schedules(pgsql):
    def _wrapper(
            pickup_point_id: int,
            week_days: Optional[Set[str]] = None,
            is_temporary: bool = False,
            work_start_hour: int = 7,
            work_end_hour: int = 24,
            work_break_start_hour: Optional[int] = None,
            work_break_end_hour: Optional[int] = None,
    ):
        if week_days is None:
            week_days = {
                'Sunday',
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
            }
        week_days_str = ','.join('\'{}\''.format(day) for day in week_days)
        cursor = pgsql['cargo_misc'].conn.cursor()

        if (
                work_break_start_hour is not None
                and work_break_start_hour is not None
        ):
            query = f"""
                INSERT INTO cargo_misc.pickup_partner_point_schedules (
                    pickup_point_id,
                    week_day,
                    is_temporary,
                    work_start,
                    work_end,
                    work_break_start,
                    work_break_end
                )
                SELECT
                    {pickup_point_id},
                    weekday::cargo_misc.week_day,
                    {is_temporary},
                    {work_start_hour} * 60 * 60,
                    {work_end_hour} * 60 * 60,
                    {work_break_start_hour} * 60 * 60,
                    {work_break_end_hour} * 60 * 60
                FROM unnest(ARRAY [{week_days_str}]) as weekday;
            """
        else:
            query = f"""
                INSERT INTO cargo_misc.pickup_partner_point_schedules (
                    pickup_point_id,
                    week_day,
                    is_temporary,
                    work_start,
                    work_end
                )
                SELECT
                    {pickup_point_id},
                    weekday::cargo_misc.week_day,
                    {is_temporary},
                    {work_start_hour} * 60 * 60,
                    {work_end_hour} * 60 * 60
                FROM unnest(ARRAY [{week_days_str}]) as weekday;
            """
        cursor.execute(query)
        cursor.close()

    return _wrapper


@pytest.fixture(name='mocker_fleet_parks_list')
def _mocker_fleet_parks_list(mockserver):
    def wrapper(park_id='park_id', country_id='some_country'):
        @mockserver.json_handler('/fleet-parks/v1/parks/list')
        def _mock_parks_list(request):
            if park_id is None:
                return {'parks': []}
            assert request.json['query'] == {'park': {'ids': [park_id]}}

            return {
                'parks': [
                    {
                        'id': park_id,
                        'login': 'login',
                        'is_active': True,
                        'city_id': 'city',
                        'locale': 'locale',
                        'is_billing_enabled': True,
                        'is_franchising_enabled': True,
                        'demo_mode': False,
                        'country_id': country_id,
                        'name': 'park_name',
                        'org_name': 'org_name',
                        'geodata': {'lat': 12, 'lon': 34, 'zoom': 0},
                    },
                ],
            }

    return wrapper


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver):
    class DriverProfilesContext:
        def __init__(self):
            self.profiles = []

        def set_profiles(self, profiles):
            nested_profiles = collections.defaultdict(list)
            for profile in profiles:
                data = {}
                if 'data' in profile and 'is_readonly' in profile['data']:
                    data['is_readonly'] = profile['data']['is_readonly']
                nested_profiles[profile['courier_id']].append(
                    {
                        'park_driver_profile_id': (
                            f'{profile["park_id"]}_driver1'
                        ),
                        'data': data,
                    },
                )
            self.profiles = [
                {'eats_courier_id': key, 'profiles': value}
                for key, value in nested_profiles.items()
            ]

    context = DriverProfilesContext()

    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    def _retrieve_by_eats_id(request):
        assert request.json['projection'] == ['data.is_readonly']
        return {'courier_by_eats_id': context.profiles}

    @mockserver.json_handler('/driver-profiles/v1/profile/courier-app')
    def _patch_courier_app(request):
        return {}

    @mockserver.json_handler('/driver-profiles/v1/driver/delivery')
    def _patch_delivery(request):
        assert request.json.get('delivery', {}).get('eats_equipment')
        return {}

    return context


@pytest.fixture(name='contractor_profession')
def _contractor_profession(mockserver):
    @mockserver.json_handler(
        '/contractor-profession/internal/v1/contractors/profession',
    )
    def _put_contractor_profession(request):
        return {}

    class Context:
        def __init__(self):
            self.handler = _put_contractor_profession

    context = Context()
    return context
