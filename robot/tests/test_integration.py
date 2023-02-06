import time

from mapreduce.yt.python.yt_stuff import yt_stuff  # noqa
from mongo_runner import mongo
from yql_api import yql_api
from yql_utils import tmpdir_module
from yt_runner import yt
from robot.library.yuppie.fixtures.yt import yt_config
from robot.library.yuppie.fixtures.yt import yp_yt

from favicon.targets import Base

from utils import make_and_validate_trie, run_local_favicon_integration_pipeline


BASE_TIMEOUT = 35 * 60  # seconds
DEPLOY_TIMEOUT = 5 * 60  # seconds


def base_pipeline(local_favicon):
    local_favicon.get_cm().mark_success('Deploy.cleanup')
    local_favicon.get_cm().check_call_target('Base.archive', timeout=BASE_TIMEOUT)
    while local_favicon.get_cm().get_active_targets():
        time.sleep(3)

    base = Base(tag="trunk")
    smushable_tables = [base.smushable_table()]
    return make_and_validate_trie(local_favicon, base.attrs_table(), smushable_tables)


def test_integration(config, yt_config, yt_stuff, yt, yp_yt, yql_api, links):
    return run_local_favicon_integration_pipeline(base_pipeline, yp_yt, yql_api, working_subdir="integration")
