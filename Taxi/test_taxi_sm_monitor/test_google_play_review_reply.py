# pylint: disable=protected-access,import-error,no-name-in-module
import datetime
import json
from os import path

from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient import http
import pytest

from taxi import discovery as taxi_discovery

from taxi_sm_monitor import stq_task


NOW = datetime.datetime(2019, 12, 30, 12, 45)


class GoodTestFinish(Exception):
    pass


@pytest.mark.config(SM_MONITOR_GOOGLE_PLAY_SEND_REPLY=True)
async def test_reply_review(
        taxi_sm_monitor_app_stq,
        patch_aiohttp_session,
        patch,
        response_mock,
        mock,
        monkeypatch,
):
    @patch_aiohttp_session(
        taxi_discovery.find_service('support_chat').url, 'POST',
    )
    def support_chat_api(method, url, **kwargs):
        return response_mock(
            json={
                'messages': [
                    {
                        'id': 'user_review',
                        'text': 'bad app',
                        'metadata': {'created': '2018-07-13T14:15:50+0000'},
                        'sender': {
                            'id': 'review_id_1',
                            'role': 'google_play_review',
                        },
                    },
                    {
                        'id': 'support_reply',
                        'text': 'No, it is a good app!',
                        'metadata': {'created': '2018-07-15T11:12:50+0000'},
                        'sender': {'id': 'some_support', 'role': 'support'},
                    },
                ],
                'metadata': {'google_play_app': 'ru.yandex.uber'},
                'participants': [
                    {'id': 'support', 'role': 'support'},
                    {'id': 'review_id_1', 'role': 'google_play_review'},
                ],
            },
        )

    @mock
    def _dummy_retry_request(*args, **kwargs):
        assert kwargs['body'] == '{"replyText": "No, it is a good app!"}'
        raise GoodTestFinish()

    monkeypatch.setattr(http, '_retry_request', _dummy_retry_request)

    @mock
    def _dummy_get_creds(*args, **kwargs):
        return service_account.Credentials(
            signer=None, service_account_email=None, token_uri=None,
        )

    monkeypatch.setattr(
        service_account.Credentials,
        'from_service_account_info',
        _dummy_get_creds,
    )

    @mock
    def _dummy_retrieve_service_doc(*args, **kwargs):
        service_path = path.join(
            path.dirname(__file__),
            'static',
            __file__.split('/')[-1].split('.')[0],
            'service_mock.json',
        )
        return json.load(open(service_path))

    monkeypatch.setattr(
        discovery, '_retrieve_discovery_doc', _dummy_retrieve_service_doc,
    )

    with pytest.raises(GoodTestFinish):
        await stq_task.google_play_review_reply(
            taxi_sm_monitor_app_stq, 'some_chat_id', 'support_reply',
        )

    assert support_chat_api.calls
    assert _dummy_retry_request.calls


@pytest.mark.now(NOW.isoformat())
async def test_set_new_stq_task(taxi_sm_monitor_app_stq, patch_stq_put):

    await stq_task.google_play_review_reply(
        taxi_sm_monitor_app_stq, 'some_chat_id', 'support_reply',
    )

    assert patch_stq_put.calls == [
        {
            'args': ('some_chat_id', 'support_reply'),
            'eta': NOW + datetime.timedelta(minutes=10),
            'kwargs': {'log_extra': None},
            'queue': 'taxi_sm_monitor_google_play',
            'task_id': None,
            'loop': None,
        },
    ]
