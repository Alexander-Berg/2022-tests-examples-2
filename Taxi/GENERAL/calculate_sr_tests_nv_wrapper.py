#!/usr/bin/env python2

from __future__ import print_function

import argparse
import datetime
import sys
import traceback

import nirvana.job_context as nv
from nile.api.v1 import clusters, Record

from zoo.utils.experiments_helpers import (
    calculate_sum_ratio_tests, validate_metric
)


LOG_PATH = '//home/taxi_ml/public/nirvana_bucket_test/log'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--main-script', default='calculator',
                        choices=['calculator', 'validator'])
    parser.add_argument('--log-cluster', required=False, default='Hahn')
    wrapper_args, main_args = parser.parse_known_args()

    meta = nv.context().get_meta()

    main_error_type, main_error, main_error_tb = None, None, None
    start = datetime.datetime.utcnow()
    try:
        if wrapper_args.main_script == 'calculator':
            calculate_sum_ratio_tests.main(main_args)
        if wrapper_args.main_script == 'validator':
            validate_metric.main(main_args)
    except Exception as e:
        main_error_type, main_error, main_error_tb = sys.exc_info()
    end = datetime.datetime.utcnow()

    try:
        info = [Record.from_dict({
            'main_script': wrapper_args.main_script,
            'main_args': main_args,
            'description': meta.get_description(),
            'owner': meta.get_owner(),
            'workflow_url': meta.get_workflow_url(),
            'workflow_instance_uid': meta.get_workflow_instance_uid(),
            'block_uid': meta.get_block_uid(),
            'block_url': meta.get_block_url(),
            'quota_project': meta.get_quota_project(),
            'success': main_error is None,
            'error': repr(main_error) if main_error else None,
            'traceback': traceback.format_exc() if main_error else None,
            'utc_start_dttm': start.strftime(format='%Y-%m-%d %H:%M:%S'),
            'utc_start_date': start.strftime(format='%Y-%m-%d'),
            'utc_end_dttm': end.strftime(format='%Y-%m-%d %H:%M:%S'),
            'duration': (end - start).total_seconds()
        })]

        clusters.yt.YT(wrapper_args.log_cluster).write(
            LOG_PATH, records=info, append=True
        )
    except Exception as e:
        print('LOGGING ERROR:\n', file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print(repr(e), file=sys.stderr)

    if main_error:
        raise main_error_type, main_error, main_error_tb
