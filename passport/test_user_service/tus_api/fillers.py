# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api.utils import (
    random_alphanumeric,
    random_numeric,
)


log = logging.getLogger(__name__)

DEFAULT_FIRSTNAME = u'Default-Имя'
DEFAULT_LASTNAME = u'Default Фамилия'
DEFAULT_LANGUAGE = 'ru'
DEFAULT_COUNTRY = 'ru'


def _generate_uid_for_external_account():
    return int('999{0}'.format(random_numeric(10)))


def _generate_login():
    return 'yandex-team-{0}.{1}'.format(random_numeric(5), random_numeric(5))


def _generate_password():
    return '{part1}.{part2}'.format(part1=random_alphanumeric(4), part2=random_alphanumeric(4))


def generate_value(field_name):
    if field_name == 'login':
        return _generate_login()
    if field_name == 'password':
        return _generate_password()
    if field_name == 'firstname':
        return DEFAULT_FIRSTNAME
    if field_name == 'lastname':
        return DEFAULT_LASTNAME
    if field_name == 'language':
        return DEFAULT_LANGUAGE
    if field_name == 'country':
        return DEFAULT_COUNTRY
    raise NotImplementedError(field_name)


def fill_missing_account_data(current_data):
    for field, value in current_data.items():
        if not value:
            current_data[field] = generate_value(field)


def normalize_login(login):
    if not login:
        return login

    login = login.strip().lower()
    if '@' in login:
        return login
    return login.replace('.', '-')


def generate_fake_phone_in_e164():
    return "+70000" + random_numeric(6)
