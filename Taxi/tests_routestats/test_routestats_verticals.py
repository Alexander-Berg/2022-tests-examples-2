import pytest


PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
    'X-AppMetrica-DeviceId': 'DeviceId',
}


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=['top_level:proxy', 'top_level:verticals', 'verticals:multiclass'],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['uservices/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='verticals_multiclass_support',
    consumers=['uservices/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(filename='verticals_selector_exp.json')
@pytest.mark.translations(
    tariff={
        'interval_description': {'ru': 'от %(minimal_price)s'},
        'routestats.multiclass.name': {'ru': 'Самый быстрый'},
        'routestats.multiclass.details.description.title': {
            'ru': 'Несколько тарифов',
        },
        'routestats.multiclass.details.description.subtitle': {
            'ru': 'Назначим ближайшую к вам машину',
        },
        'routestats.multiclass.details.order_button.text': {
            'ru': 'Выберите минимум два тарифа',
        },
        'routestats.multiclass.search_screen.title': {'ru': 'Поиск'},
        'routestats.multiclass.search_screen.subtitle': {
            'ru': 'в нескольких тарифах',
        },
        'routestats.multiclass.details.fixed_price': {'ru': 'до %(price)s'},
        'routestats.multiclass.details.not_fixed_price': {
            'ru': 'от %(price)s',
        },
    },
    client_messages={
        'multiclass.min_selected_count.text': {
            'ru': 'Выберите минимум два тарифа',
        },
        'routestats.tariff_unavailable.multiclass_preorder_unavailable': {
            'ru': 'Для этого тарифа нельзя запланировать поездку',
        },
    },
)
async def test_verticals_selector(taxi_routestats, mockserver, load_json):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        # check that we pass multiclass options for old multiclass to protocol
        assert request.json['multiclass_options'] == {
            'class': ['econom', 'business', 'comfortplus'],
        }
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_2.json'),
        }

    req = load_json('request.json')
    req['supports_verticals_selector'] = True
    req['multiclass_options'] = {
        'class': ['econom', 'business', 'comfortplus'],
        'verticals': [
            {'class': ['business', 'econom'], 'vertical_id': 'taxi'},
        ],
    }
    req['supported'] = [{'type': 'verticals_multiclass'}]

    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    response_body = response.json()

    assert (
        load_json('verticals_selector_response.json')
        == response_body['verticals']
    )
    assert response_body['verticals_modes'] == ['verticals_selector']


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=['top_level:proxy', 'top_level:verticals', 'verticals:multiclass'],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['uservices/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='verticals_multiclass_support',
    consumers=['uservices/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='plugin_decoupling',
    consumers=['uservices/routestats'],
    clauses=[
        {
            'value': {},
            'predicate': {
                'init': {
                    'value': 'corp',
                    'arg_name': 'payment_option',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
        },
    ],
)
@pytest.mark.experiments3(filename='verticals_selector_exp.json')
@pytest.mark.translations(
    tariff={
        'interval_description': {'ru': 'от %(minimal_price)s'},
        'routestats.multiclass.name': {'ru': 'Самый быстрый'},
        'routestats.multiclass.details.description.title': {
            'ru': 'Несколько тарифов',
        },
        'routestats.multiclass.details.description.subtitle': {
            'ru': 'Назначим ближайшую к вам машину',
        },
        'routestats.multiclass.details.order_button.text': {
            'ru': 'Выберите минимум два тарифа',
        },
        'routestats.multiclass.search_screen.title': {'ru': 'Поиск'},
        'routestats.multiclass.search_screen.subtitle': {
            'ru': 'в нескольких тарифах',
        },
        'routestats.multiclass.details.fixed_price': {'ru': 'до %(price)s'},
        'routestats.multiclass.details.not_fixed_price': {
            'ru': 'от %(price)s',
        },
    },
    client_messages={
        'multiclass.min_selected_count.text': {
            'ru': 'Выберите минимум два тарифа',
        },
        'routestats.tariff_unavailable.multiclass_preorder_unavailable': {
            'ru': 'Для этого тарифа нельзя запланировать поездку',
        },
        'routestats.tariff_unavailable.unsupported_requirement': {
            'ru': 'Для этого тарифа нельзя запланировать поездку',
        },
        'routestats.tariff_unavailable.unsupported_payment_method': {
            'ru': 'Выбранный способ оплаты не доступен',
        },
        'routestats.tariff_unavailable.multiclass_unavailable': {
            'ru': 'Поменяйте тарифы: выбранные сейчас недоступны',
        },
    },
)
@pytest.mark.parametrize(
    'preorder,expected_response_file,request_file',
    [
        pytest.param(
            True, 'multiclass/response_preorder.json', 'request.json',
        ),
        pytest.param(
            False,
            'multiclass/response_unsupported_payment_type.json',
            'multiclass/request_unsupported_payment_type.json',
        ),
        pytest.param(
            False,
            'multiclass/response_unsupported_reqs.json',
            'multiclass/request_unsupported_req.json',
            marks=(
                pytest.mark.tariff_settings(
                    filename='multiclass/tariff_settings_bad_reqs.json',
                ),
            ),
        ),
    ],
)
async def test_verticals_selector_multiclass(
        taxi_routestats,
        mockserver,
        load_json,
        expected_response_file,
        preorder,
        request_file,
):
    preorder_id = 'test_preorder_id'

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        # check that we pass multiclass options for old multiclass to protocol
        assert request.json['multiclass_options'] == {
            'class': ['econom', 'business', 'comfortplus'],
        }
        if preorder:
            assert request.json['preorder_request_id'] == preorder_id
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_2.json'),
        }

    req = load_json(request_file)

    req['multiclass_options']['verticals'] = [
        {'class': ['business', 'econom'], 'vertical_id': 'taxi'},
    ]
    req['supported'] = [{'type': 'verticals_multiclass'}]
    req['supports_verticals_selector'] = True

    if preorder:
        req['preorder_request_id'] = preorder_id

    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert load_json(expected_response_file) == response_body['verticals']
    assert response_body['verticals_modes'] == ['verticals_selector']
