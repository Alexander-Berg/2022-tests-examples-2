import datetime

import pytest

from taxi.util import csrf


CSRF_SECRET = 'secret'
CSRF_TOKEN_TTL = 60 * 60  # one hour in seconds
DEFAULT_UID = '0'


def get_timestamp(*args, **kwargs):
    return int(datetime.datetime(*args, **kwargs).timestamp())


def get_token(*args, **kwargs):
    return csrf.get_token(
        'yandexuid', CSRF_SECRET, get_timestamp(*args, **kwargs), DEFAULT_UID,
    )


@pytest.mark.parametrize(
    'token_or_time, yandexuid, uid, expected_exception',
    [
        (
            # valid token
            (2008, 8, 8, 11),
            'yandexuid',
            DEFAULT_UID,
            None,
        ),
        (
            # valid token
            (2008, 8, 8, 11, 30),
            'yandexuid',
            DEFAULT_UID,
            None,
        ),
        (
            # token is expired
            (2008, 8, 8, 10, 59),
            'yandexuid',
            DEFAULT_UID,
            csrf.ExpiredTokenError,
        ),
        (
            # token from future
            (2008, 8, 8, 13),
            'yandexuid',
            DEFAULT_UID,
            None,
        ),
        (
            # bad timestamp
            csrf.get_token('yandexuid', CSRF_SECRET, 'bad_timestamp'),
            'yandexuid',
            DEFAULT_UID,
            csrf.InvalidTokenError,
        ),
        (
            # no timestamp
            'some_hash',
            'yandexuid',
            DEFAULT_UID,
            csrf.InvalidTokenError,
        ),
        (
            # different yandexuid
            (2008, 8, 8, 11),
            'other_yandexuid',
            DEFAULT_UID,
            csrf.InvalidTokenError,
        ),
        (
            # different uid
            (2008, 8, 8, 11),
            'yandexuid',
            'other_uid',
            csrf.InvalidTokenError,
        ),
    ],
)
@pytest.mark.now('2008-08-08T12:00:00')
@pytest.mark.nofilldb()
def test_check_csrf_token(token_or_time, yandexuid, uid, expected_exception):
    if isinstance(token_or_time, tuple):
        token = get_token(*token_or_time)
    else:
        token = token_or_time

    try:
        csrf.check_csrf_token(
            token, yandexuid, CSRF_SECRET, CSRF_TOKEN_TTL, uid,
        )
    except Exception as exc:  # pylint: disable=broad-except
        result_exc = exc
    else:
        result_exc = None

    if expected_exception:
        assert isinstance(result_exc, expected_exception)
    else:
        assert result_exc is None
