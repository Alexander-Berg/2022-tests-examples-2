import pytest


async def test_handler(web_app_client):
    response = await web_app_client.get(
        '/status/',
        params={'idempotence_token': '0', 'recipient_personal_id': '0'},
    )
    # cause no test data was inserted
    assert response.status == 404


@pytest.mark.parametrize(
    'idempotence_token, recipient_personal_id, recipient, expected_status',
    [
        (1, 1, None, 'PENDING'),
        (2, 2, None, 'PROCESSING'),
        (3, 3, None, 'TO_RETRY'),
        (4, 4, None, 'FAILED'),
        (5, 5, None, 'SCHEDULED'),
        (1, None, 'ya@ya.ru', 'PENDING'),
    ],
)
@pytest.mark.pgsql('sticker', files=('test_statuses.sql',))
async def test_statuses(
        web_app_client,
        idempotence_token,
        recipient_personal_id,
        recipient,
        expected_status,
):
    params = {'idempotence_token': str(idempotence_token)}
    if recipient is not None:
        params['recipient'] = recipient
    if recipient_personal_id is not None:
        params['recipient_personal_id'] = str(recipient_personal_id)

    response = await web_app_client.get('/status/', params=params)
    assert response.status == 200
    assert (await response.json())['status'] == expected_status
