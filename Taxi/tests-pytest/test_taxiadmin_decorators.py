import pytest

from taxi.core import async

from taxiadmin import decorators, admin_permissions
from taxiadmin.api import apiutils

import helpers


@pytest.mark.config(
    ADMIN_SUPPORT_CHECK_ENABLED=True,
    ADMIN_SUPPORT_CHECK_FIELDS={
        'admin_get_users_info': {
            'fields': [
                'phone',
            ],
            'mapping': {
                'phone': 'user_phone',
            },
        },
    },
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    (
            'params', 'expected_data',
            'chatterbox_permitted', 'expected_code',
    ),
    [
        (
            'phone=%2B79210001234&__chatterbox_id=5f293817931944cbe7ca1234',
            {
                'chatterbox_id': '5f293817931944cbe7ca1234',
                'meta_info': {
                    'user_phone': '+79210001234',
                },
            },
            True,
            200,
        ),
        (
            'phone=%2B79210001234&__chatterbox_id=5f293817931944cbe7ca1234&'
            'extra_field=extra_field',
            {
                'chatterbox_id': '5f293817931944cbe7ca1234',
                'meta_info': {
                    'user_phone': '+79210001234',
                },
            },
            True,
            200,
        ),
        (
            'phone=%2B79210001234&__chatterbox_id=5f293817931944cbe7ca1234',
            {
                'chatterbox_id': '5f293817931944cbe7ca1234',
                'meta_info': {
                    'user_phone': '+79210001234',
                },
            },
            False,
            403,
        ),
    ]
)
@pytest.inline_callbacks
def test_first_line_support_check(
        params, expected_data, chatterbox_permitted, expected_code, patch,
):
    @apiutils.get_request
    @decorators.first_line_support_check('admin_get_users_info')
    @async.inline_callbacks
    def get_users_info(request, data):
        async.return_value(apiutils.json_http_response({}))

    @patch('taxiadmin.permissions.get_user_permissions')
    @async.inline_callbacks
    def get_user_permissions(request):
        permissions = [admin_permissions.chatterbox_first_line_restrictions]
        request.superuser = False
        request.permissions = permissions
        yield async.return_value(permissions)

    @patch('taxi.external.chatterbox.check_data_access')
    @async.inline_callbacks
    def check_data_access(data, *args, **kwargs):
        assert data == expected_data
        if chatterbox_permitted:
            yield async.return_value({'access_status': 'permitted'})
        else:
            yield async.return_value({'access_status': 'forbidden'})

    @patch('taxi.external.passport.get_yateam_info_by_sid')
    @async.inline_callbacks
    def get_yateam_info_by_sid(*args, **kwargs):
        yield async.return_value({
            'uid': 'uid',
            'login': 'login',
            'user_ticket': 'user_ticket',
        })

    uri = '/api/user_info/get_users_info/?' + params
    request = helpers.TaxiAdminRequest(
        groups=['group_can_search_phone']
    ).get(uri)
    request.remote_addr = '127.0.0.1'
    response = yield get_users_info(request)

    status_code = response.status_code
    assert status_code == expected_code
