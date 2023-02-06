import pytest

from hiring_selfreg_forms.internal import constants
from hiring_selfreg_forms.internal import tools
from hiring_selfreg_forms.stq import publish
from test_hiring_selfreg_forms import conftest


GET_TICKET_ID = (
    f'SELECT ticket_id '
    f'FROM hiring_selfreg_forms.forms_completion '
    f'WHERE form_completion_id=%s'
)
HIRING_API_RESPONSE = 'hiring_api_response.json'


@pytest.mark.parametrize(
    'use_external_id, external_id, ticket_id, config_switch',
    [
        [True, conftest.DEFAULT_EXTERNAL_ID, 200000, 'config_on'],
        [False, conftest.DEFAULT_FORM_COMPLETION_ID, 100000, 'config_off'],
    ],
)
@conftest.main_configuration
async def test_task_correct_id(
        stq3_context,
        perform_auth,
        mock_hiring_candidates_py3,
        hiring_api_create,
        use_external_id,
        external_id,
        ticket_id,
        config_switch,
        pgsql,
        load_json,
):  # pylint: disable=W0621
    @mock_hiring_candidates_py3('/v1/leads/list')
    def mock_leads_list(request):  # pylint: disable=W0612
        assert request.json['external_ids'][0] == external_id
        return {
            'leads': [{'lead_id': 'fewfweff34554', 'fields': []}],
            'is_bounded_by_limit': False,
        }

    mock_create = hiring_api_create(
        load_json(HIRING_API_RESPONSE)[config_switch],
    )

    data = {'rent': True, 'sex': 'shemale'}
    stq3_context.config.HIRING_SELFREG_FORMS_INFRANAIM_PATH = (
        constants.HIRING_API_SALESFORCE_ENDPOINT
    )
    stq3_context.config.HIRING_API_ENABLE_USE_NEW_EXTERNAL_ID = use_external_id
    id_ = await perform_auth(id_=conftest.DEFAULT_FORM_COMPLETION_ID)

    await publish.task(
        stq3_context,
        task_id=tools.hex_uuid(),
        ticket_data=data,
        form_completion_id=id_,
        create=True,
    )

    data = {'rent': True, 'sex': 'male'}
    await publish.task(
        stq3_context,
        task_id=tools.hex_uuid(),
        ticket_data=data,
        form_completion_id=id_,
        create=False,
    )

    assert mock_create.times_called == 1

    cursor = pgsql['hiring_misc'].cursor()
    cursor.execute(GET_TICKET_ID, (conftest.DEFAULT_FORM_COMPLETION_ID,))
    assert cursor.fetchone()[0] == ticket_id
