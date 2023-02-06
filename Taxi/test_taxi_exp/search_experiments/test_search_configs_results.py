import pytest


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            {'configs': []},
            marks=(pytest.mark.pgsql('taxi_exp'),),
            id='empty_answer_with_configs_key',
        ),
        pytest.param(
            {
                'configs': [
                    {
                        'created': '2020-03-23T18:54:05+03:00',
                        'description': 'DESCRIPTION',
                        'enabled': True,
                        'last_manual_update': '2020-03-24T12:54:05+03:00',
                        'last_modified_at': 1,
                        'biz_revision': 1,
                        'name': 'first_experiment',
                    },
                    {
                        'created': '2020-03-23T11:54:05+03:00',
                        'description': 'DESCRIPTION',
                        'enabled': True,
                        'last_manual_update': '2020-03-24T22:54:05+03:00',
                        'last_modified_at': 2,
                        'biz_revision': 1,
                        'name': 'second_experiment',
                    },
                    {
                        'created': '2020-03-24T11:04:05+03:00',
                        'description': 'DESCRIPTION',
                        'enabled': True,
                        'last_manual_update': '2020-03-25T12:00:05+03:00',
                        'last_modified_at': 3,
                        'biz_revision': 1,
                        'name': 'third_experiment',
                    },
                ],
            },
            marks=(pytest.mark.pgsql('taxi_exp', files=['filled.sql']),),
            id='filled_answer_with_configs_key',
        ),
    ],
)
async def test_search_configs_results(taxi_exp_client, expected):
    response = await taxi_exp_client.get(
        '/v1/configs/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == expected
