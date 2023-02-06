# pylint: disable=redefined-outer-name
import dataclasses

import pytest


def _number(value: float):
    return {'type': 'number', 'numberValue': value}


def _string(value: str):
    return {'type': 'string', 'stringValue': value}


def _file(value: str):
    return {'type': 'file', 'fileValue': value}


def _datetime(value: str):
    return {'type': 'datetime', 'datetimeValue': value}


def _array_value(*values):
    return {'type': 'array', 'arrayValue': list(values)}


@pytest.fixture()
def get_form(taxi_form_builder_web):
    async def _do_it(form_code: str, submit_id: str):
        _response = await taxi_form_builder_web.get(
            '/v1/view/forms/',
            params={'code': form_code, 'submit_id': submit_id},
            headers={'Accept-Language': 'ru'},
        )
        assert _response.status == 200, await _response.text()
        return await _response.json()

    return _do_it


@dataclasses.dataclass(frozen=True)
class PartialCheck:
    empty: bool = False
    overrides: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class ExternalCheck:
    empty: bool = False
    data: dict = dataclasses.field(default_factory=dict)


@pytest.fixture
def check_form(get_form):
    async def _do_it(
            submit_id,
            partial_check: PartialCheck = PartialCheck(),
            external_check: ExternalCheck = ExternalCheck(empty=True),
    ):
        form = await get_form('form_1', submit_id)
        if partial_check.empty:
            assert form.get('partial') is None, 'forms partial is not empty'
        else:
            assert form.get('partial') == {
                'field_1': _string('abc'),
                'field_2': _string('+79999999999'),
                **partial_check.overrides,
            }, 'forms partial differs'
        if external_check.empty:
            assert (
                form.get('external_sources') is None
            ), 'forms external sources are not empty'
        else:
            assert (
                form['external_sources'] == external_check.data
            ), 'external sources differs'

    return _do_it


@pytest.fixture
def check_count(web_context):
    async def _do_it(
            table_name, count, *, schema_name='form_builder', condition=None,
    ):
        query = f'SELECT count(*) FROM {schema_name}.{table_name}'
        if condition:
            query += f' WHERE {condition}'
        _count = await web_context.pg.primary.fetchval(query)
        assert _count == count, table_name

    return _do_it


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('cached_personal_mock')
@pytest.mark.parametrize(
    'form_code, submit_id, expected_code, saved_count',
    [
        pytest.param('form_1', 'abc', 200, 2, id='override-existing'),
        pytest.param('form_1', 'zbc', 200, 3, id='add-new-submit_id'),
        pytest.param('form_2', 'abc', 404, 2, id='no-form_no-add'),
    ],
)
async def test_save(
        taxi_form_builder_web,
        check_count,
        form_code,
        submit_id,
        expected_code,
        saved_count,
):
    _response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/partial/',
        params={'code': form_code, 'submit_id': submit_id},
        json={
            'data': {
                'field_1': _string('value_1'),
                'field_2': _string('personal_id_1'),
            },
        },
    )
    assert _response.status == expected_code, await _response.text()
    await check_count(
        'responses', saved_count, condition='submit_id is not null',
    )


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('cached_personal_mock')
@pytest.mark.parametrize(
    'submit_id, expected_partial_data',
    [
        ('abc', {'field_1': _string('abc'), 'field_2': _string('B')}),
        ('abd', {'field_1': _string('abc')}),
        ('abz', None),
        (None, None),
    ],
)
async def test_fetch(get_form, submit_id, expected_partial_data):
    form = await get_form('form_1', submit_id)
    assert form.get('partial') == expected_partial_data


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
async def test_save_and_fetch(
        taxi_form_builder_web, cached_personal_mock, check_count, check_form,
):
    cached_personal_mock['phones'].store_with_id(
        '+79999999999', 'personal_id_1',
    )
    await check_form('abc')
    _response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/partial/',
        params={'code': 'form_1', 'submit_id': 'abc'},
        json={
            'data': {
                'field_1': _string('value_1'),
                'field_2': _string('+79999999999'),
                'number_field': _number(1),
                'numbers_field': _array_value(_number(1), _number(2.0)),
            },
            'external_sources': {'field_1': {'uniq_id': 'abc'}},
        },
    )
    assert _response.status == 200, await _response.text()
    await check_count('metas', 1, schema_name='caches')

    await check_form(
        'abc',
        PartialCheck(
            overrides=dict(
                field_1=_string('value_1'),
                number_field=_number(1),
                numbers_field=_array_value(_number(1), _number(2.0)),
            ),
        ),
        ExternalCheck(data={'field_1': {'uniq_id': 'abc'}}),
    )


def case(
        submit_id: str,
        *,
        extra_payload=None,
        partials_overrides=None,
        counts_after_partial_submit: dict,
        counts_after_complete_submit: dict,
        with_partial_submit_options=False,
):
    return (
        submit_id,
        extra_payload or {},
        partials_overrides or {},
        counts_after_partial_submit,
        counts_after_complete_submit,
        with_partial_submit_options,
    )


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('territories_mock')
@pytest.mark.parametrize(
    (
        'submit_id,'
        'extra_payload,'
        'partials_overrides,'
        'counts_after_partial_submit,'
        'counts_after_complete_submit,'
        'with_partial_submit_options'
    ),
    [
        case(
            'abc',
            counts_after_partial_submit={
                'response_values': 8,
                'request_queue': 0,
                'partial_request_queue': 0,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 8,
                'request_queue': 1,
                'partial_request_queue': 0,
                'responses': {
                    'count': 1,
                    'condition': 'submit_id is not null',
                },
            },
        ),
        case(
            'abc',
            counts_after_partial_submit={
                'response_values': 12,
                'request_queue': 0,
                'partial_request_queue': 1,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 16,
                'request_queue': 1,
                'partial_request_queue': 1,
                'responses': {
                    'count': 1,
                    'condition': 'submit_id is not null',
                },
            },
            with_partial_submit_options=True,
        ),
        case(
            'abz',
            partials_overrides={'empty': True},
            counts_after_partial_submit={
                'response_values': 10,
                'request_queue': 0,
                'partial_request_queue': 0,
                'responses': {
                    'count': 3,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 10,
                'request_queue': 1,
                'partial_request_queue': 0,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
        ),
        case(
            'abz',
            partials_overrides={'empty': True},
            counts_after_partial_submit={
                'response_values': 14,
                'request_queue': 0,
                'partial_request_queue': 1,
                'responses': {
                    'count': 3,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 18,
                'request_queue': 1,
                'partial_request_queue': {
                    'count': 1,
                    'condition': 'stage_num = 1',
                },
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            with_partial_submit_options=True,
        ),
        case(
            'aaa',
            extra_payload={
                'file_field': _file('YWJjZA=='),
                'dt_field': _datetime('2020-03-02T14:00:00+03:00'),
                'array_field': _array_value(_string('A'), _string('B')),
            },
            partials_overrides=[
                {'empty': True},
                {
                    'file_field': _file('YWJjZA=='),
                    'dt_field': _datetime('2020-03-02T14:00:00+03:00'),
                    'array_field': _array_value(_string('A'), _string('B')),
                },
            ],
            counts_after_partial_submit={
                'response_values': 10,
                'request_queue': 0,
                'partial_request_queue': 0,
                'responses': {
                    'count': 3,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 10,
                'request_queue': 1,
                'partial_request_queue': 0,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
        ),
        case(
            'aaa',
            extra_payload={
                'file_field': _file('YWJjZA=='),
                'dt_field': _datetime('2020-03-02T14:00:00+03:00'),
                'array_field': _array_value(_string('A'), _string('B')),
            },
            partials_overrides=[
                {'empty': True},
                {
                    'file_field': _file('YWJjZA=='),
                    'dt_field': _datetime('2020-03-02T14:00:00+03:00'),
                    'array_field': _array_value(_string('A'), _string('B')),
                },
            ],
            counts_after_partial_submit={
                'response_values': 14,
                'request_queue': 0,
                'partial_request_queue': 1,
                'responses': {
                    'count': 3,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 18,
                'request_queue': 1,
                'partial_request_queue': 1,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            with_partial_submit_options=True,
        ),
        case(
            'only_1_stage_submits',
            extra_payload={'number_field': _number(1)},
            partials_overrides=[{'empty': True}, {'number_field': _number(1)}],
            counts_after_partial_submit={
                'response_values': 14,
                'request_queue': 0,
                'partial_request_queue': 1,
                'responses': {
                    'count': 3,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 18,
                'request_queue': 1,
                'partial_request_queue': {
                    'count': 1,
                    'condition': 'stage_num = 1',
                },
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            with_partial_submit_options=True,
        ),
    ],
)
async def test_partial_submit_and_completed(
        web_context,
        taxi_form_builder_web,
        cached_personal_mock,
        mk_state,
        check_count,
        check_form,
        submit_id,
        extra_payload,
        partials_overrides,
        counts_after_partial_submit,
        counts_after_complete_submit,
        with_partial_submit_options,
):
    cached_personal_mock['phones'].store_with_id(
        '+79999999999', 'personal_id_1',
    )

    await mk_state(
        form_code='form_1',
        field_code='field_2',
        submit_id=submit_id,
        value={'type': 'string', 'stringValue': 'personal_id_1'},
        is_sent=True,
        is_valid=True,
    )

    if with_partial_submit_options:
        await web_context.pg.primary.execute(
            """
            INSERT INTO form_builder.partial_submit_options
                (stage_id, method, url)
            VALUES (1, 'POST', 'tst');
            """,
        )
    await check_count('response_values', 3)
    await check_count('metas', 0, schema_name='caches')
    if isinstance(partials_overrides, list):
        await check_form(submit_id, PartialCheck(**partials_overrides[0]))
    else:
        await check_form(submit_id, PartialCheck(**partials_overrides))
    _response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/partial/',
        params={'code': 'form_1', 'submit_id': submit_id},
        json={
            'data': {
                'field_1': _string('value_1'),
                'field_2': _string('+79999999999'),
                **extra_payload,
            },
            'external_sources': {'field_1': {'uniq_id': '1-en'}},
        },
    )
    assert _response.status == 200, await _response.text()
    await check_count('metas', 1, schema_name='caches')

    if isinstance(partials_overrides, list):
        await check_form(
            submit_id,
            PartialCheck(
                overrides={
                    'field_1': _string('value_1'),
                    **(partials_overrides[1]),
                },
            ),
            ExternalCheck(data={'field_1': {'uniq_id': '1-en'}}),
        )
    else:
        await check_form(
            submit_id,
            PartialCheck(overrides={'field_1': _string('value_1')}),
            ExternalCheck(data={'field_1': {'uniq_id': '1-en'}}),
        )
    for table_name, count in counts_after_partial_submit.items():
        if isinstance(count, dict):
            await check_count(
                table_name, count['count'], condition=count['condition'],
            )
        else:
            await check_count(table_name, count)

    _response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/',
        params={'code': 'form_1', 'submit_id': submit_id},
        json={
            'data': {
                'field_1': _string('value_1'),
                'field_2': _string('+79999999999'),
                **extra_payload,
            },
            'external_sources': {'field_1': {'uniq_id': '1-en'}},
        },
    )
    assert _response.status == 200, await _response.text()
    await check_form(
        submit_id, PartialCheck(empty=True), ExternalCheck(empty=True),
    )
    for table_name, count in counts_after_complete_submit.items():
        if isinstance(count, dict):
            await check_count(
                table_name, count['count'], condition=count['condition'],
            )
        else:
            await check_count(table_name, count)
    await check_count('metas', 0, schema_name='caches')


def _case(
        submit_id: str,
        *,
        extra_payload=None,
        partials_overrides=None,
        counts_after_partial_submit: dict,
        counts_after_complete_submit: dict,
        with_partial_submit_options=False,
        partial_status_code=200,
        partial_response_body=None,
        final_status_code=200,
        final_response_body=None,
):
    return (
        submit_id,
        extra_payload or {},
        partials_overrides or {},
        counts_after_partial_submit,
        counts_after_complete_submit,
        with_partial_submit_options,
        partial_status_code,
        partial_response_body or {},
        final_status_code,
        final_response_body or {},
    )


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('cached_personal_mock')
@pytest.mark.parametrize(
    (
        'submit_id,'
        'extra_payload,'
        'partials_overrides,'
        'counts_after_partial_submit,'
        'counts_after_complete_submit,'
        'with_partial_submit_options,'
        'partial_status_code,'
        'partial_response_body,'
        'final_status_code,'
        'final_response_body,'
    ),
    [
        _case(
            'verification-fail',
            partials_overrides={'empty': True},
            counts_after_partial_submit={
                'response_values': 3,
                'request_queue': 0,
                'partial_request_queue': 0,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 3,
                'request_queue': 0,
                'partial_request_queue': 0,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            partial_status_code=400,
            partial_response_body={
                'code': 'VALIDATION_ERROR',
                'message': '"sms_validator" verification not passed',
            },
            final_status_code=400,
            final_response_body={
                'code': 'VALIDATION_ERROR',
                'message': '"sms_validator" verification not passed',
            },
        ),
        _case(
            'verification-not-sent',
            partials_overrides={'empty': True},
            counts_after_partial_submit={
                'response_values': 3,
                'request_queue': 0,
                'partial_request_queue': 0,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            counts_after_complete_submit={
                'response_values': 3,
                'request_queue': 0,
                'partial_request_queue': 0,
                'responses': {
                    'count': 2,
                    'condition': 'submit_id is not null',
                },
            },
            partial_status_code=400,
            partial_response_body={
                'code': 'VALIDATION_ERROR',
                'message': '"sms_validator" verification not passed',
            },
            final_status_code=400,
            final_response_body={
                'code': 'VALIDATION_ERROR',
                'message': '"sms_validator" verification not passed',
            },
        ),
    ],
)
async def test_failed_partial_submit_and_completed(
        web_context,
        taxi_form_builder_web,
        check_count,
        check_form,
        submit_id,
        extra_payload,
        partials_overrides,
        counts_after_partial_submit,
        counts_after_complete_submit,
        with_partial_submit_options,
        partial_status_code,
        partial_response_body,
        final_status_code,
        final_response_body,
):

    await check_count('response_values', 3)
    await check_count('metas', 0, schema_name='caches')
    if isinstance(partials_overrides, list):
        await check_form(submit_id, PartialCheck(**partials_overrides[0]))
    else:
        await check_form(submit_id, PartialCheck(**partials_overrides))
    _response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/partial/',
        params={'code': 'form_1', 'submit_id': submit_id},
        json={
            'data': {
                'field_1': _string('value_1'),
                'field_2': _string('B'),
                **extra_payload,
            },
            'external_sources': {'field_1': {'uniq_id': '1-en'}},
        },
    )
    assert _response.status == partial_status_code, await _response.text()
    assert await _response.json() == partial_response_body
    await check_count('metas', 0, schema_name='caches')

    if isinstance(partials_overrides, list):
        await check_form(
            submit_id,
            PartialCheck(
                overrides={
                    'field_1': _string('value_1'),
                    **(partials_overrides[1]),
                },
            ),
            ExternalCheck(data={'field_1': {'uniq_id': '1-en'}}),
        )
    else:
        await check_form(
            submit_id, PartialCheck(empty=True), ExternalCheck(empty=True),
        )
    for table_name, count in counts_after_partial_submit.items():
        if isinstance(count, dict):
            await check_count(
                table_name, count['count'], condition=count['condition'],
            )
        else:
            await check_count(table_name, count)

    _response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/',
        params={'code': 'form_1', 'submit_id': submit_id},
        json={
            'data': {
                'field_1': _string('value_1'),
                'field_2': _string('B'),
                **extra_payload,
            },
            'external_sources': {'field_1': {'uniq_id': '1-en'}},
        },
    )
    assert _response.status == final_status_code, await _response.text()
    assert await _response.json() == final_response_body
    await check_form(
        submit_id, PartialCheck(empty=True), ExternalCheck(empty=True),
    )
    for table_name, count in counts_after_complete_submit.items():
        if isinstance(count, dict):
            await check_count(
                table_name, count['count'], condition=count['condition'],
            )
        else:
            await check_count(table_name, count)
    await check_count('metas', 0, schema_name='caches')
