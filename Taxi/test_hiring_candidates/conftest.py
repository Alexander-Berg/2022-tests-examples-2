# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import datetime
import functools
import random
import re
import string
import uuid

import pytest

import hiring_candidates.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_candidates.generated.cron import run_cron  # noqa: I100
from hiring_candidates.internal import yt_operations

pytest_plugins = ['hiring_candidates.generated.service.pytest_plugins']

MAX_DATES_INTERVAL = 45
PARKS_COUNT = 100
DRIVERS_COUNT = 100000
TVM_DESTINATIONS = [
    'personal',
    'driver-orders',
    'driver-profiles',
    'stq-agent',
    'hiring-data-markup',
    'territories',
    'statistics',
]
PHONES_MATCH = {
    '+70000000000': 'df26389528dd429a903d59f731ccf6b4',
    '+70000000001': '6749538458d64102a3c7efedc179ae45',
    '+79998887766': '1104248e26074dd88e46f350037459fa',
    '+79998887782': 'be5da8c4f4c741afa8887c41502c441b',
    '+79998887783': '8608aed6702142e38a1b1c343d5e7b7c',
    '+79998887785': 'ab5d889aab6d448091766a7649c604ce',
    '+79998887786': 'c6f13636554a492cb284e2b40c6fc0bb',
    '+79998887789': '2aef6af8cc8246af9253fd08dcedba87',
    'somestring': '0e285708577e43aea76a2d5644f072d7',
    'f5b6a9399d624084ae0ff73e6f67174f': '+79998887788',
    '2aef6af8cc8246af9253fd08dcedba87': '+79998887789',
    '6ba83c0cb6c8451a9f30759534e03aab': '+79998887781',
    'be5da8c4f4c741afa8887c41502c441b': '+79998887782',
    '8608aed6702142e38a1b1c343d5e7b7c': '+79998887783',
    '00af1a3019474754aa376e6280cc2dd4': '+79998887784',
    'ab5d889aab6d448091766a7649c604ce': '+79998887785',
    'c6f13636554a492cb284e2b40c6fc0bb': '+79998887786',
    'INVALID': None,
    '+79999999999': None,
}
LICENSES_MATCH = {
    '12AT123456': '1104248e26074dd88e46f350037459fa',
    '12МФЦ123456': 'b7ca05845f59429f9c40e451f08762f9',
    'COURIER_12AT123456': 'bcd0453b57c8443baa4a6ea774c765a7',
    '$=+$1$$$2A$$$T123456': '47057b74bd6e46e18764945686674ae2',
    '1_2_A_T_1_234_56': '9e542e5cd1cd43a9a482e6eec59daa4c',
    '12    AT   123  456': '5a36c225806e4a1d90a90beb0e8779d4',
    'NORIDES': 'df26389528dd429a903d59f731ccf6b4',
    'NORIDES_SELFEMPLOYED': '6749538458d64102a3c7efedc179ae45',
    'INVALID': None,
    '456789': 'bd4c88e3e36b4cc58f993c2d19794dca',
    '12313123': '98f755a58b5d4d578cd504bdcb7de06d',
    '0123': 'b096c787cc744c33bca703990fef384b',
    '12AA444333': '260c2e98b6514594bc988171ba2b16f7',
    '14KK222888': '84e68ba6534e49e2893151194a8b909b',
    '14KK222999': '37b48d6efd784ba4acc8ad33fc0bf218',
    'b096c787cc744c33bca703990fef384b': '0123',
    'bd4c88e3e36b4cc58f993c2d19794dca': '456789',
    '37b48d6efd784ba4acc8ad33fc0bf218': '14KK222999',
    'FREEDRIVER': 'FREEDRIVERPD',
}
YANDEX_LOGINS_MATCH = {'den_lspd': 'a95c01defa9d4909910e084cbdabecca'}
PROFILES_PHONE_KEY = 'profiles_by_phone'
PROFILES_LICENSE_KEY = 'profiles_by_license'

EMAIL_MATCH = {'some@example.com': '1104243e26074dd88e46f350037459fa'}

ROUTE_SALESFORCE_CREATE_CANDIDATE = '/v1/salesforce/create-candidate'

PERSONAL_NULL_RESPONSE = {
    'code': '400',
    'message': 'Field \'value\' is of a wrong type...',
}


def _generator(doc: dict):
    while True:
        yield doc


class ActiveDriversGenerator:
    __instance = None

    def __init__(self, q_parks, q_drivers):
        if ActiveDriversGenerator.__instance:
            msg = 'Only one instance of ActiveDriversGenerator is acceptable'
            raise RuntimeError(msg)

        ActiveDriversGenerator.__instance = self

        self.q_parks = q_parks
        self.q_drivers = q_drivers

        self.parks = [hex_uuid() for _ in range(q_parks)]
        self.drivers_dict = self.generate()
        self.drivers_list = None

    @classmethod
    def get_instance(cls):
        return cls.__instance

    @staticmethod
    def _generate_timestamps():
        max_in_sec = 44 * 24 * 3600
        days2_in_sec = 2 * 24 * 3600
        now = datetime.datetime.utcnow()

        def one():
            shift = random.randint(days2_in_sec, max_in_sec)
            return now - datetime.timedelta(seconds=shift)

        dates = sorted([one() for _ in range(2)])
        dates = [dt.timestamp() for dt in dates]
        first, last = dates
        return first, last

    def _generator(self):
        while True:
            first, last = self._generate_timestamps()
            doc = {
                'db_id': random.choice(self.parks),
                'driver_id': hex_uuid(),
                'first_ride': first,
                'last_ride': last,
                'rides_count': random.randint(1, 1000),
            }
            yield doc

    def generate(self):
        generator = self._generator()
        drivers_list = [next(generator) for _ in range(self.q_drivers)]
        drivers_dict = {
            doc['db_id'] + '_' + doc['driver_id']: doc for doc in drivers_list
        }
        return drivers_dict

    def as_list(self):
        if self.drivers_list is None:
            self.drivers_list = list(self.drivers_dict.values())
        return self.drivers_list


def hex_uuid():
    return uuid.uuid4().hex


@pytest.fixture(scope='session')  # noqa: F405
def mock_fetch_table():
    data = ActiveDriversGenerator(PARKS_COUNT, DRIVERS_COUNT).as_list()

    async def func(*args, **kwargs):
        return data

    yt_operations.fetch_table = func


@pytest.fixture(scope='session')  # noqa: F405
def mock_fetch_drivers_rides_table():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    doc = {
        'license_id': hex_uuid(),
        'car_plate': hex_uuid(),
        'phone_id': hex_uuid(),
        'last_ride_date': today,
    }
    data = [next(_generator(doc)) for _ in range(DRIVERS_COUNT)]

    async def func(*args, **kwargs):
        return data

    yt_operations.fetch_table = func


@pytest.fixture
def mock_yt_search(load_json):
    async def func(context, path, log_extra=None):
        return load_json(f'comm_tables_{path}.json')

    yt_operations.search = func


@pytest.fixture
def mock_yt_fetch_table(load_json):
    async def func(context, path, log_extra=None):

        return load_json(f'comm_data_{path}.json')

    yt_operations.fetch_table = func


@pytest.fixture()
def mock_yt_target_events(load_json):
    async def func(context, path, log_extra=None):
        return load_json('target_events_data.json')['payload']

    yt_operations.fetch_table = func


@pytest.fixture  # noqa: F405
def get_all_candidates(fetch_all_from_table):
    return lambda: list(fetch_all_from_table(table='candidates'))


@pytest.fixture  # noqa: F405
def get_all_drivers(fetch_all_from_table):
    return lambda: list(fetch_all_from_table(table='active_drivers'))


@pytest.fixture  # noqa: F405
def get_all_drivers_v2(fetch_all_from_table):
    return lambda: list(fetch_all_from_table(table='drivers_rides'))


@pytest.fixture  # noqa: F405
def get_all_leads(fetch_all_from_table):
    return lambda: list(fetch_all_from_table(table='leads'))


@pytest.fixture  # noqa: F405
def get_all_driver_profiles(fetch_all_from_table):
    return lambda: list(fetch_all_from_table(table='driver_profiles'))


@pytest.fixture  # noqa: F405
def get_all_target_events(fetch_all_from_table):
    return lambda: list(fetch_all_from_table(table='target_events'))


@pytest.fixture  # noqa: F405
def fetch_all_from_table(pgsql, load):
    db = pgsql['hiring_candidates']

    def _do_it(table, schema='hiring_candidates'):
        table = schema + '.' + table
        cursor = db.cursor()
        query = 'SELECT * FROM {};'.format(table)
        cursor.execute(query.format(table))
        colnames = [desc[0] for desc in cursor.description]
        for raw_row in cursor:
            yield ({column: value for column, value in zip(colnames, raw_row)})

    return _do_it


@pytest.mark.usefixtures('mock_fetch_table')  # noqa: F405
@pytest.fixture  # noqa: F405
def run_cron_fixture(mock_fetch_table):
    async def func():
        await run_cron.main(
            ['hiring_candidates.crontasks.fetch_drivers_activity', '-t', '0'],
        )

    return func


@pytest.fixture  # noqa: F405
async def fill_initial_data(run_cron_fixture):
    await run_cron_fixture()


def _gen_string(length):
    res = ''.join(
        random.choices(string.ascii_uppercase + string.digits * 5, k=length),
    )
    return res


def gen_license():
    return 'LIC{}'.format(_gen_string(10).upper())


def gen_phone():
    return '+79' + str(random.randint(10 ** 8, 10 ** 9 - 1))


@functools.lru_cache(None)
def personal_response(type_, id_):
    if type_ == 'license':
        value = LICENSES_MATCH.get(id_, gen_license())
    elif type_ == 'phone':
        value = PHONES_MATCH.get(id_, gen_phone())
    elif type_ == 'phone_id':
        value = id_
        id_ = PHONES_MATCH.get(value, hex_uuid())
    elif type_ == 'login_id':
        value = id_
        id_ = YANDEX_LOGINS_MATCH.get(value, hex_uuid())
    elif type_ == 'license_id':
        value = id_
        id_ = LICENSES_MATCH.get(value, hex_uuid())
    elif type_ == 'email_id':
        value = id_
        id_ = LICENSES_MATCH.get(value, hex_uuid())
    else:
        raise ValueError
    response = {'value': value, 'id': id_}
    return response


@pytest.fixture  # noqa: F405
def personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def retrieve_phones(request):
        type_ = 'phone'
        return personal_response(type_, request.json['id'])

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def retrieve_licenses(request):
        type_ = 'license'
        response = personal_response(type_, request.json['id'])
        return response

    @mockserver.json_handler('/personal/v1/phones/store')
    def store_phones(request):
        type_ = 'phone_id'
        value = request.json['value']
        if not value or not re.match(r'^\+\d+$', value):
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response(type_, value)

    @mockserver.json_handler('/personal/v1/yandex_logins/store')
    def store_yandex_logins(request):
        type_ = 'login_id'
        value = request.json['value']
        if not value:
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response(type_, value)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def store_licenses(request):
        type_ = 'license_id'
        value = request.json['value']
        if not value:
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response(type_, value)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/emails/store')
    def store_emails(request):
        type_ = 'email_id'
        value = request.json['value']
        if not value:
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response(type_, value)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def find_licenses(request):
        type_ = 'license_id'
        response = personal_response(type_, request.json['value'])
        return response


@pytest.fixture
def _mock_territories_api(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }


@pytest.fixture  # noqa: F405
def driver_profiles_mock(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def retrieve_by_phone(request):
        phone = request.json['driver_phone_in_set'][0]
        return load_json('response_driver_profiles.json')[phone]['PHONE']

    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def retrieve_by_license(request):
        driver_license = request.json['driver_license_in_set'][0]
        return load_json('response_driver_profiles.json')[driver_license][
            'LICENSE'
        ]


@pytest.fixture  # noqa: F405
def fleet_vehicles_mock(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/retrieve_by_number_with_normalization',
    )
    def cars(request):
        response_id = '_'.join(sorted(request.json['numbers_in_set']))
        return load_json('response_fleet_vehicles.json')[response_id]


@pytest.fixture  # noqa: F405
def fleet_parks_mock(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def parks(request):
        ids = request.json['query']['park']['ids']
        response_id = '_'.join(sorted(ids))
        return load_json('response_fleet_parks.json')[response_id]


@pytest.fixture  # noqa: F405
def driver_orders_mock(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def orders(request):
        if request.json.get('cursor'):
            response_id = 'NO_ORDERS'
        elif request.json['query']['park'].get('driver_profile'):
            driver = request.json['query']['park']['driver_profile']
            response_id = driver['id']
        else:
            car = request.json['query']['park']['car']
            response_id = car['id']
        return load_json('response_driver_orders.json')[response_id]

    return orders


@pytest.fixture  # noqa: F405
def eda_core_mock(mockserver):
    catalog_search_url = (
        '/eda_core/api/v1/general-information/couriers/catalog/search'
    )
    storage = {catalog_search_url: {}}

    @mockserver.json_handler(catalog_search_url)
    # pylint: disable=unused-variable
    def catalog_search(request):
        phone = request.query['phone']
        default = {'couriers': []}
        response = storage[catalog_search_url].get(phone, default)
        return response

    return storage


def _tvm_rules():
    return [
        {'dst': item, 'src': 'hiring-candidates'} for item in TVM_DESTINATIONS
    ]


@pytest.fixture
def mock_data_markup_perform(mockserver, load_json):
    @mockserver.json_handler('/hiring-data-markup/v1/experiments/perform')
    def _perform(request):
        flow = request.json['flow']
        fields = {
            item['name']: item['value'] for item in request.json['fields']
        }
        if flow == 'blacklist_monetization':
            assert request.query['only_data'] == '1'
            kind = 'not_blacklisted'
            tags = fields['tags']
            if 'and_in_the_darkness_bind_them' in tags:
                kind = 'blacklisted'
            response = load_json('data_markup.json')[kind]
        elif flow == 'eda_selfreg_retention':
            assert 'only_data' not in request.query
            if request.json['ticket_id'] == '12615921':
                response = load_json('data_markup.json')['deactivated']
            else:
                response = load_json('data_markup.json')['default']
        elif flow == 'eda_retention_submit':
            assert 'only_data' not in request.query
            response = load_json('data_markup.json')
        elif flow == 'paid_acquisition':
            responses = load_json('data_markup.json')
            if fields['driver_license_pd_id'] == 'FREEDRIVERPD':
                response = responses['free_acquisition']
            else:
                response = responses.get('paid_acquisition', {})
        else:
            assert False
        return response

    return _perform


@pytest.fixture
def mock_data_markup_perform_response(mockserver):  # pylint: disable=C0103
    def _wrapper(response, status=200):
        @mockserver.json_handler('/hiring-data-markup/v1/experiments/perform')
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


def main_configuration(func):
    @pytest.mark.config(
        TVM_RULES=_tvm_rules(),
        HIRING_DRIVER_COMMUNICATIONS_TABLE_PATH='test_path',
        HIRING_FIELDS_WITH_TYPES=[
            {'fields': [{'name': 'tags', 'type': 'set_string'}]},
        ],
    )  # noqa: F405
    @pytest.mark.usefixtures(  # noqa: F405
        'personal',
        '_mock_territories_api',
        'driver_profiles_mock',
        'driver_orders_mock',
        'fleet_parks_mock',
        'fleet_vehicles_mock',
        'mock_data_markup_perform',
    )
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


@pytest.fixture  # noqa: F405
async def request_create_candidate(taxi_hiring_candidates_web):
    async def func(body, code=200):
        response = await taxi_hiring_candidates_web.post(
            ROUTE_SALESFORCE_CREATE_CANDIDATE, json=body,
        )
        assert response.status == code
        return response

    return func


@pytest.fixture
def mock_parks_driver_profile_post(mockserver, mock_parks):
    def _wrapper(response, status):
        @mock_parks(f'/internal/driver-profiles/create')
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_driver_profiles_update(mockserver, mock_driver_profiles):
    def _wrapper(status):
        @mock_driver_profiles(f'/v1/contractor/hiring-details')
        def _handler(request):
            return mockserver.make_response(status=status)

        return _handler

    return _wrapper


@pytest.fixture
def mock_statistics_retention(mockserver, mock_eats_performer_statistics):
    def _wrapper(retention):
        @mock_eats_performer_statistics(
            '/internal/eats-performer-statistics/v1/eda/retention/retrieve',
        )
        def _handler(request):
            return {'retention': retention}

        return _handler

    return _wrapper


@pytest.fixture
def mock_configs3(mockserver):
    def _wrapper(response):
        @mockserver.json_handler('/experiments3/v1/configs')
        def _handler(request):
            return response

        return _handler

    return _wrapper


def pytest_register_matching_hooks():
    class AnyDate:
        def __eq__(self, other):
            if isinstance(other, datetime.datetime):
                return True
            return False

    def _custom_date_match(doc: dict):
        return datetime.date.fromisoformat(doc['value'])

    def _custom_datetime_match(doc: dict):
        return datetime.datetime.fromisoformat(doc['value'])

    return {
        'any-date': AnyDate(),
        'date': _custom_date_match,
        'date-time': _custom_datetime_match,
    }


@pytest.fixture
def mock_personal_phone_retrieve(mockserver):
    def _wrapper(response, status=200):
        @mockserver.json_handler('/personal/v1/phones/retrieve')
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_personal_login_retrieve(mockserver):
    def _wrapper(response, status=200):
        @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_personal_license_retrieve(mockserver):
    def _wrapper(response, status=200):
        @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_gambling_territories_bulk_post(mockserver):  # pylint: disable=C0103
    def _wrapper(response, status=200):
        @mockserver.json_handler(
            '/hiring-taxiparks-gambling/v2/territories/bulk_post',
        )
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_gambling_conditions_bulk_post(mockserver):  # pylint: disable=C0103
    def _wrapper(response, status=200):
        @mockserver.json_handler(
            '/hiring-taxiparks-gambling/v2/hiring-conditions/bulk_post',
        )
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper
