# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.muztorg_dialog import order_meta


@pytest.fixture(name='mock_muztorg_api')
def _mock_muztorg_api(mockserver):
    @mockserver.json_handler(r'/muztorg-api/public/order/.*', regex=True)
    def _(request):
        return mockserver.make_response(
            json={
                'response': {
                    'contacts': {
                        'name': 'Name',
                        'surename': 'Surname',
                        'phone': 'XXXX-XXX XX XX',
                    },
                    'shipment': {
                        'title': 'Title',
                        'address': 'City, Street, 14',
                        'when': 'today',
                        'price': '999',
                    },
                    'statusTitle': [],
                },
            },
        )


@pytest.mark.parametrize('_call_param', [[]])
async def test_muztorg_dialog_order_meta_validation(_call_param):
    _ = order_meta.OrderMetaAction(
        'muztorg_dialog', 'order_meta', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 999999}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id_2', 'value': 999999}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': '999999'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_muztorg_dialog_order_meta_state_validation(state, _call_param):
    action = order_meta.OrderMetaAction(
        'muztorg_dialog', 'order_meta', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 999999}],
                ),
            ),
            [],
        ),
    ],
)
async def test_muztorg_dialog_order_meta_call(
        web_context, state, _call_param, mock_muztorg_api,
):
    action = order_meta.OrderMetaAction(
        'muztorg_dialog', 'order_meta', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'user_first_name' in _state.features
