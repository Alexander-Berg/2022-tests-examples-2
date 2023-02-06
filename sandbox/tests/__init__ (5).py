from __future__ import absolute_import, print_function, unicode_literals

import uuid

from sandbox.common import auth as common_auth


def check_custom_str(obj):
    assert 'at 0x' not in str(obj)


SECRET_A = uuid.uuid4().hex
SECRET_B = uuid.uuid4().hex
SECRET_C = uuid.uuid4().hex


class TestAuth(object):

    def test__noauth(self):
        auth = common_auth.NoAuth()
        assert dict(auth) == {}
        check_custom_str(auth)

    def test__plain(self):
        auth = common_auth.Plain(auth_token=SECRET_A)
        assert dict(auth) == {"Authorization": SECRET_A}
        check_custom_str(auth)

    def test__oauth(self):
        auth = common_auth.OAuth(token=SECRET_A)
        assert auth.token == SECRET_A
        assert dict(auth) == {"Authorization": "OAuth {}".format(SECRET_A)}
        check_custom_str(auth)

    def test__groupoauth(self):
        auth = common_auth.GroupOAuth(token=SECRET_A)
        assert auth.token == SECRET_A
        assert dict(auth) == {"Authorization": "OAuthTeam {}".format(SECRET_A)}
        check_custom_str(auth)

    def test__yandexsession(self):
        auth = common_auth.YandexSession(session_id=SECRET_A)
        assert auth.session_id == SECRET_A
        assert dict(auth) == {"Cookie": "Session_id={}".format(SECRET_A)}
        check_custom_str(auth)

    def test__session(self):

        auth = common_auth.Session(user_token=SECRET_A, task_token=SECRET_B)
        assert auth.user_token == SECRET_A
        assert auth.task_token == SECRET_B

        auth.task_token = SECRET_C
        assert auth.task_token == SECRET_C

        assert dict(auth) == {"Authorization": "OAuth {}".format(SECRET_C)}
        check_custom_str(auth)

        delattr(auth, "task_token")
        assert auth.task_token is None

        assert dict(auth) == {"Authorization": "OAuth {}".format(SECRET_A)}
        check_custom_str(auth)

        assert dict(common_auth.Session(None, None)) == {}

    def test__tvmsession(self):

        auth = common_auth.TVMSession(service_ticket=SECRET_A)

        assert dict(auth) == {"X-Ya-Service-Ticket": SECRET_A}
        check_custom_str(auth)

        auth = common_auth.TVMSession(service_ticket=SECRET_A, user_ticket=SECRET_B)

        assert dict(auth) == {"X-Ya-User-Ticket": SECRET_B, "X-Ya-Service-Ticket": SECRET_A}
        check_custom_str(auth)
