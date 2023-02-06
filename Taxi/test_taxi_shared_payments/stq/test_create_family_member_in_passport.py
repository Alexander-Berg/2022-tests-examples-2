import pytest

from taxi_shared_payments.repositories.passport_family import (
    PASSPORT_FAMILY_IS_MEMBER_THIS,
)
from taxi_shared_payments.stq.passport import create_family_member_in_passport

OWNER_YANDEX_UID = 'portal_user1'
ACCOUNT_WITHOUT_PASSPORT_FAMILY = 'acc1'
ACCOUNT_WITH_PASSPORT_FAMILY = 'acc2'
MEMBER_PORTAL_UID = 'portal_user2'


@pytest.mark.parametrize(
    'params, passport_response, call_passport',
    [
        pytest.param(
            {
                'owner_yandex_uid': OWNER_YANDEX_UID,
                'account_id': ACCOUNT_WITH_PASSPORT_FAMILY,
                'member_portal_uid': MEMBER_PORTAL_UID,
            },
            {'status': 'ok', 'family_id': '123'},
            True,
            id='add member to passport family',
        ),
        pytest.param(
            {
                'owner_yandex_uid': OWNER_YANDEX_UID,
                'account_id': ACCOUNT_WITH_PASSPORT_FAMILY,
                'member_portal_uid': MEMBER_PORTAL_UID,
            },
            {'status': 'error', 'errors': [PASSPORT_FAMILY_IS_MEMBER_THIS]},
            True,
            id='add member to passport family, member already added',
        ),
        pytest.param(
            {
                'owner_yandex_uid': OWNER_YANDEX_UID,
                'account_id': ACCOUNT_WITHOUT_PASSPORT_FAMILY,
                'member_portal_uid': MEMBER_PORTAL_UID,
            },
            {},
            False,
            id='family already migrate',
        ),
    ],
)
async def test_create_family_member_in_passport(
        stq3_context,
        mockserver,
        load_json,
        patch,
        web_context,
        params,
        passport_response,
        call_passport,
):
    @mockserver.json_handler('/passport-internal/1/bundle/family/add_member/')
    def _create_family_member(request):
        return passport_response

    await create_family_member_in_passport.task(stq3_context, **params)

    create_member_call_count = 1 if call_passport else 0
    assert _create_family_member.times_called == create_member_call_count
