import datetime
import typing

import pytest

TEST_BASIC_DATA: typing.Dict[str, typing.Any] = {
    'title': 'title',
    'loyalty_statuses': [
        {'loyalty': 'bronze', 'is_enabled': False},
        {'loyalty': 'gold', 'is_enabled': False},
        {'loyalty': 'platinum', 'is_enabled': False},
        {'loyalty': 'silver', 'is_enabled': False},
    ],
    'contractor_merch_offer_id': '01234567890123456789012345678901',
}


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
@pytest.mark.parametrize(
    'basic_data',
    [
        TEST_BASIC_DATA,
        {
            'title': 'title',
            'loyalty_statuses': [],
            'contractor_merch_offer_id': '01234567890123456789012345678901',
        },
    ],
)
async def test_create_ok(web_app_client, basic_data):
    response = await web_app_client.post(
        '/internal/v1/deals/driver/',
        json={
            'partner_id': '1',
            'basic_data': basic_data,
            'locations_availability': [{'id': '102', 'is_enabled': True}],
        },
        headers={
            'X-Yandex-Login': 'hello',
            'X-Idempotency-Token': 'test*test',
        },
    )
    assert response.status == 201, await response.text()
    expected: typing.Any = basic_data.copy()
    expected['description'] = 'here_will_be_cm_description'
    expected['description_title'] = 'here_will_be_cm_title'
    expected['subtitle'] = 'here_will_be_cm_subtitle'
    expected['title'] = 'title'
    expected['icon'] = 'here_will_be_cm_link'
    expected['begin_at'] = '1970-01-01T00:00:00+00:00'
    expected['is_enabled'] = True
    expected['kind'] = {'price': {'currency': 'RUB', 'decimal_value': '0'}}
    expected['loyalty_statuses'] = [
        {'loyalty': 'bronze', 'is_enabled': False},
        {'loyalty': 'gold', 'is_enabled': False},
        {'loyalty': 'platinum', 'is_enabled': False},
        {'loyalty': 'silver', 'is_enabled': False},
    ]
    response_basic = (await response.json())['basic_data']
    for time_field in ('begin_at', 'finish_at'):
        if time_field in expected:
            expected[time_field] = datetime.datetime.fromisoformat(
                expected[time_field],
            )
        if time_field in response_basic:
            response_basic[time_field] = datetime.datetime.fromisoformat(
                response_basic[time_field],
            )
    assert response_basic == expected
    assert (await response.json())['locations'] == [
        {
            'name': 'Russia, Moscow',
            'locations': [
                {
                    'id': '101',
                    'name': 'Big zombie shop',
                    'is_enabled': False,
                    'address': 'Москва, Лубянка, 5',
                    'map_link': (
                        'https://yandex.ru/maps/?mode=search&ol=biz&oid=101'
                    ),
                },
            ],
        },
        {
            'name': 'Russia',
            'locations': [
                {
                    'id': '102',
                    'name': 'Cataclyzm',
                    'is_enabled': True,
                    'address': 'Россия, Лубянка, 5',
                    'map_link': (
                        'https://yandex.ru/maps/?mode=search&ol=biz&oid=102'
                    ),
                },
            ],
        },
    ]


@pytest.mark.pgsql('partner_offers', files=['pg_init_partner.sql'])
async def test_create_idempotent(web_app_client):
    response1 = await web_app_client.post(
        '/internal/v1/deals/driver/',
        json={
            'partner_id': '1',
            'basic_data': TEST_BASIC_DATA,
            'locations_availability': [{'id': '102', 'is_enabled': False}],
        },
        headers={
            'X-Yandex-Login': 'hello',
            'X-Idempotency-Token': 'test*test',
        },
    )
    assert response1.status == 201, await response1.text()

    response2 = await web_app_client.post(
        '/internal/v1/deals/driver/',
        json={
            'partner_id': '2',
            'basic_data': TEST_BASIC_DATA,
            'locations_availability': [{'id': '102', 'is_enabled': True}],
        },
        headers={
            'X-Yandex-Login': 'hello',
            'X-Idempotency-Token': 'test*test',
        },
    )

    assert response2.status == 200, await response2.text()
    assert await response1.json() == await response2.json()

    fixed_data = {
        **TEST_BASIC_DATA,
        'loyalty_statuses': [
            {'loyalty': '1', 'is_enabled': False},
            {'loyalty': '2', 'is_enabled': False},
            {'loyalty': '3', 'is_enabled': True},
            {'loyalty': '4', 'is_enabled': False},
            {'loyalty': '5', 'is_enabled': False},
        ],
    }
    response3 = await web_app_client.post(
        '/internal/v1/deals/courier/',
        json={
            'partner_id': '1',
            'basic_data': fixed_data,
            'locations_availability': [{'id': '123456', 'is_enabled': False}],
        },
        headers={
            'X-Yandex-Login': 'hello',
            'X-Idempotency-Token': 'test*test',
        },
    )
    assert response3.status == 201, await response3.text()


async def test_not_found(web_app_client):
    response1 = await web_app_client.post(
        '/internal/v1/deals/unknown/',
        json={
            'partner_id': '1',
            'basic_data': TEST_BASIC_DATA,
            'locations_availability': [{'id': '102', 'is_enabled': False}],
        },
        headers={
            'X-Yandex-Login': 'hello',
            'X-Idempotency-Token': 'test*test',
        },
    )
    assert response1.status == 404, await response1.text()
