import pytest


from tests_tags.tags import tags_tools

_PROVIDER = tags_tools.Provider(100, 'support', 'answering calls', True)

_PERSONAL_PHONE = tags_tools.Entity(
    1000, 'PersonalPhoneId', 'personal_phone_id',
)
_PERSONAL_PHONE_TAG = tags_tools.TagName(1000, 'has_some_personality')

_HASH = tags_tools.Entity(1001, 'PhoneHashSum', 'phone_hash_id')
_HASH_TAG = tags_tools.TagName(1001, 'knows_math')

_MC_DONALDS = tags_tools.Entity(1002, 'McDonalds', 'corp_client_id')
_MC_DONALDS_TAG = tags_tools.TagName(1002, 'pick_big_tasty')

_USER = tags_tools.Entity(1003, 'DimaId', 'user_id')
_USER_TAG = tags_tools.TagName(1003, 'humble_customer')

_ACCOUNT = tags_tools.Entity(1004, 'yandex_uid')
_ACCOUNT_TAG = tags_tools.TagName(1004, 'plus_subscription')


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities(
            [_PERSONAL_PHONE, _HASH, _MC_DONALDS, _USER, _ACCOUNT],
        ),
        tags_tools.insert_providers([_PROVIDER]),
        tags_tools.insert_tag_names(
            [
                _PERSONAL_PHONE_TAG,
                _HASH_TAG,
                _MC_DONALDS_TAG,
                _USER_TAG,
                _ACCOUNT_TAG,
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(
                    name_id=_PERSONAL_PHONE_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_PERSONAL_PHONE.entity_id,
                    entity_type=_PERSONAL_PHONE.type,
                ),
                tags_tools.Tag(
                    name_id=_HASH_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_HASH.entity_id,
                    entity_type=_HASH.type,
                ),
                tags_tools.Tag(
                    name_id=_MC_DONALDS_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_MC_DONALDS.entity_id,
                    entity_type=_MC_DONALDS.type,
                ),
                tags_tools.Tag(
                    name_id=_USER_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_USER.entity_id,
                    entity_type=_USER.type,
                ),
                tags_tools.Tag(
                    name_id=_ACCOUNT_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_ACCOUNT.entity_id,
                    entity_type=_ACCOUNT.type,
                ),
            ],
        ),
    ],
)
async def test_match_single(taxi_passenger_tags):
    response = await taxi_passenger_tags.post(
        'v2/match_single',
        {
            'match': [
                {'value': _PERSONAL_PHONE.value, 'type': _PERSONAL_PHONE.type},
                {'value': _HASH.value, 'type': _HASH.type},
                {'value': _MC_DONALDS.value, 'type': _MC_DONALDS.type},
                {'value': _USER.value, 'type': _USER.type},
                {'value': _ACCOUNT.value, 'type': _ACCOUNT.type},
            ],
        },
    )

    assert response.status_code == 200
    tags = response.json()['tags']
    tags.sort()

    assert tags == [
        _PERSONAL_PHONE_TAG.name,
        _USER_TAG.name,
        _HASH_TAG.name,
        _MC_DONALDS_TAG.name,
        _ACCOUNT_TAG.name,
    ]
