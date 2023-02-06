PROBLEM_UI_TANKER_KEYS = {
    'maas.problem_ui.button.try_again': {'ru': 'Попробовать снова'},
    'maas.problem_ui.button.cancel': {'ru': 'Отменить'},
    'maas.problem_ui.button.support': {'ru': 'Связаться с поддержкой'},
    'maas.problem_ui.default_title': {'ru': 'Ошибка!!!'},
    'maas.problem_ui.default_description': {
        'ru': 'Наташ, вообще всё сломалось!',
    },
    'maas.problem_ui.known.title': {'ru': 'Ошибка!'},
    'maas.problem_ui.known.description': {'ru': 'Почти всё сломалось..'},
}


KNOWN_PROBLEM_UI = {
    'title_key': 'maas.problem_ui.known.title',
    'description_key': 'maas.problem_ui.known.description',
}

MAAS_TARIFF_SETTINGS = {
    'sale_allowed': True,
    'coupon_series': 'coupon_series_id',
    'trips_count': 10,
    'duration_days': 30,
    'taxi_price': '100.50',
    'subscription_price': '200.50',
    'composite_maas_tariff_id': 'outer_maas_tariff_id',
    'hints': [],
    'description_text_tanker_key': 'maas.tariffs.maas_s.description_text',
    'detailed_description_content_tanker_key': (
        'maas.tariffs.maas_s.detailed_description_content'
    ),
    'title_tanker_key': 'maas.tariffs.maas_s.title',
    'toggle_title_tanker_key': 'maas.tariffs.maas_s.toggle_title',
    'active_image_tag': 'active_tag',
    'expired_image_tag': 'expired_tag',
    'reserved_image_tag': 'reserved_tag',
    'outer_description_tanker_key': 'maas.tariffs.maas_s.outer_description',
}

REDIRECT_URLS = {
    'succeed': 'https://succeed-payment',
    'declined': 'https://failed-payment',
    'canceled': 'https://canceled-payment',
}
