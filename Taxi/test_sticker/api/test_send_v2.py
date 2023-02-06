import pytest


@pytest.mark.parametrize(
    'request_data,expected_stq_times_called',
    [
        (
            # the same token as in db
            {
                'account': 'taxi',
                'send_to': ['1'],
                'idempotence_token': '1',
                'campaign_slug': 'TEST',
                'args': {'a': 1, 'b': 2},
            },
            0,
        ),
        (
            # different token
            {
                'account': 'taxi',
                'send_to': ['1'],
                'idempotence_token': '2',
                'campaign_slug': 'TEST',
                'args': {'a': 1, 'b': 2},
            },
            1,
        ),
        (
            # different token with attachments
            {
                'account': 'taxi',
                'send_to': ['1'],
                'idempotence_token': '2',
                'campaign_slug': 'TEST',
                'args': {'a': 1, 'b': 2},
                'attachments': [
                    {
                        'filename': 'a.json',
                        'mime_type': 'application/json',
                        'data': 'data',
                    },
                ],
            },
            1,
        ),
    ],
)
@pytest.mark.usefixtures('mock_tvm')
@pytest.mark.config(
    TVM_ENABLED=True,
    STICKER_RAW_SEND_ALLOWED_SERVICES={'tvm_names': ['src_test_service']},
)
@pytest.mark.config(TVM_RULES=[{'src': 'sticker', 'dst': 'personal'}])
async def test_send_v2(
        web_app_client,
        mockserver,
        request_data,
        expected_stq_times_called,
        web_context,
):
    @mockserver.json_handler('/stq-agent/queues/api/add/sticker_send_email')
    async def _mock_stq_agent_queue(request):
        data = request.json
        assert data['task_id'] == '2'
        return {}

    response = await web_app_client.post(
        '/v2/send/',
        json=request_data,
        headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == 200
    assert _mock_stq_agent_queue.times_called == expected_stq_times_called

    async with web_context.pg.master.acquire() as connection:
        query = 'SELECT * FROM sticker.mail_queue'
        products_result = await connection.fetch(query)
        if len(products_result) > 1:
            assert products_result[1]['tvm_name'] == 'src_test_service'
