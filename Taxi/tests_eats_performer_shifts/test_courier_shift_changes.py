# flake8: noqa
import datetime
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


@pytest.mark.parametrize(
    ('courier_id', 'hours', 'seconds'),
    [
        ('1', 12, 0),
        ('2', 12, 0),
        ('3', 12, 0),
        ('4', 17, 10800),
        ('5', 21, 10800),
        ('6', 23, 10800),
        ('7', 23, 10800),
    ],
)
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['test_change_shifts_data.sql'],
)
async def test_courier_shift_changes_start_time(
        taxi_eats_performer_shifts,
        load_json,
        courier_id,
        mocked_time,
        hours,
        seconds,
):

    time = datetime.datetime(
        2021,
        8,
        5,
        hours,
        0,
        0,
        0,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=seconds)),
    )
    mocked_time.set(time)
    await taxi_eats_performer_shifts.invalidate_caches(clean_update=False)

    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/eats-performer-shifts/v1/courier-shifts/changes',
        headers=make_headers(courier_id),
    )

    expected_response = load_json(f'response_courier_id_{courier_id}.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.pgsql('eda_couriers_schedule', files=['test_shift_changes.sql'])
async def test_shift_get_changes_location(taxi_eats_performer_shifts, pgsql):
    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/eats-performer-shifts/v1/courier-shifts/changes',
        headers=make_headers('1'),
    )

    assert response.status_code == 200
    response = response.json()
    assert response['data'] is not None
    assert (
        int((response['data'][0]['attributes']['oldStartPoint']['id'])) == 6341
    )
    assert (
        int(response['data'][0]['attributes']['newStartPoint']['id']) == 6596
    )
    cursor = pgsql['eda_couriers_schedule'].dict_cursor()
    cursor.execute(
        """select is_approved from courier_shift_change_requests
        where shift_id = 1""",
    )
    approval_status = cursor.fetchone()
    assert approval_status[0] is None


@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['test_shift_changes_on_days_border.sql'],
)
@pytest.mark.parametrize(
    'current_time,courier_id,expected_result',
    [
        pytest.param(
            '2021-09-23T23:00:00+03:00',
            1,
            [{'id': '2', 'changes': ['startsAt']}],
            id='moscow courier',
        ),
        pytest.param(
            '2021-09-23T23:00:00+05:00',
            3,
            [{'id': '4', 'changes': ['startsAt']}],
            id='ekaterinburg courier',
        ),
        pytest.param(
            '2021-09-23T23:00:00+00:00',
            2,
            [{'id': '3', 'changes': ['startsAt', 'endsAt']}],
            id='london courier',
        ),
    ],
)
async def test_get_shifts_changes_on_days_border(
        taxi_eats_performer_shifts,
        pgsql,
        mocked_time,
        current_time,
        courier_id,
        expected_result,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/eats-performer-shifts/v1/courier-shifts/changes',
        headers=make_headers(str(courier_id)),
    )

    assert response.status_code == 200
    response = response.json()
    assert response['meta']['count'] == len(expected_result)
    for idx, expected_shift_info in enumerate(expected_result):
        shift_info = response['data'][idx]
        assert expected_shift_info['id'] == shift_info['id']
        assert (
            expected_shift_info['changes']
            == shift_info['attributes']['changes']
        )


async def test_403(taxi_eats_performer_shifts):

    response = await taxi_eats_performer_shifts.get(
        path='/driver/v1/eats-performer-shifts/v1/courier-shifts/changes',
        headers=make_headers(1, False),
    )

    assert response.status_code == 403
