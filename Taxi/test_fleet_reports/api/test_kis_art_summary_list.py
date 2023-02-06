import pytest

DATA = [
    {
        'active_drivers_count': 100,
        'drivers_with_permanent_id_count': 31,
        'drivers_with_permanent_id_percent': 31.0,
        'drivers_with_requested_id_count': 30,
        'drivers_with_requested_id_percent': 30.0,
        'drivers_with_temporary_id_count': 30,
        'drivers_with_temporary_id_percent': 30.0,
        'drivers_with_failed_id_count': 2,
        'drivers_with_failed_id_percent': 2.0,
        'drivers_without_id_count': 7,
        'drivers_without_id_percent': 7.0,
        'report_date': '2020-01-05',
    },
    {
        'active_drivers_count': 200,
        'drivers_with_permanent_id_count': 33,
        'drivers_with_permanent_id_percent': 16.5,
        'drivers_with_requested_id_count': 15,
        'drivers_with_requested_id_percent': 7.5,
        'drivers_with_temporary_id_count': 30,
        'drivers_with_temporary_id_percent': 15.0,
        'drivers_with_failed_id_count': 15,
        'drivers_with_failed_id_percent': 7.5,
        'drivers_without_id_count': 107,
        'drivers_without_id_percent': 53.5,
        'report_date': '2020-01-04',
    },
    {
        'active_drivers_count': 200,
        'drivers_with_permanent_id_count': 33,
        'drivers_with_permanent_id_percent': 16.5,
        'drivers_with_requested_id_count': 30,
        'drivers_with_requested_id_percent': 15.0,
        'drivers_with_temporary_id_count': 30,
        'drivers_with_temporary_id_percent': 15.0,
        'drivers_with_failed_id_count': 0,
        'drivers_with_failed_id_percent': 0.0,
        'drivers_without_id_count': 107,
        'drivers_without_id_percent': 53.5,
        'report_date': '2020-01-03',
    },
    {
        'active_drivers_count': 200,
        'drivers_with_permanent_id_count': 33,
        'drivers_with_permanent_id_percent': 16.5,
        'drivers_with_requested_id_count': 30,
        'drivers_with_requested_id_percent': 15.0,
        'drivers_with_temporary_id_count': 20,
        'drivers_with_temporary_id_percent': 10.0,
        'drivers_with_failed_id_count': 10,
        'drivers_with_failed_id_percent': 5.0,
        'drivers_without_id_count': 107,
        'drivers_without_id_percent': 53.5,
        'report_date': '2020-01-02',
    },
    {
        'active_drivers_count': 200,
        'drivers_with_permanent_id_count': 33,
        'drivers_with_permanent_id_percent': 16.5,
        'drivers_with_requested_id_count': 30,
        'drivers_with_requested_id_percent': 15.0,
        'drivers_with_temporary_id_count': 30,
        'drivers_with_temporary_id_percent': 15.0,
        'drivers_with_failed_id_count': 0,
        'drivers_with_failed_id_percent': 0.0,
        'drivers_without_id_count': 107,
        'drivers_without_id_percent': 53.5,
        'report_date': '2020-01-01',
    },
]


@pytest.mark.pgsql('fleet_reports', files=['kis_art_summary_data.sql'])
async def test_ok_simple(web_app_client, headers):
    response = await web_app_client.post(
        '/reports-api/v1/summaries/kis-art/list',
        headers={**headers, 'X-Park-Id': 'pid1'},
        json={'limit': 2},
    )
    assert response.status == 200
    assert await response.json() == {
        'cursor': 'MjAyMC0wMS0wMw==',
        'summaries': DATA[:2],
    }

    response = await web_app_client.post(
        '/reports-api/v1/summaries/kis-art/list',
        headers={**headers, 'X-Park-Id': 'pid1'},
        json={'limit': 3, 'cursor': 'MjAyMC0wMS0wMw=='},
    )
    assert response.status == 200
    assert await response.json() == {
        'cursor': 'MjAxOS0xMi0zMQ==',
        'summaries': DATA[2:5],
    }

    response = await web_app_client.post(
        '/reports-api/v1/summaries/kis-art/list',
        headers={**headers, 'X-Park-Id': 'pid1'},
        json={'limit': 3, 'cursor': 'MjAxOS0xMi0zMQ=='},
    )
    assert response.status == 200
    assert await response.json() == {'summaries': []}


@pytest.mark.parametrize(
    'from_, to_, lower_b, upper_b',
    [
        ('2020-01-01', '2021-01-01', 0, len(DATA)),
        ('2020-01-03', '2020-01-04', 1, 3),
        ('2020-01-03', '2020-02-01', 0, 3),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=['kis_art_summary_data.sql'])
async def test_limits(web_app_client, headers, from_, to_, lower_b, upper_b):
    response = await web_app_client.post(
        '/reports-api/v1/summaries/kis-art/list',
        headers={**headers, 'X-Park-Id': 'pid1'},
        json={
            'limit': 10,
            'date_from_inclusive': from_,
            'date_to_inclusive': to_,
        },
    )
    assert response.status == 200
    assert await response.json() == {'summaries': DATA[lower_b:upper_b]}
