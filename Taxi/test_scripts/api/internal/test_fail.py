import datetime

import pytest

from taxi.scripts import db as scripts_db

NOW = datetime.datetime(2019, 2, 28)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.config(
    SCRIPTS_FEATURES={'push_back_to_queue_on_force_fail': True},
    USE_APPROVALS=True,
)
async def test_force_fail_push_back_to_queue(mockserver, scripts_client, db):
    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _handler(request):
        return [{'change_doc_id': 'scripts_approved-test-id'}]

    response = await scripts_client.post(
        '/scripts/next-script/',
        json={'service_name': 'approved-test', 'fetch_lock_time': 120},
    )
    assert response.status == 200
    script = await response.json()
    _id = script['id']

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-running/'.format(id=_id),
        json={'fqdn': 'test-fqdn'},
    )
    assert response.status == 200

    script = await scripts_db.Script.get_script(db, _id)
    assert script.status == scripts_db.ScriptStatus.RUNNING

    response = await scripts_client.post(
        '/scripts/{id}/mark-as-failed/'.format(id=_id),
        json={'reason': 'archive download failed', 'force': True},
    )
    assert response.status == 200

    script = await scripts_db.Script.get_script(db, _id)
    assert script.status == scripts_db.ScriptStatus.NEED_APPROVAL

    response = await scripts_client.post(
        '/scripts/next-script/',
        json={'service_name': 'approved-test', 'fetch_lock_time': 120},
    )
    assert response.status == 200
    script = await response.json()
    assert _id == script['id']
