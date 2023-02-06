import os
import time

import pytest

from taxi_tests.environment.services import postgresql
from taxi_tests.utils import gensecdist
from tests_plugins.daemons import spawn


class TaxiJobsRunner:
    ExitCodeError = spawn.ExitCodeError

    def __init__(
            self,
            binary_path,
            secdist_path,
            fallback_json_path,
            taxi_jobs_config_path,
    ):
        self.binary_path = binary_path
        self.secdist_path = secdist_path
        self.fallback_json_path = fallback_json_path
        self.taxi_jobs_config_path = taxi_jobs_config_path

    def run(self, *args):
        popen_args = [self.binary_path]
        popen_args.extend(args)

        env = os.environ.copy()
        env['TAXI_SECDIST_SETTINGS'] = self.secdist_path
        env['CONFIG_FALLBACK_JSON'] = self.fallback_json_path
        env['TAXI_JOBS_CONFIG'] = self.taxi_jobs_config_path

        # Don't use subprocess.call(...) - it calls wait() inside that leads to
        # deadlock with script.
        with spawn.spawned(
                popen_args, allowed_exit_codes=(0,), env=env,
        ) as process:
            # Wait until process terminates
            while process.poll() is None:
                time.sleep(0.01)


@pytest.fixture(scope='session')
def jobs_secdist(
        jobs_config,
        build_dir,
        mongo_host,
        mongo_collections_settings,
        redis_sentinels,
        testsuite_session_context,
        worker_id,
):
    gensecdist.generate_secdist(
        service_desc=jobs_config,
        mongo_host=mongo_host,
        mongo_collections_settings=mongo_collections_settings,
        redis_sentinels=redis_sentinels,
        secdist_vars={
            'mockserver_host': testsuite_session_context.mockserver.base_url,
            'pg_connstring': postgresql.get_connection_string(worker_id),
        },
    )


@pytest.fixture
def taxi_jobs(
        mongodb,
        taxi_config,
        settings,
        build_dir,
        jobs_secdist,
        regenerate_config,
):
    fallback_path = regenerate_config(
        os.path.join(build_dir, 'jobs/lib/conf/files/jobs.testsuite.json'),
        settings.JOBS_SECDIST_PATH,
    )
    return TaxiJobsRunner(
        settings.TAXI_JOBS_PATH,
        secdist_path=settings.JOBS_SECDIST_PATH,
        fallback_json_path=os.path.join(
            build_dir, 'common/generated/fallback/configs.json',
        ),
        taxi_jobs_config_path=fallback_path,
    )
