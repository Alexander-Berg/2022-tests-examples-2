# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import datetime
from typing import Any
from typing import Dict

import pytest

from tests_passenger_feedback.plugins.mock_order_core import mock_order_core
from tests_passenger_feedback.plugins.mock_order_core import order_core


def default_save_request(order_id: str) -> dict:
    return {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'personal_phone_id': 'p_123456789012345678901234',
        'reorder_id': 'reorder_id',
        'rating': 3,
        'msg': 'message',
        'call_me': True,
        'app_comment': False,
        'created_time': '2018-08-10T21:01:30+0300',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'order_city': 'Москва',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'order_completed': False,
        'order_finished_for_client': True,
        'driver_license_pd_id': 'license_pd_id',
        'order_id': order_id,
        'badges': [{'type': 'rating_reason', 'value': 'pleasantmusic'}],
    }


@pytest.fixture(name='feedback_proposal_handle')
def feedback_proposal_fixture(taxi_passenger_feedback):
    async def _func(json_body: Dict[str, Any], headers: Dict[str, Any]):
        return await taxi_passenger_feedback.post(
            '/4.0/passenger-feedback/v1/feedback-proposal',
            json=json_body,
            headers=headers,
        )

    return _func


async def test_no_questions(feedback_proposal_handle, order_core_api):
    json_body = {'order_id': '12345'}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(filename='ride_quality_survey_exp.json')
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
        'question_key2': {'ru': 'Текст вопроса 2'},
        'answer_key3': {'ru': 'Ответ 3'},
        'answer_key4': {'ru': 'Ответ 4'},
    },
)
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
        ],
        'feedback_rating_mapping': [
            {
                'rating': 3,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic'],
            },
        ],
    },
)
@pytest.mark.parametrize('feedback_save', ['v2'], indirect=True)
@pytest.mark.parametrize('user_answers_to_survey', [True, False])
async def test_survey(
        feedback_proposal_handle,
        order_core_api,
        mongodb,
        feedback_save,
        user_answers_to_survey,
):

    order_id = '9b0ef3c5398b3e07b59f03110563479d'
    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert response['survey_info'] == [
        {
            'answer_options': [
                {'id': 'a_1', 'text': 'Ответ 1'},
                {'id': 'a_2', 'text': 'Ответ 2'},
            ],
            'question_id': 'q_1',
            'question_text': 'Текст вопроса',
        },
        {
            'answer_options': [
                {'id': 'a_3', 'text': 'Ответ 3'},
                {'id': 'a_4', 'text': 'Ответ 4'},
            ],
            'question_id': 'q_2',
            'question_text': 'Текст вопроса 2',
        },
    ]

    feedback = mongodb.feedbacks_mdb.find_one(order_id)
    feedback.pop('created', None)
    feedback.pop('data_updated', None)
    feedback.pop('updated', None)
    feedback.pop('udid', None)
    assert feedback == {
        '_id': order_id,
        'order_created': datetime.datetime(2017, 1, 1, 0, 0, 0),
        'survey': [{'question_id': 'q_1'}, {'question_id': 'q_2'}],
    }

    # check that we can save feedback correctly after saving question ids
    save_request = default_save_request(order_id)
    result = await feedback_save.call(
        save_request, 200, user_answers_to_survey,
    )
    assert order_core_api.times_called == 1

    expected_survey = (
        [{'answer_id': 'a_1', 'question_id': 'q_1'}]
        if user_answers_to_survey
        else [{'question_id': 'q_1'}, {'question_id': 'q_2'}]
    )

    assert result.feedback == {
        'created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'data_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'order_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        '_id': '9b0ef3c5398b3e07b59f03110563479d',
        'reorder_id': 'reorder_id',
        'data': {
            'rating': 3,
            'call_me': True,
            'choices': [
                {'type': 'rating_reason', 'value': 'pleasantmusic'},
                {'type': 'low_rating_reason', 'value': 'rudedriver'},
            ],
            'app_comment': False,
            'is_after_complete': False,
            'msg': 'message',
        },
        'survey': expected_survey,
        'user_id': 'user_id',
        'user_phone_id': '123456789012345678901234',
        'wanted': False,
        'udid': 'udid00',
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(filename='ride_quality_survey_exp.json')
async def test_no_survey_selfdriving(feedback_proposal_handle, order_core_api):
    order_id = 'no_feedback_for_selfdriving'
    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert response == {'survey_info': []}


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(filename='ride_quality_survey_exp.json')
@pytest.mark.translations(
    client_messages={
        'question_key2': {'ru': 'Текст вопроса 2'},
        'answer_key3': {'ru': 'Ответ 3'},
        'answer_key4': {'ru': 'Ответ 4'},
    },
)
async def test_question_only_for_selected_tariffs(
        feedback_proposal_handle, order_core_api,
):
    order_id = 'excluded_tariff'
    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert response['survey_info'] == [
        {
            'answer_options': [
                {'id': 'a_3', 'text': 'Ответ 3'},
                {'id': 'a_4', 'text': 'Ответ 4'},
            ],
            'question_id': 'q_2',
            'question_text': 'Текст вопроса 2',
        },
    ]


@pytest.mark.experiments3(filename='ride_quality_survey_exp.json')
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
        'question_key2': {'ru': 'Текст вопроса 2'},
    },
)
async def test_no_some_tanker_keys(feedback_proposal_handle, order_core_api):

    json_body = {'order_id': '9b0ef3c5398b3e07b59f03110563479d'}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert response['survey_info'] == [
        {
            'answer_options': [
                {'id': 'a_1', 'text': 'Ответ 1'},
                {'id': 'a_2', 'text': 'Ответ 2'},
            ],
            'question_id': 'q_1',
            'question_text': 'Текст вопроса',
        },
    ]


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(filename='ride_quality_survey_exp.json')
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
        'question_key2': {'ru': 'Текст вопроса 2'},
        'answer_key3': {'ru': 'Ответ 3'},
        'answer_key4': {'ru': 'Ответ 4'},
    },
)
@pytest.mark.parametrize(
    ['order_id', 'expected_survey'],
    [
        (
            'already_saved_feedback_with_survey',
            [
                {'question_id': 'q_1', 'answer_id': 'a_1'},
                {'question_id': 'q_2', 'answer_id': 'a_2'},
            ],
        ),
        (
            'already_saved_feedback_without_survey',
            [{'question_id': 'q_1'}, {'question_id': 'q_2'}],
        ),
    ],
)
async def test_no_conflicts_with_saved_feedback(
        feedback_proposal_handle,
        order_core_api,
        mongodb,
        order_id,
        expected_survey,
):

    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert response['survey_info'] == [
        {
            'answer_options': [
                {'id': 'a_1', 'text': 'Ответ 1'},
                {'id': 'a_2', 'text': 'Ответ 2'},
            ],
            'question_id': 'q_1',
            'question_text': 'Текст вопроса',
        },
        {
            'answer_options': [
                {'id': 'a_3', 'text': 'Ответ 3'},
                {'id': 'a_4', 'text': 'Ответ 4'},
            ],
            'question_id': 'q_2',
            'question_text': 'Текст вопроса 2',
        },
    ]

    feedback = mongodb.feedbacks_mdb.find_one(order_id)
    if 'updated' in feedback:
        feedback.pop('updated')
    if 'data_updated' in feedback:
        feedback.pop('data_updated')
    if 'udid' in feedback:
        feedback.pop('udid')

    expected_feedback = {
        '_id': order_id,
        'created': datetime.datetime(2017, 1, 1, 0, 0),
        'survey': expected_survey,
        'order_completed': datetime.datetime(2017, 1, 1, 0, 0),
        'order_created': datetime.datetime(2017, 1, 1, 0, 0),
        'order_due': datetime.datetime(2017, 1, 1, 0, 0),
        'park_id': 'park_id',
        'reorder_id': 'reorder_id',
        'user_id': 'user_id',
        'user_phone_id': '123456789012345678901234',
        'wanted': True,
    }
    assert feedback == expected_feedback


def get_current_questions_db(pgsql):
    cursor = pgsql['passenger_feedback'].cursor()
    cursor.execute(
        (
            f'SELECT udid, current_question_id '
            f'FROM passenger_feedback.current_questions'
        ),
    )
    return list(cursor)


@pytest.mark.pgsql('passenger_feedback', files=['pg_feedback_proposal.sql'])
@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(
    filename='ride_quality_survey_questions_engine_exp.json',
)
@pytest.mark.parametrize(
    ['order_id', 'expected_cur_questions_db', 'expected_response_question'],
    [
        (
            'udid00_order_id',
            [
                ('udid01', 'q_1'),
                ('udid02', 'pleasent music'),
                ('udid03', 'q_1'),
                ('udid00', 'q_2'),
            ],
            'q_2',
        ),
        (
            'udid01_order_id',
            [
                ('udid00', 'q_1'),
                ('udid00', 'q_2'),
                ('udid01', 'q_1'),
                ('udid02', 'pleasent music'),
                ('udid03', 'q_1'),
            ],
            'q_1',
        ),
        (
            'udid02_order_id',
            [
                ('udid00', 'q_1'),
                ('udid00', 'q_2'),
                ('udid01', 'q_1'),
                ('udid03', 'q_1'),
                ('udid02', 'q_2'),
            ],
            'q_2',
        ),
        (
            'udid03_order_id',
            [
                ('udid00', 'q_1'),
                ('udid00', 'q_2'),
                ('udid01', 'q_1'),
                ('udid02', 'pleasent music'),
                ('udid03', 'q_1'),
            ],
            'q_1',
        ),
        (
            'udid04_order_id',
            [
                ('udid00', 'q_1'),
                ('udid00', 'q_2'),
                ('udid01', 'q_1'),
                ('udid02', 'pleasent music'),
                ('udid03', 'q_1'),
                ('udid04', 'q_2'),
            ],
            'q_2',
        ),
    ],
    ids=[
        'negative, positive, positive',
        'positive',
        'question doesn\'t exist in experiment',
        'positive, negative',
        'driver doesn\'t exist in experiment',
    ],
)
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
        'question_key2': {'ru': 'Текст вопроса 2'},
        'answer_key3': {'ru': 'Ответ 3'},
        'answer_key4': {'ru': 'Ответ 4'},
    },
)
async def test_smart_question_picker_cur_question(
        feedback_proposal_handle,
        pgsql,
        order_core_api,
        order_id,
        expected_cur_questions_db,
        expected_response_question,
):
    expected_initial_db = [
        ('udid00', 'q_1'),
        ('udid00', 'q_2'),
        ('udid01', 'q_1'),
        ('udid02', 'pleasent music'),
        ('udid03', 'q_1'),
    ]

    assert expected_initial_db == get_current_questions_db(pgsql)

    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert (
        response['survey_info'][0]['question_id'] == expected_response_question
    )
    assert expected_cur_questions_db == get_current_questions_db(pgsql)


def get_questions_history_db(pgsql):
    cursor = pgsql['passenger_feedback'].cursor()
    cursor.execute(
        (
            f'SELECT udid , question_id, answer_ids, answer_values '
            f'FROM passenger_feedback.questions_history'
        ),
    )
    return list(cursor)


def get_update_at_from_db(pgsql):
    cursor = pgsql['passenger_feedback'].cursor()
    cursor.execute(
        (f'SELECT updated_at ' f'FROM passenger_feedback.questions_history'),
    )
    return list(cursor)


@pytest.mark.pgsql('passenger_feedback', files=['pg_feedback_proposal.sql'])
@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(
    filename='ride_quality_survey_questions_engine_exp.json',
)
@pytest.mark.parametrize(
    ['order_id', 'expected_cur_questions_db', 'expected_history_questions_db'],
    [
        (
            'udid00_order_id',
            [
                ('udid01', 'q_1'),
                ('udid02', 'pleasent music'),
                ('udid03', 'q_1'),
                ('udid00', 'q_2'),
            ],
            [
                ('udid02', 'pleasent music', ['positive', 'positive'], [1, 1]),
                (
                    'udid00',
                    'q_1',
                    ['negative', 'positive', 'positive'],
                    [0, 1, 1],
                ),
            ],
        ),
        (
            'udid02_order_id',
            [
                ('udid00', 'q_1'),
                ('udid00', 'q_2'),
                ('udid01', 'q_1'),
                ('udid03', 'q_1'),
                ('udid02', 'q_2'),
            ],
            [
                (
                    'udid02',
                    'pleasent music',
                    ['positive', 'positive', 'negative'],
                    [1, 1, 0],
                ),
            ],
        ),
    ],
    ids=['simple', 'concat'],
)
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
        'question_key2': {'ru': 'Текст вопроса 2'},
        'answer_key3': {'ru': 'Ответ 3'},
        'answer_key4': {'ru': 'Ответ 4'},
    },
)
async def test_smart_question_picker_save_question(
        feedback_proposal_handle,
        pgsql,
        order_core_api,
        order_id,
        expected_cur_questions_db,
        expected_history_questions_db,
):
    expected_initial_db = [
        ('udid00', 'q_1'),
        ('udid00', 'q_2'),
        ('udid01', 'q_1'),
        ('udid02', 'pleasent music'),
        ('udid03', 'q_1'),
    ]
    assert expected_initial_db == get_current_questions_db(pgsql)

    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert expected_cur_questions_db == get_current_questions_db(pgsql)
    assert expected_history_questions_db == get_questions_history_db(pgsql)


@pytest.mark.pgsql('passenger_feedback', files=['pg_feedback_proposal.sql'])
@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(
    filename='ride_quality_survey_questions_engine_exp.json',
)
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
        'question_key2': {'ru': 'Текст вопроса 2'},
        'answer_key3': {'ru': 'Ответ 3'},
        'answer_key4': {'ru': 'Ответ 4'},
    },
)
async def test_smart_question_picker_save_question_update_time(
        feedback_proposal_handle, pgsql, order_core_api,
):
    expected_initial_db = [
        ('udid00', 'q_1'),
        ('udid00', 'q_2'),
        ('udid01', 'q_1'),
        ('udid02', 'pleasent music'),
        ('udid03', 'q_1'),
    ]
    assert expected_initial_db == get_current_questions_db(pgsql)

    json_body = {'order_id': 'udid02_order_id'}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200

    updated_at = get_update_at_from_db(pgsql)[0][0]
    assert updated_at >= datetime.datetime.now(
        updated_at.tzinfo,
    ) - datetime.timedelta(minutes=9)


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(
    filename='ride_quality_survey_questions_engine_exp.json',
)
@pytest.mark.translations(
    client_messages={
        'question_key1': {'ru': 'Текст вопроса'},
        'answer_key1': {'ru': 'Ответ 1'},
        'answer_key2': {'ru': 'Ответ 2'},
    },
)
async def test_smart_question_picker_only_for_selected_tariffs(
        feedback_proposal_handle, order_core_api,
):
    order_id = 'excluded_tariff'
    json_body = {'order_id': order_id}
    headers = ({'X-Yandex-Uid': '123456', 'X-YaTaxi-UserId': 'testsuite'},)
    response = await feedback_proposal_handle(json_body, headers)
    assert response.status_code == 200
    response = response.json()
    assert response['survey_info'] == [
        {
            'answer_options': [
                {'id': 'a_1', 'text': 'Ответ 1'},
                {'id': 'a_2', 'text': 'Ответ 2'},
            ],
            'question_id': 'q_1',
            'question_text': 'Текст вопроса',
        },
    ]
