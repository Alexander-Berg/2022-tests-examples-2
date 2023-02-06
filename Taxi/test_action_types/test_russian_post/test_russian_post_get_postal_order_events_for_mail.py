# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.russian_post import (
    russian_post_get_postal_order_events_for_mail,
)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number', 'value': 'XXX-XXXX'}],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': '80083564541543'}],
                ),
            ),
            [
                param_module.ActionParam(
                    {'track_number_feature_name': 'order_id'},
                ),
            ],
        ),
    ],
)
@pytest.mark.russian_post_mock(is_event=True)
async def test_russian_post_get_postal_order_events_for_mail(
        web_context, state, _call_param,
):
    action = (
        russian_post_get_postal_order_events_for_mail.GetPostalOrderEventsForMail(
            'test', 'get_postal_order_events_for_mail', '0', _call_param,
        )
    )

    _state = await action(web_context, state)

    import sys
    sys.stderr.write(f'DATA: {_state}')
    assert 'postal_order_number' in _state.features
    assert _state.features['postal_order_number'] is not None
    assert _state.features['postal_order_sum_payment_forward'] == 449000
    assert _state.features['postal_order_sum_payment_forward_rubles'] == 4490
    assert _state.features['postal_order_sum_payment_forward_kopecks'] == 0
    assert 'postal_order_sum_payment_forward' in _state.features
