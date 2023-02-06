import pytest

EXPECTED_DEALS = [
    {
        'partner_id': '1',
        'title': 'First',
        'kind': 'Фикс-прайс',
        'is_enabled': True,
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ульянов'},
    },
    {
        'partner_id': '1',
        'title': 'Second',
        'kind': 'Купон',
        'is_enabled': True,
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ульянов'},
    },
    {
        'partner_id': '1',
        'title': 'Third',
        'kind': 'Скидка',
        'is_enabled': True,
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ильич'},
    },
    {
        'partner_id': '1',
        'title': 'Fourth',
        'kind': 'Фикс-прайс',
        'is_enabled': False,
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ильич'},
    },
    {
        'partner_id': '2',
        'title': 'Fifth',
        'kind': 'Скидка',
        'is_enabled': True,
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ульянов'},
    },
    {
        'partner_id': '2',
        'title': 'Six',
        'kind': 'Купон',
        'is_enabled': False,
        'changelog': {'created_by': 'Ильич', 'updated_by': 'Ильич'},
    },
]

TARIFF_EDITOR_TRANSLATIONS = {
    'partner_offers_kinds_coupon': {'ru': 'Купон'},
    'partner_offers_kinds_discount': {'ru': 'Скидка'},
    'partner_offers_kinds_fix_price': {'ru': 'Фикс-прайс'},
}


def clean_response(res_json):
    for deal in res_json['deals']:
        del deal['changelog']['created_at']
        del deal['changelog']['updated_at']
        del deal['begin_at']


@pytest.mark.parametrize(
    'filter_kv,indices',
    [
        (dict(), list(range(5, -1, -1))),
        ({'partner_id': '1'}, [3, 2, 1, 0]),
        ({'partner_id': '2'}, [5, 4]),
        ({'updated_by': 'Ильич'}, [5, 3, 2]),
        ({'updated_by': 'Ульянов'}, [4, 1, 0]),
        ({'is_enabled': True}, [4, 2, 1, 0]),
        ({'is_enabled': False}, [5, 3]),
        ({'updated_by': 'Ульянов', 'partner_id': '1'}, [1, 0]),
        ({'updated_by': 'Ильич', 'partner_id': '1', 'is_enabled': True}, [2]),
    ],
)
@pytest.mark.parametrize('consumer, id_offet', [('courier', 6), ('driver', 0)])
@pytest.mark.pgsql('partner_offers', files=['pg_init_items.sql'])
@pytest.mark.translations(tariff_editor=TARIFF_EDITOR_TRANSLATIONS)
async def test_list_deals_filter(
        web_app_client, filter_kv, indices, consumer, id_offet,
):
    filters = [{'field': x, 'value': filter_kv[x]} for x in filter_kv]
    response = await web_app_client.post(
        f'/internal/v1/deals/{consumer}/list/',
        json={'filters': filters} if filters else {},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status == 200, await response.text()
    res_json = await response.json()
    clean_response(res_json)

    expected = {
        'limit': 100,
        'deals': [
            {**EXPECTED_DEALS[i], 'id': str(i + 1 + id_offet)} for i in indices
        ],
    }
    assert res_json == expected


@pytest.mark.parametrize(
    'cursor,limit,indices',
    [(None, 1, [5]), ('2', None, [0]), ('1', None, [])],
)
@pytest.mark.pgsql('partner_offers', files=['pg_init_items.sql'])
@pytest.mark.translations(tariff_editor=TARIFF_EDITOR_TRANSLATIONS)
async def test_list_partners_pagination(
        web_app_client, cursor, limit, indices,
):
    jsn = dict()
    if cursor:
        jsn['cursor'] = cursor
    if limit:
        jsn['limit'] = limit
    response = await web_app_client.post(
        '/internal/v1/deals/driver/list/', json=jsn,
    )
    assert response.status == 200, await response.text()
    expected = dict()
    if cursor:
        expected['cursor'] = cursor
    expected['limit'] = limit or 100
    expected['deals'] = [
        {**EXPECTED_DEALS[i], 'id': str(i + 1)} for i in indices
    ]
    res_json = await response.json()
    clean_response(res_json)
    assert res_json == expected


@pytest.mark.translations(tariff_editor=TARIFF_EDITOR_TRANSLATIONS)
async def test_list_deals_multiple_filters400(web_app_client):
    filters = [{'updated_by': 'Ильич'}, {'category': 'Ульянов'}]
    response = await web_app_client.post(
        '/internal/v1/deals/driver/list/', json={'filters': filters},
    )
    assert response.status == 400, await response.text()


@pytest.mark.parametrize('cursor', ['hello', '-1'])
@pytest.mark.translations(tariff_editor=TARIFF_EDITOR_TRANSLATIONS)
async def test_list_deals_invalid_cursor(web_app_client, cursor):
    response = await web_app_client.post(
        '/internal/v1/deals/driver/list/', json={'cursor': cursor},
    )
    assert response.status == 400, await response.text()


@pytest.mark.translations(tariff_editor=TARIFF_EDITOR_TRANSLATIONS)
async def test_list_deals_invalid_consumer(web_app_client):
    response = await web_app_client.post(
        '/internal/v1/deals/invalid_user/list/', json={},
    )
    assert response.status == 404, await response.text()


@pytest.mark.parametrize(
    'filter_field,filter_value',
    [('partner_id', True), ('updated_by', True), ('is_enabled', 'No')],
)
@pytest.mark.translations(tariff_editor=TARIFF_EDITOR_TRANSLATIONS)
async def test_list_deals_invalid_filters(
        web_app_client, filter_field, filter_value,
):
    response = await web_app_client.post(
        '/internal/v1/deals/driver/list/',
        json={'filters': [{'field': filter_field, 'value': filter_value}]},
    )
    assert response.status == 400, await response.text()
