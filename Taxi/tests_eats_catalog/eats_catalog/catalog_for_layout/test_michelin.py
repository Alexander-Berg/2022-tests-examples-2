import copy

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils


NOW = parser.parse('2021-01-01T12:00:00+03:00')

AWARD_TAG = 'michelin_two_star'
PROJECT_TAG = 'michelin'

ACTION = {
    'award_type': AWARD_TAG,
    'icon': {'url': 'michelin/icon', 'width': 'single'},
    'text': {
        'color': [
            {'theme': 'light', 'value': '#000000'},
            {'theme': 'dark', 'value': '#FFFFFF'},
        ],
        'text': 'Звезда МИШЛЕН',
    },
    'url': 'https://eda.yandex.ru/mishelin',
    'button_text': 'Ого!',
}


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@experiments.known_tags([AWARD_TAG])
@experiments.michelin(project_tag=PROJECT_TAG, actions=[ACTION])
async def test_michelin(catalog_for_layout, mockserver, eats_catalog_storage):
    """
    Проверяем, что если рест помечен тегом мишлена, то в ответ
    добавляется экшон с данными из конфига
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

    block_id = 'open'
    response = await catalog_for_layout(
        blocks=[{'id': block_id, 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())
    place = layout_utils.find_place_by_slug(place_slug, block)

    expected_action = copy.deepcopy(ACTION)
    expected_action.pop('award_type')
    expected_action['project_tag'] = PROJECT_TAG

    action = place['payload']['data']['actions'][0]
    assert action['type'] == 'special_project'
    assert action['payload'] == expected_action
