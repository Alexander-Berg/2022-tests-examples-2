# pylint: disable=import-only-modules, import-error
import datetime

import pytest

from tests_shuttle_control.utils import select_named


MOCK_NOW_DT = datetime.datetime(2022, 4, 21, 15, 40, 17)


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'booking_id, expected_response, expected_status',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730776', 200, 'transporting'),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 409, 'finished'),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730777', 404, None),
    ],
)
async def test_main(
        taxi_shuttle_control,
        pgsql,
        booking_id,
        expected_response,
        expected_status,
):
    service_id = 'service_origin_id_1'

    response = await taxi_shuttle_control.post(
        f'/internal/shuttle-control/v1/service/confirm-boarding'
        f'?service_id={service_id}',
        json={'booking_id': booking_id},
    )
    assert response.status_code == expected_response

    if expected_status:
        rows = select_named(
            f'SELECT booking_id, service_origin_id, status '
            f'FROM state.passengers '
            f'WHERE booking_id = \'{booking_id}\'',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': booking_id,
                'service_origin_id': service_id,
                'status': expected_status,
            },
        ]
