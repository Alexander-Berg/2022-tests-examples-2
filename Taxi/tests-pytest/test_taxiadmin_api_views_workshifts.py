import collections
import datetime
import json

from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import audit_actions


@pytest.mark.config(
    WORKSHIFTS_DEFAULT_CATEGORIES=['econom']
)
@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.asyncenv('blocking')
def test_list_workshift(load):
    test_client = django_test.Client()
    response = test_client.get('/api/workshift/list/moscow/')
    assert response.status_code == 200
    data = json.loads(response.content)
    expected_data = json.loads(load('response/expected_list_workshift.json'))

    data['items'] = sorted(data['items'], key=lambda x: x['id'])
    expected_data['items'] = sorted(expected_data['items'],
                                    key=lambda x: x['id'])
    assert data == expected_data


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
    WORKSHIFTS_DEFAULT_CATEGORIES=['econom']
)
@pytest.mark.parametrize('request_json,expected_data', [
    (
        {
            'parent_id': None,
            'zones': [
                'moscow'
            ],
            'is_active': False,
            'percent_discount_available': False,
            'view_type': 'base',
            'begin': '2017-03-01T10:00:00+03:00',
            'price': '100',
            'price_list': [],
            'duration_hours': 12,
            'ticket': 'TAXIRATE-123',
            'request_id': '8f12be08a2b34b809a2c1ccb7bb8347a',
            'hiring_extra_percent': 0.12,
            'discount_conditions': []
        },
        {
            'parent_id': None,
            'created': datetime.datetime(2017, 3, 1, 7, 0),
            'updated': datetime.datetime(2017, 3, 1, 7, 0),
            'home_zone': 'moscow',
            'zones': [
                'moscow'
            ],
            'tariffs': [
                'econom'
            ],
            'is_active': False,
            'percent_discount_available': False,
            'view_type': 'base',
            'begin': datetime.datetime(2017, 3, 1, 7),
            'end': None,
            'price': '100',
            'price_list': [],
            'duration_hours': 12,
            'hiring_extra_percent': '0.12',
            'request_id': 'dmkurilov_8f12be08a2b34b809a2c1ccb7bb8347a',
            'discount_conditions': [],
            'driver_experiment_id': None,
            'title_key': None
        }
    ),
    (
        {
            'zones': [
                'moscow',
                'mytishchi'
            ],
            'tariffs': [
                'econom',
                'comfort'
            ],
            'parent_id': 'shift1',
            'is_active': False,
            'percent_discount_available': True,
            'view_type': 'schedule',
            'begin': '2017-03-01T10:00:00+03:00',
            'price': None,
            'price_list': [
                {
                    'week_day': 'mon',
                    'price': '600',
                    'time': '06:00',
                    'duration_hours': 1
                },
                {
                    'week_day': 'mon',
                    'price': '700',
                    'time': '07:00',
                    'duration_hours': 1
                }
            ],
            'duration_hours': 24,
            'ticket': 'TAXIRATE-123',
            'request_id': '8f12be08a2b34b809a2c1ccb7bb8347b',
            'hiring_extra_percent': 0.12,
            'driver_experiment_id': ' exp1 ',
            'discount_conditions': [
                {
                    'experiment_id': ' exp1',
                    'discount_percent': '15',
                    'show_discount_badge': True
                }
            ],
            'title_key': 'moscow '
        },
        {
            'parent_id': 'shift1',
            'created': datetime.datetime(2017, 3, 1, 7, 0),
            'updated': datetime.datetime(2017, 3, 1, 7, 0),
            'home_zone': 'moscow',
            'zones': [
                'moscow',
                'mytishchi'
            ],
            'tariffs': [
                'econom',
                'comfort'
            ],
            'is_active': False,
            'percent_discount_available': True,
            'view_type': 'schedule',
            'begin': datetime.datetime(2017, 3, 1, 7),
            'end': None,
            'price': None,
            'price_list': [
                {
                    'week_day': 'mon',
                    'price': '600',
                    'time': '06:00',
                    'duration_hours': 1
                },
                {
                    'week_day': 'mon',
                    'price': '700',
                    'time': '07:00',
                    'duration_hours': 1
                }
            ],
            'duration_hours': 24,
            'hiring_extra_percent': '0.12',
            'request_id': 'dmkurilov_8f12be08a2b34b809a2c1ccb7bb8347b',
            'discount_conditions': [
                {
                    'experiment_id': 'exp1',
                    'discount_percent': '15',
                    'show_discount_badge': True
                }
            ],
            'driver_experiment_id': 'exp1',
            'title_key': 'moscow'
        }
    )
])
@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_add_workshift(request_json, expected_data):
    test_client = django_test.Client()
    response = test_client.post(
        '/api/workshift/add/moscow/',
        json.dumps(request_json),
        'application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert 'id' in data

    doc = yield db.workshift_rules.find_one({'_id': data['id']})

    assert data['id'] == doc['_id']
    doc.pop('_id')

    assert doc == expected_data

    action = yield db.log_admin.find_one({
        'action': audit_actions.add_workshift.id,
    })
    assert action is not None
    assert action['ticket'] == 'TAXIRATE-123'


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
    WORKSHIFTS_DEFAULT_CATEGORIES=['econom'],
    WORKSHIFTS_NEED_TO_CHECK_TOPIC=True
)
@pytest.mark.parametrize('experiment_id,expected_code', [
    (
        'exp1',
        200
    ),
    (
        'exp2',
        400
    )
])
@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.asyncenv('blocking')
def test_add_workshift_check_topic(experiment_id, expected_code, patch):
    @patch('taxi.external.tags_service.topics_items')
    @async.inline_callbacks
    def topics_items(
        src_service,
        topic=None,
        tag_contains=None,
        offset=None,
        limit=None,
        log_extra=None
    ):
        assert topic == 'workshifts'
        yield async.return_value([{'tag': 'exp1', 'topic': topic}])

    test_client = django_test.Client()
    response = test_client.post(
        '/api/workshift/add/moscow/', json.dumps({
            'parent_id': None,
            'zones': [
                'moscow'
            ],
            'is_active': False,
            'percent_discount_available': False,
            'view_type': 'base',
            'begin': '2017-03-01T10:00:00+03:00',
            'price': '100',
            'price_list': [],
            'duration_hours': 12,
            'ticket': 'TAXIRATE-123',
            'request_id': '8f12be08a2b34b809a2c1ccb7bb8347a',
            'hiring_extra_percent': 0.12,
            'driver_experiment_id': experiment_id,
            'discount_conditions': [
                {
                    'experiment_id': experiment_id,
                    'discount_percent': '15',
                    'show_discount_badge': True
                }
            ],
        }), 'application/json'
    )
    assert response.status_code == expected_code


@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.filldb(workshift_rules='overlapping')
@pytest.mark.asyncenv('blocking')
def test_add_workshift_overlapping():
    test_client = django_test.Client()
    response = test_client.post(
        '/api/workshift/add/moscow/', json.dumps({
            'parent_id': None,
            'zones': [
                'moscow',
                'mytishchi',
                'lyberci'
            ],
            'tariffs': [
                'econom'
            ],
            'is_active': True,
            'percent_discount_available': False,
            'view_type': 'base',
            'begin': '2016-02-08T22:35:00+03:00',
            'price': '100',
            'price_list': [],
            'duration_hours': 24,
            'discount_conditions': [],
            'ticket': 'TAXIRATE-123',
            'request_id': '00000000000000000000000000000001',
        }), 'application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.content)
    assert data == {
        'code': 'overlapping',
        'message': 'Overlapping workshifts',
        'details': [
            {
                'id': 'shift-with-schedule',
                'created': '2016-02-09T13:35:00+0300',
                'begin': '2016-02-09T13:35:00+0300',
                'end': '2016-02-10T13:35:00+0300',
                'home_zone': 'moscow',
            }
        ],
        'status': 'error'
    }


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.filldb(workshift_rules='overlapping')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_add_workshift_warning():
    test_client = django_test.Client()
    response = test_client.post(
        '/api/workshift/add/spb/', json.dumps({
            'zones': [
                'spb'
            ],
            'tariffs': [
                'econom'
            ],
            'parent_id': 'shift1',
            'is_active': True,
            'percent_discount_available': True,
            'view_type': 'schedule',
            'begin': '2016-02-07T10:00:00+03:00',
            'price': None,
            'price_list': [
                {
                    'week_day': 'mon',
                    'price': '600',
                    'time': '06:00',
                    'duration_hours': 1
                }
            ],
            'duration_hours': 24,
            'ticket': 'TAXIRATE-123',
            'request_id': '8f12be08a2b34b809a2c1ccb7bb8347b',
            'hiring_extra_percent': 0.12,
            'driver_experiment_id': 'experiment1',
            'discount_conditions': [],
            'title_key': 'spb',
        }), 'application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert 'id' in data

    doc = yield db.workshift_rules.find_one({'_id': data['id']})

    assert data['id'] == doc['_id']
    doc.pop('_id')
    assert data['message'] == (
        'These experiments are not allowed to have '
        'the same drivers: experiment1, experiment2'
    )

    assert doc == {
        'parent_id': 'shift1',
        'created': datetime.datetime(2017, 3, 1, 7, 0),
        'updated': datetime.datetime(2017, 3, 1, 7, 0),
        'home_zone': 'spb',
        'zones': [
            'spb'
        ],
        'tariffs': [
            'econom'
        ],
        'is_active': True,
        'percent_discount_available': True,
        'view_type': 'schedule',
        'begin': datetime.datetime(2016, 2, 7, 7),
        'end': None,
        'price': None,
        'price_list': [
            {
                'week_day': 'mon',
                'price': '600',
                'time': '06:00',
                'duration_hours': 1
            }
        ],
        'duration_hours': 24,
        'hiring_extra_percent': '0.12',
        'request_id': 'dmkurilov_8f12be08a2b34b809a2c1ccb7bb8347b',
        'discount_conditions': [],
        'driver_experiment_id': 'experiment1',
        'title_key': 'spb'
    }

    action = yield db.log_admin.find_one({
        'action': audit_actions.add_workshift.id,
    })
    assert action is not None
    assert action['ticket'] == 'TAXIRATE-123'


@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.asyncenv('blocking')
def test_add_workshift_conflict():
    test_client = django_test.Client()
    response = test_client.post(
        '/api/workshift/add/moscow/', json.dumps({
            'parent_id': None,
            'zones': [
                'moscow'
            ],
            'is_active': False,
            'percent_discount_available': False,
            'view_type': 'base',
            'begin': '2017-03-01T10:00:00+03:00',
            'price': '100',
            'price_list': [],
            'duration_hours': 12,
            'discount_conditions': [],
            'ticket': 'TAXIRATE-123',
            'request_id': '00000000000000000000000000000000',
        }), 'application/json'
    )
    assert response.status_code == 409
    data = json.loads(response.content)
    assert data == {
        'code': 'already-exists',
        'message': 'Object already created',
        'object_id': 'shift-that-already-exists',
        'status': 'error'
    }


@pytest.mark.parametrize('method', [
    ('POST'),
    ('PATCH')
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_edit_workshift(method):
    shift_id = 'shift4'
    request_json = {
        'is_active': False,
        'begin': '2017-03-01T10:00:00+03:00',
        'end': '2017-03-10T10:00:00+03:00',
        'discount_conditions': [
            {
                'experiment_id': 'exp1',
                'discount_price': '260',
                'show_discount_badge': False
            }
        ],
        'ticket': 'TAXIRATE-123'
    }

    if method == 'POST':
        response = django_test.Client().post(
            '/api/workshift/edit/%s/' % shift_id,
            json.dumps(request_json),
            'application/json'
        )
    else:
        response = django_test.Client().put(
            '/api/workshift/edit/%s/' % shift_id,
            json.dumps(request_json),
            'application/json',
            REQUEST_METHOD='PATCH'
        )

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {'id': shift_id}

    doc = yield db.workshift_rules.find_one({'_id': shift_id})
    assert doc == {
        '_id': shift_id,
        'request_id': 'request-%s' % shift_id,
        'home_zone': 'moscow',
        'is_active': False,
        'percent_discount_available': False,
        'view_type': 'base',
        'updated': datetime.datetime(2017, 3, 1, 10, 0),
        'created': datetime.datetime(2016, 2, 9, 10, 35),
        'begin': datetime.datetime(2017, 3, 1, 7),
        'end': datetime.datetime(2017, 3, 10, 7),
        'price': '100',
        'hiring_extra_percent': '0.12',
        'discount_conditions': [
            {
                'experiment_id': 'exp1',
                'discount_price': '260',
                'show_discount_badge': False
            }
        ],
        'duration_hours': 10
    }

    action = yield db.log_admin.find_one({
        'action': audit_actions.edit_workshift.id,
    })
    assert action is not None
    assert action['ticket'] == 'TAXIRATE-123'


@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.filldb(workshift_rules='overlapping')
@pytest.mark.asyncenv('blocking')
def test_edit_workshift_overlapping():
    shift_id = 'shift-overlapping'
    response = django_test.Client().put(
        '/api/workshift/edit/%s/' % shift_id,
        json.dumps({
            'is_active': True,
            'begin': '2016-02-08T22:35:00+03:00',
            'ticket': 'TAXIRATE-12',
        }),
        'application/json',
        REQUEST_METHOD='PATCH'
    )
    assert response.status_code == 400
    data = json.loads(response.content)
    assert data == {
        'code': 'overlapping',
        'message': 'Overlapping workshifts',
        'details': [
            {
                'id': 'shift-with-schedule',
                'created': '2016-02-09T13:35:00+0300',
                'begin': '2016-02-09T13:35:00+0300',
                'end': '2016-02-10T13:35:00+0300',
                'home_zone': 'moscow',
            }
        ],
        'status': 'error'
    }


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2017-03-01T10:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_workshift(shift_id='shift1'):
    test_client = django_test.Client()
    response = test_client.post(
        '/api/workshift/delete/%s/' % shift_id,
        json.dumps({
            'ticket': 'TAXIRATE-123'
        }), 'application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {'id': shift_id}

    doc = yield db.workshift_rules.find_one(
        {'_id': shift_id, 'is_deleted': True}
    )
    assert doc == {
        '_id': shift_id,
        'request_id': 'request-%s' % shift_id,
        'home_zone': 'moscow',
        'is_active': False,
        'is_deleted': True,
        'percent_discount_available': False,
        'view_type': 'base',
        'updated': datetime.datetime(2017, 3, 1, 10, 0),
        'created': datetime.datetime(2016, 2, 9, 10, 35),
        'begin': datetime.datetime(2016, 2, 9, 10, 35),
        'price': '100',
        'hiring_extra_percent': '0.12',
        'duration_hours': 10
    }

    action = yield db.log_admin.find_one({
        'action': audit_actions.edit_workshift.id,
    })
    assert action is not None
    assert action['ticket'] == 'TAXIRATE-123'


@pytest.mark.now('2019-07-03T01:06:01+03:00')
@pytest.mark.asyncenv('blocking')
def test_approvals_create_check(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_tuple = collections.namedtuple('uuid4', 'hex')
        return uuid4_tuple('c2252f07b652410a887bc4599a5f6763')

    client = django_test.Client()
    request_data = load('request/approvals_create_check_request_data.json')
    expected_response = json.loads(
        load('response/approvals_create_check_expected_response.json'),
    )
    response = client.post(
        '/api/approvals/workshifts_create/check/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_response


@pytest.mark.asyncenv('blocking')
def test_approvals_create_apply(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = load('request/approvals_create_apply_request_data.json')
    response = client.post(
        '/api/approvals/workshifts_create/apply/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.now('2019-07-03T01:06:01+03:00')
@pytest.mark.asyncenv('blocking')
def test_approvals_edit_check(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = load('request/approvals_edit_check_request_data.json')
    expected_response = json.loads(
        load('response/approvals_edit_check_expected_response.json'),
    )
    response = client.post(
        '/api/approvals/workshifts_edit/check/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_response


@pytest.mark.asyncenv('blocking')
def test_approvals_edit_apply(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = load('request/approvals_edit_apply_request_data.json')
    response = client.post(
        '/api/approvals/workshifts_edit/apply/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}
