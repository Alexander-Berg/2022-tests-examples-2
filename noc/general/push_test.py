#!/usr/bin/env python3
# How to get dump?
# ssh host "slbch_client.py -n -o -" > host_dump.data
import asyncio
import gzip
import io
import json
import logging
import os.path
import time
from typing import Any, Dict, List

import aiohttp


def gzip_str(data: str) -> bytes:
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='w') as fo:
        fo.write(data.encode())
    bytes_obj = out.getvalue()
    return bytes_obj


async def post(url: str, data: str) -> None:
    data = gzip_str(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers={"Content-Encoding": "gzip"}) as resp:
            logging.debug("got %s", resp.status)


async def send(items: List[Dict[str, Any]], url) -> None:
    tasks = []
    for item in items:
        item["sta"]["ts"] = int(time.time())
        tasks.append(asyncio.Task(post(url, data=json.dumps(item))))
    logging.debug("start http sender")
    await asyncio.wait(tasks)


async def pusher(files: List[str], url: str) -> None:
    files_content = {}
    for file in files:
        with open(file, "r") as f:
            files_content[file] = json.load(f)
    while True:
        try:
            await send(list(files_content.values()), url)
        except Exception as e:
            print(e)
        time.sleep(5)


def main() -> None:
    url = "http://localhost:8000/api/v1/write"
    file = "host_dump2.data"
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file)

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(name)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s")
    asyncio.get_event_loop().run_until_complete(pusher(files, url))


if __name__ == "__main__":
    main()
