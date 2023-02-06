# pylint: disable=protected-access
import pathlib

import pytest

from replication.drafts import admin_run_draft


# TODO: tests on dev teams and audit id
@pytest.mark.config(
    REPLICATION_WEB_CTL={
        'admin': {
            'dev_teams_can_approve_draft': True,
            'dev_teams_can_approve_draft_names': ['change_state'],
            'force_dev_team_map': {'__default_no_team__': 'dummy'},
        },
    },
)
@pytest.mark.parametrize(
    'model_name, request_example',
    [
        (model.name, request_example)
        for model in admin_run_draft._MODELS
        for request_example in model.request_examples
    ],
)
async def test_admin_drafts_check(
        replication_ctx,
        replication_client,
        model_name: str,
        request_example: admin_run_draft.RequestExample,
):
    response = await replication_client.post(
        f'/admin/v1/drafts/check', json=request_example.body,
    )
    assert response.status == request_example.status, await response.text()

    expected_response: dict
    if response.status == 200:
        expected_response = {'data': {**request_example.body}, 'mode': 'poll'}
        dev_team = admin_run_draft.retrieve_dev_team(
            replication_ctx, request_example.body,
        )
        if dev_team is not None:
            expected_response['data']['dev_team'] = dev_team
        audit_id = admin_run_draft.retrieve_audit_id(request_example.body)
        if audit_id is not None:
            expected_response['data']['audit_id'] = audit_id
        change_doc_id = True
    else:
        expected_response = {
            'message': request_example.error_message,
            'code': 'draft-check-error',
        }
        change_doc_id = False

    response_json = await response.json()
    if change_doc_id:
        response_json.pop('change_doc_id')
    assert response_json == expected_response


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
