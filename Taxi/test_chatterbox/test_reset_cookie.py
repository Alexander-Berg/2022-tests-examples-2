# pylint: disable=no-self-use,unused-variable
import collections
import http

import blackbox
import pytest


@pytest.mark.now('2018-06-28T14:45:00+0300')
@pytest.mark.config(TVM_ENABLED=True)
async def test_reset_cookie(
        cbox, monkeypatch, patch_aiohttp_session, response_mock,
):
    class BlackboxSessionMock:
        def __init__(self):
            self.valid = True
            self.secure = True
            self.status = 'NEED_RESET'
            self.fields = collections.namedtuple(
                'fields', ['default_avatar_id', 'login', 'display_name'],
            )('', 'testuser', '')

        def get(self, *args):
            return ''

    class DummyBlackbox:
        TIMEOUT = 2
        RETRY_INTERVAL = 0.5

        def __init__(self, *args, **kwargs):
            self.timeout = self.TIMEOUT

        def sessionid(self, *args, **kwargs):
            return BlackboxSessionMock()

    monkeypatch.setattr(blackbox, 'Blackbox', DummyBlackbox)

    cbox.set_user('some_user')
    cbox.app.settings.BLACKBOX_AUTH = True

    headers = {'X-Real-Ip': '1.1.1.1'}

    disallowed_paths = {
        '/v1/lines/available': {},
        '/v1/tasks/take/': {},
        '/v1/tasks/search/': {},
        '/v1/tasks/123/show_hidden_comments': {},
        '/v1/tasks/123/hidden_comment/': {'hidden_comment': 'test'},
        '/v1/tasks/123/comment/': {'comment': 'test'},
        '/v1/tasks/123/forward/?line=corp': {},
        '/v1/tasks/123/defer/?reopen_at=123': {'comment': 'test'},
        '/v1/tasks/123/close/': {'comment': 'test'},
        '/v1/tasks/123/dismiss/?chatterbox_button=chatterbox_eng': {},
        '/v1/tasks/123/export/?chatterbox_button=chatterbox_eng': {},
        '/v1/stat/chats_by_user/123': {},
        '/v1/stat/chats_by_supporter': {},
        '/v1/stat/chats_by_status': {},
        '/v1/stat/supporters_count': {},
        '/v1/stat/supporters_online': {},
        '/v1/stat/actions': {'day': '2018-10-30'},
        '/v1/stat/actions_detailed': {},
        '/v1/stat/actions_by_supporter': {'day': '2018-10-30'},
    }
    for path, data in disallowed_paths.items():
        await cbox.post(path, data=data, headers=headers)
        assert cbox.status in {
            http.HTTPStatus.UNAUTHORIZED,
            http.HTTPStatus.FORBIDDEN,
        }
