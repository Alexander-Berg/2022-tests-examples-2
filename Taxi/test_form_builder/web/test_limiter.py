import json

import asyncpg
import pytest


def _to_dict(record):
    if isinstance(record, asyncpg.Record):
        record = dict(record)
    if isinstance(record, dict):
        return {key: _to_dict(val) for key, val in record.items()}
    if isinstance(record, list):
        return [_to_dict(x) for x in record]
    if isinstance(record, str):
        try:
            return json.loads(record)
        except json.JSONDecodeError:
            return record
    return record


def _int_value(value: int):
    return {'type': 'integer', 'integerValue': value}


def _str_value(value: str):
    return {'type': 'string', 'stringValue': value}


def _translation(**kwargs):
    return {'tanker_key': '', 'static_value': 'x', **kwargs}


def _submit_options(**kwargs):
    return {
        'method': 'POST',
        'url': 'http://form-builder.taxi.yandex.net',
        'tvm_service_id': '12345',
        'body_template': '',
        'headers': [{'name': 'test', 'value': 'test'}],
        'is_multipart': False,
        **kwargs,
    }


def _form(*stages, submit_options=None, submit_limit=None, **kwargs):
    return {
        'form': {
            'default_locale': 'ru',
            'supported_locales': ['ru', 'en'],
            'code': 'form_2',
            'title': _translation(),
            'description': _translation(),
            'stages': list(stages),
            'conditions': {},
            'ya_metric_counter': 62138506,
            **kwargs,
        },
        'submit_options': (
            submit_options if submit_options else [_submit_options()]
        ),
        'submit_limit': submit_limit,
    }


def _stage(*fields, **kwargs):
    return {
        'title': _translation(),
        'description': _translation(),
        'fields': list(fields),
        **kwargs,
    }


def _field(**kwargs):
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


@pytest.fixture(name='submit')
def _submit(taxi_form_builder_web):
    async def _do_it(expected_code=200, clid_value=None):
        response = await taxi_form_builder_web.post(
            '/v1/view/forms/submit/',
            params={'code': 'form_2'},
            json={
                'data': {
                    'driver_email': _str_value('aaaa'),
                    'clid': clid_value or _str_value('abc'),
                },
            },
        )
        assert response.status == expected_code, await response.text()
        return response

    return _do_it


@pytest.fixture(name='update_create_form')
def _update_create(taxi_form_builder_web):
    async def _do_it(
            create=False, submit_updates=None, check_field_extras=None,
    ):
        method = (
            taxi_form_builder_web.post if create else taxi_form_builder_web.put
        )
        response = await method(
            '/v1/builder/form-configs/',
            json=_form(
                _stage(
                    _field(),
                    _field(
                        code='clid',
                        visible=False,
                        **(check_field_extras or {}),
                    ),
                ),
                submit_limit={
                    'field_code': 'clid',
                    'max_count': 1,
                    **(submit_updates or {}),
                },
            ),
            headers={'X-Yandex-Login': 'd1mbas'},
        )
        assert response.status == 200, await response.text()
        return response

    return _do_it


async def test_save_n_update_limiter(
        taxi_form_builder_web, update_create_form,
):
    await update_create_form(create=True)
    response = await taxi_form_builder_web.get(
        '/v1/builder/form-configs/', params={'code': 'form_2'},
    )
    assert response.status == 200
    form = await response.json()
    assert form['submit_limit'] == {'field_code': 'clid', 'max_count': 1}

    await update_create_form(submit_updates={'max_count': 2})
    response = await taxi_form_builder_web.get(
        '/v1/builder/form-configs/', params={'code': 'form_2'},
    )
    assert response.status == 200
    form = await response.json()
    assert form['submit_limit'] == {'field_code': 'clid', 'max_count': 2}


@pytest.mark.parametrize(
    'template_id, field_value', [(1, _str_value('abc')), (3, _int_value(123))],
)
async def test_create_n_submit(
        submit, update_create_form, template_id, field_value,
):
    await update_create_form(
        create=True, check_field_extras={'template_id': template_id},
    )
    await submit(clid_value=field_value)
    await submit(429, clid_value=field_value)


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('cached_personal_mock')
async def test_submit_with_pd(web_context, submit, update_create_form):
    await update_create_form(
        create=True,
        submit_updates={'max_count': 2},
        check_field_extras={'template_id': 2},
    )
    await submit()
    await submit()

    limits = await web_context.pg.primary.fetch(
        'SELECT * FROM form_builder.limits',
    )
    assert _to_dict(limits) == [
        {'limiter': 1, 'value': 'personal_id_2', 'current_count': 2},
    ]
