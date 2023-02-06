import pytest


@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(taxi_shuttle_control, pgsql):
    response = await taxi_shuttle_control.get(
        '/4.0/shuttle-control/v1/booking/list',
        headers={'X-Yandex-UID': '0123456789'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'bookings': [
            {
                'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
                'status': 'finished',
            },
            {
                'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
                'status': 'driving',
            },
        ],
    }
