import pytest

DEFAULT_HEADERS = {
    'X-Park-Id': 'park_id',
    'User-Agent': 'Taximeter 9.30',
    'X-Yandex-UID': '123',
    'X-Ya-User-Ticket-Provider': 'yandex',
}


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.parks_additional_terms (park_id, contractor_profile_id, 
        yandex_uid, yandex_provider, is_accepted, created_at, updated_at)
        VALUES ('park_id', 'contractor_profile_id', '123', 'yandex', true, 
        '2021-12-22 15:17:34', '2021-12-22 15:17:34');
        """,  # noqa: W291
    ],
)
async def test_parks_additional_terms_state(se_client):
    response = await se_client.get(
        '/fleet/selfemployed/v1/qse/additional-terms/state',
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'is_accepted': True,
        'date_at': '2021-12-22T15:17:34+03:00',
    }


@pytest.mark.now('2021-12-22T15:17:34+03:00')
async def test_parks_additional_terms_not_accepted(se_client):
    response = await se_client.get(
        '/fleet/selfemployed/v1/qse/additional-terms/state',
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'is_accepted': False,
        'date_at': '2021-12-22T15:17:34+03:00',
    }
