import uuid

TRACE_ID_HEADER = 'X-YaTraceId'
SPAN_ID_HEADER = 'X-YaSpanId'

TRACE_ID_PREFIX = 'testsuite-'


def generate_trace_id():
    return TRACE_ID_PREFIX + uuid.uuid4().hex


def is_from_client_fixture(trace_id: str):
    return trace_id is not None and trace_id.startswith(TRACE_ID_PREFIX)


def is_other_test(trace_id: str, current_trace_id: str):
    return trace_id != current_trace_id and is_from_client_fixture(trace_id)
