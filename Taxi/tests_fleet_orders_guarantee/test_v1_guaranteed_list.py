# pylint: disable=C0302
import pytest


ENDPOINT = 'v1/guaranteed/list'


class UniqueDriversContext:
    def __init__(self):
        self.uniques = []

    def set_uniques(self, uniques):
        self.uniques = uniques


@pytest.fixture(name='mock_unique_drivers')
def _mock_unique_drivers(mockserver):

    context = UniqueDriversContext()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_driver_uniques_retrieve_by_profiles(request):
        return {'uniques': [t for t in context.uniques]}

    return context


@pytest.mark.now('2021-09-02T17:00:00+00:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.parametrize(
    'interval, unique_response, orders',
    [
        (
            {
                'from': '2021-09-02T00:00:00+03:00',
                'to': '2021-09-04T00:00:00+03:00',
            },
            [
                {
                    'data': {'unique_driver_id': 'unique_driver_id1'},
                    'park_driver_profile_id': 'park_id1_driver_id1',
                },
                {
                    'data': {'unique_driver_id': 'unique_driver_id3'},
                    'park_driver_profile_id': 'park_id1_driver_id3',
                },
                {
                    'data': {'unique_driver_id': 'unique_driver_id4'},
                    'park_driver_profile_id': 'park_id2_driver_id4',
                },
            ],
            [
                {
                    'booked_at': '2021-09-02T18:00:00+00:00',
                    'contractor_udid': 'unique_driver_id1',
                    'created_at': '2021-09-02T16:00:00+00:00',
                    'id': 'order_id1',
                    'location_from': [13.388378, 52.519894],
                    'locations_to': [
                        [13.396846, 52.502811],
                        [13.397283, 52.503113],
                    ],
                    'lookup_triggered': False,
                },
                {
                    'booked_at': '2021-09-02T20:23:00+00:00',
                    'contractor_udid': 'unique_driver_id3',
                    'created_at': '2021-09-02T16:32:00+00:00',
                    'id': 'order_id3',
                    'location_from': [13.388378, 52.519894],
                    'locations_to': [
                        [13.396846, 52.502811],
                        [13.397283, 52.503113],
                    ],
                    'lookup_triggered': True,
                },
                {
                    'booked_at': '2021-09-02T21:20:00+00:00',
                    'contractor_udid': 'unique_driver_id4',
                    'created_at': '2021-09-02T16:00:00+00:00',
                    'id': 'order_id4',
                    'location_from': [13.388378, 52.519894],
                    'locations_to': [
                        [13.396846, 52.502811],
                        [13.397283, 52.503113],
                    ],
                    'lookup_triggered': False,
                },
            ],
        ),
    ],
)
async def test_fleet_orders_get_cursor(
        taxi_fleet_orders_guarantee,
        interval,
        unique_response,
        orders,
        mock_unique_drivers,
):
    mock_unique_drivers.set_uniques(unique_response)

    query = {'interval': interval}

    response = await taxi_fleet_orders_guarantee.post(ENDPOINT, json=query)

    expected_json = {'orders': orders}

    assert response.status_code == 200
    assert response.json() == expected_json
