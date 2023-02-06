from robot.library.yuppie.modules.io import IO
from os.path import join as pj
import logging
import jinja2
import typing as tp
from functools import partial
from yatest.common import \
    work_path, \
    binary_path, \
    source_path, \
    output_path, \
    network, \
    canonical_file

from robot.library.yuppie.modules.environment import Environment
from robot.library.yuppie.modules.yt_mod import LocalYt
from yt.wrapper import YtClient
from yt.wrapper.client_impl import YtClient as TYtClient
from ads.bsyeti.big_rt.py_lib import YtQueue

from ads.bsyeti.big_rt.py_test_lib import (
    launch_bullied_processes_reading_queue as launch,
    check_queue_is_read,
    BulliedProcess,
    make_json_file,
    make_namedtuple,
    create_yt_queue
)


# YT data
YT_WORK_DIR = work_path("yt-local-workdir")
TAR_DATA = work_path("resource.tar.gz")
TEST_DUMP_DIR = work_path("test/test_snap")

QUEUE_DIR = "//home/resharder"
CONSUMER = "consumer"
SHARD_COUNT_IN = 1

YT_OUTPUT_QUEUE_PATH = "//home/OutputQueue"
SHARD_COUNT_OUT = 10
DUMP_FILE_PATH = output_path("queue_content")

# Resharder data
RESHARDER_CONFIG_TEMPLATE = source_path("robot/mirror/config/resharder/resharder.tmpl.j2")
RESHARDER_CONFIG_NAME = "resharder_test_config.json"

RESHARDER_WORKER_BIN = binary_path("robot/mirror/tools/resharder/resharder")


def get_queue_data_checker(queue, consumer):
    shards_info = queue["queue"].get_shard_infos()
    offsets = queue["queue"].get_consumer_offsets(consumer)
    expected_offsets = {shard: offsets[shard] + shards_info[shard]["total_row_count"] for shard in range(queue["queue"].get_shard_count())}
    return partial(check_queue_is_read, queue, consumer, expected_offsets)


class ShardingProcess(BulliedProcess):
    def __init__(self, config_path):
        super(ShardingProcess, self).__init__(launch_cmd=[RESHARDER_WORKER_BIN, "--config-file", config_path])


def prepare_local_yt_with_test_data(test_snapshot_dir: str) -> tp.Tuple[LocalYt, TYtClient]:
    '''Set up local YT cluster and upload test snapshot'''

    local_yt = LocalYt(
        yt_work_dir=YT_WORK_DIR,
        wait_tablet_cell_initialization=True
    )

    yt_client: YtClient = local_yt.create_yt_client()
    local_yt.upload(test_snapshot_dir, QUEUE_DIR, binary_content=True)
    logging.info("Local YT prepared and run on proxy %s", local_yt.get_proxy())

    return local_yt, yt_client


def make_resharder_test_config(yt_proxy: str):
    '''Make config by template'''

    with open(RESHARDER_CONFIG_TEMPLATE) as f:
        config_data = jinja2.Template(f.read()).render(
            shards_count=SHARD_COUNT_IN,
            port=network.PortManager().get_port(),
            consumer=CONSUMER,
            queue_dir=QUEUE_DIR,
            cluster=yt_proxy,
            global_log=output_path("resharder_test.log"),
            yt_out=YT_OUTPUT_QUEUE_PATH
        )
    logging.info("Log path: %s", output_path("resharder_test.log"))
    return make_namedtuple(
        "ShardingConfig",
        path=make_json_file(config_data, name_template=RESHARDER_CONFIG_NAME),
    )


def run_worker(client: TYtClient, config: str):
    '''Prepare queue data for launching function'''
    queue = {
        "cluster": client.config["proxy"]["url"],
        "path": QUEUE_DIR,
        "shards": SHARD_COUNT_IN,
        "queue": YtQueue(dict(path=QUEUE_DIR, cluster=client.config["proxy"]["url"])),
    }

    shards_info = queue["queue"].get_shard_infos()
    rows_in_shards = {shard: shards_info[shard]["total_row_count"] for shard in range(queue["queue"].get_shard_count())}
    logging.info("DATA: %s", str(rows_in_shards))

    check_func = get_queue_data_checker(
        queue,
        CONSUMER,
    )

    create_yt_queue(client, YT_OUTPUT_QUEUE_PATH, SHARD_COUNT_OUT)

    launch(
        [ShardingProcess(config)],
        queue=queue,
        consumer=CONSUMER,
        data_or_check_func=check_func,
        restart_randmax=None,
        timeout=600,
    )


def dump_queue(yt: LocalYt):
    '''
    Dump queue content to queue_content file with mapping:
        Tablet {shard id}: [WeakKey ...]
    Can be usefull for investigation if diff
    '''

    yt.yt_client.freeze_table(pj(YT_OUTPUT_QUEUE_PATH, "queue"), sync=True)

    table = yt.yt_client.read_table(
        pj(YT_OUTPUT_QUEUE_PATH, "queue"),
        format='<format=pretty;skip_null_values=%true>yson',
        raw=True,
    ).read()

    with open(DUMP_FILE_PATH, "wb") as f:
        f.write(table)
    logging.info("Dump of Data: %s", DUMP_FILE_PATH)


def test_resharder():
    Environment()
    # Unpack the downloaded archive with test data
    IO.unpack(TAR_DATA, work_path("test"))

    # Prepare local YT test cluster
    local_yt, yt_client = prepare_local_yt_with_test_data(TEST_DUMP_DIR)
    yt_proxy = local_yt.get_proxy()

    # Generate test config and run binary
    config = make_resharder_test_config(yt_proxy)
    logging.info("Config path: %s", config.path)

    # Launch binary with generated config
    run_worker(yt_client, config.path)

    # Dump results in queue_content file
    dump_queue(local_yt)

    return canonical_file(DUMP_FILE_PATH)
