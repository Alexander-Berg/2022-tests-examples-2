async def test_v1_categories_types_response(taxi_billing_commissions):
    response = await taxi_billing_commissions.get('v1/categories/types')
    assert response.status_code == 200, response.json()
    assert response.json() == {
        'types': [
            {'id': 'absolute', 'name': 'Абсолют'},
            {'id': 'call_center', 'name': 'Комиссия за КЦ'},
            {'id': 'core', 'name': 'Процент'},
            {'id': 'fine', 'name': 'Штраф'},
            {'id': 'hiring', 'name': 'Процент (наём)'},
            {'id': 'software_subscription', 'name': 'Подписка на ПО'},
        ],
    }
