from .plugins import configs


async def test_response(taxi_grocery_cibus):
    response = await taxi_grocery_cibus.get(
        '/cibus/integration/v1/finish', json={}, headers={},
    )

    assert response.status_code == 200
    assert response.text == configs.FINISH_FORM
