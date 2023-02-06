# coding: utf-8

from __future__ import unicode_literals

import copy
import datetime
import json

from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db


@pytest.fixture
def startrack_ext_request(areq_request):
    @areq_request
    def ext_request(*args, **kwargs):
        return areq_request.response(200, json.dumps({
            'status': {'key': 'approved'},
            'assignee': {'id': 'assignee'},
            'createdBy': {'id': 'creator'}
        }))
    return ext_request


@pytest.fixture(autouse=True)
def mock_last_approver(patch):
    @patch('taxiadmin.audit.get_last_approver')
    @async.inline_callbacks
    def get_last_approver(*args, **kwargs):
        yield
        async.return_value(('approver', None))


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.config(
    ADMIN_AUDIT_TICKET_CONFIG={
        'enabled': True,
        'queues': {
            'TAXIRATE': {
                'statuses': ['approved']
            }
        },
        'components': {},
    },
    PROMOCODES_ADMIN_NEW_API=True
)
@pytest.mark.parametrize('extra_data,status_code,startrack_call', [
    ({'first_limit': 1}, 200, False),
    ({'external_budget': True, 'first_limit': 1}, 200, False),
    ({'external_budget': True, 'ticket': 'TAXIRATE-10'}, 200, True),
    ({'ticket': 'TAXIRATE-10'}, 200, True),
    ({}, 400, False)
])
@pytest.inline_callbacks
def test_add_promocode(startrack_ext_request, extra_data,
                       status_code, startrack_call):
    data = {
        'country': 'rus',
        'creditcard_only': True,
        'descr': 'descr',
        'finish': '2016-12-01',
        'for_support': False,
        'is_unique': False,
        'series_id': 'ssr',
        'start': '2016-11-01',
        'user_limit': 1,
        'value': 250,
    }
    data.update(extra_data)

    response = django_test.Client().post(
        '/api/promocodes/add/', json.dumps(data), 'application/json'
    )

    assert response.status_code == status_code, response.content
    if status_code == 200:
        assert response.content == '{}'
        doc = yield db.promocode_series.find_one('ssr')
        data['_id'] = data.pop('series_id')
        data['clear_text'] = True
        data['created'] = datetime.datetime.utcnow()
        data['currency'] = 'RUB'
        data['finish'] = datetime.datetime(2016, 12, 1)
        data['start'] = datetime.datetime(2016, 11, 1)
        data['creator'] = {'login': 'dmkurilov', 'uid': 0}
        data['services'] = ['taxi']
        assert doc == data

    if startrack_call:
        assert startrack_ext_request.call
    else:
        assert not startrack_ext_request.call


GOOD_CLASSES = ['econom', 'uberkids']
WRONG_CLASS = ['notexist']

DATA_FOR_CREATE = {
    'country': 'rus',
    'creditcard_only': True,
    'descr': 'descr',
    'finish': '2016-12-01',
    'first_limit': 1,
    'for_support': False,
    'is_unique': False,
    'series_id': 'ssr',
    'start': '2016-11-01',
    'user_limit': 1,
    'value': 250,
    'classes': GOOD_CLASSES
}

DATA_FOR_EDIT = {
    'finish': '2016-12-03',
    'series_id': '1qwert',
    'classes': GOOD_CLASSES
}


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.inline_callbacks
def test_add_promocode_classes():
    """
    Checks that choosen classes exist in config.
    Classes is non-mandatory parameter, request without classes is
    1. Request contains wrong class
    2. Request contains only good classes
    """

    url = '/api/promocodes/add/'

    data = copy.copy(DATA_FOR_CREATE)

    # 1. Request contains wrong class with good clases

    data['classes'] = WRONG_CLASS + GOOD_CLASSES

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == 400, response.content

    # 2. Request contains only good classes

    data['classes'] = GOOD_CLASSES

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == 200, response.content
    doc = yield db.promocode_series.find_one('ssr')

    # other contents are checked in func test_add_promocode
    assert doc['classes'] == GOOD_CLASSES


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize('payment_methods,status_code', [
    (['notexist'], 400),
    (['notexist', 'card'], 400),
    (None, 200),  # field not passed
    ([], 200),
    (['card'], 200),
    (['cash', 'coop_account'], 200),
])
@pytest.inline_callbacks
def test_add_promocode_payment_methods(payment_methods, status_code):
    """
    Checks that choosen payment_methods exist in config.
    """

    url = '/api/promocodes/add/'

    data = copy.copy(DATA_FOR_CREATE)
    data.pop('creditcard_only')
    if payment_methods is not None:
        data['payment_methods'] = payment_methods

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == status_code, response.content

    doc = yield db.promocode_series.find_one('ssr')

    if status_code == 200:
        if payment_methods is not None:
            # other contents are checked in test_add_promocode
            assert doc['payment_methods'] == payment_methods
        else:
            assert 'payment_methods' not in doc
    else:
        assert doc is None


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize('services,status_code', [
    (None, 400),
    ([], 406),
    (['notexist'], 400),
    (['taxi'], 200),
    (['lavka'], 200),
    (['taxi', 'lavka'], 406)  # temp solution for MVP
])
@pytest.inline_callbacks
def test_add_promocode_service(services, status_code):
    """
    Checks that choosen services exist in config.
    """

    url = '/api/promocodes/add/'

    data = copy.copy(DATA_FOR_CREATE)
    data['services'] = services

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == status_code, response.content

    doc = yield db.promocode_series.find_one('ssr')

    if status_code == 200:
        # other checks in another func
        assert doc['services'] == services
    else:
        assert doc is None


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize('meta,status_code', [
    (None, 200),
    ({}, 200),
    ({'id': 123}, 200),
    ({'arr0': []}, 200),
    ({'arr1': [1, 2, 3, 10000]}, 200),
    ({'arr2': ['taxi', 'lavka']}, 200),
    ({'arr3': [{'id': 'taxi'}, {'id': 'eda'}]}, 200),
    ({'str': 'my string'}, 200),
    ({'user': {'id': 123}}, 200),
    ({'user': {'id': 123}, 'city': 'Moscow', 'uids': []}, 200),
])
@pytest.inline_callbacks
def test_add_promocode_meta(meta, status_code):
    """
    Checks that meta works fine for add.
    """

    url = '/api/promocodes/add/'

    data = copy.copy(DATA_FOR_CREATE)
    data['external_meta'] = meta

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == status_code, response.content

    doc = yield db.promocode_series.find_one('ssr')

    if status_code == 200:
        # other checks in another func
        assert doc.get('external_meta') == meta
    else:
        assert doc is None


@pytest.mark.filldb(promocode_usages='edit')
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.config(
    ADMIN_AUDIT_TICKET_CONFIG={
        'enabled': True,
        'queues': {
            'TAXIRATE': {
                'statuses': ['approved']
            }
        },
        'components': {},
    },
    PROMOCODES_ADMIN_NEW_API=True
)
@pytest.mark.parametrize(
    'extra_data,first_limit,external_budget,status_code,startrack_call',
    [
        ({}, None, False, 400, False),
        ({'ticket': 'TAXIRATE-10'}, None, False, 200, True),
        ({'ticket': 'TAXIRATE-10', 'descr': '1234'}, None, False, 400, False),
        (
            {
                'descr': '1234',
                'start': '2016-11-01',
                'user_limit': 10,
                'creditcard_only': False
            }, None, True, 200, False
        ),
        (
            {
                'descr': '1234',
                'start': '2016-11-01',
                'user_limit': 10,
                'creditcard_only': False,
                'value': 200,
            }, None, True, 400, False
        ),
        (
            {
                'descr': '1234',
                'start': '2016-11-01',
                'user_limit': 10,
                'creditcard_only': False
            }, 1, True, 400, False
        ),
        (
            {
                'descr': '1234',
                'start': '2016-11-01',
                'user_limit': 10,
                'creditcard_only': False,
                'country': 'rus',
                'for_support': True,
                'is_unique': True,
                'value': 200,
            }, 1, True, 200, False
        ),
        (
            {
                'descr': '1234',
                'start': '2016-11-01',
                'user_limit': 10,
                'creditcard_only': False,
                'country': 'rus',
                'for_support': True,
                'is_unique': True,
                'value': 200,
            }, 1, False, 200, False
        ),
        (
            {
                'descr': '1234',
                'start': '2016-11-02',
                'user_limit': 10,
                'creditcard_only': False,
                'country': 'rus',
                'for_support': True,
                'is_unique': True,
                'value': 200,
            }, 1, False, 400, False
        )
    ]
)
@pytest.inline_callbacks
def test_edit_promocode(startrack_ext_request, extra_data, first_limit,
                        external_budget, status_code, startrack_call):
    yield db.promocode_series.update(
        {'_id': 'sery'},
        {
            '$set': {
                'first_limit': first_limit,
                'external_budget': external_budget
            }
        }
    )

    data = {
        'series_id': 'sery',
        'finish': '2016-12-03',
        'classes': ['econom'],
        'cities': ['moscow']
    }
    data.update(extra_data)

    response = django_test.Client().post(
        '/api/promocodes/edit/', json.dumps(data), 'application/json'
    )
    assert response.status_code == status_code, response.content
    if status_code == 200:
        assert response.content == '{}'
        doc = yield db.promocode_series.find_one('sery')
        assert doc['_id'] == data['series_id']
        assert doc['finish'] == datetime.datetime(2016, 12, 3)
        assert doc['classes'] == data['classes']
        assert doc['cities'] == data['cities']

    if startrack_call:
        assert startrack_ext_request.call
    else:
        assert not startrack_ext_request.call


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.inline_callbacks
def test_edit_promocode_classes():

    '''
    Checks that choosen classes exist in config.
    Classes is non-mandatory parameter, request without classes is
    1. Request contains wrong class
    2. Request contains only good classes
    '''

    url = '/api/promocodes/edit/'

    data = copy.copy(DATA_FOR_EDIT)

    # 1. Request contains wrong class with good clases

    data['classes'] = WRONG_CLASS + GOOD_CLASSES

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == 400, response.content

    # 2. Request contains only good classes

    data['classes'] = GOOD_CLASSES

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == 200, response.content
    doc = yield db.promocode_series.find_one('1qwert')

    # other contents are checked in func test_edit_promocode
    assert doc['classes'] == GOOD_CLASSES


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize('payment_methods,status_code', [
    (['notexist'], 400),
    (['notexist', 'card'], 400),
    (None, 200),  # field not passed
    ([], 200),
    (['card'], 200),
    (['cash', 'coop_account'], 200),
])
@pytest.inline_callbacks
def test_edit_promocode_payment_methods(payment_methods, status_code):
    """
    Checks that choosen payment_methods exist in config.
    """

    url = '/api/promocodes/edit/'

    data = copy.copy(DATA_FOR_EDIT)
    if payment_methods is not None:
        data['payment_methods'] = payment_methods

    doc_before = yield db.promocode_series.find_one('1qwert')

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == status_code, response.content

    doc_after = yield db.promocode_series.find_one('1qwert')

    if status_code == 200:
        if payment_methods is not None:
            # other contents are checked in func test_edit_promocode
            assert doc_after['payment_methods'] == payment_methods
        else:
            assert 'payment_methods' not in doc_after
    else:
        assert doc_before == doc_after


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize('services,status_code', [
    (None, 400),
    ([], 400),
    (['notexist'], 400),
    (['taxi'], 200),
    (['lavka'], 200),
    (['taxi', 'lavka'], 400)  # temp solution for MVP
])
@pytest.inline_callbacks
def test_edit_promocode_service(services, status_code):

    '''
    Checks that choosen services not empty and exist in config.
    '''

    url = '/api/promocodes/edit/'

    data = copy.copy(DATA_FOR_EDIT)
    data['services'] = services

    doc_before = yield db.promocode_series.find_one('1qwert')

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == status_code, response.content

    doc_after = yield db.promocode_series.find_one('1qwert')

    if status_code == 200:
        # other checks in another func
        assert doc_after['services'] == services
    else:
        assert doc_before == doc_after


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize('meta,status_code', [
    (None, 200),
    ({}, 200),
    ({'id': 123}, 200),
    ({'arr0': []}, 200),
    ({'arr1': [1, 2, 3, 10000]}, 200),
    ({'arr2': ['taxi', 'lavka']}, 200),
    ({'arr3': [{'id': 'taxi'}, {'id': 'eda'}]}, 200),
    ({'str': 'my string'}, 200),
    ({'user': {'id': 123}}, 200),
    ({'user': {'id': 123}, 'city': 'Moscow', 'uids': []}, 200),
])
@pytest.inline_callbacks
def test_edit_promocode_meta(meta, status_code):
    """
    Checks that meta works fine for edit.
    """

    url = '/api/promocodes/edit/'

    data = copy.copy(DATA_FOR_EDIT)
    data['external_meta'] = meta

    doc_before = yield db.promocode_series.find_one('1qwert')

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == status_code, response.content

    doc_after = yield db.promocode_series.find_one('1qwert')

    if status_code == 200:
        # other checks in another func
        assert doc_after.get('external_meta') == meta
    else:
        assert doc_before == doc_after


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize("use_coupons", [True, False])
def test_usage_promocode(
    patch,
    use_coupons_exp3,
    coupons_find_one,
    use_coupons
):
    use_coupons_exp3(use_coupons)
    data = {
        'series_id': 'sery',
    }
    response = django_test.Client().post(
        '/api/promocodes/usages/', json.dumps(data), 'application/json'
    )
    assert response.status_code == 200, response.content
    assert response.content == '[]'


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize("use_coupons", [True, False])
@pytest.mark.parametrize("unique_code, status_code", [
    ("sery123456", 200),
    ("sery777777", 406),
    ("wrong_format", 400)
])
def test_usage_promocode_by_code(
    patch,
    use_coupons_exp3,
    coupons_find_one,
    use_coupons,
    unique_code,
    status_code
):
    use_coupons_exp3(use_coupons)
    data = {
        'series_id': 'sery',
        'unique_code': unique_code
    }
    response = django_test.Client().post(
        '/api/promocodes/usages/', json.dumps(data), 'application/json'
    )
    assert response.status_code == status_code, response.content
    if status_code == 200:
        assert response.content == '[]'


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-11-01T11:00:00.0')
@pytest.mark.parametrize(
    'field_name',
    [
        'first_usage_by_classes',
        'first_usage_by_payment_methods'
    ]
)
@pytest.inline_callbacks
def test_add_promocode_check_optional_fields(field_name):
    url = '/api/promocodes/add/'

    data = copy.copy(DATA_FOR_CREATE)
    data[field_name] = True

    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )

    assert response.status_code == 200, response.content
    doc = yield db.promocode_series.find_one('ssr')

    assert doc[field_name]


@pytest.mark.now('2019-07-02T22:06:01')
@pytest.mark.asyncenv('blocking')
def test_approvals_create_check(patch, load):
    client = django_test.Client()
    request_data = load('request/approvals_create_check_request_data.json')
    expected_response = json.loads(
        load('response/approvals_create_check_expected_response.json'),
    )
    error_first_limit_response = client.post(
        '/api/approvals/promocodes_create/check/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert error_first_limit_response.status_code == 400
    assert json.loads(error_first_limit_response.content) == {
        'message': 'wrong handler for first_limit',
        'code': 'bad_request',
        'status': 'error',
    }
    response = client.post(
        '/api/approvals/promocodes_first_limit_create/check/',
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
    client = django_test.Client()
    request_data = load('request/approvals_create_apply_request_data.json')
    response = client.post(
        '/api/approvals/promocodes_create/apply/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {'status': 'succeeded'}


@pytest.mark.now('2019-07-02T22:06:01')
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('edit_handler', ['edit', 'external_budget_edit'])
def test_approvals_edit_check(patch, load, edit_handler):
    client = django_test.Client()
    request_data = load('request/approvals_edit_check_request_data.json')
    expected_response = json.loads(
        load('response/approvals_edit_check_expected_response.json'),
    )
    error_first_limit_response = client.post(
        '/api/approvals/promocodes_{}/check/'.format(edit_handler),
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert error_first_limit_response.status_code == 400
    assert json.loads(error_first_limit_response.content) == {
        'message': 'wrong handler for first_limit',
        'code': 'bad_request',
        'status': 'error',
    }
    response = client.post(
        '/api/approvals/promocodes_first_limit_edit/check/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_response


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('edit_handler', ['edit', 'external_budget_edit'])
def test_approvals_edit_apply(patch, load, edit_handler):
    client = django_test.Client()
    request_data = load('request/approvals_edit_apply_request_data.json')
    response = client.post(
        '/api/approvals/promocodes_{}/apply/'.format(edit_handler),
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200  # handlers are equal in py2
