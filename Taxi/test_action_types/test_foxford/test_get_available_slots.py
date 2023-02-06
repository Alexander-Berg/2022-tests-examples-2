# pylint: disable=broad-except

import datetime

import pytest
import pytz

from supportai_actions.action_types.foxford_dialog import constants
from supportai_actions.action_types.foxford_dialog import get_available_slots
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

ACTION_NAME = 'get_available_slots'
PROJECT_NAME = 'foxford_dialog'


def shift_utc(
        delta=datetime.timedelta(), timezone='Europe/Moscow', use_short=False,
):
    dttm = (
        datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) + delta
    ).astimezone(pytz.timezone(timezone))
    return (
        dttm.strftime(constants.DATETIME_FORMAT_SHORT)
        if use_short
        else dttm.strftime(constants.DATETIME_FORMAT_FOR_API)
    )


@pytest.mark.parametrize(
    'state, raises',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    [
                        {
                            'key': 'some_weird_feature',
                            'value': 'some_weird_feature_value',
                        },
                    ],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'agent_id', 'value': '123'}],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
    ],
)
async def test_suggest_available_slots_state_validation(state, raises):
    action = get_available_slots.GetAvailableSlots(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford_get_agent_slots')
def _mock_foxford_get_agent_slots(mockserver):
    @mockserver.json_handler(
        path='foxford-api/api/yandex_support_ai/agents/321/slot',
    )
    def _(_):
        return mockserver.make_response(
            json=[
                {
                    'slot': shift_utc(datetime.timedelta(days=1)),
                    'status': 'available',
                },
                {
                    'slot': shift_utc(datetime.timedelta(days=2, hours=3)),
                    'status': 'booked',
                    'pupil_id': '123',
                },
                {
                    'slot': shift_utc(datetime.timedelta(days=2, hours=5)),
                    'status': 'by_mini_group',
                },
                {
                    'slot': shift_utc(datetime.timedelta(days=2, hours=8)),
                    'status': 'available',
                },
            ],
            status=200,
        )

    @mockserver.json_handler(
        path='foxford-api/api/yandex_support_ai/agents/4321/slot',
    )
    def _(request):
        return mockserver.make_response(
            json=[
                {
                    'slot': shift_utc(
                        delta=datetime.timedelta(days=0),
                        timezone='Asia/Kolkata',
                    ),
                    'status': 'available',
                },
                {
                    'slot': shift_utc(
                        delta=datetime.timedelta(days=1, hours=1),
                        timezone='US/Eastern',
                    ),
                    'status': 'available',
                },
                {
                    'slot': shift_utc(
                        delta=datetime.timedelta(days=2, hours=3),
                        timezone='Asia/Tokyo',
                    ),
                    'status': 'available',
                },
            ],
        )


@pytest.fixture(name='mock_foxford_get_user_slots')
def _mock_foxford_get_user_slots(mockserver):
    @mockserver.json_handler(
        path='foxford-api/api/yandex_support_ai/users/123/slot',
    )
    def _(_):
        return mockserver.make_response(
            json=[
                {
                    'slot': shift_utc(datetime.timedelta(days=1)),
                    'status': 'available',
                },
                {
                    'slot': shift_utc(datetime.timedelta(days=2, hours=9)),
                    'status': 'available',
                },
            ],
            status=200,
        )

    @mockserver.json_handler(
        path='foxford-api/api/yandex_support_ai/users/1234/slot',
    )
    def _(_):
        return mockserver.make_response(
            json=[
                {
                    'slot': shift_utc(
                        delta=datetime.timedelta(days=1, hours=1),
                        timezone='Europe/Moscow',
                    ),
                    'status': 'available',
                },
                {
                    'slot': shift_utc(
                        delta=datetime.timedelta(days=2, hours=3),
                        timezone='Europe/Moscow',
                    ),
                    'status': 'available',
                },
            ],
            status=200,
        )


async def test_get_available_slots_v1(
        web_context, mock_foxford_get_user_slots, mock_foxford_get_agent_slots,
):
    _call_params = []
    state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'user_id', 'value': 123},
                {'key': 'agent_id', 'value': 321},
            ],
        ),
    )
    action = get_available_slots.GetAvailableSlots(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)

    assert _state.features['available_slots'][0] == shift_utc(
        datetime.timedelta(days=1), use_short=True,
    )
    assert _state.features['booked_slots'][0] == shift_utc(
        datetime.timedelta(days=2, hours=3), use_short=True,
    )


async def test_get_available_slots_different_time_zones(
        web_context, mock_foxford_get_user_slots, mock_foxford_get_agent_slots,
):
    _call_params = [{'search_from_next_day': True}]
    state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'user_id', 'value': 1234},
                {'key': 'agent_id', 'value': 4321},
            ],
        ),
    )

    action = get_available_slots.GetAvailableSlots(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)

    assert _state.features['all_slots'][0] == shift_utc(
        delta=datetime.timedelta(days=1, hours=1),
        timezone='Europe/Moscow',
        use_short=True,
    )

    assert _state.features['all_slots'][1] == shift_utc(
        delta=datetime.timedelta(days=2, hours=3),
        timezone='Europe/Moscow',
        use_short=True,
    )
