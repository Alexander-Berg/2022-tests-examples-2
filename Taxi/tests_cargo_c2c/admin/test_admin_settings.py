async def test_admin_settings(taxi_cargo_c2c):
    response = await taxi_cargo_c2c.get(
        '/v1/admin/delivery/settings', headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'enums': {
            'order_provider_id': [
                {'value': 'cargo-claims'},
                {'value': 'cargo-c2c'},
                {'value': 'logistic-platform'},
                {'value': 'logistic-platform-c2c'},
                {'value': 'taxi'},
            ],
        },
    }
