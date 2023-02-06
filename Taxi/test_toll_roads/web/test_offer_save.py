import pytest

from test_toll_roads import queries

OFFER_ID = '00234567890123456789abcdefGHIJKLMN'


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='save_new_offer'),
        pytest.param(
            id='save_existed_offer',
            marks=pytest.mark.pgsql(
                'toll_roads',
                queries=[
                    queries.OFFER_SAVE_SQL.replace(
                        '$1', '\'' + OFFER_ID + '\'',
                    ),
                ],
            ),
        ),
    ],
)
async def test_offer_save(web_app_client, db):
    response = await web_app_client.post(
        '/toll-roads/v1/offer', json={'offer_id': OFFER_ID},
    )
    assert response.status == 200

    offer = await db.fetch_offer(OFFER_ID)
    assert offer


async def test_offer_save_invalid_param(web_app_client):
    response = await web_app_client.post(
        '/toll-roads/v1/offer', json={'id': OFFER_ID},
    )
    assert response.status == 400
