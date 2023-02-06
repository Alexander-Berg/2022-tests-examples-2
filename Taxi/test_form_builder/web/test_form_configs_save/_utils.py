import pytest


TRANSLATIONS = pytest.mark.translations(
    form_builder={
        'x.y': {'ru': 'Привет', 'en': 'Hello'},
        'x.z': {'en': 'Hello', 'ge': 'გამარჯობა'},
    },
)


def remove_ro_fields(form_):
    return {
        **form_,
        'stages': [
            {
                **stage_,
                'fields': [
                    {
                        k: v
                        for k, v in field_.items()
                        if k not in ['can_be_filler', 'can_be_fillable']
                    }
                    for field_ in stage_['fields']
                ],
            }
            for stage_ in form_['stages']
        ],
    }


def translation(**kwargs):
    return {'tanker_key': '', 'static_value': 'x', **kwargs}


def submit_options(**kwargs):
    return {
        'method': 'POST',
        'url': 'http://form-builder.taxi.yandex.net',
        'tvm_service_id': '12345',
        'body_template': '',
        'headers': [{'name': 'test', 'value': 'test'}],
        'is_multipart': False,
        'allow_resend': False,
        **kwargs,
    }


def form(*stages, submit_options_=None, **kwargs):
    return {
        'form': {
            'default_locale': 'ru',
            'supported_locales': ['ru', 'en'],
            'code': 'form_2',
            'title': translation(),
            'description': translation(),
            'stages': list(stages),
            'conditions': {},
            'ya_metric_counter': 62138506,
            **kwargs,
        },
        'submit_options': (
            submit_options_ if submit_options_ else [submit_options()]
        ),
    }


def stage_submit_options(
        url, method, body_template, tvm_service_id=None, headers=None,
):
    return {
        'url': url,
        'method': method,
        'body_template': body_template,
        'tvm_service_id': tvm_service_id,
        'headers': headers or [],
        'allow_resend': False,
    }


def stage(*fields, **kwargs):
    return {
        'title': translation(),
        'description': translation(),
        'fields': list(fields),
        **kwargs,
    }


def field(**kwargs):
    return {
        k: v
        for k, v in {
            'code': 'driver_email',
            'template_id': 1,
            'label': {'tanker_key': '', 'static_value': 'e-mail водителя'},
            'obligatory': True,
            'visible': True,
            **kwargs,
        }.items()
        if v is not None
    }


def external_source(**kwargs):
    return kwargs


def simple_form(*fields, **kwargs):
    return form(stage(*fields), **kwargs)


def conf_field(template_id, code, can_be_filler=None, can_be_fillable=None):
    return field(
        template_id=template_id,
        code=code,
        can_be_filler=can_be_filler,
        can_be_fillable=can_be_fillable,
    )
