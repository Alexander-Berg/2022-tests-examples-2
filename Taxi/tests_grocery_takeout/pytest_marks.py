import pytest

from . import consts
from . import models

NOW = pytest.mark.now(consts.NOW)

JOB_TYPES = pytest.mark.parametrize('job_type', models.JobType.values)
