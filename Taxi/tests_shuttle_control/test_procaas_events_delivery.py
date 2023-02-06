# pylint: disable=import-only-modules
import datetime

import pytest

from tests_shuttle_control.utils import select_named

MOCK_OLD_DT = datetime.datetime(2020, 5, 28, 11, 30, 55)
MOCK_NOW_DT = datetime.datetime(2020, 5, 28, 11, 40, 55)


@pytest.mark.now('2020-05-28T11:40:55+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_events_delivery(taxi_shuttle_control, mockserver, pgsql):
    @mockserver.json_handler('/processing/v1/shuttle/create-event-batch')
    def _mock(request):
        assert request.json == {
            'events': [
                {
                    'queue': 'orders',
                    'item-id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
                    'idempotency-token': (
                        '2fef68c9-25d0-4174-9dd0-bdd1b3730775_1'
                    ),
                    'payload': {},
                },
                {
                    'queue': 'orders',
                    'item-id': '427a330d-2506-464a-accf-346b31e288c9',
                    'idempotency-token': (
                        '427a330d-2506-464a-accf-346b31e288c9_2'
                    ),
                    'payload': {'foo': False, 'bar': True},
                },
            ],
        }

        return {'event_ids': ['1', '2']}

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': 'cron-procaas-events-delivery'},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT * FROM state.procaas_events ' 'ORDER BY event_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'event_id': 1,
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'payload': {},
            'created_at': MOCK_OLD_DT,
            'processed_at': MOCK_NOW_DT,
            'procaas_event_id': '1',
        },
        {
            'event_id': 2,
            'booking_id': '427a330d-2506-464a-accf-346b31e288c9',
            'payload': {'foo': False, 'bar': True},
            'created_at': MOCK_OLD_DT,
            'processed_at': MOCK_NOW_DT,
            'procaas_event_id': '2',
        },
    ]
