import pytest


MULTICLASS_TRANSLATIONS = pytest.mark.translations(
    client_messages={
        'multiclass.min_selected_count.text': {
            'ru': 'Выберите %(min_count)s и более классов',
        },
        'multiclass.popup.text': {'ru': 'Кто быстрей'},
    },
    tariff={
        'routestats.multiclass.name': {'ru': 'Fast'},
        'routestats.multiclass.details.description': {
            'ru': 'description of multiclass',
        },
        'routestats.multiclass.search_screen.title': {'ru': 'Searching'},
        'routestats.multiclass.search_screen.subtitle': {'ru': 'fastest car'},
    },
)


MULTICLASS_PYTEST_MARKS = [
    pytest.mark.experiments3(
        filename='lightweight_multiclass_experiment.json',
    ),
    pytest.mark.user_experiments('multiclass'),
    pytest.mark.config(
        MULTICLASS_TARIFFS_BY_ZONE={'__default__': ['econom', 'comfortplus']},
    ),
    MULTICLASS_TRANSLATIONS,
]


@pytest.fixture
def mock_request(load_json):
    request = load_json('request.json')

    def _mock(selected_class=None, is_lightweight=None, keep_point_b=False):
        if selected_class:
            request['selected_class'] = selected_class

        if is_lightweight is not None:
            request['is_lightweight'] = is_lightweight

        if keep_point_b is not True:
            request['route'] = request['route'][:1]

        return request

    return _mock


@pytest.mark.parametrize('is_lightweight', [True, False])
@pytest.mark.parametrize(
    'selected_class',
    ['econom', 'business', 'premium_suv', 'nonexistent_class', None],
)
@pytest.mark.config(
    PROTOCOL_CREATE_PIN_IN_PIN_STORAGE=True,
    PROTOCOL_USE_SURGE_CALCULATOR=True,
)
@pytest.mark.user_experiments('no_cars_order_available')
def test_lightweight_request(
        local_services_base,
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        mock_request,
        is_lightweight,
        selected_class,
):
    local_services_base.set_is_lightweight_routestats(is_lightweight)

    visible_classes = ['econom', 'business', 'comfortplus', 'vip', 'minivan']
    is_selected_class_visible = selected_class in visible_classes

    expected_classes = (
        [selected_class]
        if is_lightweight is True and is_selected_class_visible
        else visible_classes
    )
    local_services.set_driver_eta_expected_classes(expected_classes)

    request = mock_request(
        selected_class=selected_class, is_lightweight=is_lightweight,
    )
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()

    for service_level in data['service_levels']:
        expected_has_eta = service_level['class'] in expected_classes
        actual_has_eta = service_level.get('estimated_waiting') is not None
        if is_lightweight:
            assert not actual_has_eta
        else:
            assert actual_has_eta == expected_has_eta


@pytest.mark.parametrize('keep_point_b', [True, False])
@pytest.mark.parametrize(
    'additional_options, response_filename',
    [
        pytest.param('none', 'response.json'),
        pytest.param(
            'paid_options_surge',
            'response_with_surge.json',
            marks=pytest.mark.experiments3(
                filename='lightweight_surge_experiment.json',
            ),
        ),
        pytest.param(
            'multiclass',
            'response_with_multiclass.json',
            marks=MULTICLASS_PYTEST_MARKS,
        ),
    ],
)
@pytest.mark.config(PROTOCOL_USE_SURGE_CALCULATOR=True)
@pytest.mark.user_experiments('no_cars_order_available')
def test_lightweight_response(
        local_services_base,
        local_services,
        taxi_protocol,
        load_json,
        mock_request,
        keep_point_b,
        additional_options,
        response_filename,
):
    local_services_base.set_surge_value(1.4)

    request = mock_request(
        selected_class='econom',
        is_lightweight=True,
        keep_point_b=keep_point_b,
    )
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response = response.json()

    expected_response = load_json(response_filename)
    assert response == expected_response


@pytest.mark.parametrize(
    'selected_class', ['econom', 'business', 'nonexistent_class', None],
)
@pytest.mark.user_experiments('no_cars_order_available')
def test_lightweight_tariffs_available(
        local_services, taxi_protocol, mock_request, selected_class,
):
    visible_classes = ['econom', 'business', 'comfortplus', 'vip', 'minivan']

    request = mock_request(selected_class=selected_class, is_lightweight=True)
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()

    for service_level in data['service_levels']:
        sl_class = service_level['class']
        if sl_class not in visible_classes:
            continue
        assert 'tariff_unavailable' not in service_level
