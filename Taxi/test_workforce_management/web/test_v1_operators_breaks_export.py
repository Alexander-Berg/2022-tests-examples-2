import csv
import io

import pytest


URI = 'v1/operators/breaks/export'
HEADERS = {'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators_schedule.sql', 'shifts_for_filtering.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_filename',
    [
        (
            {
                'datetime_from': '2020-08-01T00:00:00+03:00',
                'datetime_to': '2020-08-02T00:00:00+03:00',
                'skill': 'pokemon',
            },
            200,
            [
                [
                    'Логин',
                    'Доп',
                    'График',
                    'Начало смены',
                    'Конец смены',
                    'Перерыв 1',
                    'Перерыв 2',
                ],
                [
                    'chakchak',
                    'Нет',
                    'schedule_one',
                    '01.08.2020 09:00',
                    '01.08.2020 10:00',
                    'Перерыв 01.08.2020 09:15-01.08.2020 09:30',
                    'Перерыв 01.08.2020 09:45-01.08.2020 10:00',
                ],
            ],
            'Перерывы (pokemon) за (01.08.2020 00:00 - 02.08.2020 00:00)',
        ),
        (
            {
                'datetime_from': '2020-08-26 04:00:00.0 +0300',
                'datetime_to': '2020-08-26 23:00:00.0 +0300',
                'skill': 'order',
            },
            200,
            [
                [
                    'Логин',
                    'Доп',
                    'График',
                    'Начало смены',
                    'Конец смены',
                    'Перерыв 1',
                ],
                [
                    'abd-damir',
                    'Нет',
                    '5x2/10:00-00:00',
                    '26.08.2020 12:00',
                    '26.08.2020 18:00',
                    'Перерыв 26.08.2020 14:15-26.08.2020 14:30',
                ],
            ],
            'Перерывы (order) за (26.08.2020 04:00 - 26.08.2020 23:00)',
        ),
        (
            {
                'datetime_from': '2020-08-26 04:00:00.0 +0300',
                'datetime_to': '2022-08-29 23:00:00.0 +0300',
                'skill': 'order',
            },
            400,
            None,
            None,
        ),
    ],
)
async def test_breaks_export(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_filename,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    headers = res.headers
    assert headers['Content-Type'] == 'text/csv'
    assert (
        headers['Content-Disposition'] == f'attachment; '
        f'filename={expected_filename}.csv'
    )
    data = await res.text()
    string_io = io.StringIO(data)
    reader = list(csv.reader(string_io))

    assert reader == expected_res
