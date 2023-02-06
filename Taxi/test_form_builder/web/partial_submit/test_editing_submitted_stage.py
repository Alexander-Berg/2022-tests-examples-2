import pytest


@pytest.fixture(name='get_queue_items')
def _get_queue_items(web_context):
    async def _wrapper():
        return await web_context.pg.primary.fetch(
            """
            SELECT * FROM form_builder.partial_request_queue
            """,
        )

    return _wrapper


@pytest.fixture(name='update_queue_item')
def _update_queue_item(web_context):
    async def _wrapper(form_code, stage_num, submit_id, **updates):
        return await web_context.pg.primary.fetchrow(
            """
            UPDATE form_builder.partial_request_queue
            SET {}
            WHERE form_code = $1 AND stage_num = $2 AND submit_id = $3
            RETURNING *
            """.format(
                ', '.join(f'{key} = {val!r}' for key, val in updates.items()),
            ),
            form_code,
            stage_num,
            submit_id,
        )

    return _wrapper


@pytest.mark.parametrize(
    [
        'templates_data_json',
        'form_data_json',
        'request_params',
        'request_json',
        'submit_result',
        'second_time_count',
    ],
    [
        pytest.param(
            'templates_data.json',
            'form_data.json',
            {'code': 'form-1', 'submit_id': 'submit-id'},
            {
                'data': {
                    'required-field': {'type': 'string', 'stringValue': 'A'},
                },
            },
            'SUBMITTED',
            1,
            id='double submit with success submit status',
        ),
        pytest.param(
            'templates_data.json',
            'form_data.json',
            {'code': 'form-1', 'submit_id': 'submit-id'},
            {
                'data': {
                    'required-field': {'type': 'string', 'stringValue': 'A'},
                },
            },
            'FAILED',
            2,
            id='double submit with failed submit status',
        ),
    ],
)
async def test_submitted_stage_twice(
        load_json,
        taxi_form_builder_web,
        create_templates,
        create_form,
        get_queue_items,
        update_queue_item,
        templates_data_json,
        form_data_json,
        request_params,
        request_json,
        submit_result,
        second_time_count,
):
    await create_templates(load_json(templates_data_json))
    await create_form(load_json(form_data_json))
    response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/partial/',
        params=request_params,
        json=request_json,
    )
    assert response.status == 200, await response.text()

    queue_items = await get_queue_items()
    assert len(queue_items) == 1
    queue_item = queue_items[0]
    await update_queue_item(
        queue_item['form_code'],
        queue_item['stage_num'],
        queue_item['submit_id'],
        status=submit_result,
    )

    response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/partial/',
        params=request_params,
        json=request_json,
    )
    assert response.status == 200, await response.text()

    assert len(await get_queue_items()) == second_time_count
