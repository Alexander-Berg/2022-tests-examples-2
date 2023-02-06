import pytest

from hiring_selfreg_forms.internal import tools
from hiring_selfreg_forms.stq import publish
from test_hiring_selfreg_forms import conftest

EXPECTED_YT_DATA_TABLE = 'expected_yt_data.json'
YT_STQ_TABLE = '//home/test/stq_table'


@conftest.main_configuration
async def test_task_create(stq3_context):
    data = {'name': 'Joe', 'phone': '+79210000000'}
    id_ = tools.hex_uuid()
    await publish.task(
        stq3_context,
        task_id=tools.hex_uuid(),
        ticket_data=data,
        form_completion_id=id_,
        create=True,
    )

    # Check that duplicated data is handled correctly
    await publish.task(
        stq3_context,
        task_id=tools.hex_uuid(),
        ticket_data=data,
        form_completion_id=id_,
        create=True,
    )


@conftest.main_configuration
async def test_task_update(
        stq3_context, perform_auth,
):  # pylint: disable=W0621
    data = {'rent': True, 'sex': 'shemale'}
    id_ = await perform_auth()
    await publish.task(
        stq3_context,
        task_id=tools.hex_uuid(),
        ticket_data=data,
        form_completion_id=id_,
        create=False,
    )


@conftest.main_configuration
@pytest.mark.config(HIRING_FAILED_STQ_TABLE_PATH=YT_STQ_TABLE)
@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.parametrize('use_hiring_api', [True, False])
async def test_task_should_call_correct_api_on_create(
        infranaim_api,
        hiring_api,
        stq3_context,
        perform_auth,
        use_hiring_api,
        load_json,
        yt_client,
):
    data = {'rent': True, 'sex': 'shemale'}
    id_ = await perform_auth(id_=conftest.DEFAULT_FORM_COMPLETION_ID)
    stq3_context.config.HIRING_SELFREG_FORMS_MOVE_TO_SALESFORCE_SETTINGS[
        'use_hiring_api'
    ] = use_hiring_api

    await publish.task(
        stq3_context,
        task_id=tools.hex_uuid(),
        ticket_data=data,
        form_completion_id=id_,
        create=True,
    )
    if use_hiring_api:
        assert hiring_api.create.times_called == 1
        assert hiring_api.update.times_called == 0
        assert infranaim_api.post_submit.times_called == 0
        assert infranaim_api.post_update.times_called == 0
    else:
        assert infranaim_api.post_submit.times_called == 1
        assert infranaim_api.post_update.times_called == 0
        assert hiring_api.create.times_called == 0
        assert hiring_api.update.times_called == 0

    if use_hiring_api:
        await publish.task(
            stq3_context,
            task_id=tools.hex_uuid(),
            ticket_data=data,
            form_completion_id=id_,
            create=True,
        )
        expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)
        rows = list(yt_client.read_table(YT_STQ_TABLE))
        assert rows == expected_yt_data


@pytest.mark.client_experiments3(
    consumer='hiring-selfreg-forms/endpoints',
    experiment_name='selfreg_forms_endpoints',
    args=[{'name': 'form_completion_id', 'type': 'string', 'value': ''}],
    value={'endpoint': 'selfreg-forms'},
)
@pytest.mark.client_experiments3(
    consumer='hiring-selfreg-forms/endpoints',
    experiment_name='selfreg_forms_endpoints',
    args=[
        {
            'name': 'phone_pd_id',
            'type': 'string',
            'value': 'aaaaaaaabbbb4cccddddeeeeeeeeeeee',
        },
        {
            'name': 'form_completion_id',
            'type': 'string',
            'value': '61fdabf83a0940d0b199768689b3ae32',
        },
        {'name': 'source', 'type': 'string', 'value': 'some-source'},
        {
            'name': 'advertisement_campaign',
            'type': 'string',
            'value': 'some-advertisement_campaign',
        },
    ],
    value={'endpoint': 'selfreg-forms-salesforce'},
)
@pytest.mark.parametrize(
    'use_hiring_api, use_hiring_candidates, force_use_hiring_api,'
    'ticket_id, lead_id, lead_id_from_hiring_candidates,'
    'call_hiring_api, call_infranaim_api',
    [
        [True, False, False, None, None, None, False, False],
        [True, False, False, None, None, '12', False, False],
        [True, False, False, None, '12', None, True, False],
        [True, False, False, 1, None, '12', True, False],
        [True, False, False, 1, None, '12', True, False],
        [True, False, False, 1, '12', None, True, False],
        [True, False, True, None, None, None, False, False],
        [True, False, True, None, None, '12', False, False],
        [True, False, True, None, '12', None, True, False],
        [True, False, True, 1, None, None, False, False],
        [True, False, True, 1, None, '12', False, False],
        [True, False, True, 1, '12', None, True, False],
        [True, True, False, None, None, None, False, False],
        [True, True, False, None, None, '12', True, False],
        [True, True, False, None, '12', None, True, False],
        [True, True, False, 1, None, None, True, False],
        [True, True, False, 1, None, '12', True, False],
        [True, True, False, 1, '12', None, True, False],
        [True, True, True, None, None, None, False, False],
        [True, True, True, None, None, '12', True, False],
        [True, True, True, None, '12', None, True, False],
        [True, True, True, 1, None, None, False, False],
        [True, True, True, 1, None, '12', True, False],
        [True, True, True, 1, '12', None, True, False],
        [False, False, False, None, None, None, False, False],
        [False, False, False, None, None, '12', False, False],
        [False, False, False, None, '12', None, False, False],
        [False, False, False, 1, None, None, False, True],
        [False, False, False, 1, None, '12', False, True],
        [False, False, False, 1, '12', None, False, True],
        [False, False, True, None, None, None, False, False],
        [False, False, True, None, None, '12', False, False],
        [False, False, True, None, '12', None, False, False],
        [False, False, True, 1, None, None, False, True],
        [False, False, True, 1, None, '12', False, True],
        [False, False, True, 1, '12', None, False, True],
        [False, True, False, None, None, None, False, False],
        [False, True, False, None, None, '12', False, False],
        [False, True, False, None, '12', None, False, False],
        [False, True, False, 1, None, None, False, True],
        [False, True, False, 1, None, '12', False, True],
        [False, True, False, 1, '12', None, False, True],
        [False, True, True, None, None, None, False, False],
        [False, True, True, None, None, '12', False, False],
        [False, True, True, None, '12', None, False, False],
        [False, True, True, 1, None, None, False, True],
        [False, True, True, 1, None, '12', False, True],
        [False, True, True, 1, '12', None, False, True],
    ],
)
@conftest.main_configuration
async def test_task_should_call_hiring_candidates(
        use_hiring_api,
        use_hiring_candidates,
        force_use_hiring_api,
        ticket_id,
        lead_id,
        lead_id_from_hiring_candidates,
        call_hiring_api,
        call_infranaim_api,
        infranaim_api,
        hiring_api,
        stq3_context,
        perform_auth,
        pgsql,
        mock_hiring_candidates_py3,
        fill_form_data,
):
    @mock_hiring_candidates_py3('/v1/leads/list')
    def mock_leads_list(request):  # pylint: disable=W0612
        leads = []
        if lead_id_from_hiring_candidates:
            leads.append(
                {'lead_id': lead_id_from_hiring_candidates, 'fields': []},
            )

        return {'leads': leads, 'is_bounded_by_limit': False}

    data = {
        'rent': True,
        'sex': 'shemale',
        'external_id': conftest.DEFAULT_FORM_COMPLETION_ID,
    }
    id_ = await perform_auth(id_=conftest.DEFAULT_FORM_COMPLETION_ID)
    stq3_context.config.HIRING_SELFREG_FORMS_MOVE_TO_SALESFORCE_SETTINGS = {
        'use_hiring_api': use_hiring_api,
        'use_hiring_candidates': use_hiring_candidates,
        'force_use_hiring_api': force_use_hiring_api,
    }

    res = fill_form_data(
        conftest.DEFAULT_FORM_COMPLETION_ID,
        {
            'source': 'some-source',
            'advertisement_campaign': 'some-advertisement_campaign',
        },
    )
    assert res

    cursor = pgsql['hiring_misc'].cursor()
    if ticket_id:
        cursor.execute(
            'update hiring_selfreg_forms.forms_completion set ticket_id=%s',
            (ticket_id,),
        )
    if lead_id:
        cursor.execute(
            'update hiring_selfreg_forms.forms_completion set lead_id=%s',
            (lead_id,),
        )

    await publish.task(
        stq3_context,
        task_id=tools.hex_uuid(),
        ticket_data=data,
        form_completion_id=id_,
        create=False,
    )
    assert hiring_api.create.times_called == 0
    assert infranaim_api.post_submit.times_called == 0

    if call_hiring_api:
        assert hiring_api.update.times_called == 1
        assert (
            hiring_api.update.next_call()['request'].query['endpoint']
            == 'selfreg-forms-salesforce'
        )
    else:
        assert hiring_api.update.times_called == 0

    if call_infranaim_api:
        assert infranaim_api.post_update.times_called == 1
    else:
        assert infranaim_api.post_update.times_called == 0
