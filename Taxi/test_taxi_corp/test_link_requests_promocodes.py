import pytest

MOCK_ID = 'promocode'


@pytest.mark.config(CORP_YALOGIN_LINKING={'request_expire_time': 1})
@pytest.mark.parametrize(
    [
        'passport_mock',
        'post_content',
        'promocodes_count',
        'link_calls',
        'expected_promocode_request',
    ],
    [
        pytest.param(
            'client1',
            {'user_id': 'user1'},
            1,
            0,
            {
                'is_active': False,
                'meta': {'hard_limit': 20000, 'soft_limit': 20000},
                'name': 'corp_yataxi_client1_default',
            },
            id='create_request',
        ),
        pytest.param(
            'client1',
            {'user_id': 'user4'},
            1,
            1,
            {
                'is_active': True,
                'meta': {'hard_limit': 30000, 'soft_limit': 30000},
                'name': 'example',
            },
            id='create_request_with_unlink',
        ),
        pytest.param(
            'client2',
            {'user_id': 'user3'},
            2,
            0,
            {
                'is_active': False,
                'meta': {},
                'name': 'corp_yataxi_client2_default',
            },
            id='create_request_for_expired_link',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_post_request_link(
        passport_mock,
        pd_patch,
        patch,
        drive_patch,
        taxi_corp_real_auth_client,
        db,
        post_content,
        promocodes_count,
        link_calls,
        expected_promocode_request,
):
    user_id = post_content['user_id']

    @patch('taxi.clients.drive.DriveClient.promocode')
    async def _promocode(*args, **kwargs):
        return [
            {
                'code': MOCK_ID,
                'account_id': 123,
                'deeplink': 'http://deeplink',
            },
        ]

    @patch('taxi.clients.drive.DriveClient.link')
    async def _link(*args, **kwargs):
        pass

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        passed = kwargs['kwargs']
        assert passed['user_id'] == user_id

    prev_db_state = await db.corp_drive_promocodes.count()

    response = await taxi_corp_real_auth_client.post(
        '/1.0/request-link', json=post_content,
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    request = await db.corp_drive_promocodes.find(
        {'user_id': user_id},
    ).to_list(None)
    assert promocodes_count == len(request)
    assert request[0]['status'] == 'add'
    assert 'code' not in request[0]['status']

    post_db_state = await db.corp_drive_promocodes.count()
    assert prev_db_state <= post_db_state

    stq_calls = _put.calls
    assert len(stq_calls) == 1

    assert len(_link.calls) == link_calls

    promocode_calls = _promocode.calls
    assert len(promocode_calls) == 1
    assert promocode_calls[0]['kwargs'] == expected_promocode_request


@pytest.mark.parametrize(
    'passport_mock, post_content, error_code',
    [
        pytest.param(
            'client1',
            {'user_id': 'user2'},
            409,
            id='create_request_for_user_with_active_request',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_post_request_link_fail(
        taxi_corp_real_auth_client,
        pd_patch,
        passport_mock,
        patch,
        db,
        post_content,
        error_code,
):
    prev_db_state = await db.corp_drive_promocodes.count()

    @patch('taxi.clients.drive.DriveClient.promocode')
    async def _promocode(*args, **kwargs):
        return [{'code': MOCK_ID, 'account_id': 123, 'deeplink': 'some link'}]

    request = await db.corp_drive_promocodes.find_one(
        {'user_id': post_content['user_id']},
    )
    assert request['status'] is not None

    response = await taxi_corp_real_auth_client.post(
        '/1.0/request-link', json=post_content,
    )
    response_json = await response.json()
    assert response.status == error_code, response_json

    post_db_state = await db.corp_drive_promocodes.count()
    assert prev_db_state == post_db_state


@pytest.mark.parametrize(
    'post_content, passport_mock, error_code',
    [
        pytest.param(
            {'user_id': 'user3'},
            'client1',
            403,
            id='create_request_for_the_wrong_user',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_post_request_link_403(
        taxi_corp_real_auth_client,
        pd_patch,
        db,
        post_content,
        passport_mock,
        error_code,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/request-link', json=post_content,
    )
    response_json = await response.json()
    assert response.status == error_code, response_json
