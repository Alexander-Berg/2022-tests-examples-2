import pytest

import yatest
from mapreduce.yt.python.yt_stuff import YtConfig

CYPRESS_DIR = 'sandbox/projects/k50/sow_map_reduce/tests/data'


@pytest.fixture(scope='module')
def yt_config(request):
    return YtConfig(local_cypress_dir=yatest.common.source_path(CYPRESS_DIR))
