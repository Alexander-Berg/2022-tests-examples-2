from itertools import groupby
from operator import itemgetter
from pathlib import Path
from os.path import join as pj
import re
import logging
import asyncio
import typing as tp

from yatest.common import \
    work_path, \
    source_path, \
    binary_path, \
    output_path, \
    execute, \
    canonical_file

from ads.bsyeti.big_rt.cli.lib import create_queue
from robot.library.yuppie.modules.environment import Environment
from robot.library.yuppie.modules.yt_mod import LocalYt
from robot.melter.protos.melter_pb2 import TMelterQueueItem
from yt.yson.yson_types import get_bytes

from yt.wrapper import TablePath, YtClient
# Only for mypy and IDE helpers
from yt.wrapper.client_impl import YtClient as TYtClient


MELTER_CONFIG_GENERATOR_BIN = binary_path("robot/melter/configs/worker/generator/generator")
MELTER_RUNTIME_FS_PRINTER = binary_path("robot/melter/utils/melter_printer/melter_printer")
MELTER_WORKER_BIN = binary_path("robot/melter/impl/worker/worker")
YDT = binary_path("search/plutonium/tools/yt_dynamic_tables/yt_dynamic_tables")

MELTER_CONFIG_TEMPLATE = source_path("robot/melter/configs/worker/melter.worker.tmpl.j2")

YT_WORK_DIR = work_path("yt-local-workdir")
TEST_DUMP_DIR = work_path("test_snapshot")

RUNTIME_FS_DUMP_PATH = output_path("runtime_fs")
MELTER_WORKER_CONFIG = output_path("melter_generated_test.pb.txt")

# Yt wokers paths
MELTER_DIR = "//home/melter"
WORKDIR_PATH = pj(MELTER_DIR, "work_dir")
QUEUE_PATH = pj(MELTER_DIR, "rt_index")

WORKERS_CNT = 32
SHARDS_CNT = 64


class WorkersRunTimeException(Exception):
    def __init__(self, failed_workers_ids: tp.List[int]):
        super().__init__("Workers with ids [%s] failed" % ", ".join([str(id_) for id_ in failed_workers_ids]))


def test_melter():
    # Step 0: Prepare local YT test cluster
    local_yt, yt_client = prepare_local_yt_with_test_data(TEST_DUMP_DIR)
    yt_proxy = local_yt.get_proxy()

    # Step 1: Generate test configs for workers
    setup_configs(yt_proxy)

    # Step 2: Run workers and process modifications queue
    asyncio.run(run_workers(WORKERS_CNT))

    # Step 3: Dump results (runtime FS from Plutonium RO FS)
    dump_runtime_fs()

    return canonical_file(RUNTIME_FS_DUMP_PATH)


#########################################################################################################################
# Some helpers

def dump_queue(client: TYtClient):
    '''
    Dump queue content to queue_content file with mapping:
        Tablet {tablet id}: [ZDocId ...]

    Can be usefull for investigation if diff
    '''

    states = client.select_rows(f"* FROM [{QUEUE_PATH}/queue]")
    tablets: tp.List[tp.List[str]] = [[] for _ in range(SHARDS_CNT)]

    for tablet, rows in groupby(states, key=itemgetter("$tablet_index")):
        for row in sorted(rows, key=itemgetter("$row_index")):
            value = row["value"]
            queue_item = TMelterQueueItem()
            queue_item.ParseFromString(get_bytes(value))
            tablets[tablet].append(queue_item.ZDocId)

    with open(output_path("queue_content"), "w+") as f:
        for tablet, zdocids in enumerate(tablets):
            print(f"Tablet = {str(tablet)}: " + " ".join([str(zdocid) for zdocid in zdocids]), file=f)


def dump_runtime_fs():
    '''Dump runtime FS for test workers result'''

    logging.info("Dumping runtime FS")

    execute([
        MELTER_RUNTIME_FS_PRINTER, "PrintChunkDocs",
        "--cfg", MELTER_WORKER_CONFIG
    ], stdout=RUNTIME_FS_DUMP_PATH)

    logging.info("Runtime FS successfully dumped")


def run_worker(worker_id: int):
    stdout_ = "melter.{}.out".format(worker_id)
    stderr_ = "melter.{}.err".format(worker_id)

    execute([
        MELTER_WORKER_BIN,
        "Daemon",
        "--cfg", MELTER_WORKER_CONFIG,
        "--throw-error-after-consecutive-failed-iterations-cnt", "1"
    ], stdout=output_path(stdout_), stderr=output_path(stderr_))


async def run_workers(num_workers: int):
    '''Run workers simultaneously in num_workers processes'''

    logging.info("Running %d workers", num_workers)

    futures = [asyncio.to_thread(run_worker, worker_id) for worker_id in range(num_workers)]
    results = await asyncio.gather(*futures, return_exceptions=True)

    logging.info("Workers finished")

    failed_workers_ids = [id_ for id_, result in enumerate(results) if isinstance(result, Exception)]
    if failed_workers_ids:
        raise WorkersRunTimeException(failed_workers_ids)


def setup_configs(yt_proxy: str):
    '''Create test configs for worker'''

    execute([
        MELTER_CONFIG_GENERATOR_BIN,
        "--workers-count", str(WORKERS_CNT),
        "--cluster", yt_proxy,
        "--modifications-per-state", "100",
        "--queue-path", QUEUE_PATH,
        "--working-dir", WORKDIR_PATH,
        "--shards-count", str(SHARDS_CNT),
        "--loop-timer-phase", "5",
        "--max-duration-between-states", "5",
        "--idle-limit-iterations", "5",
        "--chunks-cnt", "4",
        "--max-items-per-read", "100",
        MELTER_CONFIG_TEMPLATE,
        MELTER_WORKER_CONFIG,
    ])


def prepare_local_yt_with_test_data(test_snapshot_dir: str) -> tp.Tuple[LocalYt, TYtClient]:
    '''Set up local YT cluster and upload test snapshot'''
    env = Environment()

    local_yt = LocalYt(
        yt_work_dir=YT_WORK_DIR,
        wait_tablet_cell_initialization=True,
        ram_drive_path=env.ram_drive_path
    )

    yt_client: YtClient = local_yt.create_yt_client()

    # Explicitly create BigRT queue over SHARDS_CNT shards
    create_queue(QUEUE_PATH, SHARDS_CNT, "default", None, "weak", False, yt_client)

    # Unmount table for script data uploading
    queue = TablePath(pj(QUEUE_PATH, "queue"))
    yt_client.unmount_table(queue, sync=True)

    # Upload data from test snapshot to local YT cluster
    local_yt.upload(test_snapshot_dir, MELTER_DIR, binary_content=True)

    dump_queue(yt_client)

    logging.info("Local YT prepared and run on proxy %s", local_yt.get_proxy())

    return local_yt, yt_client


def prepare_canonical_dir(canonical_dump_dir: str, mask: str = "***"):
    '''
    Replaces dates and uuids with mask
    {b10b3435-defb7264-132288a6-733b016} => {***}
    {2021-12-29T13:38:33.571669Z} => {***}
    '''

    datetime_reg = re.compile(r"\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(?:\.\d+)?Z?")
    uuid_ref = re.compile(r"(\w{4,}\-){3}\w{4,}")

    for file_ in Path(canonical_dump_dir).rglob("*.conf"):
        text = file_.read_text()
        updated_text = datetime_reg.sub(mask, text)
        updated_text = uuid_ref.sub(mask, updated_text)
        file_.write_text(updated_text)
