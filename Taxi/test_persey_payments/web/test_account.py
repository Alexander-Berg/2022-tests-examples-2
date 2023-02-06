import pytest


@pytest.mark.config(
    ORDERHISTORY_PAYMENT_METHOD_IMAGE_TAG={
        '__default__': 'other_payment_default_card',
        'applepay': {'image_tag': 'other_payment_applepay'},
        'card': {
            'key': 'system',
            'key_image_tags': {
                'MasterCard': 'mastercard_card',
                'VISA': 'visa_card',
                '__default__': 'other_payment_default_card',
            },
        },
    },
)
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    [
        'donation_type',
        'brand',
        'subs_id',
        'cursor',
        'exp_check_basket_times_called',
        'exp_tp_times_called',
        'exp_cardstorage_times_called',
        'exp_zalogin_times_called',
        'exp_resp',
    ],
    [
        (
            'oneshot',
            None,
            None,
            None,
            3,
            0,
            0,
            0,
            'transactions_resp_oneshot.json',
        ),
        (
            'subs',
            None,
            'first_external_id',
            None,
            1,
            0,
            0,
            0,
            'transactions_resp_subs.json',
        ),
        (
            'ride_subs',
            'yataxi',
            None,
            None,
            0,
            3,
            1,
            1,
            'transactions_resp_ride_subs.json',
        ),
        (
            'oneshot',
            None,
            None,
            '2019-01-23T22:49:57.000000+03:00',
            2,
            0,
            0,
            0,
            'transactions_resp_oneshot_cursor.json',
        ),
    ],
)
async def test_transactions(
        taxi_persey_payments_web,
        load_json,
        mock_cardstorage_card,
        mock_transactions_persey,
        mock_zalogin,
        mock_trust_check_basket,
        donation_type,
        brand,
        subs_id,
        cursor,
        exp_check_basket_times_called,
        exp_tp_times_called,
        exp_cardstorage_times_called,
        exp_zalogin_times_called,
        exp_resp,
):
    transactions_persey_mock = mock_transactions_persey(
        'transactions_persey_resp.json',
    )
    cardstorage_mock = mock_cardstorage_card(
        [('tp_uid', 'card-x777')], 'cardstorage_card_resp.json',
    )
    zalogin_mock = mock_zalogin('portal_uid', 'zalogin_resp_portal.json')
    check_basket_mock = mock_trust_check_basket(
        {
            'user_account': '00000000****0000',
            'card_type': 'MasterCard',
            'payment_status': 'cleared',
        },
    )

    request_params = {
        'donation_type': donation_type,
        'brand': brand,
        'subs_id': subs_id,
    }
    if cursor is not None:
        request_params['cursor'] = cursor

    response = await taxi_persey_payments_web.get(
        '/payments/v1/personal_account/transactions',
        params=request_params,
        headers={'X-Yandex-UID': 'portal_uid'},
    )

    assert response.status == 200
    assert await response.json() == load_json(exp_resp)

    assert transactions_persey_mock.times_called == exp_tp_times_called
    assert cardstorage_mock.times_called == exp_cardstorage_times_called
    assert zalogin_mock.times_called == exp_zalogin_times_called
    assert check_basket_mock.times_called == exp_check_basket_times_called


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    'zalogin_resp, exp_resp',
    [
        ('zalogin_resp_portal.json', 'summary_resp_portal.json'),
        ('zalogin_resp_no_bound.json', 'summary_resp_no_bound.json'),
    ],
)
async def test_summary(
        taxi_persey_payments_web,
        load_json,
        mock_zalogin,
        zalogin_resp,
        exp_resp,
):
    zalogin_mock = mock_zalogin('portal_uid', zalogin_resp)

    response = await taxi_persey_payments_web.get(
        '/payments/v1/personal_account/summary',
        headers={'X-Yandex-UID': 'portal_uid'},
    )

    assert response.status == 200
    assert await response.json() == load_json(exp_resp)

    assert zalogin_mock.times_called == 1


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    [
        'donation_type',
        'exp_check_basket_times_called',
        'exp_check_subs_times_called',
        'exp_tp_times_called',
        'exp_cardstorage_card_times_called',
        'exp_payment_methods_times_called',
        'exp_zalogin_times_called',
        'exp_resp',
    ],
    [
        ('oneshot', 3, 0, 0, 0, 0, 0, 'summary_oneshot_resp.json'),
        ('subs', 2, 2, 0, 0, 1, 0, 'summary_subs_resp.json'),
        ('ride_subs', 0, 0, 4, 1, 0, 1, 'summary_ride_subs_resp.json'),
    ],
)
async def test_summary_donation_type(
        taxi_persey_payments_web,
        load_json,
        mock_cardstorage_card,
        mock_cs_payment_methods,
        mock_transactions_persey,
        mock_zalogin,
        mock_trust_check_basket,
        mock_check_subs,
        donation_type,
        exp_check_basket_times_called,
        exp_check_subs_times_called,
        exp_tp_times_called,
        exp_cardstorage_card_times_called,
        exp_payment_methods_times_called,
        exp_zalogin_times_called,
        exp_resp,
):
    transactions_persey_mock = mock_transactions_persey(
        'transactions_persey_resp.json',
    )
    cardstorage_mock = mock_cardstorage_card(
        [('tp_uid', 'card-x777')], 'cardstorage_card_resp.json',
    )
    payment_methods_mock = mock_cs_payment_methods('payment_methods_resp.json')
    zalogin_mock = mock_zalogin('portal_uid', 'zalogin_resp_portal.json')
    check_basket_mock = mock_trust_check_basket(
        {
            'user_account': '00000000****0000',
            'card_type': 'MasterCard',
            'payment_status': 'cleared',
        },
    )
    check_subs_mock = mock_check_subs('check_subs_response.json')

    response = await taxi_persey_payments_web.get(
        f'/payments/v1/personal_account/summary/{donation_type}',
        headers={'X-Yandex-UID': 'portal_uid'},
    )

    assert response.status == 200
    assert await response.json() == load_json(exp_resp)

    assert transactions_persey_mock.times_called == exp_tp_times_called
    assert cardstorage_mock.times_called == exp_cardstorage_card_times_called
    assert zalogin_mock.times_called == exp_zalogin_times_called
    assert check_basket_mock.times_called == exp_check_basket_times_called
    assert check_subs_mock.times_called == exp_check_subs_times_called
    assert (
        payment_methods_mock.times_called == exp_payment_methods_times_called
    )


@pytest.mark.parametrize(
    [
        'brand',
        'expected_resp_code',
        'expected_hidden_at',
        'expected_active_ride_subs',
        'expected_events',
    ],
    [
        (
            'yataxi',
            204,
            {
                ('portal_uid', 'yataxi'): True,
                ('phonish_uid', 'yataxi'): True,
                ('portal_uid', 'lavka'): False,
                ('portal_uid', 'market'): False,
            },
            [[3, 'portal_uid', 'lavka'], [4, 'portal_uid', 'market']],
            'expected_events_yataxi.json',
        ),
        (
            'lavka',
            204,
            {
                ('portal_uid', 'yataxi'): False,
                ('phonish_uid', 'yataxi'): False,
                ('portal_uid', 'lavka'): True,
                ('portal_uid', 'market'): False,
            },
            [
                [1, 'phonish_uid', 'yataxi'],
                [2, 'portal_uid', 'yataxi'],
                [4, 'portal_uid', 'market'],
            ],
            'expected_events_lavka.json',
        ),
        (
            'nonexistent',
            404,
            {
                ('portal_uid', 'yataxi'): False,
                ('phonish_uid', 'yataxi'): False,
                ('portal_uid', 'lavka'): False,
                ('portal_uid', 'market'): False,
            },
            [
                [1, 'phonish_uid', 'yataxi'],
                [2, 'portal_uid', 'yataxi'],
                [3, 'portal_uid', 'lavka'],
                [4, 'portal_uid', 'market'],
            ],
            'expected_events_empty.json',
        ),
    ],
)
async def test_delete_ride_subs(
        taxi_persey_payments_web,
        stq,
        load_json,
        mock_zalogin,
        get_ride_subs,
        get_active_ride_subs,
        check_ride_subs_events,
        brand,
        expected_resp_code,
        expected_hidden_at,
        expected_active_ride_subs,
        expected_events,
):
    zalogin_mock = mock_zalogin('portal_uid', 'zalogin_resp_portal.json')

    response = await taxi_persey_payments_web.delete(
        '/payments/v1/personal_account/ride_subs',
        params={'brand': brand},
        headers={'X-Yandex-UID': 'portal_uid'},
    )

    assert response.status == expected_resp_code, await response.json()

    hidden_at = {(data[0], data[2]): data[-1] for data in get_ride_subs()}
    assert hidden_at == expected_hidden_at
    assert get_active_ride_subs() == expected_active_ride_subs
    check_ride_subs_events(expected_events)
    assert zalogin_mock.times_called == 1
