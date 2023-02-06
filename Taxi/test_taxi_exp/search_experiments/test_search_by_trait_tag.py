import pytest


@pytest.mark.parametrize(
    'custom_url,params,expected_result',
    [
        (
            None,
            {'trait_tags': ['analytical']},
            [
                {
                    'closed': False,
                    'created': '2020-03-23T21:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T12:54:05+03:00',
                    'last_modified_at': 1,
                    'biz_revision': 1,
                    'name': 'first_experiment',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                },
                {
                    'closed': False,
                    'created': '2020-03-23T11:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T22:54:05+03:00',
                    'last_modified_at': 2,
                    'biz_revision': 1,
                    'name': 'second_experiment',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                },
            ],
        ),
        (None, {'trait_tags': ['unknown']}, []),
        (
            None,
            {'trait_tags': ['other', 'other-analytical']},
            [
                {
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'biz_revision': 1,
                    'name': 'third_experiment',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                },
            ],
        ),
        (
            None,
            {'trait_tags': ['other-analytical', 'other']},
            [
                {
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'biz_revision': 1,
                    'name': 'third_experiment',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                },
            ],
        ),
        (
            None,
            (('trait_tags', 'other-analytical'), ('trait_tags', 'other')),
            [
                {
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'biz_revision': 1,
                    'name': 'third_experiment',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                },
            ],
        ),
        (
            (
                '/v1/experiments/list/?'
                'trait_tags=other&trait_tags=other-analytical'
            ),
            {},
            [
                {
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'biz_revision': 1,
                    'name': 'third_experiment',
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['filled.sql'])
async def test_search_with_order(
        taxi_exp_client, custom_url, params, expected_result,
):

    if isinstance(params, dict):
        for key, value in params.items():
            if isinstance(value, list):
                params[key] = ','.join(str(item) for item in value)

    url = custom_url or '/v1/experiments/list/'

    response = await taxi_exp_client.get(
        url, headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert result['experiments'] == expected_result, [
        item['name'] for item in result['experiments']
    ]
