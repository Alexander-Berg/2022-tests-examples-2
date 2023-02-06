# pylint: disable=C5521, C0103
import pytest

from .fbs import AirportQueueStateFbs

fbs_handler = AirportQueueStateFbs()


def _compare_states(first, second):
    assert len(first) == len(second) == 1
    assert 'states' in first and 'states' in second

    states_first = first['states']
    states_second = second['states']

    assert len(states_first) == len(states_second)

    st_len = len(states_first)
    mask = [False for _ in range(st_len)]
    for i in range(st_len):
        used = False
        for j in range(st_len):
            if not mask[j] and states_first[j] == states_second[i]:
                mask[j] = True
                used = True
                break
        assert used, 'Elem ' + str(states_second[i]) + ' is not matched'


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql('reposition')
async def test_empty_request(taxi_reposition_api):

    response = await taxi_reposition_api.post(
        '/v1/service/airport_queue/state',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {'airport_queue_id': 'q1', 'queries': []},
        ),
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {'states': []}


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.parametrize(
    'query, id_response',
    [
        (
            {
                'airport_queue_id': 'q1',
                'queries': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd1'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd4'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd5'},
                ],
            },
            '0',
        ),
        (
            {
                'airport_queue_id': 'q2',
                'queries': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd1'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd4'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd5'},
                ],
            },
            '1',
        ),
        (
            {
                'airport_queue_id': 'q3',
                'queries': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd1'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd4'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd5'},
                ],
            },
            '2',
        ),
        (
            {
                'airport_queue_id': 'q1',
                'queries': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd3'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd4'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd5'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd1'},
                ],
            },
            '3',
        ),
        (
            {
                'airport_queue_id': 'q3',
                'queries': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd2'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd3'},
                ],
            },
            '4',
        ),
        (
            {
                'airport_queue_id': 'q2',
                'queries': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd6'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd3'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd1'},
                ],
            },
            '5',
        ),
        (
            {
                'queries': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd1'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd2'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd3'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd4'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd5'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd6'},
                ],
            },
            '6',
        ),
        (
            {
                'airport_queue_id': 'q1',
                'queries': [
                    {
                        'park_db_id': 'no_park',
                        'driver_profile_id': 'no_driver',
                    },
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd5'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'd1'},
                ],
            },
            '7',
        ),
    ],
)
async def test_simple_correct_request(
        taxi_reposition_api, load_json, query, id_response,
):

    response = await taxi_reposition_api.post(
        '/v1/service/airport_queue/state',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(query),
    )

    assert response.status_code == 200

    responses = load_json('responses.json')
    _compare_states(
        fbs_handler.parse_response(response.content), responses[id_response],
    )
