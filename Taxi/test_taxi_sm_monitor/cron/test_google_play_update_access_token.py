# pylint: disable=redefined-outer-name
import pytest

from taxi_sm_monitor.crontasks import google_play_update_access_token


@pytest.mark.config(SM_MONITOR_GOOGLE_PLAY_LOAD_REVIEWS=True)
async def test_pagination(
        taxi_sm_monitor_app_stq, sm_monitor_context, loop, patch,
):
    @patch(
        'taxi_sm_monitor.crontasks.google_play_update_access_token.'
        '_get_new_token',
    )
    def _dummy_get_new_token(*args, **kwargs):
        return 'new_token'

    reviews_state = (
        await taxi_sm_monitor_app_stq.db.google_play_reviews_state.find_one(
            {'package_name': 'ru.yandex.uber'},
        )
    )
    assert 'access_token' not in reviews_state

    await google_play_update_access_token.do_stuff(sm_monitor_context, loop)

    reviews_state = (
        await taxi_sm_monitor_app_stq.db.google_play_reviews_state.find_one(
            {'package_name': 'ru.yandex.uber'},
        )
    )
    assert reviews_state['access_token'] == 'new_token'
