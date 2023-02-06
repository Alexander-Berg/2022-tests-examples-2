from __future__ import unicode_literals
import datetime

import pytest

from taxi_maintenance.stuff import calculate_support_metrics


@pytest.mark.parametrize(
    'start_time, end_time, expected_result',
    [
        (
            datetime.datetime(2018, 1, 1, 10, 10),
            datetime.datetime(2018, 1, 1, 10, 11),
            (1, 1)
        ),
        (
            datetime.datetime(2018, 2, 1, 10, 10),
            datetime.datetime(2018, 2, 1, 10, 11),
            (2, 3)
        ),
    ]
)
@pytest.inline_callbacks
def test_calc_chat_messages_metric(start_time, end_time, expected_result):
    result = yield calculate_support_metrics._calc_chat_messages_metric(
        start_time, end_time
    )
    assert result == expected_result


@pytest.mark.parametrize(
    'start_time, end_time, expected_result',
    [
        (
            datetime.datetime(2050, 1, 1, 10, 15),
            datetime.datetime(2050, 1, 1, 10, 16),
            0
        ),
        (
            datetime.datetime(2051, 1, 1, 15, 18),
            datetime.datetime(2051, 1, 1, 15, 19),
            2
        ),
    ]
)
@pytest.inline_callbacks
def test_calc_feedback_forms_metric(start_time, end_time, expected_result):
    result = yield calculate_support_metrics._calc_feedback_form_metric(
        start_time, end_time
    )
    assert result == expected_result


@pytest.mark.parametrize(
    'start_time, end_time, expected_result',
    [
        (
            datetime.datetime(2050, 1, 1, 10, 15),
            datetime.datetime(2050, 1, 1, 10, 16),
            (1, 0)
        ),
        (
            datetime.datetime(2050, 1, 1, 15, 18),
            datetime.datetime(2050, 1, 1, 15, 19),
            (2, 1)
        ),
    ]
)
@pytest.inline_callbacks
def test_calc_feedback_reports_metric(start_time, end_time, expected_result):
    result = yield calculate_support_metrics._calc_feedback_report_metric(
        start_time, end_time
    )
    assert result == expected_result
