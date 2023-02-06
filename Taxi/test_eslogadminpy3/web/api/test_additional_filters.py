from eslogadminpy3.generated.service.service_schemas import (
    plugin as service_schemas,
)


async def test_get_filters(monkeypatch, load_yaml, web_app, web_app_client):
    _data = sorted(
        [
            {
                'name': 'park_name',
                'type': 'string',
                'title': 'Название парка',
                'search_in': 'response',
            },
            {
                'name': 'type',
                'type': 'string',
                'title': 'Тип логов',
                'allow_array': True,
                'important': True,
                'suggest_from': 'log_types',
            },
            {
                'name': 'user_phone',
                'type': 'string',
                'title': 'Телефон пассажира',
                'placeholder': '+70000000000',
                'search_in': 'response',
            },
            {
                'name': 'cgroups',
                'type': 'string',
                'title': 'Кондукторная группа',
                'allow_array': True,
                'search_in': 'response',
            },
            {
                'name': 'http_code',
                'type': 'integer',
                'title': 'HTTP код',
                'search_in': 'request',
            },
            {
                'name': 'stq_task',
                'type': 'string',
                'title': 'STQ таска',
                'allow_array': True,
                'important': True,
                'suggest_from': 'stq_task_names',
            },
        ],
        key=lambda x: x['name'],
    )
    expected = [
        {
            'name': 'useragent',
            'type': 'string',
            'title': 'UserAgent',
            'search_in': 'response',
            'order': 0,
        },
    ]
    expected.extend({'order': i, **x} for i, x in enumerate(_data, start=1))

    schema = load_yaml('filters.yaml')
    monkeypatch.setitem(
        web_app['context'].service_schemas.schemas, 'filters', schema,
    )
    monkeypatch.setattr(
        web_app['context'].service_schemas,
        'known_filters',
        {x['name']: service_schemas.Filter(**x) for x in schema['filters']},
    )

    response = await web_app_client.get('/v2/additional-filters/')
    assert response.status == 200
    data = await response.json()
    assert sorted(data['filters'], key=lambda x: x['order']) == sorted(
        expected, key=lambda x: x['order'],
    )
