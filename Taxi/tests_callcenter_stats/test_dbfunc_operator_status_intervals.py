import datetime

import pytest


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    return obj


AGENT_TIMES = {
    '21': [
        {
            'connected': datetime.timedelta(hours=1),
            'paused': datetime.timedelta(0),
        },
    ],
    '22': [
        {
            'connected': datetime.timedelta(hours=1),
            'paused': datetime.timedelta(0),
        },
    ],
    '23': [
        {
            'connected': datetime.timedelta(minutes=50),
            'paused': datetime.timedelta(0),
        },
    ],
    '32': [
        {
            'connected': datetime.timedelta(minutes=10),
            'paused': datetime.timedelta(0),
        },
    ],
    '33': [
        {
            'connected': datetime.timedelta(minutes=50),
            'paused': datetime.timedelta(0),
        },
    ],
    '34': [
        {
            'connected': datetime.timedelta(minutes=40),
            'paused': datetime.timedelta(0),
        },
    ],
    '35': [
        {
            'connected': datetime.timedelta(minutes=50),
            'paused': datetime.timedelta(0),
        },
    ],
    '36': [
        {
            'connected': datetime.timedelta(minutes=50),
            'paused': datetime.timedelta(0),
        },
    ],
    '41': [
        {
            'connected': datetime.timedelta(minutes=10),
            'paused': datetime.timedelta(0),
        },
        {
            'connected': datetime.timedelta(minutes=50),
            'paused': datetime.timedelta(0),
        },
    ],
    '44': [
        {
            'connected': datetime.timedelta(minutes=10),
            'paused': datetime.timedelta(0),
        },
    ],
    '45': [
        {
            'connected': datetime.timedelta(minutes=10),
            'paused': datetime.timedelta(0),
        },
    ],
    '51': [
        {
            'connected': datetime.timedelta(minutes=10),
            'paused': datetime.timedelta(0),
        },
    ],
    '52': [
        {'connected': datetime.timedelta(0), 'paused': datetime.timedelta(0)},
        {
            'connected': datetime.timedelta(0),
            'paused': datetime.timedelta(seconds=900),
        },
        {
            'connected': datetime.timedelta(minutes=10),
            'paused': datetime.timedelta(0),
        },
        {
            'connected': datetime.timedelta(minutes=20),
            'paused': datetime.timedelta(0),
        },
    ],
    '53': [
        {
            'connected': datetime.timedelta(minutes=10),
            'paused': datetime.timedelta(0),
        },
        {
            'connected': datetime.timedelta(minutes=20),
            'paused': datetime.timedelta(0),
        },
    ],
}


@pytest.mark.pgsql('callcenter_stats', files=['insert_operator_history.sql'])
async def test_time_calculation(pgsql):
    cursor = pgsql['callcenter_stats'].cursor()
    query = (
        'SELECT *'
        ' FROM callcenter_stats.operator_status_intervals('
        ' \'{disp, support}\','
        ' \'2020-01-01T00:00:00Z\','
        ' \'2020-01-01T05:00:00Z\','
        ' \'2020-01-01T06:00:00Z\')'
    )

    cursor.execute(query)

    resulted_summary_map = {}
    # map from agent_id to list of intervals for agent:
    # {{connected: ..., paused: ...} , {connected: ..., paused: ...}}
    for record in cursor.fetchall():
        agent_id = record[0]
        if not resulted_summary_map.get(agent_id):
            resulted_summary_map[agent_id] = list()
        resulted_summary_map[agent_id].append(
            {'connected': record[1], 'paused': record[2]},
        )
    for agent_id in resulted_summary_map:
        assert agent_id in AGENT_TIMES, f'agent_id = {agent_id}'
        assert _ordered(AGENT_TIMES[agent_id]) == _ordered(
            resulted_summary_map[agent_id],
        ), f'agent_id = {agent_id}'
    cursor.close()


@pytest.mark.parametrize(
    ['queues', 'expected_agents'],
    [
        pytest.param(
            '\'{disp, support}\'',
            {
                '21',
                '22',
                '23',
                '32',
                '33',
                '34',
                '35',
                '36',
                '41',
                '44',
                '45',
                '51',
                '52',
                '53',
            },
        ),
        pytest.param(
            '\'{disp}\'',
            {
                '21',
                '22',
                '23',
                '32',
                '33',
                '34',
                '35',
                '36',
                '41',
                '45',
                '52',
                '53',
            },
        ),
        pytest.param(
            '\'{support}\'',
            {'21', '22', '23', '32', '33', '34', '35', '44', '51', '53'},
        ),
        pytest.param('\'{}\'', set()),
        pytest.param(
            'NULL',
            {
                '21',
                '22',
                '23',
                '32',
                '33',
                '34',
                '35',
                '36',
                '41',
                '44',
                '45',
                '51',
                '52',
                '53',
            },
        ),
    ],
)
@pytest.mark.pgsql('callcenter_stats', files=['insert_operator_history.sql'])
async def test_agent_filtering(pgsql, queues, expected_agents):
    cursor = pgsql['callcenter_stats'].cursor()
    query = (
        'SELECT agent_id'
        ' FROM callcenter_stats.operator_status_intervals('
        f' {queues},'
        ' \'2020-01-01T00:00:00Z\','
        ' \'2020-01-01T05:00:00Z\','
        ' \'2020-01-01T06:00:00Z\')'
        ' WHERE connected_time > interval \'0\''
    )

    cursor.execute(query)

    agents = set()
    for record in cursor.fetchall():
        agents.add(record[0])
    cursor.close()

    assert agents == expected_agents
