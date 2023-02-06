import contextlib
import struct
import threading
import typing
from unittest import mock

import bson.json_util
import bson.objectid
import pymongo
from motor import motor_asyncio

DocumentT = typing.Any
CollectionT = typing.List[DocumentT]


async def dump(uri: str) -> bytes:
    """Dump db contents to JSON bytes."""
    client = motor_asyncio.AsyncIOMotorClient(uri)
    db = client.get_default_database()
    collection_names = await db.list_collection_names()
    exported_db = {}
    for collection_name in collection_names:
        exported_db[collection_name] = []
        cursor = db[collection_name].find()
        async for document in cursor:
            exported_db[collection_name].append(document)
    return bson.json_util.dumps(exported_db, indent=4, sort_keys=True).encode()


async def load(uri: str, data: bytes) -> None:
    """Load db from JSON bytes."""
    client = motor_asyncio.AsyncIOMotorClient(uri)
    db = client.get_default_database()
    for collection_name, documents in bson.json_util.loads(data).items():
        await db[collection_name].insert_many(documents)


@contextlib.asynccontextmanager
async def keep_db_clean_async(uri: str) -> None:
    try:
        yield
    finally:
        client = motor_asyncio.AsyncIOMotorClient(uri)
        await client.drop_database(client.get_default_database())


@contextlib.contextmanager
def keep_db_clean(uri: str) -> None:
    try:
        yield
    finally:
        client = pymongo.MongoClient(uri)
        client.drop_database(client.get_default_database())


COUNTER_LOCK = threading.Lock()
COUNTER = {"counter": 0}


@contextlib.contextmanager
def predictable_object_id() -> typing.Generator[None, None, None]:
    real_init = bson.objectid.ObjectId.__init__

    def fake_init(self, oid=None):
        if oid is None:
            # 4 bytes current time
            oid = b"\x00\x00\x00\x00"

            # 5 bytes random
            oid += b"\x00\x00\x00\x00\x00"

            # 3 bytes inc
            with COUNTER_LOCK:
                COUNTER["counter"] += 1
                counter = COUNTER["counter"]
            oid += struct.pack(">I", counter)[-3:]

            real_init(self, oid=oid)
        else:
            real_init(self, oid=oid)

    with mock.patch.object(bson.objectid.ObjectId, "__init__", new=fake_init):
        try:
            yield
        finally:
            with COUNTER_LOCK:
                COUNTER["counter"] = 0
