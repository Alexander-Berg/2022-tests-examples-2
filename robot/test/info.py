import re
import yatest.common

def name():
    return yatest.common.context.test_name

def directory():
    return yatest.common.work_path()


def setup_environ(environ, test_time=None, test_rand=True):
    if test_time is not None:
        environ['TEST_TIME'] = str(test_time)
    if test_rand:
        environ['TEST_RANDOM'] = 'TRUE'
    return environ

def is_known_table(table_name):
    prefixes = (
        "counters/tmp/vintage_map.shard.(?P<shard_id>[0-9]{8})",
        "data/(?P<shard_id>[0-9]{8})/delta/incoming",
        "data/(?P<shard_id>[0-9]{8})/persistent",
        "data/(?P<shard_id>[0-9]{8})/global",
        "data/(?P<shard_id>[0-9]{8})/preparat/inliks",
        "data/(?P<shard_id>[0-9]{8})/queue",
        "data/(?P<shard_id>[0-9]{8})/tmp/combine",
        "data/(?P<shard_id>[0-9]{8})/views",
        "exports/dump/(?P<shard_id>[0-9]{8})",
        "factors/dump/(?P<shard_id>[0-9]{8})",
        "preparat/seomarkfactors/(?P<shard_id>[0-9]{8})",
        "log/vintage_",
        "redirect/incoming",
        "incoming/final",
        "sendlink/incoming"
    )
    for prefix in prefixes:
        if re.match(prefix, table_name):
            return True
    return False
