# pylint: disable=C5521
from datetime import datetime

import pytest

from tests_grocery_goals import common
from tests_grocery_goals import models

DATE_NOW = '2020-02-26T18:12:00+00:00'


@pytest.mark.now(DATE_NOW)
async def test_goals_finish_push(
        taxi_grocery_goals, pgsql, stq_runner, mockserver,
):
    title_tanker_key = common.GOAL_PUSH_INFO['finish_title_tanker_key']
    text_tanker_key = common.GOAL_PUSH_INFO['finish_message_tanker_key']
    goal_id = common.GOAL_ID
    yandex_uid = common.YANDEX_UID
    taxi_user_id = 'taxi_user_id'
    locale = 'ru'
    idempotency_token = 'idempotency_token'
    application = 'lavka_iphone'
    push_args = {'some_args': 'args'}

    models.insert_goal_progress(pgsql)

    @mockserver.json_handler(
        '/grocery-communications/internal/communications/v1/goal/finish',
    )
    def _mock_goal_finish(request):
        assert request.json == {
            'title_tanker_key': title_tanker_key,
            'text_tanker_key': text_tanker_key,
            'goal_id': goal_id,
            'taxi_user_id': taxi_user_id,
            'yandex_uid': yandex_uid,
            'eats_user_id': common.EATS_USER_ID,
            'locale': locale,
            'idempotency_token': idempotency_token,
            'application': application,
            'push_args': push_args,
        }
        return {}

    await stq_runner.grocery_goals_finish_push.call(
        task_id='task_id',
        kwargs={
            'args': {
                'title_tanker_key': title_tanker_key,
                'message_tanker_key': text_tanker_key,
                'goal_id': goal_id,
                'taxi_user_id': taxi_user_id,
                'yandex_uid': yandex_uid,
                'eats_user_id': common.EATS_USER_ID,
                'locale': locale,
                'idempotency_token': idempotency_token,
                'application': application,
                'push_args': push_args,
            },
        },
    )

    goal_progress = models.get_goal_progress(pgsql, yandex_uid, goal_id)
    assert goal_progress.completed_push_time == datetime.fromisoformat(
        DATE_NOW,
    )


@pytest.mark.now(DATE_NOW)
async def test_communications_error(
        taxi_grocery_goals, pgsql, stq_runner, mockserver,
):
    goal_id = common.GOAL_ID
    yandex_uid = common.YANDEX_UID

    models.insert_goal_progress(pgsql)

    @mockserver.json_handler(
        '/grocery-communications/internal/communications/v1/goal/finish',
    )
    def _mock_goal_finish(request):
        return mockserver.make_response(status=500)

    await stq_runner.grocery_goals_finish_push.call(
        task_id='task_id',
        expect_fail=True,
        kwargs={
            'args': {
                'title_tanker_key': common.GOAL_PUSH_INFO[
                    'finish_title_tanker_key'
                ],
                'message_tanker_key': common.GOAL_PUSH_INFO[
                    'finish_message_tanker_key'
                ],
                'goal_id': goal_id,
                'taxi_user_id': 'taxi_user_id',
                'yandex_uid': yandex_uid,
                'locale': 'ru',
                'idempotency_token': 'idempotency_token',
                'application': 'lavka_iphone',
                'push_args': {'some_args': 'args'},
            },
        },
    )

    goal_progress = models.get_goal_progress(pgsql, yandex_uid, goal_id)
    assert not goal_progress.completed_push_time
