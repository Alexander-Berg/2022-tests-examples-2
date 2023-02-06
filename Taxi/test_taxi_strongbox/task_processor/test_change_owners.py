import pytest


@pytest.mark.parametrize(
    ['input_data'],
    [
        pytest.param({'secret_uuid': 'secret_uuid_1', 'new_owners': []}),
        pytest.param({'secret_uuid': 'secret_uuid_1', 'new_owners': None}),
        pytest.param(
            {'secret_uuid': 'secret_uuid_1', 'new_owners': ['deoevgen']},
        ),
        pytest.param(
            {
                'secret_uuid': 'secret_uuid_1',
                'new_abc_groups': [{'abc_id': 123}],
                'new_staff_ids': [123],
            },
        ),
    ],
)
async def test_cube_change_project(
        call_cube, web_context, input_data, vault_mockserver,
):
    vault_mockserver()
    data = await call_cube('ChangeOwnersCompletely', input_data)
    assert data == {'status': 'success'}
