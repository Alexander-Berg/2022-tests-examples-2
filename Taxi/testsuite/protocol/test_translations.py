import json

import pytest


def test_translations_cancel_state(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/translations', {'keyset': 'cancel_state'},
    )
    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {
        'cancel_state.cash.paid.message',
        'cancel_state.free.message',
        'cancel_state.free.message_support',
        'cancel_state.free.title',
        'cancel_state.paid.message',
        'cancel_state.paid.message_support',
        'cancel_state.paid.title',
    }


def test_translations_order_chain(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/translations', {'keyset': 'order_chain'},
    )
    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {
        'order_chain.parent_destination',
        'order_chain.driver_info',
    }


def test_translations_itaxi_messages(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/translations', {'keyset': 'itaxi_messages'},
    )
    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {
        'Only for order to airport',
        (
            'Select airport and then you will be able choose date and time of '
            'order'
        ),
        (
            'We will start searching a car one hour before the selected time '
            'and then send you a notification'
        ),
    }


def test_translations_surge_reduced_lookandfeel(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/translations', {'keyset': 'surge_reduced_lookandfeel'},
    )
    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {
        'surge_reduced_lookandfeel.alert',
        'surge_reduced_lookandfeel.card_title',
        'surge_reduced_lookandfeel.card_body',
        'surge_reduced_lookandfeel.card_ok',
    }


@pytest.mark.config(
    LOCALES_SUPPORTED=['ru', 'en', 'hy', 'ka', 'kk', 'uk', 'az', 'rr'],
)
def test_unknown_language(taxi_protocol):
    headers = {'Accept-Language': 'rr'}
    body = json.dumps({'keyset': 'itaxi_messages'})
    response = taxi_protocol.post(
        '3.0/translations', headers=headers, data=body,
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        'Only for order to airport',
        (
            'Select airport and then you will be able choose date and time of '
            'order'
        ),
        (
            'We will start searching a car one hour before the selected time '
            'and then send you a notification'
        ),
    }
    assert data['Only for order to airport'] == 'Только для поездок в аэропорт'

    assert data[
        'Select airport and then you will be '
        'able choose date and time of order'
    ] == ('Выберите аэропорт, ' 'а после — дату и ' 'время поездки')

    assert (
        data[
            'We will start searching a car one hour '
            'before the selected time and then send '
            'you a notification'
        ]
        == (
            'Поиск начнётся за час до выезда '
            'и вы получите уведомление, '
            'когда такси найдётся'
        )
    )
