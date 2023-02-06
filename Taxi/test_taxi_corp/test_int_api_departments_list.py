import pytest

from taxi_corp.api import routes
from taxi_corp.util import hdrs


@pytest.mark.parametrize(
    [
        'passport_mock',
        'performer_department_id',
        'query_params',
        'expected_response',
    ],
    [
        pytest.param(
            'client3',
            'dep1',
            {'limit': '1', 'offset': '0'},
            {
                'limit': 1,
                'offset': 0,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'dep1',
                        'limits': {
                            'eats2': {'budget': 100},
                            'tanker': {'budget': None},
                            'taxi': {'budget': 200},
                        },
                        'name': 'department 1',
                        'parent_id': None,
                    },
                ],
            },
            id='test general',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_departments_list(
        taxi_corp_real_auth_client,
        passport_mock,
        performer_department_id,
        mock_corp_users,
        query_params,
        expected_response,
):
    mock_corp_users.data.int_api_departments_list_response = expected_response

    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/departments/list', params=query_params,
    )
    response_data = await response.json()
    assert response_data == expected_response

    mock_request = mock_corp_users.int_api_departments_list.next_call()

    assert mock_request['request'].query == dict(query_params)
    assert (
        mock_request['request'].headers[hdrs.X_YATAXI_CORP_ACL_CLIENT_ID]
        == passport_mock
    )
    assert (
        mock_request['request'].headers[hdrs.X_YATAXI_CORP_ACL_DEPARTMENT_ID]
        == performer_department_id
    )
