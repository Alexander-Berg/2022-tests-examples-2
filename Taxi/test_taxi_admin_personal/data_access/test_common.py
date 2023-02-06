import pytest

from taxi_admin_personal import exceptions
from taxi_admin_personal.data_access import common

COLLECTIONS = ['phones_confirmations']


def fill_environment(environment):
    return pytest.mark.filldb(
        **{collection: environment for collection in COLLECTIONS},
    )


@pytest.mark.parametrize(
    'user,expected',
    [
        # Non-existent user
        ({'id': 'test_none_data'}, None),
        # No phone_id or yandex_uid
        ({'id': 'test_phone_id_yandex_uid'}, None),
    ],
)
@fill_environment('no_type')
async def test_exeptions_get_user_preferred_uids_no_type(
        web_context, user, expected,
):
    with pytest.raises(exceptions.BadRequest):
        await common.get_user_search_params(
            web_context.mongo, web_context.config, user,
        )


@pytest.mark.parametrize(
    'user,expected',
    [
        # Unknown uid_type,
        (
            {
                'id': 'test_unknown_uid_type',
                'phone_id': '5825ba64c0d947f1eef0b501',
                'yandex_uid': '4014659048',
            },
            ({'phone_id': '5825ba64c0d947f1eef0b501'}, ['4014659048']),
        ),
        # Unknown uid_type,
        (
            {
                'id': 'test_unknown_uid_type_2',
                'phone_id': '54f031119cc7a09257112b61',
            },
            (
                {'phone_id': '54f031119cc7a09257112b61'},
                ['4015870654', '4010982636'],
            ),
        ),
        # uid_type phonish
        (
            {
                'id': 'test_unknown_uid_type_3',
                'phone_id': '53903d2db5f273e6a6d34393',
                'yandex_uid_type': 'phonish',
            },
            (
                {
                    'phone_id': '53903d2db5f273e6a6d34393',
                    'yandex_uids': ['4016157384', '4007675826'],
                },
                ['4016157384', '4007675826'],
            ),
        ),
    ],
)
@fill_environment('no_type')
async def test_get_user_preferred_uids_no_type(web_context, user, expected):
    result = await common.get_user_search_params(
        web_context.mongo, web_context.config, user,
    )
    assert result == expected


@pytest.mark.parametrize(
    'user,expected',
    [
        (
            {
                'id': 'test_portal',
                'phone_id': 'some_gibberish',
                'yandex_uid': 'test_uid',
                'yandex_uid_type': 'portal',
            },
            ({'yandex_uids': ['test_uid']}, ['test_uid']),
        ),
        (
            {
                'id': 'test_portal',
                'phone_id': 'some_gibberish',
                'yandex_uid_type': 'portal',
                'yandex_uid': '7',
            },
            (
                {
                    'yandex_uids': [
                        '7',
                        '5000111000',
                        '5000111001',
                        '5000111002',
                    ],
                },
                ['7', '5000111000', '5000111001', '5000111002'],
            ),
        ),
    ],
)
@fill_environment('portal')
@pytest.mark.config(
    PORTAL_AUTH_PORTAL_ACCOUNT_BOUND_PHONISHES_FETCHING_LIMIT=3,
)
async def test_get_user_preferred_uids(web_context, user, expected):
    result = await common.get_user_search_params(
        web_context.mongo, web_context.config, user,
    )
    assert result == expected
