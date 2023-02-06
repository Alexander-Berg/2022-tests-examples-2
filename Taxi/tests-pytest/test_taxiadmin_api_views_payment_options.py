# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

import pytest

from django import test as django_test


@pytest.mark.parametrize(
    'url_path,expected_data',
    [
        (
            '/api/tariff_settings/payment_options/',
            [
                {'value': 'cash', 'label': 'Наличные'},
                {'value': 'card', 'label': 'Карта'},
                {'value': 'coupon', 'label': 'Купон'},
                {'value': 'corp', 'label': 'Корп'},
                {'value': 'applepay', 'label': 'Apple Pay'},
                {'value': 'googlepay', 'label': 'Google Pay'},
                {'value': 'personal_wallet', 'label': 'Личный счет'},
                {'value': 'coop_account', 'label': 'Групповой счет'},
                {'value': 'agent', 'label': 'Через агента'},
                {'value': 'yandex_card', 'label': 'Счёт в Яндексе'},
                {'value': 'cargocorp', 'label': 'Корпоративный Карго'},
                {'value': 'sbp', 'label': 'СБП'},
            ],
        ),
        (
            '/api/user_discounts/payment_options/',
            [
                {'value': 'cash', 'label': 'Наличные'},
                {'value': 'card', 'label': 'Банковская карта'},
                {'value': 'corp', 'label': 'Корпоративный'},
                {'value': 'applepay', 'label': 'Apple Pay'},
                {'value': 'googlepay', 'label': 'Google Pay'},
                {'value': 'personal_wallet', 'label': 'Личный счет'},
                {'value': 'coop_account', 'label': 'Групповой счет'},
                {'value': 'family_account', 'label': 'Семейный аккаунт'},
                {'value': 'business_account', 'label': 'Бизнес аккаунт'},
                {'value': 'yandex_card', 'label': 'Счёт в Яндексе'},
                {'value': 'cargocorp', 'label': 'Корпоративный Карго'},
                {'value': 'sbp', 'label': 'СБП'},
            ],
        ),
        (
            '/api/commissions/payment_options/',
            [
                {'value': 'cash', 'label': 'Наличные'},
                {'value': 'card', 'label': 'Банковская карта'},
                {'value': 'corp', 'label': 'Корпоративный'},
                {'value': 'personal_wallet', 'label': 'Личный счет'},
            ],
        ),
        (
            '/api/commissions/payment_options/?with_workshift=true',
            [
                {'value': 'cash', 'label': 'Наличные'},
                {'value': 'card', 'label': 'Банковская карта'},
                {'value': 'corp', 'label': 'Корпоративный'},
                {'value': 'workshift', 'label': 'Покупка смены'},
                {'value': 'personal_wallet', 'label': 'Личный счет'},
            ],
        ),
    ],
)
@pytest.mark.asyncenv('blocking')
def test_payment_options_views(url_path, expected_data):
    response = django_test.Client().get(url_path)
    assert response.status_code == 200
    data = json.loads(response.content)
    assert sorted(data) == sorted(expected_data)
