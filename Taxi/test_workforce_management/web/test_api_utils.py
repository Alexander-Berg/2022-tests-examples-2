import pytest


JOB_SETUP_URI = 'v1/additional-shifts/job/setup'

SIMPLE_JOB_SETUP_REQUEST = {
    'job_data': {
        'datetime_from': '2021-12-30T09:00:00+03:00',
        'datetime_to': '2021-12-30T11:00:00+03:00',
        'skill': 'pokemon',
        'additional_shifts_count': 1,
        'candidates_count': 1,
        'dry_run': True,
        'ttl_time': '2021-12-30T09:00:00+03:00',
    },
}


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_headers, expected_status',
    [
        pytest.param(
            {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'},
            200,
            id='x_yandex_uid exists',
        ),
        pytest.param(
            {'X-Yandex-UID': '0000', 'X-WFM-Domain': 'taxi'},
            400,
            id='x_yandex_yid doesnt exist',
        ),
    ],
)
async def test_check_setup_simple(
        taxi_workforce_management_web, tst_headers, expected_status,
):
    res = await taxi_workforce_management_web.post(
        JOB_SETUP_URI, json=SIMPLE_JOB_SETUP_REQUEST, headers=tst_headers,
    )
    assert res.status == expected_status
