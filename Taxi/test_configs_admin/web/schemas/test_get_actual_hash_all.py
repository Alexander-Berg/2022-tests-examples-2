from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest


class Case(NamedTuple):
    expected_response: List[Dict]
    headers: Dict = {}
    params: Optional[Dict] = None
    response_code: int = 200

    @classmethod
    def get_args(cls) -> str:
        return ','.join(cls.__annotations__.keys())  # pylint: disable=E1101


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    Case.get_args(),
    [
        pytest.param(
            *Case(
                expected_response=[
                    {
                        'group': 'CONFIG_SCHEMAS_META_ID',
                        'commit': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
                    },
                    {
                        'group': 'schemas',
                        'commit': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
                    },
                    {
                        'group': 'schemas_2',
                        'commit': '9055f4b5ab6ed0ab805804d8b5ce277903492c54',
                    },
                ],
            ),
            id='all_schemas',
        ),
        pytest.param(
            *Case(
                params={'limit': 2},
                expected_response=[
                    {
                        'group': 'CONFIG_SCHEMAS_META_ID',
                        'commit': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
                    },
                    {
                        'group': 'schemas',
                        'commit': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
                    },
                ],
            ),
            id='limit_schemas',
        ),
        pytest.param(
            *Case(
                params={'last_group': 'CONFIG_SCHEMAS_META_ID'},
                expected_response=[
                    {
                        'group': 'schemas',
                        'commit': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
                    },
                    {
                        'group': 'schemas_2',
                        'commit': '9055f4b5ab6ed0ab805804d8b5ce277903492c54',
                    },
                ],
            ),
            id='start_with_schemas',
        ),
        pytest.param(
            *Case(
                params={'last_group': 'CONFIG_SCHEMAS_META_ID', 'limit': 1},
                expected_response=[
                    {
                        'group': 'schemas',
                        'commit': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
                    },
                ],
            ),
            id='paginated_schemas',
        ),
        pytest.param(
            *Case(
                params={'last_group': 'schemas_2', 'limit': 1},
                expected_response=[],
            ),
            id='empty_paginated_schemas',
        ),
    ],
)
async def test(
        web_app_client,
        patcher_tvm_ticket_check,
        headers,
        params,
        response_code,
        expected_response,
):
    patcher_tvm_ticket_check('configs-admin')
    response = await web_app_client.get(
        '/v1/schemas/actual_commit/all/', headers=headers, params=params or {},
    )

    assert response.status == response_code
    assert await response.json() == expected_response, await response.text()
