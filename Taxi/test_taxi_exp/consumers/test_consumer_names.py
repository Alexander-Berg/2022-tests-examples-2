import pytest


@pytest.mark.parametrize(
    'name,expected_status',
    [
        ('name with spaces', 400),
        ('русские_имена', 400),
        ('names_with,', 400),
        ('true_consumer_name', 200),
        ('some/more/part/consumer_name', 200),
        ('another/true_consumer_name', 200),
        ('another/with-dash/true_consumer_name', 200),
        ('another/with.point/true_consumer_name', 200),
    ],
)
async def test_consumer_names(name, expected_status, taxi_exp_client):
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': name, 'service': 'service_name'},
    )
    assert response.status == expected_status
