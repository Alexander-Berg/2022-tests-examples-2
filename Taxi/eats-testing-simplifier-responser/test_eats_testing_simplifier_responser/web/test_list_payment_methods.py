async def test_get_payment_methods_from_config(
        taxi_eats_testing_simplifier_responser_web,
):
    response = await taxi_eats_testing_simplifier_responser_web.get(
        path='/payment-methods',
    )
    assert response.status == 200, 'Response code should be 200'
    assert await response.json() == {
        'default_payment_methods': [
            {
                'id': 'card-x8e000cd57550021906e9ee43',
                'type': 'card',
                'title': 'VISA',
            },
            {
                'id': 'card-x8e000cd57550021906e9ee43',
                'type': 'card',
                'title': 'MasterCard',
            },
            {'id': 'applepay', 'type': 'applepay', 'title': 'applepay'},
            {'id': 'googlepay', 'type': 'googlepay', 'title': 'googlepay'},
            {
                'id': 'add_new_card',
                'type': 'add_new_card',
                'title': 'add_new_card',
            },
            {'id': 'cash', 'type': 'cash', 'title': 'cash'},
            {'id': 'cash', 'type': 'sbp', 'title': 'sbp'},
            {
                'id': 'corp:7c3a629872d944d8b7fad154aff37b14:RUB',
                'type': 'corp',
                'title': 'Кабинет для QA Еды',
            },
            {
                'id': 'w/031bb88c-2e53-5f95-a2f6-82b6886c61f2',
                'type': 'personal_wallet',
                'title': 'Плюс',
            },
        ],
    }
