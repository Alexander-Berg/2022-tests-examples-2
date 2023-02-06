import pytest

from . import configs
from . import experiments

LAYOUT_SLUG_EXPERIMENT = {
    'name': 'eats_layout_template_experiments_widget',
    'consumers': ['layout-constructor/layout'],
    'default_value': {'layout_slug': 'layout_with_experiments'},
}

LAYOUT_RESPONSE = {
    'data': {
        'type of widget': [
            {
                'id': '1_experiments_widget',
                'template_name': 'experiments_widget template 1',
                'payload': {'something': 'put in widget'},
            },
        ],
    },
    'layout': [
        {
            'id': '1_experiments_widget',
            'payload': {'title': 'Any name widget'},
            'type': 'type of widget',
        },
    ],
}


@configs.keep_empty_layout()
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template_experiments_widget',
    },
)
@pytest.mark.experiments3(**LAYOUT_SLUG_EXPERIMENT)
@pytest.mark.experiments3(
    name='exp_id_1',
    consumers=['layout-constructor/widget'],
    default_value={
        'type': 'type of widget',
        'payload': {'something': 'put in widget'},
    },
)
async def test_layout_exp_standard(taxi_eats_layout_constructor):
    """Теструет виджет экспериментов, что он возвращает корректный ответ
    """

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'content-type': 'application/json',
        },
        #  params={},
        json={'location': {'latitude': 1.0, 'longitude': 2.0}},
    )

    assert response.status_code == 200
    assert response.json() == LAYOUT_RESPONSE


@configs.layout_experiment_name('eats_layout_template_experiments_widget')
@experiments.layout(
    layout_slug='layout_with_experiments',
    experiment_name='eats_layout_template_experiments_widget',
)
@pytest.mark.experiments3(
    name='exp_id_1',
    consumers=['layout-constructor/widget'],
    default_value={
        'type': 'type of widget',
        'payload': {'places': ['some place']},
    },
)
async def test_layout_exp_with_places(taxi_eats_layout_constructor):
    """Проверяем, что виджет эксперимента с массивом 'places' не удаляется
    """

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'content-type': 'application/json',
        },
        #  params={},
        json={'location': {'latitude': 1.0, 'longitude': 2.0}},
    )

    assert response.status_code == 200
    assert response.json() == {
        'data': {
            'type of widget': [
                {
                    'id': '1_experiments_widget',
                    'template_name': 'experiments_widget template 1',
                    'payload': {'places': ['some place']},
                },
            ],
        },
        'layout': [
            {
                'id': '1_experiments_widget',
                'payload': {'title': 'Any name widget'},
                'type': 'type of widget',
            },
        ],
    }


@configs.keep_empty_layout()
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template_experiments_widget',
    },
)
@pytest.mark.experiments3(**LAYOUT_SLUG_EXPERIMENT)
@pytest.mark.experiments3(
    name='exp_not_our_id',
    consumers=['layout-constructor/widget'],
    default_value={
        'type': 'stories',
        'payload': {'something': 'put in widget'},
    },
)
async def test_layout_exp_empty(taxi_eats_layout_constructor):
    """Теструет виджет экспериментов, что он ничего не возвращает, если
    нет нужного эксперимента
    """

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'content-type': 'application/json',
        },
        #  params={},
        json={'location': {'latitude': 1.0, 'longitude': 2.0}},
    )

    expected = {'data': {}, 'layout': []}

    assert response.status_code == 200
    assert response.json() == expected


@configs.keep_empty_layout()
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template_experiments_widget',
    },
)
@pytest.mark.experiments3(**LAYOUT_SLUG_EXPERIMENT)
@pytest.mark.experiments3(
    name='exp_id_1',
    consumers=['layout-constructor/widget'],
    default_value={'type': 1, 'payload': {'something': 'put in widget'}},
)
async def test_layout_exp_invalid_type(taxi_eats_layout_constructor):
    """
    Проверяет, что в случае если в эксперементе содержится невалидное
    значение сервис не вернет ошибок.
    """

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'content-type': 'application/json',
        },
        json={'location': {'latitude': 1.0, 'longitude': 2.0}},
    )

    expected = {'data': {}, 'layout': []}

    assert response.status_code == 200
    assert response.json() == expected
