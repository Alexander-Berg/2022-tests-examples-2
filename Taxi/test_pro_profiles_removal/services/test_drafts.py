from testsuite.utils import http

from pro_profiles_removal.generated.cron import cron_context as context
from pro_profiles_removal.services import drafts as drafts_service


async def test_create_draft_ok(
        cron_context: context.Context, mock_taxi_approvals,
):
    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft(request: http.Request):
        assert request.json == {
            'service_name': 'pro-profiles-removal',
            'request_id': 'pro-profiles-removal_request_id',
            'change_doc_id': 'request_id',
            'api_path': 'api_path',
            'mode': 'poll',
            'run_manually': False,
            'description': 'draft description',
            'data': {'profiles': ['park_contractor1', 'park_contractor2']},
            'summon_users': ['summon_user1', 'summon_user2'],
            'tickets': {
                'create_data': {
                    'description': 'description of new ticket',
                    'summary': 'summary of new ticket',
                },
            },
        }
        return {'id': 1, 'version': 1, 'status': 'need_approval'}

    draft = drafts_service.DraftInfo(
        request_id='request_id',
        data={'profiles': ['park_contractor1', 'park_contractor2']},
        description='draft description',
        summon_users=['summon_user1', 'summon_user2'],
        new_ticket=drafts_service.NewTicket(
            summary='summary of new ticket',
            description='description of new ticket',
        ),
        run_manually=False,
        mode=drafts_service.DraftMode.POLL,
        api_path='api_path',
    )

    draft_id = await cron_context.services.drafts.create_draft(draft)
    assert draft_id == 1


async def test_create_existing_draft(
        cron_context: context.Context, mock_taxi_approvals, mockserver,
):
    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft(request: http.Request):
        return mockserver.make_response(
            json={'code': '409', 'message': 'error'}, status=409,
        )

    @mock_taxi_approvals('/drafts/list/')
    async def _drafts_list(request: http.Request):
        assert request.json == {
            'service_name': 'pro-profiles-removal',
            'change_doc_ids': ['pro-profiles-removal_request_id'],
        }
        return [{'id': 1, 'version': 1, 'status': 'need_approval'}]

    draft = drafts_service.DraftInfo(
        request_id='request_id',
        data={'profiles': ['park_contractor1', 'park_contractor2']},
        description='draft description',
        summon_users=['summon_user1', 'summon_user2'],
        new_ticket=drafts_service.NewTicket(
            summary='summary of new ticket',
            description='description of new ticket',
        ),
        run_manually=False,
        mode=drafts_service.DraftMode.POLL,
        api_path='api_path',
    )

    draft_id = await cron_context.services.drafts.create_draft(draft)
    assert draft_id == 1
    assert _create_draft.times_called == 1
    assert _drafts_list.times_called == 1


async def test_successfully_finish_draft_ok(
        cron_context: context.Context, mock_taxi_approvals,
):
    @mock_taxi_approvals('/drafts/1/finish/')
    async def _finish_draft(request: http.Request):
        assert request.json == {
            'final_status': 'succeeded',
            'comment': 'comment',
        }
        return {'id': 1, 'version': 1, 'status': 'succeeded'}

    await cron_context.services.drafts.finish_draft(
        draft_id=1,
        comment='comment',
        final_status=str(drafts_service.DraftStatus.SUCCEEDED),
        errors=None,
    )


async def test_unsuccessfully_finish_draft_ok(
        cron_context: context.Context, mock_taxi_approvals,
):
    @mock_taxi_approvals('/drafts/1/finish/')
    async def _finish_draft(request: http.Request):
        assert request.json == {
            'final_status': 'failed',
            'errors': [{'key1': 'val1'}, {'key2': 'val2'}],
            'comment': 'comment',
        }
        return {'id': 1, 'version': 1, 'status': 'failed'}

    await cron_context.services.drafts.finish_draft(
        draft_id=1,
        comment='comment',
        errors=[{'key1': 'val1'}, {'key2': 'val2'}],
        final_status=str(drafts_service.DraftStatus.FAILED),
    )


async def test_reject_draft_ok(
        cron_context: context.Context, mock_taxi_approvals,
):
    @mock_taxi_approvals('/drafts/1/reject/')
    async def _reject_draft(request: http.Request):
        assert request.json == {'comment': 'comment'}
        return {'id': 1, 'version': 1, 'status': 'rejected'}

    await cron_context.services.drafts.reject_draft(
        draft_id=1, comment='comment',
    )


async def test_get_status(cron_context: context.Context, mock_taxi_approvals):
    @mock_taxi_approvals('/drafts/1/')
    async def _get_draft():
        return {'id': 1, 'version': 2, 'status': 'approved'}

    status = await cron_context.services.drafts.get_draft_status(draft_id=1)
    assert status == drafts_service.DraftStatus.APPROVED


async def test_summon_approvers(
        cron_context: context.Context, mock_taxi_approvals,
):
    @mock_taxi_approvals('/drafts/1/summon_approvers/')
    async def _summon_approvers(request: http.Request):
        assert request.json == {'summon_users': ['user']}
        return {
            'summoned_users': [
                {'login': 'user', 'summoned': '2022-06-30T12:00:00'},
            ],
        }

    await cron_context.services.drafts.summon_approvers(
        draft_id=1, summon_users=['user'],
    )
