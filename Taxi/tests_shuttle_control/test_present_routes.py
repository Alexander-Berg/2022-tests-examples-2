import pytest


@pytest.mark.translations(
    client_messages={
        'shuttle_control.routes.main_route': {'ru': 'main route'},
        'shuttle_control.routes.some_route': {'ru': 'some route'},
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_add_fake_booking(taxi_shuttle_control):
    response = await taxi_shuttle_control.get(
        '/admin/shuttle-control/v1/present-routes',
    )

    assert sorted(response.json(), key=lambda x: x['id']) == sorted(
        [
            {
                'city': 'Санкт-Петербург',
                'id': 'main_route',
                'name': 'main route',
                'time_zone': 'Europe/Moscow',
            },
            {
                'city': 'Санкт-Петербург',
                'id': 'some_route',
                'name': 'some route',
                'time_zone': 'Europe/Moscow',
            },
        ],
        key=lambda x: x['id'],
    )
