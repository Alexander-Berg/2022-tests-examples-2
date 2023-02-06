import pytest


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'dst': 'passport-yateam', 'src': 'example_service'}],
)
async def test_happy_path(web_context, mockserver, patch):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def handler(request):
        assert request.query['login'] == 'abacaba'
        assert request.query['userip'] == '127.0.0.1'
        assert request.query['method'] == 'userinfo'
        assert request.headers['X-Ya-Service-Ticket'] == 'ticket'
        return {'users': [{'uid': {'value': 'azaz'}}]}

    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(dst_service_name, use_tvm_enabled, log_extra):
        return 'ticket'

    result = await web_context.client_passport_ya_team.get_info_by_login(
        login='abacaba', user_ip='127.0.0.1',
    )

    assert result == {'uid': 'azaz'}

    get_ticket_calls = get_ticket.calls
    assert len(get_ticket_calls) == 1
    call = get_ticket_calls[0]
    call.pop('log_extra')
    assert get_ticket_calls == [
        {'dst_service_name': 'passport-yateam', 'use_tvm_enabled': True},
    ]

    assert handler.times_called == 1


@pytest.mark.parametrize('get_user_ticket', [True, False])
async def test_get_user_ticket_with_token(
        web_context, mockserver, get_user_ticket,
):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def handler(request):
        assert request.query['method'] == 'oauth'
        assert request.query['oauth_token'] == 'aaa'
        assert request.query['userip'] == '127.0.0.1'
        get_user_ticket_query = request.query['get_user_ticket']
        if get_user_ticket:
            assert get_user_ticket_query == 'yes'
        else:
            assert get_user_ticket_query == 'no'

        data = {'uid': {'value': 'azaz'}, 'status': {'value': 'VALID'}}
        if get_user_ticket:
            data['user_ticket'] = 'BACBAC'

        return data

    response = await web_context.client_passport_ya_team.get_info_by_token(
        token='aaa', user_ip='127.0.0.1', get_user_ticket=get_user_ticket,
    )

    assert response['uid'] == 'azaz'
    if get_user_ticket:
        assert response['user_ticket'] == 'BACBAC'
    else:
        assert response['user_ticket'] is None

    assert handler.times_called == 1


@pytest.mark.parametrize('get_user_ticket', [True, False])
async def test_get_user_ticket_with_sid(
        web_context, mockserver, get_user_ticket,
):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def handler(request):
        assert request.query['method'] == 'sessionid'
        assert request.query['sessionid'] == 'sid'
        assert request.query['userip'] == '127.0.0.1'
        get_user_ticket_query = request.query['get_user_ticket']
        if get_user_ticket:
            assert get_user_ticket_query == 'yes'
        else:
            assert get_user_ticket_query == 'no'

        data = {'uid': {'value': 'azaz'}, 'status': {'value': 'VALID'}}
        if get_user_ticket:
            data['user_ticket'] = 'BACBAC'

        return data

    response = await web_context.client_passport_ya_team.get_info_by_sid(
        sid='sid', user_ip='127.0.0.1', get_user_ticket=get_user_ticket,
    )

    assert response['uid'] == 'azaz'
    if get_user_ticket:
        assert response['user_ticket'] == 'BACBAC'
    else:
        assert response['user_ticket'] is None

    assert handler.times_called == 1
