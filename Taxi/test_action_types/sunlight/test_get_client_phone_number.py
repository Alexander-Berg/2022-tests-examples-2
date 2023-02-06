import pytest

from supportai_actions.action_types.sunlight import get_client_phone_number
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize('_call_param', [[], []])
async def test_sunlight_get_client_phone_number_validation(_call_param):
    _ = get_client_phone_number.GetClientPhoneNumberAction(
        'sunlight', 'get_client_phone_number', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'channelType', 'value': 'WhatsAppMfms'},
                        {'key': 'visitorId', 'value': '1234567890'},
                    ],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'channelType', 'value': 'WhatsAppMfms'}],
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
                    features=[{'key': 'visitorId', 'value': '123'}],
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
                    features=[{'key': 'kek', 'value': 'lol'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_sunlight_get_client_phone_number_state_validation(
        state, _call_param,
):
    action = get_client_phone_number.GetClientPhoneNumberAction(
        'sunlight', 'get_client_phone_number', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'channelType', 'value': 'WhatsAppMfms'},
                        {'key': 'visitorId', 'value': '79005553535'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_get_client_phone_number_call_found(
        web_context, state, _call_param,
):
    action = get_client_phone_number.GetClientPhoneNumberAction(
        'sunlight', 'get_client_phone_number', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'client_phone_number' in _state.features
    assert _state.features['client_phone_number'] == 79005553535


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'channelType', 'value': 'Viber'},
                        {'key': 'visitorId', 'value': '123'},
                    ],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'channelType', 'value': 'WhatsAppMfms'},
                        {'key': 'visitorId', 'value': '123'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_get_client_phone_number_call_not_found(
        web_context, state, _call_param,
):
    action = get_client_phone_number.GetClientPhoneNumberAction(
        'sunlight', 'get_client_phone_number', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'client_phone_number' not in _state.features
