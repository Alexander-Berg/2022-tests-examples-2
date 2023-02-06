import datetime

import pytest


async def test_availability_not_found(taxi_tristero_b2b):
    """ Should return 404 if depot is not found """
    request = {
        'position': {'location': [33.1, 55.1]},
        'delivery_date': '2020-09-09T13:16:00+00:00',
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru', json=request,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'status, code',
    [
        ('active', 200),
        ('disabled', 404),
        ('closed', 404),
        ('coming_soon', 404),
    ],
)
async def test_availability_status(
        taxi_tristero_b2b, grocery_depots, status, code,
):
    """ Should return 404 if depot is not active """
    depot = grocery_depots.add_depot(
        depot_test_id=1, status=status, allow_parcels=True,
    )

    request = {
        'position': {'location': depot.location_as_array},
        'delivery_date': '2020-09-09T13:16:00+00:00',
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru', json=request,
    )
    assert response.status_code == code


async def test_availability_found(
        taxi_tristero_b2b, grocery_depots, overlord_catalog,
):
    """ availability should return phone_number, work_hours,
    depot_id and delivery_type """
    phone_number = '+79876543210'
    depot_id = 'depot_id_1'
    depot = grocery_depots.add_depot(
        depot_test_id=1,
        depot_id=depot_id,
        allow_parcels=True,
        phone_number=phone_number,
        auto_add_zone=False,
    )
    zone = depot.add_zone(
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 23, 'minute': 0},
                },
            },
        ],
    )
    request = {
        'position': {'location': zone.zone_center_as_array},
        'delivery_date': '2020-09-09T13:16:00+00:00',
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru', json=request,
    )
    assert response.status_code == 200

    depots = response.json()
    assert len(depots['delivery_options']) == 1
    depot = depots['delivery_options'][0]
    assert depot['depot_id'] == 'depot_id_1'
    assert depot['work_hours'] == {'from': '07:00', 'to': '23:00'}
    assert depot['phone_number'] == phone_number


@pytest.mark.config(
    TRISTERO_B2B_ALLOWED_DELIVERY_TYPES=['pedestrian', 'yandex_taxi'],
)
@pytest.mark.parametrize(
    'delivery_type, code',
    [
        ('pedestrian', 200),
        ('yandex_taxi', 200),
        ('yandex_taxi_night', 404),
        ('yandex_taxi_remote', 404),
        ('rover', 404),
    ],
)
async def test_availability_delivery_types(
        taxi_tristero_b2b, grocery_depots, delivery_type, code,
):
    """ Should return 404 if delivery_type is
    not in TRISTERO_B2B_ALLOWED_DELIVERY_TYPES """
    depot = grocery_depots.add_depot(
        depot_test_id=1, delivery_type=delivery_type, allow_parcels=True,
    )

    request = {
        'position': {'location': depot.location_as_array},
        'delivery_date': '2020-09-09T13:16:00+00:00',
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru', json=request,
    )
    assert response.status_code == code


@pytest.mark.parametrize('allow_parcels, code', [(True, 200), (False, 404)])
async def test_availability_allow_parcels(
        taxi_tristero_b2b, grocery_depots, allow_parcels, code,
):
    """ Should return 200 only if parcels are allowed """
    depot = grocery_depots.add_depot(
        depot_test_id=1, allow_parcels=allow_parcels,
    )

    request = {
        'position': {'location': depot.location_as_array},
        'delivery_date': '2020-09-09T13:16:00+00:00',
    }
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru', json=request,
    )
    assert response.status_code == code


async def test_availability_depot_changed_expiry_date_not_match(
        taxi_tristero_b2b, grocery_depots,
):
    now = datetime.datetime.now(datetime.timezone.utc)

    depot = grocery_depots.add_depot(1, auto_add_zone=False)
    depot.add_zone(
        delivery_type='pedestrian',
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
        effective_from=(now - datetime.timedelta(days=1)).isoformat(),
        effective_till=(now + datetime.timedelta(days=1)).isoformat(),
    )

    request = {
        'position': {'location': depot.location_as_array},
        'delivery_date': now.isoformat(),
        'expiry_date': (now + datetime.timedelta(days=2)).isoformat(),
    }

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru', json=request,
    )

    error_code = 404
    assert response.status_code == error_code


async def test_availability_depot_changed_expiry_date_not_exist(
        taxi_tristero_b2b, grocery_depots,
):
    now = datetime.datetime.now(datetime.timezone.utc)

    depot = grocery_depots.add_depot(2, auto_add_zone=False)
    depot.add_zone(
        delivery_type='pedestrian',
        timetable=[
            {
                'day_type': 'Everyday',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 20, 'minute': 0},
                },
            },
        ],
        effective_from=(now + datetime.timedelta(days=3)).isoformat(),
        effective_till=(now + datetime.timedelta(days=5)).isoformat(),
    )

    request = {
        'position': {'location': depot.location_as_array},
        'delivery_date': (now + datetime.timedelta(days=4)).isoformat(),
    }

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru', json=request,
    )
    error_code = 404
    assert response.status_code == error_code
