import dateutil.parser
import pytest

from tests_fleet_orders_guarantee import db_utils


CANDIDATES_BEFORE = [
    {
        'candidates': ['1', '2', '3'],
        'order_id': 'order_id1',
        'updated_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
    },
    {
        'candidates': ['1', '2', '3'],
        'order_id': 'order_id2',
        'updated_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
    },
    {
        'candidates': ['1', '2', '3'],
        'order_id': 'order_id3',
        'updated_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
    },
    {
        'candidates': ['1', '2', '3'],
        'order_id': 'order_id4',
        'updated_at': dateutil.parser.parse('2021-09-02T21:50:00Z'),
    },
    {
        'candidates': ['1', '2', '3'],
        'order_id': 'order_id5',
        'updated_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
    },
]

CANDIDATES_AFTER = [
    {
        'candidates': [
            [
                'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                '667392a27033aa709dea9b23fbb6eca4',
            ],
            [
                'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                '67a288c7265f372e26bde693535b56f1',
            ],
        ],
        'order_id': 'order_id1',
        'updated_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
    },
    {
        'candidates': ['1', '2', '3'],
        'order_id': 'order_id4',
        'updated_at': dateutil.parser.parse('2021-09-02T21:50:00Z'),
    },
    {
        'candidates': [
            [
                'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                '667392a27033aa709dea9b23fbb6eca4',
            ],
            [
                'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                '67a288c7265f372e26bde693535b56f1',
            ],
        ],
        'order_id': 'order_id5',
        'updated_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
    },
]


@pytest.mark.now('2021-09-02T22:00:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.config(
    FLEET_ORDERS_GUARANTEE_CANDIDATES_UPDATE_SETTINGS={
        'job_period_seconds': 60,
        'candidates_update_period_minutes': 30,
        'max_candidates_to_retrive': 20,
    },
)
async def test_job(testpoint, pgsql, taxi_fleet_orders_guarantee, mockserver):
    @testpoint('candidates-update-worker-finished')
    def handle_finished(arg):
        pass

    @mockserver.json_handler('/candidates/list-profiles')
    def _candidates_search(request):
        assert request.json in [
            {
                'allowed_classes': ['econom'],
                'filtration': 'order',
                'limit': 20,
                'only_free': False,
                'point': [13.388378, 52.519894],
                'zone_id': 'moscow',
                'data_keys': [],
            },
            {
                'allowed_classes': ['comfort'],
                'filtration': 'order',
                'limit': 20,
                'only_free': False,
                'point': [13.388378, 52.519894],
                'zone_id': 'berlin',
                'data_keys': [],
            },
        ]
        return mockserver.make_response(
            json={
                'drivers': [
                    {
                        'position': [13.371241, 52.518477],
                        'id': (
                            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
                            '667392a27033aa709dea9b23fbb6eca4'
                        ),
                        'dbid': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                        'uuid': '667392a27033aa709dea9b23fbb6eca4',
                    },
                    {
                        'position': [13.380166, 52.509764],
                        'id': (
                            'c5cdea22ad6b4e4da8f3fdbd4bddc2e7_'
                            '67a288c7265f372e26bde693535b56f1'
                        ),
                        'dbid': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                        'uuid': '67a288c7265f372e26bde693535b56f1',
                    },
                ],
            },
            status=200,
        )

    cursor = pgsql['fleet_orders_guarantee'].cursor()

    assert db_utils.get_candidates(cursor) == CANDIDATES_BEFORE

    await taxi_fleet_orders_guarantee.run_distlock_task(
        'candidates-update-task',
    )

    result = handle_finished.next_call()
    assert result == {'arg': ['order_id1', 'order_id5']}

    assert db_utils.get_candidates(cursor) == CANDIDATES_AFTER
