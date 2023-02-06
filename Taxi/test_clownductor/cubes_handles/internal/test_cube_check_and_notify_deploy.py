import pytest


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    'data_request, content_expected, need_comment',
    [
        pytest.param(
            {
                'input_data': {
                    'lock_names': ['Deploy.taxi_test_service_stable'],
                    'release_ticket_st': 'startrack_get_ticket_response',
                },
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            {'status': 'success'},
            True,
            id='test_with_old_job',
        ),
        pytest.param(
            {
                'input_data': {
                    'lock_names': ['Deploy.taxi_non_service_yaml_stable'],
                    'release_ticket_st': 'startrack_get_ticket_response',
                },
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            {'status': 'success'},
            False,
            id='test_without_job',
        ),
    ],
)
@pytest.mark.features_on('enable_open_last_ticket_notifications')
async def test_cube_check_and_notify_deploy(
        call_cube_handle,
        staff_mockserver,
        patch,
        load_json,
        data_request,
        content_expected,
        need_comment,
):
    staff_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        mocked_file = '{}.json'.format(ticket.lower().replace('-', '_'))
        return load_json(mocked_file)

    @patch('clownductor.internal.utils.startrek.find_comment')
    async def find_comment(st_api, st_key, comment_text, problem_slug):
        assert st_api is not None
        assert st_key == 'startrack_get_ticket_response'
        assert comment_text
        assert problem_slug is None
        return None

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text, summonees):
        assert ticket == 'startrack_get_ticket_response'
        assert (
            text == 'Deployment can\'t be started because the '
            'old release ticket isn\'t closed: TAXIREL-33245'
        )
        assert len(summonees) == 1

    await call_cube_handle(
        'InternalCubeCheckAndNotifyDeployments',
        {'data_request': data_request, 'content_expected': content_expected},
    )

    if need_comment:
        assert len(_get_ticket.calls) == 1
        assert len(create_comment.calls) == 1
        assert len(find_comment.calls) == 1
    else:
        assert not _get_ticket.calls
        assert not create_comment.calls
        assert not find_comment.calls
