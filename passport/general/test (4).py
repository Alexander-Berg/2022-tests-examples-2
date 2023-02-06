# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from passport.backend.social.common.test.consts import APPLICATION_TOKEN1
from passport.backend.social.common.test.types import FakeResponse


def build_error(error, error_description=None, error_uri=None, status_code=400):
    value = {'error': error}
    if error_description is not None:
        value['error_description'] = error_description
    if error_uri is not None:
        value['error_uri'] = error_uri
    return FakeResponse(
        value=json.dumps(value),
        status_code=status_code,
    )


def oauth2_access_token_response(access_token=APPLICATION_TOKEN1, token_type='bearer',
                                 expires_in=None, refresh_token=None, scope=None,
                                 extra=None):
    response = dict(token_type=token_type)
    if access_token is not None:
        response.update(dict(access_token=access_token))
    if expires_in is not None:
        response.update(dict(expires_in=expires_in))
    if refresh_token is not None:
        response.update(dict(refresh_token=refresh_token))
    if scope is not None:
        response.update(dict(scope=scope))
    if extra:
        response.update(extra)
    return FakeResponse(
        value=json.dumps(response),
        status_code=200,
    )
