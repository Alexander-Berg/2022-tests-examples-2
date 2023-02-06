import logging
from contextlib import contextmanager
from easytap.pytest_plugin import PytestTap
from _pytest.logging import LogCaptureFixture

from stall.metric import metric
from libstall.log import metrics_log


@contextmanager
def propagate_log(logger: logging.Logger):
    propagate_backup = logger.propagate
    logger.propagate = True
    try:
        yield
    finally:
        logger.propagate = propagate_backup


async def test_metric(tap: PytestTap, caplog: LogCaptureFixture):
    with tap, propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        metric('default_metric', 3)
        metric('sigle_metric', 5, 'avg')
        metric(
            'improved_metric_1', 6, 'avg',
            labels={'group': 'group_1', 'label': 'label_1'}
        )
        metric(
            'improved_metric_2', 8,
            labels={'group': 'group_2'}, label='label_2'
        )

        sent_metrics = {
            rec.ctx['name']: (
                rec.ctx['value'],
                rec.ctx.get('agg'),
                rec.ctx.get('group'),
                rec.ctx.get('label'),
                rec.ctx.get('extra_labels'),
            )
            for rec in caplog.records
            if rec.name == metrics_log.name and 'name' in rec.ctx
        }

        tap.eq_ok(sent_metrics['default_metric'], (3, 'sum', None, None, None),
                  'metric with default aggregation was sent')
        tap.eq_ok(sent_metrics['sigle_metric'], (5, 'avg', None, None, None),
                  'sigle metric was sent')
        tap.eq_ok(
            sent_metrics['improved_metric_1'],
            (6, 'avg', 'group_1', 'label_1', ['group', 'label']),
            'first metric with extra label with was sent'
        )
        tap.eq_ok(
            sent_metrics['improved_metric_2'],
            (8, 'sum', 'group_2', 'label_2', ['group']),
            'second metric with extra label was sent'
        )
