import pytest

from taxi_shared_payments.stq.passport import delete_family_in_passport

USER_YANDEX_UID = '4082379126'
ACCOUNT_WITHOUT_PASSPORT_FAMILY = 'acc1'
ACCOUNT_WITH_PASSPORT_FAMILY = 'acc2'
CREATED_FAMILY_ID = 'f49491'


@pytest.mark.parametrize(
    'params, passport_info, call_passport',
    [
        pytest.param(
            {
                'yandex_uid': USER_YANDEX_UID,
                'user_ip': 'amazing_ip',
                'account_id': ACCOUNT_WITH_PASSPORT_FAMILY,
            },
            'response_passport_userinfo_with_family.json',
            True,
            id='delete family in passport',
        ),
        pytest.param(
            {
                'yandex_uid': USER_YANDEX_UID,
                'user_ip': 'amazing_ip',
                'account_id': ACCOUNT_WITHOUT_PASSPORT_FAMILY,
            },
            'response_passport_userinfo.json',
            False,
            id='account without passport family',
        ),
    ],
)
async def test_delete_family_in_passport(
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

    @mockserver.json_handler('/passport-internal/1/bundle/family/delete/')
    def _delete_family(request):
        return {'status': 'ok'}

    await delete_family_in_passport.task(stq3_context, **params)
    delete_call_count = 1 if call_passport else 0
    assert _delete_family.times_called == delete_call_count
