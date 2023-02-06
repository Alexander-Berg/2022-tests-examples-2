import pytest

TAXIMETER = 'Taximeter 9.61 (1234)'

DEFAULT_FLOWS_SETTINGS_CONFIG = {
    'flows_ordering': [
        {'name': 'driver-without-auto'},
        {'name': 'driver-with-auto'},
        {'name': 'courier'},
        {'name': 'eats-courier'},
    ],
}

DEFAULT_AVAILABLE_FLOWS = {
    'available_flows': [
        {'code': 'driver-without-auto'},
        {'code': 'driver-with-auto'},
        {'code': 'courier'},
        {'code': 'eats-courier', 'url': 'https://courier-selfreg-form.yandex'},
    ],
    'delivery_driver_allowed': True,
}


@pytest.mark.config(
    TAXIMETER_SELFREG_ON_FOOT_ENABLED={'enable': True, 'cities': ['Москва']},
    TAXIMETER_SELFREG_SETTINGS={'enabled_countries': ['rus']},
    SELFREG_EATS_COURIER_SETTINGS={
        'url': 'https://courier-selfreg-form.yandex',
    },
)
@pytest.mark.client_experiments3(
    consumer='selfreg',
    config_name='selfreg_v2_available_flows_settings',
    args=[],
    value=DEFAULT_FLOWS_SETTINGS_CONFIG,
)
@pytest.mark.parametrize(
    'token, city, response_status',
    [
        pytest.param('token_moscow', 'Москва', 200, id='Ok'),
        pytest.param('token_unknown', 'Москва', 401, id='Unknown token'),
        pytest.param('token_piter', 'Питер', 400, id='Invalid city'),
    ],
)
async def test_selfreg_v1_professions(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        token,
        city,
        response_status,
):
    mock_hiring_forms_default.set_regions(['Москва'])

    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    @mockserver.json_handler(
        '/contractor-profession/internal/v1/selfreg/professions',
    )
    async def _get_constructor(request):
        assert request.method == 'POST'
        assert request.headers['User-Agent'] == TAXIMETER
        assert request.headers['Accept-Language'] == 'ru'
        body = request.json
        assert body['city'] == city
        assert body['phone_pd_id'] == '+70009325298_personal'
        assert body['flows_info'] == DEFAULT_AVAILABLE_FLOWS
        return {'foo': 'bar'}

    headers = {'User-Agent': TAXIMETER, 'Accept-Language': 'ru'}

    response = await taxi_selfreg.post(
        '/selfreg/v1/professions',
        json={'city': city},
        params={'token': token},
        headers=headers,
    )
    assert response.status == response_status
    if response.status == 200:
        content = await response.json()
        assert content == {'foo': 'bar'}
        assert _hiring_types.times_called == 1
        assert _get_constructor.times_called == 1
