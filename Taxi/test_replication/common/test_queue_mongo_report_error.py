from freezegun.api import FakeDatetime
import pymongo
import pytest

from taxi.clients import solomon

from replication.common.solomon import pusher as solomon_pusher
from replication.foundation import consts
from replication.foundation import map_doc_classes


class ErrorBulk:
    @staticmethod
    def execute(*args, **kwargs):
        raise pymongo.errors.BulkWriteError({})


@pytest.mark.now('2020-12-04T21:00:00.000+0000')
@pytest.mark.parametrize(
    ('test_doc', 'expected_data'),
    (
        (
            map_doc_classes.MapDocInfo(0, {'data': '', 'id': ''}, '0'),
            [
                {
                    'value': 1,
                    'timestamp': FakeDatetime(2020, 12, 4, 21, 0),
                    'kind': solomon.GaugeKind.INT,
                    'sensor': 'queue_mongo_errors',
                    'queue_db_cluster': 'replication_queue_mdb_0',
                    'error_name': 'mongo_bulk_write_error',
                    'error_type': 'target',
                    'rule_name': 'test_rule',
                },
            ],
        ),
    ),
)
async def test_insert_data_error(
        replication_ctx, monkeypatch, test_doc, expected_data,
):
    sensors_data = []

    async def _fake_flush_solomon_metric(solomon_client, sensors, application):
        sensors_data.extend(sensors)

    monkeypatch.setattr(
        solomon_pusher, '_flush_solomon_metric', _fake_flush_solomon_metric,
    )

    rules_list = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_types=[consts.TARGET_TYPE_QUEUE_MONGO], rule_name='test_rule',
    )
    for rule in rules_list:
        for target in rule.targets:
            # pylint: disable=protected-access
            original_execute_bulk = target._execute_bulk
            monkeypatch.setattr(
                target,
                '_execute_bulk',
                _patched_execute_bulk_wrapper(original_execute_bulk),
            )
            with pytest.raises(pymongo.errors.BulkWriteError):
                await target.insert_data([test_doc])
            break

    assert sensors_data == expected_data


def _patched_execute_bulk_wrapper(original_execute_bulk):
    async def _patched_execute_bulk(bulk, *args, **kwargs):
        await original_execute_bulk(ErrorBulk, *args, **kwargs)

    return _patched_execute_bulk
