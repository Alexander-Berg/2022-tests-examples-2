import logging

import freezegun
import pytest

logger = logging.getLogger(__name__)


@freezegun.freeze_time('2019-01-01T12:00:00.999')
@pytest.mark.parametrize(
    'name',
    ['valid', 'locked']
)
def test_find_license(
        run_check_create_walking_courier,
        get_mongo,
        mongo_create_indexes,
        find_field,
        find_documents_in_update_queue,
        patch,
        name,
):
    @patch('infranaim.clients.cargo_misc.get_operation_status')
    def _get_operation_status(*args, **kwargs):
        return {
            'status': 'processed',
            'driver_id': 'dbid_uuid'
        }

    mongo = get_mongo
    mongo_create_indexes(mongo)
    if name == 'valid':
        mongo.cron_locks.delete_many({})
    run_check_create_walking_courier(mongo)

    docs = find_documents_in_update_queue(mongo)
    if name == 'locked':
        assert not docs
        assert not _get_operation_status.calls
        return

    assert len(docs) == 1
    assert _get_operation_status.calls
    for doc in docs:
        assert (
            find_field(
                doc['upd_data'][0]['data']['custom_fields'],
                114103138813
            )['value'] == 'uuid'
        )
        assert (
            find_field(
                doc['upd_data'][0]['data']['custom_fields'],
                360008809039
            )['value'] == 'processed'
        )
