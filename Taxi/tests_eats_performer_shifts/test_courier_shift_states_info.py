import pytest


MOCK_NOW = '2021-08-11T14:40:50+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_closed_eda_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?eatsId=1',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_in_progress_eda_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?eatsId=2',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': True}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_paused_eda_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?eatsId=3',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_closed_taxi_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_in_progress_taxi_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_2',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': True}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_paused_taxi_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_3',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}


@pytest.mark.now('2021-08-11T14:39:00+03:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_msk_timezones_active(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_4',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': True}

    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_5',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': True}


@pytest.mark.now('2021-08-11T14:41:00+03:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_msk_timezones_no_active(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_4',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}

    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_5',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}


@pytest.mark.now('2021-08-11T11:39:00+00:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_utc_timezones_active(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_4',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': True}

    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_5',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': True}


@pytest.mark.now('2021-08-11T11:41:00+00:00')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_utc_timezones_no_active(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_4',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}

    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_5',
    )
    assert response.status_code == 200
    assert response.json() == {'isActive': False}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_two_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?taxiId=EXTERNAL_ID_3&eatsId=3',
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_without_two_id(taxi_eats_performer_shifts):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'info?',
    )
    assert response.status_code == 400
