import pytest


INITIAL_DB = dict(
    user1='{"(contact_1_1,+79151234567_id)"}',
    user2='{"(contact_2_1,+79157654321_id)"}',
)


@pytest.mark.pgsql('safety_center', files=['db_safety_center.sql'])
@pytest.mark.parametrize(
    ['yandex_uid', 'bound_uids', 'expected_db'],
    [
        pytest.param('user1', [], ['user2'], id='delete_without_bounds'),
        pytest.param('user1', ['user2'], [], id='delete_with_bounds'),
        pytest.param('user1', ['invalid'], ['user2'], id='invalid_bounds'),
        pytest.param('invalid', [], ['user1', 'user2'], id='invalid_uid'),
    ],
)
async def test_delete_user(
        web_app_client, pgsql, mockserver, yandex_uid, bound_uids, expected_db,
):
    phone = 'phone_1'
    phone_type = 'yandex'
    phone_id = 'phone_id_1'

    @mockserver.json_handler('user-api/user_phones/by_number/retrieve')
    def _user_api_mock(request):
        assert request.json == dict(
            phone=phone, type=phone_type, primary_replica=False,
        )
        return dict(
            id=phone_id,  # used components
            # unused required components
            stat=dict(
                big_first_discounts=0,
                complete=0,
                complete_card=0,
                complete_apple=0,
                complete_google=0,
                fake=0,
                total=0,
            ),
            is_loyal=False,
            is_yandex_staff=False,
            is_taxi_staff=False,
            type='yandex',
            phone=phone,
        )

    @mockserver.json_handler('zalogin/v1/internal/phone-info')
    def _zalogin_mock(request):
        assert request.query['phone_id'] == phone_id
        items = [dict(yandex_uid=yandex_uid, type='phonish')]
        items.extend(
            [dict(yandex_uid=uid, type='phonish') for uid in bound_uids],
        )
        return dict(items=items)

    response = await web_app_client.post(
        path='/safety-center/v1/delete-user',
        json=dict(phone=phone, phone_type=phone_type),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
    assert _user_api_mock.times_called == 1
    assert _zalogin_mock.times_called == 1

    cursor = pgsql['safety_center'].cursor()
    cursor.execute('SELECT * from safety_center.contacts')
    result = [row[:2] for row in cursor]
    assert result == [(user, INITIAL_DB[user]) for user in expected_db]
