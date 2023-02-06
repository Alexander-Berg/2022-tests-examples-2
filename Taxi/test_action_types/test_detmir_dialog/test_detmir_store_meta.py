# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.detmir_dialog import get_store_meta

DATA = [
    {
        'id': '197',
        'code': '2420',
        'alias': None,
        'title': 'СТЦ «МЕГА Дыбенко»',
        'description': '',
        'city': 'Санкт-Петербург',
        'city_code': '78000000000',
        'address': {'address': 'Кудрово, Мурманское шоссе, 12-й км, 1 этаж'},
        'lat': 59.893631225697646,
        'long': 30.514122527092706,
        'region': 'RU-SPE',
        'metro': [
            {
                'title': 'Улица Дыбенко',
                'lat': None,
                'long': None,
                'line': {
                    'title': 'Правобережная линия',
                    'code': '',
                    'color': '#FF8716',
                },
            },
        ],
        'working_hours': 'Ежедневно с 10:00 до 22:00',
        'guide': 'Фирменным автобусом «МЕГА» от ст. м. Ул. Дыбенко, Ломоносовская. Маршрутное такси от м. ул. Дыбенко: 153, 254, 269; от м. Ломоносовская: 56, 339. В МЕГЕ магазин находится рядом с кинотеатром «Киностар».',
        'payment_methods': [
            {'type': 'card', 'threshold': None},
            {'type': 'cash', 'threshold': None},
            {'type': 'loyalty', 'threshold': None},
        ],
        'offline_payment_methods': [
            {'type': 'card', 'threshold': None},
            {'type': 'cash', 'threshold': None},
            {'type': 'loyalty', 'threshold': None},
        ],
        'pickup_available': None,
        'express_delivery': True,
        'instore': True,
        'timezone_offset': 3,
        'collection_time': None,
        'storage_period': 5,
        'time_open': {'hours': 10, 'minutes': 0},
        'time_close': {'hours': 22, 'minutes': 0},
        'type': 'store',
        'subtype': 'DM',
        'is_store_pos': False,
        'partial_checkout_available': True,
        'fitting_available': True,
        'return_available': True,
        'is_active': True,
        'assembly_slots': None,
        'electro': False,
    },
]


@pytest.fixture(name='mock_store_meta', autouse=True)
def _mock_store_meta(mockserver):
    @mockserver.json_handler('/detmir-orders/v2/shops/.*', regex=True)
    def _(req):
        return mockserver.make_response(json=DATA)


@pytest.mark.parametrize(
    '_call_param',
    [
        [],
        [param_module.ActionParam({'response_mapping': []})],
        pytest.param(
            [
                param_module.ActionParam(
                    {'response_mapping': [{'key': 'value'}]},
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_detmir_store_meta_validation(_call_param):
    _ = get_store_meta.StoreMetaAction('test', 'test_detmir', '0', _call_param)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'store_id', 'value': 'XXX-XXXX'}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number', 'value': 'some'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_detmir_store_meta_state_validation(state, _call_param):
    action = get_store_meta.StoreMetaAction(
        'test', 'test_detmir', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'store_id', 'value': 'XXX-XXXX'}],
                ),
            ),
            [],
        ),
    ],
)
@pytest.mark.russian_post_mock(records=[{'oper_type': 'Test'}])
async def test_detmir_store_meta_call(web_context, state, _call_param):
    action = get_store_meta.StoreMetaAction(
        'test', 'test_detmir', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'working_hours' in _state.features
    assert _state.features['working_hours'] == 'Ежедневно с 10:00 до 22:00'
    assert 'city' in _state.features
