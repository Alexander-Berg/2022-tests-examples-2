import pytest

from . import utils


MIN_SEARCH_TEXT_LENGTH = 3


@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response',
    (
        (
            {'place_slug': 'my_place_slug', 'text': 'My'},
            400,
            {
                'code': 'TEXT_TOO_SHORT',
                'message': 'Search text must be bigger than 3 symbols',
            },
        ),
        (
            {'place_slug': 'my_place_slug', 'text': 'Ян'},
            400,
            {
                'code': 'TEXT_TOO_SHORT',
                'message': 'Search text must be bigger than 3 symbols',
            },
        ),
    ),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_TEXT_SEARCH_SETTINGS={'min_search_text_length': 3},
)
async def test_min_text_lenght_validation(
        taxi_eats_full_text_search, fts_request, fts_status_code, fts_response,
):
    """
    Проверяем валидацию минимальной длины
    поискового запроса
    """

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response


@pytest.mark.parametrize(
    'fts_params,fts_status_code,fts_response',
    (
        (
            {'text': 'My'},
            400,
            {
                'code': 'TEXT_TOO_SHORT',
                'message': 'Search text must be bigger than 3 symbols',
            },
        ),
        (
            {'text': 'Ян'},
            400,
            {
                'code': 'TEXT_TOO_SHORT',
                'message': 'Search text must be bigger than 3 symbols',
            },
        ),
    ),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_TEXT_SEARCH_SETTINGS={'min_search_text_length': 3},
)
async def test_min_text_lenght_validation_legacy(
        taxi_eats_full_text_search, fts_params, fts_status_code, fts_response,
):
    """
    Проверяем валидацию минимальной длины
    поискового запроса в старом формате API
    """

    place_slug = 'my_place_slug'

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=fts_params,
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
