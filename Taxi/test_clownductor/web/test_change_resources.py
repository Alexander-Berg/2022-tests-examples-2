import pytest


@pytest.mark.parametrize(
    'branch_id, tickets, parameters, exp_status, expected_data',
    [
        (
            5,
            'TAXIREL-2',
            [{'name': 'cpu', 'value': 1}],
            200,
            {
                'data': {
                    'parameters': [{'name': 'cpu', 'value': 1}],
                    'branch_id': 5,
                },
                'change_doc_id': '3_5_ChangeResourcesNannyService',
            },
        ),
        (
            5,
            None,
            [{'name': 'cpu', 'value': 1}],
            200,
            {
                'data': {
                    'branch_id': 5,
                    'parameters': [{'name': 'cpu', 'value': 1}],
                },
                'tickets': {
                    'create_data': {
                        'summary': '',
                        'description': '',
                        'components': [74933],
                        'ticket_queue': 'TAXIADMIN',
                    },
                },
                'change_doc_id': '3_5_ChangeResourcesNannyService',
            },
        ),
        (
            1,
            'TAXIREL-2',
            [{'name': 'cpu', 'value': 1}],
            400,
            'WRONG_SERVICE_TYPE',
        ),
        (2, 'TAXIREL-2', [{'name': 'cpu', 'value': 1}], 404, 'NOT_FOUND_URL'),
        (
            3,
            'TAXIREL-2',
            [{'name': 'cpu', 'value': 1}],
            400,
            'CUSTOM_ENV_ONLY',
        ),
        (
            5,
            'TAXIREL-2',
            [{'name': 'CPU', 'value': 1}],
            400,
            'VALIDATION_ERROR',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'diff_validation': True})
async def test_change_resources_check(
        web_app_client,
        branch_id,
        tickets,
        parameters,
        exp_status,
        expected_data,
):
    headers = {'X-Yandex-Login': 'robot'}
    if tickets:
        headers['X-YaTaxi-Draft-Tickets'] = tickets
    body = {'branch_id': branch_id, 'parameters': parameters}
    response = await web_app_client.post(
        'v1/services/change_resources/validate/', headers=headers, json=body,
    )
    assert response.status == exp_status
    response_data = await response.json()
    if response.status == 200:
        assert response_data == expected_data
    else:
        assert response_data['code'] == expected_data


@pytest.mark.parametrize(
    'branch_id, tickets, parameters, exp_status, expected_data',
    [(5, 'TAXIREL-2', [{'name': 'cpu', 'value': 1}], 200, {'job_id': 4})],
)
@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'diff_validation': True})
async def test_change_resources(
        web_app_client,
        branch_id,
        tickets,
        parameters,
        exp_status,
        expected_data,
):
    headers = {
        'X-Yandex-Login': 'robot',
        'X-YaTaxi-Draft-Approvals': 'deoevgen',
    }
    if tickets:
        headers['X-YaTaxi-Draft-Tickets'] = tickets
    body = {'branch_id': branch_id, 'parameters': parameters}
    response = await web_app_client.post(
        'v1/services/change_resources/', headers=headers, json=body,
    )
    assert response.status == exp_status
    response_data = await response.json()
    if response.status == 200:
        assert response_data == expected_data
    else:
        assert response_data['code'] == expected_data
