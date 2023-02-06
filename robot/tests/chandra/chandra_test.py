from robot.library.yuppie.modules.io import IO
import logging
import jinja2
import typing as tp
from os.path import join as pj
from functools import partial
from yatest.common import \
    work_path, \
    binary_path, \
    source_path, \
    output_path, \
    network, \
    canonical_file, \
    execute

from robot.library.yuppie.modules.environment import Environment
from robot.library.yuppie.modules.yt_mod import LocalYt
from yt.wrapper import YtClient
from yt.wrapper.client_impl import YtClient as TYtClient
from ads.bsyeti.big_rt.py_lib import YtQueue
from ads.bsyeti.big_rt.cli.lib import create_consumer

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

INPUT_QUEUE_DIR = "//home/chandra"
CONSUMER = "ray"
SHARD_COUNT_IN = 1
SHARD_COUNT_OUT = 10

URL_STATUSES_TABLE_DUMP_FILE_PATH = output_path("url_statuses_table")
URL_STATUSES_TABLE_PATH = "//home/MirrorTable"

MIRROR_SUBGROUP_QUEUE_SHARDS_COUNT_IN = 10
QUEUE_DUMP_FILE_PATH = output_path("mirror_subgroup_queue")
MIRROR_SUBGROUP_QUEUE_PATH = "//home/SubGroupQueue"

MIRROR_SUBGROUP_TABLE_DUMP_FILE_PATH = output_path("mirror_subgroup_table")
MIRROR_SUBGROUP_TABLE_PATH = "//home/UrlSubgroupTable"

# Chandra data
CHOOSE_HOSTS_SUBGROUP_CONFIG_TEMPLATE = source_path("robot/mirror/config/chandra/choose_hosts_subgroup_test.tmpl.j2")
CHOOSE_HOSTS_SUBGROUP_CONFIG_NAME = "choose_hosts_subgroup_test_config.json"

MAINTAIN_SUBGROUP_TABLE_CONFIG_TEMPLATE = source_path("robot/mirror/config/chandra/maintain_subgroup_table_test.tmpl.j2")
MAINTAIN_SUBGROUP_TABLE_CONFIG_NAME = "maintain_subgroup_table_test_config.json"

CHANDRA_WORKER_BIN = binary_path("robot/mirror/tools/chandra/chandra")
CHANDRA_LOG_PATH = output_path("chandra_test.log")


def get_queue_data_checker(queue, consumer):
    shards_info = queue["queue"].get_shard_infos()
    offsets = queue["queue"].get_consumer_offsets(consumer)
    expected_offsets = {shard: offsets[shard] + shards_info[shard]["total_row_count"] for shard in range(queue["queue"].get_shard_count())}
    return partial(check_queue_is_read, queue, consumer, expected_offsets)


class ChooseHostsSubgroupProcess(BulliedProcess):
    def __init__(self, config_path):
        super(ChooseHostsSubgroupProcess, self).__init__(launch_cmd=[CHANDRA_WORKER_BIN, "ChooseHostsSubgroup", "--config-file", config_path])


class MaintainSubgroupTableProcess(BulliedProcess):
    def __init__(self, config_path):
        super(MaintainSubgroupTableProcess, self).__init__(launch_cmd=[CHANDRA_WORKER_BIN, "MaintainSubgroupTable", "--config-file", config_path])


def prepare_local_yt_with_test_data(test_snapshot_dir: str) -> tp.Tuple[LocalYt, TYtClient]:
    '''Set up local YT cluster and upload test snapshot'''

    local_yt = LocalYt(
        yt_work_dir=YT_WORK_DIR,
        wait_tablet_cell_initialization=True
    )

    yt_client: YtClient = local_yt.create_yt_client()
    local_yt.upload(test_snapshot_dir, INPUT_QUEUE_DIR, binary_content=True)
    logging.info("Local YT prepared and run on proxy %s", local_yt.get_proxy())

    create_yt_queue(yt_client, MIRROR_SUBGROUP_QUEUE_PATH, SHARD_COUNT_OUT)
    create_consumer(MIRROR_SUBGROUP_QUEUE_PATH, CONSUMER, 1, yt_client)

    return local_yt, yt_client


def make_choose_hosts_subgroup_test_config(yt_proxy: str):
    '''Make config by template'''

    with open(CHOOSE_HOSTS_SUBGROUP_CONFIG_TEMPLATE) as f:
        config_data = jinja2.Template(f.read()).render(
            shards_count=SHARD_COUNT_IN,
            port=network.PortManager().get_port(),
            consumer=CONSUMER,
            queue_dir=INPUT_QUEUE_DIR,
            cluster=yt_proxy,
            global_log=CHANDRA_LOG_PATH,
            yt_out=URL_STATUSES_TABLE_PATH,
            queue_out=MIRROR_SUBGROUP_QUEUE_PATH,
        )
    logging.info("Log path: %s", CHANDRA_LOG_PATH)

    return make_namedtuple(
        "ChooseHostsSubgroupConfig",
        path=make_json_file(config_data, name_template=CHOOSE_HOSTS_SUBGROUP_CONFIG_NAME),
    )


def make_maintain_subgroup_table_test_config(yt_proxy: str):
    '''Make config by template'''

    with open(MAINTAIN_SUBGROUP_TABLE_CONFIG_TEMPLATE) as f:
        config_data = jinja2.Template(f.read()).render(
            shards_count=MIRROR_SUBGROUP_QUEUE_SHARDS_COUNT_IN,
            port=network.PortManager().get_port(),
            consumer=CONSUMER,
            queue_dir=MIRROR_SUBGROUP_QUEUE_PATH,
            cluster=yt_proxy,
            global_log=CHANDRA_LOG_PATH,
            yt_out=MIRROR_SUBGROUP_TABLE_PATH,
        )
    logging.info("Log path: %s", CHANDRA_LOG_PATH)

    return make_namedtuple(
        "MaintainSubgroupTableConfig",
        path=make_json_file(config_data, name_template=MAINTAIN_SUBGROUP_TABLE_CONFIG_NAME),
    )


def prepare_queue_and_check_func(client: TYtClient, config: str, input_queue_path: str, input_queue_shards_count):
    '''Prepare queue data for launching function'''

    queue = {
        "cluster": client.config["proxy"]["url"],
        "path": input_queue_path,
        "shards": input_queue_shards_count,
        "queue": YtQueue(dict(path=input_queue_path, cluster=client.config["proxy"]["url"])),
    }

    shards_info = queue["queue"].get_shard_infos()
    rows_in_shards = {shard: shards_info[shard]["total_row_count"] for shard in range(queue["queue"].get_shard_count())}
    logging.info("DATA: %s", str(rows_in_shards))

    check_func = get_queue_data_checker(
        queue,
        CONSUMER,
    )

    return queue, check_func


def run_choose_hosts_subgroup(client: TYtClient, config: str, input_queue_path: str, input_queue_shards_count):
    queue, check_func = prepare_queue_and_check_func(client, config, input_queue_path, input_queue_shards_count)

    launch(
        [ChooseHostsSubgroupProcess(config)],
        queue=queue,
        consumer=CONSUMER,
        data_or_check_func=check_func,
        restart_randmax=None,
        timeout=300,
    )


def run_maintain_subgroup_table(client: TYtClient, config: str, input_queue_path: str, input_queue_shards_count):
    queue, check_func = prepare_queue_and_check_func(client, config, input_queue_path, input_queue_shards_count)

    launch(
        [MaintainSubgroupTableProcess(config)],
        queue=queue,
        consumer=CONSUMER,
        data_or_check_func=check_func,
        restart_randmax=None,
        timeout=300,
    )


def create_url_statuses_table(choose_hosts_subgroup_config_file):
    execute([
        CHANDRA_WORKER_BIN,
        "CreateTables",
        "--url-statuses",
        choose_hosts_subgroup_config_file
    ])

    logging.info("Url statuses table created")


def create_mirror_subgroup_table(maintain_subgroup_table_config_file):
    execute([
        CHANDRA_WORKER_BIN,
        "CreateTables",
        "--mirror-subgroup",
        maintain_subgroup_table_config_file
    ])

    logging.info("Mirror subgroup table created")


def dump_table(yt: LocalYt, path_to_table, dump_file_path):
    yt.yt_client.freeze_table(path_to_table, sync=True)

    table = yt.yt_client.read_table(
        path_to_table,
        format='<format=pretty;skip_null_values=%true>yson',
        raw=True,
    ).read()

    with open(dump_file_path, "wb") as f:
        f.write(table)

    logging.info("Dump of %s: %s", path_to_table, dump_file_path)


def test_chandra():
    Environment()
    # Unpack the downloaded archive with test data
    IO.unpack(TAR_DATA, work_path("test"))

    # Prepare local YT test cluster
    local_yt, yt_client = prepare_local_yt_with_test_data(TEST_DUMP_DIR)
    yt_proxy = local_yt.get_proxy()

    # Generate test config and run choose hosts subgroup
    config = make_choose_hosts_subgroup_test_config(yt_proxy)
    logging.info("Choose hosts subgroup config path: %s", config.path)

    create_url_statuses_table(config.path)
    run_choose_hosts_subgroup(yt_client, config.path, INPUT_QUEUE_DIR, SHARD_COUNT_IN)

    # Generate test config and maintain subgroup table
    config = make_maintain_subgroup_table_test_config(yt_proxy)
    logging.info("Maintain subgroup table config path: %s", config.path)

    create_mirror_subgroup_table(config.path)
    run_maintain_subgroup_table(yt_client, config.path, MIRROR_SUBGROUP_QUEUE_PATH, MIRROR_SUBGROUP_QUEUE_SHARDS_COUNT_IN)

    # Dump results
    dump_table(local_yt, URL_STATUSES_TABLE_PATH, URL_STATUSES_TABLE_DUMP_FILE_PATH)
    dump_table(local_yt, pj(MIRROR_SUBGROUP_QUEUE_PATH, "queue"), QUEUE_DUMP_FILE_PATH)
    dump_table(local_yt, MIRROR_SUBGROUP_TABLE_PATH, MIRROR_SUBGROUP_TABLE_DUMP_FILE_PATH)

    return {
        "Url statuses table dump": canonical_file(URL_STATUSES_TABLE_DUMP_FILE_PATH),
        "Mirror subgroup queue dump": canonical_file(QUEUE_DUMP_FILE_PATH),
        "Mirror subgroup table dump": canonical_file(MIRROR_SUBGROUP_TABLE_DUMP_FILE_PATH)
    }
