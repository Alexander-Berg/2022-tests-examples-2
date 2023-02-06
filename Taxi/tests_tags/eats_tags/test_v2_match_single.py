import pytest


from tests_tags.tags import tags_tools

_PROVIDER = tags_tools.Provider(100, 'truth', 'believe me', True)

_LVH = tags_tools.Entity(1000, 'LarisuVannuHochu', 'place_id')
_LVH_TAG = tags_tools.TagName(1000, 'good_restaurant')

_GINZA = tags_tools.Entity(1001, 'GinzaProject', 'brand_id')
_GINZA_TAG = tags_tools.TagName(1001, 'nice_brand')

_SOUP = tags_tools.Entity(1002, 'Soup', 'category_id')
_SOUP_TAG = tags_tools.TagName(1002, 'best_type_of_food')

_USER = tags_tools.Entity(1003, 'DimaId', 'user_id')
_USER_TAG = tags_tools.TagName(1003, 'humble_customer')

_PERSONAL_PHONE_ID = tags_tools.Entity(1004, 'some_id', 'personal_phone_id')
_PERSONAL_PHONE_ID_TAG = tags_tools.TagName(1004, 'vip_user')


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities(
            [_LVH, _GINZA, _SOUP, _USER, _PERSONAL_PHONE_ID],
        ),
        tags_tools.insert_providers([_PROVIDER]),
        tags_tools.insert_tag_names(
            [
                _LVH_TAG,
                _GINZA_TAG,
                _SOUP_TAG,
                _USER_TAG,
                _PERSONAL_PHONE_ID_TAG,
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
                    name_id=_GINZA_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_GINZA.entity_id,
                    entity_type=_GINZA.type,
                ),
                tags_tools.Tag(
                    name_id=_SOUP_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_SOUP.entity_id,
                    entity_type=_SOUP.type,
                ),
                tags_tools.Tag(
                    name_id=_USER_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_USER.entity_id,
                    entity_type=_USER.type,
                ),
                tags_tools.Tag(
                    name_id=_PERSONAL_PHONE_ID_TAG.tag_name_id,
                    provider_id=_PROVIDER.provider_id,
                    entity_id=_PERSONAL_PHONE_ID.entity_id,
                    entity_type=_PERSONAL_PHONE_ID.type,
                ),
            ],
        ),
    ],
)
async def test_match_single(taxi_eats_tags):
    response = await taxi_eats_tags.post(
        'v2/match_single',
        {
            'match': [
                {'value': _LVH.value, 'type': _LVH.type},
                {'value': _GINZA.value, 'type': _GINZA.type},
                {'value': _SOUP.value, 'type': _SOUP.type},
                {'value': _USER.value, 'type': _USER.type},
                {
                    'value': _PERSONAL_PHONE_ID.value,
                    'type': _PERSONAL_PHONE_ID.type,
                },
            ],
        },
    )

    assert response.status_code == 200
    tags = response.json()['tags']
    tags.sort()

    assert tags == [
        _SOUP_TAG.name,
        _LVH_TAG.name,
        _USER_TAG.name,
        _GINZA_TAG.name,
        _PERSONAL_PHONE_ID_TAG.name,
    ]
