# pylint: disable=import-only-modules, import-error
import datetime

import pytest

from tests_shuttle_control.utils import select_named
from tests_shuttle_control.utils import stringify_detailed_view


MOCK_NOW_DT = datetime.datetime(2022, 4, 15, 14, 15, 16)


class AnyNumber:
    def __eq__(self, other):
        return isinstance(other, int)


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(taxi_shuttle_control, pgsql):
    service_id = 'service_origin_id_1'
    booking_id = '2fef68c9-25d0-4174-9dd0-bdd1b3730776'

    for _ in range(2):
        response = await taxi_shuttle_control.post(
            f'/internal/shuttle-control/v1/service/booking/cancel'
            f'?service_id={service_id}',
            json={'booking_id': booking_id},
        )
        assert response.status_code == 200
        assert response.json() == {
            'booking_id': booking_id,
            'status': {'status': 'cancelled', 'cancel_reason': 'by_user'},
        }

        rows = select_named(
            f'SELECT booking_id, service_origin_id, shuttle_id, stop_id, '
            f'dropoff_stop_id, status, finished_at, ticket, cancel_reason '
            f'FROM state.passengers '
            f'WHERE booking_id = \'{booking_id}\' '
            f'ORDER BY service_origin_id, shuttle_id, stop_id',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': booking_id,
                'service_origin_id': service_id,
                'shuttle_id': 2,
                'stop_id': 1,
                'dropoff_stop_id': 5,
                'status': 'cancelled',
                'finished_at': MOCK_NOW_DT,
                'ticket': '123',
                'cancel_reason': 'by_user',
            },
        ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic.sql'])
@pytest.mark.parametrize(
    'booking_id, expected_route_view, expected_detailed_route_view',
    [
        (
            'acfff773-398f-4913-b9e9-03bf5eda22ad',
            [3, 4, 7],
            [
                (3, 'acfff773-398f-4913-b9e9-03bf5eda22ae', True),
                (4, 'acfff773-398f-4913-b9e9-03bf5eda22ac', False),
                (7, 'acfff773-398f-4913-b9e9-03bf5eda22ae', False),
            ],
        ),
        (
            'acfff773-398f-4913-b9e9-03bf5eda22ae',
            [4, 6, 7],
            [
                (4, 'acfff773-398f-4913-b9e9-03bf5eda22ad', True),
                (4, 'acfff773-398f-4913-b9e9-03bf5eda22ac', False),
                (6, 'acfff773-398f-4913-b9e9-03bf5eda22ad', False),
                (7, None, None),
            ],
        ),
    ],
)
async def test_main_dynamic(
        taxi_shuttle_control,
        pgsql,
        booking_id,
        expected_route_view,
        expected_detailed_route_view,
):
    service_id = 'service_origin_id_1'

    for _ in range(2):
        response = await taxi_shuttle_control.post(
            f'/internal/shuttle-control/v1/service/booking/cancel'
            f'?service_id={service_id}',
            json={'booking_id': booking_id},
        )
        assert response.status_code == 200
        assert response.json() == {
            'booking_id': booking_id,
            'status': {'status': 'cancelled', 'cancel_reason': 'by_user'},
        }

        rows = select_named(
            f'SELECT booking_id, service_origin_id, shuttle_id, '
            f'status, finished_at, cancel_reason '
            f'FROM state.passengers '
            f'WHERE booking_id = \'{booking_id}\' '
            f'ORDER BY service_origin_id, shuttle_id, stop_id',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': booking_id,
                'service_origin_id': service_id,
                'shuttle_id': 1,
                'status': 'cancelled',
                'finished_at': MOCK_NOW_DT,
                'cancel_reason': 'by_user',
            },
        ]

        rows = select_named(
            'SELECT * FROM state.route_views', pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'view_id': 1,
                'route_id': 1,
                'current_view': expected_route_view,
                'traversal_plan': stringify_detailed_view(
                    expected_detailed_route_view,
                ),
                'revision': AnyNumber(),
            },
        ]

        rows = select_named(
            'SELECT next_stop_id FROM state.shuttle_trip_progress '
            'WHERE shuttle_id = 1',
            pgsql['shuttle_control'],
        )
        assert rows == [{'next_stop_id': expected_route_view[0]}]
