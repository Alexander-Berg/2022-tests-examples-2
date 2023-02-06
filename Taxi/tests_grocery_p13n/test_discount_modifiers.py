# pylint: disable=too-many-lines

import pytest

from tests_grocery_p13n import common
from tests_grocery_p13n import depot
from tests_grocery_p13n import experiments
from tests_grocery_p13n import tests_headers


# Если сервис скидок отдает 500, то p13n:/discount-modifiers отвечает 400.
async def test_p13n_returns_400_on_grocery_discounts_500(
        taxi_grocery_p13n, mock_grocery_discounts_500,
):
    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [
                {
                    'product_id': 'test_product_id',
                    'category_ids': ['test_category_i'],
                },
            ],
        },
    )
    assert response.status_code == 400


# Скидки на меню от сервиса скидок преобразуются в модификаторы цены.
@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.PAYMENT_METHOD_DISCOUNT_EXPERIMENT
async def test_menu_discounts_are_transformed_to_item_modifiers(
        taxi_grocery_p13n, grocery_discounts,
):
    first_product_id = 'product-one'
    menu_percent = '10'

    second_product_id = 'product-two'
    cashback_absolute = '30'

    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value=menu_percent,
        hierarchy_name='menu_discounts',
    )

    grocery_discounts.add_cashback_discount(
        product_id=second_product_id,
        value_type='absolute',
        value=cashback_absolute,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': first_product_id, 'category_ids': []},
                {'product_id': second_product_id, 'category_ids': []},
            ],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_discounts'},
                'product_id': first_product_id,
                'rule': {'discount_percent': menu_percent},
                'type': 'item_discount',
            },
            {
                'meta': {'hierarchy_name': 'menu_cashback'},
                'product_id': second_product_id,
                'rule': {'gain_value': cashback_absolute},
                'type': 'item_discount',
            },
        ],
    }


# Модификаторы корзины возвращаются, если передать соответствующий параметр.
async def test_specify_appropriate_purpose_to_get_cart_modifiers(
        taxi_grocery_p13n, grocery_discounts,
):
    first_product_id = 'product-one'
    menu_percent = '10'

    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value=menu_percent,
        hierarchy_name='menu_discounts',
    )

    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
        {
            'discount': {'value': '20', 'value_type': 'fraction'},
            'from_cost': '150',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=first_product_id, table_items=table_items,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [{'product_id': first_product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_discounts'},
                'product_id': first_product_id,
                'rule': {'discount_percent': menu_percent},
                'type': 'item_discount',
            },
            {
                'meta': {'hierarchy_name': 'cart_discounts'},
                'min_cart_price': '0',
                'steps': [
                    {'rule': {'discount_value': '10'}, 'threshold': '75'},
                    {'rule': {'discount_percent': '20'}, 'threshold': '150'},
                ],
                'type': 'cart_discount',
            },
        ],
    }


# Модификаторы корзины не возвращаются для каталога.
async def test_cart_modifiers_are_dropped_for_catalog(
        taxi_grocery_p13n, grocery_discounts,
):
    first_product_id = 'product-one'
    menu_percent = '10'

    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value=menu_percent,
        hierarchy_name='menu_discounts',
    )

    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
        {
            'discount': {'value': '20', 'value_type': 'fraction'},
            'from_cost': '150',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=first_product_id, table_items=table_items,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': first_product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_discounts'},
                'product_id': first_product_id,
                'rule': {'discount_percent': menu_percent},
                'type': 'item_discount',
            },
        ],
    }


# Скидки на метод оплаты возвращаются только если передать соответствующий
# параметр запроса.
@experiments.PAYMENT_METHOD_DISCOUNT_EXPERIMENT
@pytest.mark.parametrize(
    'payment_method',
    [
        pytest.param(None, id='not payment method'),
        pytest.param({'type': 'card', 'id': '1'}, id='with payment method'),
    ],
)
async def test_specify_payment_method_to_get_payment_method_modifiers(
        taxi_grocery_p13n, grocery_discounts, payment_method,
):
    first_product_id = 'product-one'
    payment_method_percent = '20'

    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value=payment_method_percent,
        hierarchy_name='payment_method_discounts',
    )

    request_json = {
        'purpose': 'catalog',
        'depot': depot.DEPOT,
        'items': [{'product_id': first_product_id, 'category_ids': []}],
    }
    if payment_method:
        request_json['payment_method'] = {'type': 'card', 'id': '1'}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json=request_json,
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1

    payment_method_modifier = {
        'meta': {'hierarchy_name': 'payment_method_discounts'},
        'product_id': first_product_id,
        'rule': {'discount_percent': payment_method_percent},
        'type': 'payment_method_discount',
    }
    expected_modifiers = (
        [] if payment_method is None else [payment_method_modifier]
    )
    assert response.json() == {'modifiers': expected_modifiers}


async def test_modifiers_meta(taxi_grocery_p13n, grocery_discounts):
    first_product_id = 'product-one'
    payment_percent = '20'
    title = 'discount_title'
    subtitle = 'discount_subtitle'
    payment_method_subtitle = 'discount_payment_method_subtitle'
    label_color = 'discount_label_color'
    picture = 'discount_picture'
    is_price_strikethrough = True
    is_expiring = True
    discount_category = 'discount_category'

    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value=payment_percent,
        hierarchy_name='menu_discounts',
        discount_meta={
            'tanker_keys': {
                'title': title,
                'subtitle': subtitle,
                'payment_method_subtitle': payment_method_subtitle,
            },
            'is_price_strikethrough': is_price_strikethrough,
            'is_expiring': is_expiring,
            'picture': picture,
            'label_color': label_color,
            'discount_category': discount_category,
        },
    )

    request_json = {
        'purpose': 'catalog',
        'depot': depot.DEPOT,
        'items': [{'product_id': first_product_id, 'category_ids': []}],
    }

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json=request_json,
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1

    modifier = {
        'meta': {
            'title_tanker_key': title,
            'subtitle_tanker_key': subtitle,
            'payment_method_subtitle': payment_method_subtitle,
            'is_price_uncrossed': not is_price_strikethrough,
            'is_expiring': is_expiring,
            'picture': picture,
            'label_color': label_color,
            'hierarchy_name': 'menu_discounts',
            'discount_category': discount_category,
        },
        'product_id': first_product_id,
        'rule': {'discount_percent': payment_percent},
        'type': 'item_discount',
    }
    assert response.json() == {'modifiers': [modifier]}


async def test_modifiers_draft_id(taxi_grocery_p13n, grocery_discounts):
    first_product_id = 'product-one'
    menu_percent = '10'

    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value=menu_percent,
        hierarchy_name='menu_discounts',
        draft_id='draft_1',
    )
    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
        {
            'discount': {'value': '20', 'value_type': 'fraction'},
            'from_cost': '150',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=first_product_id,
        table_items=table_items,
        draft_id='draft_2',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [{'product_id': first_product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    modifiers = response.json()['modifiers']
    assert modifiers[0]['meta']['draft_id'] == 'draft_1'
    assert modifiers[1]['meta']['draft_id'] == 'draft_2'


# Проверяем что кол-во заказов пользователя отдается в g-discounts
# А также, что отдается максимум
@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_p13n_discount_modifiers_response': {
            'tag': 'total_orders_count',
            'payment_id_divisor': 3,
        },
    },
)
@pytest.mark.parametrize('purpose', ['catalog', 'cart'])
@pytest.mark.parametrize(
    'user_orders_count,appmetrica_device_id_usage_count,'
    'eats_id_usage_count,payment_id_usage_count,personal_phone_id_usage_count',
    [
        (2, 2, 2, 6, 2),
        (2, 1, 1, 5, 1),
        (1, 2, 1, 1, None),
        (1, 1, 2, 4, None),
        (1, 1, 1, 6, None),
        (2, None, None, None, None),
        (None, 2, None, None, None),
        (None, None, 2, None, None),
        (None, None, None, 6, None),
        (None, None, None, None, 2),
        (1, 1, 1, 1, 2),
    ],
)
async def test_orders_count_to_discounts(
        taxi_grocery_p13n,
        mockserver,
        purpose,
        grocery_marketing,
        user_orders_count,
        appmetrica_device_id_usage_count,
        eats_id_usage_count,
        payment_id_usage_count,
        personal_phone_id_usage_count,
):
    payment_id = '1'
    if user_orders_count is not None:
        grocery_marketing.add_user_tag(
            'total_orders_count',
            user_orders_count,
            user_id=tests_headers.HEADER_YANDEX_UID,
        )
    if appmetrica_device_id_usage_count is not None:
        grocery_marketing.add_device_tag(
            'total_orders_count',
            appmetrica_device_id_usage_count,
            device_id=tests_headers.APPMETRICA_DEVICE_ID,
        )
    if payment_id_usage_count is not None:
        grocery_marketing.add_payment_id_tag(
            'total_orders_count',
            payment_id_usage_count,
            payment_id=payment_id,
        )
    if eats_id_usage_count is not None:
        grocery_marketing.add_eats_id_tag(
            'total_orders_count',
            eats_id_usage_count,
            eats_id=tests_headers.HEADER_EATS_ID,
        )
    if personal_phone_id_usage_count is not None:
        grocery_marketing.add_phone_id_tag(
            'total_orders_count',
            personal_phone_id_usage_count,
            phone_id=tests_headers.PERSONAL_PHONE_ID,
        )

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        assert request.json['common_conditions']['orders_counts'][0] == {
            'orders_count': 2,
            'payment_method': 'All',
            'application_name': 'All',
        }
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': purpose,
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_id', 'category_ids': []}],
            'payment_method': {'type': 'card', 'id': payment_id},
        },
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1
    assert grocery_marketing.retrieve_v2_times_called == 1


# Кол-во заказов пользователя отдается в g-discounts
# Когда количество заказов передано - не ходим в g-marketing
@pytest.mark.parametrize('purpose', ['catalog', 'cart'])
async def test_body_orders_count_to_discounts(
        taxi_grocery_p13n, mockserver, purpose, grocery_marketing,
):
    orders_count = 2

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        assert request.json['common_conditions']['orders_counts'][0] == {
            'orders_count': orders_count,
            'payment_method': 'All',
            'application_name': 'All',
        }
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': purpose,
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_id', 'category_ids': []}],
            'payment_method': {'type': 'card', 'id': '1'},
            'orders_count': orders_count,
        },
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1
    assert grocery_marketing.retrieve_v2_times_called == 0


@pytest.mark.parametrize(
    'grocery_discounts_surge_enabled',
    [
        pytest.param(
            False,
            marks=[experiments.GROCERY_DISCOUNTS_SURGE_DISABLED],
            id='grocery_discounts_surge_disabled',
        ),
        pytest.param(
            True,
            marks=[experiments.GROCERY_DISCOUNTS_SURGE_ENABLED],
            id='grocery_discounts_surge_enabled',
        ),
    ],
)
@pytest.mark.parametrize('purpose', ['catalog', 'cart'])
@pytest.mark.parametrize('has_surge', [True, False, None])
async def test_grocery_discounts_receives_surge(
        mockserver,
        taxi_grocery_p13n,
        purpose,
        has_surge,
        grocery_discounts_surge_enabled,
):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        if not grocery_discounts_surge_enabled or has_surge is None:
            assert 'has_surge' not in request.json['common_conditions']
        else:
            assert request.json['common_conditions']['has_surge'] == has_surge
        return {'match_results': []}

    request_body = {
        'purpose': purpose,
        'depot': depot.DEPOT,
        'items': [{'product_id': 'test_id', 'category_ids': []}],
    }
    if has_surge is not None:
        request_body['has_surge'] = has_surge

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json=request_body,
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1


@pytest.mark.parametrize('purpose', ['catalog', 'cart'])
async def test_grocery_marketing_error(taxi_grocery_p13n, mockserver, purpose):
    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def mock_grocery_marketing(request):
        return mockserver.make_response(
            json={'code': 400, 'message': 'error'}, status='400',
        )

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        assert 'orders_counts' not in request.json['common_conditions']
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': purpose,
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_id', 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1
    assert mock_grocery_marketing.times_called == 1


# Проверяем что в g-discounts отдается 0 заказов
# если пользователь не авторизован
async def test_orders_count_with_no_yuid(taxi_grocery_p13n, mockserver):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        assert request.json['common_conditions']['orders_counts'][0] == {
            'orders_count': 0,
            'payment_method': 'All',
            'application_name': 'All',
        }
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_id', 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1


# Протаскивает теги пользователя и товаролавки в скидки
@pytest.mark.parametrize('purpose', ['catalog', 'cart'])
async def test_modifiers_user_tags(
        taxi_grocery_p13n, mockserver, grocery_tags, purpose,
):
    personal_phone_id = 'test_phone_id'
    tags = ['tag_1', 'tag_2']
    store_item_tags = ['store_item_tag_1', 'store_item_tag_2']
    product_id = 'test_id'
    grocery_tags.add_tags(personal_phone_id=personal_phone_id, tags=tags)

    store_item_id = '{}_{}'.format(depot.DEPOT['depot_id'], product_id)
    grocery_tags.add_store_item_id_tags(
        store_item_id=store_item_id, tags=store_item_tags,
    )

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        assert common.get_tags_from_match_request(request.json) == tags
        assert common.get_product_tags_from_request(request.json) == [
            (product_id, store_item_tags),
        ]
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}'},
        json={
            'purpose': purpose,
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1


# Возвращается только одна скидка на корзину
@pytest.mark.config(GROCERY_P13N_MATCH_DISCOUNTS_LIMIT=1)
async def test_cart_modifier_is_unique(taxi_grocery_p13n, grocery_discounts):
    first_product_id = 'product-one'
    second_product_id = 'product-two'

    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
        {
            'discount': {'value': '20', 'value_type': 'fraction'},
            'from_cost': '150',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=first_product_id, table_items=table_items,
    )

    grocery_discounts.add_cart_money_discount(
        product_id=second_product_id, table_items=table_items,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': first_product_id, 'category_ids': []},
                {'product_id': second_product_id, 'category_ids': []},
            ],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 2
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'cart_discounts'},
                'min_cart_price': '0',
                'steps': [
                    {'rule': {'discount_value': '10'}, 'threshold': '75'},
                    {'rule': {'discount_percent': '20'}, 'threshold': '150'},
                ],
                'type': 'cart_discount',
            },
        ],
    }


@pytest.mark.parametrize(
    'number_discounts_request',
    [
        pytest.param(
            1,
            id='1_request',
            marks=[pytest.mark.config(GROCERY_P13N_MATCH_DISCOUNTS_LIMIT=2)],
        ),
        pytest.param(
            2,
            id='2_request',
            marks=[pytest.mark.config(GROCERY_P13N_MATCH_DISCOUNTS_LIMIT=1)],
        ),
    ],
)
async def test_cart_modifier_filtered_if_different(
        taxi_grocery_p13n, grocery_discounts, number_discounts_request,
):
    first_product_id = 'product-one'
    second_product_id = 'product-two'
    table_items_1 = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
    ]
    table_items_2 = [
        {
            'discount': {'value': '15', 'value_type': 'absolute'},
            'from_cost': '75',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=first_product_id, table_items=table_items_1,
    )

    grocery_discounts.add_cart_money_discount(
        product_id=second_product_id, table_items=table_items_2,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': first_product_id, 'category_ids': []},
                {'product_id': second_product_id, 'category_ids': []},
            ],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == number_discounts_request
    assert not response.json()['modifiers']


@pytest.mark.parametrize(
    'number_discounts_request',
    [
        pytest.param(
            1,
            id='1_discount_request',
            marks=[pytest.mark.config(GROCERY_P13N_MATCH_DISCOUNTS_LIMIT=3)],
        ),
        pytest.param(
            2,
            id='2_discount_requests',
            marks=[pytest.mark.config(GROCERY_P13N_MATCH_DISCOUNTS_LIMIT=2)],
        ),
        pytest.param(
            3,
            id='3_discount_requests',
            marks=[pytest.mark.config(GROCERY_P13N_MATCH_DISCOUNTS_LIMIT=1)],
        ),
    ],
)
async def test_cart_modifier_exclusions(
        taxi_grocery_p13n, grocery_discounts, number_discounts_request,
):
    product_1 = 'product-one'
    product_2 = 'product-two'
    product_3 = 'product-three'

    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=product_1, table_items=table_items,
    )
    grocery_discounts.add_cart_money_discount(
        product_id=product_2, table_items=table_items,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': product_1, 'category_ids': []},
                {'product_id': product_2, 'category_ids': []},
                {'product_id': product_3, 'category_ids': []},
            ],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == number_discounts_request
    cart_modifier = response.json()['modifiers'][0]
    assert cart_modifier['exclusions'] == [product_3]


# Проверяем что отдается только одна скидка для скидки деньгами/продуктом
async def test_menu_discount_money_payment_unique(
        taxi_grocery_p13n, grocery_discounts,
):
    first_product_id = 'product-one'
    menu_percent = '10'

    grocery_discounts.add_bundle_discount(
        product_id=first_product_id,
        discount_value='150',
        bundle=3,
        hierarchy_name='menu_discounts',
    )

    # эта скидка не будет в выдаче
    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value=menu_percent,
        hierarchy_name='menu_discounts',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': first_product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_discounts'},
                'product_id': first_product_id,
                'rule': {
                    'payment_per_product': {'discount_percent': '150'},
                    'quantity': '3',
                },
                'type': 'item_discount',
            },
        ],
    }


# Проверяем что забираем скидку продуктом и скидку деньгами если это
# одна скидка
async def test_menu_discount_money_with_product_payment(
        taxi_grocery_p13n, grocery_discounts,
):
    first_product_id = 'product-one'

    grocery_discounts.add_complex_discount(
        product_id=first_product_id,
        bundle_discount_value='150',
        bundle=3,
        money_value_type='fraction',
        money_value='50',
        hierarchy_name='menu_discounts',
    )

    # эта скидка не будет в выдаче
    grocery_discounts.add_money_discount(
        product_id=first_product_id,
        value_type='fraction',
        value='10',
        hierarchy_name='menu_discounts',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': first_product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_discounts'},
                'product_id': first_product_id,
                'rule': {
                    'payment_per_product': {'discount_percent': '150'},
                    'quantity': '3',
                },
                'type': 'item_discount',
            },
            {
                'meta': {'hierarchy_name': 'menu_discounts'},
                'product_id': first_product_id,
                'rule': {'discount_percent': '50'},
                'type': 'item_discount',
            },
        ],
    }


# Проверяем ограничение на максимальное значение для скидки деньгами
# и начисления кэшбека
@experiments.CASHBACK_EXPERIMENT_RUSSIA
async def test_relative_discount_max_value(
        taxi_grocery_p13n, grocery_discounts,
):
    product_id_first = 'product-one'
    product_id_second = 'product-two'

    grocery_discounts.add_money_discount(
        product_id=product_id_first,
        value_type='fraction',
        value='10',
        hierarchy_name='menu_discounts',
        maximum_discount='100',
    )

    grocery_discounts.add_cashback_discount(
        product_id=product_id_second,
        value_type='fraction',
        value='10',
        maximum_discount='100',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': product_id_first, 'category_ids': []},
                {'product_id': product_id_second, 'category_ids': []},
            ],
        },
    )

    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_discounts'},
                'product_id': product_id_first,
                'rule': {'discount_percent': '10', 'maximal_value': '100'},
                'type': 'item_discount',
            },
            {
                'meta': {'hierarchy_name': 'menu_cashback'},
                'product_id': product_id_second,
                'rule': {
                    'gain_percent': '10',
                    'gain_cashback_max_value': '100',
                },
                'type': 'item_discount',
            },
        ],
    }


async def test_dynamic_discount(taxi_grocery_p13n, grocery_discounts):
    product_id_first = 'product-one'

    grocery_discounts.add_money_discount(
        product_id=product_id_first,
        value_type='fraction',
        value='10',
        hierarchy_name='dynamic_discounts',
        maximum_discount='100',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id_first, 'category_ids': []}],
        },
    )
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'dynamic_discounts'},
                'product_id': product_id_first,
                'rule': {'discount_percent': '10', 'maximal_value': '100'},
                'type': 'item_discount',
            },
        ],
    }


# проверяем что работает получение кэшбека на корзину
# с вкл экспериментом и выключенным
@pytest.mark.parametrize(
    'is_cashback_on',
    [
        pytest.param(
            True,
            id='cashback_on',
            marks=[experiments.CASHBACK_EXPERIMENT_RUSSIA],
        ),
        pytest.param(False, id='cashback_off', marks=[]),
    ],
)
async def test_cashback_cart_gain(
        taxi_grocery_p13n, grocery_discounts, is_cashback_on,
):
    first_product_id = 'product-one'
    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
        {
            'discount': {'value': '15', 'value_type': 'fraction'},
            'from_cost': '100',
        },
    ]
    grocery_discounts.add_cart_cashback_gain(
        product_id=first_product_id, table_items=table_items,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [{'product_id': first_product_id, 'category_ids': []}],
        },
    )
    if is_cashback_on:
        assert response.json() == {
            'modifiers': [
                {
                    'meta': {'hierarchy_name': 'cart_discounts'},
                    'min_cart_price': '0',
                    'steps': [
                        {'rule': {'gain_value': '10'}, 'threshold': '75'},
                        {'rule': {'gain_percent': '15'}, 'threshold': '100'},
                    ],
                    'type': 'cart_discount',
                },
            ],
        }
    else:
        assert response.json() == {'modifiers': []}


# меняем приоритет иерархий, смотрим что возвращается модификатор
# самой приоритетной иерархии
@pytest.mark.parametrize(
    'expected_discount',
    [
        pytest.param(
            'suppliers',
            marks=[
                pytest.mark.config(
                    GROCERY_P13N_DISCOUNTS_HIERARCHY_PRIORITY=[
                        'suppliers',
                        'dynamic',
                        'menu',
                    ],
                ),
            ],
            id='suppliers',
        ),
        pytest.param(
            'dynamic',
            marks=[
                pytest.mark.config(
                    GROCERY_P13N_DISCOUNTS_HIERARCHY_PRIORITY=[
                        'dynamic',
                        'suppliers',
                        'menu',
                    ],
                ),
            ],
            id='dynamic',
        ),
        pytest.param(
            'menu',
            marks=[
                pytest.mark.config(
                    GROCERY_P13N_DISCOUNTS_HIERARCHY_PRIORITY=[
                        'menu',
                        'suppliers',
                        'dynamic',
                    ],
                ),
            ],
            id='menu',
        ),
    ],
)
async def test_hierarchy_priority(
        taxi_grocery_p13n, grocery_discounts, expected_discount,
):
    product_id_first = 'product-one'

    grocery_discounts.add_money_discount(
        product_id=product_id_first,
        value_type='fraction',
        value='10',
        hierarchy_name='dynamic_discounts',
        draft_id='dynamic',
    )

    grocery_discounts.add_money_discount(
        product_id=product_id_first,
        value_type='fraction',
        value='20',
        hierarchy_name='menu_discounts',
        draft_id='menu',
    )

    grocery_discounts.add_money_discount(
        product_id=product_id_first,
        value_type='fraction',
        value='30',
        hierarchy_name='suppliers_discounts',
        draft_id='suppliers',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id_first, 'category_ids': []}],
        },
    )
    modifiers = response.json()['modifiers']
    assert len(modifiers) == 1
    assert modifiers[0]['meta']['draft_id'] == expected_discount
    assert (
        modifiers[0]['meta']['hierarchy_name']
        == expected_discount + '_discounts'
    )


@pytest.mark.config(GROCERY_DISCOUNTS_TAGS_BATCH_SIZE=3)
@pytest.mark.parametrize('items_count, tags_called', [(9, 4), (8, 3), (2, 1)])
async def test_tags_bulk_request(
        taxi_grocery_p13n,
        items_count,
        tags_called,
        grocery_tags,
        grocery_discounts,
):
    personal_phone_id = 'test_phone_id'

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={
            'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}',
            'X-Yandex-UID': 'test_yuid',
        },
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': f'product-{i}', 'category_ids': []}
                for i in range(items_count)
            ],
        },
    )
    assert response.status_code == 200
    assert grocery_tags.v2_match_times_called() == tags_called


# проверяем что передаются новые поля discount_id
# и has_discount_usage_restrictions в discount_meta
@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.PAYMENT_METHOD_DISCOUNT_EXPERIMENT
@pytest.mark.parametrize(
    'hierarchy_name,has_discount_usage_restrictions_field',
    [
        ('menu_discounts', True),
        ('suppliers_discounts', False),
        ('payment_method_discounts', False),
        ('dynamic_discounts', True),
    ],
)
async def test_modifier_id_and_usage_properties(
        taxi_grocery_p13n,
        grocery_discounts,
        hierarchy_name,
        has_discount_usage_restrictions_field,
):
    product_id_first = 'product-one'
    discount_id = '12345'
    has_discount_usage_restrictions = True

    grocery_discounts.add_money_discount(
        product_id=product_id_first,
        value_type='fraction',
        value='10',
        hierarchy_name=hierarchy_name,
        discount_id=discount_id,
        has_discount_usage_restrictions=has_discount_usage_restrictions,
    )

    request_json = {
        'purpose': 'catalog',
        'depot': depot.DEPOT,
        'items': [{'product_id': product_id_first, 'category_ids': []}],
        'payment_method': {'type': 'card', 'id': '1'},
    }

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json=request_json,
    )

    modifier = response.json()['modifiers'][0]
    assert modifier['meta']['discount_id'] == '12345'
    if has_discount_usage_restrictions_field:
        assert (
            modifier['meta']['has_discount_usage_restrictions']
            == has_discount_usage_restrictions
        )


# проверяем что передаются новые поля discount_id
# и has_discount_usage_restrictions в discount_meta для корзины
async def test_modifier_id_and_usage_properties_for_cart(
        taxi_grocery_p13n, grocery_discounts,
):
    product_id_second = 'product-two'

    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '0',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=product_id_second,
        table_items=table_items,
        discount_id='12345',
        has_discount_usage_restrictions=True,
    )

    response_for_cart = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id_second, 'category_ids': []}],
        },
    )

    modifier = response_for_cart.json()['modifiers'][0]
    assert modifier['meta']['discount_id'] == '12345'
    assert modifier['meta']['has_discount_usage_restrictions']


# скидка на корзину возвращается если в корзине есть посылка,
# не возвращается если есть уцененный товар
@pytest.mark.parametrize(
    'item_id, cart_discount_presented',
    [
        pytest.param('product:st-md', False, id='markdown'),
        pytest.param('product:st-pa', True, id='parcel'),
    ],
)
async def test_cart_modifier_is_available_with_store_item(
        taxi_grocery_p13n, grocery_discounts, item_id, cart_discount_presented,
):
    product_id = 'product-1'
    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=product_id, table_items=table_items,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': product_id, 'category_ids': []},
                {'product_id': item_id, 'category_ids': []},
            ],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    if cart_discount_presented:
        assert len(response.json()['modifiers']) == 1
    else:
        assert not response.json()['modifiers']


# ходим с флагом посылок в эксп
@experiments.GROCERY_DISCOUNTS_LABELS
@pytest.mark.config(
    GROCERY_DISCOUNTS_LABELS_EXPERIMENTS=[
        {'name': 'grocery_discounts_labels', 'experiment_type': 'config'},
    ],
)
async def test_cart_modifier_labels_experiment(
        taxi_grocery_p13n, grocery_discounts,
):
    grocery_discounts.set_v4_match_discounts_check(
        on_v4_match_discounts=lambda headers, json: json['common_conditions'][
            'experiments'
        ][0]
        == 'has_parcels_label',
    )
    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [],
            'has_parcels': True,
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1


# Модификаторы корзины возвращаются при пустом списке товаров.
async def test_cart_modifiers_empty_items_list(
        taxi_grocery_p13n, grocery_discounts,
):
    dummy_product_id = 'dummy_cart_item'

    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
        {
            'discount': {'value': '20', 'value_type': 'fraction'},
            'from_cost': '150',
        },
    ]

    grocery_discounts.add_cart_money_discount(
        product_id=dummy_product_id, table_items=table_items,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={'purpose': 'cart', 'depot': depot.DEPOT, 'items': []},
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'cart_discounts'},
                'min_cart_price': '0',
                'steps': [
                    {'rule': {'discount_value': '10'}, 'threshold': '75'},
                    {'rule': {'discount_percent': '20'}, 'threshold': '150'},
                ],
                'type': 'cart_discount',
            },
        ],
    }


async def test_uid_and_phone_passed_to_discounts(
        taxi_grocery_p13n, mockserver,
):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        assert (
            request.headers['X-Yandex-UID'] == tests_headers.HEADER_YANDEX_UID
        )
        assert (
            request.json['common_conditions']['personal_phone_id']
            == tests_headers.PERSONAL_PHONE_ID
        )
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_id', 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1


# проверяем что для уцененных товаров делаем запрос только с
# иерархией markdown_discounts и обрезаем суфикс у id
@experiments.MARKDOWN_DISCOUNTS_ENABLED
@pytest.mark.parametrize('purpose', ['catalog', 'cart'])
async def test_markdown_product_discount_request(
        taxi_grocery_p13n, mockserver, purpose,
):
    markdown_product = 'product-1:st-md'

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_match_discounts(request):
        body = request.json
        assert body['hierarchy_names'] == ['markdown_discounts']
        assert request.json['subqueries'][0]['subquery_id'] == markdown_product
        assert (
            request.json['subqueries'][0]['conditions']['product']
            == markdown_product[:-6]
        )
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': markdown_product, 'category_ids': []}],
        },
    )

    assert response.status == 200
    assert _mock_match_discounts.times_called == 1


# проверяем что возвращаются скидки для иерархии markdown_discounts
# запросы для обычных товаров и уцененных происходят асинхронно
@experiments.MARKDOWN_DISCOUNTS_ENABLED
async def test_markdown_store_products_discounts(
        taxi_grocery_p13n, grocery_discounts,
):
    store_product = 'product-1'
    markdown_product = 'product-1:st-md'

    grocery_discounts.add_money_discount(
        product_id=store_product,
        value_type='fraction',
        value='10',
        hierarchy_name='menu_discounts',
    )

    grocery_discounts.add_money_discount(
        product_id=store_product,
        value_type='fraction',
        value='20',
        hierarchy_name='markdown_discounts',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [
                {'product_id': store_product, 'category_ids': []},
                {'product_id': markdown_product, 'category_ids': []},
            ],
        },
    )
    assert response.status == 200
    assert grocery_discounts.times_called == 2
    modifiers = response.json()['modifiers']
    assert len(modifiers) == 2
    assert modifiers == [
        {
            'meta': {'hierarchy_name': 'menu_discounts'},
            'product_id': 'product-1',
            'rule': {'discount_percent': '10'},
            'type': 'item_discount',
        },
        {
            'meta': {'hierarchy_name': 'markdown_discounts'},
            'product_id': 'product-1:st-md',
            'rule': {'discount_percent': '20'},
            'type': 'item_discount',
        },
    ]


# проверяем какие иерархии передаем в матчинг сервиса скидок
@experiments.MARKDOWN_DISCOUNTS_ENABLED
@pytest.mark.parametrize(
    'is_cashback_on',
    [
        pytest.param(
            True,
            id='cashback_on',
            marks=[experiments.CASHBACK_EXPERIMENT_RUSSIA],
        ),
        pytest.param(False, id='cashback_off', marks=[]),
    ],
)
@pytest.mark.parametrize(
    'purpose, expected_hierarchies',
    [
        (
            'catalog',
            ['suppliers_discounts', 'dynamic_discounts', 'menu_discounts'],
        ),
        (
            'cart',
            [
                'cart_discounts',
                'suppliers_discounts',
                'dynamic_discounts',
                'menu_discounts',
            ],
        ),
    ],
)
async def test_hierarchies_request(
        taxi_grocery_p13n,
        mockserver,
        purpose,
        expected_hierarchies,
        is_cashback_on,
):
    request_hierarchies = expected_hierarchies.copy()
    if is_cashback_on:
        request_hierarchies.append('menu_cashback')
        if purpose == 'cart':
            request_hierarchies.append('cart_cashback')

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_match_discounts(request):
        assert set(request.json['hierarchy_names']) == set(request_hierarchies)
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': purpose,
            'depot': depot.DEPOT,
            'items': [{'product_id': 'product-1', 'category_ids': []}],
        },
    )

    assert response.status == 200
    assert _mock_match_discounts.times_called == 1


# проверяем что передаем иерархии метода оплаты в сервис скидок
@pytest.mark.parametrize(
    'is_cashback_on',
    [
        pytest.param(
            True,
            id='cashback_on',
            marks=[experiments.CASHBACK_EXPERIMENT_RUSSIA],
        ),
        pytest.param(False, id='cashback_off', marks=[]),
    ],
)
@experiments.PAYMENT_METHOD_DISCOUNT_EXPERIMENT
async def test_payment_method_hierarchies_request(
        taxi_grocery_p13n, mockserver, is_cashback_on,
):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_match_discounts(request):
        assert 'payment_method_discounts' in request.json['hierarchy_names']
        if is_cashback_on:
            assert 'payment_method_cashback' in request.json['hierarchy_names']
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': 'product-1', 'category_ids': []}],
            'payment_method': {'type': 'card', 'id': '1'},
        },
    )
    assert response.status == 200
    assert _mock_match_discounts.times_called == 1


@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud,'
    'antifraud_user_profile_tagged, is_fraud_in_user_profile',
    [
        pytest.param(
            False,
            True,
            False,
            False,
            marks=experiments.ANTIFRAUD_CHECK_DISABLED,
        ),
        pytest.param(
            True,
            False,
            False,
            True,
            marks=experiments.ANTIFRAUD_CHECK_ENABLED,
        ),
        pytest.param(
            True,
            False,
            True,
            True,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            True,
            False,
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            True,
            True,
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
    ],
)
async def test_orders_count_antifraud(
        taxi_grocery_p13n,
        mockserver,
        grocery_marketing,
        grocery_user_profiles,
        testpoint,
        antifraud,
        antifraud_enabled,
        is_fraud,
        antifraud_user_profile_tagged,
        is_fraud_in_user_profile,
):
    lon = 30.0
    lat = 40.0
    user_agent = 'user-agent'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'
    city = 'city'
    street = 'street'
    house = 'house'
    flat = 'flat'
    comment = 'comment'
    orders_count = 2
    discount_prohibited = (
        antifraud_enabled
        and is_fraud
        or antifraud_user_profile_tagged
        and is_fraud_in_user_profile
    )

    grocery_marketing.add_user_tag(
        'total_orders_count',
        orders_count,
        user_id=tests_headers.HEADER_YANDEX_UID,
    )

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_grocery_discounts(request):
        assert request.json['common_conditions']['orders_counts'][0] == {
            'orders_count': orders_count,
            'payment_method': 'All',
            'application_name': 'All',
        }
        return {'match_results': []}

    antifraud.set_is_fraud(is_fraud)
    antifraud.check_discount_antifraud(
        user_id=tests_headers.HEADER_YANDEX_UID,
        user_id_service='passport',
        user_personal_phone_id=tests_headers.PERSONAL_PHONE_ID,
        user_agent=user_agent,
        application_type='android',
        service_name='grocery',
        short_address=f'{city}, {street} {house} {flat}',
        address_comment=comment,
        order_coordinates={'lat': lat, 'lon': lon},
        device_coordinates={'lat': lat, 'lon': lon},
        payment_method_id='1',
        payment_method='card',
        user_device_id=tests_headers.APPMETRICA_DEVICE_ID,
        store_id=depot.DEPOT['external_depot_id'],
    )
    grocery_user_profiles.set_is_fraud(is_fraud_in_user_profile)
    grocery_user_profiles.check_info_request(
        yandex_uid=tests_headers.HEADER_YANDEX_UID,
        personal_phone_id=tests_headers.PERSONAL_PHONE_ID,
    )
    grocery_user_profiles.check_save_request(
        yandex_uid=tests_headers.HEADER_YANDEX_UID,
        personal_phone_id=tests_headers.PERSONAL_PHONE_ID,
        antifraud_info={'name': 'lavka_newcomer_discount_fraud'},
    )

    @testpoint('yt_discount_offer_info')
    def yt_discount_offer_info(discount_offer_info):
        assert discount_offer_info['cart_id'] == cart_id
        assert discount_offer_info['doc'] == {
            'cart_id': cart_id,
            'passport_uid': tests_headers.HEADER_YANDEX_UID,
            'eats_uid': tests_headers.HEADER_EATS_ID,
            'personal_phone_id': tests_headers.PERSONAL_PHONE_ID,
            'personal_email_id': '',
            'discount_allowed_by_antifraud': not discount_prohibited,
            'discount_allowed': False,
            'discount_allowed_by_rt_xaron': not (
                antifraud_enabled and is_fraud
            ),
            'discount_allowed_by_truncated_flat': True,
            'discount_allowed_by_user_profile': not (
                antifraud_user_profile_tagged and is_fraud_in_user_profile
            ),
            'usage_count': orders_count,
            'usage_count_according_to_uid': orders_count,
            'promocode_id': '',
            'promocode': '',
        }

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=tests_headers.HEADERS,
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_id', 'category_ids': []}],
            'payment_method': {'type': 'card', 'id': '1'},
            'user_agent': user_agent,
            'position': {'location': [lon, lat]},
            'cart_id': cart_id,
            'additional_data': {
                'device_coordinates': {'location': [lon, lat]},
                'city': city,
                'street': street,
                'house': house,
                'flat': flat,
                'comment': comment,
            },
        },
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1
    assert grocery_marketing.retrieve_v2_times_called == 1
    assert grocery_user_profiles.times_antifraud_info_called() == int(
        antifraud_user_profile_tagged,
    )

    if is_fraud and not is_fraud_in_user_profile:
        assert grocery_user_profiles.times_antifraud_save_called() == int(
            antifraud_user_profile_tagged,
        )

    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )
    assert yt_discount_offer_info.times_called == 1


async def test_modifiers_request_categories(taxi_grocery_p13n, mockserver):
    front_categories = ['front-category']
    master_categories = ['master-category']

    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_match_discounts(request):
        request_condition = request.json['subqueries'][0]['conditions']
        assert request_condition['groups'] == front_categories
        assert request_condition['master_groups'] == master_categories
        return {'match_results': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [
                {
                    'product_id': 'test_product_id',
                    'category_ids': front_categories,
                    'master_categories': master_categories,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert _mock_match_discounts.times_called == 1


# Протаскивает метки из эксперимента 3.0 в скидки
@experiments.GROCERY_DISCOUNTS_LABELS
@pytest.mark.config(
    GROCERY_DISCOUNTS_LABELS_EXPERIMENTS=[
        {'name': 'grocery_discounts_labels', 'experiment_type': 'config'},
    ],
)
@pytest.mark.parametrize(
    'headers,label',
    [
        pytest.param(
            {'X-YaTaxi-Session': 'taxi:1', 'X-Yandex-UID': '123'},
            'from_user_id',
            id='match by taxi user_id',
        ),
        pytest.param(
            {
                'X-YaTaxi-Session': 'taxi:2',
                'X-Yandex-UID': '123',
                'X-YaTaxi-GeoId': '3',
            },
            'from_geo_id',
            id='match by X-YaTaxi-GeoId',
        ),
    ],
)
async def test_discounts_labels_experiment(
        taxi_grocery_p13n, mockserver, headers, label,
):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_grocery_discounts(request):
        experiments.check_labels_for_discounts(request, [label])
        return mockserver.make_response(json={'match_results': []}, status=200)

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers=headers,
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_product_id', 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert _mock_grocery_discounts.times_called == 1


@pytest.mark.config(
    GROCERY_DISCOUNTS_LABELS_EXPERIMENTS=[
        {'name': 'config_name', 'experiment_type': 'config'},
        {'name': 'experiment_name', 'experiment_type': 'experiment'},
    ],
)
@experiments.generate_labels_experiment(
    'config_name', True, ['label_1, label_2'],
)
@experiments.generate_labels_experiment(
    'experiment_name', False, ['label_3, label_4'],
)
async def test_discounts_labels_several_experiments(
        taxi_grocery_p13n, mockserver,
):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_grocery_discounts(request):
        experiments.check_labels_for_discounts(
            request, ['label_1, label_2', 'label_3, label_4'],
        )
        return mockserver.make_response(json={'match_results': []}, status=200)

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_product_id', 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert _mock_grocery_discounts.times_called == 1


async def test_discounts_ya_plus_flag(taxi_grocery_p13n, mockserver):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def _mock_grocery_discounts(request):
        assert request.json['common_conditions'].get('has_yaplus', None)
        return mockserver.make_response(json={'match_results': []}, status=200)

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': 'test_product_id', 'category_ids': []}],
        },
        headers={'X-YaTaxi-Pass-Flags': 'ya-plus'},
    )
    assert response.status_code == 200
    assert _mock_grocery_discounts.times_called == 1
