import pytest

from . import utils


PERIODIC_NAME = 'place-info-synchronizer'


@pytest.fixture(name='update_place_from_json')
def _update_place_from_json(make_place, load_json):
    def do_update_place_from_json(place, filename):
        place_info = load_json(filename)
        kwargs = place.copy()
        kwargs.update(
            {
                'slug': place_info['slug'],
                'enabled': place_info['enabled'],
                'type': place_info['type'],
                'business': place_info['business'],
                'brand_id': place_info['brand']['id'],
                'brand_slug': place_info['brand']['slug'],
                'city': place_info['address']['city'],
                'address': place_info['address']['short'],
                'country_id': place_info['country']['id'],
                'country_currency': place_info['country']['currency'],
                'region_id': place_info['region']['id'],
                'location': '({},{})'.format(
                    place_info['location']['geo_point'][0],
                    place_info['location']['geo_point'][1],
                ),
                'is_fast_food': place_info['features']['fast_food'],
                'shop_picking_type': place_info['features'][
                    'shop_picking_type'
                ],
                'preparation': place_info['timing']['preparation'],
                'average_preparation': place_info['timing'][
                    'average_preparation'
                ],
                'extra_preparation': place_info['timing']['extra_preparation'],
                'updated_at': place_info['updated_at'],
                'price_category_value': place_info['price_category']['value'],
                'rating_users': place_info['rating']['users'],
            },
        )
        place.update(**make_place(**kwargs))

    return do_update_place_from_json


@utils.eats_eta_settings_config3()
async def test_place_info_synchronizer_no_updates(
        catalog, taxi_eats_eta, db_select_places,
):
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_places() == []

    assert catalog.mock_places_updates.times_called == 1


@utils.eats_eta_settings_config3(places_batch_size=2)
async def test_place_info_synchronizer_batch_revisions(
        catalog,
        taxi_eats_eta,
        db_select_places,
        make_place,
        update_place_from_json,
):
    places = [
        make_place(
            id=i, revision_id=i // 2 + 1,
        )  # ids 1,2 has revision 1, id 3 has revision 2
        for i in range(3)
    ]
    for place in places:
        catalog.add_place(
            place_id=place['id'], revision_id=place['revision_id'],
        )

        update_place_from_json(place, 'place_info.json')

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert catalog.mock_places_updates.times_called == 2
    assert db_select_places() == places


@utils.eats_eta_settings_config3(places_batch_size=1)
async def test_place_info_synchronizer_update_existing(
        catalog,
        taxi_eats_eta,
        db_insert_place,
        db_select_places,
        make_place,
        update_place_from_json,
):
    places = [make_place(id=i, revision_id=i + 1) for i in range(5)]
    for place in places:
        db_insert_place(place)

        catalog.add_place(
            place_id=place['id'], revision_id=place['revision_id'],
        )

        update_place_from_json(place, 'place_info.json')

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert catalog.mock_places_updates.times_called == 6
    assert db_select_places() == places
