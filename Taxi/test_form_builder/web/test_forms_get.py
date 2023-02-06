import pytest


def _expected_data(expected_translation, **kwargs):
    return {
        'authorization': {'opteum': False, 'passport': False},
        'field_templates': [
            {
                'id': 1,
                'value_type': 'string',
                'is_array': False,
                'has_choices': False,
                'personal_data_type': 'emails',
                'tags': [],
                'default_label': {'translation': 'e-mail'},
                'regex_pattern': '^\\S+@\\S+$',
                'can_be_fillable': True,
                'can_be_filler': True,
            },
            {
                'can_be_fillable': True,
                'can_be_filler': True,
                'has_choices': False,
                'id': 2,
                'is_array': False,
                'tags': [],
                'value_type': 'datetime',
            },
        ],
        'form': {
            'code': 'form_1',
            'title': {'translation': 'x'},
            'description': {'translation': 'x'},
            'default_locale': 'ru',
            'supported_locales': ['en', 'ge'],
            'ya_metric_counter': 62138506,
            'stages': [
                {
                    'title': {'translation': 'x'},
                    'description': {'translation': 'x'},
                    'fields': [
                        {
                            'code': 'driver_email',
                            'template_id': 1,
                            'label': {'translation': 'e-mail водителя'},
                            'obligatory': True,
                            'obligation_condition': 'cond_1',
                            'visible': True,
                            'can_be_filler': True,
                            'can_be_fillable': True,
                        },
                        {
                            'code': 'park_email',
                            'template_id': 1,
                            'label': {'translation': expected_translation},
                            'obligatory': True,
                            'obligation_condition': 'cond_1',
                            'visible': True,
                            'can_be_filler': True,
                            'can_be_fillable': True,
                        },
                        {
                            'can_be_fillable': True,
                            'can_be_filler': True,
                            'code': 'registration_date',
                            'default': {
                                'datetimeValue': '2020-09-09T19:09:00+03:00',
                                'type': 'datetime',
                            },
                            'label': {'translation': 'Дата регистрации'},
                            'obligatory': False,
                            'template_id': 2,
                            'visible': True,
                        },
                    ],
                },
            ],
            'conditions': {
                'cond_1': {
                    'driver_email': {
                        '$ne': {
                            'type': 'string',
                            'stringValue': 'nevladov@yandex.ru',
                        },
                    },
                },
            },
            **kwargs,
        },
    }


def _form_2(expected_translation, **kwargs):
    data = _expected_data(expected_translation, code='form_2', **kwargs)
    data['field_templates'].pop()
    data['form']['stages'][0]['fields'].pop()
    return data


@pytest.mark.parametrize(
    'accept_language, form_code,expected_code,expected_data',
    [
        (None, 'form_1', 200, _expected_data('Электронная почта парка')),
        ('ru', 'form_1', 200, _expected_data('Электронная почта парка')),
        ('be', 'form_1', 200, _expected_data('Электронная почта парка')),
        ('ge', 'form_1', 200, _expected_data('პარკის ელ')),
        ('en', 'form_1', 200, _expected_data('Park\'s email')),
        (
            None,
            'form_2',
            200,
            _form_2('Электронная почта парка', ya_metric_counter=123),
        ),
        (
            None,
            'form_3',
            404,
            {
                'code': 'NOT_FOUND_ERROR',
                'message': 'form "form_3" is not found',
            },
        ),
    ],
)
@pytest.mark.translations(
    form_builder={
        'x.y': {
            'ru': 'Электронная почта парка',
            'en': 'Park\'s email',
            'ge': 'პარკის ელ',
        },
    },
)
async def test_forms_get(
        taxi_form_builder_web,
        accept_language,
        form_code,
        expected_code,
        expected_data,
):
    headers = {}
    if accept_language:
        headers['Accept-Language'] = accept_language
    response = await taxi_form_builder_web.get(
        '/v1/view/forms/', headers=headers, params={'code': form_code},
    )
    assert response.status == expected_code
    data = await response.json()
    if expected_data is not None:
        assert data == expected_data
