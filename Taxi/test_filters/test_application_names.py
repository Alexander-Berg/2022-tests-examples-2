import pytest


@pytest.mark.parametrize(
    'name,expected_status',
    [
        ('name with spaces', 400),
        ('русские_имена', 400),
        ('names_with,', 400),
        ('now_ok/app_name', 200),
        ('true_app_name', 200),
    ],
)
async def test_application_names(name, expected_status, taxi_exp_client):
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/applications/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': name},
    )
    assert response.status == expected_status
