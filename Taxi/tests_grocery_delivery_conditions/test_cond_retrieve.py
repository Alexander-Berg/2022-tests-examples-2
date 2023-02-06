import pytest

from . import configs
from .plugins import keys


@pytest.mark.parametrize(
    ['req_body'],
    [
        [{'delivery_conditions_id': '46275fee-e483-4973-a67b-6c09f368201b'}],
        [{'external_id': {'id': 'qwerty', 'type': 'some'}}],
    ],
)
async def test_not_found(taxi_grocery_delivery_conditions, req_body):
    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/retrieve', json=req_body,
    )
    assert response.status_code == 404


@configs.EXP3_CALC_SETTINGS
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
@pytest.mark.parametrize(
    ['external_id'], [[{'id': 'qwerty', 'type': 'some'}], [None]],
)
async def test_dummy(taxi_grocery_delivery_conditions, external_id):
    req = {'position': keys.DEFAULT_DEPOT_LOCATION, 'meta': {}}
    if external_id is not None:
        req['external_id'] = external_id
    response1 = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create', json=req,
    )
    assert response1.status_code == 200

    response2 = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/retrieve',
        json={
            'delivery_conditions_id': response1.json()[
                'delivery_conditions_id'
            ],
        },
    )
    assert response2.status_code == 200
    assert response2.json() == response1.json()

    if external_id is not None:
        response2 = await taxi_grocery_delivery_conditions.post(
            '/internal/v1/grocery-delivery-conditions/v1/retrieve',
            json={'external_id': external_id},
        )
        assert response2.status_code == 200
        assert response2.json() == response1.json()
