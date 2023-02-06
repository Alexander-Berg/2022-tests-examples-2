# -*- coding: utf-8 -*-
import json

import pytest

from django import test as django_test
from django.test import utils

from taxi.core import async
from taxi.internal import admin_restrictions

from taxiadmin.api.views import users as api_views_users
from taxiadmin.api.views import user_info as api_views_user_info

import helpers


@pytest.mark.asyncenv('blocking')
def test_get_scripts(patch):
    _patch_internals(patch, {})
    response = django_test.Client().get('/api/user_info/')
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['login'] == 'dmkurilov'
    assert 'approve_scripts' in data['permissions']
    assert 'approve_scripts_manager' in data['permissions']


def _patch_internals(patch, config):

    @patch('taxi.external.experiments3.get_config_values')
    @async.inline_callbacks
    def _get_experiments(consumer, config_name, *args, **kwargs):
        yield
        if config_name in config:
            resp = [
                admin_restrictions.experiments3.ExperimentsValue(
                    config_name, config[config_name],
                ),
            ]
        else:
            resp = []
        async.return_value(resp)


case = helpers.case_getter(
    'groups config expected_filters',
)

DEFAULT_CONFIG = {
    admin_restrictions.COUNTRY_ACCESS_CONFIG_NAME: {
        'rus': {
            'groups': [
                'russian_manager',
            ],
        },
    },
    admin_restrictions.CONFIG_NAME: {
        '/orders/': {
            'last_days': 7,
            'last_orders': 7,
        },
        '/payments/orders_info/': {
            'last_days': 7,
            'last_orders': 7,
        },
    },
}


@pytest.mark.parametrize(
    case.params,
    [
        # merging filters for different handles
        case(
            groups=['russian_manager'],
            config=DEFAULT_CONFIG,
            expected_filters={
                '/orders/': {
                    'last_days': 7,
                    'last_orders': 7,
                },
                '/payments/orders_info/': {
                    'last_days': 7,
                    'last_orders': 7,
                },
            },
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_api_user_info_filters(patch, groups, config, expected_filters):
    _patch_internals(patch, config)
    request = helpers.TaxiAdminRequest(groups=groups).get('')
    response = yield api_views_users.user_info(request)
    data = json.loads(response.content)
    assert data.get('filters') == expected_filters, data


@utils.override_settings(BLACKBOX_AUTH=True)
@pytest.mark.asyncenv('blocking')
def test_user_info_v2():
    request = django_test.RequestFactory().get('/api/user_info/v2/')
    request.superuser = False
    request.groups = ['group_1', 'group_3']
    request.login = 'test_login'
    response = api_views_users.user_info_v2(request)
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['login'] == 'test_login'
    assert sorted(data['permissions'], key=lambda p: p['id']) == [
        {
            'id': 'edit_classification_rules',
            'mode': 'countries_filter',
            'countries_filter': ['blr', 'rus']
        },
        {'id': 'view_classification_rules', 'mode': 'unrestricted'},
        {'id': 'view_map', 'mode': 'unrestricted'},
    ]


REQUEST_YANDEX = {
    'phone': 'phone_number_1',
    'phone_type': 'yandex',
    'ticket': 'SOMETICKET-123',
}
REQUEST_UBER = {
    'phone': 'phone_number_2',
    'phone_type': 'uber',
    'ticket': 'SOMETICKET-123',
}
REQUEST_DELETED = {
    'phone': 'phone_number_0',
    'phone_type': 'deleted:yandex:TICKET-123:some_uuid_for_uniqueness_000_000',
    'ticket': 'SOMETICKET-123',
}
REQUEST_ABSENT_PHONE = {
    'phone': '+79008007060',
    'phone_type': 'partner',
    'ticket': 'SOMETICKET-123',
}
REQUEST_NO_TICKET = {
    'phone': 'phone_number_1',
    'phone_type': 'yandex',
}
case = helpers.case_getter(
    'request_data groups expected_code expected_response new_type_startswith'
    ' log_admin_doc',
)
case_group_deleter = case.partial(
    groups=['group_deleter'],
    expected_code=200,
)


@pytest.mark.parametrize(
    'uuid,user_id,phone,user_phone_id,expected_code,expected_length',
    [
        ('some_uuid_enlarged_to_32_symbols', None, None, None, 200, 1),
        (None, 'some_user_id', None, None, 200, 1),
        (None, None, 'some_phone', None, 200, 1),
        (None, None, None, '5c1122bfcb688c63c949f557', 200, 1),
        (
            'some_uuid_enlarged_to_32_symbols', 'some_user_id',
            None, None, 200, 1
        ),
        (
            'some_uuid_enlarged_to_32_symbols', None, 'some_phone',
            None, 200, 1
        ),
        (None, 'some_user_id', 'some_phone', None, 200, 1),
        (
            'some_uuid_enlarged_to_32_symbols', 'wrong_user_id', None,
            None, 404, None
        ),
        (
            'some_uuid_enlarged_to_32_symbols', None, 'wrong_phone',
            None, 404, None
        ),
        (None, None, 'wrong_phone', 'wrong_user_phone_id', 400, None),
        (None, 'wrong_uuid', 'some_phone', None, 404, None),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_get_user_info(uuid, user_id, phone, user_phone_id, expected_code,
                       expected_length):
    params = []
    if uuid is not None:
        params.append('yandex_uuid={}'.format(uuid))
    if user_id is not None:
        params.append('user_id={}'.format(user_id))
    if phone is not None:
        params.append('phone={}'.format(phone))
    if user_phone_id is not None:
        params.append('user_phone_id={}'.format(user_phone_id))
    response = django_test.Client().get('/api/user_info/get_users_info/?' +
                                        ';'.join(params))
    assert response.status_code == expected_code
    if expected_code == 200:
        data = json.loads(response.content)
        assert len(data) == expected_length


case = helpers.case_getter(
    'uuid uid user_id any_id phone groups show_deleted'
    ' expected_code expected_response',
    groups=['group_other'],
    expected_code=200,
)
case_can_delete = case.partial(groups=['group_deleter'], show_deleted=True)
case_can_view = case_can_delete.partial(groups=['group_can_view_deleted'])
NOT_FOUND = {
    'code': 'not_found',
    'message': 'Not found',
    'status': 'error',
}
USERS_NOT_FOUND = {
    'code': 'not_found',
    'message': 'users not found',
    'status': 'error',
}
NOT_EXPECTED = {
    'code': 'general',
    'message': 'Forbidden',
    'status': 'error',
    'details': {
        'groups': [
            u'Группа с правом удаления',
            u'Группа с правом просмотра удалённых',
        ],
        'permissions': [
            'view_deleted_users',
        ],
    }
}
USERS = []

for x in range(6):
    _user = {
        'user_id': 'user_id_{}'.format(x),
        'yandex_uid': 'yandex_uid_{}'.format(x),
        'yandex_uuid': 'uuid_000{}_enlarged_to_32_symbols'.format(x),
        'phone': 'phone_number_{}'.format(x),
        'user_phone_id': '5c1122bfcb688c63c949f55{}'.format(x),
    }
    if x in {2, 5}:
        _user['phone_type'] = 'uber'
        _user['uber_id'] = 'uber_id_{}'.format(x)
    else:
        _user['phone_type'] = 'yandex'
    if x > 2:
        _user['is_phone_deleted'] = True
        del _user['phone_type']
        del _user['phone']
    USERS.append(_user)

DELETABLE_USERS = [
    dict(phone_can_be_deleted=True, **user)
    for user in USERS[:3]
]


@pytest.mark.parametrize(
    case.params,
    [
        # no permission gives 403
        case(
            uuid='uuid_0000_enlarged_to_32_symbols',
            groups=['some_group_that_cannot_see_this'],
            expected_code=403,
        ),
        # using show_deleted without access gives 400
        case(
            phone='uuid_0000_enlarged_to_32_symbols',
            groups=['group_can_search_phone'],
            show_deleted=True,
            expected_code=403,
            expected_response=NOT_EXPECTED,
        ),
        # wrong identifier gives 404
        case(
            user_id='wrong_user_id',
            groups=['group_other'],
            expected_code=404,
            expected_response=USERS_NOT_FOUND,
        ),
        case(
            phone='wrong_phone_number',
            groups=['group_can_search_phone'],
            expected_code=404,
            expected_response=NOT_FOUND
        ),
        # ------------------------
        # SEARCH NON-DELETED USERS
        # ------------------------
        # searches by uuid/uid/user_id
        case(
            uuid='uuid_0000_enlarged_to_32_symbols',
            expected_response=[USERS[0]]
        ),
        case(
            uid='yandex_uid_0',
            expected_response=[USERS[0]]
        ),
        case(
            user_id='user_id_0',
            expected_response=[USERS[0]]
        ),
        # searching by phones requires specific permission
        case(
            phone='phone_number_1',
            expected_code=403,
        ),
        # searching by phone gives non-deleted user only
        case(
            phone='phone_number_1',
            groups=['group_can_search_phone'],
            expected_code=200,
            expected_response=[USERS[1]]
        ),
        # search by any_id
        case(
            any_id='uber_id_2',
            expected_response=[USERS[2]]
        ),
        # --------------------
        # SEARCH DELETED USERS HAVING NO ACCESS TO THEM
        # --------------------
        # searches by uuid/uid/user_id
        case(
            uuid='uuid_0003_enlarged_to_32_symbols',
            expected_code=404,
            expected_response=USERS_NOT_FOUND,
        ),
        case(
            uid='yandex_uid_3',
            expected_code=404,
            expected_response=USERS_NOT_FOUND,
        ),
        case(
            user_id='user_id_3',
            expected_code=404,
            expected_response=USERS_NOT_FOUND,
        ),
        # search by any_id
        case(
            any_id='uber_id_5',
            expected_code=404,
            expected_response=USERS_NOT_FOUND,
        ),
        # --------------------
        # SEARCH DELETED USERS WITH VIEW ACCESS
        # --------------------
        # searches by uuid/uid/user_id
        case_can_view(
            uuid='uuid_0003_enlarged_to_32_symbols',
            expected_response=[USERS[3]]
        ),
        case_can_view(
            uid='yandex_uid_3',
            expected_response=[USERS[3]]
        ),
        case_can_view(
            user_id='user_id_3',
            expected_response=[USERS[3]]
        ),
        # without show_deleted no user is returned
        case_can_view(
            user_id='user_id_3',
            show_deleted=False,
            expected_code=404,
            expected_response=USERS_NOT_FOUND,
        ),
        # searching by phone gives both deleted and non-deleted users
        # if show_deleted is provided
        case(
            phone='phone_number_1',
            groups=['group_can_search_phone', 'group_can_view_deleted'],
            show_deleted=True,
            expected_response=[USERS[1], USERS[4]]
        ),
        # otherwise non-deleted only
        case(
            phone='phone_number_1',
            groups=['group_can_search_phone', 'group_can_view_deleted'],
            expected_response=[USERS[1]]
        ),
        # search by any_id
        case_can_view(
            any_id='uber_id_5',
            expected_response=[USERS[5]]
        ),
        # --------------------
        # SEARCH DELETED USERS WITH DELETE ACCESS
        # --------------------
        # searches by uuid/uid/user_id
        case_can_delete(
            uuid='uuid_0000_enlarged_to_32_symbols',
            expected_response=[DELETABLE_USERS[0]]
        ),
        case_can_delete(
            uid='yandex_uid_0',
            expected_response=[DELETABLE_USERS[0]]
        ),
        case_can_delete(
            user_id='user_id_0',
            expected_response=[DELETABLE_USERS[0]]
        ),
        # deleted users are not deletable
        case_can_delete(
            uuid='uuid_0003_enlarged_to_32_symbols',
            expected_response=[USERS[3]]
        ),
        case_can_delete(
            uid='yandex_uid_3',
            expected_response=[USERS[3]]
        ),
        case_can_delete(
            user_id='user_id_3',
            expected_response=[USERS[3]]
        ),
        # undeleted user is deletable, while deleted is not
        case(
            phone='phone_number_1',
            groups=['group_can_search_phone', 'group_deleter'],
            show_deleted=True,
            expected_response=[DELETABLE_USERS[1], USERS[4]]
        ),
        # yet without show_deleted there's no deleted user in response
        case(
            phone='phone_number_1',
            groups=['group_can_search_phone', 'group_deleter'],
            expected_response=[DELETABLE_USERS[1]]
        ),
        # search by any_id
        case_can_delete(
            any_id='uber_id_2',
            expected_response=[DELETABLE_USERS[2]]
        ),
        case_can_delete(
            any_id='uber_id_5',
            expected_response=[USERS[5]]
        ),
    ]
)
@pytest.mark.filldb(
    users='check_deleted',
    user_phones='check_deleted',
)
@pytest.mark.asyncenv('blocking')
def test_get_deleted_user_info(uuid, uid, user_id, any_id, phone, groups,
                               show_deleted,
                               expected_code, expected_response):
    params = []
    if uuid is not None:
        params.append('yandex_uuid={}'.format(uuid))
    if uid is not None:
        params.append('yandex_uid={}'.format(uid))
    if user_id is not None:
        params.append('user_id={}'.format(user_id))
    if any_id is not None:
        params.append('any_id={}'.format(any_id))
    if phone is not None:
        params.append('phone={}'.format(phone))
    if show_deleted:
        params.append('show_deleted=true')
    uri = '/api/user_info/get_users_info/?' + ';'.join(params)
    request = helpers.TaxiAdminRequest(groups=groups).get(uri)
    response = api_views_user_info.get_users_info(request)

    data = json.loads(response.content)
    status_code = response.status_code
    if expected_response is None:
        assert status_code == expected_code
    else:
        assert (status_code, data) == (expected_code, expected_response)
