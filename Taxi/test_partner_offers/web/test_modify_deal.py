import datetime
import typing

import pytest

TEST_LOYALTIES = [
    [
        {'loyalty': 'bronze', 'is_enabled': False},
        {'loyalty': 'gold', 'is_enabled': True},
        {'loyalty': 'platinum', 'is_enabled': False},
        {'loyalty': 'silver', 'is_enabled': False},
    ],
    [
        {'loyalty': '1', 'is_enabled': False},
        {'loyalty': '2', 'is_enabled': False},
        {'loyalty': '3', 'is_enabled': True},
        {'loyalty': '4', 'is_enabled': False},
        {'loyalty': '5', 'is_enabled': False},
    ],
]

TEST_BASIC_DATA: typing.Dict[str, typing.Any] = {
    'title': 'foo',
    'subtitle': '1',
    'kind': {
        'text': 'text1',
        'price': {'decimal_value': '1', 'currency': 'RUB'},
    },
    'is_enabled': True,
    'begin_at': '2019-11-18T03:03:08+04:00',
    'description_title': '1',
    'description': '1',
}

EXPECTED = [
    {
        'loyalty_statuses': [
            {'loyalty': 'bronze', 'is_enabled': False},
            {'loyalty': 'gold', 'is_enabled': False},
            {'loyalty': 'platinum', 'is_enabled': False},
            {'loyalty': 'silver', 'is_enabled': False},
        ],
        'contractor_merch_offer_id': '33333333333333333333333333333333',
        'title': 'foo',
        'subtitle': 'here_will_be_cm_subtitle',
        'icon': 'here_will_be_cm_link',
        'kind': {'price': {'currency': 'RUB', 'decimal_value': '0'}},
        'is_enabled': True,
        'begin_at': datetime.datetime(
            1970,
            1,
            1,
            0,
            0,
            0,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=0)),
        ),
        'description_title': 'here_will_be_cm_title',
        'description': 'here_will_be_cm_description',
    },
    {
        'loyalty_statuses': [
            {'loyalty': '1', 'is_enabled': False},
            {'loyalty': '2', 'is_enabled': False},
            {'loyalty': '3', 'is_enabled': False},
            {'loyalty': '4', 'is_enabled': False},
            {'loyalty': '5', 'is_enabled': False},
        ],
        'contractor_merch_offer_id': '33333333333333333333333333333333',
        'title': 'foo',
        'subtitle': 'here_will_be_cm_subtitle',
        'icon': 'here_will_be_cm_link',
        'kind': {'price': {'currency': 'RUB', 'decimal_value': '0'}},
        'is_enabled': True,
        'begin_at': datetime.datetime(
            1970,
            1,
            1,
            0,
            0,
            0,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=0)),
        ),
        'description_title': 'here_will_be_cm_title',
        'description': 'here_will_be_cm_description',
    },
]


def _fix_dates(json_data):
    for key in ('begin_at', 'finish_at'):
        if key in json_data:
            json_data[key] = datetime.datetime.fromisoformat(json_data[key])


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize('consumer,num', [('driver', 0), ('courier', 1)])
@pytest.mark.parametrize(
    'basic_data',
    [TEST_BASIC_DATA, {'title': 'foo', 'contractor_merch_offer_id': '3' * 32}],
)
async def test_modify_basic_data(web_app_client, consumer, basic_data, num):
    request = {**basic_data}
    if 'contractor_merch_offer_id' not in basic_data:
        request['loyalty_statuses'] = TEST_LOYALTIES[num]
    deal_id = 1 if consumer == 'driver' else 2
    response = await web_app_client.put(
        f'/internal/v1/deals/{consumer}/basic-data?deal_id={deal_id}',
        json=request,
        headers={'X-Yandex-Login': 'barracuda'},
    )
    assert response.status == 200, await response.text()
    resp_json = await response.json()
    _fix_dates(resp_json['basic_data'])
    _fix_dates(request)
    if 'contractor_merch_offer_id' not in basic_data:
        assert resp_json['basic_data'] == request
    else:
        assert resp_json['basic_data'] == EXPECTED[num]
    assert resp_json['changelog']['updated_by'] == 'barracuda'


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize('map_pin_text', ['Hello', None])
async def test_modify_basic_data_map_pin_text(web_app_client, map_pin_text):
    request = {**TEST_BASIC_DATA, 'loyalty_statuses': TEST_LOYALTIES[0]}
    if map_pin_text:
        request['map_pin_text'] = map_pin_text
    response = await web_app_client.put(
        f'/internal/v1/deals/driver/basic-data?deal_id=1',
        json=request,
        headers={'X-Yandex-Login': 'barracuda'},
    )
    assert response.status == 200, await response.text()
    resp_json = await response.json()
    assert resp_json['basic_data'].get('map_pin_text', None) == map_pin_text


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize(
    'consumer,deal_id',
    [('driver', 20), ('courier', 20), ('driver', 2), ('courier', 1)],
)
async def test_modify_basic_data_not_found(web_app_client, consumer, deal_id):
    request = {
        **TEST_BASIC_DATA,
        'loyalty_statuses': TEST_LOYALTIES[0 if consumer == 'driver' else 1],
    }
    response = await web_app_client.put(
        f'/internal/v1/deals/{consumer}/basic-data?deal_id={deal_id}',
        json=request,
        headers={'X-Yandex-Login': 'barracuda'},
    )
    assert response.status == 404, await response.text()


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize('consumer,deal_id', [('driver', 1), ('courier', 2)])
async def test_modify_locations(web_app_client, pgsql, consumer, deal_id):
    response = await web_app_client.put(
        f'/internal/v1/deals/{consumer}/'
        f'locations-availability?deal_id={deal_id}',
        json=[
            {'id': '101', 'is_enabled': False},
            {'id': '102', 'is_enabled': False},
        ],
        headers={'X-Yandex-Login': 'barracuda'},
    )
    assert response.status == 200, await response.text()
    cursor = pgsql['partner_offers'].cursor()
    cursor.execute(
        'SELECT business_oid FROM '
        'location JOIN deal on location.partner_id = deal.partner_id'
        f' WHERE deal.id = {deal_id} AND '
        ' NOT EXISTS(SELECT 1 FROM active_deal_location'
        ' WHERE deal_id = deal.id AND location_id = location.business_oid);',
    )
    assert set(x[0] for x in cursor) == {101, 102}
    assert (await response.json())['changelog']['updated_by'] == 'barracuda'


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize(
    'consumer,deal_id',
    [('driver', 20), ('courier', 20), ('driver', 2), ('courier', 1)],
)
async def test_modify_locations_not_found(web_app_client, consumer, deal_id):
    response = await web_app_client.put(
        f'/internal/v1/deals/{consumer}/'
        f'locations-availability?deal_id={deal_id}',
        json=[
            {'id': '101', 'is_enabled': False},
            {'id': '102', 'is_enabled': False},
        ],
        headers={'X-Yandex-Login': 'barracuda'},
    )
    assert response.status == 404, await response.text()


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize('consumer,deal_id', [('driver', 1), ('courier', 2)])
async def test_delete_deal(web_app_client, pgsql, consumer, deal_id):
    response = await web_app_client.delete(
        f'/internal/v1/deals/{consumer}?deal_id={deal_id}',
    )
    assert response.status == 200, await response.text()
    cursor = pgsql['partner_offers'].cursor()
    cursor.execute(
        'SELECT business_oid FROM '
        'location JOIN deal on location.partner_id = deal.partner_id'
        f' WHERE deal.id = {deal_id} AND '
        ' NOT EXISTS(SELECT 1 FROM active_deal_location'
        ' WHERE deal_id = deal.id AND location_id = location.business_oid);',
    )
    assert not set(cursor)

    cursor = pgsql['partner_offers'].cursor()
    cursor.execute(
        f'SELECT * FROM deal_consumer_subclass' f' WHERE deal_id = {deal_id};',
    )
    assert not set(cursor)

    cursor = pgsql['partner_offers'].cursor()
    cursor.execute(f'SELECT * FROM deal WHERE id = {deal_id};')
    assert not set(cursor)


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize(
    'consumer,loyalties, deal_id',
    [
        ('driver', ['1', '2', '3', '4', '5'], 1),
        ('courier', ['1', '2', '3', '4', '5', '5'], 2),
        ('driver', ['bronze', 'silver', 'gold', 'platinum', 'bronze'], 1),
        ('courier', ['bronze', 'silver', 'gold', 'platinum'], 2),
    ],
)
async def test_invalid_loyalty(web_app_client, consumer, loyalties, deal_id):
    request = {
        **TEST_BASIC_DATA,
        'loyalty_statuses': [
            {'loyalty': l, 'is_enabled': True} for l in loyalties
        ],
    }
    response = await web_app_client.put(
        f'/internal/v1/deals/{consumer}/basic-data?deal_id={deal_id}',
        json=request,
        headers={'X-Yandex-Login': 'barracuda'},
    )
    assert response.status == 400, await response.text()
