import pytest

from tracemalloc_api import client

DISABLED_RESPONSE = {
    'status': 'disabled',
    'tracemalloc_memory': 600,
    'traced_memory': {'current': 0, 'peak': 0},
    'traceback_limit': 1,
}
DISABLED_STRING = """Tracemalloc status: disabled
Traceback limit: 1 frame(s)
Traced memory:
\tCurrent: 0 B
\tPeak: 0 B
Tracemalloc overhead: 600.0 B"""

ENABLED_RESPONSE = {
    'status': 'enabled',
    'tracemalloc_memory': 65412,
    'traced_memory': {'current': 5232312, 'peak': 662124112},
    'traceback_limit': 5,
}
ENABLED_STRING = """Tracemalloc status: enabled
Traceback limit: 5 frame(s)
Traced memory:
\tCurrent: 5.0 MiB
\tPeak: 631.5 MiB
Tracemalloc overhead: 63.9 KiB"""


@pytest.mark.parametrize(
    'response,expected_string',
    [
        pytest.param(DISABLED_RESPONSE, DISABLED_STRING, id='disabled'),
        pytest.param(ENABLED_RESPONSE, ENABLED_STRING, id='enabled'),
    ],
)
def test_status_str(response, expected_string):
    status = client.TracingStatus.deserialize(response)

    assert str(status) == expected_string
