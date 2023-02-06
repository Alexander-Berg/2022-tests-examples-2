import pytest

from taxi_corp.api import routes
from taxi_corp.util import hdrs


@pytest.mark.parametrize(
    ['passport_mock', 'query_params', 'expected_response'],
    [
        pytest.param(
            'client1',
            {'limit': '1', 'offset': '0'},
            {
                'limit': 1,
                'offset': 0,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'cc_options_id_2',
                        'default': False,
                        'field_settings': [
                            {
                                'format': 'mixed',
                                'id': 'cost_center',
                                'required': True,
                                'services': ['eats', 'taxi', 'drive'],
                                'title': 'Центр затрат',
                                'values': [
                                    'запасная командировка',
                                    'из центрального офиса',
                                ],
                            },
                        ],
                        'name': 'Запасной',
                    },
                ],
            },
            id='test general',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_cost_centers_list(
        taxi_corp_real_auth_client,
        passport_mock,
        mock_corp_users,
        query_params,
        expected_response,
):
    mock_corp_users.data.int_api_cost_centers_list_response = expected_response

    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/cost_centers/list', params=query_params,
    )
    response_data = await response.json()
    assert response_data == expected_response

    mock_request = mock_corp_users.int_api_cost_centers_list.next_call()

    assert mock_request['request'].query == dict(query_params)
    assert (
        mock_request['request'].headers[hdrs.X_YATAXI_CORP_ACL_CLIENT_ID]
        == passport_mock
    )
