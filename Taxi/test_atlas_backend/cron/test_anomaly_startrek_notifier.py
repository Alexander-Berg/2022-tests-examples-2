import bson
import pytest

import atlas_backend.crontasks.anomalies.startrek_notifier as notifier_cron
from atlas_backend.generated.cron import run_cron
from atlas_backend.internal.anomalies import hierarchy
import atlas_backend.internal.anomalies.storage as _anomaly_storage

ADMIN_LOGINS = ['admin']


@pytest.mark.config(
    ATLAS_ANOMALY_NOTIFIER={
        'components': ['duty'],
        'startrek_queue': 'TAXIADMIN',
        'startrek_queue_by_source': [
            {
                'components': [],
                'queue': 'EDAOPS',
                'source': 'food',
                'tags': ['duty'],
            },
        ],
        'tags': [],
    },
    ATLAS_ANOMALY_NOTIFIER_ADMIN_LIST={'logins': ADMIN_LOGINS},
)
async def test_anomaly_startrek_notifier(patch, db):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    # pylint: disable=W0612
    async def create_ticket(**kwargs):
        assert kwargs['summary'] == '[Order Metrics] New problems'
        queue = kwargs['queue']

        if queue == 'TAXIADMIN':
            assert kwargs['tags'] == ()
            assert kwargs['components'] == ('duty',)
            return {'key': 'TAXIADMIN-1'}

        if queue == 'EDAOPS':
            assert kwargs['tags'] == ('duty',)
            assert kwargs['components'] == ()
            return {'key': 'EDAOPS-1'}

        assert False, f'Mock not expected "{queue}" as queue value'

    storage = _anomaly_storage.AnomalyStorage(
        db.atlas_anomalies, hierarchy.SourceHierarchy({}),
    )
    to_notify = await storage.get_anomalies_to_notify(
        ADMIN_LOGINS, notifier_cron.NOTIFY_CREATED_FROM,
    )
    assert len(to_notify) == 2, 'Expect something non-trivial'

    await run_cron.main(
        [
            'atlas_backend.crontasks.anomalies.startrek_notifier',
            '-t',
            '0',
        ],  # noqa: E501
    )

    to_notify_after = await storage.get_anomalies_to_notify(
        ADMIN_LOGINS, notifier_cron.NOTIFY_CREATED_FROM,
    )
    assert not to_notify_after, 'Some anomalies was not notified'

    taxiadmin_anomaly = await db.atlas_anomalies.find_one(
        {'_id': bson.ObjectId('5e00b661954de74d8a6af7c7')},
    )
    assert taxiadmin_anomaly['notifications']['startrek'] == 'TAXIADMIN-1'

    edaops_anomaly = await db.atlas_anomalies.find_one(
        {'_id': bson.ObjectId('5e00b661954de74d8a6af7c8')},
    )
    assert edaops_anomaly['notifications']['startrek'] == 'EDAOPS-1'
