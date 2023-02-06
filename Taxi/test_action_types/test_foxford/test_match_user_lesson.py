# pylint: disable=broad-except
import datetime

import pytest

from supportai_actions.action_types.foxford_dialog import constants
from supportai_actions.action_types.foxford_dialog import match_user_lesson
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)

ACTION_NAME = 'match_user_lesson'
PROJECT_NAME = 'foxford_dialog'


@pytest.mark.parametrize('_call_param', [[]])
async def test_foxford_dialog_match_user_lesson_validation(_call_param):
    _ = match_user_lesson.FindLesson(
        PROJECT_NAME, ACTION_NAME, '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'lessons_course_ids', 'value': [4, 5, 4, 5]},
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-20T15:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-10-13T12:04:35+03:00',
                        },
                        {'key': 'course_subname_to_find', 'value': 'матем'},
                    ],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'some', 'value': 'some'}],
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
                    features=[{'key': 'lesson_ids', 'value': []}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_foxford_match_user_lesson_state_validation(state, _call_param):
    action = match_user_lesson.FindLesson(
        PROJECT_NAME, ACTION_NAME, '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.now('2021-11-30T10:00')
@pytest.mark.parametrize(
    'state, expected_found_matched_lesson,'
    'expected_lesson_id, expected_dttm, expected_less_than_8_hours,'
    'expected_several_best_matches, expected_course_id, expected_agent_id',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'lessons_course_ids', 'value': []},
                        {'key': 'lessons_ids', 'value': []},
                        {'key': 'lessons_starts_ats', 'value': []},
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-13T12:04:35+03:00',
                        },
                    ],
                ),
            ),
            False,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'lessons_course_ids', 'value': [4, 5, 4, 5]},
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-20T15:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-13T12:04:35+03:00',
                        },
                    ],
                ),
            ),
            False,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'lessons_course_ids', 'value': [4, 5, 4, 5]},
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-30T15:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-30T10:00:00+03:00',
                        },
                    ],
                ),
            ),
            True,
            13,
            '2021-11-30T15:00:00+0300',
            True,
            False,
            5,
            14,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'lessons_course_ids', 'value': [4, 5, 4, 5]},
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-30T21:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-30T10:00:00+03:00',
                        },
                    ],
                ),
            ),
            True,
            13,
            '2021-11-30T21:00:00+0300',
            False,
            False,
            5,
            14,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lessons_course_ids',
                            'value': [4, 5, 4, 5, 4],
                        },
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 14, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-30T15:00:00+0300',
                                '2021-11-30T21:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-30T21:00:00+03:00',
                        },
                    ],
                ),
            ),
            True,
            13,
            '2021-11-30T21:00:00+0300',
            False,
            False,
            4,
            13,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lessons_course_ids',
                            'value': [4, 5, 4, 5, 4],
                        },
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 14, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-30T15:00:00+0300',
                                '2021-11-30T21:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-30T21:00:00+03:00',
                        },
                        {'key': 'course_subname_to_find', 'value': 'англ'},
                    ],
                ),
            ),
            True,
            14,
            '2021-11-30T15:00:00+0300',
            True,
            False,
            5,
            14,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lessons_course_ids',
                            'value': [4, 5, 4, 5, 4],
                        },
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 14, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-30T15:00:00+0300',
                                '2021-11-30T21:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-30T21:00:00+03:00',
                        },
                        {'key': 'course_subname_to_find', 'value': 'матем'},
                    ],
                ),
            ),
            False,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lessons_course_ids',
                            'value': [4, 5, 4, 5, 4],
                        },
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 14, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2021-11-17T12:00:00+0300',
                                '2021-11-18T13:00:00+0300',
                                '2021-11-19T14:00:00+0300',
                                '2021-11-30T15:00:00+0300',
                                '2021-11-30T21:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2021-11-30T10:00:00+03:00',
                        },
                    ],
                ),
            ),
            True,
            14,
            '2021-11-30T15:00:00+0300',
            True,
            True,
            5,
            14,
        ),
    ],
)
async def test_foxford_dialog_get_lesson_to_cancel_call_lesson_choose(
        web_context,
        state,
        expected_found_matched_lesson,
        expected_lesson_id,
        expected_dttm,
        expected_less_than_8_hours,
        expected_several_best_matches,
        expected_course_id,
        expected_agent_id,
):

    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = match_user_lesson.FindLesson(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )

    _state = await action(web_context, new_state)

    assert (
        _state.features.get('several_best_matches')
        == expected_several_best_matches
    )
    assert (
        _state.features.get('found_matched_lesson')
        is expected_found_matched_lesson
    )

    if not expected_several_best_matches:
        assert (
            _state.features.get('best_match_lesson_id') == expected_lesson_id
        )
        assert _state.features.get('best_match_lesson_dttm') == expected_dttm
        if expected_dttm:
            expected_formatted_dttm = datetime.datetime.strptime(
                expected_dttm, constants.DATETIME_FORMAT_FOR_API,
            ).strftime(constants.DATETIME_FORMAT_SHORT)
            assert (
                _state.features.get('best_match_lesson_dttm_formatted')
                == expected_formatted_dttm
            )

        assert (
            _state.features.get('best_match_less_than_8_hours')
            == expected_less_than_8_hours
        )


@pytest.mark.now('2021-11-30T10:00')
@pytest.mark.parametrize(
    'state,' 'expected_lesson_id, expected_dttm,' 'expected_short_format',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lessons_course_ids',
                            'value': [4, 5, 4, 5, 4],
                        },
                        {'key': 'lessons_ids', 'value': [10, 11, 12, 14, 13]},
                        {
                            'key': 'lessons_starts_ats',
                            'value': [
                                '2022-02-16T13:00:00+0300',
                                '2022-02-15T00:00:00+0300',
                                '2022-02-16T12:00:00+0300',
                                '2022-02-16T15:00:00+0300',
                                '2022-02-27T21:00:00+0300',
                            ],
                        },
                        {
                            'key': 'lessons_states',
                            'value': [
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                                'pending',
                            ],
                        },
                        {
                            'key': 'lessons_intros',
                            'value': [True, False, True, False],
                        },
                        {'key': 'course_ids', 'value': [4, 5]},
                        {'key': 'agent_ids', 'value': [13, 14]},
                        {
                            'key': 'course_names',
                            'value': ['Русский язык', 'Английский язык'],
                        },
                        {
                            'key': 'datetime_to_find',
                            'value': '2022-02-16T13:00+01:00',
                        },
                    ],
                ),
            ),
            14,
            '2022-02-16T15:00:00+0300',
            '16.02 в 13:00',
        ),
    ],
)
async def test_foxford_dialog_get_lesson_to_cancel_call_timezones(
        web_context,
        state,
        expected_lesson_id,
        expected_dttm,
        expected_short_format,
):
    action = match_user_lesson.FindLesson(PROJECT_NAME, ACTION_NAME, '0', [])

    _state = await action(web_context, state)

    assert _state.features.get('best_match_lesson_id') == expected_lesson_id
    assert _state.features.get('best_match_lesson_dttm') == expected_dttm

    assert (
        _state.features.get('best_match_lesson_dttm_formatted')
        == expected_short_format
    )
