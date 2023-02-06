from datetime import datetime

import mock
import pytest

from dmp_suite.juggler import EventStatus
from dmp_suite.maintenance.monitoring.juggler_monitoring import (
    SlaEntityEnrich, prepare_juggler_reports, get_sla_entities
)


@pytest.mark.parametrize('sla_entities, expected_status', [
    ([SlaEntityEnrich('YT', '//one/two/three', 'last_load', datetime(2021, 1, 1), None, 100500)], EventStatus.OK),
    ([SlaEntityEnrich('YT', '//one/two/three', 'last_load', datetime(2021, 1, 1), 100500, None)], EventStatus.OK),
    ([SlaEntityEnrich('YT', '//one/two/three', 'last_load', datetime(2021, 1, 1), 100500, 100600)], EventStatus.OK),
    ([SlaEntityEnrich('YT', '//one/two/three', 'last_sync', datetime(2021, 1, 1), 12, 100)], EventStatus.WARN),
    ([SlaEntityEnrich('YT', '//one/two/three', 'last_load', datetime(2021, 1, 1), 12, None)], EventStatus.WARN),
    ([SlaEntityEnrich('YT', '//one/two/three', 'last_sync', datetime(2021, 1, 1), 12, 22)], EventStatus.CRIT),
    ([SlaEntityEnrich('YT', '//one/two/three', 'last_load', datetime(2021, 1, 1), None, 22)], EventStatus.CRIT),
])
def test_prepare_juggler_reports(sla_entities, expected_status):
    with mock.patch('dmp_suite.maintenance.monitoring.juggler_monitoring.get_sla_entities', lambda _: sla_entities):
        reports = prepare_juggler_reports('test_etl', utc_dttm=datetime(2021, 1, 1, 0, 0, 50))

        for report in reports:
            assert report.domain == 'yt'
            assert report.name == '//one/two/three'
            assert report.status == expected_status


@pytest.mark.parametrize('rows, expected', [
    (
            [],
            []
    ),
    (
            [('domain', 'entity_name', 'last_load_date', '2020-04-02 13:20:38.973680', 1, 2)],
            [SlaEntityEnrich('domain', 'entity_name', 'last_load_date', datetime(2020, 4, 2, 13, 20, 38, 973680), 1, 2)]
    ),
    (
            [('domain', 'entity_name', 'last_load_date', '2020-04-02 13:20:38', 1, None)],
            [SlaEntityEnrich('domain', 'entity_name', 'last_load_date', datetime(2020, 4, 2, 13, 20, 38), 1, None)]
    ),
    (
            [('domain', 'entity_name', 'last_sync_date', '2020-04-02 13:20:00', None, 2)],
            [SlaEntityEnrich('domain', 'entity_name', 'last_sync_date', datetime(2020, 4, 2, 13, 20), None, 2)]
    ),
])
def test_get_sla_entities(rows, expected):
    pg_connection = mock.Mock()
    pg_connection.query = (
        lambda query, service: rows
    )

    class ContextManager:
        def __enter__(self):
            return pg_connection

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    context_manager = mock.patch(
        'dmp_suite.maintenance.monitoring.juggler_monitoring.get_pgaas_connection',
        return_value=ContextManager()
    )

    settings = mock.patch('dmp_suite.maintenance.monitoring.juggler_monitoring.settings', lambda name: 'schema')

    with context_manager, settings:
        res = list(get_sla_entities('root_etl'))

    for i in range(len(res)):
        assert res[i] == expected[i]
