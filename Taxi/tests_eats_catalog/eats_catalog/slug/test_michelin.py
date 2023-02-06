import copy

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations


NOW = parser.parse('2021-01-01T12:00:00+03:00')

AWARD_TAG = 'michelin_one_star'
PROJECT_TAG = 'michelin'

TRANSLATIONS = {
    'slug.michelin.star': 'Звезда МИШЛЕН',
    'slug.michelin.button': 'Ого!',
}

BANNER = {
    'award_type': AWARD_TAG,
    'icon': {'url': 'michelin/icon', 'width': 'single'},
    'text': {
        'color': [
            {'theme': 'light', 'value': '#000000'},
            {'theme': 'dark', 'value': '#FFFFFF'},
        ],
        'text': '_',
        'text_key': 'slug.michelin.star',
    },
    'background_color': [
        {'theme': 'light', 'value': '#FFFFFF'},
        {'theme': 'dark', 'value': '#000000'},
    ],
    'url': 'https://eda.yandex.ru/mishelin',
    'button_text': '_',
    'button_text_key': 'slug.michelin.button',
}


def to_response_banner(banner: dict) -> dict:
    result = copy.deepcopy(banner)
    result.pop('award_type')
    result['text']['text'] = TRANSLATIONS[result['text'].pop('text_key')]
    result['button_text'] = TRANSLATIONS[result.pop('button_text_key')]

    rename = {
        'background_color': 'backgroundColor',
        'button_text': 'buttonText',
    }

    for orig, new in rename.items():
        result[new] = result.pop(orig)

    result['projectTag'] = PROJECT_TAG

    return result


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@experiments.known_tags([AWARD_TAG])
@experiments.michelin(project_tag=PROJECT_TAG, banners=[BANNER])
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_michelin(slug, eats_catalog_storage):
    """
    Проверяем, что если рест помечен тегом мишлена, то в ответ
    добавляется банер с данными из конфига
    """

    place_slug = 'place_slug'
    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug=place_slug, tags=[AWARD_TAG]),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(place_slug)

    assert response.status_code == 200

    banner = response.json()['payload']['foundPlace'].get(
        'specialProjectBanner',
    )
    assert banner == to_response_banner(BANNER)
