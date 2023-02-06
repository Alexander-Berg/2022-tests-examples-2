from testsuite.utils import http

from pro_profiles_removal.generated.cron import cron_context as context
from pro_profiles_removal.services import blocklist as blocklist_service


async def test_add_block(cron_context: context.Context, mock_blocklist):
    @mock_blocklist('/internal/blocklist/v1/add')
    async def _add_block(request: http.Request):
        assert request.json == {
            'block': {
                'predicate_id': '44444444-4444-4444-4444-444444444444',
                'kwargs': {'license_id': 'license_id', 'park_id': 'park_id'},
                'reason': {'key': 'reason_tanker_key'},
                'comment': 'inner_comment',
                'mechanics': 'pro_profiles_removal',
                'disable_service': ['candidates'],
            },
            'identity': {
                'name': 'pro-profiles-removal',
                'type': 'service',
                'id': 'idempotency_token',
            },
        }
        return {'block_id': 'block_id'}

    block_id = await cron_context.services.blocklist.add_block(
        idempotency_token='idempotency_token',
        accept_language='ru',
        block=blocklist_service.BlockInfo(
            inner_comment='inner_comment',
            predicate_id='44444444-4444-4444-4444-444444444444',
            mechanics='pro_profiles_removal',
            kwargs={'license_id': 'license_id', 'park_id': 'park_id'},
            reason_tanker_key='reason_tanker_key',
            disable_services=['candidates'],
        ),
    )
    assert block_id == 'block_id'


async def test_delete_block(cron_context: context.Context, mock_blocklist):
    @mock_blocklist('/internal/blocklist/v1/delete')
    async def _delete_block(request: http.Request):
        assert request.json == {
            'block': {'block_id': 'block_id', 'comment': 'inner_comment'},
            'identity': {
                'name': 'pro-profiles-removal',
                'type': 'service',
                'id': 'block_id',
            },
        }
        return {}

    await cron_context.services.blocklist.delete_block(
        block_id='block_id', inner_comment='inner_comment',
    )
