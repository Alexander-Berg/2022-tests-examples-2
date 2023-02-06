import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'
NOT_FOUND_NAME = 'something'


@pytest.mark.parametrize(
    'use_draft_id', [pytest.param(False), pytest.param(True)],
)
@pytest.mark.parametrize(
    'test_func,is_delete',
    [
        pytest.param(helpers.get_schema_draft, False),
        pytest.param(helpers.delete_schema_draft, True),
    ],
)
@pytest.mark.parametrize(
    'gen_func,init_func,is_config',
    [
        pytest.param(
            experiment.generate, helpers.init_exp, False, id='experiment',
        ),
        pytest.param(
            experiment.generate_config, helpers.init_config, True, id='config',
        ),
    ],
)
@pytest.mark.parametrize(
    'exp_name,create_draft,expected_status,expected_error',
    [
        pytest.param(
            NOT_FOUND_NAME, False, 404, {'code': 'SCHEMA_DRAFT_NOT_FOUND'},
        ),
        pytest.param(
            EXPERIMENT_NAME, False, 404, {'code': 'SCHEMA_DRAFT_NOT_FOUND'},
        ),
        pytest.param(EXPERIMENT_NAME, True, 200, {}),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_get_and_delete_schema_draft(
        taxi_exp_client,
        use_draft_id,
        test_func,
        is_delete,
        gen_func,
        init_func,
        is_config,
        exp_name,
        create_draft,
        expected_status,
        expected_error,
):
    # init exp/config
    experiment_body = gen_func(name=EXPERIMENT_NAME, last_modified_at=1)

    await init_func(taxi_exp_client, experiment_body)
    # create draft if needed
    if create_draft:
        await helpers.add_schema_draft(
            taxi_exp_client,
            name=EXPERIMENT_NAME,
            schema_body=experiment.DEFAULT_SCHEMA,
            is_config=is_config,
        )
    # get/delete draft
    if use_draft_id:
        response = await test_func(
            taxi_exp_client, draft_id=1 + (exp_name == NOT_FOUND_NAME),
        )
    else:
        response = await test_func(
            taxi_exp_client, name=exp_name, is_config=is_config,
        )
    # check error
    assert response.status == expected_status
    if not is_delete or expected_status != 200:
        response_body = await response.json()
        if expected_status == 200:
            assert response_body == {
                'schema_body': experiment.DEFAULT_SCHEMA,
                'draft_id': 1,
            }
        else:
            assert response_body['code'] == expected_error['code']
            if 'message' in expected_error:
                assert response_body['message'] == expected_error['message']
        return
    # if deleting, check response and that draft no longer exists
    if is_delete:
        assert (await response.json()) == {'name': EXPERIMENT_NAME}
        response = await helpers.get_schema_draft(
            taxi_exp_client, name=exp_name, is_config=is_config,
        )
        assert response.status == 404
