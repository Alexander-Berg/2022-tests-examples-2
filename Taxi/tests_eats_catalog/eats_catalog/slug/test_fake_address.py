import pytest

from eats_catalog import storage


@pytest.mark.parametrize(
    'place_id, expected_address',
    [
        pytest.param(
            1,
            'ул. Фальшивых Адресов, 13',
            marks=(
                pytest.mark.experiments3(
                    name='eats_catalog_fake_place_address',
                    is_config=True,
                    consumers=['eats-catalog-slug'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'places': [
                                    {
                                        'place_id': 1,
                                        'address': 'ул. Фальшивых Адресов, 13',
                                    },
                                ],
                            },
                        },
                    ],
                    default_value={},
                )
            ),
            id='matching expreiment',
        ),
        pytest.param(
            1,
            'Новодмитровская улица, 2к6',
            marks=(
                pytest.mark.experiments3(
                    name='eats_catalog_fake_place_address',
                    is_config=True,
                    consumers=['eats-catalog-slug'],
                    clauses=[
                        {
                            'title': 'Always false',
                            'predicate': {'type': 'false'},
                            'value': {
                                'places': [
                                    {
                                        'place_id': 1,
                                        'address': 'ул. Фальшивых Адресов, 13',
                                    },
                                ],
                            },
                        },
                    ],
                    default_value={},
                )
            ),
            id='not matching expreiment',
        ),
        pytest.param(
            2,
            'Новодмитровская улица, 2к6',
            marks=(
                pytest.mark.experiments3(
                    name='eats_catalog_fake_place_address',
                    is_config=True,
                    consumers=['eats-catalog-slug'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always false',
                            'predicate': {'type': 'false'},
                            'value': {
                                'places': [
                                    {
                                        'place_id': 1,
                                        'address': 'ул. Фальшивых Адресов, 13',
                                    },
                                ],
                            },
                        },
                    ],
                    default_value={},
                )
            ),
            id='place not in config',
        ),
    ],
)
async def test_fake_address(
        slug, eats_catalog_storage, place_id, expected_address,
):

    eats_catalog_storage.add_place(storage.Place(place_id=place_id))

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200
    place = response.json()['payload']['foundPlace']['place']
    assert expected_address == place['address']['short']
