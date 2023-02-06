import pytest


@pytest.mark.parametrize(
    'filter_value, expected_result',
    [
        (
            {'dev_team': 'team1'},
            {
                'success_queues': ['queue3'],
                'conflict_queues': ['queue1'],
                'tplatform_namespace': 'taxi',
            },
        ),
        (
            {'queues': ['queue1', 'queue4']},
            {
                'success_queues': ['queue4'],
                'conflict_queues': ['queue1'],
                'tplatform_namespace': 'market',
            },
        ),
        (
            {},
            {
                'success_queues': ['queue3', 'queue4', 'queue5'],
                'conflict_queues': ['queue1', 'queue2'],
            },
        ),
        (
            {'department': 'department1'},
            {
                'success_queues': ['queue3'],
                'conflict_queues': ['queue2'],
                'tplatform_namespace': 'taxi',
            },
        ),
        (
            {'department': 'department3'},
            {'success_queues': [], 'conflict_queues': []},
        ),
    ],
)
async def test_downtime_activate_200(
        web_app_client, filter_value, expected_result,
):
    full_json = {'dc': 'vla', 'until': '2020-01-02T03:00:00+03:00'}
    full_json.update(filter_value)
    response = await web_app_client.post('/downtime/activate/', json=full_json)
    assert response.status == 200
    content = await response.json()
    content.pop('id')
    assert content == expected_result


async def test_downtime_activate_400(web_app_client):
    requests = [
        {
            'dc': 'vla',
            'until': '2020-01-02T03:00:00+03:00',
            'dev_team': 'team1',
            'queues': ['queue2'],
        },
        {
            'dc': 'vla',
            'until': '2020-01-02T03:00:00+03:00',
            'department': 'department1',
            'queues': ['queue2'],
        },
        {
            'dc': 'vla',
            'until': '2020-01-02T03:00:00+03:00',
            'department': 'department1',
            'dev_team': 'team1',
        },
    ]
    for request in requests:
        response = await web_app_client.post(
            '/downtime/activate/', json=request,
        )
        assert response.status == 400
        content = await response.json()
        assert (
            content['message'] == 'Either dev_team, queues list or department '
            'can be specified, not few of them'
        )
