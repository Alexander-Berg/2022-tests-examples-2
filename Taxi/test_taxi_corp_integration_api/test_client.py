import pytest


@pytest.mark.parametrize(
    'client_id, expected',
    [
        pytest.param(
            'client_id_1',
            {
                'client_id': 'client_id_1',
                'country': 'rus',
                'name': 'Yandex.Uber team',
                'contract_id': '123456/89',
                'billing_client_id': '2000101',
                'billing_contract_id': '654321',
                'services': {
                    'taxi': {
                        'contract_id': '123456/89',
                        'is_active': True,
                        'is_visible': True,
                        'is_test': True,
                        'comment': 'comment',
                        'deactivate_threshold_date': '2030-01-01T00:00:00Z',
                        'deactivate_threshold_ride': 100,
                        'contract_info': {
                            'balance': '500000.00',
                            'contract_id': '654321',
                            'is_blocked': False,
                            'payment_type': 'prepaid',
                        },
                    },
                },
                'without_vat_contract': True,
            },
            id='client_id_1',
        ),
    ],
)
async def test_get_client(web_app_client, client_id, expected):
    response = await web_app_client.get(
        '/v1/client', params={'client_id': client_id},
    )

    data = await response.json()

    assert response.status == 200, data
    assert data == expected


async def test_get_client_400(web_app_client):
    response = await web_app_client.get('/v1/client')
    assert response.status == 400


async def test_get_client_404(web_app_client):
    response = await web_app_client.get(
        '/v1/client', params={'client_id': 'not_found'},
    )

    data = await response.json()

    assert response.status == 404, data
    assert data == {'code': 'NOT_FOUND', 'message': 'Client not found'}
