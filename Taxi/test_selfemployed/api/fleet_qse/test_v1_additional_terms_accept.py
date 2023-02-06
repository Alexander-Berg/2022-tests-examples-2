import pytest

DEFAULT_HEADERS = {
    'X-Park-Id': 'park_id',
    'User-Agent': 'Taximeter 9.30',
    'X-Yandex-UID': '123',
    'X-Ya-User-Ticket-Provider': 'yandex',
}


async def test_parks_additional_terms_accept(se_web_context, se_client):
    response = await se_client.post(
        '/fleet/selfemployed/v1/qse/additional-terms/accept',
        headers=DEFAULT_HEADERS,
        json={
            'contractor_profile_id': 'contractor_profile_id',
            'phone': '+79999999999',
        },
    )
    assert response.status == 200

    sql = """
        SELECT * FROM se.parks_additional_terms
    """

    async with se_web_context.pg.main_master.acquire() as conn:
        rows = await conn.fetch(sql)
        assert len(rows) == 1
        row = rows.pop()
        assert row['park_id'] == 'park_id'
        assert row['contractor_profile_id'] == 'contractor_profile_id'
        assert row['yandex_uid'] == '123'
        assert row['yandex_provider'] == 'yandex'
        assert row['is_accepted']
        assert row['created_at'] == row['updated_at']


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.parks_additional_terms (park_id, contractor_profile_id, 
        yandex_uid, yandex_provider, is_accepted, created_at, updated_at)
        VALUES ('park_id', 'contractor_profile_id', '123', 'yandex', true, 
        now(), now());
        """,  # noqa: W291
    ],
)
async def test_parks_additional_terms_accept_duplicate(
        se_web_context, se_client,
):
    response = await se_client.post(
        '/fleet/selfemployed/v1/qse/additional-terms/accept',
        headers=DEFAULT_HEADERS,
        json={
            'contractor_profile_id': 'contractor_profile_id',
            'phone': '+79999999999',
        },
    )
    assert response.status == 200

    sql = """
        SELECT * FROM se.parks_additional_terms
    """

    async with se_web_context.pg.main_master.acquire() as conn:
        rows = await conn.fetch(sql)
        assert len(rows) == 1
        row = rows.pop()
        assert row['park_id'] == 'park_id'
        assert row['contractor_profile_id'] == 'contractor_profile_id'
        assert row['yandex_uid'] == '123'
        assert row['yandex_provider'] == 'yandex'
        assert row['is_accepted']
        assert row['created_at'] < row['updated_at']
