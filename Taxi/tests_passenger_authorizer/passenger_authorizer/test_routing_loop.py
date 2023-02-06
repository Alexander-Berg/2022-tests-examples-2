import pytest


# Generated with:
# ya tool tvmknife unittest service --src 404 --dst 101
TVM_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIlAMQZQ:Dp-l02wKq6RMvh5VMkux17_8ES7EUAsAEvp'
    '88BYHzwCYOL6cNKKGHA21BhE5J-ePB6KdNNHpbYE2KqIDY7kssiJ2TDMQ79qlQX8qwLDl'
    'VR0QGRMuwt6C2DVhY2V9CbDaamvHTjRozKJMAJd1kX_UFCegkRYdlC-1FN18CozWrJQ'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'passenger-authorizer'}],
)
async def test_remote_ip_tvm(taxi_passenger_authorizer, mockserver):
    @mockserver.json_handler('/blackbox')
    def _mock_blackbox(request):
        assert False

    @mockserver.json_handler('/4.0/route403')
    def _test(request):
        assert False

    headers = {
        'X-Real-IP': '1.2.3.4',
        'X-Remote-Ip': 'remote',
        'X-Ya-Service-Ticket': TVM_SERVICE_TICKET,
    }
    response = await taxi_passenger_authorizer.post(
        '4.0/route403', bearer='test_token', headers=headers,
    )

    assert response.status == 400
    assert response.json()['code'] == 'ROUTING_LOOP_DETECTED'
