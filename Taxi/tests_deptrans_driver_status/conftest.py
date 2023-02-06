import base64
import dataclasses
import typing

import bcrypt
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from deptrans_driver_status_plugins import *  # noqa: F403 F401

from tests_deptrans_driver_status import utils


@pytest.fixture
def deptrans_profile():
    @dataclasses.dataclass
    class DeptransProfile:
        license_pd_id: str
        license_country: str = None
        deptrans_id: str = ''
        status: typing.Optional[str] = None
        checking_deptrans_id: str = None

    profiles = {
        ('park1', 'driver1'): DeptransProfile(
            'driver_license_pd_id_1', 'rus', '1', 'approved', None,
        ),
        ('park1', 'driver2'): DeptransProfile(
            'driver_license_pd_id_2', 'rus', '2', None, '2',
        ),
        ('park2', 'driver1'): DeptransProfile(
            'driver_license_pd_id_3', 'rus', '3', 'temporary', None,
        ),
        ('park3', 'driver1'): DeptransProfile(
            'driver_license_pd_id_5', 'rus', '5', 'temporary', None,
        ),
        ('park3', 'driver3'): DeptransProfile(
            'driver_license_pd_id_7', None, '7', 'temporary_outdated', None,
        ),
        ('park3', 'driver4'): DeptransProfile(
            'driver_license_pd_id_8', 'rus', '8', 'temporary', 'some_id',
        ),
        ('park3', 'driver5'): DeptransProfile(
            'driver_license_pd_id_9', 'rus', '9', 'temporary_outdated', None,
        ),
        ('park4', 'driver1'): DeptransProfile(
            'DRdriver_license_pd_id_11', 'oth', '11', 'temporary', None,
        ),
        ('park4', 'driver2'): DeptransProfile(
            'LRdriver_license_pd_id_12', 'rus', '12', 'temporary', None,
        ),
        ('park4', 'driver3'): DeptransProfile(
            'LRdriver_license_pd_id_13', None, '13', 'temporary', None,
        ),
        ('park4', 'driver4'): DeptransProfile(
            'driver_license_pd_id_14', 'oth', '14', 'temporary', None,
        ),
    }

    class Context:
        @staticmethod
        def get(park_id, driver_id):
            return profiles.get(
                (park_id, driver_id), DeptransProfile('unknown'),
            )

        @staticmethod
        def get_all():
            return sorted(profiles.values(), key=lambda x: x.license_pd_id)

        @staticmethod
        def get_licenses_with_none_country():
            profiles_with_none_country = filter(
                lambda profile: profile.license_country is None,
                profiles.values(),
            )
            return [
                profile.license_pd_id for profile in profiles_with_none_country
            ]

        @staticmethod
        def get_licenses_oth_without_prefix():
            result_profiles = filter(
                lambda x: utils.is_license_oth_without_prefix(
                    x.license_pd_id, x.license_country,
                ),
                profiles.values(),
            )
            return [profile.license_pd_id for profile in result_profiles]

    return Context()


@pytest.fixture
def driver_profile():
    @dataclasses.dataclass
    class DriverProfile:
        license_pd_id: str
        license_country: str
        car_id: str

    profiles = {
        ('park1', 'driver1'): DriverProfile(
            'driver_license_pd_id_1', 'rus', 'car1',
        ),
        ('park1', 'driver2'): DriverProfile(
            'driver_license_pd_id_2', 'rus', 'car2',
        ),
        ('park2', 'driver1'): DriverProfile(
            'driver_license_pd_id_3', 'rus', 'car3',
        ),
        ('park2', 'driver2'): DriverProfile(
            'driver_license_pd_id_4', 'blr', 'car4',
        ),
        ('park3', 'driver1'): DriverProfile(
            'driver_license_pd_id_5', 'rus', 'car5',
        ),
        ('park3', 'driver2'): DriverProfile(
            'driver_license_pd_id_4', 'blr', 'car6',
        ),
        ('park3', 'driver3'): DriverProfile(
            'driver_license_pd_id_7', None, 'car7',
        ),
        ('park3', 'driver4'): DriverProfile(
            'driver_license_pd_id_8', 'rus', 'car8',
        ),
        ('park3', 'driver5'): DriverProfile(
            'driver_license_pd_id_9', 'rus', 'car9',
        ),
        ('park3', 'driver6'): DriverProfile(
            'driver_license_pd_id_10', None, 'car10',
        ),
        ('park4', 'driver1'): DriverProfile(
            'DRdriver_license_pd_id_11', 'oth', 'car11',
        ),
        ('park4', 'driver2'): DriverProfile(
            'LRdriver_license_pd_id_12', 'rus', 'car12',
        ),
        ('park4', 'driver3'): DriverProfile(
            'LRdriver_license_pd_id_13', None, 'car13',
        ),
        ('park4', 'driver4'): DriverProfile(
            'driver_license_pd_id_14', 'oth', 'car14',
        ),
        ('park5', 'driver1'): DriverProfile(
            'driver_license_pd_id_15', 'aze', 'car15',
        ),
        ('park6', 'driver1'): DriverProfile(
            'DRdriver_license_pd_id_16', 'oth', 'car16',
        ),
        ('park6', 'driver2'): DriverProfile(
            'LRdriver_license_pd_id_17', 'rus', 'car17',
        ),
        ('park6', 'driver3'): DriverProfile(
            'LRdriver_license_pd_id_18', None, 'car18',
        ),
        ('park6', 'driver4'): DriverProfile(
            'driver_license_pd_id_19', 'oth', 'car19',
        ),
    }

    return lambda park_id, driver_id: profiles.get((park_id, driver_id))


@pytest.fixture
def pg_deptrans_driver_status():
    check_agreement_query = """
    SELECT 1 
    FROM deptrans.agreements 
    WHERE 
    driver_license_pd_id=%(license)s
    AND link=%(link)s
    """  # noqa: W291

    check_request_query = """
    SELECT 1 
    FROM deptrans.temp_profile_requests 
    WHERE 
    park_id=%(park_id)s
    AND driver_profile_id=%(driver_id)s
    """  # noqa: W291

    fetch_profile_query = """
    SELECT deptrans_pd_id, status, checking_deptrans_id
    FROM deptrans.profiles 
    WHERE 
    driver_license_pd_id=%(license_pd_id)s
    """  # noqa: W291

    insert_profile = """
    INSERT INTO deptrans.profiles 
    (driver_license_pd_id, deptrans_pd_id, updated_ts, status)
    VALUES 
    (%(license_pd_id)s, %(deptrans_pd_id)s, %(updated_ts)s, %(status)s)
    """  # noqa: W291

    update_profile = """
    UPDATE deptrans.profiles 
    SET deptrans_pd_id=%(deptrans_pd_id)s, 
    updated_ts=%(updated_ts)s, status=%(status)s
    WHERE 
    driver_license_pd_id=%(license_pd_id)s
    """  # noqa: W291

    insert_request = """
    INSERT INTO deptrans.temp_profile_requests 
    (park_id, driver_profile_id, created_ts)
    VALUES
    (%(park_id)s, %(driver_profile_id)s, %(created_ts)s)
    """  # noqa: W291

    class Context:
        @staticmethod
        def agreement_accepted(license_pd_id, agreement, pgsql):
            cursor = pgsql['deptrans_driver_status'].cursor()
            cursor.execute(
                check_agreement_query,
                {'license': license_pd_id, 'link': agreement},
            )
            return cursor.fetchone() is not None

        @staticmethod
        def request_exists(park_id, driver_id, pgsql):
            cursor = pgsql['deptrans_driver_status'].cursor()
            cursor.execute(
                check_request_query,
                {'park_id': park_id, 'driver_id': driver_id},
            )
            return cursor.fetchone() is not None

        @staticmethod
        def get_deptrans_profile(license_pd_id, pgsql):
            cursor = pgsql['deptrans_driver_status'].cursor()
            cursor.execute(
                fetch_profile_query, {'license_pd_id': license_pd_id},
            )
            return cursor.fetchone()

        @staticmethod
        def insert_deptrans_profile(
                license_pd_id, deptrans_pd_id, updated_ts, status, pgsql,
        ):
            cursor = pgsql['deptrans_driver_status'].cursor()
            cursor.execute(
                insert_profile,
                {
                    'license_pd_id': license_pd_id,
                    'deptrans_pd_id': deptrans_pd_id,
                    'updated_ts': updated_ts,
                    'status': status,
                },
            )

        @staticmethod
        def update_deptrans_profile(
                license_pd_id, deptrans_pd_id, updated_ts, status, pgsql,
        ):
            cursor = pgsql['deptrans_driver_status'].cursor()
            cursor.execute(
                update_profile,
                {
                    'license_pd_id': license_pd_id,
                    'deptrans_pd_id': deptrans_pd_id,
                    'updated_ts': updated_ts,
                    'status': status,
                },
            )

        @staticmethod
        def insert_request_for_profile(
                park_id, driver_profile_id, created_ts, pgsql,
        ):
            cursor = pgsql['deptrans_driver_status'].cursor()
            cursor.execute(
                insert_request,
                {
                    'park_id': park_id,
                    'driver_profile_id': driver_profile_id,
                    'created_ts': created_ts,
                },
            )

    return Context()


@pytest.fixture
def pg_deptrans_profile_status_logs():
    fetch_logs = """
    SELECT 
      driver_license_pd_id,
      deptrans_pd_id,
      status
    FROM deptrans.profiles_status_logs 
    WHERE 
        driver_license_pd_id=%(license)s
    ORDER BY
        created_ts DESC;
    """  # noqa: W291

    class Context:
        @staticmethod
        def fetch_logs(license_pd_id, pgsql):
            cursor = pgsql['deptrans_driver_status'].cursor()
            cursor.execute(fetch_logs, {'license': license_pd_id})
            return cursor.fetchall()

    return Context()


@pytest.fixture(name='driver_trackstory')
def driver_trackstory_(mockserver):
    class Context:
        def __init__(self):
            self.timeouts_count = 0
            self.data = {}
            self.excluded_drivers = set()

        def set_timeouts_count(self, timeouts_count):
            self.timeouts_count = timeouts_count

        def set_data(self, driver_id, lon, lat):
            self.data[driver_id] = {'lon': lon, 'lat': lat}

        def exclude_driver(self, driver_id):
            self.excluded_drivers.add(driver_id)

    context = Context()

    @mockserver.json_handler('driver-trackstory/positions')
    def _positions(request):
        if context.timeouts_count > 0:
            context.timeouts_count -= 1
            raise mockserver.TimeoutError()

        result = []
        for driver_id in request.json['driver_ids']:
            if driver_id not in context.excluded_drivers:
                data = context.data.get(driver_id, {'lon': 37.5, 'lat': 55.5})
                result.append(
                    {
                        'driver_id': driver_id,
                        'position': {
                            'lon': data['lon'],
                            'lat': data['lat'],
                            'timestamp': 1607635209,
                        },
                        'type': 'raw',
                    },
                )
        return {'results': result}

    return context


@pytest.fixture(name='driver_categories_api')
def driver_categories_api_(mockserver):
    class Context:
        def __init__(self):
            self.data = {}
            self.timeouts_count = 0
            self.excluded_drivers = set()

        def set_data(self, driver_id, categories):
            self.data[driver_id] = categories

        def set_timeouts_count(self, timeouts_count):
            self.timeouts_count = timeouts_count

        def exclude_driver(self, driver_id):
            self.excluded_drivers.add(driver_id)

    context = Context()

    @mockserver.json_handler('driver-categories-api/v2/aggregation/categories')
    def _categories(request):
        if context.timeouts_count > 0:
            context.timeouts_count -= 1
            raise mockserver.TimeoutError()

        drivers = []
        for driver in request.json['drivers']:
            if (
                    f'{driver["park_id"]}_{driver["driver_id"]}'
                    not in context.excluded_drivers
            ):
                categories = context.data.get(
                    f'{driver["park_id"]}_{driver["driver_id"]}', ['econom'],
                )
                drivers.append({**driver, 'categories': categories})
        return {'drivers': drivers}

    return context


@pytest.fixture(name='personal')
def personal_(mockserver):
    @mockserver.json_handler('/personal/v1/deptrans_ids/bulk_retrieve')
    def _bulk_retrieve(request):
        return {
            'items': [
                {'id': item['id'], 'value': item['id']}
                for item in request.json['items']
            ],
        }

    # /v2/data_type/bulk_store
    @mockserver.json_handler('/personal/v2/deptrans_ids/bulk_store')
    def _bulk_store(request):
        return {
            'items': [
                {'id': item['value'], 'value': item['value']}
                for item in request.json['items']
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _bulk_retrieve_licenses(request):
        return {
            'items': [
                {'id': item['id'], 'value': item['id']}
                for item in request.json['items']
            ],
        }

    @mockserver.json_handler('/personal/v1/deptrans_ids/retrieve')
    def _retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id']}

    @mockserver.json_handler('/personal/v1/deptrans_ids/store')
    def _store(request):
        return {'id': request.json['value'], 'value': request.json['value']}

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _retrieve_license(request):
        return {'id': request.json['id'], 'value': request.json['id']}

    return {
        'bulk_retrieve': _bulk_retrieve,
        'retrieve': _retrieve,
        'store': _store,
        'bulk_store': _bulk_store,
        'retrieve_license': _retrieve_license,
        'bulk_retrieve_licenses': _bulk_retrieve_licenses,
    }


@pytest.fixture(name='deptrans_ais_krt', autouse=True)
def deptrans_ais_krt_(mockserver):
    class Context:
        def __init__(self):
            self.session_status = 'SESSION_OPENED'
            self.session_deny_reason = None
            self.licenses = {}
            self.driver_id_statuses = {}
            self.import_date = {}
            self.raise_error = False

        def set_session_status(self, session_status):
            self.session_status = session_status

        def set_session_deny_reason(self, session_deny_reason):
            self.session_deny_reason = session_deny_reason

        def add_license(self, deptrans_driver_id, driver_license):
            self.licenses[deptrans_driver_id] = driver_license.encode()

        def get_license(self, deptrans_driver_id):
            return self.licenses.get(deptrans_driver_id, b'')

        def add_driver_id_status(self, deptrans_driver_id, status):
            self.driver_id_statuses[deptrans_driver_id] = status

        def add_import_date(self, deptrans_driver_id, import_date):
            self.import_date[deptrans_driver_id] = import_date

        def set_raise_error(self, raise_error):
            self.raise_error = raise_error

    context = Context()

    @mockserver.json_handler('/deptrans-ais-krt/aggregator/api/oauth/token')
    def _oauth_token(request):
        assert request.headers['Authorization'][:5] == 'Basic'
        assert (
            base64.b64decode(request.headers['Authorization'][6:])
            == b'username:password'
        )
        return {
            'access_token': 'token',
            'token_type': 'Bearer',
            'expires_in': 3600,
        }

    @mockserver.json_handler('/deptrans-ais-krt/aggregator/api/driver_status')
    def _driver_status(request):
        response = {
            'requestId': 'request_id',
            'responseId': 'response_id',
            'sessionStatus': context.session_status,
            'sessionEnd': 3600,
        }
        if context.session_deny_reason:
            response['sessionDenyReason'] = context.session_deny_reason
        return response

    @mockserver.json_handler(
        '/deptrans-ais-krt/aggregator/api/check_driver_id',
    )
    def _check_driver(request):
        if context.raise_error:
            raise mockserver.TimeoutError()

        deptrans_driver_id = str(request.form['driverId'])
        driver_license = request.form['driverLicense']
        check_status = bcrypt.checkpw(
            context.get_license(deptrans_driver_id), driver_license.encode(),
        )
        response = {
            'check_status': 'success' if check_status else 'failed',
            'driverIdStatus': context.driver_id_statuses.get(
                deptrans_driver_id, 'PERMANENT',
            ),
        }
        if context.import_date.get(deptrans_driver_id, None):
            response['importDate'] = context.import_date.get(
                deptrans_driver_id,
            )

        return response

    setattr(context, 'oauth_token', _oauth_token)
    setattr(context, 'driver_status', _driver_status)
    setattr(context, 'check_driver', _check_driver)
    return context


@pytest.fixture(name='client_notify')
def client_notify_(mockserver):
    class Context:
        def __init__(self):
            self.message = None

        def set_message(self, message):
            self.message = message

    context = Context()

    @mockserver.json_handler('/client-notify/v2/push')
    def _notification_push(request):
        assert request.json['notification']['text'] == context.message
        return {}

    setattr(context, 'push', _notification_push)
    return context


@pytest.fixture(name='unique_drivers')
def unique_drivers_(mockserver):
    class Context:
        def __init__(self):
            self.license_mapping = {}

        def add_license_mapping(self, driver_license, udid):
            self.license_mapping[driver_license] = udid

    context = Context()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        return mockserver.make_response(
            json={
                'uniques': [
                    {
                        'park_driver_profile_id': 'parkid1_driverid1',
                        'data': {'unique_driver_id': 'unique_driver_id_1'},
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_license_pd_ids',
    )
    def _retrieve_by_license(request):
        return mockserver.make_response(
            json={
                'uniques': [
                    {
                        'license_pd_id': license_pd_id,
                        'unique_driver_ids': [udid],
                    }
                    for license_pd_id, udid in context.license_mapping.items()
                ],
            },
            status=200,
        )

    setattr(context, 'retrieve_by_profiles', _retrieve_by_profiles)
    setattr(context, 'retrieve_by_license', _retrieve_by_license)
    return context


@pytest.fixture(name='tags')
def tags_(mockserver):
    class Context:
        def __init__(self):
            self.tags = {}

        def add_tags(self, udid, tags):
            self.tags[udid] = tags

    context = Context()

    @mockserver.json_handler('/tags/v1/assign')
    def _assign(request):
        if context.tags:
            tags = [
                {'name': udid, 'type': 'udid', 'tags': tags}
                for udid, tags in context.tags.items()
            ]
            assert tags == request.json['entities']
        return {}

    setattr(context, 'assign', _assign)
    return context
