# -*- coding: utf-8 -*-

from sandbox.projects.EntitySearchNMetaToAppHost.lib.req_converter import convert_request_url_to_apphost_context


def test_req_converter():
    url = '/search?client=nmeta&lr=213&qtree=abc&rearr=is_mobile%3D1;entsearch_experiment=exp' \
        '&ento=0oCglydXc2MjQ3MzgSEHJ1dzIwNTIwOTAtYXNzb2MYAh8G-m4&text=my_text&tld=ru' \
        '&user_request=%D0%9F%D0%B8+%D1%84%D0%B8%D0%BB%D1%8C%D0%BC'
    ret = convert_request_url_to_apphost_context(url)
    assert isinstance(ret, list)
    assert len(ret) == 1
    init_request = ret[0]
    assert isinstance(init_request, dict)
    assert 'name' in init_request
    assert init_request['name'] == 'INIT'
    assert 'results' in init_request
    results = init_request['results']
    assert len(results) == 3
    request = results[0]
    device = results[1]
    internal_params = results[2]
    assert isinstance(request, dict)
    assert isinstance(device, dict)
    assert isinstance(internal_params, dict)
    assert request['type'] == 'request'
    assert device['type'] == 'device'
    assert internal_params['type'] == 'flags'

    assert request['uri'] == url
    params = request['params']
    assert isinstance(params, dict)
    assert params['lr'] == ['213']
    assert params['qtree'] == ['abc']
    assert params['ento'] == ['0oCglydXc2MjQ3MzgSEHJ1dzIwNTIwOTAtYXNzb2MYAh8G-m4']
    assert params['text'] == ['my_text']
    assert params['user_request'] == ['Пи фильм']
    assert 'client' not in params
    assert request['tld'] == 'ru'
    rearr = internal_params['all']['CONTEXT']['MAIN']['source']['WEB_ALL']['rearr']
    assert isinstance(rearr, list)
    assert len(rearr) == 1
    assert rearr[0] == 'is_mobile=1;entsearch_experiment=exp'

    assert device['is_mobile'] == 1
