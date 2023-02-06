import pytest


@pytest.mark.parametrize(
    ['request_params', 'expected_result'],
    [
        (
            {'status': ['accepted']},
            {
                'items': [
                    {
                        'id': 'request_accepted',
                        'created': '2000-01-01T03:00:00+03:00',
                        'status': 'accepted',
                        'service': 'taxi',
                        'enterprise_name_short': 'r1_enterprise_name_short',
                        'company_tin': '500100732259',
                        'client_login': 'small_yandex_login',
                        'client_id': 'r1_client_id',
                        'manager_login': 'r1_manager_login',
                        'contract_type': 'postpaid',
                        'final_status_date': '2000-01-01T03:00:00+03:00',
                        'final_status_manager_login': (
                            'r1_final_status_manager_login'
                        ),
                    },
                ],
                'total': 1,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
        (
            {'status': ['accepted', 'pending']},
            {
                'items': [
                    {
                        'id': 'request_pending',
                        'created': '2000-01-02T03:00:00+03:00',
                        'status': 'pending',
                        'country': 'rus',
                        'service': 'cargo',
                        'enterprise_name_short': 'r2_4',
                        'company_tin': '1503009020',
                        'manager_login': 'r2_1',
                        'contract_type': 'prepaid',
                    },
                    {
                        'id': 'request_accepted',
                        'created': '2000-01-01T03:00:00+03:00',
                        'status': 'accepted',
                        'service': 'taxi',
                        'enterprise_name_short': 'r1_enterprise_name_short',
                        'company_tin': '500100732259',
                        'client_login': 'small_yandex_login',
                        'client_id': 'r1_client_id',
                        'manager_login': 'r1_manager_login',
                        'contract_type': 'postpaid',
                        'final_status_date': '2000-01-01T03:00:00+03:00',
                        'final_status_manager_login': (
                            'r1_final_status_manager_login'
                        ),
                    },
                ],
                'total': 2,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
        (
            {'offset': 20},
            {
                'items': [],
                'total': 4,
                'offset': 20,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
        (
            {'limit': 1},
            {
                'items': [
                    {
                        'id': 'bad_request',
                        'created': '2000-01-04T03:00:00+03:00',
                        'status': 'failed',
                        'service': 'drive',
                        'enterprise_name_short': 'r4_4',
                        'company_tin': '102500352',
                        'manager_login': 'r4_1',
                        'contract_type': 'prepaid',
                    },
                ],
                'total': 4,
                'offset': 0,
                'limit': 1,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
        (
            {'sort': [{'field': 'created', 'direction': 'asc'}]},
            {
                'items': [
                    {
                        'id': 'request_accepted',
                        'created': '2000-01-01T03:00:00+03:00',
                        'status': 'accepted',
                        'service': 'taxi',
                        'enterprise_name_short': 'r1_enterprise_name_short',
                        'company_tin': '500100732259',
                        'client_login': 'small_yandex_login',
                        'client_id': 'r1_client_id',
                        'manager_login': 'r1_manager_login',
                        'contract_type': 'postpaid',
                        'final_status_date': '2000-01-01T03:00:00+03:00',
                        'final_status_manager_login': (
                            'r1_final_status_manager_login'
                        ),
                    },
                    {
                        'id': 'request_pending',
                        'created': '2000-01-02T03:00:00+03:00',
                        'status': 'pending',
                        'country': 'rus',
                        'service': 'cargo',
                        'enterprise_name_short': 'r2_4',
                        'company_tin': '1503009020',
                        'manager_login': 'r2_1',
                        'contract_type': 'prepaid',
                    },
                    {
                        'id': 'request_accepting',
                        'created': '2000-01-03T03:00:00+03:00',
                        'status': 'accepting',
                        'service': 'taxi',
                        'enterprise_name_short': 'r3_4',
                        'company_tin': '102500351',
                        'manager_login': 'r3_1',
                        'contract_type': 'prepaid',
                    },
                    {
                        'id': 'bad_request',
                        'created': '2000-01-04T03:00:00+03:00',
                        'status': 'failed',
                        'service': 'drive',
                        'enterprise_name_short': 'r4_4',
                        'company_tin': '102500352',
                        'manager_login': 'r4_1',
                        'contract_type': 'prepaid',
                    },
                ],
                'total': 4,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'asc'}],
            },
        ),
        (
            {'search': ' 1503009020 '},
            {
                'items': [
                    {
                        'id': 'request_pending',
                        'created': '2000-01-02T03:00:00+03:00',
                        'status': 'pending',
                        'country': 'rus',
                        'service': 'cargo',
                        'enterprise_name_short': 'r2_4',
                        'company_tin': '1503009020',
                        'manager_login': 'r2_1',
                        'contract_type': 'prepaid',
                    },
                ],
                'total': 1,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
                'search': '1503009020',
            },
        ),
        (
            {'search': ' 1503009020 ', 'status': ['accepted']},
            {
                'items': [],
                'total': 0,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
                'search': '1503009020',
            },
        ),
        (
            {'country': ['rus']},
            {
                'items': [
                    {
                        'id': 'request_pending',
                        'created': '2000-01-02T03:00:00+03:00',
                        'status': 'pending',
                        'country': 'rus',
                        'service': 'cargo',
                        'enterprise_name_short': 'r2_4',
                        'company_tin': '1503009020',
                        'manager_login': 'r2_1',
                        'contract_type': 'prepaid',
                    },
                ],
                'total': 1,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
        (
            {'service': ['cargo']},
            {
                'items': [
                    {
                        'id': 'request_pending',
                        'created': '2000-01-02T03:00:00+03:00',
                        'status': 'pending',
                        'country': 'rus',
                        'service': 'cargo',
                        'enterprise_name_short': 'r2_4',
                        'company_tin': '1503009020',
                        'manager_login': 'r2_1',
                        'contract_type': 'prepaid',
                    },
                ],
                'total': 1,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
        (
            {'service': ['cargo', 'drive']},
            {
                'items': [
                    {
                        'id': 'bad_request',
                        'created': '2000-01-04T03:00:00+03:00',
                        'status': 'failed',
                        'service': 'drive',
                        'enterprise_name_short': 'r4_4',
                        'company_tin': '102500352',
                        'manager_login': 'r4_1',
                        'contract_type': 'prepaid',
                    },
                    {
                        'id': 'request_pending',
                        'created': '2000-01-02T03:00:00+03:00',
                        'status': 'pending',
                        'country': 'rus',
                        'service': 'cargo',
                        'enterprise_name_short': 'r2_4',
                        'company_tin': '1503009020',
                        'manager_login': 'r2_1',
                        'contract_type': 'prepaid',
                    },
                ],
                'total': 2,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
        (
            {'updated_since': '2000-01-05T03:00:00+03:00'},
            {
                'items': [
                    {
                        'id': 'bad_request',
                        'created': '2000-01-04T03:00:00+03:00',
                        'status': 'failed',
                        'service': 'drive',
                        'enterprise_name_short': 'r4_4',
                        'company_tin': '102500352',
                        'manager_login': 'r4_1',
                        'contract_type': 'prepaid',
                    },
                ],
                'total': 1,
                'offset': 0,
                'limit': 100,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_manager_requests_search(
        taxi_corp_requests_web, mock_personal, request_params, expected_result,
):
    response = await taxi_corp_requests_web.post(
        '/v1/manager-requests/search', json=request_params,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == expected_result
