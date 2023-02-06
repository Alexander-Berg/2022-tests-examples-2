import pytest

from taxi_shared_payments.repositories import accounts as accounts_repo
from taxi_shared_payments.stq.passport import create_family_in_passport

USER_YANDEX_UID = 'portal_user1'
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
            'response_passport_userinfo_with_family.json',
            False,
            id='family already migrate',
        ),
    ],
)
async def test_create_family_in_passport(
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

    @mockserver.json_handler('/passport-internal/1/bundle/family/create/')
    def _create_family(request):
        return {'status': 'ok', 'family_id': CREATED_FAMILY_ID}

    await create_family_in_passport.task(stq3_context, **params)

    if call_passport:
        assert _create_family.times_called == 1
        account = await accounts_repo.get_one_by_id(
            web_context, params['account_id'],
        )
        assert account.passport_family_id == CREATED_FAMILY_ID
    else:
        assert _create_family.times_called == 0
