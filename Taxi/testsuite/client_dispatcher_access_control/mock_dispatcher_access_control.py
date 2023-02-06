# pylint: disable=attribute-defined-outside-init,invalid-name

"""
Mocks for dispatcher-access-control.
"""

import json

import aiohttp
import pytest


class DispatcherAccessControlContext:
    def __init__(self, load_json):
        try:
            self.parks = load_json('dispatcher_access_control_parks.json')
        except FileNotFoundError:
            self.parks = []
        try:
            self.permissions = load_json(
                'dispatcher_access_control_permissions.json',
            )
        except FileNotFoundError:
            self.permissions = []
        try:
            self.users = load_json('dispatcher_access_control_users.json')
        except FileNotFoundError:
            self.users = []
        self.parks_users_list = None
        self.users_parks_list = None
        self.is_error = False
        self.http_code = None
        self.error_code = None
        self.message = None

    def set_parks(self, parks):
        self.parks = parks

    def set_permissions(self, permissions):
        self.permissions = permissions

    def set_users(self, users):
        self.users = users

    def set_error(self, http_code, error_code, message):
        self.is_error = True
        self.http_code = http_code
        self.error_code = error_code
        self.message = message

    def reset_error(self):
        self.is_error = False


@pytest.fixture
def dispatcher_access_control(mockserver, load_json):
    context = DispatcherAccessControlContext(load_json)

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def mock_v1_parks_users_list(request):
        if context.is_error:
            return aiohttp.web.json_response(
                status=context.http_code,
                data={'code': context.error_code, 'message': 'error'},
            )

        park_id = json.loads(request.get_data())['query']['park']['id']
        return {
            'users': [{**user, 'park_id': park_id} for user in context.users],
        }

    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/users/permissions/list',
    )
    def mock_v1_parks_users_permissions_list(request):
        if context.is_error:
            return aiohttp.web.json_response(
                status=context.http_code,
                data={'code': context.error_code, 'message': 'error'},
            )

        return {'permissions': context.permissions}

    @mockserver.json_handler('/dispatcher-access-control/v1/users/parks/list')
    def mock_v1_users_parks_list(request):
        if context.is_error:
            return aiohttp.web.json_response(
                status=context.http_code,
                data={'code': context.error_code, 'message': 'error'},
            )

        return {'parks': context.parks}

    context.parks_users_list = mock_v1_parks_users_list
    context.parks_users_permissions_list = mock_v1_parks_users_permissions_list
    context.users_parks_list = mock_v1_users_parks_list
    return context
