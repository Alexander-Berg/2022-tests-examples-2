from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import search_utils


@pytest.mark.now('2021-07-05T14:14:00+03:00')
@experiments.USE_UMLAAS
async def test_compilation(
        mockserver, catalog_for_full_text_search, eats_catalog_storage,
):
    """
    Проверяем, что подборки ML работают.
    Делаем запрос в каталог с параметром compilation
    и ожидаем, что сматчится рест, помеченный подборкой со стороны
    ml.
    """

    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    expected_slug = 'slug_1'
    unexpected_slug = 'slug_2'
    first_position_slug = 'slug_3'

    slugs = list([expected_slug, unexpected_slug, first_position_slug])

    for idx, slug in enumerate(slugs, 1):
        eats_catalog_storage.add_place(
            storage.Place(
                slug=slug, place_id=idx, brand=storage.Brand(brand_id=idx),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=idx, place_id=idx, working_intervals=open_schedule,
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': ['test_1'],
            'result': [
                {
                    'id': 1,
                    'relevance': 1,
                    'type': 'ranking',
                    'predicted_times': {'min': 10, 'max': 20},
                    'blocks': [{'block_id': 'test_1', 'relevance': 1.0}],
                },
                {
                    'id': 3,
                    'relevance': 1,
                    'type': 'ranking',
                    'predicted_times': {'min': 20, 'max': 30},
                    'blocks': [{'block_id': 'test_1', 'relevance': 3.0}],
                },
            ],
        }

    block_id = 'block_id'

    response = await catalog_for_full_text_search(
        blocks=[{'id': block_id, 'type': 'any', 'compilation_type': 'test_1'}],
    )

    assert umlaas_eats.times_called == 1

    assert response.status == 200
    data = response.json()

    block = search_utils.find_block(block_id, data)
    search_utils.find_place_by_slug(expected_slug, block)
    search_utils.find_place_by_slug(first_position_slug, block)
    search_utils.assert_no_slug(unexpected_slug, block)

    assert [
        first_position_slug,
        expected_slug,
    ] == search_utils.get_slugs_order(block)
