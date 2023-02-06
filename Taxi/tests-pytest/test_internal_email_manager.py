# -*- coding: utf-8 -*-

import pytest

from taxi.core import async
from taxi.core import translations
from taxi.external import experiments3 as exp3
from taxi.internal import email_manager

YATAXI_APP_NAME = 'android'


@pytest.mark.filldb(users='get')
@pytest.mark.parametrize(
    'user_id, exc, email, phone_id, email_info',
    [
        # Non-existent user
        (
            'user_3', email_manager.NotFoundError, None,
            'user_phone_3', None,
        ),
        # Unconfirmed email
        (
            'user_2', email_manager.ConfirmationError, 'another@mail.ru',
            'user_phone_2',
            {
                'id': 'user_phone_2',
                'phone_id': 'user_phone_2',
                'personal_email_id': 'personal_another@mail.ru',
                'confirmed': False,
                'confirmation_code': '5678',
            },
        ),
        # Happy path
        (
            'user_1', None, 'sample@mail.ru',
            'user_phone_1',
            {
                'id': 'user_phone_1',
                'phone_id': 'user_phone_1',
                'personal_email_id': 'personal_sample@mail.ru',
                'confirmed': True,
                'confirmation_code': '1234',
            },
        ),
    ],
)
@pytest.inline_callbacks
def test_get_email(patch, user_id, exc, email, phone_id, email_info):
    @patch('taxi.external.userapi.get_user_emails')
    @async.inline_callbacks
    def mock_userapi(
            brand,
            email_ids=None,
            phone_ids=None,
            yandex_uids=None,
            fields=None,
            primary_replica=False,
            log_extra=None,
    ):
        assert email_ids is None
        assert phone_ids == [phone_id]
        assert yandex_uids is None
        assert fields is None
        assert not primary_replica
        email_infos = []
        if email_info is not None:
            email_info.update(
                {
                    'created': '2015-05-18T00:00:00+0000',
                    'updated': '2015-05-18T00:00:00+0000',
                },
            )
            email_infos.append(email_info)
        yield async.return_value(email_infos)

    @patch('taxi.external.personal.retrieve')
    @async.inline_callbacks
    def mock_personal(data_type, request_id, log_extra=None, **kwargs):
        assert data_type == 'emails'
        assert request_id.startswith('personal_')
        yield
        async.return_value({'id': request_id, 'email': request_id[9:]})

    if exc is not None:
        with pytest.raises(exc) as exc_info:
            yield email_manager.get_email(user_id=user_id)
        if type(exc) == email_manager.ConfirmationError:
            assert email == exc_info.value.email
    else:
        email_info = yield email_manager.get_email(user_id=user_id)
        assert email_info.email == email
        assert email_info.confirmed is True


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('email,valid', [
    ('', False),
    ('a', False),
    ('@', False),
    ('a@b', False),
    ('a@b.c', False),
    ('user@.ru', False),
    ('@mail.ru', False),
    ('123@mail.ru', True),
    ('m-e.too@some.other.service', True),
    ('nikslim@mail.yandex', True),
    ('someuser+yataxi@gmail.com', True),
    ('user1@ya.ru', True),
    ('e_val@chat.ru', True),
    ('  trim@me.ru ', True)  # TAXIBACKEND-2569
])
def test_validate_email(email, valid):
    if valid:
        assert email_manager.validate_email(email) is True
    else:
        with pytest.raises(email_manager.MalformedEmailError):
            email_manager.validate_email(email)


@pytest.mark.filldb(
    static='confirm',
    user_phones='confirm',
)
@pytest.mark.config(
    APPLICATION_MAP_BRAND={
        '__default__': 'yataxi',
        'someotherapp': 'other_app',
    },
    APPLICATION_MAP_TRANSLATIONS={
        'android:10': {
            'notify': 'go.notify'
        }
    },
    RIDE_REPORT_PARAMS_EXTENDED={
        '__default__': {
            '__default__': {
              '__default__': {
                'confirmation_logo': 'CONFIRMATION_LOGO_URL',
                'headers': {
                  'X-Yandex-Hint': 'label=SystMetkaSO:taxi'
                },
                'logo_url': 'LOGO_URL',
                'logo_width': 154,
                'scheme_url': 'DEFAULT_SCHEME_URL',
                'sender': 'Yandex.Taxi <no-reply@taxi.yandex.com>',
                'support_url': 'https://yandex.ru/support/taxi/contact-us.html',
                'taxi_host': 'taxi.yandex.com',
                'ride_report_template': 'this_should_not_be_used'
              },
              'ru': {
                'logo_url': 'RU_LOGO_URL',
                'logo_width': 178,
                'scheme_url': 'RU_SCHEME_URL',
                'sender': 'Яндекс.Такси <no-reply@taxi.yandex.ru>',
                'taxi_host': 'taxi.yandex.ru'
              },
              'en': {
              }
            }
        },
        'yataxi:android:10': {
            '__default__': {
              '__default__': {
                'confirmation_logo': 'CONFIRMATION_LOGO_URL',
                'headers': {
                  'X-Yandex-Hint': 'label=SystMetkaSO:taxi'
                },
                'logo_url': 'LOGO_URL',
                'logo_width': 154,
                'scheme_url': 'DEFAULT_SCHEME_URL',
                'sender': 'Yandex.go <no-reply@go.yandex.com>',
                'support_url': 'https://yandex.ru/support/taxi/contact-us.html',
                'taxi_host': 'go.yandex.com',
                'logo_host': 'another.url.com',
                'ride_report_template': 'this_should_not_be_used'
              },
              'ru': {
                'logo_url': 'RU_LOGO_URL',
                'logo_width': 178,
                'scheme_url': 'RU_SCHEME_URL',
                'sender': 'Яндекс.Go <no-reply@go.yandex.ru>',
                'taxi_host': 'go.yandex.ru'
              },
              'en': {
              }
            }
        },
        'yauber': {
            '__default__': {
                '__default__': {
                    'arrow_png': 'ARROW_PNG_URL',
                    'confirmation_logo': 'UBER_CONFIRMATION_LOGO',
                    'headers': {
                      'X-Yandex-Hint': 'label=SystMetkaSO:taxi'
                    },
                    'lightning': 'UBER_LIGHTNING',
                    'logo_url': 'UBER_LOGO_URL',
                    'logo_width': 100,
                    'point_a': 'UBER_POINT_A',
                    'point_b': 'UBER_POINT_B',
                    'print_png': 'PRINT_PNG',
                    'ruble': 'UBER_RUBLE',
                    'ruble_big': 'UBER_RUBLE_BIG',
                    'scheme_url': 'UBER_SCHEME_URL',
                    'sender': 'Uber <no-reply@support-uber.com>',
                    'shadow': 'UBER_SHADOW',
                    'support_url': 'https://support-uber.com/support',
                    'taxi_host': 'support-uber.com',
                    'visa_card': 'UBER_VISA'
                },
                'ru': {
                }
            }
        },
        'other_app': {
            '__default__': {
                '__default__': {
                    'taxi_host': 'other_app.com',
                    'logo_url': 'hello',
                    'logo_width': 120,
                    'scheme_url': 'url',
                    'support_url': 'support_url',
                    'sender': 'no-reply@other_app.com',
                    'ride_report_template': 'this_should_not_be_used'
                }
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'confirmation_link.body.confirmation_text', 'ru', 'confirmation_text'),
    ('notify', 'confirmation_link.body.ignore_it', 'ru', 'ignore it'),
    ('notify', 'confirmation_link.html_body.title', 'ru', 'title'),
    ('notify', 'confirmation_link.html_body.hello', 'ru', 'hello'),
    (
            'notify',
            'confirmation_link.html_body.confirmation_text.other_app',
            'ru',
            'other_app_confirmation'
    ),
    ('notify', 'confirmation_link.html_body.confirmation_text', 'ru', 'html_confirmation_text'),
    ('notify', 'confirmation_link.html_body.ignore_it', 'ru', 'ignore_it'),
    ('notify', 'confirmation_link.html_body.thanks', 'ru', 'thanks'),
    ('notify', 'confirmation_link.html_body.yandex_taxi', 'ru', 'yandex_taxi'),
    ('notify', 'confirmation_link.html_body.logo_title', 'ru', 'logo_title'),
    ('notify', 'confirmation_link.subject', 'ru', 'subject'),

    ('notify', 'confirmation_link.body.confirmation_text', 'en', 'confirmation_text'),
    ('notify', 'confirmation_link.body.ignore_it', 'en', 'ignore it'),
    ('notify', 'confirmation_link.html_body.title', 'en', 'title'),
    ('notify', 'confirmation_link.html_body.hello', 'en', 'hello'),
    (
            'notify',
            'confirmation_link.html_body.confirmation_text.other_app',
            'en',
            'other_app_confirmation'
    ),
    ('notify', 'confirmation_link.html_body.confirmation_text', 'en', 'html_confirmation_text'),
    ('notify', 'confirmation_link.html_body.ignore_it', 'en', 'ignore_it'),
    ('notify', 'confirmation_link.html_body.thanks', 'en', 'thanks'),
    ('notify', 'confirmation_link.html_body.yandex_taxi', 'en', 'yandex_taxi'),
    ('notify', 'confirmation_link.html_body.logo_title', 'en', 'logo_title'),
    ('notify', 'confirmation_link.subject', 'en', 'Your confirmation link'),
    ('notify', 'confirmation_link.body.confirmation_text.other_app', 'ru', 'other_app'),

    ('go.notify', 'confirmation_link.body.confirmation_text', 'ru', 'go confirmation_text'),
    ('go.notify', 'confirmation_link.body.ignore_it', 'ru', 'go ignore it'),
    ('go.notify', 'confirmation_link.html_body.title', 'ru', 'go title'),
    ('go.notify', 'confirmation_link.html_body.hello', 'ru', 'go hello'),
    (
            'go.notify',
            'confirmation_link.html_body.confirmation_text.other_app',
            'ru',
            'go other_app_confirmation'
    ),
    ('go.notify', 'confirmation_link.html_body.confirmation_text', 'ru', 'go_html_confirmation_text'),
    ('go.notify', 'confirmation_link.html_body.ignore_it', 'ru', 'go_ignore_it'),
    ('go.notify', 'confirmation_link.html_body.thanks', 'ru', 'go thanks'),
    ('go.notify', 'confirmation_link.html_body.yandex_taxi', 'ru', 'go yandex_taxi'),
    ('go.notify', 'confirmation_link.html_body.logo_title', 'ru', 'go logo_title'),
    ('go.notify', 'confirmation_link.subject', 'ru', 'go_subject'),
])
@pytest.mark.parametrize(
    'email_id, personal_email_id, confirmed, confirmation_code, application, '
    'locale, has_call, test_data',
    [
        # no sent email for confirmed email
        (
            'email_id_user_phone_2',
            'personal_another@mail.ru', True, '5678',
            YATAXI_APP_NAME, 'ru', False, {},
        ),
        # sent email (locale: ru)
        (
            'email_id_user_phone_1',
            'personal_sample@mail.ru', False, '1234',
            YATAXI_APP_NAME, 'ru', True,
            {
                'sender': 'Яндекс.Такси <no-reply@taxi.yandex.ru>',
                'to': 'sample@mail.ru',
                'subject': 'subject',
                'body': 'https://taxi.yandex.ru/email/confirm/?'
                        'email=sample%40mail.ru&confirmation_code=1234',
                'html_body': u'html_confirmation_text taxi.yandex.ru '
                             u'RU_SCHEME_URL ignore_it',
            },
        ),
        # sent email (locale: en)
        (
            'email_id_user_phone_1',
            'personal_sample@mail.ru', False, '1234',
            YATAXI_APP_NAME, 'en', True,
            {
                'sender': 'Yandex.Taxi <no-reply@taxi.yandex.com>',
                'to': 'sample@mail.ru',
                'subject': 'Your confirmation link',
                'body': 'https://taxi.yandex.com/email/confirm/?'
                        'email=sample%40mail.ru&confirmation_code=1234',
                'html_body': u'html_confirmation_text taxi.yandex.com '
                             u'DEFAULT_SCHEME_URL ignore_it',
            },
         ),
        # sent email (unknown locale)
        (
            'email_id_user_phone_1',
            'personal_sample@mail.ru', False, '1234',
            YATAXI_APP_NAME, 'de', True,
            {
                'subject': 'subject',
            },
        ),
        # sent email for another app
        (
            'email_id_user_phone_3',
            'personal_onemore@mail.ru', False, '9012',
            'someotherapp', 'ru', True,
            {
                'sender': 'no-reply@other_app.com',
                'to': 'onemore@mail.ru',
                'subject': 'subject',
                'body': u'https://other_app.com/email/confirm/?'
                        u'email=onemore%40mail.ru&confirmation_code=9012',
                'html_body': u'other_app_confirmation other_app.com '
                             u'url ignore_it',
            },
        ),
        # sent email with overriden major version customization
        (
            'email_id_user_phone_3',
            'personal_sample@mail.ru', False, '1234',
            YATAXI_APP_NAME + ':10', 'ru', True,
            {
                'sender': 'Яндекс.Go <no-reply@go.yandex.ru>',
                'to': 'sample@mail.ru',
                'subject': 'go_subject',
                'body': 'https://go.yandex.ru/email/confirm/?'
                        'email=sample%40mail.ru&confirmation_code=1234',
                'html_body': u'go_html_confirmation_text go.yandex.ru '
                             u'RU_SCHEME_URL go_ignore_it',
            },
        ),
        # sent email for another app with some major version (same result as wo version)
        (
            'email_id_user_phone_3',
            'personal_onemore@mail.ru', False, '9012',
            'someotherapp:999', 'ru', True,
            {
                'sender': 'no-reply@other_app.com',
                'to': 'onemore@mail.ru',
                'subject': 'subject',
                'body': u'https://other_app.com/email/confirm/?'
                        u'email=onemore%40mail.ru&confirmation_code=9012',
                'html_body': u'other_app_confirmation other_app.com '
                             u'url ignore_it',
            },
        ),
    ],
)
@pytest.mark.parametrize('exp_use_sticker, exp_send_via_sender', [
    (exp_use_sticker, exp_send_via_sender)
    for exp_use_sticker in [True, False]
    for exp_send_via_sender in [True, False]
])
@pytest.inline_callbacks
def test_send_confirmation_email(
    patch,
    email_id,
    personal_email_id,
    confirmed,
    confirmation_code,
    application,
    locale,
    has_call,
    test_data,
    exp_use_sticker,
    exp_send_via_sender,
):
    # we use confirmation_link_tpl template for all of our confirmation_emails

    @patch('taxi.external.experiments3.get_values')
    def _get_exp3(consumer, experiments_args, log_extra=None):
        assert consumer == 'backend/email_manager'
        assert experiments_args[0].name == 'personal_email_id'
        assert experiments_args[0].type == 'string'
        assert experiments_args[0].value == personal_email_id

        return [exp3.ExperimentsValue(
            'use_sticker_for_confirmation_email',
            {
                'use_sticker': exp_use_sticker,
                'send_via_sender': exp_send_via_sender,
            }
        )]

    @patch('taxi.internal.email_sender.send')
    def _send_smailik(email_message, log_extra=None):
        email_message.validate()

    @patch('taxi.internal.email_sender.sticker.send')
    def _send_sticker(
        email_message,
        email_personal_id,
        send_via_sender,
        log_extra=None,
    ):
        assert personal_email_id == email_personal_id
        assert exp_send_via_sender == send_via_sender
        email_message.validate(recipient_required=False)

    @patch('taxi.util.template.render_template')
    def _render_template(template, context, template_type=None):
        for key, value in context.items():
            template = template.replace(u'${{{}}}'.format(key), unicode(value))
        return template

    @patch('taxi.external.userapi.get_user_emails')
    @async.inline_callbacks
    def mock_userapi(
            brand,
            email_ids=None,
            phone_ids=None,
            yandex_uids=None,
            fields=None,
            primary_replica=False,
            log_extra=None,
    ):
        assert email_ids == [email_id]
        assert phone_ids is None
        assert yandex_uids is None
        assert fields == [
            'personal_email_id', 'confirmed', 'confirmation_code',
        ]
        assert primary_replica
        email_info = {
            'personal_email_id': personal_email_id,
            'confirmed': confirmed,
            'confirmation_code': confirmation_code,
        }
        yield async.return_value([email_info])

    @patch('taxi.external.personal.retrieve')
    @async.inline_callbacks
    def mock_personal(data_type, request_id, log_extra=None, **kwargs):
        assert request_id.startswith('personal_')
        yield
        async.return_value({'id': request_id, 'email': request_id[9:]})

    yield email_manager.send_confirmation_email(
        email_id, application, locale,
    )

    assert len(_get_exp3.calls) == (1 if has_call else 0)

    should_send_via_sticker = exp_use_sticker or exp_send_via_sender
    if should_send_via_sticker:
        assert len(_send_smailik.calls) == 0

        calls = _send_sticker.calls
        keys_to_skip = ['to']
    else:
        assert len(_send_sticker.calls) == 0

        calls = _send_smailik.calls
        keys_to_skip = []

    assert len(calls) == (1 if has_call else 0)
    if has_call:
        message = calls[0]['email_message']
        for key in test_data:
            if key in keys_to_skip:
                continue
            assert getattr(message, key, None) == test_data[key]


@pytest.mark.config(
    RIDE_REPORT_PARAMS_EXTENDED={
        '__default__': {
            '__default__': {
                '__default__': {
                    'key': 'value'
                }
            }
        },
        'common': {
            'all_key': 'all_value',
        },
        'yataxi': {
            '__default__': {
                '__default__': {}
            },
            'common': {
              'app_key': 'app_value',
            },
            'rus': {
                '__default__': {
                    'overridden_key2': 'value'
                },
                'ru': {
                    'overridden_key': 'russian_override'
                },
                'en': {
                    'overridden_key': 'english_override'
                },
            },
            'byl': {
                '__default__': {
                    'key': 'default_byl'
                },
                'by': {
                    'key': 'byl_by_override'
                },
            }
        },
        'yauber': {
            '__default__': {
                '__default__': {
                    'def_uber': 'def_uber'
                }
            },
            'common': {
                'app_key': 'uber_app_value',
            },
            'rus': {
                '__default__': {
                    'key': 'default_rus'
                },
                'az': {
                    'key': 'override_def_az'
                },
            },
        }
    },
    TEST_RIDE_REPORT_PARAMS_EXTENDED={
        '__default__': {
            '__default__': {
                '__default__': {
                    'key': 'test_override_value'
                }
            }
        },
        'yauber': {
            '__default__': {
                '__default__': {}
            },
            'rus': {
                '__default__': {},
                'ru': {
                    'key': 'test_override_def_ru'
                },
            },
        }
    }

)
@pytest.mark.parametrize(
    'brand, country, locale, expected_locale, '
    'expected_config, test_new_template',
    [
        (
            'yataxi', 'rus', 'ru',
            'ru',
            {
                'all_key': 'all_value',  # common
                'app_key': 'app_value',  # yataxi.common
                'overridden_key2': 'value',  # yataxi.rus
                'overridden_key': 'russian_override',  # yataxi.ru
            },
            False,
        ),
        (
            'yataxi', 'rus', 'en',
            'en',
            {
                'all_key': 'all_value',  # common
                'app_key': 'app_value',  # yataxi.common
                'overridden_key2': 'value',  # yataxi.rus
                'overridden_key': 'english_override',  # yataxi.en
            },
            False,
        ),
        (
            'yataxi', 'byl', 'by',
            'by',
            {
                'all_key': 'all_value',  # common
                'app_key': 'app_value',  # yataxi.common
                'key': 'byl_by_override',  # yataxi.by (override yataxi.byl)
            },
            False,
        ),
        (
            'yauber', 'rus', 'ru',
            'ru',
            {
                'all_key': 'all_value',  # common
                'app_key': 'uber_app_value',  # yauber.common
                'key': 'default_rus',   # yauber.rus
            },
            False,
        ),
        (
            'yauber', 'rus', 'az',
            'az',
            {
                'all_key': 'all_value',  # common
                'app_key': 'uber_app_value',  # yauber.common
                'key': 'override_def_az',   # yauber.az (not yauber.rus)
            },
            False,
        ),
        (
            'yauber', 'rom', 'ru',
            'ru',
            {
                'all_key': 'all_value',  # common
                'app_key': 'uber_app_value',   # yauber.common
                'def_uber': 'def_uber',  # yauber.__default__.__default__
            },
            False,
        ),
        (
            'yauber', 'rus', 'ru',
            'ru',
            {
                'all_key': 'all_value',  # common
                'app_key': 'uber_app_value',  # yauber.common
                'key': 'test_override_def_ru',  # yauber.rus.ru
            },
            True
        ),
    ]
)
@pytest.inline_callbacks
def test_ride_report_config(brand, country, locale, expected_locale,
                            expected_config, test_new_template):
    locale, locale_config = yield email_manager._get_extended_config(
        brand,
        country,
        locale,
        test_new_template=test_new_template
    )
    assert locale == expected_locale
    assert locale_config == expected_config


@pytest.mark.translations([
    ('notify', 'somekey', 'ru', 'original value'),
    ('notify', 'someotherkey', 'ru', 'original'),
    ('notify', 'someotherkey.application', 'ru', 'overridden'),

])
def test_application_translations():
    result = email_manager._get_string_for_application(translations.translations.notify,
        'somekey', 'application', 'ru'
    )
    assert result == 'original value'

    result = email_manager._get_string_for_application(translations.translations.notify,
        'someotherkey', 'application', 'ru'
    )
    assert result == 'overridden'
