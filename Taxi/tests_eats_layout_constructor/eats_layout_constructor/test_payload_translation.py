import pytest

from . import configs
from . import experiments
from . import translations
from . import utils


TITLE = 'Переведенный заголовок'
DESCRIPTION = 'Описание'


@experiments.layout('layout_1')
@configs.layout_experiment_name()
@pytest.mark.layout(
    slug='layout_1',
    widgets=[
        utils.Widget(
            name='open',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={
                'title': 'payload.title',
                'description': 'payload.description',
            },
            payload_schema={},
        ),
    ],
)
@pytest.mark.parametrize(
    'expected_title, expected_description',
    (
        pytest.param(
            TITLE,
            DESCRIPTION,
            marks=translations.eats_layout_constructor_ru(
                {'payload.title': TITLE, 'payload.description': DESCRIPTION},
            ),
            id='has_keys',
        ),
        pytest.param('payload.title', 'payload.description', id='no_keys'),
    ),
)
async def test_payload_translation(
        layout_constructor, mockserver, expected_title, expected_description,
):
    """
    Проверяет перевод payload-а виджета
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        blocks = request.json['blocks']

        assert len(blocks) == 1
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': blocks[0]['id'],
                    'type': 'open',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {'id': 'id_1', 'name': 'name1'},
                        },
                    ],
                },
            ],
        }

    response = await layout_constructor.post()

    assert response.status == 200
    data = response.json()
    payload = data['layout'][0]['payload']

    assert payload['title'] == expected_title
    assert payload['description'] == expected_description
