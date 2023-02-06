import pytest

ENDPOINT = '/driver/v1/driver-feedback/v1/choices'
PARK_ID = 'ParkId'
DRIVER_ID = 'DriverId'

HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}


def make_choices(feed_type):
    return {
        'choices': [
            {
                'options': ['reason_1', 'reason_2', 'reason_3'],
                'score': 1,
                'title': 'title',
                'custom_comment_available': True,
                'is_option_required': True,
            },
            {
                'options': ['reason_1', 'reason_2', 'reason_3'],
                'score': 2,
                'title': 'title',
                'custom_comment_available': False,
                'is_option_required': True,
            },
            {
                'options': ['reason_1', 'reason_3'],
                'score': 3,
                'title': 'title',
                'custom_comment_available': True,
                'is_option_required': True,
            },
            {
                'options': ['reason_3'],
                'score': 4,
                'title': 'title',
                'custom_comment_available': False,
                'is_option_required': False,
            },
            {
                'options': [],
                'score': 5,
                'title': 'title',
                'custom_comment_available': True,
                'is_option_required': False,
            },
        ],
        'feed_type': feed_type,
        'default_title': 'default_title',
        'order_history_title': 'order_history_title',
    }


def make_response_item(feed_type):
    item = make_choices(feed_type)
    for choice in item['choices']:
        choice['title'] += '_localized'
        choice['options'] = [
            {'key': reason, 'value': reason + '_localized'}
            for reason in choice['options']
        ]
    item['default_title'] += '_localized'
    item['order_history_title'] += '_localized'

    return item


def builder(keys, config=True):
    maker = make_choices if config else make_response_item
    return {'items': [maker(key) for key in keys]}


@pytest.mark.parametrize(
    'keys,corp',
    [
        pytest.param(['passenger'], False, id='passenger'),
        pytest.param(['sender'], False, id='sender'),
        pytest.param(['recipient'], False, id='recipient'),
        pytest.param(['eater'], False, id='eater'),
        pytest.param(
            ['eater', 'restaurant', 'misc'], False, id='eats with misc',
        ),
        pytest.param(['sender', 'recipient'], False, id='both'),
        pytest.param(['sender', 'recipient'], True, id='corp'),
    ],
)
async def test_feedback_choices(
        taxi_driver_feedback,
        driver_orders,
        experiments3,
        load_json,
        keys,
        corp,
):
    driver_orders.set_order_params(
        'order_id_1',
        {
            'category': 'econom',
            'address_to': {
                'address': 'Москва, улица Героев Панфиловцев, 1А',
                'lon': 37.438229,
                'lat': 55.851563,
            },
        },
    )
    exp_template = load_json('choices_config_template.json')
    exp_template['configs'][0]['clauses'][0]['value'] = builder(keys)
    if corp:
        exp_template['configs'][0]['clauses'][0]['predicate'] = {
            'type': 'eq',
            'init': {
                'arg_name': 'corp_id',
                'arg_type': 'string',
                'value': 'ClientCorpId',
            },
        }

    experiments3.add_experiments_json(exp_template)
    await taxi_driver_feedback.tests_control(invalidate_caches=True)

    response = await taxi_driver_feedback.get(
        ENDPOINT, params={'order_id': 'order_id_1'}, headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == builder(keys, config=False)
