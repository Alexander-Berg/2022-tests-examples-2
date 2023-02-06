import datetime

import dateutil.parser

from tests_signal_device_api_admin import utils


def _check_cursors(cursor1, cursor2):
    if cursor1 is None and cursor2 is None:
        return

    assert cursor1 is not None and cursor2 is not None

    cursor1_decoded = utils.get_decoded_cursor(cursor1)
    cursor2_decoded = utils.get_decoded_cursor(cursor2)
    assert dateutil.parser.parse(cursor1_decoded) == dateutil.parser.parse(
        cursor2_decoded,
    )


def check_dashboard_chart_responses(response1, response2):
    assert len(response1['chart']) == len(response2['chart']), len(
        response1['chart'],
    ) - len(response2['chart'])
    _check_cursors(
        response1.get('cursor_before'), response2.get('cursor_before'),
    )
    _check_cursors(
        response1.get('cursor_after'), response2.get('cursor_after'),
    )
    for chart_elem1, chart_elem2 in zip(
            response1['chart'], response2['chart'],
    ):
        assert chart_elem1['critical'] == chart_elem2['critical']
        assert chart_elem1['non_critical'] == chart_elem2['non_critical']
        assert dateutil.parser.parse(
            chart_elem1['date'],
        ) == dateutil.parser.parse(chart_elem2['date'])


def get_dashboard_chart_response(
        *,
        chart_period_from,
        chart_period_to,
        chart_elems,
        timezone,
        is_cursor_before_needed=False,
        is_cursor_after_needed=False,
):
    """
    The purpose of this function is to to fill period
    with missing zeros elements, because I don't want to hardcode
    big responses where almost all elements in chart are zeros.
    """
    period_from = utils.convert_datetime_in_tz(chart_period_from, timezone)
    period_to = utils.convert_datetime_in_tz(chart_period_to, timezone)
    assert period_from < period_to
    assert period_to.month - period_from.month <= 1
    assert utils.is_datetime_start_day(period_from)
    assert utils.is_datetime_start_day(period_to)
    assert not is_cursor_before_needed or period_from.day == 1
    assert not is_cursor_after_needed or period_to.day == 1

    time_to_chart = {
        date: {'date': date.isoformat(), 'critical': 0, 'non_critical': 0}
        for date in (
            period_from + datetime.timedelta(days=days)
            for days in range((period_to - period_from).days)
        )
    }
    for chart_elem in chart_elems:
        chart_elem_date = utils.convert_datetime_in_tz(
            chart_elem['date'], timezone,
        )
        assert utils.is_datetime_start_day(chart_elem_date)
        if chart_elem_date in time_to_chart:
            time_to_chart[chart_elem_date] = chart_elem
    chart = sorted(
        time_to_chart.values(),
        key=lambda elem: dateutil.parser.parse(elem['date']),
    )

    response = {'chart': chart}
    if is_cursor_before_needed:
        # print('toencode=',period_from)
        response['cursor_before'] = utils.get_encoded_chart_cursor(period_from)
    if is_cursor_after_needed:
        response['cursor_after'] = utils.get_encoded_chart_cursor(period_to)
    return response
