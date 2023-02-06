import dataclasses
import typing

from tests_access_control.helpers import common


@dataclasses.dataclass
class CreateUserRequest:
    provider: str
    provider_user_id: str

    def get_body(self):
        return {
            'provider': self.provider,
            'provider_user_id': self.provider_user_id,
        }


@dataclasses.dataclass
class CreateUserTestCase:
    id_for_pytest: str
    create_user_request: CreateUserRequest
    expected_status_code: int
    expected_response: dict

    @staticmethod
    def get_id_for_pytest(create_user_test_case):
        return create_user_test_case.id_for_pytest


@dataclasses.dataclass
class BulkCreateUsersTestCase:
    id_for_pytest: str
    bulk_create_users_request: typing.List[CreateUserRequest]
    expected_status_code: int
    expected_response: dict

    @staticmethod
    def get_id_for_pytest(bulk_create_users_test_case):
        return bulk_create_users_test_case.id_for_pytest


async def create_user(
        taxi_access_control,
        create_user_request: CreateUserRequest,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/users/create/',
        create_user_request.get_body(),
        expected_status_code,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json


async def bulk_create_users(
        taxi_access_control,
        bulk_create_users_request: typing.List[CreateUserRequest],
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/users/bulk-create/',
        {'users': [user.get_body() for user in bulk_create_users_request]},
        expected_status_code,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json
