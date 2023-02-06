import socket
import urllib.parse

import pytest


def test_db_connection(mongo_url):
    url = urllib.parse.urlparse(mongo_url)
    assert url.hostname
    assert url.port
    sock = socket.create_connection((url.hostname, url.port), 0.1)
    sock.send(b"\n")


@pytest.mark.asyncio
async def test_db_avail(core):
    col = core.db["some_collection"]
    some = {
        "some-key": "some-value",
    }
    await col.insert_one(some)
    doc = await col.find_one({}, dict.fromkeys(some.keys(), True))
    assert doc == some
