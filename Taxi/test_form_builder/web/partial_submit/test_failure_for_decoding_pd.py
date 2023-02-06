import pytest

from form_builder.crontasks import stages_submitter
from form_builder.utils import submitter


@pytest.mark.config(
    TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}],
    TVM_SERVICES={'personal': 2020260},
)
@pytest.mark.usefixtures('cached_personal_mock')
@pytest.mark.parametrize(
    (
        'templates_data_json,'
        'form_data_json,'
        'request_data_json,'
        'submit_queue_data_json'
    ),
    [
        (
            'field_templates_1.json',
            'form_data_1.json',
            'submit_form_data_1.json',
            'submit_queue_data_1.json',
        ),
    ],
)
async def test_partial_submit(
        load_json,
        cron_context,
        create_templates,
        create_form,
        submit_form,
        templates_data_json,
        form_data_json,
        request_data_json,
        submit_queue_data_json,
):
    await create_templates(load_json(templates_data_json))
    form_code = await create_form(load_json(form_data_json))
    await submit_form(
        form_code, load_json(request_data_json), partial=True, submit_id='abc',
    )

    submitter_processor = stages_submitter.Processor(cron_context)
    chunk = await submitter_processor.get_chunk()
    items = await submitter_processor.build_items(chunk)
    assert {
        y.key: y.value.data
        for x in items
        for y in x.response_data.response_values
    } == load_json(submit_queue_data_json)

    requests = [
        await submitter.Request.build(
            cron_context, x.submit_options, x.response_data,
        )
        for x in items
    ]
    assert [{'content-type': 'application/json', 'some': 'abc'}] == [
        x.headers for x in requests
    ]
