import pytest


DEFAULT_LIMIT = 100
DEFAULT_OFFSET = 0


async def test_internal_list_ok_all_formats_false(web_app_client, load_json):
    response = await web_app_client.get('/internal/list', params={'limit': 6})
    data = await response.json()
    assert response.status == 200
    assert data == load_json('response_ok_all_formats_false.json')


async def test_internal_list_ok_all_formats_true(web_app_client, load_json):
    # 2 more records of non-default format are returned
    response = await web_app_client.get(
        '/internal/list?all_formats=true', params={'limit': 6},
    )
    data = await response.json()
    assert response.status == 200
    assert data == load_json('response_ok_all_formats_true.json')


@pytest.mark.parametrize(
    ['limit', 'offset', 'all_formats', 'expected', 'total'],
    [
        # collection fixture has 64 rows total,
        # where 4 have non-default formats
        (None, None, None, 60, 60),  # default limit=100, offset=0
        (None, 0, None, 60, 60),
        (None, 20, None, 40, 60),
        (30, None, None, 30, 60),
        (20, 0, None, 20, 60),
        (20, 20, None, 20, 60),
        (59, 0, None, 59, 60),
        (60, 0, None, 60, 60),
        (100, 0, None, 60, 60),
        (100, 55, None, 5, 60),
        (100, 100, None, 0, 60),
        (100, 0, False, 60, 60),
        (20, 20, True, 20, 64),
        (100, 0, True, 64, 64),
        (100, 55, True, 9, 64),
    ],
)
async def test_internal_list_paging(
        web_app_client, limit, offset, all_formats, expected, total,
):
    params = {}
    url = '/internal/list'
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    if all_formats is not None:
        # params of .get() dont support boolean 0_o
        url += '?all_formats=true' if all_formats else '?all_formats=false'
    response = await web_app_client.get(url, params=params)
    data = await response.json()
    assert response.status == 200
    assert data['total'] == total
    assert len(data['items']) == expected
    assert data['limit'] == (limit or DEFAULT_LIMIT)
    assert data['offset'] == (offset or DEFAULT_OFFSET)
