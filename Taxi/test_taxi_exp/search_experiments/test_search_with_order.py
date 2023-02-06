import pytest


@pytest.mark.parametrize(
    'params,status,expected_result',
    [
        pytest.param(
            {'order': 'by_name'},
            200,
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
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                },
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
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
                    },
                },
            ],
            id='by_name',
        ),
        pytest.param(
            {'order': 'by_name_desc'},
            200,
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
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
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
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                },
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
            ],
            id='by_name_desc',
        ),
        pytest.param(
            {'order': 'by_created'},
            200,
            [
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
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                },
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
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'biz_revision': 1,
                    'name': 'third_experiment',
                    'action_time': {
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
                    },
                },
            ],
            id='by_created',
        ),
        pytest.param(
            {'order': 'by_updated_desc'},
            200,
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
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
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
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                },
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
            ],
            id='by_updated_desc',
        ),
        pytest.param(
            {'order': 'bad_order'},
            400,
            {
                'code': 'BAD_ORDER',
                'message': (
                    'order must `action_from, action_to, created, department, '
                    'name, owner, updated, watcher` field names only, '
                    'name `bad_order`'
                ),
            },
            id='bad_order',
        ),
        pytest.param(
            {'order': 'by_name__created_desc'},
            200,
            [
                {
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T21:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T12:54:05+03:00',
                    'last_modified_at': 1,
                    'name': 'first_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T11:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T22:54:05+03:00',
                    'last_modified_at': 2,
                    'name': 'second_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'name': 'third_experiment',
                },
            ],
            id='by_name__created_desc',
        ),
        pytest.param(
            {'order': 'action_from'},
            200,
            [
                {
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T21:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T12:54:05+03:00',
                    'last_modified_at': 1,
                    'name': 'first_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'name': 'third_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T11:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T22:54:05+03:00',
                    'last_modified_at': 2,
                    'name': 'second_experiment',
                },
            ],
            id='action_from',
        ),
        pytest.param(
            {'order': 'action_from_desc'},
            200,
            [
                {
                    'action_time': {
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T11:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T22:54:05+03:00',
                    'last_modified_at': 2,
                    'name': 'second_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'name': 'third_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T21:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T12:54:05+03:00',
                    'last_modified_at': 1,
                    'name': 'first_experiment',
                },
            ],
            id='action_from_desc',
        ),
        pytest.param(
            {'order': 'action_to'},
            200,
            [
                {
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T21:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T12:54:05+03:00',
                    'last_modified_at': 1,
                    'name': 'first_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'name': 'third_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T11:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T22:54:05+03:00',
                    'last_modified_at': 2,
                    'name': 'second_experiment',
                },
            ],
            id='action_to',
        ),
        pytest.param(
            {'order': 'watcher_desc'},
            200,
            [
                {
                    'action_time': {
                        'from': '2020-03-25T20:54:05+03:00',
                        'to': '2022-03-25T21:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T11:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T22:54:05+03:00',
                    'last_modified_at': 2,
                    'name': 'second_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T21:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T12:54:05+03:00',
                    'last_modified_at': 1,
                    'name': 'first_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T18:54:05+03:00',
                        'to': '2022-03-25T18:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-23T21:54:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-24T12:54:05+03:00',
                    'last_modified_at': 1,
                    'name': 'first_experiment',
                },
                {
                    'action_time': {
                        'from': '2020-03-25T19:54:05+03:00',
                        'to': '2022-03-25T20:54:05+03:00',
                    },
                    'biz_revision': 1,
                    'closed': False,
                    'created': '2020-03-24T11:04:05+03:00',
                    'description': 'DESCRIPTION',
                    'enabled': True,
                    'last_manual_update': '2020-03-25T12:00:05+03:00',
                    'last_modified_at': 3,
                    'name': 'third_experiment',
                },
            ],
            id='watcher_desc',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['filled.sql'])
async def test_search_with_order(
        taxi_exp_client, params, status, expected_result,
):

    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == status, await response.text()
    result = await response.json()
    if status == 200:
        assert result['experiments'] == expected_result
    else:
        assert result == expected_result
