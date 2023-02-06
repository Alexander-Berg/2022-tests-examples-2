import pytest

EXPECTED_PARTNERS = [
    {
        'id': '1',
        'name': 'Грибница',
        'category': 'food',
        'logo': 'https://example.com/image.jpg',
        'deals_number': 2,
        'changelog': {
            'created_at': '2019-05-26T19:10:25+03:00',
            'created_by': 'Ильич',
            'updated_at': '2019-05-26T19:10:25+03:00',
            'updated_by': 'Ильич',
        },
    },
    {
        'id': '2',
        'name': 'Радиоволна',
        'category': 'service',
        'logo': 'http://bronevik.com/im.png',
        'deals_number': 1,
        'changelog': {
            'created_at': '2019-05-28T19:10:25+03:00',
            'created_by': 'Ульянов',
            'updated_at': '2019-07-28T19:10:25+03:00',
            'updated_by': 'Ульянов',
        },
    },
    {
        'id': '3',
        'name': 'Мухоморье',
        'category': 'food',
        'deals_number': 0,
        'changelog': {
            'created_at': '2019-05-29T19:10:25+03:00',
            'created_by': 'Ульянов',
            'updated_at': '2019-07-29T19:10:25+03:00',
            'updated_by': 'Ульянов',
        },
    },
    {
        'id': '4',
        'name': 'не действующие офферы',
        'category': 'food',
        'deals_number': 0,
        'changelog': {
            'created_at': '2019-05-29T19:10:25+03:00',
            'created_by': 'Ульянов',
            'updated_at': '2019-07-29T19:10:25+03:00',
            'updated_by': 'Ульянов',
        },
    },
]


@pytest.mark.parametrize(
    'filter_kv,indices',
    [
        (dict(), [3, 2, 1, 0]),
        ({'category': 'service'}, [1]),
        ({'category': 'food'}, [3, 2, 0]),
        ({'updated_by': 'Ильич'}, [0]),
        ({'updated_by': 'Ульянов'}, [3, 2, 1]),
        ({'category': 'other'}, []),
        ({'updated_by': 'other'}, []),
        ({'name': 'Грибница'}, [0]),
    ],
)
@pytest.mark.pgsql('partner_offers', files=['pg_init_items.sql'])
async def test_list_partners_filter(web_app_client, filter_kv, indices):
    filters = [{'field': x, 'value': filter_kv[x]} for x in filter_kv]
    response = await web_app_client.post(
        '/internal/v1/partners/list/', json={'filters': filters},
    )

    assert response.status == 200, await response.text()
    expected = {
        'limit': 100,
        'partners': [EXPECTED_PARTNERS[i] for i in indices],
    }
    assert await response.json() == expected


@pytest.mark.parametrize(
    'cursor,limit,indices',
    [(None, 1, [3]), ('2', None, [0]), ('1', None, [])],
)
@pytest.mark.pgsql('partner_offers', files=['pg_init_items.sql'])
async def test_list_partners_pagination(
        web_app_client, cursor, limit, indices,
):
    jsn = dict()
    if cursor:
        jsn['cursor'] = cursor
    if limit:
        jsn['limit'] = limit
    response = await web_app_client.post(
        '/internal/v1/partners/list/', json=jsn,
    )
    assert response.status == 200, await response.text()
    expected = dict()
    if cursor:
        expected['cursor'] = cursor
    expected['limit'] = limit or 100
    expected['partners'] = [EXPECTED_PARTNERS[i] for i in indices]
    assert await response.json() == expected


async def test_list_partners_multiple_filters400(web_app_client):
    filters = [{'category': 'food'}, {'category': 'service'}]
    response = await web_app_client.post(
        '/internal/v1/partners/list/', json={'filters': filters},
    )
    assert response.status == 400, await response.text()


@pytest.mark.parametrize('cursor', ['hello', '-1'])
async def test_list_partners_invalid_cursor(web_app_client, cursor):
    response = await web_app_client.post(
        '/internal/v1/partners/list/', json={'cursor': cursor},
    )
    assert response.status == 400, await response.text()


@pytest.mark.pgsql(
    'partner_offers',
    queries=[
        """
    INSERT INTO partner
    (id, geo_chain_id, category, created_by, updated_by, name)
    VALUES (1,1, 'food', 'ilich', 'ilich', 'Супермаркет'),
    (2,2, 'food', 'ilich', 'ilich', 'Супермаркет Дикси'),
    (3,3, 'food', 'ilich', 'ilich', 'Супермаркет Абсент'),
    (4,4, 'food', 'ilich', 'ilich', 'Супермаркет Вода')
    ;
    """,
    ],
)
@pytest.mark.parametrize('name_req', ['Супер Ди', 'Дикс', 'Дикси'])
async def test_spaces_in_list(web_app_client, name_req):
    response = await web_app_client.post(
        '/internal/v1/partners/list/',
        json={'filters': [{'field': 'name', 'value': name_req}]},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    if 'partners' in body:
        for val in body['partners']:
            del val['changelog']['updated_at']
            del val['changelog']['created_at']
    assert body == {
        'limit': 100,
        'partners': [
            {
                'id': '2',
                'name': 'Супермаркет Дикси',
                'category': 'food',
                'deals_number': 0,
                'changelog': {'created_by': 'ilich', 'updated_by': 'ilich'},
            },
        ],
    }
