# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi_corp import stq
from taxi_corp.stq import drive_service_task

DATETIME_AFTER_CODE_EXPIRING = datetime.datetime(year=2021, month=10, day=5)
DATETIME_BEFORE_CODE_EXPIRING = datetime.datetime(
    year=2021, month=3, day=28, hour=10,
)


@pytest.mark.parametrize(
    ['client_id'],
    [
        pytest.param('client3', id='client with active drive service'),
        pytest.param('client1', id='client without active drive service'),
    ],
)
async def test_common_stq_flow(patch, db, taxi_corp_app_stq, client_id):
    @patch('taxi_corp.stq.drive_service_task.link_users')
    async def _link_users(*args, **kwargs):
        pass

    @patch('taxi_corp.stq.drive_service_task.update_users_wallets')
    async def _update_users_wallets(*args, **kwargs):
        pass

    user_ids = ['test_user_2', 'fake_user_id']
    await stq.process_drive_service(taxi_corp_app_stq, client_id, user_ids)

    if client_id == 'client3':
        assert len(_link_users.calls) == 1
        assert len(_update_users_wallets.calls) == 1

    users = await db.corp_users.find({'_id': {'$in': user_ids}}).to_list(None)
    assert all(
        [user['services']['drive'].get('task_id') is None for user in users],
    )


@pytest.mark.parametrize(
    ['now', 'description_response', 'expected_promo_codes'],
    [
        pytest.param(
            DATETIME_AFTER_CODE_EXPIRING,
            {'accounts': [{'name': 'corp_yataxi_client3_default'}]},
            [
                {
                    'account_id': 345,
                    'client_id': 'client3',
                    'code': 'corp123',
                    'created': datetime.datetime(2021, 10, 5, 0, 0),
                    'status': 'add',
                    'updated': datetime.datetime(2021, 10, 5, 0, 0),
                    'user_id': 'test_user_5',
                },
            ],
            marks=pytest.mark.now(DATETIME_AFTER_CODE_EXPIRING.isoformat()),
        ),
        pytest.param(
            DATETIME_AFTER_CODE_EXPIRING,
            {'accounts': []},
            [
                {
                    'account_id': 345,
                    'client_id': 'client3',
                    'code': 'corp123',
                    'created': datetime.datetime(2021, 10, 5, 0, 0),
                    'status': 'add',
                    'updated': datetime.datetime(2021, 10, 5, 0, 0),
                    'user_id': 'test_user_5',
                },
            ],
            marks=pytest.mark.now(DATETIME_AFTER_CODE_EXPIRING.isoformat()),
        ),
        pytest.param(
            DATETIME_BEFORE_CODE_EXPIRING,
            {'accounts': [{'name': 'corp_yataxi_client3_default'}]},
            [],
            marks=pytest.mark.now(DATETIME_BEFORE_CODE_EXPIRING.isoformat()),
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'sms.link_drive_with_promocode': {
            'ru': 'link={link}. promocode={promocode}',
        },
    },
)
async def test_link_users(
        patch,
        db,
        taxi_corp_app_stq,
        mock_drive,
        now,
        description_response,
        expected_promo_codes,
):
    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert text == 'link=https://clck.ru/PvirP. promocode=corp123'
        assert personal_phone_id == 'd0f7a7842295497facae12ff05441622'
        assert intent == 'taxi_corp_send_link'

    mock_drive.data.descriptions_response = description_response
    mock_drive.data.promocode_response = {
        'accounts': [
            {
                'code': 'corp123',
                'account_id': 345,
                'deeplink': 'https://clck.ru/PvirP',
            },
        ],
    }

    user_ids = [
        'test_user_1',  # has drive_user_id, skip
        'test_user_3',  # hasn't drive limit, skip
        'test_user_5',  # checks ok, link this user
    ]
    client = await db.corp_clients.find_one({'_id': 'client3'})
    await drive_service_task.link_users(taxi_corp_app_stq, client, user_ids)

    promo_codes = await db.corp_drive_promocodes.find(
        {'created': now}, projection={'_id': False},
    ).to_list(None)
    assert promo_codes == expected_promo_codes

    if expected_promo_codes:
        promo_codes_call = mock_drive.create_promocode.next_call()['request']
        assert promo_codes_call.query_string == b'count=1'
        assert promo_codes_call.json == {
            'account_meta': {'hard_limit': 0, 'soft_limit': 0},
            'active_flag': True,
            'name': 'corp_yataxi_client3_default',
        }

    if not description_response['accounts']:
        assert mock_drive.update_accounts.next_call()['request'].json == {
            'hard_limit': 100000,
            'meta': {
                'hr_name': 'client3_name',
                'is_personal': True,
                'max_links': 1,
                'offers_filter': 'corporate*rus',
                'parent_id': 12345,
                'refresh_policy': 'month',
                'selectable': True,
            },
            'name': 'corp_yataxi_client3_default',
            'soft_limit': 100000,
            'type': 'wallet',
        }


@pytest.mark.parametrize(
    [
        'user_ids',
        'expected_update_limits_request',
        'expected_activate_wallet_request',
    ],
    [
        # test_user_1 - activate and assign drive limit
        # test_user_2 - do nothing, user without account_id
        # test_user_3 - doesn't have drive limit, deactivate
        # test_user_4 - doesn't have promo code, but has account,
        #  activate and assign limit
        # test_user_5 - inactive user, deactivate
        pytest.param(
            [
                'test_user_1',
                'test_user_2',
                'test_user_3',
                'test_user_4',
                'test_user_5',
            ],
            {
                'accounts': [54321, 22222],
                'soft_limit': 100000,
                'hard_limit': 100000,
            },
            [
                {'accounts': [54321, 22222], 'active_flag': True},
                {'accounts': [12121, 55555], 'active_flag': False},
            ],
            id='assign new limit',
        ),
    ],
)
async def test_update_users_wallets_unit(
        db,
        taxi_corp_app_stq,
        mock_drive,
        user_ids,
        expected_update_limits_request,
        expected_activate_wallet_request,
):
    await drive_service_task.update_users_wallets(taxi_corp_app_stq, user_ids)

    assert (
        mock_drive.update_limits.next_call()['request'].json
        == expected_update_limits_request
    )
    assert (
        mock_drive.activate_wallet.next_call()['request'].json
        == expected_activate_wallet_request[0]
    )
    assert (
        mock_drive.activate_wallet.next_call()['request'].json
        == expected_activate_wallet_request[1]
    )
