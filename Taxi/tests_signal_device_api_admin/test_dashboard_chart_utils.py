from tests_signal_device_api_admin import dashboard_chart_utils
from tests_signal_device_api_admin import utils


def test_get_dashboard_chart_response():
    assert (
        dashboard_chart_utils.get_dashboard_chart_response(
            chart_period_from='2020-12-12T00:00:00+00:00',
            chart_period_to='2020-12-17T00:00:00+00:00',
            chart_elems=[
                {
                    'date': '2020-12-17T00:00:00+00:00',
                    'critical': 2,
                    'non_critical': 5,
                },
                {
                    'date': '2020-12-16T00:00:00+00:00',
                    'critical': 22,
                    'non_critical': 51,
                },
                {
                    'date': '2020-12-14T00:00:00+00:00',
                    'critical': 1,
                    'non_critical': 0,
                },
            ],
            timezone='UTC',
        )
        == {
            'chart': [
                {
                    'date': '2020-12-12T00:00:00+00:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-13T00:00:00+00:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-14T00:00:00+00:00',
                    'critical': 1,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-15T00:00:00+00:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-16T00:00:00+00:00',
                    'critical': 22,
                    'non_critical': 51,
                },
            ],
        }
    )
    assert (
        dashboard_chart_utils.get_dashboard_chart_response(
            chart_period_from='2020-12-11T21:00:00+00:00',
            chart_period_to='2020-12-16T21:00:00+00:00',
            chart_elems=[],
            timezone='Europe/Moscow',
        )
        == {
            'chart': [
                {
                    'date': '2020-12-12T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-13T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-14T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-15T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-16T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
            ],
        }
    )
    assert (
        dashboard_chart_utils.get_dashboard_chart_response(
            chart_period_from='2020-11-30T21:00:00+00:00',
            chart_period_to='2020-12-02T21:00:00+00:00',
            chart_elems=[],
            timezone='Europe/Moscow',
            is_cursor_before_needed=True,
        )
        == {
            'chart': [
                {
                    'date': '2020-12-01T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-12-02T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
            ],
            'cursor_before': utils.get_encoded_chart_cursor(
                '2020-12-01T00:00:00+03:00',
            ),
        }
    )
    assert (
        dashboard_chart_utils.get_dashboard_chart_response(
            chart_period_from='2020-11-28T21:00:00+00:00',
            chart_period_to='2020-11-30T21:00:00+00:00',
            chart_elems=[],
            timezone='Europe/Moscow',
            is_cursor_after_needed=True,
        )
        == {
            'chart': [
                {
                    'date': '2020-11-29T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
                {
                    'date': '2020-11-30T00:00:00+03:00',
                    'critical': 0,
                    'non_critical': 0,
                },
            ],
            'cursor_after': utils.get_encoded_chart_cursor(
                '2020-12-01T00:00:00+03:00',
            ),
        }
    )
    response_with_two_cursors = (
        dashboard_chart_utils.get_dashboard_chart_response(
            chart_period_from='2020-11-01T00:00:00+00:00',
            chart_period_to='2020-12-01T00:00:00+00:00',
            chart_elems=[],
            timezone='UTC',
            is_cursor_before_needed=True,
            is_cursor_after_needed=True,
        )
    )
    assert response_with_two_cursors[
        'cursor_before'
    ] == utils.get_encoded_chart_cursor('2020-11-01T00:00:00+00:00')
    assert response_with_two_cursors[
        'cursor_after'
    ] == utils.get_encoded_chart_cursor('2020-12-01T00:00:00+00:00')
