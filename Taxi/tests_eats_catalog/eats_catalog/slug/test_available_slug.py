from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage


@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_available_slug(slug, eats_catalog_storage):
    def search(request):
        if 'place_slug' in request.json:
            return {'ids': [{'place_id': 1, 'zone_ids': [1]}]}

        return {
            'ids': [
                {'place_id': 1, 'zone_ids': [1]},
                {'place_id': 2, 'zone_ids': [2]},
            ],
        }

    eats_catalog_storage.overide_search(search)

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug='unavailable'),
    )

    eats_catalog_storage.add_place(storage.Place(place_id=2, slug='available'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await slug('unavailable')

    assert response.status_code == 200
    assert eats_catalog_storage.search_times_called == 2

    response_data = response.json()

    place = response_data['payload']['foundPlace']

    assert place['place']['slug'] == 'unavailable'
    assert not place['locationParams']['available']
    assert place['locationParams']['availableTo'] is None
    assert place['locationParams']['availableSlug'] == 'available'


@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_available_slug_preview(slug, eats_catalog_storage):
    """
    EDACAT-6: Проверяет, что в available_slug не может вернуться активное
    preview заведение
    """

    def search(request):
        if 'place_slug' in request.json:
            return {'ids': [{'place_id': 1, 'zone_ids': [1]}]}

        return {
            'ids': [
                {'place_id': 1, 'zone_ids': [1]},
                {'place_id': 2, 'zone_ids': [2]},
            ],
        }

    eats_catalog_storage.overide_search(search)

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug='unavailable'),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            slug='available',
            features=storage.Features(visibility_mode='preview'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await slug('unavailable')

    assert response.status_code == 200
    assert eats_catalog_storage.search_times_called == 2

    response_data = response.json()

    place = response_data['payload']['foundPlace']

    assert place['place']['slug'] == 'unavailable'
    assert not place['locationParams']['available']
    assert place['locationParams']['availableTo'] is None
    assert place['locationParams']['availableSlug'] is None


@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_available_slug_without_position(
        taxi_eats_catalog, eats_catalog_storage,
):
    """
    EDACAT-906: проверяет, что при запросе слага без координат не будет попытки
    запросить заведения по бренду из eats-catalog-storage
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='available',
            features=storage.Features(visibility_mode='preview'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/available',
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
        },
    )

    assert response.status_code == 200
    assert eats_catalog_storage.search_times_called == 1

    response_data = response.json()

    place = response_data['payload']['foundPlace']

    assert place['place']['slug'] == 'available'
    assert place['locationParams'] is None


@pytest.mark.now('2021-06-11T17:06:00+03:00')
@experiments.DISABLE_AVAILABLE_SLUG
async def test_unavailable_slug(slug, eats_catalog_storage):
    def search(request):
        if 'place_slug' in request.json:
            return {'ids': [{'place_id': 1, 'zone_ids': [1]}]}

        return {
            'ids': [
                {'place_id': 1, 'zone_ids': [1]},
                {'place_id': 2, 'zone_ids': [2]},
            ],
        }

    eats_catalog_storage.overide_search(search)

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug='unavailable'),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-05-11T10:00:00+00:00'),
                    end=parser.parse('2021-05-11T19:00:00+00:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(storage.Place(place_id=2, slug='available'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-11T10:00:00+00:00'),
                    end=parser.parse('2021-06-11T19:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await slug('unavailable')

    assert response.status_code == 200
    assert eats_catalog_storage.search_times_called == 2

    response_data = response.json()

    place = response_data['payload']['foundPlace']

    assert place['place']['slug'] == 'available'
    assert place['locationParams']['available']
    assert place['locationParams']['availableTo']
    assert place['locationParams']['availableSlug'] is None
