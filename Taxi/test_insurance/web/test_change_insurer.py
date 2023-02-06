async def test_simple(web_app_client, mockserver):
    order_id = 'some_order_id'

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _handler_get_order_fields(request):
        assert request.json == {
            'fields': ['insurer_id', 'order.user_id'],
            'order_id': 'some_order_id',
            'lookup_flags': 'none',
            'require_latest': False,
            'search_archive': False,
        }
        return {
            'fields': {
                'insurer_id': 'insurer_id_1',
                '_id': order_id,
                'order': {'user_id': '485bc80721964a95a04ee0ddcc27a174'},
            },
            'order_id': order_id,
            'replica': 'secondary',
            'version': 'DAAAAAAABgAMAAQABgAAAIBq0rV4AQAA',
        }

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _handler_set_order_fields(request):
        assert request.json == {
            'order_id': 'some_order_id',
            'user_id': '485bc80721964a95a04ee0ddcc27a174',
            'version': 'DAAAAAAABgAMAAQABgAAAIBq0rV4AQAA',
            'update': {'set': {'insurer_id': 'insurer_id_2'}},
            'call_processing': False,
        }
        return {}

    response = await web_app_client.post(
        '/internal/change_insurer',
        json={
            'order_id': order_id,
            'insurer_id_from': 'insurer_id_1',
            'insurer_id_to': 'insurer_id_2',
        },
    )
    assert response.status == 200
