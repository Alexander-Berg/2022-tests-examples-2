# -*- coding: utf-8 -*-
import json

from passport.backend.logbroker_client.oauth.exceptions import (
    OAuthPersistentError,
    OAuthRequestError,
    OAuthTemporaryError,
)
from passport.backend.logbroker_client.oauth.fake import FakeOAuth
from passport.backend.logbroker_client.oauth.oauth import OAuth
import pytest


oauth_fake = FakeOAuth()
oauth_fake.start()

oauth_client = OAuth('http://oauth', 3)


@pytest.fixture
def fake_oauth(request):
    oauth_fake = FakeOAuth()
    oauth_fake.start()

    def fin():
        oauth_fake.stop()
    request.addfinalizer(fin)
    return oauth_fake


def test_notify_valid(fake_oauth):
    fake_oauth.set_oauth_response_value(json.dumps({'status': 'ok'}), 200)
    oauth_client.refresh_token('125256075')


def test_notify_invalid_json_error(fake_oauth):
    fake_oauth.set_oauth_response_value('', 200)
    with pytest.raises(OAuthRequestError):
        oauth_client.refresh_token('125256075')


def test_notify_status_not_ok_error(fake_oauth):
    fake_oauth.set_oauth_response_value(json.dumps({'status': 'err'}), 200)
    with pytest.raises(OAuthRequestError):
        oauth_client.refresh_token('125256075')


def test_notify_persistent_error(fake_oauth):
    fake_oauth.set_oauth_response_value(json.dumps({'acl': 'reject'}), 400)
    with pytest.raises(OAuthPersistentError):
        oauth_client.refresh_token('123')


def test_notify_temporary_error(fake_oauth):
    fake_oauth.set_oauth_response_value(json.dumps({'error': 'database error'}), 500)
    with pytest.raises(OAuthTemporaryError):
        oauth_client.refresh_token('123')
