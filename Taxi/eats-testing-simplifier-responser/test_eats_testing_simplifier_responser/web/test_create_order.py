# pylint: disable=import-only-modules
import logging

from freezegun.api import FakeDatetime
import pytest


@pytest.mark.parametrize('path', ['/v1/orders/create', '/v2/orders/create'])
async def test_create_order_invalid_parameters(
        taxi_eats_testing_simplifier_responser_web, path,
):
    response = await taxi_eats_testing_simplifier_responser_web.post(
        path=path,
        json={
            'id': '1',
            'payment_method': 'test',
            'currency': 'RUB',
            'items': [],
            'mcc': 'test',
            'revision': '1',
        },
        headers={
            'Accept-Language': 'test',
            'X-AppMetrica-DeviceId': 'test',
            'User-Agent': 'test',
            'X-Platform': 'test',
            'X-App-Version': 'test',
            'X-Eats-Testing-Mock-Bypass': 'not_enough_funds',
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {
            'reason': (
                'Invalid value to deserialize ClientPaymentMethod: '
                '\'test\' is not instance of dict'
            ),
        },
    }


@pytest.mark.parametrize('path', ['/v1/orders/create', '/v2/orders/create'])
@pytest.mark.parametrize(
    'header_json,exp_task',
    [
        (
            '{"first_payment": "processing_error"}',
            {
                'queue': 'eda_order_processing_payment_events_callback',
                'id': '211228-158589_1',
                'args': [],
                'kwargs': {
                    'action': 'debt',
                    'status': 'confirmed',
                    'revision': '1',
                    'order_id': '211228-158589',
                    'meta': [{'discriminator': 'debt_type', 'value': 'auto'}],
                },
                'eta': FakeDatetime(1970, 1, 1, 0, 0),
            },
        ),
        (
            '{"first_payment": "not_enough_funds"}',
            {
                'queue': 'eda_order_processing_payment_events_callback',
                'id': '211228-158589_1',
                'args': [],
                'kwargs': {
                    'action': 'purchase',
                    'status': 'rejected',
                    'revision': '1',
                    'order_id': '211228-158589',
                },
                'eta': FakeDatetime(1970, 1, 1, 0, 0),
            },
        ),
        (
            '{"first_payment": "success"}',
            {
                'queue': 'eda_order_processing_payment_events_callback',
                'id': '211228-158589_1',
                'args': [],
                'kwargs': {
                    'action': 'purchase',
                    'status': 'confirmed',
                    'revision': '1',
                    'order_id': '211228-158589',
                },
                'eta': FakeDatetime(1970, 1, 1, 0, 0),
            },
        ),
    ],
)
async def test_create_order_ok(
        taxi_eats_testing_simplifier_responser_web,
        stq,
        header_json,
        exp_task,
        path,
):
    with stq.flushing():
        response = await taxi_eats_testing_simplifier_responser_web.post(
            path=path,
            json={
                'id': '211228-158589',
                'payment_method': {'type': 'card'},
                'currency': 'RUB',
                'items': [],
                'mcc': 55,
                'revision': '1',
            },
            headers={
                'Accept-Language': 'test',
                'X-AppMetrica-DeviceId': 'test',
                'User-Agent': 'test',
                'X-Platform': 'test',
                'X-App-Version': 'test',
                'X-Eats-Testing-Mock-Bypass': header_json,
            },
        )
        assert response.status == 200, response.text
        content = await response.json()
        assert content == {}

        task = stq.eda_order_processing_payment_events_callback.next_call()
        assert task == exp_task

        assert stq.is_empty


@pytest.mark.parametrize('path', ['/v1/orders/create', '/v2/orders/create'])
@pytest.mark.parametrize(
    'exp_task',
    [
        (
            {
                'queue': 'eda_order_processing_payment_events_callback',
                'id': '211228-158589_1',
                'args': [],
                'kwargs': {
                    'action': 'purchase',
                    'status': 'confirmed',
                    'revision': '1',
                    'order_id': '211228-158589',
                },
                'eta': FakeDatetime(1970, 1, 1, 0, 0),
            }
        ),
    ],
)
async def test_create_order_without_header(
        taxi_eats_testing_simplifier_responser_web, stq, exp_task, path,
):
    with stq.flushing():
        response = await taxi_eats_testing_simplifier_responser_web.post(
            path=path,
            json={
                'id': '211228-158589',
                'payment_method': {'type': 'card'},
                'currency': 'RUB',
                'items': [],
                'mcc': 55,
                'revision': '1',
            },
            headers={
                'Accept-Language': 'test',
                'X-AppMetrica-DeviceId': 'test',
                'User-Agent': 'test',
                'X-Platform': 'test',
                'X-App-Version': 'test',
            },
        )
        assert response.status == 200, response.text
        content = await response.json()
        assert content == {}

        task = stq.eda_order_processing_payment_events_callback.next_call()
        logging.critical(task)
        logging.critical(exp_task)
        assert task == exp_task

        assert stq.is_empty
