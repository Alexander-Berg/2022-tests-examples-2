import pytest

from taxi_shared_payments.stq.passport import delete_family_member_in_passport

OWNER_YANDEX_UID = 'portal_user1'
ACCOUNT_WITHOUT_PASSPORT_FAMILY = 'acc1'
ACCOUNT_WITH_PASSPORT_FAMILY = 'acc2'
MEMBER_PORTAL_UID = 'portal_user2'
OWNER_IP = 'amazing_ip'
PASSPORT_FAMILY_ID = 'f124'


@pytest.mark.parametrize(
    'params, passport_info, call_passport',
    [
        pytest.param(
            {
                'owner_yandex_uid': OWNER_YANDEX_UID,
                'owner_ip': OWNER_IP,
                'account_id': ACCOUNT_WITH_PASSPORT_FAMILY,
                'member_portal_uid': MEMBER_PORTAL_UID,
            },
            'response_passport_userinfo_with_family.json',
            True,
            id='delete member from passport family, success',
        ),
        pytest.param(
            {
                'owner_yandex_uid': OWNER_YANDEX_UID,
                'owner_ip': OWNER_IP,
                'account_id': ACCOUNT_WITH_PASSPORT_FAMILY,
                'member_portal_uid': MEMBER_PORTAL_UID,
            },
            'response_passport_userinfo.json',
            False,
            id='delete member from passport family, no passport family',
        ),
        pytest.param(
            {
                'owner_yandex_uid': OWNER_YANDEX_UID,
                'owner_ip': OWNER_IP,
                'account_id': ACCOUNT_WITHOUT_PASSPORT_FAMILY,
                'member_portal_uid': MEMBER_PORTAL_UID,
            },
            'response_passport_userinfo.json',
            False,
            id='delete member from passport family, no account family info',
        ),
    ],
)
async def test_delete_family_member_in_passport(
        stq3_context,
        mockserver,
        load_json,
        patch,
        web_context,
        params,
        passport_info,
        call_passport,
):
    @patch('taxi.clients.passport.PassportClient.get_raw_userinfo')
    async def _get_info_by_uid(*args, **kwargs):
        return load_json(passport_info)

    @mockserver.json_handler(
        '/passport-internal/1/bundle/family/remove_member/',
    )
    def _delete_family_member(request):
        return {'status': 'ok'}

    await delete_family_member_in_passport.task(stq3_context, **params)

    delete_member_call_count = 1 if call_passport else 0
    assert _delete_family_member.times_called == delete_member_call_count
