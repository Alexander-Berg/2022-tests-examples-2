from ads.bsyeti.big_rt.py_lib import YtQueue
from yt.wrapper.http_helpers import get_proxy_url

from os.path import join as pj
from retrying import retry
import logging


def check_cannot_read_any_message(queue, consumer):
    try:
        consumer_offsets = queue["queue"].get_consumer_offsets(consumer)
    except Exception:
        logging.exception("Can't get consumer offsets or actual table size")
        return False
    for shard in range(queue["shards"]):
        consumer_offset = consumer_offsets[shard]
        if consumer_offset == queue["queue"].unreachable_offset:
            continue
        messages_not_consumed = queue["queue"].read_messages(shard, consumer_offset + 1, 1)
        if messages_not_consumed:
            return False
    logging.info("All messages in all shards for queue {} are read".format(queue["path"]))
    return True


def wait_queue_fully_consumed(local_blrt, queue_relative_path, consumer, timeout=600):
    yt_cluster = get_proxy_url(client=local_blrt.yt_client)
    queue_full_path = pj(local_blrt.yt_prefix, queue_relative_path)

    queue = {
        "cluster": yt_cluster,
        "path": queue_full_path,
        "shards": local_blrt.yt_client.get(pj(queue_full_path, "queue", "@tablet_count")),
        "queue": YtQueue({"path": queue_full_path, "cluster": yt_cluster}),
    }

    @retry(stop_max_delay=timeout * 1000, wait_fixed=5000)
    def check_queue_fully_consumed():
        logging.info("Checking for QYT {} to be fully consumed...".format(queue_full_path))
        assert check_cannot_read_any_message(queue, consumer)

    check_queue_fully_consumed()
    logging.info("QYT {} has been successfully fully consumed...".format(queue_full_path))
