import uuid

import pytest

from . import common
from . import models


@pytest.mark.now(models.NOW)
async def test_remove_200(taxi_grocery_support, pgsql, now):
    situation_maas_id = 12
    situation_maas_id_2 = 13

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation = common.create_situation(pgsql, situation_maas_id)
    situation_2 = common.create_situation(pgsql, situation_maas_id_2)

    situation.update_db()
    situation_2.update_db()

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}

    request_json = {
        'order_id': situation.order_id,
        'situation_id': situation_maas_id,
    }

    response = await taxi_grocery_support.post(
        '/v2/api/compensation/delete-situation',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.now(models.NOW)
async def test_remove_400(taxi_grocery_support, pgsql, now):
    compensation_id = str(uuid.uuid4())
    situation_maas_id = 12

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation = common.create_situation(
        pgsql, situation_maas_id, compensation_id,
    )
    situation.update_db()

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}

    request_json = {
        'order_id': situation.order_id,
        'situation_id': situation_maas_id,
    }

    response = await taxi_grocery_support.post(
        '/v2/api/compensation/delete-situation',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.now(models.NOW)
async def test_remove_404(taxi_grocery_support, pgsql, now):
    order_id = 'fake-id'
    situation_maas_id = 12

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}

    request_json = {'order_id': order_id, 'situation_id': situation_maas_id}

    response = await taxi_grocery_support.post(
        '/v2/api/compensation/delete-situation',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.now(models.NOW)
async def test_remove_unsubmitted(taxi_grocery_support, pgsql, now):
    first_compensation_id = str(uuid.uuid4())
    second_compensation_id = str(uuid.uuid4())
    situation_maas_id = 12

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation = common.create_situation(pgsql, situation_maas_id)
    situation_2 = common.create_situation(
        pgsql, situation_maas_id, first_compensation_id,
    )
    situation_3 = common.create_situation(
        pgsql, situation_maas_id, second_compensation_id,
    )

    situation.update_db()
    situation_2.update_db()
    situation_3.update_db()

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}

    request_json = {
        'order_id': situation.order_id,
        'situation_id': situation_maas_id,
    }

    response = await taxi_grocery_support.post(
        '/v2/api/compensation/delete-situation',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200

    situation_2.compare_with_db()
    situation_3.compare_with_db()
