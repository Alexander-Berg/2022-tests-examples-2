# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import pytest

from grocery_takeout_plugins import *  # noqa: F403 F401

from . import job_pipeline


@pytest.fixture(name='job_pipeline')
def _job_pipeline(
        stq_runner, stq, grocery_takeout_db, grocery_takeout_configs,
):
    return job_pipeline.JobPipeline(
        stq_runner, stq, grocery_takeout_db, grocery_takeout_configs,
    )
