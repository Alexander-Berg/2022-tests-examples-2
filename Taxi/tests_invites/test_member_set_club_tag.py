import json

import pytest


@pytest.mark.pgsql('invites', files=['data.sql'])
@pytest.mark.experiments3(filename='experiments3.json')
async def test_stq_run(taxi_invites, mockserver, stq_runner):
    @mockserver.json_handler('/passenger-tags/v1/upload')
    def _v1_upload(request):
        data = json.loads(request.get_data())
        assert data == {
            'merge_policy': 'append',
            'entity_type': 'user_phone_id',
            'tags': [{'name': 'active_club_1', 'match': {'id': '100'}}],
        }
        return {'status': 'ok'}

    stq_task_kwargs = {
        'phone_id': '100',
        'club_id': '11111111-1111-1111-1111-111111111111',
    }

    await stq_runner.invites_member_set_club_tag.call(
        task_id='invites_member_set_club_tag', kwargs=stq_task_kwargs,
    )
