import pytest


@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'ru': {'ticket_locale': 'ru', 'destination': 'oebs'},
    },
)
@pytest.mark.translations(
    piecework={
        'tariff_type.support_taxi': {'ru': 'Поддержка Такси'},
        'tariff_type.support_eats': {'ru': 'Поддержка Еды'},
        'tariff_type.call_taxi_unified': {
            'ru': 'Заказ Такси по телефону (новый флоу)',
        },
        'tariff_type.cargo_callcenter': {'ru': 'КЦ Логистики'},
        'tariff_type.cargo_support': {'ru': 'Поддержка Логистики'},
        'tariff_type.driver_hiring': {'ru': 'ЦНВ'},
        'tariff_type.grocery': {'ru': 'Поддержка Лавки'},
        'rule_status.waiting_cmpd': {'ru': 'Ожидание данных из Агента'},
        'rule_status.waiting_oebs': {'ru': 'Ожидание данных из OEBS'},
        'rule_status.waiting_calc': {'ru': 'Ожидание расчёта'},
        'rule_status.waiting_tracker': {'ru': 'Ожидание расчёта по Трекеру'},
        'rule_status.waiting_correction': {'ru': 'Ожидание корректировки'},
        'rule_status.waiting_benefits': {'ru': 'Ожидание расчёта премии'},
        'rule_status.success': {'ru': 'Завершено успешно'},
        'rule_status.error': {'ru': 'Завершено с ошибкой'},
        'chatterbox_action.close': {'ru': 'Ответить/решён'},
        'chatterbox_action.comment': {'ru': 'Ответить/ожидание'},
        'chatterbox_action.communicate': {'ru': 'Только отправить'},
        'chatterbox_action.defer': {'ru': 'Отложить'},
        'chatterbox_action.dismiss': {'ru': 'НТО'},
        'chatterbox_action.forward': {'ru': 'В другую линию'},
        'chatterbox_action.export': {'ru': 'Экспорт'},
        'chatterbox_action.update_meta': {'ru': 'Обновление меты'},
    },
)
@pytest.mark.parametrize(
    ['url', 'expected_response'],
    [
        (
            '/v1/tariff_types/list',
            {
                'tariff_types': [
                    {
                        'label': 'Поддержка Такси',
                        'name': 'support-taxi',
                        'api_path': 'v1_payments_support-taxi_process',
                    },
                    {
                        'label': 'Заказ Такси по телефону (новый флоу)',
                        'name': 'call-taxi-unified',
                        'api_path': 'v1_payments_call-taxi-unified_process',
                    },
                    {
                        'label': 'КЦ Логистики',
                        'name': 'cargo-callcenter',
                        'api_path': 'v1_payments_cargo-callcenter_process',
                    },
                    {
                        'label': 'Поддержка Логистики',
                        'name': 'cargo-support',
                        'api_path': 'v1_payments_cargo-support_process',
                    },
                    {
                        'label': 'Поддержка Лавки',
                        'name': 'grocery',
                        'api_path': 'v1_payments_grocery_process',
                    },
                    {
                        'label': 'Поддержка Еды',
                        'name': 'support-eats',
                        'api_path': 'v1_payments_support-eats_process',
                    },
                    {
                        'label': 'ЦНВ',
                        'name': 'driver-hiring',
                        'api_path': 'v1_payments_driver-hiring_process',
                    },
                    {
                        'label': 'asterisk-support-taxi',
                        'name': 'asterisk-support-taxi',
                        'api_path': (
                            'v1_payments_asterisk-support-taxi_process'
                        ),
                    },
                ],
            },
        ),
        (
            '/v1/statuses/list',
            {
                'statuses': [
                    {
                        'label': 'Ожидание данных из Агента',
                        'name': 'waiting_cmpd',
                    },
                    {
                        'label': 'Ожидание данных из OEBS',
                        'name': 'waiting_oebs',
                    },
                    {'label': 'Ожидание расчёта', 'name': 'waiting_calc'},
                    {
                        'label': 'Ожидание расчёта по Трекеру',
                        'name': 'waiting_tracker',
                    },
                    {
                        'label': 'Ожидание корректировки',
                        'name': 'waiting_correction',
                    },
                    {
                        'label': 'Ожидание расчёта премии',
                        'name': 'waiting_benefits',
                    },
                    {'label': 'Завершено успешно', 'name': 'success'},
                    {'label': 'Завершено с ошибкой', 'name': 'error'},
                ],
            },
        ),
        (
            '/v1/actions/list',
            {
                'actions': [
                    {'label': 'Ответить/решён', 'name': 'close'},
                    {'label': 'Ответить/ожидание', 'name': 'comment'},
                    {'label': 'Только отправить', 'name': 'communicate'},
                    {'label': 'НТО', 'name': 'dismiss'},
                    {'label': 'Отложить', 'name': 'defer'},
                    {'label': 'В другую линию', 'name': 'forward'},
                    {'label': 'Экспорт', 'name': 'export'},
                    {'label': 'Обновление меты', 'name': 'update_meta'},
                ],
            },
        ),
        (
            '/v1/countries/list',
            {'countries': [{'label': 'Россия', 'code': 'ru'}]},
        ),
    ],
)
async def test_dropdown_lists(
        web_app_client, mockserver, url, expected_response,
):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _list(request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'code2': 'RU',
                    'name': 'Россия',
                    'phone_code': '7',
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'region_id': 0,
                },
            ],
        }

    response = await web_app_client.get(url)
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response
