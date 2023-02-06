async def test_list(taxi_form_builder_web):
    response = await taxi_form_builder_web.get(
        '/v1/async-validators/builder/list/',
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'async_validators': [{'id': 'sms_validator', 'name': 'sms_validator'}],
    }
