import datetime
import json

from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db
from taxi.util import evlog
from taxi.external import chatterbox, passport
from taxiadmin import admin_permissions
from taxiadmin.api import apiutils

from taxiadmin.api.views import driver_promocodes as api_driver_promocodes

CHATTERBOX_TASK_ID = '5b958ac184b597399c0dd9f7'
WRONG_TASK_ID = '5b958c5084b597399c0dd9f8'


@pytest.fixture
def dummy_chatterbox(monkeypatch):
    def dummy_check_task(task_id, src_service, log_extra=None):
        if task_id == WRONG_TASK_ID:
            return False
        return True

    def dummy_check_data_access(*args, **kwargs):
        return {'access_status': apiutils.USER_DATA_PERMITTED}

    monkeypatch.setattr(chatterbox, 'check_task', dummy_check_task)
    monkeypatch.setattr(chatterbox, 'check_data_access', dummy_check_data_access)


PROMOCODE_1 = {
    'id': 'promocode_1',
    'series_id': 'nominal_1',
    'code': 'QWERTYUI1',
    'created_by': 'login_1',
    'created': '2018-09-01T13:35:00+0300',
    'clid': 'park_1',
    'uuid': 'driver_1',
    'country': 'rus',
    'currency': 'RUB',
    'zendesk_ticket': 'yataxi_123456',
    'duration_hours': 12,
    'start': None,
    'finish': None,
    'description': 'promo for driver_1',
    'usages': [
        'order_1',
        'order_2'
    ]
}

PROMOCODE_2 = {
    'id': 'promocode_2',
    'series_id': 'nominal_1',
    'code': 'QWERTYUI2',
    'created_by': 'login_2',
    'created': '2018-09-02T13:35:00+0300',
    'clid': 'park_2',
    'uuid': 'driver_2',
    'country': 'rus',
    'currency': 'RUB',
    'zendesk_ticket': 'yataxi_123456',
    'duration_hours': 12,
    'start': '2018-09-12T13:35:00+0300',
    'finish': '2018-09-13T01:35:00+0300',
    'description': 'promo for driver_2',
    'usages': [
        'order_1',
    ]
}

PROMOCODE_3 = {
    'id': 'promocode_3',
    'series_id': 'nominal_2',
    'code': 'QWERTYUI3',
    'created_by': 'login_3',
    'created': '2018-09-03T13:35:00+0300',
    'clid': 'park_3',
    'uuid': 'driver_3',
    'country': 'blr',
    'currency': 'BYN',
    'zendesk_ticket': '321',
    'duration_hours': 12,
    'start': '2018-09-12T13:35:00+0300',
    'finish': '2018-09-13T01:35:00+0300',
    'description': 'promo for driver_3',
    'usages': [
        'order_1',
    ]
}

PROMOCODE_4 = {
    'id': 'promocode_4',
    'series_id': 'nominal_1',
    'code': 'QWERTYUI4',
    'created_by': 'login_4',
    'created': '2018-09-03T13:35:00+0300',
    'clid': 'clid_5',
    'uuid': 'uuid_5',
    'country': 'rus',
    'currency': 'RUB',
    'zendesk_ticket': '321',
    'duration_hours': 12,
    'start': '2018-09-12T13:35:00+0300',
    'finish': '2018-09-13T01:35:00+0300',
    'description': 'promo for driver_5',
    'usages': [
        'order_1',
    ]
}

PROMOCODE_5 = {
    'id': 'promocode_5',
    'series_id': 'nominal_1',
    'code': 'QWERTYUI5',
    'created_by': 'login_5',
    'created': '2018-09-03T13:35:00+0300',
    'clid': 'clid_1',
    'uuid': 'uuid_1',
    'country': 'rus',
    'currency': 'RUB',
    'zendesk_ticket': '321',
    'duration_hours': 12,
    'start': '2018-09-12T13:35:00+0300',
    'finish': '2018-09-13T01:35:00+0300',
    'description': 'promo for driver_1',
    'usages': [
        'order_1',
    ]
}


@pytest.mark.parametrize('request_json,expected_response', [
    (
        {},
        [
            PROMOCODE_5,
            PROMOCODE_4,
            PROMOCODE_3,
            PROMOCODE_2,
            PROMOCODE_1
        ]
    ),
    (
        {
            'skip': 1,
            'limit': 1,
        },
        [
            PROMOCODE_4
        ]
    ),
    (
        {
            'clid': 'park_3'
        },
        [
            PROMOCODE_3
        ]
    ),
    (
        {
            'uuid': 'driver_1'
        },
        [
            PROMOCODE_1
        ]
    ),
    (
        {
            'zendesk_ticket': 'yataxi_123456'
        },
        [
            PROMOCODE_2,
            PROMOCODE_1
        ]
    ),
    (
        {
            'clid': 'park_2',
            'created_by': 'login_1'
        },
        []
    ),
    (
        {
            'series_id': 'nominal_1'
        },
        [
            PROMOCODE_5,
            PROMOCODE_4,
            PROMOCODE_2,
            PROMOCODE_1
        ]
    ),
    (
        {
            'active_from': '2018-09-02T00:00:00+03:00'
        },
        [
            PROMOCODE_5,
            PROMOCODE_4,
            PROMOCODE_3,
            PROMOCODE_2
        ]
    ),
    (
        {
            'active_to': '2018-09-02T00:00:00+03:00'
        },
        [
            PROMOCODE_1
        ]
    ),
    (
        {
            'code': 'QWERTYUI1'
        },
        [
            PROMOCODE_1
        ]
    )
])
@pytest.mark.now('2018-11-15T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
def test_promocode_list(request_json, expected_response):
    client = django_test.Client()
    response = client.post(
        '/api/driver_promocodes/list/',
        json.dumps(request_json),
        'application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {
        'items': expected_response
    }


@pytest.mark.parametrize('request_json,expected_code,expected_data', [
    (
        {
            'series_id': 'nominal_0',
            'clid': 'clid0',
            'uuid': 'uuid0'
        },
        404,
        'No such nominal, series_id: nominal_0'
    ),
    (
        {
            'series_id': 'nominal_3',
            'clid': 'clid0',
            'uuid': 'uuid0'
        },
        400,
        'Nominal is not active, series_id: nominal_3'
    ),
    (
        {
            'series_id': 'nominal_4',
            'clid': 'clid0',
            'uuid': 'uuid0'
        },
        400,
        'Nominal is not active, series_id: nominal_4'
    ),
    (
        {
            'series_id': 'nominal_5',
            'clid': 'clid0',
            'uuid': 'uuid0'
        },
        400,
        'Limit is over for nominal, series_id: nominal_5'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid0',
            'uuid': 'uuid0'
        },
        404,
        'Driver is not found: clid0_uuid0'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid3',
            'uuid': 'uuid3'
        },
        404,
        'Parks are not found'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid2',
            'uuid': 'uuid2'
        },
        404,
        'Cities are not found'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid4',
            'uuid': 'uuid4'
        },
        400,
        'Park and nominal have different countries: blr and rus'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid1',
            'uuid': 'uuid1'
        },
        200,
        {
            'series_id': 'nominal_1',
            'created_by': 'dmkurilov',
            'idempotency_token': None,
            'created': datetime.datetime(2018, 9, 10, 9, 0),
            'updated': datetime.datetime(2018, 9, 10, 9, 0),
            'send_notification': 'created',
            'db_id': 'park1',
            'clid': 'clid1',
            'uuid': 'uuid1',
            'zendesk_ticket': None,
            'description': None,
            'usages': [],
        }
    )
])
@pytest.mark.filldb(driver_promocodes='new')
@pytest.mark.now('2018-09-10T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_add_promocode(request_json, expected_code, expected_data):
    client = django_test.Client()
    response = client.post(
        '/api/driver_promocodes/add/',
        json.dumps(request_json),
        'application/json'
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        data = json.loads(response.content)
        assert 'id' in data
        assert 'code' in data

        doc = yield db.driver_promocodes.find_one({
            '_id': data['id']
        })
        doc.pop('_id')
        assert 'code' in doc
        doc.pop('code')
        assert doc == expected_data


@pytest.mark.config(
    DRIVER_PROMOCODE_GENERATIONS_DAILY_LIMIT=0
)
@pytest.mark.filldb(driver_promocodes='new')
@pytest.mark.now('2018-09-10T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
def test_add_promocode_limit_exceeded():
    client = django_test.Client()
    data = {
        'series_id': 'nominal_1',
        'clid': 'clid1',
        'uuid': 'uuid1'
    }
    response = client.post(
        '/api/driver_promocodes/add/',
        json.dumps(data),
        'application/json'
    )
    assert response.status_code == 406


@pytest.mark.parametrize('nominal,csv_file,expected_code,expected_response', [
    (
        'nominal_0',
        'drivers_00.csv',
        404,
        'No such nominal, series_id: nominal_0'
    ),
    (
        'nominal_3',
        'drivers_00.csv',
        400,
        'Nominal is not active, series_id: nominal_3'
    ),
    (
        'nominal_4',
        'drivers_00.csv',
        400,
        'Nominal is not active, series_id: nominal_4'
    ),
    (
        'nominal_5',
        'drivers_00.csv',
        400,
        'Limit is over for nominal, series_id: nominal_5'
    ),
    (
        'nominal_1',
        'drivers_00.csv',
        404,
        'Drivers are not found'
    ),
    (
        'nominal_1',
        'drivers_03.csv',
        404,
        'Parks are not found'
    ),
    (
        'nominal_1',
        'drivers_02.csv',
        404,
        'Cities are not found'
    ),
    (
        'nominal_1',
        'drivers_04.csv',
        400,
        'Park and nominal have different countries: blr and rus'
    ),
    (
        'nominal_6',
        'drivers_06.csv',
        406,
        'Daily limit excedeed',
    ),
    (
        'nominal_1',
        'drivers_01.csv',
        200,
        {
            'success': [
                {
                    'driver_id': 'clid1_uuid1'
                }
            ],
            'failed': []
        }
    ),
    (
        'nominal_6',
        'drivers_05.csv',
        200,
        {
            'success': [
                {
                    'driver_id': 'clid5_clid6'
                }
            ],
            'failed': [
                {
                    'driver_id': 'clid6_uuid6',
                    'reason': 'limit'
                }
            ]
        }
    )
])
@pytest.mark.config(DRIVER_PROMOCODE_GENERATIONS_DAILY_LIMIT=2)
@pytest.mark.filldb(driver_promocodes='new')
@pytest.mark.now('2018-09-10T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
def test_add_promocodes_bulk(patch, open_file, nominal, csv_file,
                             expected_code, expected_response):
    @patch('taxi.external.mds.upload')
    @async.inline_callbacks
    def upload(
        image_file, namespace=None, key_suffix=None,
        headers=None, retry_on_fails=True, log_extra=None
    ):
        yield
        async.return_value('mds_id')

    @patch('taxi.external.mds.download')
    @async.inline_callbacks
    def download(
        path, range_start=None, range_end=None,
        namespace=None, log_extra=None
    ):
        assert path == 'mds_id'
        yield
        with open_file(csv_file) as fp:
            async.return_value(fp.read())

    client = django_test.Client()
    with open_file(csv_file) as f:
        response = client.post(
            '/api/driver_promocodes/prepare_drivers/',
            {'drivers': f}
        )
        assert response.status_code == 200
        mds_file_id = json.loads(response.content)['mds_file_id']

    response = client.post(
        '/api/driver_promocodes/add_bulk/',
        json.dumps({
            'ticket': 'TAXIRATE-123',
            'series_id': nominal,
            'mds_file_id': mds_file_id,
            'description': 'add many promocodes'
        }),
        'application/json'
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        data = json.loads(response.content)
        assert len(data['success']) == len(expected_response['success'])
        assert data['failed'] == expected_response['failed']


@pytest.mark.filldb(driver_promocodes='new')
@pytest.mark.now('2018-09-10T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_add_promocodes_bulk_idempotency(patch, open_file):
    @patch('taxi.external.mds.download')
    @async.inline_callbacks
    def download(
        path, range_start=None, range_end=None,
        namespace=None, log_extra=None
    ):
        assert path == 'mds_id'
        yield
        with open_file('drivers_01.csv') as fp:
            async.return_value(fp.read())

    client = django_test.Client()
    response = client.post(
        '/api/driver_promocodes/add_bulk/',
        json.dumps({
            'ticket': 'TAXIRATE-123',
            'series_id': 'nominal_1',
            'mds_file_id': 'mds_id',
            'description': 'add many promocodes'
        }),
        'application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data['success']) == 1
    assert data['failed'] == []

    response = client.post(
        '/api/driver_promocodes/add_bulk/',
        json.dumps({
            'ticket': 'TAXIRATE-123',
            'series_id': 'nominal_1',
            'mds_file_id': 'mds_id',
            'description': 'add many promocodes'
        }),
        'application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {
        'success': [],
        'failed': []
    }

    num = yield db.driver_promocodes.find({
        'idempotency_token': 'mds_id/0'
    }).count()
    assert num == 1


@pytest.mark.parametrize('is_superuser', [False, True])
@pytest.mark.parametrize('has_require_ticket_validation_permission', [False, True])
@pytest.mark.parametrize('chatterbox_check_data_access_response', [False, True])
@pytest.mark.parametrize('request_json,expected_code,expected_data', [
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid1',
            'uuid': 'uuid1'
        },
        406,
        'Missing required field: zendesk_ticket'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid1',
            'uuid': 'uuid1',
            'zendesk_ticket': '12347'
        },
        406,
        'Zendesk or Chatterbox ticket does not exist: 12347'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid1',
            'uuid': 'uuid1'
        },
        406,
        'Missing required field: zendesk_ticket'
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid1',
            'uuid': 'uuid1',
            'description': 'promocode for driver',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
        },
        200,
        {
            'series_id': 'nominal_1',
            'created_by': 'dmkurilov',
            'idempotency_token': None,
            'created': datetime.datetime(2018, 9, 10, 9, 0),
            'updated': datetime.datetime(2018, 9, 10, 9, 0),
            'send_notification': 'created',
            'db_id': 'park1',
            'clid': 'clid1',
            'uuid': 'uuid1',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
            'description': 'promocode for driver',
            'usages': [],
        }
    ),
    (
        {
            'series_id': 'nominal_1',
            'clid': 'clid1',
            'uuid': 'uuid1',
            'description': 'promocode for driver',
            'zendesk_ticket': '  \n{}\t'.format(CHATTERBOX_TASK_ID),
        },
        200,
        {
            'series_id': 'nominal_1',
            'created_by': 'dmkurilov',
            'idempotency_token': None,
            'created': datetime.datetime(2018, 9, 10, 9, 0),
            'updated': datetime.datetime(2018, 9, 10, 9, 0),
            'send_notification': 'created',
            'db_id': 'park1',
            'clid': 'clid1',
            'uuid': 'uuid1',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
            'description': 'promocode for driver',
            'usages': [],
        }
    )
])
@pytest.mark.filldb(driver_promocodes='new')
@pytest.mark.now('2018-09-10T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    ADMIN_CHECK_CHATTERBOX_TICKET_ENABLED=True
)
def test_add_promocode_zendesk(monkeypatch, request_json, expected_code,
                               expected_data, dummy_chatterbox,
                               is_superuser, has_require_ticket_validation_permission,
                               chatterbox_check_data_access_response):
    request = django_test.RequestFactory().post(
        '/api/driver_promocodes/add/',
        json.dumps(request_json),
        'application/json'
    )
    request.login = 'dmkurilov'
    request.uid = 0
    request.superuser = is_superuser
    request.groups = []
    request.permissions = {admin_permissions.edit_driver_promocodes: {'mode': 'unrestricted'}}
    request.user_ticket = None
    request.time_storage = evlog.new_time_storage('')
    request.remote_addr = '127.0.0.1'

    if has_require_ticket_validation_permission:
        request.permissions[admin_permissions.require_ticket_validation] = {'mode': 'unrestricted'}

    def check_data_access(*args, **kwargs):
        return {
            'access_status': apiutils.USER_DATA_PERMITTED if chatterbox_check_data_access_response else ''
        }

    def get_yateam_info_by_sid(*args, **kwargs):
        return {'user_ticket': 42}

    monkeypatch.setattr(chatterbox, 'check_data_access', check_data_access)
    monkeypatch.setattr(passport, 'get_yateam_info_by_sid', get_yateam_info_by_sid)
    response = api_driver_promocodes.add_promocode(request)

    if not is_superuser and (has_require_ticket_validation_permission and not chatterbox_check_data_access_response):
        expected_code = 406

    assert response.status_code == expected_code
    if response.status_code == 200:
        data = json.loads(response.content)
        assert 'id' in data

        doc = yield db.driver_promocodes.find_one({
            '_id': data['id']
        })
        doc.pop('_id')
        assert 'code' in doc
        doc.pop('code')
        assert doc == expected_data


@pytest.mark.now('2018-09-10T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    SUPPORT_PROMOCODE_GENERATIONS_LIMIT_PER_TICKET=1,
)
def test_add_promocode_zendesk_limit_per_ticket(patch):
    client = django_test.Client()
    response = client.post(
        '/api/driver_promocodes/add/',
        json.dumps({
            'series_id': 'nominal_1',
            'clid': 'clid1',
            'uuid': 'uuid1',
            'description': 'promocode for driver',
            'zendesk_ticket': '123456'
        }),
        'application/json'
    )
    assert response.status_code == 406
