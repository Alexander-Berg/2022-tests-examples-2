import pytest

import hiring_taxiparks_gambling.internal.constants as constants
import hiring_taxiparks_gambling.internal.suggests_localization as suggests

ROUTE = '/v2/hiring-conditions/suggest'

FILE_REQUESTS = 'requests.json'
FILE_EXPECTED_RESPONSES = 'expected_responses.json'


@pytest.mark.translations(
    territories_suggests={
        'tariffs.econom': {'ru': 'эконом', 'en': 'econom'},
        'tariffs.business': {'ru': 'бизнес', 'en': 'business'},
        'tariffs.children': {'ru': 'детский', 'en': 'children'},
        'tariffs.comfort': {'ru': 'комфорт', 'en': 'comfort'},
        'tariffs.comfort_plus': {'ru': 'комфорт плюч', 'en': 'comfort_plus'},
        'tariffs.park_1': {'ru': 'парк_1', 'en': 'park_1'},
        'tariffs.park_2': {'ru': 'парк_2', 'en': 'park_2'},
        'tariffs.park_3': {'ru': 'парк_3', 'en': 'park_3'},
        'tariffs.park_not_offers_rent': {
            'ru': 'парк без аренды',
            'en': 'park_not_offers_rent',
        },
        'tariffs.park_not_accepts_private_vehicles': {
            'ru': 'парк без частных машин',
            'en': 'park_not_accepts_private_vehicles',
        },
        'tariffs.park_4': {'ru': 'парк_4', 'en': 'park_4'},
        'employment_type.natural_person': {
            'ru': 'наемный',
            'en': 'natural_person',
        },
        'employment_type.self_employed': {'ru': 'СМЗ', 'en': 'self_employed'},
    },
)
@pytest.mark.parametrize(
    'case, locale',
    [
        ('unique_region_id', 'en'),
        ('unique_region_id', 'not_found'),
        ('not_unique_region_id', 'en'),
        ('not_existing_region_id', 'en'),
        ('city_without_parks', 'en'),
        ('city_without_self_employed', 'en'),
        ('city_without_self_employed_ru', 'ru'),
    ],
)
async def test_post_hiring_condition_suggest(
        web_app_client,
        taxi_hiring_taxiparks_gambling_web,
        load_json,
        pgsql,
        case,
        locale,
):
    region_id = load_json(FILE_REQUESTS)[case]
    expected_response = load_json(FILE_EXPECTED_RESPONSES)[case]
    response = await taxi_hiring_taxiparks_gambling_web.get(
        ROUTE, params={'region_id': region_id, 'locale': locale},
    )

    assert response.status == expected_response['status']
    response = await response.json()
    assert response == expected_response['body']


async def test_suggests_items_without_translations(web_context):
    response = sorted(
        list(
            suggests.generate_suggests_items(
                web_context.translations.territories_suggests,
                constants.L10N_EMPLOYMENT_TYPE_FIELD_NAME,
                'ru',
                ['natural_person', 'self_employed'],
            ),
        ),
        key=lambda x: x.key,
    )
    result = [item.serialize() for item in response]
    assert result == [
        {'key': 'natural_person', 'value': ''},
        {'key': 'self_employed', 'value': ''},
    ]
