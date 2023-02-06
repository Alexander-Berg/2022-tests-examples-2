import json
import re

# _QUEUE_KEY_FMT = '{}:queue'
_UPDATED_AT_KEY_FMT = '{}:upd:{}'
_RAW_GROUP_KEY_REGEXP_FMT = '{}:gr:.+'

_QUEUE_KEY_RE = re.compile(r'\w+:queue')
_UPDATED_AT_KEY_RE = re.compile(r'\w+:upd:.+')
_RAW_GROUP_KEY_RE = re.compile(r'\w+:gr:.+_.+')


def _extract_updated_at(redis_store, key):
    bytestr = redis_store.get(key)
    return bytestr.decode() if bytestr is not None else None


def _extract_keys(redis_store, **kwargs):
    iterator = redis_store.scan_iter(**kwargs)
    return [bytestr.decode() for bytestr in iterator]


def _extract_raw_event_group(redis_store, key):
    raw_values = redis_store.lrange(key, 0, -1)

    def _sort_key(raw_event_json):
        if 'timestamp' in raw_event_json:
            return raw_event_json['timestamp']
        return ''

    docs = [json.loads(bytestr.decode()) for bytestr in raw_values]
    return sorted(docs, key=_sort_key)


def get_dbsize(redis_store):
    return redis_store.dbsize()


def get_updated_at(redis_store, shard_number, group_identifier):
    key = _UPDATED_AT_KEY_FMT.format(shard_number, group_identifier)
    return _extract_updated_at(redis_store, key)


def get_raw_event_group_keys(redis_store, shard_number, prefix):
    match = _RAW_GROUP_KEY_REGEXP_FMT.format(shard_number, prefix)
    return _extract_keys(redis_store, match=match)


def get_raw_event_group_values(redis_store, shard_number, prefix):
    keys = get_raw_event_group_keys(redis_store, shard_number, prefix)

    result = []
    for key in keys:
        value = _extract_raw_event_group(redis_store, key)
        result.append(value)

    return result


def _put_raw_event_group(redis_store, key, doc_json):
    for raw_event in doc_json:
        if not isinstance(raw_event, dict):
            raise TypeError('invalid value, expected dict')
        redis_store.lpush(key, json.dumps(raw_event))


def _put_updated_at(redis_store, key, value):
    if not isinstance(value, str):
        raise TypeError('invalid value, expected string')
    redis_store.set(key, value)


def prepare_storage(redis_store, doc):
    for key in doc:
        try:
            if _UPDATED_AT_KEY_RE.match(key):
                _put_updated_at(redis_store, key, doc[key])
            elif _RAW_GROUP_KEY_RE.match(key):
                _put_raw_event_group(redis_store, key, doc[key])
            else:
                raise KeyError('Unknown key in your doc: "{}"'.format(key))
        except Exception as exc:
            raise ValueError(
                'Invalid value at key "{}" causes error: {}'.format(
                    key, str(exc),
                ),
            )


def get_state_as_doc(redis_store):
    keys = _extract_keys(redis_store)
    doc = dict()
    for key in keys:
        try:
            if _UPDATED_AT_KEY_RE.match(key):
                doc[key] = _extract_updated_at(redis_store, key)
            elif _RAW_GROUP_KEY_RE.match(key):
                doc[key] = _extract_raw_event_group(redis_store, key)
            else:
                raise KeyError(
                    'Unknown key '
                    '(do not know how to read it): "{}"'.format(key),
                )
        except Exception as exc:
            raise Exception(
                'Failed to read by key {}: {}'.format(key, str(exc)),
            )
    return doc
