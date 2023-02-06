import pytest


DEFAULT_NAME = 'Neo'


@pytest.mark.parametrize('name', ['Arthas', None])
async def test_happy_path(web_app_client, name):
    params = {}
    if name is not None:
        params['name'] = name
    response = await web_app_client.get('/default_parameter', params=params)
    assert response.status == 200
    assert await response.json() == {'name': name or DEFAULT_NAME}


@pytest.mark.parametrize(
    'req_ids, req_body, resp',
    [
        (None, None, {'ids': ['foo', 'bar'], 'body': ['goo', 'gar']}),
        (['foo'], None, {'ids': ['foo'], 'body': ['goo', 'gar']}),
        (
            None,
            ['well', 'hello'],
            {'ids': ['foo', 'bar'], 'body': ['well', 'hello']},
        ),
    ],
)
async def test_arrays(web_app_client, req_ids, req_body, resp):
    params = {}
    if req_ids:
        params['ids'] = ','.join(req_ids)
    response = await web_app_client.post(
        '/array-default', params=params, json=req_body,
    )
    assert await response.json() == resp
