import typing


class Params(typing.NamedTuple):
    request: typing.Any
    status: int = 200
    response: typing.Any = None


def make_request_error(reason):
    return {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {'reason': reason},
    }


def make_internal_error(reason):
    return {
        'code': 'INTERNAL_SERVER_ERROR',
        'message': 'Internal server error',
        'details': {'reason': reason},
    }


def make_response_error(reason):
    return {
        'code': 'RESPONSE_VALIDATION_ERROR',
        'message': 'Response validation or serialization failed',
        'details': {'reason': reason},
    }


def get_request_response(caplog):
    request_log = response_log = None
    for log_record in caplog.records:
        if not hasattr(log_record, 'extdict'):
            continue
        if log_record.extdict.get('_type') == 'request':
            request_log = log_record
        if log_record.extdict.get('_type') == 'response':
            response_log = log_record
    assert request_log is not None
    assert response_log is not None
    return request_log, response_log
