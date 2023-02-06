# -*- coding: utf-8 -*-
from functools import wraps
import json
import logging
import random
import string
import sys
import urllib.parse

from flask import (
    make_response,
    redirect,
)
from passport.backend.core.logging_utils.helpers import mask_sensitive_fields
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    TemporarilyUnavailableError,
    TestUserServiceException,
)
from passport.backend.qa.test_user_service.tus_api.request_id import get_request_id
from passport.backend.qa.test_user_service.tus_api.settings import SENSITIVE_FIELDS_TO_MASK
from passport.backend.utils.common import encode_query_mapping
from passport.backend.utils.string import smart_str


ESCAPABLE_URL_CHARACTERS = {c: urllib.parse.quote(c) for c in {'\n', '\r', ' '}}

log = logging.getLogger(__name__)


def random_numeric(n_digits):
    return ''.join(random.choice(string.digits) for _ in range(n_digits))


def random_alphanumeric(n_digits):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n_digits))


def retry_decorator(attempts=3, exception=Exception):
    if type(exception) == list:
        exception = tuple(exception)
    elif type(exception) != tuple:
        assert type(exception) == type, 'exception should be subclass of Exception'
        assert issubclass(exception, Exception), 'exception should be subclass of Exception'

    def decorator(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            for i in range(attempts - 1):
                try:
                    return f(*args, **kwargs)
                except exception as e:
                    log.debug('Retry(%d) %s after: %s' % (i + 1, f.__name__, str(e)))
            return f(*args, **kwargs)
        return _wrapper
    return decorator


def rename_exception_decorator(exception, new_exception):
    def _decorator(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exception as e:
                raise new_exception(str(e)).with_traceback(sys.exc_info()[2])
        return _wrapper
    return _decorator


def escape_query_characters_middleware(wsgi_app):
    """
    Экранирует символы в HTTP-Query.
    """
    @wraps(wsgi_app)
    def wrapper(environ, start_response):
        qs = environ.get('QUERY_STRING')
        if qs:
            new_qs = qs
            for esc_ch, repl in ESCAPABLE_URL_CHARACTERS.items():
                new_qs = new_qs.replace(esc_ch, repl)
            if new_qs != qs:
                log.debug(u'Escape CR/LF characters in query')
            environ['QUERY_STRING'] = new_qs
        return wsgi_app(environ, start_response)
    return wrapper


def json_response(data, return_code):
    log.info('Return code %d\tdata: %s' % (return_code, str(mask_sensitive_fields(data, SENSITIVE_FIELDS_TO_MASK))))
    return make_response(
        json.dumps(data, indent=4) + '\n',
        return_code,
        {'Content-Type': 'application/json'},
    )


def ok_response(**kwargs):
    return json_response(kwargs, 200)


def error_response(**kwargs):
    return json_response(kwargs, 400)


def get_exception_dict(e):
    if isinstance(e, TestUserServiceException):
        description = str(e)
        if e.error_description:
            description = e.error_description
        return dict(
            error=e.code,
            error_description=description,
        )
    return dict(error='server_error', error_description='%s: %s' % (type(e).__name__, str(e)))


def error_handler(e, **kwargs):
    response_data = dict(get_exception_dict(e), **kwargs)
    if isinstance(e, TestUserServiceException):
        log.debug('processing exception', exc_info=True)
        if isinstance(e, TemporarilyUnavailableError):
            return json_response(response_data, 503)
        return error_response(**response_data)
    log.exception('exception.unhandled')
    return json_response(response_data, 500)


def add_query_params_to_url(url, **params):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.query:
        args_pairs = urllib.parse.parse_qsl(smart_str(parsed_url.query, encoding='ascii', strings_only=True), keep_blank_values=True, strict_parsing=True)
        # merge into kwargs
        params = dict(args_pairs, **params)
    return urllib.parse.urlunparse([
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        urllib.parse.urlencode(encode_query_mapping(params)),
        parsed_url.fragment,
    ])


def redirect_with_args(url, **kwargs):
    url = add_query_params_to_url(url, **kwargs)
    log.debug('redirection to %s' % url)
    return redirect(url)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True


class TskvFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().startswith('tskv	')
