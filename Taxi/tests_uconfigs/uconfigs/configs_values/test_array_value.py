CONFIGS_VALUES_URL = 'configs/values'


async def test_array_value(taxi_uconfigs, config_schemas):
    config_schemas.defaults.answer = {
        'commit': 'hash',
        'defaults': {'BILLING_FISCAL_RECEIPT_COUNTRIES': ['rus']},
    }
    await taxi_uconfigs.invalidate_caches()

    response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json={})
    assert response.headers['Content-Type'] == 'application/json'
    assert response.status_code == 200
    assert isinstance(
        response.json()['configs']['BILLING_FISCAL_RECEIPT_COUNTRIES'], list,
    )
