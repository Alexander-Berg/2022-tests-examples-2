# -*- coding: utf-8 -*-
import pytest

from taxi.internal.order_kit import sms

# Just some test dummy data
test_logextra = {
    'extdict': {
        'order_id': '514ed981526e548b8ecc132b1419eda9',
        'loop_id': 'e94631bec6bd44219d887743eaa594fe',
    },
    '_link': 'db1d67984dba0aebd185463fa904369a'
}


@pytest.inline_callbacks
@pytest.mark.translations([
    (
            'notify',
            'sms.some',
            'ru',
            u'Водитель из парка %(park_name)s отказался от заказа на %(due)s'),
])
@pytest.mark.parametrize('text,expected_text,local_kwargs', [
    (
            u'Водитель из парка БЕЗ ПРОЦЕНТОВ 0% отказался от заказа на 22:50',
            u'Водитель из парка БЕЗ ПРОЦЕНТОВ 0% отказался от заказа на 22:50',
            {},
    ),
    (
            u'useless text, not used when sms_key is provided',
            {
                'key': 'sms.some',
                'keyset': 'notify',
                'params': {
                    'from_sms_other_key': u'',
                    'park_name': u'ТакСити 3%',
                    'due': u'123',
                    'order_id': '514ed981526e548b8ecc132b1419eda9'
                },
            },
            {
                'park_name': u'ТакСити 3%',
                'due': u'123',
                'localizable_text': {
                    'key': 'sms.some',
                    'keyset': 'notify',
                    'params': {
                        'from_sms_other_key': u'',
                        'park_name': u'ТакСити 3%',
                        'due': u'123',
                        'order_id': '514ed981526e548b8ecc132b1419eda9'
                        },
                    },
            },
    ),
])
def test_sms_localizable_text(mock, text, expected_text, patch, local_kwargs):
    """Check that sms is properly formatted, including proper special symbols handling
    """

    # No 'nolocal' in py2, so ...
    sms_sent = {'sent': False}

    @patch('taxi.external.communications.send_user_sms')
    def send_sms_patched(
            text, intent, tvm_src_service_name, phone=None, phone_id=None,
            notification=None, user_id=None, locale=None,
            meta=None, log_extra=None):
        assert text == expected_text
        sms_sent['sent'] = True

    @patch('taxi.internal.order_kit.sms._get_params_for_sms')
    def _get_params_for_sms(fields_dict):
        SMS_OTHER_KEYS = ['from_sms_other_key', 'park_name']
        sms_fields = {}
        sms_fields.update(fields_dict)
        for k in SMS_OTHER_KEYS:
            sms_fields[k] = sms_fields.get(k, u'')
        return sms_fields

    yield sms.communications_send(
        '+71112223344',
        None,
        None,
        log_extra=test_logextra,
        order_id='514ed981526e548b8ecc132b1419eda9',
        locale='ru',
        route='',
        from_uid='',
        application="callcenter",
        message_key="on_waiting",
        text=text,
        **local_kwargs
    )
    assert sms_sent['sent']


@pytest.inline_callbacks
@pytest.mark.config(PASSPORT_SMS_DEFAULT_ROUTE='taxi')
@pytest.mark.parametrize('intent,message_key,route,override_route,excepted_intent,excepted_meta', [
    ('intent', 'key', 'route', True, 'intent_route',
     {'application': 'application', 'message_key': 'key', 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
    ('', 'key', 'route', True, 'taxi_order_route',
     {'application': 'application', 'message_key': 'key', 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
    (None, 'key', 'route', True, 'taxi_order_route',
     {'application': 'application', 'message_key': 'key', 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
    (None, 'key', None, False, 'taxi_order_taxi',
     {'application': 'application', 'message_key': 'key', 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
    (None, 'key', '', True, 'taxi_order_taxi',
     {'application': 'application', 'message_key': 'key', 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
    (None, 'key', None, True, 'taxi_order_overrided',
     {'application': 'application', 'message_key': 'key', 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
    (None, '', 'route', True, 'taxi_order_route',
     {'application': 'application', 'message_key': '', 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
    (None, None, 'route', True, 'taxi_order_route',
     {'application': 'application', 'message_key': None, 'order_id': '514ed981526e548b8ecc132b1419eda9'}),
])
def test_sms_intents_communications(
        mock, patch, intent, message_key, route, override_route, excepted_intent, excepted_meta
):
    """Check that sms is properly formatted, including proper special symbols handling
    """

    # No 'nolocal' in py2, so ...
    sms_sent = {'sent': False}

    @patch('taxi.external.communications.send_user_sms')
    def send_sms_patched(
            text, intent, tvm_src_service_name, phone=None, phone_id=None,
            notification=None, user_id=None, locale=None,
            meta=None, log_extra=None):
        assert intent == excepted_intent
        assert meta == excepted_meta
        sms_sent['sent'] = True

    @patch('taxi.internal.order_kit.sms._override_route_if_needed')
    def _override_route_if_needed(route, *args, **kwargs):
        if route is None and override_route:
            return 'overrided'
        else:
            return route

    yield sms.communications_send(
        '+71112223344',
        None,
        None,
        log_extra=test_logextra,
        order_id='514ed981526e548b8ecc132b1419eda9',
        locale='ru',
        route=route,
        from_uid='',
        application="application",
        message_key=message_key,
        intent=intent,
        text=None
    )
    assert sms_sent['sent']


@pytest.inline_callbacks
@pytest.mark.translations([
    (
            'notify',
            'sms.some',
            'ru',
            u'Водитель из парка %(park_name)s отказался от заказа на %(due)s'),
])
@pytest.mark.parametrize('text,expected_text,local_kwargs,sms_key', [
    (
            u'Водитель из парка БЕЗ ПРОЦЕНТОВ 0% отказался от заказа на 22:50',
            u'Водитель из парка БЕЗ ПРОЦЕНТОВ 0% отказался от заказа на 22:50',
            {},
            None,
    ),
    (
            u'useless text, not used when sms_key is provided',
            {
                'key': 'sms.some',
                'keyset': 'notify',
                'params': {
                    'from_sms_other_key': u'',
                    'park_name': u'ТакСити 3%',
                    'due': u'123',
                    'order_id': '514ed981526e548b8ecc132b1419eda9'
                },
            },
            {
                'park_name': u'ТакСити 3%',
                'due': u'123'
            },
            "some",
    ),
])
def test_sms_key(mock, text, expected_text, patch, local_kwargs, sms_key):
    """Check that sms is properly formatted, including proper special symbols handling
    """

    # No 'nolocal' in py2, so ...
    sms_sent = {'sent': False}

    @patch('taxi.external.communications.send_user_sms')
    def send_sms_patched(
            text, intent, tvm_src_service_name, phone=None, phone_id=None,
            notification=None, user_id=None, locale=None,
            meta=None, log_extra=None):
        assert text == expected_text
        sms_sent['sent'] = True

    @patch('taxi.internal.order_kit.sms._get_params_for_sms')
    def _get_params_for_sms(fields_dict):
        SMS_OTHER_KEYS = ['from_sms_other_key', 'park_name']
        sms_fields = {}
        sms_fields.update(fields_dict)
        for k in SMS_OTHER_KEYS:
            sms_fields[k] = sms_fields.get(k, u'')
        return sms_fields

    yield sms.communications_send(
        '+71112223344',
        sms_key,
        None,
        log_extra=test_logextra,
        order_id='514ed981526e548b8ecc132b1419eda9',
        locale='ru',
        route='',
        from_uid='',
        application="callcenter",
        message_key="on_waiting",
        text=text,
        **local_kwargs
    )
    assert sms_sent['sent']
