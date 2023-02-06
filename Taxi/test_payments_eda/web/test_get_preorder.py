# pylint: disable=too-many-lines
import enum
import typing

import pytest

from taxi.clients import experiments3
from taxi.util import unused

from payments_eda import consts as service_consts
from payments_eda.utils import experiments
from payments_eda.utils import payment_methods
from test_payments_eda import common
from test_payments_eda import consts
from test_payments_eda import preorder


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.translations(
        tariff={
            'currency_with_sign.default': {
                'ru': '$VALUE$ $SIGN$$CURRENCY$',
                'en': '$VALUE$ $SIGN$$CURRENCY$',
            },
            'currency.rub': {'ru': 'rub.', 'en': 'eub.'},
            'currency.usd': {'en': 'usd'},
            'currency_sign.rub': {'ru': '$R', 'en': '$R'},
            'currency_sign.usd': {'ru': '$R', 'en': '$R'},
        },
        client_messages={
            'payments_eda.preorder.user_order_mismatch.message': {
                'ru': 'User order mismatch ru message',
            },
        },
    ),
]


class CardSource(enum.Enum):
    CARDSTORAGE = 'cardstorage'
    CARD_FILTER = 'card_filter'


def _card_to_preorder(
        card: dict,
        allowed_cards: typing.Optional[typing.List[str]],
        disabled_reason: typing.Optional[str],
        cards_from: CardSource,
):
    is_available = True
    if allowed_cards:
        is_verified = card['card_id'] in allowed_cards
        is_available = card['valid'] and is_verified
    disabled_reason = disabled_reason or ''
    id_key = 'card_id' if cards_from == CardSource.CARDSTORAGE else 'id'
    return {
        'type': 'card',
        'name': card['system'],
        'id': card.get(id_key),
        'bin': card['number'][:6],
        'number': card['number'],
        'system': card['system'],
        'currency': card['currency'],
        'available': is_available,
        'availability': {
            'available': is_available,
            'disabled_reason': disabled_reason,
        },
    }


def _enable_wallet_for(service=None):
    args = [
        {
            'name': 'yandex_uid',
            'type': 'string',
            'value': consts.DEFAULT_YANDEX_UID,
        },
        {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
    ]
    if service is not None:
        args.append({'name': 'service', 'type': 'string', 'value': service})
    return pytest.mark.client_experiments3(
        consumer=service_consts.EXP3_CONSUMER_WEB,
        experiment_name=experiments.PERSONAL_WALLET_ENABLED_EXP,
        args=args,
        value={'enabled': True},
    )


async def _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        card_payment_methods,
        build_pa_headers,
        additional_payment_methods=None,
        allowed_cards=None,
        pa_ya_taxi_pass_flags=None,
        user_agent=None,
        yandex_login_id=None,
        disabled_reason=None,
        filter_cards=None,
        cards_from=CardSource.CARDSTORAGE,
        external_ref='123',
        service_token=None,
        service=service_consts.SERVICE_EATS,
):
    if additional_payment_methods is None:
        additional_payment_methods = []

    headers = build_pa_headers(
        user_ip,
        locale,
        yandex_login_id=yandex_login_id,
        ya_taxi_pass_flags=pa_ya_taxi_pass_flags,
        user_agent=user_agent,
    )
    resp = await web_app_client.post(
        f'/4.0/payments/v1/preorder?'
        f'service={service}&external_ref={external_ref}',
        headers=headers,
    )

    assert resp.status == 200

    # cards payment methods
    preorder_card_payment_methods = [
        _card_to_preorder(
            card, allowed_cards, disabled_reason, cards_from=cards_from,
        )
        for card in card_payment_methods['available_cards']
    ]
    filtered_card_payment_methods = [
        card
        for card in preorder_card_payment_methods
        if not filter_cards
        or filter_cards == preorder.NO_CARD_ID  # look to |NO_CARD_ID| comment.
        or card['id'] in filter_cards
    ]

    # also add additional payment methods like 'apple pay' or 'google pay'
    result_payment_methods = filtered_card_payment_methods + [
        {'type': payment_method}
        for payment_method in additional_payment_methods
    ]
    expected_response = {
        'amount': '10.50',
        'amount_template': '10,50 $SIGN$$CURRENCY$',
        'currency': currency,
        'items': [
            {
                'amount_template': '10,50 $SIGN$$CURRENCY$',
                'currency': currency,
                'id': external_ref,
            },
        ],
        'payment_methods': result_payment_methods,
        'currency_rules': {
            'code': currency,
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'sign': '$R',
            'text': expected_currency_text,
        },
        'country_code': 'RU',
        'region_id': 123,
        'merchant_id_list': ['merchant.ru.yandex.ytaxi.trust'],
    }

    if service_token is not None:
        expected_response['service_token'] = service_token

    assert await resp.json() == expected_response


DEFAULT_PREORDER_BASIC_TEST_PARAMS = ('RUB', None, 'rub.')


# pylint: disable=protected-access
@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.config(LOCALES_MAPPING={'xx': 'ru'})
@pytest.mark.parametrize(
    'currency,locale,expected_currency_text,service',
    [
        # checking locales
        (*DEFAULT_PREORDER_BASIC_TEST_PARAMS, service_consts.SERVICE_EATS),
        ('RUB', 'en', 'eub.', service_consts.SERVICE_EATS),
        ('RUB', 'en, ru;0.8', 'eub.', service_consts.SERVICE_EATS),
        ('RUB', 'ru;0.9, en;0.6', 'rub.', service_consts.SERVICE_EATS),
        ('RUB', 'xxxx', 'rub.', service_consts.SERVICE_EATS),
        ('USD', 'zz', 'usd', service_consts.SERVICE_EATS),
        ('RUB', 'xxxx', 'rub.', service_consts.SERVICE_EATS),
        # checking services
        (*DEFAULT_PREORDER_BASIC_TEST_PARAMS, service_consts.SERVICE_GROCERY),
        (*DEFAULT_PREORDER_BASIC_TEST_PARAMS, service_consts.SERVICE_PHARMACY),
        (*DEFAULT_PREORDER_BASIC_TEST_PARAMS, service_consts.SERVICE_SHOP),
    ],
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
@pytest.mark.parametrize('drop_grocery_cart_items_v2', [True, False])
async def test_basic(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_order,
        mock_grocery_cart,
        mock_get_payment_types_info,
        load_json,
        currency,
        locale,
        expected_currency_text,
        patch,
        build_pa_headers,
        is_grocery,
        external_ref,
        service,
        get_single_stat_by_label_values,
        drop_grocery_cart_items_v2,
):
    user_ip = '1.1.1.1'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        assert request.json == {'yandex_uid': consts.DEFAULT_YANDEX_UID}
        return cardstorage_payment_methods

    mock_get_payment_types_info(
        available_payment_types=['card', 'applepay'], request_service=service,
    )

    get_order_mock = mock_get_order(is_grocery, external_ref, currency)

    if drop_grocery_cart_items_v2:
        mock_grocery_cart.drop_items_v2()

    await _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        cardstorage_payment_methods,
        build_pa_headers,
        ['applepay'],
        external_ref=external_ref,
        service=service,
    )

    assert cardstorage_mock.times_called == 1
    assert get_order_mock.times_called == 1

    stat = get_single_stat_by_label_values(
        web_app['context'], {'sensor': 'create_preorder_prefinish'},
    )

    assert stat == common.make_stat(
        {
            'invoice_service': service,
            'sensor': 'create_preorder_prefinish',
            'currency': currency,
            'country_code': 'RU',
            'region_id': '123',
        },
    )


@pytest.mark.config(PAYMENTS_EDA_ATTEMPT_TO_PATCH_EDA_BASE_URL=True)
async def test_no_base_eda_url_without_experiment(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_order,
        mock_get_payment_types_info,
        load_json,
        patch,
        build_pa_headers,
):
    user_ip = '1.1.1.1'
    (
        currency,
        locale,
        expected_currency_text,
    ) = DEFAULT_PREORDER_BASIC_TEST_PARAMS
    service = service_consts.SERVICE_EATS
    is_grocery = False
    external_ref = '123'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        assert request.json == {'yandex_uid': consts.DEFAULT_YANDEX_UID}
        return cardstorage_payment_methods

    mock_get_payment_types_info(
        available_payment_types=['card', 'applepay'], request_service=service,
    )

    get_order_mock = mock_get_order(is_grocery, external_ref, currency)

    await _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        cardstorage_payment_methods,
        build_pa_headers,
        ['applepay'],
        external_ref=external_ref,
        service=service,
    )

    assert cardstorage_mock.times_called == 1
    assert get_order_mock.times_called == 1


NEW_BASE_URL = 'new_base_url'


@pytest.mark.config(PAYMENTS_EDA_ATTEMPT_TO_PATCH_EDA_BASE_URL=True)
@common.add_experiment(
    experiment_name=experiments.EXP3_PAYMENTS_EDA_URLS,
    experiment_value={'patched_base_url': f'$mockserver/{NEW_BASE_URL}'},
)
async def test_get_base_eda_url_from_experiment(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_order,
        mock_get_payment_types_info,
        load_json,
        patch,
        build_pa_headers,
):
    user_ip = '1.1.1.1'
    (
        currency,
        locale,
        expected_currency_text,
    ) = DEFAULT_PREORDER_BASIC_TEST_PARAMS
    service = service_consts.SERVICE_EATS
    is_grocery = False
    external_ref = '123'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        assert request.json == {'yandex_uid': consts.DEFAULT_YANDEX_UID}
        return cardstorage_payment_methods

    mock_get_payment_types_info(
        available_payment_types=['card', 'applepay'], request_service=service,
    )

    get_order_mock = mock_get_order(is_grocery, external_ref, currency)
    new_get_order_mock = mock_get_order(
        is_grocery, external_ref, currency, base_url=NEW_BASE_URL,
    )

    await _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        cardstorage_payment_methods,
        build_pa_headers,
        ['applepay'],
        external_ref=external_ref,
        service=service,
    )

    assert cardstorage_mock.times_called == 1
    assert new_get_order_mock.times_called == 1
    assert get_order_mock.times_called == 0


@pytest.mark.config(PAYMENTS_EDA_CORP_ENABLED=True)
@pytest.mark.config(PAYMENTS_EDA_LIST_PAYMENTMETHODS_FROM_CARDSTORAGE=True)
@pytest.mark.parametrize('business', [None, service_consts.BUSINESS_PHARMACY])
async def test_pass_corp_payments_response_as_is(
        web_app_client,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        _no_cards_response,
        _all_methods_in_exp3,
        _zoneinfo_mock,
        _nearestzone_mock,
        build_pa_headers,
        corp_int_api_mock,
        load_json,
        patch,
        business,
):
    mock_get_payment_types_info(available_payment_types=[], merchant_ids=[])

    dummy_eats_mock = eda_doc_mockserver(
        preorder.eats_response_body('123', 'RUB', '10.50', business),
    )
    corp_lpm = load_json('corp_int_api_list_payment_methods.json')
    dummy_corp_mock = corp_int_api_mock(corp_lpm)
    unused.dummy(dummy_eats_mock, dummy_corp_mock)

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=eats&external_ref=123',
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == 200
    body = await response.json()
    corp_methods = [
        pm for pm in body['payment_methods'] if pm['type'] == 'corp'
    ]
    if business == service_consts.BUSINESS_PHARMACY:
        assert corp_methods == []
        assert dummy_corp_mock.times_called == 0
    else:
        payment_methods_expected = corp_lpm['payment_methods']
        for method in payment_methods_expected:
            method.pop('user_id')
            method.pop('client_id')
        assert corp_methods == payment_methods_expected


@pytest.mark.config(PAYMENTS_EDA_CORP_ENABLED=False)
@pytest.mark.config(PAYMENTS_EDA_LIST_PAYMENTMETHODS_FROM_CARDSTORAGE=True)
@pytest.mark.parametrize(
    'business, available, disabled_reason',
    [
        ('restaurant', True, ''),
        ('store', True, ''),
        (
            service_consts.BUSINESS_PHARMACY,
            False,
            payment_methods.BADGE_DISABLED_REASON_MESSAGE,
        ),
    ],
)
async def test_preorder_badge(
        web_app_client,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        _no_cards_response,
        _all_methods_in_exp3,
        _zoneinfo_mock,
        _nearestzone_mock,
        build_pa_headers,
        load_json,
        patch,
        business,
        available,
        disabled_reason,
):
    dummy_eats_mock = eda_doc_mockserver(
        preorder.eats_response_body('123', 'RUB', '10.50', business),
    )
    unused.dummy(dummy_eats_mock)

    mock_get_payment_types_info(
        available_payment_types=['badge'], merchant_ids=[],
    )

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=eats&external_ref=123',
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == 200
    body = await response.json()
    corp_methods = [
        pm for pm in body['payment_methods'] if pm['type'] == 'corp'
    ]
    assert len(corp_methods) == 1

    assert corp_methods[0] == {
        'availability': {
            'available': available,
            'disabled_reason': disabled_reason,
        },
        'currency': 'RUB',
        'description': '',
        'id': 'badge:yandex_badge:RUB',
        'name': 'Yandex Badge',
        'type': 'corp',
    }


@pytest.mark.parametrize(
    'service',
    [
        pytest.param('eats', marks=_enable_wallet_for('eats')),
        pytest.param('grocery', marks=_enable_wallet_for('grocery')),
    ],
)
@pytest.mark.parametrize('complement_enabled', [False, True])
async def test_preorder_personal_wallet(
        web_app_client,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        _no_cards_response,
        _all_methods_in_exp3,
        _zoneinfo_mock,
        _nearestzone_mock,
        build_pa_headers,
        load_json,
        patch,
        complement_enabled: bool,
        service: str,
        mockserver,
):
    dummy_eats_mock = eda_doc_mockserver(
        preorder.eats_response_body('123', 'RUB', '10.50'),
    )

    mock_get_payment_types_info(
        request_service=service,
        available_payment_types=['personal_wallet'],
        merchant_ids=[],
    )

    available_accounts_response = load_json(
        'available_accounts_with_complements.json'
        if complement_enabled
        else 'personal_wallet_available_accounts.json',
    )

    @mockserver.json_handler('/personal_wallet/v1/available-accounts')
    def available_accounts_mock(request):
        assert request.query['service'] == service
        return mockserver.make_response(
            status=200, json=available_accounts_response,
        )

    unused.dummy(dummy_eats_mock, available_accounts_mock)

    response = await web_app_client.post(
        f'/4.0/payments/v1/preorder?service={service}&external_ref=123',
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == 200
    body = await response.json()
    wallet_methods = [
        pm for pm in body['payment_methods'] if pm['type'] == 'personal_wallet'
    ]
    assert len(wallet_methods) == 1

    availability = (
        {'available': True, 'disabled_reason': ''}
        if complement_enabled
        else {'available': False, 'disabled_reason': ''}
    )

    wallet_method = {
        'available': True,
        'availability': availability,
        'currency_rules': {
            'code': 'RUB',
            'sign': '₽',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'text': 'руб.',
        },
        'description': '500 $SIGN$$CURRENCY$',
        'money_left_as_decimal': '500',
        'id': 'wallet_id/1234567890',
        'name': 'Плюс',
        'type': 'personal_wallet',
    }

    if complement_enabled:
        wallet_method.update(
            {
                'complement_attributes': {
                    'compatibility_description': (
                        'Applies to cards and Google Pay'
                    ),
                    'name': 'Plus — spend on ride',
                    'payment_types': ['card', 'applepay', 'googlepay'],
                },
                'is_complement': True,
                'subtitle': 'Баланс: 500 баллов',
            },
        )
    assert wallet_methods[0] == wallet_method


@pytest.mark.parametrize(
    'filter_card_id', [preorder.NO_CARD_ID, 'card-x5a4adedaf78dba6f9c56fee4'],
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
async def test_eda_metainfo_payment_method(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_payment_types_info,
        mock_get_order,
        load_json,
        patch,
        build_pa_headers,
        filter_card_id,
        is_grocery,
        external_ref,
):
    user_ip = '1.1.1.1'
    currency = 'RUB'
    locale = 'en'
    expected_currency_text = 'eub.'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        return cardstorage_payment_methods

    mock_get_payment_types_info()

    mock_order = mock_get_order(
        is_grocery, external_ref, currency=currency, card_id=filter_card_id,
    )
    if filter_card_id != preorder.NO_CARD_ID:  # look to |NO_CARD_ID| comment.
        filter_card_id = [filter_card_id]

    await _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        cardstorage_payment_methods,
        build_pa_headers,
        filter_cards=filter_card_id,
        external_ref=external_ref,
    )
    assert cardstorage_mock.times_called == 1

    assert mock_order.times_called == 1


@pytest.mark.parametrize(
    'filter_card, make_random_card_ids',
    [('card-nosuchcard', False), (None, True)],
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
async def test_eda_metainfo_payment_method_error(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_payment_types_info,
        mock_get_order,
        load_json,
        patch,
        build_pa_headers,
        filter_card,
        make_random_card_ids,
        is_grocery,
        external_ref,
):
    user_ip = '1.1.1.1'
    locale = 'en'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        return cardstorage_payment_methods

    mock_get_payment_types_info(available_payment_types=['card', 'applepay'])

    _get_order_mock = mock_get_order(
        is_grocery,
        external_ref,
        card_id=filter_card,
        make_random=make_random_card_ids,
    )

    headers = build_pa_headers(user_ip, locale)
    resp = await web_app_client.post(
        f'/4.0/payments/v1/preorder?service=eats&external_ref={external_ref}',
        headers=headers,
    )

    assert cardstorage_mock.times_called == 1
    assert resp.status == 409

    assert _get_order_mock.times_called == 1


@pytest.mark.parametrize(
    'pa_yandex_uid, pa_bound_uids, expected_status',
    [
        (consts.DEFAULT_YANDEX_UID, '', 200),
        (
            'unknown_uid',
            f'unknown_uid_1,{consts.DEFAULT_YANDEX_UID},unknown_uid_2',
            200,
        ),
        ('unknown_uid', '', 404),
        ('unknown_uid', 'unknown_uid_1,unknown_uid_2,unknown_uid_3', 404),
    ],
)
@pytest.mark.config(PAYMENTS_EDA_LIST_PAYMENTMETHODS_FROM_CARDSTORAGE=True)
async def test_order_user_access(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_payment_types_info,
        _no_cards_response,
        _all_methods_in_exp3,
        _zoneinfo_mock,
        _nearestzone_mock,
        eda_doc_mockserver,
        pa_yandex_uid,
        pa_bound_uids,
        expected_status,
        patch,
        build_pa_headers,
):
    mock_get_payment_types_info(
        request_yandex_uid=pa_yandex_uid,
        available_payment_types=[],
        merchant_ids=[],
    )

    dummy_eats_mock = eda_doc_mockserver(
        preorder.eats_response_body('123', 'RUB', '10.50'),
    )
    unused.dummy(dummy_eats_mock)

    response = await web_app_client.post(
        '/4.0/payments/v1/preorder?service=eats&external_ref=123',
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid=pa_yandex_uid,
            bound_uids=pa_bound_uids,
        ),
    )
    assert response.status == expected_status


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'pa_user_agent, pa_request_application, expected_client_application',
    [
        # empty header from PA
        ('', '', None),
        # cannot parse header from PA
        ('some unknown header', 'some unknown header', None),
        (
            'ru.yandex.ytaxi/5.21.43204 '
            '(iPhone; iPhone8,4; iOS 12.1.2; Darwin)',
            'app_brand=yataxi,app_ver2=21,platform_ver1=12,app_ver1=5,'
            'app_name=iphone,app_build=release,platform_ver2=1,'
            'app_ver3=43204,platform_ver3=2',
            experiments3.ClientApplication(
                application='iphone', version='5.21.43204', brand='yataxi',
            ),
        ),
        (
            'yandex-taxi/3.131.0.119753 Android/9 (samsung; SM-G965F)',
            'app_brand=yataxi,app_build=release,app_name=android,'
            'platform_ver1=9,app_ver1=3,app_ver2=131,app_ver3=0',
            experiments3.ClientApplication(
                application='android', version='3.131.0', brand='yataxi',
            ),
        ),
    ],
)
@pytest.mark.config(PAYMENTS_EDA_LIST_PAYMENTMETHODS_FROM_CARDSTORAGE=True)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
async def test_experiments_params(
        web_app_client,
        mock_cardstorage,
        mock_get_payment_types_info,
        mock_get_order,
        _no_cards_response,
        _all_methods_in_exp3,
        _zoneinfo_mock,
        _nearestzone_mock,
        mockserver,
        patch,
        build_pa_headers,
        load_json,
        pa_user_agent,
        pa_request_application,
        expected_client_application,
        is_grocery,
        external_ref,
):
    get_order_mock = mock_get_order(is_grocery, external_ref)
    unused.dummy(get_order_mock)

    mock_get_payment_types_info(
        request_user_agent=pa_user_agent,
        available_payment_types=['card'],
        merchant_ids=[],
    )

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, client_application=None, **kwargs):
        assert client_application == expected_client_application
        return []

    response = await web_app_client.post(
        f'/4.0/payments/v1/preorder?service=eats&external_ref={external_ref}',
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid=consts.DEFAULT_YANDEX_UID,
            user_agent=pa_user_agent,
            request_application=pa_request_application,
        ),
    )
    assert response.status == 200

    # checking only ExperimentsChecker - get_payment_types_info mocked
    # in these tests, but is tested separately
    assert len(_mock_get_values.calls) == 1


@common.add_experiment(experiment_name=experiments.USE_CARD_ANTIFRAUD)
@pytest.mark.parametrize('allowed_card', ['card-x5aaa7b83fbacea65239f13f3'])
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
async def test_card_antifraud(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_card_antifraud,
        mock_get_payment_types_info,
        mock_get_order,
        load_json,
        patch,
        build_pa_headers,
        allowed_card,
        is_grocery,
        external_ref,
):
    currency = 'RUB'
    locale = 'ru-RU'
    expected_currency_text = 'rub.'
    user_ip = '1.1.1.1'
    user_agent = 'ua for card-antifraud'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        return cardstorage_payment_methods

    @mock_card_antifraud('/v1/payment/availability')
    async def card_antifraud_mock(request, **kwargs):
        assert request.headers['Accept-Language'] == locale
        assert request.headers['User-Agent'] == user_agent
        return {
            'all_payments_available': False,
            'available_cards': [{'card_id': allowed_card}],
            'disabled_reason_localized': 'disabled reason',
        }

    mock_get_payment_types_info()

    get_order_mock = mock_get_order(is_grocery, external_ref, currency)

    await _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        cardstorage_payment_methods,
        build_pa_headers,
        allowed_cards=[allowed_card],
        pa_ya_taxi_pass_flags='portal',
        user_agent=user_agent,
        disabled_reason='disabled reason',
        external_ref=external_ref,
    )

    assert cardstorage_mock.times_called == 1
    assert card_antifraud_mock.times_called == 1
    assert get_order_mock.times_called == 1


@common.add_experiment(experiment_name=experiments.USE_CARD_ANTIFRAUD)
@common.add_experiment(experiment_name=experiments.USE_CARD_FILTER_EXP)
@pytest.mark.parametrize(
    'card_filter_status, use_card_filter', [(500, False), (200, True)],
)
@pytest.mark.parametrize('yandex_login_id', [None, 'foo'])
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
async def test_card_filter(
        web_app,
        web_app_client,
        mock_card_antifraud,
        mock_cardstorage,
        mock_get_payment_types_info,
        mock_get_order,
        mock_card_filter,
        mockserver,
        load_json,
        build_pa_headers,
        card_filter_status,
        use_card_filter,
        yandex_login_id,
        is_grocery,
        external_ref,
):
    currency = 'RUB'
    locale = 'ru-RU'
    expected_currency_text = 'rub.'
    user_ip = '1.1.1.1'
    user_agent = 'UA'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        return cardstorage_payment_methods

    @mock_card_antifraud('/v1/payment/availability')
    async def card_antifraud_mock(request, **kwargs):
        # We don't need card-antifraud check if card-filter was used.
        # Return empty list of cards in that case to make sure that
        # test fails if we check card-antifraud by mistake.
        available_cards = (
            []
            if use_card_filter
            else [
                {'card_id': 'card-x5aaa7b83fbacea65239f13f3'},
                {'card_id': 'card-x5a4adedaf78dba6f9c56fee4'},
            ]
        )
        return {
            'all_payments_available': False,
            'available_cards': available_cards,
        }

    card_filter_payment_methods = load_json('card_filter_filtered_cards.json')

    @mock_card_filter('/v1/filteredcards')
    async def card_filter_mock(request, **kwargs):
        expected_request = {
            'yandex_uid': consts.DEFAULT_YANDEX_UID,
            'user_id': consts.DEFAULT_USER_ID,
            'cache_preferred': False,
            'service_type': 'card',
            'show_unverified': False,
            'show_unbound': False,
            'service': 'eats',
        }
        if yandex_login_id:
            expected_request['yandex_login_id'] = yandex_login_id

        assert request.json == expected_request
        if card_filter_status != 200:
            return mockserver.make_response(
                status=card_filter_status, json={'message': 'error'},
            )
        return card_filter_payment_methods

    mock_get_payment_types_info()

    get_order_mock = mock_get_order(is_grocery, external_ref, currency)

    card_payment_methods = (
        card_filter_payment_methods
        if use_card_filter
        else cardstorage_payment_methods
    )

    cards_from = (
        CardSource.CARD_FILTER if use_card_filter else CardSource.CARDSTORAGE
    )

    await _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        card_payment_methods,
        build_pa_headers,
        pa_ya_taxi_pass_flags='portal',
        yandex_login_id=yandex_login_id,
        user_agent=user_agent,
        cards_from=cards_from,
        external_ref=external_ref,
    )

    assert card_filter_mock.times_called == 1
    assert cardstorage_mock.times_called == int(not use_card_filter)
    assert card_antifraud_mock.times_called == 1
    assert get_order_mock.times_called == 1


@common.add_experiment(experiment_name=experiments.USE_CARD_ANTIFRAUD)
@common.add_experiment(experiment_name=experiments.USE_CARD_FILTER_EXP)
@common.add_experiment(experiment_name=experiments.PERSONAL_WALLET_ENABLED_EXP)
@common.add_experiment(
    experiment_name=experiments.USE_WALLETS_FROM_CARD_FILTER_EXP,
)
@pytest.mark.parametrize(
    'card_filter_status, use_card_filter', [(500, False), (200, True)],
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
async def test_wallets_from_cardfilter(
        web_app,
        web_app_client,
        mock_get_order,
        mock_card_filter,
        mock_get_payment_types_info,
        mockserver,
        build_pa_headers,
        load_json,
        card_filter_status,
        use_card_filter,
        is_grocery,
        external_ref,
):
    @mockserver.json_handler('/personal_wallet/v1/available-accounts')
    def personal_wallet_mock(request):
        return mockserver.make_response(
            status=200,
            json=load_json('available_accounts_with_complements.json'),
        )

    @mock_card_filter('/v1/filteredcards')
    async def card_filter_mock(request, **kwargs):
        if card_filter_status != 200:
            return mockserver.make_response(
                status=card_filter_status, json={'message': 'error'},
            )
        return load_json('card_filter_filtered_cards_with_wallets.json')

    mock_get_payment_types_info(
        available_payment_types=['card', 'personal_wallet'],
    )
    mock_get_order(is_grocery, external_ref, currency='RUB')

    response = await web_app_client.post(
        f'/4.0/payments/v1/preorder?service=eats&external_ref={external_ref}',
        headers=build_pa_headers('1.1.1.1', 'ru-RU'),
    )
    assert response.status == 200
    body = await response.json()

    wallets = [
        pm for pm in body['payment_methods'] if pm['type'] == 'personal_wallet'
    ]

    assert len(wallets) == 1
    assert personal_wallet_mock.times_called == 0 if use_card_filter else 1
    assert card_filter_mock.times_called == 1


@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
@common.add_experiment(
    experiment_name=experiments.SERVICE_TOKEN_EXP,
    experiment_value={'token': 'dummy-token'},
)
async def test_service_token(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_order,
        mock_get_payment_types_info,
        load_json,
        patch,
        build_pa_headers,
        is_grocery,
        external_ref,
):
    currency = 'RUB'
    locale = 'ru-RU'
    expected_currency_text = 'rub.'
    user_ip = '1.1.1.1'

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def cardstorage_mock(request, **kwargs):
        return cardstorage_payment_methods

    mock_get_payment_types_info()
    mock_get_order(is_grocery, external_ref, currency)

    await _check_preorder(
        web_app_client,
        user_ip,
        locale,
        currency,
        expected_currency_text,
        cardstorage_payment_methods,
        build_pa_headers,
        external_ref=external_ref,
        service_token='dummy-token',
    )

    assert cardstorage_mock.times_called == 1


@pytest.fixture
def _no_cards_response(mockserver):
    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def handler(request):
        return {'available_cards': []}

    return handler


@pytest.fixture
def _all_methods_in_exp3(mockserver, load_json):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def handler(request):
        return load_json('exp3_all_methods_enabled.json')

    return handler


@pytest.fixture
def _zoneinfo_mock(mockserver, load_json):
    @mockserver.json_handler('/taxi-protocol/3.0/zoneinfo')
    def handler(request):
        return load_json('zoneinfo_response.json')

    return handler


@pytest.fixture
def _nearestzone_mock(mockserver, load_json):
    @mockserver.json_handler('/taxi-protocol/3.0/nearestzone')
    def handler(request):
        return load_json('nearestzone_response.json')

    return handler
