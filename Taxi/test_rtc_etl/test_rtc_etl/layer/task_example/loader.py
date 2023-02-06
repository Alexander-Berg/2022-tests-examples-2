import logging

from dmp_suite.task import PyTask
from dmp_suite.task.cron import Cron
from dmp_suite.task.cli import StartEndDate


logger = logging.getLogger(__name__)


def load(args):
    logger.info(f'Args: {args.period}')
    logger.info('Hello ETL World!')


task = PyTask(
    'hello_etl_world',
    load,
).set_scheduler(
    Cron('0 16 * * *'),
).arguments(
    period=StartEndDate.prev_n_days(2),
)
