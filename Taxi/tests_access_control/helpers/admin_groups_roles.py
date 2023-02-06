import dataclasses
from typing import Optional

from tests_access_control.helpers import common


@dataclasses.dataclass
class BulkGroupsRolesTestCase:
    id_for_pytest: str
    request_json: dict
    expected_status_code: int
    expected_response: dict
    params: Optional[dict] = None

    @staticmethod
    def get_id_for_pytest(test_case):
        return test_case.id_for_pytest


async def bulk_create_groups_roles(
        taxi_access_control,
        request_json,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/groups_roles/bulk-create/',
        request_json,
        expected_status_code,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json


async def bulk_delete_groups_roles(
        taxi_access_control,
        request_json,
        params,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/groups_roles/bulk-delete/',
        request_json,
        expected_status_code,
        params=params,
    )
    assert expected_response_json == response_json, {
        'expected_response_json': expected_response_json,
        'response_json': response_json,
    }
    return response_json
