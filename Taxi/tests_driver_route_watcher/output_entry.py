# pylint: disable=import-error
import asyncio

import tests_driver_route_watcher.output_entry_fbs as OutputEntryFbs


def _to_dbid_uuid(driver_id):
    uuid = driver_id['uuid']
    dbid = driver_id['dbid']
    return '_'.join([dbid, uuid])


def get_output(redis_store, driver_id):
    key = 'output:{' + _to_dbid_uuid(driver_id) + '}'
    data = redis_store.hget(key, 'output')
    output = OutputEntryFbs.deserialize_output_entry(data) if data else None
    force_log_raw = redis_store.hget(key, 'force_log')
    force_log = int(force_log_raw) if force_log_raw else None
    if not output and not force_log:
        return None
    ret = {}
    if output:
        ret.update(output)
    if force_log:
        ret.update({'force_log': force_log})
    return ret


async def wait_output(redis_store, driver_id, tries=50, timeout=0.3):
    for _ in range(tries):
        ret = get_output(redis_store, driver_id)
        if ret is not None:
            return ret
        await asyncio.sleep(timeout)
    raise Exception('Timeout on wait output')


async def wait_output_deleted(redis_store, driver_id, tries=50, timeout=0.3):
    for _ in range(tries):
        ret = get_output(redis_store, driver_id)
        if ret is None:
            return True
        await asyncio.sleep(timeout)
    raise Exception('Timeout on wait output deleted')
