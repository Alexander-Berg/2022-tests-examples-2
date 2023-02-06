import pytest


@pytest.mark.now('2020-12-01T20:30:50+03:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['test_data.sql'])
async def test_courier_shift_states_updates(
        taxi_eats_performer_shifts, load_json,
):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=0_0',
    )
    expected_response = load_json('response_full.json')
    assert response.status_code == 200
    assert response.json() == expected_response

    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor='
        + response.json()['data']['cursor']
        + '&service=candidates'
        + '&limit=1',
    )
    expected_response = load_json('response_empty.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2020-12-01T20:30:50+03:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['test_data.sql'])
async def test_courier_shift_states_updates_limit(
        taxi_eats_performer_shifts, load_json,
):
    last_cursor = '0_0'
    condition = True
    i = 1
    while condition:
        response = await taxi_eats_performer_shifts.get(
            path='/internal/eats-performer-shifts/v1/courier-shift-states/'
            'updates?cursor=' + last_cursor + '&limit=1',
        )
        expected_response = load_json('response_limit_1_' + str(i) + '.json')
        condition = last_cursor != response.json()['data']['cursor']
        last_cursor = response.json()['data']['cursor']
        i += 1
        assert response.status_code == 200
        assert response.json() == expected_response

    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=' + response.json()['data']['cursor'] + '&limit=1',
    )
    expected_response = load_json('response_empty.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2020-12-01T20:30:50+03:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['test_data.sql'])
async def test_courier_shift_states_updates_cursor(
        taxi_eats_performer_shifts, load_json,
):
    last_cursor = '1606840849_2'
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=' + last_cursor + '&service=something' + '&limit=1',
    )
    assert response.status_code == 200
    assert len(response.json()['data']['shifts']) == 1

    last_cursor = '1606840851_2'
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=' + last_cursor + '&limit=1',
    )
    assert response.status_code == 200
    assert response.json()['data']['shifts'] == []


@pytest.mark.now('2020-12-01T20:30:50+03:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['test_data.sql'])
async def test_courier_shift_states_updates_empty(
        taxi_eats_performer_shifts, load_json,
):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates',
    )
    assert response.status_code == 200
    assert len(response.json()['data']['shifts']) == 3


@pytest.mark.now('2020-12-01T20:30:50+03:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['test_data.sql'])
async def test_courier_shift_states_updates_cursor_empty(
        taxi_eats_performer_shifts, load_json,
):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=',
    )
    assert response.status_code == 200
    assert len(response.json()['data']['shifts']) == 3


@pytest.mark.now('2020-12-01T20:30:50+03:00')
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['test_data_with_consumer.sql'],
)
async def test_courier_shift_states_updates_consumer(
        taxi_eats_performer_shifts, load_json,
):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=&service=picker-dispatch',
    )
    assert response.status_code == 200
    assert len(response.json()['data']['shifts']) == 1

    last_cursor = '1606840849_2'
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor='
        + last_cursor
        + '&service=picker-dispatch'
        + '&limit=1',
    )
    assert response.status_code == 200
    assert response.json()['data']['shifts'] == []
