import typing
import uuid
from random import randrange


def shard_by_eid(eid: typing.Union[str, list, tuple]):
    if isinstance(eid, (list, tuple)):
        eid = '::'.join(eid)
    return int('0x' + eid[32:], 0)

def shard_by_key(key: typing.Union[list, tuple, int, str]):
    if isinstance(key, (int, str)):
        key = [key]

    return shard_by_idstr('::'.join(key))


def eid_for_shard(shard: typing.Optional[int]):
    if shard is None:
        shard = randrange(2)

    while True:
        idstr = uuid.uuid4().hex
        if shard_by_idstr(idstr) == shard:
            return '%s%04x' % (idstr, shard)


def shard_by_idstr(idstr):

    hvalue = ord(idstr[-2]) * 256 + ord(idstr[-1])

    # в 30% случаев даст 1
    return 0 if hvalue % 100 < 30 else 1
