import pytest

from eats_catalog import experiments
from eats_catalog import storage


RATING_META_CONFIG = {
    'low': {
        'icon': {
            'color': [
                {'theme': 'light', 'value': '#NO0000'},
                {'theme': 'dark', 'value': '#NO0000'},
            ],
            'url': 'asset://no_rating_star',
        },
        'text': {
            'color': [
                {'theme': 'light', 'value': '#NO0000'},
                {'theme': 'dark', 'value': '#NO0000'},
            ],
            'text': 'Мало оценок',
        },
    },
    'new': {
        'icon': {'color': [], 'url': 'asset://rating_star_new'},
        'text': {
            'color': [
                {'theme': 'light', 'value': '#NEW000'},
                {'theme': 'dark', 'value': '#NEW000'},
            ],
            'text': 'Новый',
        },
    },
    'regular': {
        'count_description': {'min_count': 300, 'text': '322'},
        'icon_url': 'asset://rating_star',
        'thresholds': [
            {
                'icon_color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
                'min_rating': 0,
                'text_color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
            },
            {
                'icon_color': [
                    {'theme': 'light', 'value': '#LOW000'},
                    {'theme': 'dark', 'value': '#LOW000'},
                ],
                'min_rating': 4.5,
                'text_color': [
                    {'theme': 'light', 'value': '#LOW000'},
                    {'theme': 'dark', 'value': '#LOW000'},
                ],
            },
            {
                'additional_description': 'Хорошо',
                'icon_color': [
                    {'theme': 'light', 'value': '#GOOD00'},
                    {'theme': 'dark', 'value': '#GOOD00'},
                ],
                'min_rating': 4.7,
                'text_color': [
                    {'theme': 'light', 'value': '#GOOD00'},
                    {'theme': 'dark', 'value': '#GOOD00'},
                ],
            },
            {
                'additional_description': 'Отлично',
                'icon_color': [
                    {'theme': 'light', 'value': '#GREAT0'},
                    {'theme': 'dark', 'value': '#GREAT0'},
                ],
                'min_rating': 4.9,
                'text_color': [
                    {'theme': 'light', 'value': '#GREAT0'},
                    {'theme': 'dark', 'value': '#GREAT0'},
                ],
            },
        ],
    },
    'top': {
        'icon': {'color': [], 'url': 'asset://flame'},
        'tag': 'top_rating',
        'text': {
            'color': [
                {'theme': 'light', 'value': '#TOP000'},
                {'theme': 'dark', 'value': '#TOP000'},
            ],
            'text': 'Входит в Топ',
        },
    },
}


@pytest.mark.config(EATS_CATALOG_RATING_META=RATING_META_CONFIG)
@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.parametrize(
    'rating, rating_count, rating_desription, show',
    [
        pytest.param(5.0, 322, 'Отлично', True, id='from config'),
        pytest.param(
            5.0,
            322,
            'Странный рейтинг',
            True,
            marks=(
                experiments.new_rating(
                    thresholds=[
                        {
                            'min_rating': 0.0,
                            'additional_description': 'Не рейтинг',
                            'icon_color': [],
                            'text_color': [],
                        },
                        {
                            'min_rating': 4.782,
                            'additional_description': 'Странный рейтинг',
                            'icon_color': [],
                            'text_color': [],
                        },
                    ],
                )
            ),
            id='from experiment',
        ),
        pytest.param(
            None,
            None,
            None,
            False,
            marks=(
                experiments.new_rating(
                    thresholds=[
                        {
                            'min_rating': 0.0,
                            'additional_description': 'Не рейтинг',
                            'icon_color': [],
                            'text_color': [],
                        },
                    ],
                )
            ),
            id='from experiment no rating',
        ),
    ],
)
async def test_rating(
        slug,
        eats_catalog_storage,
        rating,
        rating_count,
        rating_desription,
        show,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='with_rating',
            new_rating=storage.NewRating(
                rating=4.99, show=show, count=rating_count,
            ),
        ),
    )

    response = await slug(
        'with_rating', query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200

    data = response.json()

    place = data['payload']['foundPlace']['place']

    assert place['rating'] == rating
    assert place['ratingCount'] == (
        str(rating_count) if rating_count else None
    )
    assert place['ratingDescription'] == rating_desription


@experiments.new_rating(
    thresholds=[
        {
            'min_rating': 0.0,
            'additional_description': 'Не рейтинг',
            'icon_color': [],
            'text_color': [],
        },
    ],
)
async def test_rating_none(slug, eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(slug='with_rating', new_rating=None),
    )

    response = await slug(
        'with_rating', query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200

    data = response.json()

    place = data['payload']['foundPlace']['place']

    assert place['rating'] is None
    assert place['ratingCount'] is None
    assert place['ratingDescription'] is None


@pytest.mark.parametrize(
    'rating, count',
    [
        pytest.param(4.8, '200+', id='no hide'),
        pytest.param(
            4.8, None, marks=(experiments.HIDE_RATING_COUNT,), id='hide',
        ),
    ],
)
async def test_hide_rating_count(slug, eats_catalog_storage, rating, count):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='with_rating',
            new_rating=storage.NewRating(
                rating=rating, show=True, count=41231,
            ),
        ),
    )

    response = await slug(
        'with_rating', query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200

    data = response.json()

    place = data['payload']['foundPlace']['place']

    assert place['rating'] == rating
    assert place['ratingCount'] == count


@pytest.mark.parametrize(
    'count, expected_count',
    [
        pytest.param(142, '142', id='with count'),
        pytest.param(220, '200+', id='high count'),
    ],
)
async def test_new_rating_count(
        slug, eats_catalog_storage, count, expected_count,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='with_rating', new_rating=storage.NewRating(count=count),
        ),
    )

    response = await slug(
        'with_rating', query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200

    data = response.json()

    place = data['payload']['foundPlace']['place']
    assert place['ratingCount'] == expected_count
