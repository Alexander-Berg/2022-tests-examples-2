import json

import pytest

from protocol import brands


@pytest.fixture
def paymentstatuses_services(mockserver, load):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '4006998555'},
            'status': {'value': 'VALID'},
            'oauth': {
                'scope': (
                    'yataxi:read yataxi:write yataxi:pay '
                    'yataxi:yauber_request'
                ),
            },
            'phones': [{'attributes': {'102': '+71111111111'}, 'id': '1111'}],
        }


USER_ID = 'a664ff1f661140d2821f711c2f5c644e'


@pytest.mark.translations(
    client_messages={
        'debt_notification_title': {
            'ru': 'У вас не хватило средств на Якарте',
        },
        'debt_notification_text': {'ru': 'Оплатите Якартой и получите кешбек'},
        'debt_alt_payment': {'ru': 'Другие способы оплаты'},
        'main_button_text': {'ru': 'Пополнить'},
    },
)
@pytest.mark.config(
    PAYMENTSTATUSES_POSSIBLE_PAYMENT_TYPES_FOR_DEBT=[
        'card',
        'applepay',
        'googlepay',
        'yandex_card',
    ],
)
@pytest.mark.config(
    PAYMENTSTATUSES_DEBT_NOTIFICATION={
        'yandex_card': {
            'not_enough_funds': {
                'title': 'debt_notification_title',
                'text': 'debt_notification_text',
                'icon_tag': 'icon',
                'alternative_payment_methods_text': 'debt_alt_payment',
                'main_button_text': 'main_button_text',
            },
        },
    },
)
@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_debt_notification',
    consumers=['protocol/paymentstatuses'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize(
    'id, orderid, format_currency, response_file, zone_name',
    [
        (
            USER_ID,
            'c85ea0c44fbe4d2a80400cddc61819e5',
            False,
            'response_orderid_1.json',
            'moscow',
        ),
        (
            USER_ID,
            '648c9eaf30364bbfbcc9b6183046d421',
            False,
            'response_orderid_2.json',
            'moscow',
        ),
        (
            USER_ID,
            'c85ea0c44fbe4d2a80400cddc61819e5',
            True,
            'response_orderid_3.json',
            'moscow',
        ),
        (
            USER_ID,
            '648c9eaf30364bbfbcc9b6183046d421',
            True,
            'response_orderid_4.json',
            'moscow',
        ),
        (
            'f355a8abce7b4937babf19ed8a7aaaaa',
            '0fae601f123f464ab485410052faaaaa',
            True,
            'response_orderid_5.json',
            'almaty',
        ),
        (
            'f355a8abce7b4937babf19ed8a7aaaaa',
            '0fae601f123f464ab485410052faaaab',
            True,
            'response_orderid_5_invalid_zone.json',
            'moscow_invalid_zone',
        ),
        (
            USER_ID,
            '541f2aa834801e1c82de765eb444241e',
            True,
            'response_orderid_9_cashback.json',
            'moscow',
        ),
        (
            'f355a8abce7b4937babf19ed8a7aaaaa',
            '3e19f18946bd2625bc31093c2b8f5557',
            True,
            'response_orderid_12_yandex_card.json',
            'moscow',
        ),
    ],
)
def test_paymentstatuses_by_order_id(
        taxi_protocol,
        load_json,
        paymentstatuses_services,
        id,
        orderid,
        format_currency,
        response_file,
        zone_name,
        db,
):
    json_temp = {'id': id, 'orderid': orderid}
    if format_currency is not None:
        json_temp.update({'format_currency': format_currency})
    db.orders.update_one({'_id': orderid}, {'$set': {'nz': zone_name}})

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=json_temp,
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_file)


@pytest.mark.parametrize(
    'post_json, status_code, expected_data',
    [
        pytest.param(
            {
                'id': USER_ID,
                'orderid': '499bb13a3492488a82ed354c311c3a22',
                'filter': ['debt', 'need_accept'],
            },
            200,
            {'cards': [], 'orders': []},
            id='order_without_debt',
        ),
        pytest.param(
            {'id': USER_ID},
            200,
            {'cards': [], 'orders': []},
            id='user_without_debts',
        ),
        pytest.param(
            {
                'id': USER_ID,
                'orderid': '499bb13a3492488a82ed354c311c3a22',
                'filter': ['aaa', 'bbb', 'ccc'],
            },
            400,
            None,
            id='bad_filters_names',
        ),
    ],
)
def test_paymentstatuses_wrong_response_params(
        taxi_protocol,
        paymentstatuses_services,
        post_json,
        status_code,
        expected_data,
):
    response = taxi_protocol.post(
        '3.0/paymentstatuses', json=post_json, bearer='test_token',
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == expected_data


@pytest.mark.now('2017-06-29T18:53:30+0300')
@pytest.mark.config(
    PAYMENTSTATUSES_POSSIBLE_PAYMENT_TYPES_FOR_DEBT=[
        'card',
        'applepay',
        'googlepay',
        'yandex_card',
    ],
)
@pytest.mark.parametrize(
    'id, filter, format_currency, response_file',
    [
        (USER_ID, ['can_be_paid_by_card'], True, 'response_filter_1.json'),
        (
            '43c6a963790f4f999459cc830d3fa12b',
            ['debt', 'can_be_paid_by_card'],
            False,
            'response_filter_2.json',
        ),
    ],
)
def test_paymentstatuses_by_filter_1(
        taxi_protocol,
        load_json,
        paymentstatuses_services,
        id,
        filter,
        format_currency,
        response_file,
):
    json_temp = {'id': id, 'filter': filter}
    if format_currency is not None:
        json_temp.update({'format_currency': format_currency})

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=json_temp,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_file)


@pytest.mark.config(
    PAYMENTSTATUSES_POSSIBLE_PAYMENT_TYPES_FOR_DEBT=[
        'card',
        'applepay',
        'googlepay',
        'yandex_card',
    ],
)
@pytest.mark.parametrize(
    'id, filter, format_currency, response_file',
    [
        (
            '8045c1e3ed2741619285ae9baf11c7cf',
            ['debt'],
            True,
            'response_filter_3.json',
        ),
        (
            'f355a8abce7b4937babf19ed8a76e47c',
            ['need_accept', 'debt'],
            True,
            'response_filter_4.json',
        ),
    ],
)
def test_paymentstatuses_by_filter_2(
        taxi_protocol,
        load_json,
        paymentstatuses_services,
        id,
        filter,
        format_currency,
        response_file,
):
    json_temp = {'id': id, 'filter': filter}
    if format_currency is not None:
        json_temp.update({'format_currency': format_currency})

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=json_temp,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9'},
    )
    assert response.status_code == 200
    data = response.json()
    reference_data = load_json(response_file)
    data['cards'] = sorted(data['cards'], key=lambda card: card['id'])
    data['orders'] = sorted(data['orders'], key=lambda order: order['orderid'])
    assert data == reference_data


@pytest.mark.config(BILLING_AUTOMATIC_FALLBACK_ENABLED=False)
@pytest.mark.parametrize(
    'filter', [['debt'], ['need_cvn'], ['debt', 'need_cvn']],
)
@pytest.mark.parametrize(
    'global_fallback, order_fallback, billing_ok, show_orders',
    [
        (False, False, False, True),
        (False, False, True, True),
        (False, True, False, False),
        (False, True, True, True),
        (True, False, False, False),
        (True, False, True, False),
        (True, True, False, False),
        (True, True, True, False),
    ],
)
def test_paymentstatuses_by_filter_fallback(
        taxi_protocol,
        blackbox_service,
        filter,
        global_fallback,
        order_fallback,
        billing_ok,
        show_orders,
        config,
):
    blackbox_service.set_token_info('test_token', '4006998555')
    config.set_values(
        dict(
            BILLING_STATIC_COUNTER_STATUS=billing_ok,
            BILLING_ORDER_AUTOFALLBACK_ENABLED=order_fallback,
            BILLING_DEBT_FALLBACK_ENABLED=global_fallback,
        ),
    )

    request = {
        'id': '8045c1e3ed2741619285ae9baf11c7cf',
        'filter': filter,
        'format_currency': True,
    }
    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=request,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9'},
    )
    assert response.status_code == 200
    data = response.json()

    if show_orders:
        assert data['orders'] != []
        ids = {order['orderid'] for order in data['orders']}
        assert ids == {'fe74a71bed8346e1a789f45dbad04392'}
    else:
        assert data['orders'] == []


@pytest.mark.config(
    BILLING_AUTOMATIC_FALLBACK_ENABLED=True,
    BILLING_ORDER_AUTOFALLBACK_ENABLED=True,
    BILLING_DEBT_FALLBACK_ENABLED=False,
    BILLING_USE_MONGO_STATS_COUNTER=True,
    BILLING_AUTOMATIC_FALLBACK_MIN_EVENTS=20,
)
@pytest.mark.parametrize(
    'fallback_enabled, method, auto_min_rate, method_min_rate,'
    'method_min_events, result',
    [
        (True, 'PayBasket', 0.1, 0.9, 20, True),
        (True, 'PayBasket', 0.1, 0.1, 200, True),
        (True, 'PayBasket', 0.1, 0.1, 20, False),
        (True, 'CheckCard', 0.1, 0.1, 20, True),
        (False, 'PayBasket', 0.9, 0.1, 20, True),
        (False, 'PayBasket', 0.1, 0.1, 20, False),
        (False, 'PayBasket', 0.1, 0.9, 200, False),
    ],
)
@pytest.mark.parametrize(
    'filter', [['debt'], ['need_cvn'], ['debt', 'need_cvn']],
)
def test_paymentstatuses_by_filter_methods_fallback(
        taxi_protocol,
        blackbox_service,
        config,
        filter,
        fallback_enabled,
        method,
        auto_min_rate,
        method_min_rate,
        method_min_events,
        result,
):
    blackbox_service.set_token_info('test_token', '4006998555')
    config.set_values(
        dict(
            BILLING_METHOD_FALLBACK_ENABLED=fallback_enabled,
            BILLING_FALLBACK_METHODS=[method],
            BILLING_AUTOMCATIC_FALLBACK_MIN_RATE=auto_min_rate,
            BILLING_FALLBACK_RATE={
                '__default__': {
                    '__default__': {
                        'fallback_rate': 0.1,
                        'fallback_events': 20,
                    },
                    'PayBasket': {
                        'fallback_rate': method_min_rate,
                        'fallback_events': method_min_events,
                    },
                },
            },
        ),
    )
    taxi_protocol.invalidate_caches()

    request = {
        'id': '8045c1e3ed2741619285ae9baf11c7cf',
        'filter': filter,
        'format_currency': True,
    }

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=request,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9'},
    )
    assert response.status_code == 200
    data = response.json()
    if result:
        assert data['orders'] != []
        ids = {order['orderid'] for order in data['orders']}
        assert ids == {'fe74a71bed8346e1a789f45dbad04392'}
    else:
        assert data['orders'] == []


@pytest.mark.config(
    PAYMENTSTATUSES_POSSIBLE_PAYMENT_TYPES_FOR_DEBT=[
        'card',
        'applepay',
        'googlepay',
        'yandex_card',
    ],
)
def test_manual_sum_to_pay(taxi_protocol, paymentstatuses_services, load_json):
    order_id = 'c85ea0c44fbe4d2a80400cddc6180000'
    user_id = 'a664ff1f661140d2821f711c2f5c644e'

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json={'id': user_id, 'orderid': order_id},
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    response_file = 'response_orderid_6.json'
    assert data == load_json(response_file)


@pytest.mark.config(
    PAYMENTSTATUSES_POSSIBLE_PAYMENT_TYPES_FOR_DEBT=[
        'card',
        'applepay',
        'googlepay',
        'yandex_card',
    ],
)
@pytest.mark.parametrize(
    'payment_type, payment_id',
    [
        ('personal_wallet', 'passwal-RUB'),
        ('card', 'card-x2495'),
        ('googlepay', 'card-x2495'),
        ('applepay', 'card-x2495'),
    ],
)
def test_card_like_paymentmethods(
        taxi_protocol,
        paymentstatuses_services,
        load_json,
        db,
        payment_type,
        payment_id,
):
    db.orders.update(
        {'_id': 'ffca4a6ae82e496a8d111d85ad94e4pw'},
        {
            '$set': {
                'payment_tech.type': payment_type,
                'payment_tech.main_card_payment_id': payment_id,
            },
        },
    )

    order_id = 'ffca4a6ae82e496a8d111d85ad94e4pw'
    user_id = 'f355a8abce7b4937babf19ed8a7aaapw'

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json={'id': user_id, 'orderid': order_id},
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    expected_data = load_json('response_orderid_7.json')
    expected_data['orders'][0]['payment']['cardid'] = payment_id
    expected_data['orders'][0]['payment']['type'] = payment_type
    assert data == expected_data


@pytest.mark.config(
    PAYMENTSTATUSES_POSSIBLE_PAYMENT_TYPES_FOR_DEBT=[
        'card',
        'applepay',
        'googlepay',
        'yandex_card',
    ],
)
def test_pended_payorder(taxi_protocol, paymentstatuses_services, load_json):
    order_id = '2a20d1bed4cc15a9e9eb2ad4ebc664aa'
    user_id = '786eaf3a029e883217a11cfcf331124b'

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json={'id': user_id, 'orderid': order_id},
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    response_file = 'response_orderid_8.json'
    assert data == load_json(response_file)


@pytest.mark.config(COOP_ACCOUNT_NON_IGNORE_DEBT_BY_BRAND=[])
@pytest.mark.now('2017-06-29T18:53:30+0300')
@pytest.mark.parametrize(
    'id',
    ['f355a8abce7b4937babf19ed8a700000', 'f355a8abce7b4937babf19ed8a711111'],
)
def test_paymentstatuses_coop_account_eliminated(
        taxi_protocol, load_json, paymentstatuses_services, id,
):
    json_temp = {'id': id, 'filter': ['debt', 'can_be_paid_by_card']}

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=json_temp,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9'},
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data['orders']) == 0


@pytest.mark.now('2017-06-29T18:53:30+0300')
@pytest.mark.parametrize('is_family_card', [False, True])
@pytest.mark.parametrize(
    'id, order_debt, is_owner',
    [
        pytest.param(
            'f355a8abce7b4937babf19ed8a700000',
            'ffca4a6ae82e496a8d111d85ad94e400',
            True,
            id='own_order',
        ),
        pytest.param(
            'f355a8abce7b4937babf19ed8a711111',
            'ffca4a6ae82e496a8d111d85ad94e411',
            False,
            id='member_order',
        ),
    ],
)
def test_paymentstatuses_coop_account(
        taxi_protocol,
        load_json,
        paymentstatuses_services,
        mongodb,
        is_family_card,
        id,
        order_debt,
        is_owner,
):
    if is_family_card:
        assert (
            mongodb.orders.update_one(
                {'_id': order_debt},
                {
                    '$set': {
                        'order.request.payment.type': 'card',
                        'payment_tech.family': {'is_owner': is_owner},
                    },
                },
            ).modified_count
            == 1
        )
    json_temp = {'id': id, 'filter': ['debt', 'can_be_paid_by_card']}

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=json_temp,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={
            'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9',
            'User-Agent': 'yandex-taxi/3.18.0.7675 android/6.0',
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data['orders']) == 1
    assert data['orders'][0]['orderid'] == order_debt


@pytest.mark.config(
    APPLICATION_MAP_BRAND={'__default__': 'yauber', 'uber_android': 'yauber'},
)
@pytest.mark.now('2017-06-29T18:53:30+0300')
@pytest.mark.parametrize(
    'id',
    ['f355a8abce7b4937babf19ed8a700000', 'f355a8abce7b4937babf19ed8a711111'],
)
def test_paymentstatuses_coop_account_yauber(taxi_protocol, mockserver, id):
    json_temp = {'id': id, 'filter': ['debt', 'can_be_paid_by_card']}

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '4006998555'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:yauber_request'},
            'phones': [{'attributes': {'102': '+71111111111'}, 'id': '1111'}],
        }

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=json_temp,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={
            'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9',
            'User-Agent': 'yandex-uber/3.18.0.7675 android/6.0',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data['orders']) == 0


@pytest.mark.parametrize(
    'code, response, expected_code',
    [
        (200, '', 500),
        (200, {}, 500),
        (
            200,
            {'remaining_limit': 50, 'currency': 'RUB', 'has_debts': False},
            200,
        ),
        (400, '', 500),
        (500, {}, 200),
    ],
)
@pytest.mark.user_experiments('overdraft_in_paymentstatuses')
def test_paymentstatuses_debt_servererror(
        taxi_protocol,
        mockserver,
        paymentstatuses_services,
        code,
        response,
        expected_code,
):
    @mockserver.handler('/debts/v1/overdraft/limit')
    def mock_overdraft(request):
        resp = response if isinstance(response, str) else json.dumps(response)
        return mockserver.make_response(resp, code)

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json={'id': 'f355a8abce7b4937babf19ed8a700000', 'filter': ['debt']},
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9'},
    )

    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'remaining_limit,overdraft_available',
    [(0, False), (0.1, True), (50, True)],
)
@pytest.mark.user_experiments('overdraft_in_paymentstatuses')
def test_paymentstatuses_overdraft(
        taxi_protocol,
        mockserver,
        overdraft_available,
        remaining_limit,
        paymentstatuses_services,
):
    @mockserver.json_handler('/debts/v1/overdraft/limit')
    def mock_overdraft(request):
        return {
            'remaining_limit': remaining_limit,
            'currency': 'RUB',
            'has_debts': True,
        }

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json={'id': 'f355a8abce7b4937babf19ed8a700000', 'filter': ['debt']},
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers={'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9'},
    )

    data = response.json()
    assert response.status_code == 200
    assert data['overdraft_available'] is overdraft_available


@pytest.mark.config(PAYMENT_STATUSES_FILTER_BY_APPLICATION_BRAND_ENABLED=True)
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi', 'uber_android': 'yauber'},
)
@pytest.mark.parametrize(
    'post_json, user_agent, expected_card_ids, expected_order_ids',
    [
        pytest.param(
            {
                'id': 'f355a8abce7b4937babf19ed8a76e47c',
                'orderid': '0fae601f123f464ab485410052feae2f',
                'format_currency': True,
            },
            brands.yataxi.android.user_agent,
            {'card-x2495'},
            {'0fae601f123f464ab485410052feae2f'},
            id='order_yataxi',
        ),
        pytest.param(
            {
                'id': 'f355a8abce7b4937babf19ed8a76e47c',
                'orderid': '0fae601f123f464ab485410052feae2f',
                'format_currency': True,
            },
            brands.yauber.android.user_agent,
            set(),
            set(),
            id='order_yauber',
        ),
        pytest.param(
            {
                'id': 'f355a8abce7b4937babf19ed8a76e47c',
                'filter': ['need_accept', 'debt'],
                'format_currency': True,
            },
            brands.yataxi.android.user_agent,
            {'card-x2495'},
            {'0fae601f123f464ab485410052feae2f'},
            id='filter_yataxi',
        ),
        pytest.param(
            {
                'id': 'f355a8abce7b4937babf19ed8a76e47c',
                'filter': ['need_accept', 'debt'],
                'format_currency': True,
            },
            brands.yauber.android.user_agent,
            {'card-x1445'},
            {'7243bb40c93e479985463c7155100e9d'},
            id='filter_yauber',
        ),
    ],
)
def test_paymentstatuses_multiple_apps(
        taxi_protocol,
        mockserver,
        paymentstatuses_services,
        load_json,
        post_json,
        user_agent,
        expected_card_ids,
        expected_order_ids,
):
    """Checks that debts orders are separated by application brand."""

    headers = {
        'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9',
        'User-Agent': user_agent,
    }
    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=post_json,
        bearer='test_token',
        x_real_ip='1.2.3.4',
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()

    card_ids = {card['id'] for card in data['cards']}
    order_ids = {order['orderid'] for order in data['orders']}

    assert card_ids == expected_card_ids
    assert order_ids == expected_order_ids


@pytest.mark.parametrize(
    'config_enabled,bin_info,currency_list,expected',
    [
        pytest.param(False, {}, [], True, id='config_disabled'),
        pytest.param(
            True,
            {'55555': {'currency': 'RUB'}},
            ['UZB'],
            True,
            id='config_enabled_currency_doesnt_match_1',
        ),
        pytest.param(
            True,
            {'55555': {'currency': 'UZB'}},
            ['RUB'],
            True,
            id='config_enabled_currency_doesnt_match_2',
        ),
        pytest.param(True, {}, ['RUB'], True, id='config_enabled_no_bin_info'),
        pytest.param(
            True,
            {'55555': {'currency': 'RUB'}},
            [],
            True,
            id='config_enabled_empty_currency_list',
        ),
        pytest.param(
            True,
            {'55555': {'currency': 'RUB'}},
            ['RUB'],
            False,
            id='config_enabled_all_matches',
        ),
    ],
)
def test_paymentstatuses_cvn_ignore_list(
        taxi_protocol,
        paymentstatuses_services,
        db,
        taxi_config,
        config_enabled,
        bin_info,
        currency_list,
        expected,
):
    order_id = '0fae601f123f464ab485410052feae2f'

    db.orders.update(
        {'_id': order_id}, {'$set': {'payment_tech.need_cvn': True}},
    )

    payload = {
        'id': 'f355a8abce7b4937babf19ed8a76e47c',
        'orderid': order_id,
        'format_currency': True,
    }

    taxi_config.set_values(
        {
            'PAYMENTSTATUSES_IGNORE_CVN_BY_CURRENCY_ENABLED': config_enabled,
            'CARDSTORAGE_BIN_INFO': bin_info,
            'PAYMENTSTATUSES_IGNORE_CVN_CURRENCY_LIST': currency_list,
        },
    )
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=payload,
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    assert data['orders'][0]['payment']['need_cvn'] is expected


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='pay_debts_without_cvv',
    consumers=['protocol/paymentstatuses'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize('need_cvn', [True, False])
def test_experiment_debt_payment_without_cvv(
        taxi_protocol, paymentstatuses_services, db, taxi_config, need_cvn,
):
    order_id = '0fae601f123f464ab485410052feae2f'

    db.orders.update(
        {'_id': order_id}, {'$set': {'payment_tech.need_cvn': need_cvn}},
    )

    payload = {
        'id': 'f355a8abce7b4937babf19ed8a76e47c',
        'orderid': order_id,
        'format_currency': True,
    }

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=payload,
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['orders'][0]['payment']['need_cvn']


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='taxi_service_token',
    consumers=['protocol/paymentstatuses'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True, 'service_token': 'some_token'},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_service_token_experiment(
        taxi_protocol, paymentstatuses_services, load_json,
):
    order_id = '0fae601f123f464ab485410052feae2f'

    payload = {
        'id': 'f355a8abce7b4937babf19ed8a76e47c',
        'orderid': order_id,
        'format_currency': True,
    }

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json=payload,
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    expected_data = load_json('response_orderid_10_service_token.json')
    assert response.json() == expected_data


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='taxi_service_token',
    consumers=['protocol/paymentstatuses'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True, 'service_token': 'some_token'},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(PAYMENTSTATUSES_POSSIBLE_PAYMENT_TYPES_FOR_DEBT=['sbp'])
def test_sbp(taxi_protocol, paymentstatuses_services, load_json, db):
    db.orders.update(
        {'_id': 'ffca4a6ae82e496a8d111d85ad94e4sbp'},
        {
            '$set': {
                'payment_tech.type': 'sbp',
                'payment_tech.main_card_payment_id': 'sbp_qr',
            },
        },
    )

    order_id = 'ffca4a6ae82e496a8d111d85ad94e4sbp'
    user_id = 'f355a8abce7b4937babf19ed8a7aaapw'

    response = taxi_protocol.post(
        '3.0/paymentstatuses',
        json={'id': user_id, 'orderid': order_id},
        bearer='test_token',
        x_real_ip='1.2.3.4',
    )
    assert response.status_code == 200
    data = response.json()
    expected_data = load_json('response_orderid_11_sbp.json')
    assert data == expected_data
