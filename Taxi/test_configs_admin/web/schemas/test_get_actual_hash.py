from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest


class Case(NamedTuple):
    headers: Dict = {}
    params: Optional[Dict] = None
    response_code: int = 200
    expected_response: Dict = {
        'commit': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
        'group': 'CONFIG_SCHEMAS_META_ID',
    }

    @classmethod
    def get_args(cls) -> str:
        return ','.join(cls.__annotations__.keys())  # pylint: disable=E1101


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    Case.get_args(),
    [
        pytest.param(*Case(), id='without ticket'),
        pytest.param(
            *Case(headers={'X-Ya-Service-Ticket': 'bad_key'}),
            id='with bad ticket',
        ),
        pytest.param(
            *Case(headers={'X-Ya-Service-Ticket': 'good'}),
            id='with good ticket',
        ),
        pytest.param(
            *Case(
                params={'group': 'schemas'},
                expected_response={
                    'commit': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
                    'group': 'schemas',
                },
            ),
            id='get hash for group',
        ),
        pytest.param(
            *Case(
                params={'group': 'unknown_group'},
                expected_response={
                    'message': 'Group `unknown_group` not found',
                    'code': 'GROUP_NOT_FOUND',
                },
                response_code=404,
            ),
            id='404_if_group_not_found',
        ),
    ],
)
async def test_get_actual_commit_hash(
        web_app_client,
        patcher_tvm_ticket_check,
        headers,
        params,
        response_code,
        expected_response,
):
    patcher_tvm_ticket_check('configs-admin')
    response = await web_app_client.get(
        '/v1/schemas/actual_commit/', headers=headers, params=params or {},
    )

    assert response.status == response_code
    assert await response.json() == expected_response
