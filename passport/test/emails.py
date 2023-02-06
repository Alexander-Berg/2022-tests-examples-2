# -*- coding: utf-8 -*-

from passport.backend.api.templatetags import markdown_email
from passport.backend.api.test.mixins import EmailTestToolkit
from passport.backend.core.conf import settings
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_aliasify,
    assert_user_notified_about_dealiasify,
    assert_user_notified_about_realiasify,
)


def assert_user_notified_about_alias_as_login_and_email_enabled(mailer_faker,
                                                                language,
                                                                email_address,
                                                                firstname,
                                                                login,
                                                                portal_email,
                                                                phonenumber_alias):
    if language == 'ru':
        assert_user_notified_about_aliasify(
            mailer_faker,
            language,
            email_address,
            firstname,
            login,
            portal_email,
            phonenumber_alias,
        )
        return

    yandex_domain = portal_email.split(u'@')[1]
    context = {
        'FIRST_NAME': firstname,
        'PHONE_NUMBER': '+' + phonenumber_alias,
        'PHONE_NUMBER_DIGITAL_EMAIL': markdown_email(phonenumber_alias + '@' + yandex_domain),
        'PHONE_NUMBER_E164_EMAIL': markdown_email('+' + phonenumber_alias + '@' + yandex_domain),
        'PROFILE_PHONES_URL': 'https://passport.yandex.com/profile/phones',
    }
    tanker_keys = [
        'logo_url',
        'greeting',
        'phone_alias.you_enabled_alias_as_login_and_email',
        'phone_alias.dont_use_digital_email_in_sensetive_cases',
        'phone_alias.disable_alias_as_login_in_settings',
        'signature.secure',
    ]
    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.as_login_and_email_enabled_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_alias_as_login_and_email_disabled(mailer_faker,
                                                                 language,
                                                                 email_address,
                                                                 firstname,
                                                                 login,
                                                                 portal_email,
                                                                 phonenumber_alias):
    if language == 'ru':
        assert_user_notified_about_dealiasify(
            mailer_faker,
            language,
            email_address,
            firstname,
            login,
            portal_email,
            phonenumber_alias,
        )
        return

    yandex_domain = portal_email.split(u'@')[1]
    context = {
        'FIRST_NAME': firstname,
        'PHONE_NUMBER': '+' + phonenumber_alias,
        'PHONE_NUMBER_DIGITAL_EMAIL': markdown_email(phonenumber_alias + '@' + yandex_domain),
        'PHONE_NUMBER_E164_EMAIL': markdown_email('+' + phonenumber_alias + '@' + yandex_domain),
        'PROFILE_PHONES_URL': 'https://passport.yandex.com/profile/phones',
    }
    tanker_keys = [
        'logo_url',
        'greeting',
        'phone_alias.you_disabled_alias_as_login',
        'phone_alias.you_disabled_alias_as_email',
        'phone_alias.reenable_alias_as_login_and_email_in_settings',
        'signature.secure',
    ]
    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.as_login_disabled_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_alias_as_login_disabled(mailer_faker,
                                                       language,
                                                       email_address,
                                                       firstname,
                                                       login,
                                                       portal_email,
                                                       phonenumber_alias):
    phrases = settings.translations.NOTIFICATIONS[language]

    context = {
        'FIRST_NAME': firstname,
        'PHONE_NUMBER': '+' + phonenumber_alias,
        'PROFILE_PHONES_URL': phrases['profile_phones_url'],
    }
    tanker_keys = [
        'logo_url',
        'greeting',
        'phone_alias.you_disabled_alias_as_login',
        'phone_alias.reenable_alias_as_login_and_email_in_settings',
        'signature.secure',
    ]
    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.as_login_disabled_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_alias_as_login_and_email_owner_changed(mailer_faker,
                                                                      language,
                                                                      email_address,
                                                                      firstname,
                                                                      login,
                                                                      portal_email,
                                                                      phonenumber_alias):
    if language == 'ru':
        assert_user_notified_about_realiasify(
            mailer_faker,
            language,
            email_address,
            firstname,
            login,
            portal_email,
            phonenumber_alias,
        )
        return

    yandex_domain = portal_email.split(u'@')[1]
    context = {
        'FIRST_NAME': firstname,
        'PHONE_NUMBER': '+' + phonenumber_alias,
        'PHONE_NUMBER_DIGITAL_EMAIL': markdown_email(phonenumber_alias + '@' + yandex_domain),
        'PHONE_NUMBER_E164_EMAIL': markdown_email('+' + phonenumber_alias + '@' + yandex_domain),
        'PROFILE_PHONES_URL': 'https://passport.yandex.com/profile/phones',
        'e164_phone': '+' + phonenumber_alias,
    }
    tanker_keys = [
        'logo_url',
        'greeting',
        'phone_alias.somebody_has_taken_alias_as_login',
        'phone_alias.somebody_has_taken_alias_as_email',
        'phone_alias.create_new_in_settings',
        'signature.secure',
    ]
    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.as_login_disabled_by_somebody_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_alias_as_login_owner_changed(mailer_faker,
                                                            language,
                                                            email_address,
                                                            firstname,
                                                            login,
                                                            portal_email,
                                                            phonenumber_alias):
    context = {
        'FIRST_NAME': firstname,
        'PHONE_NUMBER': '+' + phonenumber_alias,
        'PROFILE_PHONES_URL': 'https://passport.yandex.ru/profile/phones',
        'e164_phone': '+' + phonenumber_alias,
    }
    tanker_keys = [
        'logo_url',
        'greeting',
        'phone_alias.somebody_has_taken_alias_as_login',
        'phone_alias.create_new_in_settings',
        'signature.secure',
    ]
    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.as_login_disabled_by_somebody_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_alias_as_email_enabled(mailer_faker,
                                                      language,
                                                      email_address,
                                                      firstname,
                                                      portal_email,
                                                      phonenumber_alias):
    yandex_domain = portal_email.split(u'@')[1]
    context = {
        'FIRST_NAME': firstname,
        'PHONE_NUMBER_DIGITAL_EMAIL': markdown_email(phonenumber_alias + '@' + yandex_domain),
        'PHONE_NUMBER_E164_EMAIL': markdown_email('+' + phonenumber_alias + '@' + yandex_domain),
        'PROFILE_PHONES_URL': 'https://passport.yandex.ru/profile/phones',
    }
    tanker_keys = [
        'logo_url',
        'greeting',
        'phone_alias.you_enabled_alias_as_email',
        'phone_alias.dont_use_digital_email_in_sensetive_cases',
        'phone_alias.disable_alias_as_email_in_settings',
        'signature.secure',
    ]
    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.enable_as_email_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_alias_as_email_disabled(mailer_faker,
                                                       language,
                                                       email_address,
                                                       firstname,
                                                       portal_email,
                                                       phonenumber_alias):
    yandex_domain = portal_email.split(u'@')[1]
    context = {
        'FIRST_NAME': firstname,
        'PHONE_NUMBER_DIGITAL_EMAIL': markdown_email(phonenumber_alias + '@' + yandex_domain),
        'PHONE_NUMBER_E164_EMAIL': markdown_email('+' + phonenumber_alias + '@' + yandex_domain),
        'PROFILE_PHONES_URL': 'https://passport.yandex.ru/profile/phones',
    }
    tanker_keys = [
        'logo_url',
        'greeting',
        'phone_alias.you_disabled_alias_as_email',
        'phone_alias.reenable_alias_as_email_in_settings',
        'signature.secure',
    ]
    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.disable_as_email_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_alias_as_login_enabled(
    mailer_faker,
    language,
    email_address,
    firstname,
    phone_number,
):
    phrases = settings.translations.NOTIFICATIONS[language]

    context = {
        'FIRST_NAME': firstname,
        'FORMATTED_PHONE_NUMBER': phone_number.international,
        'LOGIN_ALIAS_VALUE': phone_number.digital,
        'MASKED_LOGIN': firstname,
        'YASMS_VALIDATOR_URL': phrases['validator_url'],
    }

    tanker_keys = [
        'greeting',
        'logo_url',
        'phone_alias.on.explanation.no_mailbox',
        'phone_alias.on.links',
        'phone_alias.on.notice',
        'phone_alias.on.warning',
        'signature.secure',
        'validator_url',
    ]

    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_alias.on.subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_secure_phone_bound_to_passwordless_account(
    mailer_faker,
    language,
    email_address,
    firstname,
    login,
):
    phrases = settings.translations.NOTIFICATIONS[language]

    context = {
        'FIRST_NAME': firstname,
        'MASKED_LOGIN': firstname,
        'PHONES_HELP_URL': phrases['phones_help_url'],
        'PROFILE_PHONES_URL': phrases['profile_phones_url'],
        'PROFILE_URL': phrases['profile_url'],
    }

    tanker_keys = [
        'greeting',
        'logo_url',

        'phone_secured.passwordless.phone_bound',

        'В этом случае:',
        'phone_secured.passwordless.remove_unknown_phone',
        'phone_secured.passwordless.global_logout',

        'Узнать больше об управлении привязанными номерами телефонов '
        'можно <a href="%(PHONES_HELP_URL)s" target="_blank">здесь</a>.',

        'signature.secure',
    ]

    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_secured_email_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_secure_phone_removed_without_quarantine_from_passwordless_account(
    mailer_faker,
    language,
    email_address,
    firstname,
    login,
):
    phrases = settings.translations.NOTIFICATIONS[language]

    context = {
        'FIRST_NAME': firstname,
        'MASKED_LOGIN': login,
        'PHONES_HELP_URL': phrases['phones_help_url'],
        'PROFILE_PHONES_URL': phrases['profile_phones_url'],
    }

    tanker_keys = [
        'logo_url',
        'greeting',

        'Удален основной номер телефона, привязанный к вашему аккаунту '
        '%(MASKED_LOGIN)s. Если номер удалили Вы, то всё в порядке. '
        'Если нет — это мог сделать злоумышленник.',

        'В таком случае:',
        'secure_phone_removed_without_quarantine.passwordless.check_recent_logins',

        '<a href="%(PROFILE_PHONES_URL)s" target="_blank">верните удаленный '
        'номер</a> обратно.',

        'Узнать больше об управлении привязанными номерами телефонов можно '
        '<a href="%(PHONES_HELP_URL)s" target="_blank">здесь</a>.',

        'signature.secure',
    ]

    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='secure_phone_removed_without_quarantine_email_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_secure_phone_replacement_started_on_passwordless_account(
    mailer_faker,
    language,
    email_address,
    firstname,
    login,
):
    phrases = settings.translations.NOTIFICATIONS[language]

    context = {
        'FIRST_NAME': firstname,
        'MASKED_LOGIN': login,
        'PROFILE_PHONES_URL': phrases['profile_phones_url'],
        'PHONES_HELP_URL': phrases['phones_help_url'],
    }

    tanker_keys = [
        'logo_url',
        'greeting',

        'Изменён основной номер телефона, привязанный к вашему аккаунту '
        '%(MASKED_LOGIN)s. Если номер изменили Вы, то всё в порядке. Если '
        'нет — это мог сделать злоумышленник.',

        'В таком случае:',
        'secure_phone_replacement_started.passwordless.check_recent_logins',
        'secure_phone_replacement_started.passwordless.cancel_phone_replacement',

        'Узнать больше об управлении привязанными номерами телефонов можно '
        '<a href="%(PHONES_HELP_URL)s" target="_blank">здесь</a>.',

        'signature.secure',
    ]

    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='secure_phone_replacement_started_email_subject',
        context=context,
        tanker_keys=tanker_keys,
    )


def assert_user_notified_about_secure_phone_removal_started_on_passwordless_account(
    mailer_faker,
    language,
    email_address,
    firstname,
    login,
):
    phrases = settings.translations.NOTIFICATIONS[language]

    context = {
        'FIRST_NAME': firstname,
        'MASKED_LOGIN': login,
        'PROFILE_PHONES_URL': phrases['profile_phones_url'],
        'PHONES_HELP_URL': phrases['phones_help_url'],
    }

    tanker_keys = [
        'logo_url',
        'greeting',

        'Основной номер телефона, привязанный к вашему аккаунту '
        '%(MASKED_LOGIN)s, отмечен как недоступный.<br>Это значит, что через '
        '30 дней он будет удалён. Если настройку изменили Вы, то всё в '
        'порядке. Если нет — это мог сделать злоумышленник.',

        'В таком случае:',
        'phone_removal_started.passwordless.check_recent_logins',
        'phone_removal_started.passwordless.cancel_phone_removal',

        'Узнать больше об управлении привязанными номерами телефонов можно '
        '<a href="%(PHONES_HELP_URL)s" target="_blank">здесь</a>.',

        'signature.secure',
    ]

    EmailTestToolkit(mailer_faker).assert_email_sent(
        language=language,
        email_address=email_address,
        subject='phone_removal_started_email_subject',
        context=context,
        tanker_keys=tanker_keys,
    )
