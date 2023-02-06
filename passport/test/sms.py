# -*- coding: utf-8 -*-

import re

from nose.tools import ok_


def assert_confirmation_code_sent(yasms_builder_faker, language, phone_number, identity,
                                  uid, code=None):
    LANG_TO_TEXT = {
        'en': u'^Your confirmation code is {{code}}\. Please enter it in the text field\.$',
        'ru': u'^Ваш код подтверждения: {{code}}\. Наберите его в поле ввода\.$',
    }
    expected_text = LANG_TO_TEXT[language]
    if code is None:
        expected_params = None
    else:
        expected_params = u'{"code": "%s"}' % code

    _assert_message_sent(yasms_builder_faker, phone_number, identity, uid, expected_text, expected_params)


def assert_user_notified_about_secure_phone_replacement_started(yasms_builder_faker,
                                                                language, phone_number,
                                                                uid):
    LANG_TO_TEXT = {
        'ru': u'^Начата замена телефона на Яндексе: https://ya\.cc/sms-help-ru$',
        'en': u'^Phone number has been recently replaced on Yandex: https://ya.cc/sms-help-com$',
    }
    expected_text = LANG_TO_TEXT[language]

    _assert_message_sent(
        yasms_builder_faker,
        phone_number,
        'notify_user_by_sms_that_secure_phone_replacement_started.notify',
        uid,
        expected_text,
    )


def assert_user_notified_about_secure_phone_removal_started(yasms_builder_faker,
                                                            language, phone_number,
                                                            uid):
    LANG_TO_TEXT = {
        'ru': u'^Начато удаление телефона на Яндексе: https://ya\.cc/sms-help-ru$',
        'en': u'^Phone number has been recently deleted on Yandex: https://ya.cc/sms-help-com$',
    }
    expected_text = LANG_TO_TEXT[language]

    _assert_message_sent(
        yasms_builder_faker,
        phone_number,
        'notify_user_by_sms_that_secure_phone_removal_started.notify',
        uid,
        expected_text,
    )


def _assert_message_sent(yasms_faker, phone_number, identity, uid, expected_regexp, expected_template_params=None):
    requests = yasms_faker.get_requests_by_method('send_sms')
    ok_(requests, 'not found')

    for request in requests:
        args = request.get_query_params()
        is_phone_number_ok = args['phone'][0] == phone_number.e164
        is_text_ok = re.match(expected_regexp, args['text'][0])
        if expected_template_params:
            is_params_ok = re.match(expected_template_params, args['text_template_params'][0])
        else:
            is_params_ok = True
        if is_phone_number_ok and is_text_ok and is_params_ok:
            break
    else:
        assert False, '%r and %r not found' % (expected_regexp, phone_number.e164)  # pragma: no cover

    request.assert_query_contains({
        'phone': phone_number.e164,
        'identity': identity,
        'from_uid': str(uid),
    })
