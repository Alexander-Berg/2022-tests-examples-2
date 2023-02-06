from collections import namedtuple


Header = namedtuple('Header', ['name', 'code_for_error', 'allow_empty_value'])

HEADER_CONSUMER_AUTHORIZATION = Header(
    name='Authorization',
    code_for_error='authorization',
    allow_empty_value=False,
)

HEADER_FORWARDED_FOR = Header(
    name='X-Forwarded-For',
    code_for_error='client_ip',
    allow_empty_value=False,
)

HEADER_SERVICE_TICKET = Header(
    name='X-Ya-Service-Ticket',
    code_for_error='service_ticket',
    allow_empty_value=False,
)

HEADER_X_REQ_ID = Header(
    name='X-Req-Id',
    code_for_error='request_id',
    allow_empty_value=False,
)

HEADER_IDM_X_REQ_ID = Header(
    name='X-IDM-Request-Id',
    code_for_error='idm_request_id',
    allow_empty_value=False,
)

__all__ = (
    'HEADER_CONSUMER_AUTHORIZATION',
    'HEADER_FORWARDED_FOR',
    'HEADER_SERVICE_TICKET',
    'HEADER_X_REQ_ID',
    'HEADER_IDM_X_REQ_ID'
)
