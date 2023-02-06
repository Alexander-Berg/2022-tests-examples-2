# -*- coding: utf-8 -*-
import json

from django import test as django_test
import pytest
from taxi.conf import settings

from taxi.core import async
from taxiadmin.api import apiutils
from taxiadmin.views import common
from taxiadmin import admin_permissions


@pytest.mark.parametrize(
    'is_superuser', [False, True]
)
@pytest.mark.parametrize(
    'has_require_ticket_validation_permission', [False, True]
)
@pytest.mark.parametrize(
    'valid_chatterbox_id', [False, True]
)
@pytest.mark.parametrize(
    'valid_meta_info', [False, True]
)
@pytest.mark.config(ADMIN_CHECK_CHATTERBOX_TICKET_ENABLED=True)
@pytest.inline_callbacks
def test_check_chatterbox_ticket_enabled(areq_request, patch,
                                         is_superuser, has_require_ticket_validation_permission,
                                         valid_chatterbox_id, valid_meta_info):
    @patch('taxi.external.passport.get_yateam_info_by_sid')
    @async.inline_callbacks
    def get_yateam_info_by_sid(*args, **kwargs):
        yield async.return_value({'user_ticket': ''})

    chatterbox_id = 42
    meta_info = {'field': 'value'}

    @areq_request
    def requests_request(method, url, **kwargs):
        assert kwargs['json']['chatterbox_id'] == chatterbox_id
        assert kwargs['json']['meta_info'] == meta_info
        assert method == 'POST'
        assert url.startswith(settings.CHATTERBOX_API_URL)

        return areq_request.response(200, body=json.dumps({
            'access_status': apiutils.USER_DATA_PERMITTED if valid_chatterbox_id and valid_meta_info else ''
        }))

    request = django_test.RequestFactory().request()
    request.superuser = is_superuser
    request.groups = []
    request.permissions = {}
    request.remote_addr = '127.0.0.1'
    request.uid = 0

    if has_require_ticket_validation_permission:
        request.permissions[admin_permissions.require_ticket_validation] = {'mode': 'unrestricted'}

    result = yield common.check_chatterbox_ticket(
        request, chatterbox_id, meta_info
    )

    if is_superuser or not has_require_ticket_validation_permission:
        expected_result = True
    else:
        expected_result = valid_chatterbox_id and valid_meta_info

    assert result == expected_result


@pytest.inline_callbacks
def test_check_chatterbox_ticket_disabled(areq_request, patch):
    @patch('taxi.external.passport.get_yateam_info_by_sid')
    @async.inline_callbacks
    def get_yateam_info_by_sid(*args, **kwargs):
        assert False

    @areq_request
    def requests_request(*args, **kwargs):
        assert False

    request = django_test.RequestFactory().request()
    request.superuser = True
    result = yield common.check_chatterbox_ticket(
        request, 'any_id', 'any meta'
    )

    assert result
