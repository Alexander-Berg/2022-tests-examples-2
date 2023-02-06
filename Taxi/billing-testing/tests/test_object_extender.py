# coding: utf8

import pytest

from sibilla import utils


def test_lookup_table():
    data = {
        'request': {
            'part1': {'foo': 'foo', 'bar': 'bar'},
            'part2': [7, 6, 5, 4, 3, 2, 1],
        },
        'response': [{'baz': 'baz'}, 'token'],
    }
    assert list(utils.lookup_data('response', data)) == [data['response']]
    assert list(utils.lookup_data('request', data)) == [data['request']]
    assert list(utils.lookup_data('request.part1', data)) == [
        data['request']['part1'],
    ]
    assert list(utils.lookup_data('request.part1.foo', data)) == [
        data['request']['part1']['foo'],
    ]
    assert list(utils.lookup_data('request.part2.2', data)) == [
        data['request']['part2'][2],
    ]
    assert list(utils.lookup_data('response.1', data)) == [data['response'][1]]
    assert list(utils.lookup_data('response.0.baz', data)) == [
        data['response'][0]['baz'],
    ]
    assert list(utils.lookup_data('response.*', data)) == [
        data['response'][0],
        data['response'][1],
    ]


@pytest.mark.asyncio
async def test_replace_single_elements():
    substitutions = {
        'last': {'body': {'some_json_value': []}},
        'request': {
            'body': {'request_body': 'body'},
            'headers': [
                'content-type: application/json',
                'x-auth-token: some_token',
            ],
        },
    }
    # assert utils.build('@last', substitutions) == substitutions['last']
    assert utils.build(['@last.body'], substitutions) == [
        substitutions['last']['body'],
    ]
    assert utils.build({'last': '@last'}, substitutions) == {
        'last': substitutions['last'],
    }
    assert (
        utils.build('@request.headers.0', substitutions)
        == substitutions['request']['headers'][0]
    )
    assert utils.build(42, substitutions) == 42


@pytest.mark.asyncio
async def test_imutable_of_source():
    source = '@data'
    values = {'data': [{'value': 1}, {'value': 2}, {'value': 3}]}
    assert utils.build(source, values) == values['data']
    assert source == '@data'


@pytest.mark.asyncio
async def test_global_functions():
    values = {'data': [1, 2, 3]}
    assert utils.build('@max(data)', values) == 3
    assert utils.build('@test_fn(data)', values, {'test_fn': sum}) == 6
