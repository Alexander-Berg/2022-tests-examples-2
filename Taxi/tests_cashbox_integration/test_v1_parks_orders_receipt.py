# -*- coding: utf-8 -*-
import pytest

from tests_cashbox_integration import utils

ENDPOINT = 'v1/parks/orders/receipt'
PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Чек</title>
  </head>
  <body>
    <h1>{}</h1>
  </body>
</html>
"""


BAD_REQUEST_PARAMS = [
    ({}),
    ({'receipt_id': 'a'}),
    ({'sing': 'b'}),
    ({'receipt_id': 'spider-zakaz_1', 'sign': 'trash'}),
]


@pytest.mark.parametrize('params', BAD_REQUEST_PARAMS)
async def test_bad_request(taxi_cashbox_integration, params):
    response = await taxi_cashbox_integration.get(ENDPOINT, params=params)

    assert response.status_code == 400, response.text
    assert response.text == PAGE_HTML.format('Чек не найден')


NOT_FOUND_PARAMS = [
    (utils.make_receipt_params('xxx', 'yyy')),
    (utils.make_receipt_params('xxx', 'zakaz_1')),
    (utils.make_receipt_params('spider', 'yyy')),
]


@pytest.mark.parametrize('params', NOT_FOUND_PARAMS)
async def test_not_found(taxi_cashbox_integration, params):
    response = await taxi_cashbox_integration.get(ENDPOINT, params=params)

    assert response.status_code == 404, response.text
    assert response.text == PAGE_HTML.format('Чек не найден')


OK_PARAMS = [
    ('zakaz_1', 'Чек формируется'),
    ('zakaz_22', 'Чек формируется'),
    ('zakaz_333', 'Чек формируется'),
    ('zakaz_4444', '<a href="https://cashier.com/receipt?id=124">Чек</a>'),
    ('zakaz_666666', 'Не удалось сформировать чек'),
]


@pytest.mark.parametrize('order_id,content', OK_PARAMS)
async def test_ok(taxi_cashbox_integration, order_id, content):
    response = await taxi_cashbox_integration.get(
        ENDPOINT, params=utils.make_receipt_params('spider', order_id),
    )

    assert response.status_code == 200, response.text
    assert response.text == PAGE_HTML.format(content)


async def test_internal_error(taxi_cashbox_integration):
    response = await taxi_cashbox_integration.get(
        ENDPOINT, params=utils.make_receipt_params('spider', 'zakaz_55555'),
    )

    assert response.status_code == 500, response.text
    assert response.text == PAGE_HTML.format('Не удалось сформировать чек')


async def test_empty_substitutions_config(taxi_cashbox_integration):
    response = await taxi_cashbox_integration.get(
        ENDPOINT, params=utils.make_receipt_params('spider', 'zakaz_777'),
    )

    assert response.status_code == 500
    assert response.text == ''
