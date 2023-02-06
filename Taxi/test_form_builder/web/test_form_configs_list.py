import pytest


FORM_CONFIG_1 = {
    'authorization': {'passport': False, 'opteum': False},
    'submit_options': [],
    'form': {
        'default_locale': 'ru',
        'supported_locales': ['ru', 'en'],
        'code': 'form_1',
        'ya_metric_counter': 62138506,
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
        'stages': [
            {
                'fields': [
                    {
                        'code': 'field_1',
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'label': {
                            'tanker_key': '',
                            'static_value': 'e-mail водителя',
                        },
                        'obligation_condition': 'cond_1',
                        'can_be_filler': True,
                        'can_be_fillable': True,
                    },
                    {
                        'code': 'field_2',
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'label': {
                            'tanker_key': '',
                            'static_value': 'e-mail водителя',
                        },
                        'obligation_condition': 'cond_1',
                        'can_be_filler': True,
                        'can_be_fillable': True,
                    },
                    {
                        'code': 'field_3',
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'label': {
                            'tanker_key': '',
                            'static_value': 'e-mail водителя',
                        },
                        'obligation_condition': 'cond_1',
                        'can_be_filler': True,
                        'can_be_fillable': True,
                    },
                    {
                        'code': 'field_4',
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'label': {
                            'tanker_key': '',
                            'static_value': 'e-mail водителя',
                        },
                        'obligation_condition': 'cond_1',
                        'can_be_filler': True,
                        'can_be_fillable': True,
                    },
                    {
                        'can_be_fillable': False,
                        'can_be_filler': False,
                        'default': {
                            'datetimeValue': '2020-09-09T19:09:00+03:00',
                            'type': 'datetime',
                        },
                        'label': {'static_value': 'label', 'tanker_key': ''},
                        'obligation_condition': 'cond_1',
                        'obligatory': True,
                        'template_id': 2,
                        'visible': True,
                    },
                ],
            },
            {
                'fields': [
                    {
                        'code': 'field_5',
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'label': {
                            'tanker_key': '',
                            'static_value': 'e-mail водителя',
                        },
                        'obligation_condition': 'cond_1',
                        'can_be_filler': True,
                        'can_be_fillable': True,
                    },
                ],
            },
        ],
    },
    'submit_limit': {'field_code': 'field_1', 'max_count': 100500},
    'author': 'author_1',
    'created': '2020-03-11T13:00:00+03:00',
}


FORM_CONFIG_2 = {
    'authorization': {'passport': False, 'opteum': False},
    'submit_options': [],
    'form': {
        'default_locale': 'ru',
        'supported_locales': ['ru', 'en'],
        'code': 'form_2',
        'ya_metric_counter': 62138506,
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
        'stages': [
            {
                'fields': [
                    {
                        'code': 'field_6',
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'label': {
                            'tanker_key': '',
                            'static_value': 'e-mail водителя',
                        },
                        'obligation_condition': 'cond_1',
                        'can_be_fillable': True,
                        'can_be_filler': True,
                    },
                    {
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'label': {'tanker_key': '', 'static_value': 'label'},
                        'obligation_condition': 'cond_1',
                        'can_be_filler': False,
                        'can_be_fillable': False,
                    },
                ],
            },
        ],
    },
    'submit_limit': {'field_code': 'field_2', 'max_count': 250},
    'author': 'author_2',
    'created': '2020-03-11T13:00:00+03:00',
}


@pytest.mark.parametrize(
    'params,expected_data',
    [
        ({}, {'form_configs': [FORM_CONFIG_2, FORM_CONFIG_1], 'min_id': 100}),
        ({'author': ''}, {'form_configs': []}),
        (
            {'author': 'author_1'},
            {'form_configs': [FORM_CONFIG_1], 'min_id': 100},
        ),
        ({'limit': 1}, {'form_configs': [FORM_CONFIG_2], 'min_id': 101}),
        (
            {'less_than_id': 101},
            {'form_configs': [FORM_CONFIG_1], 'min_id': 100},
        ),
        (
            {'code': 'fo'},
            {'form_configs': [FORM_CONFIG_2, FORM_CONFIG_1], 'min_id': 100},
        ),
        ({'code': 'form_1'}, {'form_configs': [FORM_CONFIG_1], 'min_id': 100}),
    ],
)
async def test_forms_configs_list(
        taxi_form_builder_web, params, expected_data,
):
    response = await taxi_form_builder_web.get(
        '/v1/builder/form-configs/list/', params=params,
    )
    assert response.status == 200
    data = await response.json()
    if expected_data is not None:
        assert data == expected_data
