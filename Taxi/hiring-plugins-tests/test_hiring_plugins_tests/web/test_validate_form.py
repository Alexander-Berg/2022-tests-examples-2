import typing

import pytest


async def test_happy_path(
        hiring_forms_mockserver,
        wait_until_ready,
        validate_form,
        get_hiring_forms_fields,
):
    await wait_until_ready()
    fields = get_hiring_forms_fields('valid_form', 'valid_filling')
    response = await validate_form(fields)
    assert response.status == 200


@pytest.mark.parametrize(
    'field_name, field_value, error_code',
    [
        ('required_string_with_two_values', 'third', 'NOT_IN_ENUM'),
        ('optional_boolean', 'true', 'EXPECTED_YES_NO'),
        ('you_cannot_reject_it', 'no', 'NOT_IN_ENUM'),
        ('integer_field', 'notint', 'EXPECTED_INTEGER'),
        ('bytes_field', 'xdf', 'INVALID_VALUE'),
        ('unkwnown_field', 'xdf', 'UNKNOWN_FIELD'),
    ],
)
async def test_invalid_values(
        field_name,
        field_value,
        error_code,
        hiring_forms_mockserver,
        wait_until_ready,
        validate_form,
        get_hiring_forms_fields,
):
    await wait_until_ready()
    fields = get_hiring_forms_fields('valid_form', 'valid_filling')
    _replace_or_add_field(fields, field_name, field_value)
    response = await validate_form(fields)
    assert response.status == 400
    body = await response.json()
    errors = [
        (obj['field_name'], obj['code'])
        for obj in body['details']['invalid_filled_fields']
    ]
    assert (field_name, error_code) in errors


@pytest.mark.config(HIRING_FORMS_DEFAULT_LANGUAGE='ru')
@pytest.mark.config(HIRING_FORMS_SUPPORTED_LANGUAGES=['ru', 'en'])
@pytest.mark.translations(
    hiring_forms={
        'backend.unknown_field': {
            'ru': 'Русский',
            'en': 'English',
            'fr': 'French?',
        },
    },
)
@pytest.mark.parametrize(
    'accept_language, message',
    [
        ('ru-RU', 'Русский'),
        ('en-US', 'English'),
        ('fr-US', 'Русский'),  # not supported, take default
    ],
)
async def test_translations(
        accept_language,
        message,
        hiring_forms_mockserver,
        wait_until_ready,
        validate_form,
        get_hiring_forms_fields,
):
    await wait_until_ready()
    (dummy_fields, invalid_filled_fields) = await _get_duplicate_errors(
        get_hiring_forms_fields, validate_form, accept_language,
    )
    error = invalid_filled_fields[0]
    # TODO(dmkurilov)  https://st.yandex-team.ru/TAXITOOLS-833
    assert error['message'] != message


async def test_hardcoded_translations(
        hiring_forms_mockserver,
        wait_until_ready,
        validate_form,
        get_hiring_forms_fields,
):
    await wait_until_ready()
    (dummy_fields, invalid_filled_fields) = await _get_duplicate_errors(
        get_hiring_forms_fields, validate_form,
    )
    error = invalid_filled_fields[0]
    assert error['message'] == 'Field meets twice or more, must be unique'


@pytest.mark.config(HIRING_FORMS_SUPPORTED_LANGUAGES=['en'])
@pytest.mark.config(HIRING_FORMS_DEFAULT_LANGUAGE='en')
@pytest.mark.translations(
    hiring_forms={
        'backend.not_in_enum': {'en': 'String with %(missing)s kwarg'},
    },
)
async def test_missing_arguments(
        hiring_forms_mockserver,
        wait_until_ready,
        validate_form,
        get_hiring_forms_fields,
):
    await wait_until_ready()
    error = await _get_not_in_enum_error(
        validate_form, get_hiring_forms_fields,
    )
    tanker_key = 'backend.not_in_enum'
    # TODO(dmkurilov)  https://st.yandex-team.ru/TAXITOOLS-833
    assert error['message'] != tanker_key


@pytest.mark.config(HIRING_FORMS_SUPPORTED_LANGUAGES=['en'])
@pytest.mark.config(HIRING_FORMS_DEFAULT_LANGUAGE='en')
@pytest.mark.translations(
    hiring_forms={
        'backend.not_in_enum': {'en': 'String with %(broken) kwarg'},
    },
)
async def test_broken_arguments(
        hiring_forms_mockserver,
        wait_until_ready,
        validate_form,
        get_hiring_forms_fields,
):
    await wait_until_ready()
    error = await _get_not_in_enum_error(
        validate_form, get_hiring_forms_fields,
    )
    tanker_key = 'backend.not_in_enum'
    # TODO(dmkurilov)  https://st.yandex-team.ru/TAXITOOLS-833
    assert error['message'] != tanker_key


async def test_duplicate(
        hiring_forms_mockserver,
        wait_until_ready,
        validate_form,
        get_hiring_forms_fields,
):
    await wait_until_ready()
    (fields, invalid_filled_fields) = await _get_duplicate_errors(
        get_hiring_forms_fields, validate_form,
    )
    error = invalid_filled_fields[0]
    assert error['code'] == 'DUPLICATE_FIELD'
    assert error['fields_list_index'] == len(fields) - 1


def _replace_or_add_field(
        fields: typing.List[dict], field_name: str, field_value: str,
):
    for obj in fields:
        if obj['field_name'] == field_name:
            obj['field_value'] = field_value
            return
    fields.append({'field_name': field_name, 'field_value': field_value})


async def _get_duplicate_errors(
        get_hiring_forms_fields, validate_form, accept_language='ru',
):
    fields = get_hiring_forms_fields('valid_form', 'valid_filling')
    fields.append(fields[0].copy())
    response = await validate_form(fields)
    assert response.status == 400
    body = await response.json()
    return (fields, body['details']['invalid_filled_fields'])


async def _get_not_in_enum_error(validate_form, get_hiring_forms_fields):
    fields = get_hiring_forms_fields('valid_form', 'valid_filling')
    _replace_or_add_field(fields, 'you_cannot_reject_it', 'no')
    response = await validate_form(fields, 'en')
    assert response.status == 400
    body = await response.json()
    error = body['details']['invalid_filled_fields'][0]
    return error
