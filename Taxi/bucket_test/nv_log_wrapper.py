from typing import List, Optional
import argparse
import datetime
import sys
import traceback

import nirvana.job_context as nv
from nile.api.v1 import clusters, Record

from projects.common.nile.environment import DEFAULT_CLUSTER
from projects.bucket_test import calculate_tests, validate_metrics


LOG_PATH = '//home/taxi_ml/public/nirvana_bucket_test/log'
DTTM_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
VERSION = 'py3'


def make_log_record(
        wrapper_args: argparse.Namespace,
        script_args: List[str],
        error: Optional[Exception],
        traceback_log: str,
        start: datetime.datetime,
        end: datetime.datetime,
):
    meta = nv.context().get_meta()
    return Record(
        main_script=wrapper_args.main_script,
        version=VERSION,
        main_args=script_args,
        description=meta.get_description(),
        owner=meta.get_owner(),
        workflow_url=meta.get_workflow_url(),
        workflow_instance_uid=meta.get_workflow_instance_uid(),
        block_uid=meta.get_block_uid(),
        block_url=meta.get_block_url(),
        quota_project=meta.get_quota_project(),
        success=error is None,
        error=repr(error) if error else None,
        traceback=traceback_log if error else None,
        utc_start_dttm=start.strftime(format=DTTM_FORMAT),
        utc_start_date=start.strftime(format=DATE_FORMAT),
        utc_end_dttm=end.strftime(format=DTTM_FORMAT),
        duration=(end - start).total_seconds(),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--main-script',
        default='calculator',
        choices=['calculator', 'validator'],
    )
    parser.add_argument('--log-cluster', default=DEFAULT_CLUSTER)
    wrapper_args, main_args = parser.parse_known_args()

    start = datetime.datetime.utcnow()
    try:
        if wrapper_args.main_script == 'calculator':
            calculate_tests.main(main_args)
        if wrapper_args.main_script == 'validator':
            validate_metrics.main(main_args)
    finally:
        end = datetime.datetime.utcnow()
        _, error, _ = sys.exc_info()
        error_traceback = traceback.format_exc()
        record = make_log_record(
            wrapper_args, main_args, error, error_traceback, start, end,
        )

        try:
            clusters.yt.YT(wrapper_args.log_cluster).write(
                LOG_PATH, records=[record], append=True,
            )
        except Exception as e:
            print('LOGGING ERROR:\n', file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            print(repr(e), file=sys.stderr)
