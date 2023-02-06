import datetime

import pytest

from tests_coupons import util

HEADERS = {'X-Yandex-Login': 'AdminLogin'}


@pytest.mark.parametrize(
    'target_promocode, service',
    [
        ('basicgrocery', 'grocery'),
        ('basiceats', 'eats'),
        ('basictaxi', 'taxi'),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0000')
@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_basic(
        taxi_coupons, mongodb, target_promocode, service, collections_tag,
):
    response = await taxi_coupons.post(
        '/admin/promocodes/revoke/',
        json={
            'promocode': target_promocode,
            'ticket': 'TICKET-0000',
            'service': service,
        },
        headers=HEADERS,
    )
    assert response.status_code == 200

    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)
    promocode = list(promocodes.find({'code': target_promocode}))[0]
    assert promocode['revoked']['created']
    assert promocode['revoked']['otrs_ticket'] == 'TICKET-0000'
    assert promocode['revoked']['operator_login'] == 'AdminLogin'
    assert promocode['updated_at']


@pytest.mark.parametrize(
    'promocode', ['[{unallowed code', 'unknown', 'noseries', 'noservice'],
)
async def test_malfunctioning_promocodes(taxi_coupons, promocode):
    response = await taxi_coupons.post(
        '/admin/promocodes/revoke/',
        json={
            'promocode': promocode,
            'ticket': 'TICKET-0000',
            'service': 'taxi',
        },
        headers=HEADERS,
    )
    assert response.status_code == 404


async def test_service_not_match(taxi_coupons):
    response = await taxi_coupons.post(
        '/admin/promocodes/revoke/',
        json={
            'promocode': 'basicgrocery',
            'ticket': 'TICKET-0000',
            'service': 'taxi',
        },
        headers=HEADERS,
    )
    assert response.status_code == 404


async def test_more_than_1_service(taxi_coupons):
    response = await taxi_coupons.post(
        '/admin/promocodes/revoke/',
        json={
            'promocode': 'morethanone',
            'ticket': 'TICKET-0000',
            'service': 'taxi',
        },
        headers=HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_already_revoked(taxi_coupons, mongodb, collections_tag):
    response = await taxi_coupons.post(
        '/admin/promocodes/revoke/',
        json={
            'promocode': 'wasrevoked',
            'ticket': 'TICKET-0000',
            'service': 'grocery',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)
    promocode = list(promocodes.find({'code': 'wasrevoked'}))[0]
    assert promocode['updated_at'] == 'not_changed'
    assert promocode['revoked']['created'] == datetime.datetime(
        2016, 10, 1, 10, 0,
    )
