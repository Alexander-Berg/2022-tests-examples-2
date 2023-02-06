import pytest

from form_builder.utils import field_types as ftps


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('cached_personal_mock')
async def test_validate(test_instance, field, get_state):
    await test_instance.send(
        form_code='tst_form',
        form_values={
            'tst-field': ftps.Value({'type': 'string', 'stringValue': 'a'}),
        },
        main_field=field(code='tst-field'),
        submit_id='some',
        locale='ru',
        x_remote_ip=None,
    )
    state = await get_state('tst_form', 'tst-field', 'some')
    assert state.is_valid is None

    result = await test_instance.verify(
        form_code='tst_form',
        form_values={
            'tst-field': ftps.Value({'type': 'string', 'stringValue': 'a'}),
        },
        main_field=field(code='tst-field'),
        submit_id='some',
        value=ftps.Value(data={}),
        locale='ru',
        x_remote_ip=None,
    )
    state = await get_state('tst_form', 'tst-field', 'some')
    assert state.is_valid is result.is_valid
