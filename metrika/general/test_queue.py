import os
import logging
import datetime
import threading

import psycopg2.errors as errors

import metrika.admin.python.cms.lib.pg.queue as queue
import metrika.admin.python.cms.lib.pg.connection_manager as connection_manager
import metrika.admin.python.cms.lib.wait as wait

logger = logging.getLogger(__name__)

pg_kwargs = {
    "host": os.getenv("POSTGRES_RECIPE_HOST"),
    "port": os.getenv("POSTGRES_RECIPE_PORT"),
    "dbname": os.getenv("POSTGRES_RECIPE_DBNAME"),
    "user": os.getenv("POSTGRES_RECIPE_USER"),
}


def producer(identity, n):
    logger.info("Starting producer {}".format(identity))
    try:
        q = queue.Queue(str(identity), "queue1", connection_manager.ConnectionManager(**pg_kwargs))

        total_items = n
        current_items = 0
        while current_items < total_items:
            logger.info("Current_items: {} total_items: {}".format(current_items, total_items))
            try:
                q.put({"producer": str(identity), "item": str(current_items)})
                current_items += 1
            except errors.DatabaseError:
                logger.warning("Temporary error. Continue iterations.", exc_info=True)
    except Exception:
        logger.exception("Unexpected exception in consumer")
    logger.info("Exiting producer")


def consumer(output, identity, event):
    logger.info("Starting consumer {}".format(identity))
    try:
        q = queue.Queue(str(identity), "queue1", connection_manager.ConnectionManager(**pg_kwargs))
        while not event.is_set():
            try:
                logger.info("Start iteration")
                with q.try_get_item() as item:
                    if item.is_aquired:
                        logger.info("Aquired {} {}".format(item.row_id, item.value))
                        output.append(item.value)
                        item.consume()
                    else:
                        logger.warning("Not aquired - proceed next iteration")
            except errors.DatabaseError:
                logger.warning("Temporary error. Continue iterations.", exc_info=True)
    except Exception:
        logger.exception("Unexpected exception in consumer")
    logger.info("Exiting consumer")


def test_queue():
    """
    создаём n consumer'ов
    в создаём m producer'ов с заданием создать k заданий

    Проверяем, что в сумме все consumer'ы обработали m*k заданий
    :return:
    """

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(threadName)-12.12s %(processName)-12.12s %(name)48.48s %(levelname)-.1s %(message)s')

    result = {}

    n_consumers = 3  # n
    n_producers = 2  # m
    items_per_producer = 20  # k

    consumers = {}
    for indx in range(n_consumers):
        output = list()
        result[str(indx)] = output
        event = threading.Event()
        proc = threading.Thread(target=consumer, args=(output, indx, event), daemon=True)
        proc.start()
        consumers[indx] = (proc, event)

    producers = []
    for indx in range(n_producers):
        proc = threading.Thread(target=producer, args=(indx, items_per_producer), daemon=True)
        proc.start()
        producers.append(proc)

    logger.info("Consumers: {}".format([proc.ident for (proc, _) in consumers.values()]))
    logger.info("Producers: {}".format([proc.ident for proc in producers]))

    for p in producers:
        p.join()

    def predicate():
        msg = []
        total = 0
        for k, v in result.items():
            msg.append("{}:{}".format(k, list(v)))
            total += len(v)
        msg = ["Total items: {}".format(total)] + msg
        logger.info("\n".join(msg))
        return total == n_producers * items_per_producer

    wait.wait_until(predicate, timeout=datetime.timedelta(minutes=2), poll_period=datetime.timedelta(seconds=2), initial_sleep=True)

    for (proc, event) in consumers.values():
        event.set()
        proc.join()

    expected_items = n_producers * items_per_producer
    actual_items = sum([len(vs) for vs in result.values()])

    assert expected_items == actual_items


def test_queue_consumation():
    q = queue.Queue("some id", "queue2", connection_manager.ConnectionManager(**pg_kwargs))

    q.put({"some": "data"})

    with q.try_get_item() as item:
        assert item.is_aquired

    with q.try_get_item() as item:
        assert item.is_aquired


def test_queue_consumation_handling():
    q = queue.Queue("some id", "queue3", connection_manager.ConnectionManager(**pg_kwargs))

    q.put({"some": "data"})

    with q.try_get_item() as item:
        item.consume()

    with q.try_get_item() as item:
        assert not item.is_aquired


def test_queue_postpone():
    q = queue.Queue("some id", "queue4", connection_manager.ConnectionManager(**pg_kwargs))
    q.put({"some": "data"})

    with q.try_get_item() as item:
        item.defer_until(datetime.datetime.now() + datetime.timedelta(seconds=10))

    with q.try_get_item() as item:
        assert not item.is_aquired

    def predicate():
        with q.try_get_item() as item:
            return item.is_aquired

    wait.wait_until(predicate, timeout=datetime.timedelta(seconds=20))
