import pytest

from . import test_client_cost_centers_util as util


@pytest.mark.parametrize(
    'case_params',
    [
        # ЦЗ для удаления не найден
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='non_existent_id',
                host_option_id=None,
                response=dict(status=404, error_key='cost_centers_not_found'),
            ),
            id='error-delete-non-existing-cost-center',
            marks=pytest.mark.filldb(corp_cost_center_options='for_delete'),
        ),
        # ЦЗ для удаления найден и удалён (нет юзеров)
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='option_to_delete',
                host_option_id=None,
                response=dict(status=200, body={}),
            ),
            id='success-delete-cost-center-no-users',
            marks=pytest.mark.filldb(corp_cost_center_options='for_delete'),
        ),
        # ЦЗ для удаления найден, но не удалён (невозможно перенести юзеров)
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='option_to_delete',
                host_option_id='option_to_delete',
                response=dict(
                    status=409, error_key='cannot_move_users_to_same_id',
                ),
            ),
            id='error-move-to-same-cost-center',
            marks=pytest.mark.filldb(corp_cost_center_options='for_delete'),
        ),
        # ЦЗ для удаления найден, но не удалён (т.к. он основной)
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='host_option_id',  # it is default
                response=dict(
                    status=409, error_key='cannot_delete_default_cost_center',
                ),
            ),
            id='error-deleting-default-cost-center',
            marks=pytest.mark.filldb(corp_cost_center_options='for_delete'),
        ),
        # ЦЗ для удаления найден, но не удалён (т.к. он основной)
        # при этом пользователи не перенесены
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='host_option_id',
                host_option_id='option_to_delete',  # sic! (see comment above)
                response=dict(
                    status=409, error_key='cannot_delete_default_cost_center',
                ),
            ),
            id='error-deleting-default-cost-center-with-users',
            marks=pytest.mark.filldb(
                corp_cost_center_options='for_delete',
                corp_users='not_for_delete',
            ),
        ),
        # ЦЗ для удаления найден, но не удалён (есть юзеры)
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='option_to_delete',
                host_option_id=None,
                response=dict(
                    status=409,
                    error_key='cannot_delete_cost_center_with_users',
                ),
            ),
            id='error-delete-cost-center-has-users',
            marks=pytest.mark.filldb(
                corp_cost_center_options='for_delete', corp_users='for_delete',
            ),
        ),
        # ЦЗ для удаления найден, но не удалён (не найден новый ЦЗ для юзеров)
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='option_to_delete',
                host_option_id='non_existent_id',
                response=dict(status=404, error_key='cost_centers_not_found'),
            ),
            id='error-delete-host-cost-center-not-found',
            marks=pytest.mark.filldb(corp_cost_center_options='for_delete'),
        ),
        # ЦЗ для удаления найден и удалён (юзеры перенесены на другой ЦЗ)
        pytest.param(
            dict(
                client_id='some_client_id',
                option_id='option_to_delete',
                host_option_id='host_option_id',
                response=dict(status=200, body={}),
            ),
            id='success-delete-cost-center-with-users',
            marks=pytest.mark.filldb(
                corp_cost_center_options='for_delete', corp_users='for_delete',
            ),
        ),
    ],
)
async def test_delete_option(taxi_corp_auth_client, db, case_params):
    client_id = case_params['client_id']
    option_id = case_params['option_id']
    host_option_id = case_params.get('host_option_id')
    url = f'/1.0/client/{client_id}/cost_centers/{option_id}'
    if host_option_id:
        url += f'?host_cost_centers_id={host_option_id}'
    cost_center_users_query = {
        'client_id': client_id,
        'cost_centers_id': option_id,
    }
    user_ids_to_move = [
        user['_id']
        async for user in db.corp_users.find(cost_center_users_query, [])
    ]

    response = await taxi_corp_auth_client.delete(url)
    response_content = await response.json()
    response_params = case_params['response']
    expected_status = response_params['status']
    if 'error_key' in response_params:
        expected_content = util.build_error(response_params['error_key'])
    else:
        expected_content = response_params['body']
    assert (response_content, response.status) == (
        expected_content,
        expected_status,
    )

    if expected_status == 200:
        old_option = await db.corp_cost_center_options.find_one(
            {'_id': option_id}, [],
        )
        assert old_option is None
        users_count = await db.corp_users.find(cost_center_users_query).count()
        assert users_count == 0
        if host_option_id:
            assert all(
                [
                    user['cost_centers_id'] == host_option_id
                    async for user in db.corp_users.find(
                        {'_id': {'$in': user_ids_to_move}},
                    )
                ],
            )
    else:
        user_ids_not_moved = {
            user['_id']
            async for user in db.corp_users.find(cost_center_users_query, [])
        }
        assert user_ids_not_moved == set(user_ids_to_move)
