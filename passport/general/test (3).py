# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.misc import urlencode
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
)
from passport.backend.social.common.test.types import FakeResponse


def oauth1_temporary_credentials_response(token=APPLICATION_TOKEN1, token_secret=APPLICATION_TOKEN2):
    creds = [
        ('oauth_token', token),
        ('oauth_token_secret', token_secret),
        ('oauth_callback_confirmed', 'true'),
    ]
    encoded = urlencode(creds)
    return FakeResponse(encoded, 200)


def oauth1_token_credentials_response(token=APPLICATION_TOKEN1, token_secret=APPLICATION_TOKEN2):
    creds = [
        ('oauth_token', token),
        ('oauth_token_secret', token_secret),
    ]
    encoded = urlencode(creds)
    return FakeResponse(encoded, 200)
