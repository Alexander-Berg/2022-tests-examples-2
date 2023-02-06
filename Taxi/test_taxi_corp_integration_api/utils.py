import itertools

from taxi_corp_integration_api.api.common import types

UPDATE_APP_ERROR = 'Обновите приложение для использования новых центров затрат'
REQUIRED_ERROR = 'Не указан центр затрат'
UNKNOWN_ERROR = 'Неверный центр затрат'
UPDATE_APP_ERROR_EN = 'Update app to use new cost centers'


TANKER_KEYS = {
    'order_classes_is_not_permitted': '{forbidden_classes} недоступны',
    'order_zone_restricted_by_payment_type_classes': (
        'Запрещён заказ по корпоративным счетам '
        'по этим тарифам: {forbidden_classes}'
    ),
    'client_doesnt_exists_in_billing': 'Ваш корпоративный счет не найден',
    'client_doesnt_have_permission_to_order': (
        'Страна клиента не совпадает со страной заказа'
    ),
    'order_cost_is_not_permitted': 'Недостаточно денег на счёте',
    'order_cost_is_not_permitted_by_reason_of_client': (
        'Недостаточно денег на счёте'
    ),
    'order_cost_is_not_permitted_by_reason_of_department': (
        'Недостаточно денег на счёте'
    ),
    'order_count_is_not_permitted': 'Лимит на поездки исчерпан',
    'client_deactivate_threshold': (
        'Баланс клиента ниже значения порога отключения'
    ),
    'client_doesnt_have_contract': 'Ваш корпоративный счет больше недоступен',
    'order_zone_corp_disabled': (
        'В зоне недоступна оплата по корпоративным счетам'
    ),
    'order_with_class_express_and_iterim_route_points': (
        'По тарифу доставка запрещено делать поездки с промежуточными точками'
    ),
    'order_is_not_permitted_due_to_high_price': (
        'Сумма поездки превышает максимальную стоимость'
    ),
    'zone_is_not_supported': 'Зона недоступна',
    'time_is_not_permitted': 'error.time_is_not_permitted',
    'fuel_type_is_not_permitted': 'error.fuel_type_is_not_permitted',
    'order_is_restricted_in_the_geo': 'error.order_is_restricted_in_the_geo',
    'description': 'Осталось {balance} из {limit} {currency}',
    'user_is_deleted': 'Пользователь удален',
    'user_is_inactive': 'Пользователь неактивен',
    'invalid_cost_center': UNKNOWN_ERROR,
    'cost_center_is_required': REQUIRED_ERROR,
    'update_app_for_new_cost_centers': UPDATE_APP_ERROR,
    'tariff_plan_is_not_available': 'Не задан тарифный план',
    'tariff_for_zone_is_not_available': 'Не задан тариф для зоны',
    'is_cabinet_only_user': 'Заказ возможен только из корпоративного кабинета',
    'offer_not_accepted': 'Оферта не принята',
    'service_is_disabled': 'Сервис отключен',
    'contract_is_disabled': 'Корпоративный контракт отключен',
    'description_left_of_limit': 'Осталось %(left)s из %(limit)s',
    'billing.insufficient_funds': 'Недостаточно средств',
    'billing.insufficient_funds_to_pay_for_order': (
        'Недостаточно средств для оплаты заказа'
    ),
    'country_is_not_supported': (
        'В этой стране корпоративная оплата не поддерживается'
    ),
    'eats.order_cost_is_not_permitted': (
        'Сумма заказа превышает доступный лимит'
    ),
    'eats.order_cost_is_not_permitted_by_reason_of_department': (
        'Превышен лимит подразделения, обратитесь в свою компанию'
    ),
    'eats.time_range_is_not_permitted': 'Оплата заказа в это время недоступна',
    'eats.time_weekly_is_not_permitted': (
        'Оплата заказа в это время недоступна'
    ),
    'eats.order_is_restricted_in_the_geo': 'Оплата недоступна по этому адресу',
}
TANKER_KEYS_EN = {
    'order_classes_is_not_permitted': '{forbidden_classes} not available',
    'order_zone_restricted_by_payment_type_classes': (
        'Forbidden order by corporates accounts '
        'for these tarifffs: {forbidden_classes}'
    ),
    'client_doesnt_exists_in_billing': 'Your corporate account not found',
    'client_doesnt_have_permission_to_order': (
        'Client country doesn\'t match with order country'
    ),
    'order_cost_is_not_permitted': 'Not sufficient funds',
    'order_cost_is_not_permitted_by_reason_of_client': 'Not sufficient funds',
    'order_cost_is_not_permitted_by_reason_of_department': (
        'Not sufficient funds'
    ),
    'order_count_is_not_permitted': 'order_count_is_not_permitted',
    'client_deactivate_threshold': 'Balance lower than threshold',
    'client_doesnt_have_contract': (
        'Your corporate account is not available anymore'
    ),
    'order_zone_corp_disabled': 'Corporate payments not available in zone',
    'order_with_class_express_and_iterim_route_points': (
        'Tariff delivery denies intermediate points'
    ),
    'order_is_not_permitted_due_to_high_price': (
        'Order is not permitted due to high price'
    ),
    'zone_is_not_supported': 'Zone is not supported',
    'time_is_not_permitted': 'error.time_is_not_permitted',
    'fuel_type_is_not_permitted': 'error.fuel_type_is_not_permitted',
    'order_is_restricted_in_the_geo': 'error.order_is_restricted_in_the_geo',
    'description': 'Left {balance} from {limit} {currency}',
    'user_is_deleted': 'User removed',
    'user_is_inactive': 'User is inactive',
    'invalid_cost_center': 'Invalid cost center',
    'cost_center_is_required': 'Cost center isn\'t specified',
    'update_app_for_new_cost_centers': UPDATE_APP_ERROR_EN,
    'tariff_plan_is_not_available': 'Tariff plan is not specified',
    'tariff_for_zone_is_not_available': 'Tariff for zone is not specified',
    'is_cabinet_only_user': 'Order is permitted only from corp cabinet',
    'offer_not_accepted': 'Offer is not accepted',
    'service_is_disabled': 'Service is disabled',
    'contract_is_disabled': 'Contract is disabled',
    'description_left_of_limit': 'Left %(left)s from %(limit)s',
    'billing.insufficient_funds': 'Insufficient funds',
    'billing.insufficient_funds_to_pay_for_order': (
        'Insufficient funds to pay for order'
    ),
    'country_is_not_supported': (
        'Corporate payment is not supported in this country'
    ),
    'eats.order_cost_is_not_permitted': (
        'error.eats.order_cost_is_not_permitted'
    ),
    'eats.order_cost_is_not_permitted_by_reason_of_department': (
        'error.eats.order_cost_is_not_permitted_by_reason_of_department'
    ),
    'eats.time_range_is_not_permitted': (
        'error.eats.time_range_is_not_permitted'
    ),
    'eats.time_weekly_is_not_permitted': (
        'error.eats.time_weekly_is_not_permitted'
    ),
    'eats.order_is_restricted_in_the_geo': (
        'eats.order_is_restricted_in_the_geo'
    ),
}


def generate_translations():
    translations = {}
    source_app_prefixes = set(
        types.SOURCE_APP_TO_TANKER_PREFIX.values(),
    ).union({'error'})

    for default_prefix, source_app_prefix, key_text in itertools.product(
            {'', 'paymentmethods'},
            source_app_prefixes | {''},
            TANKER_KEYS.items(),
    ):
        key, text = key_text
        final_key = '.'.join(
            [
                key_part
                for key_part in [default_prefix, source_app_prefix, key]
                if key_part
            ],
        )
        translations[final_key] = {'ru': text, 'en': TANKER_KEYS_EN[key]}

    return translations


def new_fields_from_old_value(old_cost_center: dict) -> list:
    if old_cost_center == OLD_COST_CENTER_VALUE:
        return []
    return [
        dict(
            old_cost_center,
            id='',  # пустой id — это признак старого ЦЗ
            title='Центр затрат',  # всегда такое значение
            order_flows=['taxi'],  # всегда такое значение
            services=['taxi'],  # всегда такое значение
        ),
    ]


OLD_COST_CENTER_VALUE = {'required': False, 'format': 'mixed', 'values': []}
OLD_COST_CENTER_NEW_FORMAT = new_fields_from_old_value(OLD_COST_CENTER_VALUE)

CONFIG = dict(
    CORP_DEFAULT_CATEGORIES={
        'rus': ['econom', 'vip'],
        'kaz': ['econom', 'vip'],
        'arm': ['econom', 'vip'],
    },
    CORP_COUNTRIES_SUPPORTED={
        'kaz': {
            'country_code': 'KZ',
            'currency': 'KZT',
            'currency_sign': '₸',
            'default_language': 'ru',
            'utc_offset': '+06:00',
            'vat': 0.12,
            'web_ui_languages': ['kk', 'ru'],
        },
        'rus': {
            'country_code': 'RU',
            'currency': 'RUB',
            'currency_sign': '₽',
            'default_language': 'ru',
            'utc_offset': '+03:00',
            'vat': 0.18,
            'web_ui_languages': ['ru'],
        },
        'arm': {
            'country_code': 'AM',
            'currency': 'AMD',
            'currency_sign': '֏',
            'default_language': 'ru',
            'utc_offset': '+03:00',
            'vat': 0.18,
            'web_ui_languages': ['ru'],
            'skip_pm_billing_check': True,
        },
    },
    COST_CENTERS_ORDER_FLOWS={'eats': 'eats2', 'taxi': 'taxi'},
    LOCALES_MAPPING={},
    CORP_CLIENTS_ORDERS_COUNT_LIMIT={'client_id_1': 1, 'client_id_11': 2},
    CORP_COMBO_ORDERS_DISABLED_CHECKERS=['CostCentersChecker'],
)
TRANSLATIONS = dict(
    corp=generate_translations(),
    tariff={
        'currency.rub': {'ru': 'руб.', 'en': 'rub'},
        'currency.kzt': {'ru': 'тенге', 'en': 'tenge'},
        'currency.amd': {'ru': 'драм', 'en': 'amd'},
        'name.business': {'ru': 'Бизнес', 'en': 'Business'},
        'name.econom': {'ru': 'Эконом', 'en': 'Economy'},
        'name.comfort': {'ru': 'Комфорт', 'en': 'Comfort'},
        'currency_sign.rub': {'ru': '₽'},
    },
)


async def request_corp_paymentmethods(
        taxi_corp_integration_api,
        mockserver,
        request_data,
        zone_name,
        nearestzone_error,
        headers=None,
):
    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _mock_nearestzone(request):
        if nearestzone_error:
            return mockserver.make_response(
                status=nearestzone_error['status'],
                json=nearestzone_error['json'],
            )
        return {'nearest_zone': zone_name}

    return await taxi_corp_integration_api.post(
        '/v1/corp_paymentmethods', headers=headers, json=request_data,
    )
