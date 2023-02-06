_ORDER_DRAFT_PATH = '3.0/orderdraft'


def orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order,
        bearer=None,
        cookie=None,
        headers={},
        x_real_ip='my-ip-address',
        expected_code=200,
        zones_filename=None,
        is_yamaps_mocked=False,
        is_blackbox_mocked=False,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_pickup_zones(request):
        if zones_filename is not None:
            return load_json(order + '/' + zones_filename)
        return {}

    if not is_yamaps_mocked:

        @mockserver.json_handler('/addrs.yandex/search')
        def mock_yamaps(request):
            geo_docs = load_json(order + '/yamaps.json')
            for doc in geo_docs:
                if request.query_string.decode().find(doc['url']) != -1:
                    return doc['response']

    @mockserver.json_handler('/chat/1.0/chat')
    def mock_chat(request):
        return {'id': 'some_new_chat_id'}

    if not is_blackbox_mocked:

        @mockserver.json_handler('/blackbox')
        def mock_blackbox(request):
            query = set(request.query_string.decode().split('&'))
            assert (
                query
                == {
                    'method=oauth',
                    'userip=my-ip-address',
                    'format=json',
                    'dbfields=subscription.suid.669',
                    'aliases=1%2C10%2C16',
                    'oauth_token=test_token',
                    'getphones=bound',
                    'get_login_id=yes',
                    'phone_attributes=102%2C107%2C4',
                }
                or query
                == {
                    'method=sessionid',
                    'userip=my-ip-address',
                    'host=yandex.ru',
                    'format=json',
                    'dbfields=subscription.suid.669',
                    'sessionid=5',
                    'getphones=bound',
                    'get_login_id=yes',
                    'phone_attributes=102%2C107',
                }
            )
            return {
                'uid': {'value': '4003514353'},
                'status': {'value': 'VALID'},
                'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
                'phones': [
                    {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                    {
                        'attributes': {'102': '+72222222222', '107': '1'},
                        'id': '2222',
                    },
                ],
            }

    if bearer is not None:
        response = taxi_protocol.post(
            _ORDER_DRAFT_PATH,
            request,
            bearer=bearer,
            headers=headers,
            x_real_ip=x_real_ip,
        )
    else:
        headers['Cookie'] = cookie
        response = taxi_protocol.post(
            _ORDER_DRAFT_PATH,
            request,
            bearer=None,
            headers=headers,
            x_real_ip=x_real_ip,
        )
    assert response.status_code == expected_code
    if response.status_code != 500:
        return response.json()
