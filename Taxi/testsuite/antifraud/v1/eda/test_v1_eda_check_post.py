import json

import pytest

from antifraud.v1.eda import eda_common

_REQUEST_PAYMENT = {
    'order_nr': 'order_nr',
    'request_uuid': 'request_uuid',
    'payment_method_id': 'payment_method_id',
    'app_metrica_device_id': 'app_metrica_device_id',
    'account_type': 'corporate',
}


@pytest.fixture
def mock_personal_phones_find(mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def mock_personal_phones_find(request):
        request_json = json.loads(request.get_data())
        phones_map = {'+79161234567': 'f3b46027b6af44ca8c998a111c94e296'}
        original_id = request_json['value']
        if original_id in phones_map:
            return {'id': phones_map[original_id], 'value': original_id}

        return mockserver.make_response({}, 404)


def test_check_base(taxi_antifraud, testpoint):
    eda_common.check_base(
        taxi_antifraud,
        testpoint,
        'v1/eda/check_post',
        _REQUEST_PAYMENT,
        eda_common.NOT_FRAUDER_RESPONSE,
    )


@pytest.mark.filldb(
    antifraud_rules='check_rule_args', antifraud_eda_check_requests='saved',
)
@pytest.mark.config(AFS_EDA_LOAD_REQUEST=True)
def test_check_fraud(taxi_antifraud, testpoint, db, now):
    db.antifraud_rules.update({}, {'$set': {'type_id': 9}}, multi=True)

    taxi_antifraud.tests_control(now, invalidate_caches=True)

    eda_common.check_fraud(
        taxi_antifraud,
        testpoint,
        'v1/eda/check_post',
        _REQUEST_PAYMENT,
        eda_common.FRAUDER_RESPONSE,
    )


@pytest.mark.filldb(antifraud_eda_check_requests='saved')
@pytest.mark.config(AFS_EDA_LOAD_REQUEST=True)
def test_check_pass_and_replace(taxi_antifraud, testpoint):
    eda_common.check_fraud(
        taxi_antifraud,
        testpoint,
        'v1/eda/check_post',
        {
            **_REQUEST_PAYMENT,
            **{
                'request_uuid': 'new_request_uuid',
                'app_metrica_device_id': 'new_app_metrica_device_id',
            },
        },
        eda_common.FRAUDER_RESPONSE,
        ['fraud_rule1', 'fraud_rule2'],
    )


_NOTIFY_CFG = {
    'direct': {
        'enabled': True,
        'bot_token': 'bot_token',
        'chat_id': 'direct_chat_id',
    },
    'inner': {
        'enabled': True,
        'chat_id': 'inner_chat_id',
        'bot_id': 'eats',
        'async': False,
    },
}


@pytest.mark.parametrize(
    'order_nr,decision,disabled_missing_base,disabled_is_suspect',
    [
        ('not_fraud_order_nr', 'not_frauder', True, False),
        ('fraud_order_nr', 'frauder', True, False),
        ('order_nr', 'not_frauder', False, True),
    ],
)
@pytest.mark.filldb(antifraud_eda_check_requests='saved')
@pytest.mark.config(
    AFS_EDA_ORDER_NOTIFY=_NOTIFY_CFG, AFS_EDA_LOAD_REQUEST=True,
)
def test_check_base_notify(
        taxi_antifraud,
        testpoint,
        order_nr,
        disabled_missing_base,
        disabled_is_suspect,
        decision,
):
    @testpoint('notify_send_disabled_missing_base')
    def notify_send_disabled_missing_base(_):
        pass

    @testpoint('notify_send_disabled_is_suspect')
    def notify_send_disabled_is_suspect(_):
        pass

    eda_common.check_new_schema(
        taxi_antifraud,
        testpoint,
        {**_REQUEST_PAYMENT, **{'order_nr': order_nr}},
        {'decision': decision},
        path='v1/eda/check_post',
    )

    if disabled_missing_base:
        assert notify_send_disabled_missing_base.wait_call()
    if disabled_is_suspect:
        assert notify_send_disabled_is_suspect.wait_call()


def _check_base_notify_suspect(
        taxi_antifraud, testpoint, mockserver, req, is_async,
):
    order_nr_head = 'https://admin.eda.yandex-team.ru/orders/{}/edit\n'

    msg = order_nr_head.format(req['order_nr']) + '\n'.join(
        [
            'order_amount: 100.500',
            'order_currency: RUB',
            'service_name: grocery',
            'passport_uid: passport_uid',
            'short_address: short_address',
            'address_comment: address_comment',
        ],
    )

    @mockserver.json_handler('/afs_tg_direct', prefix=True)
    def afs_tg_direct(request):
        assert request.path == '/afs_tg_direct/bot_token/sendMessage'
        assert request.json == {
            'chat_id': _NOTIFY_CFG['direct']['chat_id'],
            'text': msg,
        }
        # return {}

    @mockserver.json_handler('/afs_tg_base/v1/send_telegram_message')
    def afs_tg_inner(request):
        assert request.json == {
            'chat_id': _NOTIFY_CFG['inner']['chat_id'],
            'bot_id': 'eats',
            'text': msg,
        }
        # return {}

    @testpoint('notify_send_msg')
    def notify_send_msg(data):
        assert data['msg'] == msg

    @testpoint('notify_process_direct_async')
    def notify_process_direct_async(_):
        pass

    eda_common.check_new_schema(
        taxi_antifraud,
        testpoint,
        req,
        {'decision': 'suspect'},
        path='v1/eda/check_post',
    )

    assert notify_send_msg.has_calls
    if is_async:
        assert notify_process_direct_async.wait_call()
    assert afs_tg_direct.wait_call()
    assert afs_tg_inner.wait_call()


@pytest.mark.filldb(antifraud_eda_check_requests='saved')
@pytest.mark.config(
    AFS_EDA_ORDER_NOTIFY=_NOTIFY_CFG, AFS_EDA_LOAD_REQUEST=True,
)
def test_check_base_notify_suspect(taxi_antifraud, testpoint, mockserver):
    _check_base_notify_suspect(
        taxi_antifraud, testpoint, mockserver, _REQUEST_PAYMENT, False,
    )


_NOTIFY_ASYNC_CFG = {
    'direct': {
        'enabled': True,
        'bot_token': 'bot_token',
        'chat_id': 'direct_chat_id',
        'async': True,
    },
    'inner': {
        'enabled': True,
        'chat_id': 'inner_chat_id',
        'async': True,
        'bot_id': 'eats',
    },
}


@pytest.mark.filldb(antifraud_eda_check_requests='saved')
@pytest.mark.config(
    AFS_EDA_ORDER_NOTIFY=_NOTIFY_ASYNC_CFG, AFS_EDA_LOAD_REQUEST=True,
)
def test_check_base_notify_suspect_async(
        taxi_antifraud, testpoint, mockserver,
):
    _check_base_notify_suspect(
        taxi_antifraud, testpoint, mockserver, _REQUEST_PAYMENT, True,
    )


@pytest.mark.filldb(antifraud_eda_check_requests='saved')
@pytest.mark.config(AFS_EDA_TELESIGN_ENABLED=True, AFS_EDA_LOAD_REQUEST=True)
def test_check_telesign(
        taxi_antifraud, testpoint, mockserver, mock_personal_phones_find,
):
    eda_common.check_fraud(
        taxi_antifraud,
        testpoint,
        'v1/eda/check_post',
        _REQUEST_PAYMENT,
        eda_common.FRAUDER_RESPONSE,
        ['test_rule_telesign'],
    )
