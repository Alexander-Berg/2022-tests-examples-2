# pylint: disable=invalid-name
import pytest

from tests_plus.utils import common
from tests_plus.utils import requests


@pytest.mark.translations(
    client_messages={
        'taxiontheway.cashback.title.with_cashback': {'en': 'cashback:'},
        'taxiontheway.notifications.cashback.text': {
            'en': (
                'For this ride, you ll get <b>%(cashback_as_str)s points</b> '
            ),
        },
    },
)
@pytest.mark.parametrize(
    'expected_cashback',
    [
        pytest.param('78'),  # 78 = 10 + (353 - 10) * 0.2 and floor
        pytest.param(
            '79',  # same, but ceil
            marks=(pytest.mark.config(MARKETING_CASHBACK_CEIL_ENABLED=True)),
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_v2_totw_cashback_happy_path(web_plus, expected_cashback):
    result = await web_plus.totw_info.request(
        order_cost=353,
        agent_cashback=10,
        marketing_cashback=68.6,
        pass_flags=['cashback-plus', 'ya-plus'],
    ).perform()
    assert result.status_code == 200
    content = result.json()
    # cashback = 10 + (353 - 10) * 0.2
    assert content == {
        'promoted_subscriptions': [],
        'cost_message_details': {
            'cashback': {
                'value_as_str': expected_cashback,
                'title': 'cashback:',
            },
            'cost_breakdown': [],
        },
        'notifications': {
            'cashback': {
                'text': (
                    'For this ride, you ll get <b>'
                    + expected_cashback
                    + ' points</b> '
                ),
                'type': 'cashback',
            },
        },
    }


@pytest.mark.translations(
    client_messages={
        'taxiontheway.cashback.title.without_cashback': {
            'en': 'without cashback',
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_v2_totw_without_cashback_happy_path(web_plus):
    result = await web_plus.totw_info.request(
        order_id='order_without_rate', order_cost=350,
    ).perform()
    assert result.status_code == 200
    content = result.json()
    assert content == {
        'promoted_subscriptions': [],
        'cost_message_details': {
            'cashback': {
                'title': 'without cashback',
                'action': {'type': 'buy_plus'},
            },
            'cost_breakdown': [],
        },
    }


@pytest.mark.translations(
    client_messages={
        'taxiontheway.cashback.title.without_cashback': {
            'en': 'without cashback',
        },
        'taxiontheway.cashback.attributed_text.without_cashback': {
            'en': (
                '<plus_taxi_on_the_way_without_cashback>'
                'without cashback'
                '</plus_taxi_on_the_way_without_cashback>'
            ),
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_v2_totw_without_cashback_attributed_text(web_plus, taxi_config):
    taxi_config.set(
        EXTENDED_TEMPLATE_STYLES_MAP={
            'plus_taxi_on_the_way_without_cashback': {
                'color': '#FA6A3C',
                'font_size': 12,
                'font_style': 'normal',
                'font_weight': 'medium',
            },
        },
    )

    await web_plus.totw_info.client.invalidate_caches()

    result = await web_plus.totw_info.request(
        order_id='order_without_cashback', order_cost=350,
    ).perform()
    assert result.status_code == 200

    content = result.json()

    assert content == {
        'promoted_subscriptions': [],
        'cost_message_details': {
            'cashback': {
                'title': 'without cashback',
                'action': {'type': 'buy_plus'},
                'attributed_text': {
                    'items': [
                        {
                            'type': 'text',
                            'text': 'without cashback',
                            'color': '#FA6A3C',
                            'font_size': 12,
                            'font_style': 'normal',
                            'font_weight': 'medium',
                        },
                    ],
                },
            },
            'cost_breakdown': [],
        },
    }


@pytest.mark.translations(
    client_messages={
        'taxiontheway.cashback.attributed_text.cashback_title': {
            'en': (
                '<plus_taxi_on_the_way_cashback_title>'
                'Cashback:'
                '</plus_taxi_on_the_way_cashback_title>'
            ),
        },
        'taxiontheway.cashback.attributed_text.cashback_sum': {
            'en': (
                '<plus_taxi_on_the_way_cashback_sum>'
                '%(cashback_value)s points'
                '</plus_taxi_on_the_way_cashback_sum>'
            ),
        },
        'taxiontheway.cashback.attributed_text.cashback_icon': {
            'en': (
                '<plus_taxi_on_the_way_cashback_icon>'
                '<img src="plus_icon" />'
                '</plus_taxi_on_the_way_cashback_icon>'
            ),
        },
        'taxiontheway.cashback.title.with_cashback': {'en': 'cashback:'},
        'taxiontheway.notifications.cashback.text': {
            'en': (
                'For this ride, you ll get <b>'
                '%(cashback_as_str)s points</b> '
            ),
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_v2_totw_with_cashback_attributed_text(web_plus, taxi_config):
    taxi_config.set(
        EXTENDED_TEMPLATE_STYLES_MAP={
            'plus_taxi_on_the_way_cashback_title': {
                'color': '#FA6A3C',
                'font_size': 12,
                'font_style': 'normal',
                'font_weight': 'medium',
            },
            'plus_taxi_on_the_way_cashback_sum': {
                'meta_color': 'plus',
                'font_size': 14,
                'font_style': 'normal',
                'font_weight': 'medium',
            },
            'plus_taxi_on_the_way_cashback_icon': {
                'meta_color': 'plus',
                'vertical_alignment': 'baseline',
                'width': 10,
            },
        },
    )

    await web_plus.totw_info.client.invalidate_caches()

    result = await web_plus.totw_info.request(
        order_id='order_with_cashback',
        order_cost=353,
        agent_cashback=10,
        marketing_cashback=68.6,
        pass_flags=['cashback-plus', 'ya-plus'],
    ).perform()
    assert result.status_code == 200

    content = result.json()

    assert content == {
        'promoted_subscriptions': [],
        'cost_message_details': {
            'cashback': {
                'value_as_str': '78',
                'title': 'cashback:',
                'attributed_text': {
                    'items': [
                        {
                            'type': 'text',
                            'text': 'Cashback:',
                            'color': '#FA6A3C',
                            'font_size': 12,
                            'font_style': 'normal',
                            'font_weight': 'medium',
                        },
                        {
                            'image_tag': 'plus_icon',
                            'type': 'image',
                            'meta_color': 'plus',
                            'vertical_alignment': 'baseline',
                            'width': 10,
                        },
                        {
                            'type': 'text',
                            'text': '78',
                            'meta_color': 'plus',
                            'font_size': 14,
                            'font_style': 'normal',
                            'font_weight': 'medium',
                        },
                        {
                            'type': 'text',
                            'text': ' points',
                            'meta_color': 'plus',
                            'font_size': 14,
                            'font_style': 'normal',
                            'font_weight': 'medium',
                        },
                    ],
                },
            },
            'cost_breakdown': [],
        },
        'notifications': {
            'cashback': {
                'text': (
                    'For this ride, you ll get <b>' + '78' + ' points</b> '
                ),
                'type': 'cashback',
            },
        },
    }


@pytest.mark.parametrize(
    'payment_status, has_result',
    [
        pytest.param('init', True),
        pytest.param('held', True),
        pytest.param('holding', False),
        pytest.param('cleared', True),
        pytest.param('clearing', False),
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.cashback.notifications.yandex_card.title': {
            'en': 'Недостаточно средств на карте',
        },
        'taxiontheway.cashback.notifications.yandex_card.subtitle': {
            'en': 'Чтобы оплатить поездку, пополните вашу яндекс.карту',
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_informer_yandex_card.json')
async def test_v2_totw_notifications_yandex_card(
        web_plus, taxi_config, mockserver, payment_status, has_result,
):
    @mockserver.json_handler('/transactions/v2/invoice/retrieve')
    def _mock_v2_invoice_retrieve(request):
        order_id = request.json['id']

        assert order_id == 'order_informer_yandex_card'

        return {
            'id': order_id,
            'invoice_due': '2019-10-30T16:40:53.966+00:00',
            'created': '2019-10-30T16:40:53.966+00:00',
            'currency': 'RUB',
            'status': payment_status,
            'operation_info': {},
            'sum_to_pay': [
                {
                    'payment_type': 'yandex_card',
                    'items': [{'item_id': 'ride', 'amount': '300'}],
                },
                {
                    'payment_type': 'personal_wallet',
                    'items': [{'item_id': 'ride', 'amount': '100'}],
                },
            ],
            'held': [
                {
                    'payment_type': 'yandex_card',
                    'items': [{'item_id': 'ride', 'amount': '200'}],
                },
                {
                    'payment_type': 'personal_wallet',
                    'items': [{'item_id': 'ride', 'amount': '100'}],
                },
            ],
            'cleared': [],
            'debt': [],
            'transactions': [],
            'payment_types': [],
            'yandex_uid': 'some_yandex_uid',
        }

    await web_plus.totw_info.client.invalidate_caches()

    result = await web_plus.totw_info.request(
        order_id='order_informer_yandex_card',
        payment={
            'type': 'yandex_card',
            'payment_method_id': 'payment_method_id',
        },
        kind='transporting',
        cost_breakdown=[
            {'type': 'yandex_card', 'amount': 300},
            {'type': 'personal_wallet', 'amount': 100},
        ],
        request_application='app_name=iphone,app_ver1=650,app_ver2=22',
        fixed_price=400,
    ).perform()
    assert result.status_code == 200

    content = result.json()

    if has_result:
        assert content == {
            'cost_message_details': {'cost_breakdown': []},
            'promoted_subscriptions': [],
            'notifications': {
                'yandex_card': {
                    'type': 'payment_informer',
                    'translations': {
                        'title': 'Недостаточно средств на карте',
                        'subtitle': (
                            'Чтобы оплатить поездку, '
                            'пополните вашу яндекс.карту'
                        ),
                    },
                    'informer': {
                        'title': 'title',
                        'subtitle': 'subtitle',
                        'icon_tag': 'informer_yandex_card',
                        'need_send_replenish_amount': True,
                        'conditions': {
                            'required_card_balance': {
                                'amount': 100,
                                'currency': 'RUB',
                            },
                        },
                    },
                },
            },
        }
    else:
        assert content == {
            'cost_message_details': {'cost_breakdown': []},
            'promoted_subscriptions': [],
        }


@pytest.mark.translations(
    client_messages={
        'taxiontheway.cashback.attributed_text.increased_cashback_title': {
            'en': (
                '<plus_taxi_on_the_way_increased_cashback_title>'
                'Increased cashback:'
                '</plus_taxi_on_the_way_increased_cashback_title>'
            ),
        },
        'taxiontheway.cashback.attributed_text.increased_cashback_sum': {
            'en': (
                '<plus_taxi_on_the_way_increased_cashback_sum>'
                '%(cashback_value)s points'
                '</plus_taxi_on_the_way_increased_cashback_sum>'
            ),
        },
        'taxiontheway.cashback.attributed_text.increased_cashback_icon': {
            'en': (
                '<plus_taxi_on_the_way_increased_cashback_icon>'
                '<img src="increased_plus_icon"></img>'
                '</plus_taxi_on_the_way_increased_cashback_icon>'
            ),
        },
        'taxiontheway.cashback.title.with_cashback': {'en': 'cashback:'},
        'taxiontheway.notifications.cashback.text': {
            'en': (
                'For this ride, you ll get <b>'
                '%(cashback_as_str)s points</b> '
            ),
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_v2_totw_with_increased_cashback_attributed_text(
        web_plus, taxi_config,
):
    taxi_config.set(
        EXTENDED_TEMPLATE_STYLES_MAP={
            'plus_taxi_on_the_way_increased_cashback_title': {
                'color': '#FA6A3C',
                'font_size': 12,
                'font_style': 'normal',
                'font_weight': 'medium',
            },
            'plus_taxi_on_the_way_increased_cashback_sum': {
                'meta_color': 'plus_increased',
                'font_size': 14,
                'font_style': 'normal',
                'font_weight': 'medium',
            },
            'plus_taxi_on_the_way_increased_cashback_icon': {
                'meta_color': 'plus_increased',
                'vertical_alignment': 'baseline',
                'width': 10,
            },
        },
    )

    await web_plus.totw_info.client.invalidate_caches()

    result = await web_plus.totw_info.request(
        order_id='order_with_cashback',
        order_cost=353,
        agent_cashback=10,
        marketing_cashback=68.6,
        pass_flags=['cashback-plus', 'ya-plus'],
        cashback_by_sponsor={'fintech': '0.08', 'portal': '0.05'},
    ).perform()
    assert result.status_code == 200

    content = result.json()

    assert content == {
        'promoted_subscriptions': [],
        'cost_message_details': {
            'cashback': {
                'value_as_str': '78',
                'title': 'cashback:',
                'attributed_text': {
                    'items': [
                        {
                            'type': 'text',
                            'text': 'Increased cashback:',
                            'color': '#FA6A3C',
                            'font_size': 12,
                            'font_style': 'normal',
                            'font_weight': 'medium',
                        },
                        {
                            'image_tag': 'increased_plus_icon',
                            'type': 'image',
                            'vertical_alignment': 'baseline',
                            'meta_color': 'plus_increased',
                            'width': 10,
                        },
                        {
                            'type': 'text',
                            'text': '78',
                            'meta_color': 'plus_increased',
                            'font_size': 14,
                            'font_style': 'normal',
                            'font_weight': 'medium',
                        },
                        {
                            'type': 'text',
                            'text': ' points',
                            'meta_color': 'plus_increased',
                            'font_size': 14,
                            'font_style': 'normal',
                            'font_weight': 'medium',
                        },
                    ],
                },
            },
            'cost_breakdown': [],
        },
        'notifications': {
            'cashback': {
                'text': (
                    'For this ride, you ll get <b>' + '78' + ' points</b> '
                ),
                'type': 'cashback',
            },
        },
    }


@pytest.mark.translations(
    client_messages={
        'taxiontheway.cost_breakdown.paid_by_wallet.name': {
            'en': 'will be paid by Plus',
        },
        'taxiontheway.cost_breakdown.paid_by_card.name': {
            'en': 'Will be paid by card',
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_v2_totw_complements_happy_path(web_plus, mock_order_core):
    mock_order_core.order_fields.balance(45)
    result = await web_plus.totw_info.request(
        order_cost=350,
        personal_wallet=True,
        pass_flags=['cashback-plus', 'ya-plus'],
    ).perform()
    assert result.status_code == 200
    content = result.json()
    assert content == {
        'promoted_subscriptions': [],
        'cost_message_details': {
            'cost_breakdown': [
                {
                    'display_amount': '45',
                    'display_name': 'will be paid by Plus',
                },
                {
                    'display_amount': '305 $SIGN$$CURRENCY$',
                    'display_name': 'Will be paid by card',
                },
            ],
        },
    }


@pytest.mark.translations(
    client_messages={
        'plus.totw.possible_cashback.text': {'en': 'cashback', 'ru': 'баллы'},
    },
)
@pytest.mark.experiments3(filename='experiments3_plus_info.json')
@pytest.mark.parametrize(
    'is_possible_cashback, possible_cashback, pass_flags',
    [
        pytest.param(True, 100, ['cashback-plus', 'ya-plus']),
        pytest.param(False, 100, ['cashback-plus']),
        pytest.param(None, 100, ['cashback-plus']),
        pytest.param(True, 100, ['cashback-plus']),
        pytest.param(True, None, ['cashback-plus', 'ya-plus']),
        pytest.param(False, 100, ['cashback-plus', 'ya-plus']),
    ],
)
async def test_v2_totw_plus_info_with_templates(
        web_plus,
        is_possible_cashback,
        possible_cashback,
        pass_flags,
        taxi_config,
):
    taxi_config.set(
        PLUS_TOTW_PURE_TEMPLATES_PREFIXES=['personal_goals', 'some_feature'],
        PLUS_TOTW_ADDITIONAL_TEMPLATES=[
            {
                'template_name': 'additional_template_name',
                'experiment_name': 'additional_template_name_enabled',
            },
            {
                'template_name': 'additional_template_name_disabled',
                'experiment_name': 'additional_template_name_disabled_enabled',
            },
        ],
    )

    await web_plus.totw_info.client.invalidate_caches()

    result = await web_plus.totw_info.request(
        order_cost=350,
        personal_wallet=True,
        pass_flags=pass_flags,
        possible_cashback=possible_cashback,
        is_possible_cashback=is_possible_cashback,
    ).perform()
    assert result.status_code == 200
    content = result.json()
    expected_content = {
        'promoted_subscriptions': [],
        'cost_message_details': {'cost_breakdown': []},
        'plus_info': {
            'templates': [
                {'key': 'personal_goals_default_order', 'value': ''},
                {'key': 'some_feature_default_order', 'value': ''},
                {'key': 'additional_template_name', 'value': ''},
            ],
        },
    }
    if possible_cashback:
        if is_possible_cashback is True:
            expected_content['plus_info']['templates'].extend(
                [
                    {
                        'key': (
                            '$$TOTW_POSSIBLE_CASHBACK_AFTER_PURCHASE_VALUE$$'
                        ),
                        'value': '100',
                    },
                    {
                        'key': (
                            '$$TOTW_POSSIBLE_CASHBACK_AFTER_PURCHASE_TEXT$$'
                        ),
                        'value': 'cashback',
                    },
                ],
            )
        elif 'ya-plus' not in pass_flags:
            expected_content['plus_info']['templates'].extend(
                [
                    {
                        'key': '$$TOTW_POSSIBLE_CASHBACK_VALUE$$',
                        'value': '100',
                    },
                    {
                        'key': '$$TOTW_POSSIBLE_CASHBACK_TEXT$$',
                        'value': 'cashback',
                    },
                    {
                        'key': '$$CATCHING_UP_CASHBACK_PURCHASE_PARAMETERS$$',
                        'value': (
                            '%3Fevent%3Dcatching_up_cashback%26order_'
                            'id%3Ddefault_order'
                        ),
                    },
                ],
            )
    assert content == expected_content


@pytest.mark.config(PLUS_SERVICE_ENABLED=False)
async def test_v2_totw_service_disabled(web_plus):
    result = await web_plus.totw_info.request().perform()
    assert result.status_code == 429


@pytest.mark.parametrize('status', [400, 404, 500])
async def test_v2_totw_order_core_fail(web_plus, mock_order_core, status):
    mock_order_core.order_fields.http_status = status
    result = await web_plus.totw_info.request().perform()
    assert result.status_code == 200
    content = result.json()
    assert content == {
        'promoted_subscriptions': [],
        'cost_message_details': {'cost_breakdown': []},
    }


@pytest.mark.translations(
    client_messages={
        'taxiontheway.cashback.title.with_cashback': {'en': 'cashback:'},
        'taxiontheway.notifications.cashback.text': {
            'en': (
                'For this ride, you ll get <b>%(cashback_as_str)s points</b> '
            ),
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_v2_totw_rounding_cashback_byl(taxi_plus):
    class CustomTotwInfo(requests.TotwInfo):
        def request(
                self,
                order_id='default_order',
                order_cost=353,
                agent_cashback=10,
                marketing_cashback=68.6,
                kind='final_cost',
                order_status='complete',
                category='econom',
                currency='BYN',
                personal_wallet=None,
                pass_flags=None,
                possible_cashback=None,
                is_possible_cashback=None,
                cashback_by_sponsor=None,
                payment=None,
                cost_breakdown=None,
                fixed_price=None,
                request_application=None,
        ):
            complements = None
            current_prices = {
                'user_total_price': order_cost,
                'kind': kind,
                'cashback_price': agent_cashback,
                'discount_cashback': marketing_cashback,
            }
            pass_flags = ['cashback-plus', 'ya-plus']
            return (
                common.HttpRequest(self.client.post)
                .path('/internal/v2/taxiontheway/info')
                .params(order_cost=order_cost)
                .headers(yandex_uid='123456')
                .headers(remote_ip='46.56.239.62')  # Minsk ip
                .headers(request_language='en')
                .headers(pass_flags=','.join(pass_flags))
                .body(
                    order_id=order_id,
                    order_status=order_status,
                    currency=currency,
                    category=category,
                    current_prices=current_prices,
                    complements=complements,
                    is_possible_cashback=is_possible_cashback,
                    payment=payment,
                    fixed_price=fixed_price,
                )
            )

    client = CustomTotwInfo(taxi_plus)

    result = await client.request().perform()
    assert result.status_code == 200

    content = result.json()
    # cashback = 10 + (353 - 10) * 0.2 = 78.6
    cashback = content.get('cost_message_details').get('cashback')
    cashback_notifications_text = (
        content.get('notifications').get('cashback').get('text')
    )
    assert cashback == {'value_as_str': '78.6', 'title': 'cashback:'}
    assert (
        cashback_notifications_text
        == 'For this ride, you ll get <b>78.6 points</b> '
    )
