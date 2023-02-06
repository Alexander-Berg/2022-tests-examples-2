import pytest


from tests_tags.tags import tags_tools

_PROVIDER = tags_tools.Provider(100, 'truth', 'believe me', True)

_LVH = tags_tools.Entity(1000, 'LarisuVannuHochu', 'store_id')
_LVH_TAG = tags_tools.TagName(1000, 'good_restaurant')

_SOUP = tags_tools.Entity(1002, 'Soup', 'item_id')
_SOUP_TAG = tags_tools.TagName(1002, 'best_type_of_food')

_PERSONAL_PHONE_ID = tags_tools.Entity(1004, 'some_id', 'personal_phone_id')
_PERSONAL_PHONE_ID_TAG = tags_tools.TagName(1004, 'vip_user')

_LVH_SOUP = tags_tools.Entity(1005, 'LarisuVannuHochu_Soup', 'store_item_id')
_LVH_SOUP_TAG = tags_tools.TagName(1005, 'lvh_soup_discount')

_USER = tags_tools.Entity(1006, 'yandex_uid')
_USER_TAG = tags_tools.TagName(1006, 'plus_subscription')


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities(
            [_LVH, _SOUP, _PERSONAL_PHONE_ID, _LVH_SOUP],
        ),
        tags_tools.insert_providers([_PROVIDER]),
        tags_tools.insert_tag_names(
            [
                _LVH_TAG,
                _SOUP_TAG,
                _PERSONAL_PHONE_ID_TAG,
                _LVH_SOUP_TAG,
                _USER_TAG,
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(
                    name_id=_LVH_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_LVH.entity_id,
                    entity_type=_LVH.type,
                ),
                tags_tools.Tag(
                    name_id=_SOUP_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_SOUP.entity_id,
                    entity_type=_SOUP.type,
                ),
                tags_tools.Tag(
                    name_id=_PERSONAL_PHONE_ID_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_PERSONAL_PHONE_ID.entity_id,
                    entity_type=_PERSONAL_PHONE_ID.type,
                ),
                tags_tools.Tag(
                    name_id=_LVH_SOUP_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_LVH_SOUP.entity_id,
                    entity_type=_LVH_SOUP.type,
                ),
                tags_tools.Tag(
                    name_id=_USER_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_USER.entity_id,
                    entity_type=_USER.type,
                ),
            ],
        ),
    ],
)
async def test_match_single(taxi_grocery_tags):
    response = await taxi_grocery_tags.post(
        'v2/match_single',
        {
            'match': [
                {'value': _LVH.value, 'type': _LVH.type},
                {'value': _SOUP.value, 'type': _SOUP.type},
                {
                    'value': _PERSONAL_PHONE_ID.value,
                    'type': _PERSONAL_PHONE_ID.type,
                },
                {'value': _LVH_SOUP.value, 'type': _LVH_SOUP.type},
                {'value': _USER.value, 'type': _USER.type},
            ],
        },
    )

    assert response.status_code == 200
    tags = response.json()['tags']
    tags.sort()

    assert tags == [
        _SOUP_TAG.name,
        _LVH_TAG.name,
        _LVH_SOUP_TAG.name,
        _PERSONAL_PHONE_ID_TAG.name,
        _USER_TAG.name,
    ]
