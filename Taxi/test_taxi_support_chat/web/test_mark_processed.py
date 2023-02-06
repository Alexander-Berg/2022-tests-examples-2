import pytest


@pytest.mark.parametrize(
    '_id, status',
    [
        ('5b436ca8779fb3302cc784ba', 200),
        ('000000000000000000000000', 404),
        ('123', 500),
    ],
)
async def test(web_app_client, _id, status):
    response = await web_app_client.post(
        '/v1/chat/{}/mark_processed'.format(_id),
    )
    assert response.status == status
