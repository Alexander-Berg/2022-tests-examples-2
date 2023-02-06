import dataclasses
import json
import typing

import pytest


@dataclasses.dataclass
class GetLocksTestCase:
    result_locks: typing.List[typing.Tuple]
    limit: typing.Optional[int] = None
    offset: typing.Optional[int] = None
    search_draft_id: typing.Optional[int] = None
    search_lock_id: typing.Optional[str] = None

    @property
    def request_data(self):
        data = {}
        for field, value in (
                ('limit', self.limit),
                ('offset', self.offset),
                ('draft_id', self.search_draft_id),
                ('lock_id', self.search_lock_id),
        ):
            if value is not None:
                data[field] = value
        return data

    @property
    def response_data(self):
        items = [
            {
                'draft_id': draft_id,
                'service_name': service_name,
                'api_path': api_path,
                'lock_id': lock_id,
            }
            for draft_id, lock_id, api_path, service_name in self.result_locks
        ]
        return {'items': items}


@pytest.mark.parametrize(
    'case',
    [
        GetLocksTestCase(
            limit=10,
            offset=0,
            result_locks=[
                (
                    1,
                    'test_service:test_api:lock_id_1',
                    'test_api',
                    'test_service',
                ),
                (
                    1,
                    'test_service:test_api:lock_id_2',
                    'test_api',
                    'test_service',
                ),
                (
                    2,
                    'test_service:test_api2:lock_id_1',
                    'test_api2',
                    'test_service',
                ),
                (
                    2,
                    'test_service:test_api2:lock_id_3',
                    'test_api2',
                    'test_service',
                ),
            ],
        ),
        GetLocksTestCase(
            search_lock_id='id_1',
            result_locks=[
                (
                    1,
                    'test_service:test_api:lock_id_1',
                    'test_api',
                    'test_service',
                ),
                (
                    2,
                    'test_service:test_api2:lock_id_1',
                    'test_api2',
                    'test_service',
                ),
            ],
        ),
        GetLocksTestCase(
            search_draft_id=1,
            result_locks=[
                (
                    1,
                    'test_service:test_api:lock_id_1',
                    'test_api',
                    'test_service',
                ),
                (
                    1,
                    'test_service:test_api:lock_id_2',
                    'test_api',
                    'test_service',
                ),
            ],
        ),
        GetLocksTestCase(
            limit=10,
            offset=0,
            search_draft_id=1,
            search_lock_id='id_1',
            result_locks=[
                (
                    1,
                    'test_service:test_api:lock_id_1',
                    'test_api',
                    'test_service',
                ),
            ],
        ),
        GetLocksTestCase(
            search_draft_id=1, search_lock_id='id_3', result_locks=[],
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_get_locks(taxi_approvals_client, case):
    response = await taxi_approvals_client.post(
        f'/drafts/locks/',
        data=json.dumps(case.request_data),
        headers={'X-Yandex-Login': 'test_user'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == case.response_data
