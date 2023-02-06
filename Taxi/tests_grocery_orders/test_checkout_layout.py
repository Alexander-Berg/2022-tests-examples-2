import pytest


def _construct_response_layout_item(
        name,
        text,
        item_type='string',
        is_required=False,
        size=None,
        max_length=20,
        item_help=None,
        restrictions=None,
):
    return {
        'name': name,
        'type': item_type,
        'text': text,
        'is_required': is_required,
        'max_length': max_length,
        **({'size': size} if size else {}),
        **({'help': item_help} if item_help else {}),
        'restrictions': restrictions if restrictions else [],
    }


def _construct_exp_layout_item(
        name,
        tanker_key,
        item_type='string',
        is_required=False,
        size=None,
        max_length=None,
        item_help=None,
        restrictions=None,
):
    return {
        'name': name,
        'type': item_type,
        'tanker_key': tanker_key,
        'is_required': is_required,
        **({'size': size} if size else {}),
        **({'max_length': max_length} if max_length is not None else {}),
        **({'help': item_help} if item_help else {}),
        **({'restrictions': restrictions} if restrictions else {}),
    }


RUS_RESPONSE = {
    'layout_items': [
        _construct_response_layout_item(
            name='entrance', text='подъезд', size='short',
        ),
        _construct_response_layout_item(
            name='comment', text='коментарий', size='extra_long',
        ),
        _construct_response_layout_item(
            name='floor', text='этаж', size='long', max_length=5,
        ),
        _construct_response_layout_item(
            name='left_at_door',
            text='оставить у двери',
            item_type='bool',
            restrictions=[
                {
                    'text': 'Слишком дорогая посылка, чтобы оставлять у двери',
                    'label': 'parcel_too_expensive',
                },
                {
                    'text': 'Товары 18+ нельзя оставлять у двери',
                    'label': 'ru_18+',
                    'modal': {'title': 'title', 'description': 'description'},
                },
            ],
        ),
        _construct_response_layout_item(
            name='no_door_call',
            text='не звонить',
            item_type='bool',
            item_help={
                'text': 'Пожалуйста, убедитесь, что указан полный адрес',
                'show_if_empty': ['floor', 'entrance', 'flat'],
            },
        ),
    ],
}

ISR_RESPONSE = {
    'layout_items': [
        _construct_response_layout_item(
            name='left_at_door', text='оставить у двери', item_type='bool',
        ),
        _construct_response_layout_item(
            name='floor', text='этаж', is_required=True,
        ),
    ],
}

RUS_EXP_VALUE = {
    'layout_items': [
        _construct_exp_layout_item(
            name='entrance', tanker_key='entrance_key', size='short',
        ),
        _construct_exp_layout_item(
            name='comment', tanker_key='comment_key', size='extra_long',
        ),
        _construct_exp_layout_item(
            name='floor', tanker_key='floor_key', size='long', max_length=5,
        ),
        _construct_exp_layout_item(
            name='left_at_door',
            tanker_key='left_at_door_key',
            item_type='bool',
            restrictions=[
                {
                    'tanker_key': 'left_at_door_parcel_too_expensive_key',
                    'label': 'parcel_too_expensive',
                },
                {
                    'tanker_key': 'left_at_door_ru_18+_key',
                    'label': 'ru_18+',
                    'modal': {
                        'title_tanker_key': 'modal_title_tanker_key',
                        'description_tanker_key': 'description',
                    },
                },
            ],
        ),
        _construct_exp_layout_item(
            name='no_door_call',
            tanker_key='no_door_call_key',
            item_type='bool',
            item_help={
                'tanker_key': 'no_door_call_help_key',
                'show_if_empty': ['floor', 'entrance', 'flat'],
            },
        ),
    ],
}


ISR_EXP_VALUE = {
    'layout_items': [
        _construct_exp_layout_item(
            name='left_at_door',
            tanker_key='left_at_door_key',
            item_type='bool',
        ),
        _construct_exp_layout_item(
            name='floor', tanker_key='floor_key', is_required=True,
        ),
    ],
}


@pytest.mark.experiments3(
    name='grocery_checkout_layout',
    consumers=['grocery-checkout-layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'For Person',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': '222',
                    'arg_name': 'personal_phone_id',
                    'arg_type': 'string',
                },
            },
            'value': ISR_EXP_VALUE,
        },
        {
            'title': 'For Russia',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            },
            'value': RUS_EXP_VALUE,
        },
        {
            'title': 'For Israel',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'ISR',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            },
            'value': ISR_EXP_VALUE,
        },
    ],
    is_config=True,
)
@pytest.mark.translations(
    grocery_orders={
        'entrance_key': {'ru': 'подъезд'},
        'comment_key': {'ru': 'коментарий'},
        'floor_key': {'ru': 'этаж'},
        'left_at_door_key': {'ru': 'оставить у двери'},
        'left_at_door_parcel_too_expensive_key': {
            'ru': 'Слишком дорогая посылка, чтобы оставлять у двери',
        },
        'left_at_door_ru_18+_key': {
            'ru': 'Товары 18+ нельзя оставлять у двери',
        },
        'no_door_call_key': {'ru': 'не звонить'},
        'no_door_call_help_key': {
            'ru': 'Пожалуйста, убедитесь, что указан полный адрес',
        },
        'modal_title_tanker_key': {'ru': 'title'},
    },
)
@pytest.mark.parametrize(
    'location,expected_response,headers',
    [
        pytest.param([0, 0], RUS_RESPONSE, {}, id='not supported location'),
        pytest.param(
            [37, 55],
            ISR_RESPONSE,
            {'X-YaTaxi-User': 'personal_phone_id=222'},
            id='for person',
        ),
        pytest.param(
            [34.865849, 32.054721], ISR_RESPONSE, {}, id='location in ISR',
        ),
        pytest.param([37, 55], RUS_RESPONSE, {}, id='location in RUS'),
    ],
)
async def test_basic(
        taxi_grocery_orders, location, expected_response, headers,
):
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/checkout-layout',
        json={'location': location},
        headers={'Accept-Language': 'ru', **headers},
    )
    assert response.json() == {'checkout_layout': expected_response}
