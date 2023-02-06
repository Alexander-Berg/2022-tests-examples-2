# pylint: disable-all
import datetime

import pytest

from . import experiments
from . import utils


def get_body():
    return {
        'coupon_id': 'ID13',
        'series_id': 'series_id_1',
        'series_meta': {'eats_order_cnt_to': 1},
        'payload': {'order_id': 'ID13'},
        'source_handler': 'check',
    }


def get_headers(eater_id='1', personal_phone_id='2'):
    return {
        'X-YaTaxi-Session': 'taxi:1234',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-Yandex-Uid': '555',
        'X-YaTaxi-PhoneId': 'PHONE_ID',
        'X-Eats-User': (
            'user_id=' + eater_id + ',personal_phone_id=' + personal_phone_id
        ),
        'X-Device-Id': 'new_device',
    }


def check_failure_reason(response_json, reason_code, reason_descr):
    return response_json == utils.create_response(
        False, True, reason_code, reason_descr,
    )


def to_datetime(string):
    return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z')


@pytest.mark.parametrize(
    'antifraud_enable',
    [
        pytest.param(
            True,
            marks=experiments.eats_coupons_new_user_antifraud(),
            id='antifraud_enable',
        ),
        pytest.param(False, id='antifraud_disable'),
    ],
)
@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.parametrize('card_id', [False, True])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_user_antifraud(
        taxi_eats_coupons,
        eats_coupons_cursor,
        card_id,
        mock_order_stats,
        antifraud_enable,
):
    mock_order_stats.orders_cnt = [utils.StatsCounter(3)]
    mock_order_stats.exp_identities_cnt = (
        int(card_id) + 3
    )  # 3 - device and phone and eater

    headers = get_headers()
    body = get_body()

    if card_id:
        body['payload']['card_id'] = 'card_id'

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json=body, headers=headers,
    )
    assert check_failure_reason(
        response.json(), 'FIRST_ORDER_FAILURE', 'У вас не первый заказ',
    )

    headers['X-Eats-User'] = 'user_id=1,personal_phone_id=3'
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json=body, headers=headers,
    )
    assert check_failure_reason(
        response.json(), 'FIRST_ORDER_FAILURE', 'У вас не первый заказ',
    )

    headers['X-Eats-User'] = 'user_id=1,personal_phone_id=4'
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json=body, headers=headers,
    )

    assert check_failure_reason(
        response.json(),
        'EATS_ANTIFRAUD_USER_BANNED'
        if antifraud_enable
        else 'FIRST_ORDER_FAILURE',
        'У вас не первый заказ',
    )

    headers['X-Eats-User'] = 'user_id=1,personal_phone_id=5'
    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json=body, headers=headers,
    )
    assert response.status_code == 200
    assert check_failure_reason(
        response.json(),
        'EATS_ANTIFRAUD_USER_BANNED'
        if antifraud_enable
        else 'FIRST_ORDER_FAILURE',
        'У вас не первый заказ',
    )

    eats_coupons_cursor.execute(
        'SELECT banned_until FROM eats_coupons.new_user_blacklist',
    )
    blacklist = eats_coupons_cursor.fetchall()
    if antifraud_enable:
        assert len(blacklist) == (5 if card_id else 4)
        assert blacklist[0][0] == to_datetime('2022-07-03T00:00:00+0000')
    else:
        assert not blacklist

    assert mock_order_stats.order_stats_client.times_called == 4


@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.pgsql('eats_coupons', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'antifraud_enable',
    [
        pytest.param(
            True,
            marks=experiments.eats_coupons_new_user_antifraud(),
            id='antifraud_enable',
        ),
        pytest.param(False, id='antifraud_disable'),
    ],
)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_new_user_antifraud_ban_forever(
        taxi_eats_coupons,
        mock_order_stats,
        eats_coupons_cursor,
        antifraud_enable,
):
    mock_order_stats.orders_cnt = [utils.StatsCounter(3)]

    headers = get_headers()
    body = get_body()

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json=body, headers=headers,
    )
    assert response.status_code == 200

    # get blacklist for current eater_id=1
    eats_coupons_cursor.execute(
        'SELECT * FROM eats_coupons.new_user_blacklist '
        'WHERE id_type = \'eater_id\' AND id_value = \'1\'',
        'ORDER BY banned_until DESC NULLS FIRST ',
    )
    blacklist = eats_coupons_cursor.fetchall()
    if antifraud_enable:
        assert not blacklist[0]['banned_until']
        assert check_failure_reason(
            response.json(),
            'EATS_ANTIFRAUD_USER_BANNED',
            'У вас не первый заказ',
        )
    else:
        assert blacklist[0]['banned_until']  # do not ban user forever
        assert check_failure_reason(
            response.json(), 'FIRST_ORDER_FAILURE', 'У вас не первый заказ',
        )


@experiments.eats_coupons_new_user_antifraud()
@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.pgsql('eats_coupons', files=['insert_values.sql'])
async def test_new_user_antifraud_expired_ban(
        taxi_eats_coupons, mock_order_stats,
):
    mock_order_stats.orders_cnt = [utils.StatsCounter(0)]

    headers = get_headers(eater_id='3', personal_phone_id='6')
    body = get_body()

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate', json=body, headers=headers,
    )
    assert response.status_code == 200

    response = response.json()
    assert response == utils.create_response(True, True)
