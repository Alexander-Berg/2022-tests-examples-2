async def test_path_args_simple(taxi_userver_sample):
    response = await taxi_userver_sample.get('path-args/value0/value1')
    assert response.status_code == 200
    resp = response.json()
    assert resp['handler-name'] == 'handler-path-args-simple'
    assert resp['named-path-args'] == {'arg0': 'value0', 'arg1': 'value1'}
    assert resp['path-args'] == ['value0', 'value1']

    response2 = await taxi_userver_sample.get('path-args/value0/')
    assert response2.status_code == 200
    resp2 = response2.json()
    assert resp2['handler-name'] == 'handler-path-args-simple'
    assert resp2['named-path-args'] == {'arg0': 'value0', 'arg1': ''}
    assert resp2['path-args'] == ['value0', '']


async def test_path_args_override(taxi_userver_sample):
    response = await taxi_userver_sample.get('path-args/value0/fixed-arg1')
    assert response.status_code == 200
    resp = response.json()
    assert resp['handler-name'] == 'handler-path-args-override'
    assert resp['named-path-args'] == {'arg0': 'value0', 'arg1': ''}
    assert resp['path-args'] == ['value0']


async def test_path_args_unnamed(taxi_userver_sample):
    response = await taxi_userver_sample.get('path-args/value0/value1/value2')
    assert response.status_code == 200
    resp = response.json()
    assert resp['handler-name'] == 'handler-path-args-unnamed'
    assert resp['named-path-args'] == {'arg0': '', 'arg1': ''}
    assert resp['path-args'] == ['value0', 'value1', 'value2']

    response2 = await taxi_userver_sample.get(
        'path-args/value0/fixed-arg1/value2',
    )
    assert response2.status_code == 200
    resp2 = response2.json()
    assert resp2['handler-name'] == 'handler-path-args-unnamed'
    assert resp2['named-path-args'] == {'arg0': '', 'arg1': ''}
    assert resp2['path-args'] == ['value0', 'fixed-arg1', 'value2']


async def test_path_args_any_suffix(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'path-args/value0/value1/value2/value3',
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['handler-name'] == 'handler-path-args-any-suffix'
    assert resp['named-path-args'] == {'arg0': '', 'arg1': '', 'id': 'value0'}
    assert resp['path-args'] == ['value0', 'value1', 'value2', 'value3']
    assert resp['asterisk-matched-path-suffix'] == 'value1/value2/value3'

    response2 = await taxi_userver_sample.put('path-args/value0/value1/value2')
    assert response2.status_code == 200
    resp2 = response2.json()
    assert resp2['handler-name'] == 'handler-path-args-any-suffix'
    assert resp2['named-path-args'] == {'arg0': '', 'arg1': '', 'id': 'value0'}
    assert resp2['path-args'] == ['value0', 'value1', 'value2']

    response3 = await taxi_userver_sample.get('path-args/value0')
    assert response3.status_code == 200
    resp3 = response3.json()
    assert resp3['handler-name'] == 'handler-path-args-any-suffix'
    assert resp3['named-path-args'] == {'arg0': '', 'arg1': '', 'id': 'value0'}
    assert resp3['path-args'] == ['value0']

    response4 = await taxi_userver_sample.get(
        'path-args/value0/value1/value2/',
    )
    assert response4.status_code == 200
    resp4 = response4.json()
    assert resp4['handler-name'] == 'handler-path-args-any-suffix'
    assert resp4['named-path-args'] == {'arg0': '', 'arg1': '', 'id': 'value0'}
    assert resp4['path-args'] == ['value0', 'value1', 'value2', '']

    response5 = await taxi_userver_sample.get('path-args//value1//')
    assert response5.status_code == 200
    resp5 = response5.json()
    assert resp5['handler-name'] == 'handler-path-args-any-suffix'
    assert resp5['named-path-args'] == {'arg0': '', 'arg1': '', 'id': ''}
    assert resp5['path-args'] == ['', 'value1', '', '']


# pylint: disable=C0103
async def test_path_args_any_suffix_not_match(taxi_userver_sample):
    response = await taxi_userver_sample.get('path-args')
    assert response.status_code == 404


async def test_path_param_with_dash(taxi_userver_sample, mockserver):
    @mockserver.json_handler(
        '/userver-sample/autogen/test-path-param/my-param',
    )
    def _handler(request):
        return mockserver.make_response(json={'path-param': 'my-param'})

    response = await taxi_userver_sample.get(
        'autogen/test-path-param/my-param',
    )
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'path-param': 'my-param'}
