import pytest

URI = 'v1/schedule/types/shifts/preview'
HEADERS = {'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        (
            {
                'id': 1,
                'datetime_from': '2021-01-01T00:00:00Z',
                'datetime_to': '2021-01-07T00:00:00Z',
                'offset': 1,
            },
            200,
            {
                'shifts': [
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-01T15:00:00+03:00',
                    },
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-04T15:00:00+03:00',
                    },
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-05T15:00:00+03:00',
                    },
                ],
            },
        ),
        (
            {
                'id': 1000,
                'datetime_from': '2021-01-01T00:00:00Z',
                'datetime_to': '2021-01-07T00:00:00Z',
                'offset': 1,
            },
            404,
            None,
        ),
        (
            {
                'id': 1,
                'datetime_from': '2021-01-01T00:00:00Z',
                'datetime_to': '2021-05-07T00:00:00Z',
                'offset': 1,
            },
            400,
            None,
        ),
        (
            {
                'id': 1,
                'datetime_from': '2021-01-01T00:00:00Z',
                'datetime_to': '2021-01-07T00:00:00Z',
                'offset': 2,
            },
            200,
            {
                'shifts': [
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-03T15:00:00+03:00',
                    },
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-04T15:00:00+03:00',
                    },
                ],
            },
        ),
        pytest.param(
            {
                'id': 1,
                'datetime_from': '2021-01-28T00:00:00Z',
                'datetime_to': '2021-02-03T06:00:00Z',
                'offset': 2,
            },
            200,
            {
                'shifts': [
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-30T15:00:00+03:00',
                    },
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-31T15:00:00+03:00',
                    },
                    {
                        'duration_minutes': 720,
                        'start': '2021-02-03T15:00:00+03:00',
                    },
                ],
            },
            id='base_case',
        ),
        pytest.param(
            {
                'id': 1,
                'datetime_from': '2021-01-30T00:00:00Z',
                'datetime_to': '2021-02-01T06:00:00Z',
                'offset': 2,
            },
            200,
            {
                'shifts': [
                    {  # no such shift in the base_case
                        'duration_minutes': 720,
                        'start': '2021-02-01T15:00:00+03:00',
                    },
                ],
            },
            id='wrong_shift_from_future',  # TODO: EFFICIENCYDEV-19878
        ),
        pytest.param(
            {
                'id': 1,
                'datetime_from': '2021-01-28T00:00:00Z',
                'datetime_to': '2021-01-31T06:00:00Z',
                'offset': 2,
            },
            200,
            {
                'shifts': [
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-30T15:00:00+03:00',
                    },
                    {
                        'duration_minutes': 720,
                        'start': '2021-01-31T15:00:00+03:00',  # > 06:00:00Z
                    },
                ],
            },
            id='shift_outside_of_range',  # TODO: EFFICIENCYDEV-19878
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.get(
        URI, params=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_res
