from passport.backend.tools.metrics.file_parsers import tskv_log_parser
from passport.backend.tools.metrics.metrics import MetricParser
import pytest


@pytest.fixture()
def metrics_parser():
    return MetricParser(
        log_type=tskv_log_parser(),
        metric_name_template='metric.{column}.{__aggregate__}',
        fields=['column'],
        filters={},
        defaults={},
        aggregate_fs=['avg'],
        metric_value_column=None,
    )


def test_init(metrics_parser):
    assert metrics_parser.extra_context == {
        'column': '{column}',
        '__aggregate__': '{__aggregate__}',
    }
    assert metrics_parser.filters == {'column': [[], []]}
