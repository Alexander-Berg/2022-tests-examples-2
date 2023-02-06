import time

from mapreduce.yt.python.yt_stuff import yt_stuff  # noqa
from mongo_runner import mongo
from yql_api import yql_api
from yql_utils import tmpdir_module
from yt_runner import yt
from robot.library.yuppie.fixtures.yt import yt_config
from robot.library.yuppie.fixtures.yt import yp_yt

from favicon.targets import Manual

from utils import run_local_favicon_integration_pipeline


FIRST_PART_TIMEOUT = 2 * 60  # seconds
SECOND_PART_TIMEOUT = 10 * 60  # seconds


def copy_tables_from_prev_state(yt_client):
    prev_manual = Manual(tag='trunk')
    manual = Manual(tag='wip')
    yt_client.copy(prev_manual.link_table(), manual.link_table(), force=True)
    yt_client.copy(prev_manual.image_table(), manual.image_table(), force=True)


def manual_pipeline(local_favicon):
    # Targets Manual.download.* take lock for table Manual/$state/error.log.
    # Test will fail with message "Cannot take lock..." if we run this targets concurrently.

    # Targets Manual.download.* do not really download anything. They take empty lists and do nothing.
    local_favicon.get_cm().check_call_target('Manual.download.manual_list', timeout=FIRST_PART_TIMEOUT)
    local_favicon.get_cm().check_call_target('Manual.download.startrek', timeout=FIRST_PART_TIMEOUT)

    # Here we replace empty tables with prepared data from tables_data.tar.
    copy_tables_from_prev_state(local_favicon.get_yt())

    local_favicon.get_cm().check_call_target('Manual.cleanup', timeout=SECOND_PART_TIMEOUT)
    while local_favicon.get_cm().get_active_targets():
        time.sleep(3)


def test_manual(config, yt_config, yt_stuff, yt, yp_yt, yql_api, links):
    return run_local_favicon_integration_pipeline(manual_pipeline, yp_yt, yql_api, working_subdir="manual")
