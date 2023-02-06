import pytest


PENDING_ORDER_ID = '7be1b5a05caa2f46b1a60c44971ce60f'
DRIVING_ORDER_ID = '5a9ed969df691ab8ad3f703f3a8efcd5'
WAITING_ORDER_ID = '5a9ed969df691ab8ad3f703f3a8efcd6'
TRANSPORTING_ORDER_ID = '5a9ed969df691ab8ad3f703f3a8efcd7'
COMPLETE_ORDER_ID = '5a9ed969df691ab8ad3f703f3a8efcd8'

PREDICTED_COSTS = {
    'cost_message': 'Approximately 1,210\xa0$SIGN$$CURRENCY$ for 10 minutes.',
    'final_cost': 1210,
    'final_cost_as_str': '1,210\xa0$SIGN$$CURRENCY$',
    'final_cost_decimal_value': '1210',
}

PREDICTED_COSTS_FIXED = {
    'cost_message': '1,210\xa0$SIGN$$CURRENCY$ for the ride',
    'final_cost': 1210,
    'final_cost_as_str': '1,210\xa0$SIGN$$CURRENCY$',
    'final_cost_decimal_value': '1210',
}

EXPECTED_STATUS_INFO = {
    'translations': {
        'card': {
            'title_template': '$DUE_DAY$ in $DUE_TIME$',
            'subtitle_template': 'Search will start after 2 min',
        },
    },
}

EXPECTED_STATUS_INFO_GUARANTEE = {
    'translations': {
        'card': {
            'title_template': '$DUE_DAY$ in $DUE_TIME$',
            'subtitle_template': 'Сar will arrive at this time',
        },
    },
}

TOTW_COST_MESSAGES = [
    pytest.param(
        PENDING_ORDER_ID,
        'scheduling',
        PREDICTED_COSTS,
        id='scheduling_all_costs',
    ),
    pytest.param(
        DRIVING_ORDER_ID, 'driving', PREDICTED_COSTS, id='driving_all_costs',
    ),
    pytest.param(
        WAITING_ORDER_ID, 'waiting', PREDICTED_COSTS, id='waiting_all_costs',
    ),
    pytest.param(
        TRANSPORTING_ORDER_ID,
        'transporting',
        PREDICTED_COSTS,
        id='transporting_all_costs',
    ),
    pytest.param(
        COMPLETE_ORDER_ID,
        'complete',
        {
            'final_cost': 682,
            'final_cost_as_str': '682\xa0$SIGN$$CURRENCY$',
            'final_cost_decimal_value': '682',
        },
        id='complete_costs_without_message',
    ),
]


TOTW_COST_MESSAGES_FIXED_PRICE = [
    pytest.param(
        PENDING_ORDER_ID,
        'scheduling',
        PREDICTED_COSTS_FIXED,
        id='scheduling_all_costs',
    ),
    pytest.param(
        DRIVING_ORDER_ID,
        'driving',
        PREDICTED_COSTS_FIXED,
        id='driving_all_costs',
    ),
    pytest.param(
        WAITING_ORDER_ID,
        'waiting',
        PREDICTED_COSTS_FIXED,
        id='waiting_all_costs',
    ),
    pytest.param(
        TRANSPORTING_ORDER_ID,
        'transporting',
        PREDICTED_COSTS_FIXED,
        id='transporting_all_costs',
    ),
    pytest.param(
        COMPLETE_ORDER_ID,
        'complete',
        {
            'final_cost': 682,
            'final_cost_as_str': '682\xa0$SIGN$$CURRENCY$',
            'final_cost_decimal_value': '682',
        },
        id='complete_costs_without_message',
    ),
]


def _preorder_request(taxi_protocol, order_id):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
            'version': 'DAAAAAAABgAMAAQABgAAANoL1SNsAQAA',
        },
    )

    assert response.status_code == 200
    return response.json()


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    tariff={'name.business': {'ru': 'Бизнес', 'en': 'Business'}},
)
@pytest.mark.parametrize(
    ('order_id', 'totw_status', 'expected_cost'), TOTW_COST_MESSAGES,
)
def test_statuses_costs(taxi_protocol, order_id, totw_status, expected_cost):
    check_statuses_costs(taxi_protocol, order_id, totw_status, expected_cost)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    tariff={'name.business': {'ru': 'Бизнес', 'en': 'Business'}},
)
@pytest.mark.parametrize(
    ('order_id', 'totw_status', 'expected_cost'), TOTW_COST_MESSAGES,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='preorder_fixprice',
    consumers=['client_protocol/taxiontheway'],
    clauses=[
        {
            'title': '',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_statuses_costs_fixed_price(
        db, taxi_protocol, order_id, totw_status, expected_cost,
):
    prepare_order_proc_for_fix_price(db, order_id)
    check_statuses_costs(taxi_protocol, order_id, totw_status, expected_cost)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    tariff={'name.business': {'ru': 'Бизнес', 'en': 'Business'}},
)
@pytest.mark.parametrize(
    ('order_id', 'totw_status', 'expected_cost'),
    TOTW_COST_MESSAGES_FIXED_PRICE,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='preorder_fixprice',
    consumers=['client_protocol/taxiontheway'],
    clauses=[
        {
            'title': '',
            'value': {'enabled': True, 'show_labels': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_statuses_costs_fixed_price_labels(
        db, taxi_protocol, order_id, totw_status, expected_cost,
):
    prepare_order_proc_for_fix_price(db, order_id)
    check_statuses_costs(taxi_protocol, order_id, totw_status, expected_cost)


def check_statuses_costs(taxi_protocol, order_id, totw_status, expected_cost):
    content = _preorder_request(taxi_protocol, order_id)

    assert content['status'] == totw_status

    cost_fields = (
        'cost_message',
        'final_cost',
        'final_cost_as_str',
        'final_cost_decimal_value',
    )
    for cost_field in cost_fields:
        expected_value = expected_cost.get(cost_field, None)
        assert content.get(cost_field, None) == expected_value


def prepare_order_proc_for_fix_price(db, order_id):
    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.fixed_price': {'price': 1210}}},
    )
    db.order_proc.update(
        {'_id': order_id, 'order.calc_method': {'$exists': True}},
        {'$set': {'order.calc_method': 'fixed'}},
    )
    db.order_proc.update(
        {'_id': order_id, 'order_info.cc': {'$exists': True}},
        {'$set': {'order_info.cc': 1210}},
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    PREORDER_TOTW_INSTRUCTIONS={
        'scheduling': [
            {'title': 'title_key', 'icon_image_tag': 'icon image tag'},
        ],
    },
)
@pytest.mark.translations(
    client_messages={'title_key': {'ru': 'title text ru'}},
)
def test_instructions(taxi_protocol):
    content = _preorder_request(taxi_protocol, PENDING_ORDER_ID)

    assert 'notifications' in content
    notifications = content['notifications']

    assert 'requirement_card_title' in notifications
    requirement_card_title = notifications['requirement_card_title']

    assert requirement_card_title.get('type', None) == 'requirement_card_title'
    assert requirement_card_title.get('items', None) == [
        {'title': 'title text ru', 'icon_image_tag': 'icon image tag'},
    ]


@pytest.mark.translations(
    client_messages={
        'preorder.taxiontheway.scheduling.title': {
            'en': '$DUE_DAY$ in $DUE_TIME$',
        },
        'preorder.taxiontheway.scheduling.subtitle': {
            'en': 'Search will start after 2 min',
        },
    },
)
@pytest.mark.parametrize('has_preorder_id', [True, False])
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_preorder_status_info(
        taxi_protocol, tracker, now, db, has_preorder_id,
):
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )
    if not has_preorder_id:
        db.order_proc.update(
            {'_id': PENDING_ORDER_ID},
            {'$unset': {'order.preorder_request_id': True}},
        )
    content = _preorder_request(taxi_protocol, PENDING_ORDER_ID)
    assert content['status'] == 'scheduling'

    if has_preorder_id:
        assert content['status_info'] == EXPECTED_STATUS_INFO
    else:
        assert 'status_info' not in content


@pytest.mark.translations(
    client_messages={
        'preorder.taxiontheway.scheduling.title': {
            'en': '$DUE_DAY$ in $DUE_TIME$',
        },
        'preorder.taxiontheway.scheduling.subtitle': {
            'en': 'Search will start after 2 min',
        },
        'preorder.taxiontheway.scheduling.guarantee.title': {
            'en': '$DUE_DAY$ in $DUE_TIME$',
        },
        'preorder.taxiontheway.scheduling.guarantee.subtitle': {
            'en': 'Сar will arrive at this time',
        },
    },
)
@pytest.mark.parametrize('has_guarantee_intent', [True, False])
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_guarantee_preorder(
        taxi_protocol, tracker, now, db, has_guarantee_intent,
):
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )
    if has_guarantee_intent:
        db.order_proc.update(
            {'_id': PENDING_ORDER_ID},
            {
                '$set': {
                    'order.request.lookup_extra.intent': 'preorder_guarantee',
                },
            },
        )
    content = _preorder_request(taxi_protocol, PENDING_ORDER_ID)
    assert content['status'] == 'scheduling'

    if has_guarantee_intent:
        assert content['status_info'] == EXPECTED_STATUS_INFO_GUARANTEE
    else:
        assert content['status_info'] == EXPECTED_STATUS_INFO


@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_preorder_status_info_empty_translations(
        taxi_protocol, tracker, now, db,
):
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )
    content = _preorder_request(taxi_protocol, PENDING_ORDER_ID)
    assert 'status_info' not in content
