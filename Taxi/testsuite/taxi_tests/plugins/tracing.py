import pytest

from taxi_tests.utils import tracing


@pytest.fixture
def trace_id():
    return tracing.generate_trace_id()
