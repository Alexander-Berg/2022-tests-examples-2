import pytest

from taxi_shared_payments.repositories import accounts as accounts_repo
from taxi_shared_payments.stq.passport import migrate_family_to_passport

USER_YANDEX_UID = 'portal_user1'
ACCOUNT_WITHOUT_PASSPORT_FAMILY = 'acc1'
ACCOUNT_WITH_PASSPORT_FAMILY = 'acc2'
CREATED_FAMILY_ID = 'f49491'

NOTIFICATION_PARAMS = {
    'enabled': True,
    'range': {'time_from': '12:00', 'time_till': '23:00'},
    'owner': {
        'title_key': 'migrate_owner_push.title',
        'text_key': 'migrate_owner_push.text',
        'deeplink': 'yandextaxi://coopaccount?type=family/',
    },
    'member': {
        'title_key': 'migrate_member_push.title',
        'text_key': 'migrate_member_push.text',
        'deeplink': 'yandextaxi://coopaccount?type=family/',
    },
}


@pytest.mark.parametrize(
    'params, passport_info, create_new_family',
    [
        pytest.param(
            {
                'yandex_uid': USER_YANDEX_UID,
                'user_ip': 'amazing_ip',
                'account_id': ACCOUNT_WITHOUT_PASSPORT_FAMILY,
            },
            'response_passport_userinfo.json',
            True,
            id='create new passport family',
        ),
        pytest.param(
            {
                'yandex_uid': USER_YANDEX_UID,
                'user_ip': 'amazing_ip',
                'account_id': ACCOUNT_WITH_PASSPORT_FAMILY,
            },
            'response_passport_userinfo.json',
            False,
            id='family already migrate',
        ),
    ],
)
@pytest.mark.config(COOP_ACCOUNT_MIGRATION_PUSH_PARAMS=NOTIFICATION_PARAMS)
async def test_migrate_family_to_passport(
        stq3_context,
        mockserver,
        load_json,
        patch,
        web_context,
        params,
        passport_info,
        create_new_family,
):
    @patch('taxi.clients.passport.PassportClient.get_raw_userinfo')
    async def _get_info_by_uid(*args, **kwargs):
        return load_json(passport_info)

    @mockserver.json_handler('/passport-internal/1/bundle/family/create/')
    def _create_family(request):
        return {'status': 'ok', 'family_id': CREATED_FAMILY_ID}

    @mockserver.json_handler('/passport-internal/1/bundle/family/add_member/')
    def _add_member(request):
        return {'status': 'ok', 'family_id': CREATED_FAMILY_ID}

    @mockserver.json_handler('/blackbox/blackbox')
    def _blackbox(request):
        return {
            'users': [
                {
                    'id': '1130000002997135',
                    'uid': {
                        'value': '1130000002997135',
                        'attributes': {'33': 'Europe/Moscow', '34': 'ru'},
                    },
                },
            ],
        }

    @mockserver.json_handler('/user_api-api/users/search')
    def _user_api(request):
        return {
            'items': [
                {
                    'id': 'id0',
                    'application': 'android',
                    'application_version': '0',
                    'yandex_uuid': 'uuid0',
                    'updated': '2021:01:01 12:00',
                },
            ],
        }

    await migrate_family_to_passport.task(stq3_context, **params)

    if create_new_family:
        assert _create_family.times_called == 1
        assert _add_member.times_called == 2
        account = await accounts_repo.get_one_by_id(
            web_context, params['account_id'],
        )
        assert account.passport_family_id == CREATED_FAMILY_ID
