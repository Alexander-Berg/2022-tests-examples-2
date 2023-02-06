# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest


async def test_get_usual(taxi_eats_orders_tracking):
    response = await taxi_eats_orders_tracking.get(
        '/admin/translate?keyset_id=id_1', json=None,
    )
    assert response.status_code == 200

    text = response.json()['text']

    assert text == 'любой текст'


async def test_get_plural(taxi_eats_orders_tracking):
    response = await taxi_eats_orders_tracking.get(
        '/admin/translate?keyset_id=id_2&count=2', json=None,
    )
    assert response.status_code == 200

    text = response.json()['text']

    assert text == '2 минуты'

    response = await taxi_eats_orders_tracking.get(
        '/admin/translate?keyset_id=id_2&count=1', json=None,
    )
    assert response.status_code == 200

    text = response.json()['text']

    assert text == '1 минута'

    response = await taxi_eats_orders_tracking.get(
        '/admin/translate?keyset_id=id_2&count=10', json=None,
    )
    assert response.status_code == 200

    text = response.json()['text']

    assert text == '10 минут'

    response = await taxi_eats_orders_tracking.get(
        '/admin/translate?keyset_id=id_2&count=4', json=None,
    )
    assert response.status_code == 200

    text = response.json()['text']

    assert text == '2 минуты'

    response = await taxi_eats_orders_tracking.get(
        '/admin/translate?keyset_id=id_2&count=3', json=None,
    )
    assert response.status_code == 200

    text = response.json()['text']

    assert text == '2 минуты'


async def test_keyset_not_found(taxi_eats_orders_tracking):
    response = await taxi_eats_orders_tracking.get(
        '/admin/translate?keyset_id=404_not_found', json=None,
    )
    assert response.status_code == 404
