import pytest


@pytest.mark.parametrize(
    ['query_dict', 'archive_status', 'expected_status', 'expected_content'],
    [
        ({'order_id': 'x'}, 'restored', 200, {}),
        ({'order_id': 'x'}, 'mongo', 200, {}),
        # empty query
        (
            {},
            None,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'order_id is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
        # non-existent order
        (
            {'order_id': 'xxx'},
            'not_found',
            404,
            {'code': 'not_found', 'message': 'Order not found'},
        ),
        # already being restored
        (
            {'order_id': 'x'},
            'conflict',
            409,
            {'code': 'conflict', 'message': 'Already restoring'},
        ),
    ],
)
async def test_restore_order(
        web_app_client,
        mockserver,
        query_dict,
        archive_status,
        expected_status,
        expected_content,
):
    @mockserver.json_handler('/archive-api/archive/orders/restore')
    def _archive_api_restore_order(request):
        return [{'id': request.json['id'], 'status': archive_status}]

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    def _archive_api_restore_order_proc(request):
        return [{'id': request.json['id'], 'status': archive_status}]

    response = await web_app_client.post(
        '/v1/order/restore/', params=query_dict, json={},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_content
