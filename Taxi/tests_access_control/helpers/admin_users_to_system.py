import dataclasses
import typing

from tests_access_control.helpers import common


@dataclasses.dataclass
class AddUserToSystemRequest:
    system: str
    provider: str
    provider_user_id: str
    groups: list

    def get_query_params(self):
        return {'system': self.system}

    def get_body(self):
        return {
            'provider': self.provider,
            'provider_user_id': self.provider_user_id,
            'groups': self.groups,
        }


@dataclasses.dataclass
class AddUserToSystemTestCase:
    id_for_pytest: str
    add_user_to_system_request: AddUserToSystemRequest
    expected_response: dict

    @staticmethod
    def get_id_for_pytest(add_user_to_system_test_case):
        return add_user_to_system_test_case.id_for_pytest


async def add_user_to_system(
        taxi_access_control,
        add_user_to_system_request: AddUserToSystemRequest,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/users/add-to-system/',
        add_user_to_system_request.get_body(),
        expected_status_code,
        params=add_user_to_system_request.get_query_params(),
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json


@dataclasses.dataclass
class User:
    provider: str
    provider_user_id: str

    def get_body(self):
        return {
            'provider': self.provider,
            'provider_user_id': self.provider_user_id,
        }


@dataclasses.dataclass
class AddUsersToSystemRequest:
    system: str
    users: typing.List[User]
    groups: list

    @staticmethod
    def get_id_for_pytest(add_user_to_system_test_case):
        return add_user_to_system_test_case.id_for_pytest

    def get_query_params(self):
        return {'system': self.system}

    def get_body(self):
        return {
            'users': [user.get_body() for user in self.users],
            'groups': self.groups,
        }


@dataclasses.dataclass
class AddUsersToSystemTestCase:
    id_for_pytest: str
    add_users_to_system_request: AddUsersToSystemRequest
    expected_response: dict

    @staticmethod
    def get_id_for_pytest(add_users_to_system_test_case):
        return add_users_to_system_test_case.id_for_pytest


async def add_users_to_system(
        taxi_access_control,
        add_users_to_system_request: AddUsersToSystemRequest,
        *,
        expected_status_code,
        expected_response_json,
):
    url = '/v1/admin/users/bulk-add-to-system/'
    response_json = await common.post(
        taxi_access_control,
        url,
        add_users_to_system_request.get_body(),
        expected_status_code,
        params=add_users_to_system_request.get_query_params(),
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json
