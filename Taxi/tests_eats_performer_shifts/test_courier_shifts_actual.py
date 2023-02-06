import dateutil
import pytest


def make_headers(courier_id, use_courier_id_header=True):
    headers = {
        'Accept-Language': 'en',
        'X-Remote-IP': '12.34.56.78',
        'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
        'X-YaTaxi-Park-Id': 'park_id1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.65 (5397)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
    }
    if use_courier_id_header:
        headers['X-YaEda-CourierId'] = str(courier_id)
    return headers


@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['pg_ctt_shift_info_shift_in_progress.sql'],
)
async def test_shift_actual_info_current_shift_in_progress(
        taxi_eats_performer_shifts,
):

    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/courier_timetable/v1/courier-shifts/actual',
        headers=make_headers(1),
    )

    assert response.status_code == 200

    response = response.json()
    assert response['data'][0]['attributes']['status'] == 'In progress'
    assert response['meta']['count'] == 1


@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['pg_ctt_shift_info_past_shift.sql'],
)
async def test_shift_actual_info_shift_in_the_past_that_ends_yesterday(
        taxi_eats_performer_shifts,
):

    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/courier_timetable/v1/courier-shifts/actual',
        headers=make_headers(1),
    )

    assert response.status_code == 200

    response = response.json()
    assert response['meta']['count'] == 0


@pytest.mark.now(enabled=True)
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['pg_ctt_shift_info_on_days_border.sql'],
)
@pytest.mark.parametrize(
    'current_time,courier_id,expected_result',
    [
        pytest.param(
            '2021-09-23T23:00:00+03:00',
            1,
            [
                {
                    'id': '2',
                    'startsAt': '2021-09-23T20:00:00+00:00',
                    'endsAt': '2021-09-24T00:00:00+00:00',
                    'courierId': 1,
                },
            ],
            id='moscow courier',
        ),
        pytest.param(
            '2021-09-23T23:00:00+05:00',
            3,
            [
                {
                    'id': '4',
                    'startsAt': '2021-09-23T18:00:00+00:00',
                    'endsAt': '2021-09-23T22:00:00+00:00',
                    'courierId': 3,
                },
            ],
            id='ekaterinburg courier',
        ),
        pytest.param(
            '2021-09-23T23:00:00+00:00',
            2,
            [
                {
                    'id': '3',
                    'startsAt': '2021-09-23T23:00:00+00:00',
                    'endsAt': '2021-09-24T01:00:00+00:00',
                    'courierId': 2,
                },
            ],
            id='london courier',
        ),
        pytest.param(
            '2021-09-24T21:00:00+00:00',
            4,
            [
                {
                    'id': '5',
                    'startsAt': '2021-09-24T21:15:00+00:00',
                    'endsAt': '2021-09-24T23:15:00+00:00',
                    'courierId': 4,
                },
            ],
            id='london courier',
        ),
        pytest.param(
            '2021-11-24T22:09:00+03:00',
            5,
            [
                {
                    'id': '6',
                    'startsAt': '2021-11-24T18:20:46+00:00',
                    'endsAt': '2021-11-24T19:20:46+00:00',
                    'courierId': 5,
                },
            ],
            id='tyumen courier',
        ),
    ],
)
async def test_get_actual_shifts_on_days_border_info(
        taxi_eats_performer_shifts,
        mocked_time,
        current_time,
        courier_id,
        expected_result,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/courier_timetable/v1/courier-shifts/actual',
        headers=make_headers(courier_id),
    )

    assert response.status_code == 200
    response = response.json()
    assert response['meta']['count'] == len(expected_result)
    for idx, expected_shift_info in enumerate(expected_result):
        shift_info = response['data'][idx]
        assert expected_shift_info['id'] == shift_info['id']
        assert (
            expected_shift_info['startsAt']
            == shift_info['attributes']['startsAt']
        )
        assert (
            expected_shift_info['endsAt'] == shift_info['attributes']['endsAt']
        )
        assert (
            expected_shift_info['courierId']
            == shift_info['attributes']['courierId']
        )


@pytest.mark.pgsql(
    'eda_couriers_schedule',
    files=['shift_info_shift_in_progress_for_scooter.sql'],
)
async def test_shift_actual_info_current_shift_in_progress_for_scooter(
        taxi_eats_performer_shifts,
):

    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/courier_timetable/v1/courier-shifts/actual',
        headers=make_headers(1, False),
    )

    assert response.status_code == 200

    response = response.json()
    assert response['data'][0]['attributes']['status'] == 'In progress'
    assert response['meta']['count'] == 1


@pytest.mark.pgsql(
    'eda_couriers_schedule',
    files=['shift_info_shift_in_progress_for_scooter.sql'],
)
async def test_shift_actual_courier_not_found(taxi_eats_performer_shifts):

    headers = make_headers(1, False)
    headers['X-YaTaxi-Driver-Profile-Id'] = '1'
    headers['X-YaTaxi-Park-Id'] = '1'
    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/courier_timetable/v1/courier-shifts/actual',
        headers=headers,
    )

    assert response.status_code == 403
