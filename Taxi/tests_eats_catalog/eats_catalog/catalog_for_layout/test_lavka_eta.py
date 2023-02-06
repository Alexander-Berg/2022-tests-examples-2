import dataclasses

from dateutil import parser
import pytest

from eats_catalog import storage
from . import layout_utils


@dataclasses.dataclass
class Eta:
    min: int
    max: int


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_lavka_eta(catalog_for_layout, eats_catalog_storage, mockserver):
    """
    Проверяем что eta для лавки берется из ручки
    /umlaas-eats/v1/eta, а не /umlaas-eats/v1/catalog
    """

    place_slug = 'lavka'

    catalog_eta = Eta(min=15, max=20)
    eta_eta = Eta(min=40, max=50)

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            business=storage.Business.Store,
            slug=place_slug,
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T22:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats_catalog(request):
        result = [
            {
                'id': 1,
                'relevance': 1.0,
                'type': 'ranking',
                'predicted_times': dataclasses.asdict(catalog_eta),
                'blocks': [],
            },
        ]

        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': result,
        }

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def umlaas_eats_eta(request):
        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'predicted_times': [
                {
                    'id': 1,
                    'times': {
                        'total_time': 53.0,
                        'cooking_time': 41.0,
                        'delivery_time': 12.0,
                        'boundaries': dataclasses.asdict(eta_eta),
                    },
                },
            ],
        }

    block_id = 'lavka'

    response = await catalog_for_layout(
        blocks=[{'id': block_id, 'type': 'open', 'disable_filters': False}],
    )

    # В этой ручке помимо eta есть и другая информация,
    # проверяем что запрос все равно происходит
    assert umlaas_eats_catalog.times_called == 1

    # Проверяем что был запрос в правильную ручку за eta
    assert umlaas_eats_eta.times_called == 1

    assert response.status_code == 200

    data = response.json()
    block = layout_utils.find_block(block_id, data)
    place = layout_utils.find_place_by_slug(place_slug, block)

    delivery_text = place['payload']['data']['features']['delivery']['text']
    assert delivery_text == f'{eta_eta.min}\u2009–\u2009{eta_eta.max} мин'
