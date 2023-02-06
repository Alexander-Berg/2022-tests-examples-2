import pytest


TRANSLATIONS = {
    'errors.unknown_ticket_type': {'en': 'Ticket has unknown type'},
    'errors.ticket_not_found': {'en': 'Ticket was not found'},
}


@pytest.mark.translations(support_info=TRANSLATIONS)
@pytest.mark.parametrize('ticket_id', ('123', 'BACKEND_1', 'asd'))
async def test_validation(support_info_client, ticket_id: str):
    response = await support_info_client.get(
        '/v1/admin/check_ticket_exists',
        params={'ticket_id': ticket_id},
        headers={'Accept-Language': 'en'},
    )
    assert response.status == 400
    response_json = await response.json()
    assert response_json == {
        'status': 'request_error',
        'error': 'unknown_ticket_type',
        'message': 'Ticket has unknown type',
    }


@pytest.mark.translations(support_info=TRANSLATIONS)
@pytest.mark.parametrize(
    ('chatterbox_response_status', 'expected_status', 'response_body'),
    (
        (200, 200, {}),
        (
            404,
            404,
            {
                'status': 'error',
                'error': 'ticket_not_found',
                'message': 'Ticket was not found',
            },
        ),
    ),
)
async def test_check_chatterbox_ticket(
        support_info_client,
        patch_chatterbox_get_by_id,
        chatterbox_response_status: int,
        expected_status: int,
        response_body: dict,
):
    patch_chatterbox_get_by_id(response={}, status=chatterbox_response_status)

    response = await support_info_client.get(
        '/v1/admin/check_ticket_exists',
        params={'ticket_id': '5b2cae5cb2682a976914c2a3'},
        headers={'Accept-Language': 'en'},
    )
    assert response.status == expected_status
    response_json = await response.json()
    assert response_json == response_body


@pytest.mark.translations(support_info=TRANSLATIONS)
@pytest.mark.parametrize(
    ('startrack_response_status', 'expected_status', 'response_body'),
    (
        (200, 200, {}),
        (
            404,
            404,
            {
                'status': 'error',
                'error': 'ticket_not_found',
                'message': 'Ticket was not found',
            },
        ),
    ),
)
async def test_check_startrack_ticket(
        support_info_client,
        patch_get_startrack_ticket,
        startrack_response_status: int,
        expected_status: int,
        response_body: dict,
):
    patch_get_startrack_ticket(response={}, status=startrack_response_status)

    response = await support_info_client.get(
        '/v1/admin/check_ticket_exists',
        params={'ticket_id': 'TESTBACKEND-1'},
        headers={'Accept-Language': 'en'},
    )
    assert response.status == expected_status
    response_json = await response.json()
    assert response_json == response_body
