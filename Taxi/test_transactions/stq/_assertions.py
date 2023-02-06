import pytest


def assert_rescheduled_at(mock, expected, now):
    calls = mock.calls
    assert len(calls) == 1
    eta = calls[0]['eta']
    msg = f'{eta!r} != {expected!r}'
    expected_delta = (expected - now).total_seconds()
    actual_delta = (eta - now).total_seconds()
    assert actual_delta == pytest.approx(expected_delta), msg
