import pytest


@pytest.mark.parametrize(
    'params, expected_status, expected_response',
    [
        ({'manager_id': 'department_manager2'}, 200, {}),
        ({'manager_id': 'manager1'}, 200, {}),
        ({'yandex_uid': 'emily_uid'}, 200, {}),
        (
            {},
            400,
            {
                'code': 'BadRequest',
                'message': 'Missing manager_id or yandex_uid in query',
            },
        ),
        (
            {'manager_id': 'not_existed_id'},
            404,
            {'code': 'NotFound', 'message': 'Manager not found'},
        ),
    ],
)
async def test_managers_delete(
        taxi_corp_managers,
        mongodb,
        params,
        expected_status,
        expected_response,
):
    response = await taxi_corp_managers.post(
        '/v1/managers/delete', params=params,
    )

    assert response.status == expected_status
    assert response.json() == expected_response

    if response.status == 200:
        query = {}
        if params.get('manager_id'):
            query['_id'] = params['manager_id']
        if params.get('yandex_uid'):
            query['yandex_uid'] = params['yandex_uid']

        db_item = mongodb.corp_managers.find_one(query)
        assert not db_item
