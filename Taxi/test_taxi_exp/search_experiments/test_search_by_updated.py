import pytest


@pytest.mark.parametrize(
    'params,expected_result',
    [
        (
            'updated_from=2020-03-25T11:00:05Z&order=by_department',
            [
                {
                    'name': 'third_experiment',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_modified_at': 3,
                    'biz_revision': 1,
                    'created': '2020-03-24T11:04:05+03:00',
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'department': 'commando_Charlie',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'closed': False,
                },
                {
                    'name': 'other_experiment',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_modified_at': 4,
                    'biz_revision': 1,
                    'created': '2020-03-24T11:04:05+03:00',
                    'last_manual_update': '2020-03-25T12:10:05+03:00',
                    'department': 'commando_Delta',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'closed': False,
                },
                {
                    'name': 'null_experiment',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_modified_at': 5,
                    'biz_revision': 1,
                    'created': '2020-03-24T11:04:05+03:00',
                    'last_manual_update': '2020-03-25T15:00:05+03:00',
                    'department': 'commando_Echo',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'closed': False,
                },
            ],
        ),
        (
            'updated_from=2020-03-25T11:00:05Z&'
            'updated_to=2020-03-25T13:00:00Z&'
            'order=by_department',
            [
                {
                    'name': 'third_experiment',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_modified_at': 3,
                    'biz_revision': 1,
                    'created': '2020-03-24T11:04:05+03:00',
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'department': 'commando_Charlie',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'closed': False,
                },
                {
                    'name': 'other_experiment',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_modified_at': 4,
                    'biz_revision': 1,
                    'created': '2020-03-24T11:04:05+03:00',
                    'last_manual_update': '2020-03-25T12:10:05+03:00',
                    'department': 'commando_Delta',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'closed': False,
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['filled.sql'])
async def test_search_with_order(taxi_exp_client, params, expected_result):

    if isinstance(params, dict):
        for key, value in params.items():
            if isinstance(value, list):
                params[key] = ','.join(str(item) for item in value)

    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert result['experiments'] == expected_result, [
        item['name'] for item in result['experiments']
    ]
