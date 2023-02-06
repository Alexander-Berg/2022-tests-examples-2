import pytest

TRANSLATIONS = {
    'fuel.a80': {'ru': 'АИ-80'},
    'fuel.a92': {'ru': 'АИ-92'},
    'fuel.a95': {'ru': 'АИ-95'},
    'fuel.a98': {'ru': 'АИ-98'},
    'fuel.a100': {'ru': 'АИ-100'},
    'fuel.diesel': {'ru': 'ДТ'},
    'fuel.diesel_winter': {'ru': 'ДТ Зимний'},
    'fuel.diesel_demiseason': {'ru': 'ДТ Межсезонный'},
    'fuel.propane': {'ru': 'ПРОПАН'},
    'fuel.metan': {'ru': 'МЕТАН'},
    'fuel.icefree': {'ru': 'Омывайка'},
    'fuel.a92_premium': {'ru': 'АИ-92 Премиум'},
    'fuel.a95_premium': {'ru': 'АИ-95 Премиум'},
    'fuel.a98_premium': {'ru': 'АИ-98 Премиум'},
    'fuel.a100_premium': {'ru': 'АИ-100 Премиум'},
    'fuel.diesel_premium': {'ru': 'ДТ Премиум'},
}


@pytest.mark.translations(corp=TRANSLATIONS)
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_fuel_types(taxi_corp_real_auth_client, passport_mock):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/fuel-types',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {
        'fuel_types': [
            {'type_id': 'a80', 'name': 'АИ-80'},
            {'type_id': 'a92', 'name': 'АИ-92'},
            {'type_id': 'a95', 'name': 'АИ-95'},
            {'type_id': 'a98', 'name': 'АИ-98'},
            {'type_id': 'a100', 'name': 'АИ-100'},
            {'type_id': 'diesel', 'name': 'ДТ'},
            {'type_id': 'diesel_winter', 'name': 'ДТ Зимний'},
            {'type_id': 'diesel_demiseason', 'name': 'ДТ Межсезонный'},
            {'type_id': 'propane', 'name': 'ПРОПАН'},
            {'type_id': 'metan', 'name': 'МЕТАН'},
            {'type_id': 'icefree', 'name': 'Омывайка'},
            {'type_id': 'a92_premium', 'name': 'АИ-92 Премиум'},
            {'type_id': 'a95_premium', 'name': 'АИ-95 Премиум'},
            {'type_id': 'a98_premium', 'name': 'АИ-98 Премиум'},
            {'type_id': 'a100_premium', 'name': 'АИ-100 Премиум'},
            {'type_id': 'diesel_premium', 'name': 'ДТ Премиум'},
        ],
    }
