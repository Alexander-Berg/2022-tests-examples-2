import copy
import datetime

import dateutil.parser

from tests_plugins import utils


def check_mongo(db, db_extra, expected_tasks, queue_name):
    for stq_config in db.stq_config.find():
        shards = stq_config['shards']
        if stq_config['_id'] == queue_name:
            check_queue_with_tasks(db_extra, shards, expected_tasks)
        else:
            check_empty_queue(db_extra, shards)


def check_queue_with_tasks(db_extra, shards, expected_tasks):
    tasks_count = 0
    expected_tasks = {task['_id']: task for task in expected_tasks}
    tasks_ids = list(expected_tasks.keys())
    found_tasks = {}
    for shard in shards:
        collection = db_extra.shard_collection(shard)
        tasks_count += collection.count()
        tasks = collection.find({'_id': {'$in': tasks_ids}}, {'ti': 0})
        found_tasks.update({task['_id']: task for task in tasks})
    assert found_tasks == expected_tasks
    assert tasks_count == len(expected_tasks)


def check_empty_queue(db_extra, shards, except_shards=None):
    for shard in shards:
        must_be_empty = (
            not shard_is_excepted(shard, except_shards)
            if except_shards
            else True
        )
        if must_be_empty:
            collection = db_extra.shard_collection(shard)
            assert collection.count() == 0


def make_expected_task(request_body, eta_updated):
    eta = to_msec_from_epoch(request_body['eta'])
    return {
        '_id': request_body['task_id'],
        't': 0.0,
        'a': request_body['args'].copy(),
        'k': copy.deepcopy(request_body['kwargs']),
        'f': 0,
        'e': eta,
        'e_dup': eta,
        'eu': to_msec_from_epoch(eta_updated.isoformat()),
        'tag': request_body['tag'] if 'tag' in request_body else None,
    }


def to_msec_from_epoch(date_time_str):
    epoch = datetime.datetime.utcfromtimestamp(0)
    timestamp = utils.to_utc(dateutil.parser.parse(date_time_str))
    return (timestamp - epoch).total_seconds()


def shard_is_excepted(shard, except_shards):
    for except_shard in except_shards:
        if shard['collection'] == except_shard['collection']:
            return True
    return False
