import pytest


HANDLE_URL = '/internal/tips/v1/need-hold-tips'


@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.parametrize(
    ['expected_need_hold_tips'],
    [
        pytest.param(False, id='no_experiment'),
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='extra_tips_payment_methods',
                    consumers=['tips'],
                    default_value={'enabled': True, 'foo_bars': []},
                ),
            ],
            id='unexpected_schema',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='extra_tips_payment_methods',
                    consumers=['tips'],
                    default_value={'enabled': True, 'payment_types': []},
                ),
            ],
            id='no_payment_types',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='extra_tips_payment_methods',
                    consumers=['tips'],
                    default_value={
                        'enabled': True,
                        'payment_types': ['googlepay'],
                    },
                ),
            ],
            id='no_matching_payment_types',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='extra_tips_payment_methods',
                    consumers=['tips'],
                    default_value={
                        'enabled': True,
                        'payment_types': ['applepay'],
                    },
                ),
            ],
            id='matching_payment_type',
        ),
    ],
)
async def test_extra_tips_payment_types_experiment(
        taxi_tips, expected_need_hold_tips: bool,
):
    order_id = 'order_13_applepay_all_exp_params'
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    need_hold_tips = response.json()['need_hold_tips']
    assert need_hold_tips == expected_need_hold_tips


def _prepare_exp_mark(
        predicate_name, predicate_value, predicate_type='string',
):
    mark = pytest.mark.experiments3(
        name='extra_tips_payment_methods',
        consumers=['tips'],
        match={
            'enabled': True,
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': predicate_name,
                    'arg_type': predicate_type,
                    'value': predicate_value,
                },
            },
        },
        default_value={'enabled': True, 'payment_types': ['applepay']},
    )
    return mark


@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.parametrize(
    ['expected_need_hold_tips'],
    [
        pytest.param(
            True,
            marks=[_prepare_exp_mark('application', 'iphone')],
            id='correct application',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('application', 'windows_phone')],
            id='wrong application',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('version', '3.144.0', 'version')],
            id='correct version',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('version', '1.234.5', 'version')],
            id='wrong version',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('zone', 'moscow')],
            id='correct zone',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('zone', 'not_moscow')],
            id='wrong zone',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('payment_option', 'applepay')],
            id='correct payment_option',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('payment_option', 'orangepay')],
            id='wrong payment_option',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('payment_type', 'applepay')],
            id='correct payment_type',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('payment_type', 'orangepay')],
            id='wrong payment_type',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('tariff_class', 'business')],
            id='correct tariff_class',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('tariff_class', 'econom')],
            id='wrong tariff_class',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('phone_id', '5d7c57bc720026fa784138d6')],
            id='correct phone_id',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('phone_id', 'some_random_id')],
            id='wrong phone_id',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('user_id', 'correct_user_id')],
            id='correct user_id',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('user_id', 'some_random_id')],
            id='wrong user_id',
        ),
        pytest.param(
            True,
            marks=[_prepare_exp_mark('country', 'rus')],
            id='correct country',
        ),
        pytest.param(
            False,
            marks=[_prepare_exp_mark('country', 'blr')],
            id='wrong country',
        ),
    ],
)
async def test_extra_tips_payment_types_experiment_kwargs(
        taxi_tips, expected_need_hold_tips: bool,
):
    order_id = 'order_13_applepay_all_exp_params'
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    need_hold_tips = response.json()['need_hold_tips']
    assert need_hold_tips == expected_need_hold_tips


@pytest.mark.parametrize(
    'payment_type, order_id',
    [
        pytest.param('agent', 'order_14_agent_order', id='agent'),
        pytest.param(
            'yandex_card', 'order_15_yandex_card_order', id='yandex_card',
        ),
    ],
)
@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='extra_tips_payment_methods',
    consumers=['tips'],
    default_value={'enabled': True, 'payment_types': ['agent', 'yandex_card']},
)
async def test_extra_payment_type(taxi_tips, payment_type, order_id):
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    need_hold_tips = response.json()['need_hold_tips']
    assert need_hold_tips
