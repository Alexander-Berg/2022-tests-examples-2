import logging
import sys
from dmp_suite import datetime_utils as dtu
from dmp_suite.task import PyTask
from dmp_suite.task.cli import StartEndDate, Flag
from dmp_suite.ssas.ssas import ScriptTypes, ServerTypes
from support_etl.layer.greenplum.rep.contactcenter.rep_operator_stat_halfhourly.table import RepOperatorStatHalfhourly
from test_cube import TestCube
from dmp_suite.task.execution import run_task

logger = logging.getLogger(__name__)


def load(
        period: dtu.Period,
        create_partition: bool,
        process_partition: bool,
        process_dimension: bool,
        recalculate_model: bool,
        sync_model: bool,
):
    cube = TestCube()
    cube.execute(
        script=cube.get_full_script(period=period),
        script_type=ScriptTypes.TMSL,
        server_type=ServerTypes.Processing
    )
    cube.load(
        period=period,
        create_partition=create_partition,
        process_partition=process_partition,
        process_dimension=process_dimension,
        recalculate_model=recalculate_model,
        sync_model=sync_model,
    )


def run(args):
    load(
        args.period,
        args.create_partition,
        args.process_partition,
        args.process_dimension,
        args.recalculate_model,
        args.sync_model,
    )


task = PyTask(
    'test_cube',
    func=run,
    sources=[
        RepOperatorStatHalfhourly,
    ],
).arguments(
    period=StartEndDate(dtu.DateWindow().start(days=-1)),
    use_legacy_partition=Flag(
        'Which type of partition to use. Legacy or modern.',
        default=True,
    ),
    create_partition=Flag(
        'If true - will create partition.',
        default=True,
    ),
    process_partition=Flag(
        'If true - will process partition.',
        default=True,
    ),
    process_dimension=Flag(
        'If true - will process dimension.',
        default=True,
    ),
    recalculate_model=Flag(
        'If true - will recalculate entire model at the end.',
        default=True,
    ),
    sync_model=Flag(
        'If true - will sync model at the end.',
        default=True,
    ),
)

if __name__ == '__main__':
    run_task(task)
