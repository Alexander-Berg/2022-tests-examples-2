import uuid

import pytest

from . import common
from . import models


def _get_formatted_time(time):
    return time.isoformat().replace('00:00', '0000')


@pytest.mark.now(models.NOW)
async def test_by_user(taxi_grocery_support, pgsql, now):
    first_compensation_id = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14
    source = 'admin_compensation'

    numeric_value = '15'
    rounded_value = 15

    personal_phone_id = 'test_phone_id'

    user = common.create_default_customer(
        pgsql, now, personal_phone_id=personal_phone_id,
    )
    user.update_db()

    situation_first = common.create_situation_v2(
        pgsql, situation_maas_id, first_compensation_id,
    )
    situation_second = common.create_situation_v2(pgsql, situation_maas_id)

    compensation_info = {
        'generated_promo': 'test_promo',
        'compensation_value': rounded_value,
        'numeric_value': numeric_value,
        'status': 'success',
    }

    compensation_first = common.create_compensation_v2(
        pgsql,
        first_compensation_id,
        compensation_maas_id,
        user,
        situations=[situation_first.get_id()],
        main_situation_id=situation_first.maas_id,
        compensation_info=compensation_info,
        source=source,
        rate=rounded_value,
    )

    situation_first.update_db()
    situation_second.update_db()
    compensation_first.update_db()

    assert compensation_first.get_situations() == [situation_first.get_id()]
    assert (
        situation_first.get_bound_compensation() == compensation_first.get_id()
    )

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {
        'search_field': {'personal_phone_id': personal_phone_id},
        'locale': 'ru',
    }
    response = await taxi_grocery_support.post(
        '/v1/api/compensation/get-compensations',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        'given_compensations': [
            {
                'yandex_login': user.comments[0]['support_login'],
                'compensation': {
                    'type': 'promocode',
                    'description': 'Промокод на 15%',
                    'created': _get_formatted_time(compensation_first.created),
                    'status': compensation_info['status'],
                    'source': source,
                },
                'situations': [
                    {
                        'situation_id': situation_first.maas_id,
                        'comment': situation_first.comment,
                        'source': situation_first.source,
                        'has_photo': situation_first.has_photo,
                        'product_infos': situation_first.product_infos,
                        'situation_code': situation_first.situation_code,
                    },
                ],
                'main_situation_id': situation_first.maas_id,
                'order_id': 'order_id',
                'generated_promocode': 'test_promo',
            },
        ],
    }


@pytest.mark.now(models.NOW)
async def test_by_order(taxi_grocery_support, pgsql, now):
    first_compensation_id = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14
    source = 'admin_compensation'

    numeric_value = '15'
    rounded_value = 15

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation_first = common.create_situation_v2(
        pgsql, situation_maas_id, first_compensation_id,
    )
    situation_second = common.create_situation_v2(pgsql, situation_maas_id)

    compensation_info = {
        'generated_promo': 'test_promo',
        'compensation_value': rounded_value,
        'numeric_value': numeric_value,
        'status': 'success',
    }

    compensation_first = common.create_compensation_v2(
        pgsql,
        first_compensation_id,
        compensation_maas_id,
        user,
        situations=[situation_first.get_id()],
        main_situation_id=situation_first.maas_id,
        compensation_info=compensation_info,
        source=source,
        rate=rounded_value,
    )

    situation_first.update_db()
    situation_second.update_db()
    compensation_first.update_db()

    assert compensation_first.get_situations() == [situation_first.get_id()]
    assert (
        situation_first.get_bound_compensation() == compensation_first.get_id()
    )

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {
        'search_field': {'order_id': compensation_first.order_id},
        'locale': 'ru',
    }
    response = await taxi_grocery_support.post(
        '/v1/api/compensation/get-compensations',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        'given_compensations': [
            {
                'yandex_login': user.comments[0]['support_login'],
                'compensation': {
                    'type': 'promocode',
                    'description': 'Промокод на 15%',
                    'created': _get_formatted_time(compensation_first.created),
                    'status': compensation_info['status'],
                    'source': source,
                },
                'situations': [
                    {
                        'situation_id': situation_first.maas_id,
                        'comment': situation_first.comment,
                        'source': situation_first.source,
                        'has_photo': situation_first.has_photo,
                        'product_infos': situation_first.product_infos,
                        'situation_code': situation_first.situation_code,
                    },
                ],
                'main_situation_id': situation_first.maas_id,
                'order_id': 'order_id',
                'generated_promocode': 'test_promo',
            },
        ],
    }


async def test_get_not_existing(taxi_grocery_support):
    support_login = 'superSupport'
    personal_phone_id = 'p_phone_id'

    headers = {'X-Yandex-Login': support_login}
    request_json = {'search_field': {'personal_phone_id': personal_phone_id}}
    response = await taxi_grocery_support.post(
        '/v1/api/compensation/get-compensations',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {'given_compensations': []}
