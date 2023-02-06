from tests_tags_topics import constants


async def test_units_list(taxi_tags_topics):
    response = await taxi_tags_topics.get(
        '/v1/service-discovery/units-list', headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'units': [
            {
                'name': constants.TAGS_SERVICE,
                'title': 'Теги водителей',
                'short_title': 'Водительские',
            },
            {
                'name': constants.PASSENGER_TAGS_SERVICE,
                'title': 'Теги пассажиров',
                'short_title': 'Пассажирские',
            },
            {
                'name': constants.EATS_TAGS_SERVICE,
                'title': 'Теги еды',
                'short_title': 'Еда',
            },
            {
                'name': constants.GROCERY_TAGS_SERVICE,
                'title': 'Теги лавки',
                'short_title': 'Лавка',
            },
        ],
    }
