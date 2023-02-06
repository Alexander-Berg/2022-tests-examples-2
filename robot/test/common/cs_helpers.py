from ads.bsyeti.big_rt.py_lib import ConsumingSystemReflection
from yt.wrapper.http_helpers import get_proxy_url
from retrying import retry
import logging
import os


def get_consuming_system_total_lag_info(yt_client, consuming_system_path):
    total_messages, message_lag = 0, 0

    if not yt_client.exists(os.path.join(consuming_system_path, "suppliers")):
        logging.info("Suppliers directory for consuming system {} has not been created yet".format(consuming_system_path))
        return total_messages, message_lag

    os.environ["YT_PROXY"] = get_proxy_url(client=yt_client)
    for supplier, shards_info in ConsumingSystemReflection(consuming_system_path).get_suppliers_shard_info().items():
        for shard, shard_info in shards_info.items():
            total_messages += shard_info["total_messages"]
            message_lag += shard_info["message_lag"]
    logging.info("Consuming system {} has {} total message and {} message lag".format(consuming_system_path, total_messages, message_lag))
    return total_messages, message_lag


def wait_consuming_system_fully_consumed(local_blrt, consuming_system_relative_path, timeout=600):
    consuming_system_path = os.path.join(local_blrt.yt_prefix, consuming_system_relative_path)

    @retry(stop_max_delay=timeout * 1000, wait_fixed=5000)
    def check_consuming_system_fully_consumed():
        logging.info("Checking for consuming system {} to be fully consumed...".format(consuming_system_path))
        total_messages, message_lag = get_consuming_system_total_lag_info(local_blrt.yt_client, consuming_system_path)
        assert total_messages > 0 and message_lag == 0

    check_consuming_system_fully_consumed()
    logging.info("Consuming system {} has been successfully fully consumed...".format(consuming_system_path))
