import pytest

WEBHOOK_DATA = {'ticket': 'some_queue-1'}


@pytest.mark.parametrize(
    'data, api_key, expected_response',
    [
        (WEBHOOK_DATA, 'support-taxi_api_key', 200),
        (WEBHOOK_DATA, 'random_key', 401),
    ],
)
async def test_auth_required(
        cbox,
        mock_st_get_ticket_with_status,
        mock_st_get_all_attachments,
        mock_st_update_ticket,
        mock_st_get_comments,
        mock_personal,
        data,
        api_key,
        expected_response,
):
    mock_st_get_ticket_with_status('closed')
    mock_st_update_ticket('closed')
    mock_st_get_comments([])
    mock_st_get_all_attachments(empty=True)
    await cbox.post(
        '/v1/webhooks/startrack_task',
        data=data,
        headers={'X-ChatterBox-API-Key': api_key},
    )
    assert cbox.status == expected_response
