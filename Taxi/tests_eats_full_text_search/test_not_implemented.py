import pytest

from . import utils


@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response',
    (
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'place_slug': 'my_place_slug',
            },
            501,
            {
                'code': 'NOT_IMPLEMENTED_FEATURE',
                'message': (
                    'Zero suggest for menu search is not implemented yet, '
                    '\'text\' field must be provided'
                ),
            },
        ),
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'category': '100',
            },
            501,
            {
                'code': 'NOT_IMPLEMENTED_FEATURE',
                'message': 'Cannot apply category and catalog search together',
            },
        ),
    ),
)
async def test_not_implemented(
        taxi_eats_full_text_search, fts_request, fts_status_code, fts_response,
):
    """
    Проверяем что сервис отвечает 501
    на неправильные комбинации входных параметров
    """

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response


@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response',
    (
        (
            {},
            400,
            {
                'code': 'UNKNOWN_LOCATION',
                'message': (
                    'Cannot use catalog search without location, '
                    '\'location\' or \'region_id\' field must be provided'
                ),
            },
        ),
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'selector': 'unknown',
            },
            400,
            {
                'code': 'UNKNOWN_SELECTOR',
                'message': 'Got unexpected value for selector',
            },
        ),
    ),
)
async def test_bad_request(
        taxi_eats_full_text_search, fts_request, fts_status_code, fts_response,
):
    """
    Проверяем код 400
    """

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
