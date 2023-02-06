#!/usr/bin/env python3
import argparse
import asyncio
import logging
import os
from functools import partial

os.environ["COMOCUTOR_NO_NOCAUTH"] = "1"
from comocutor.devices import AutoDevice, ConnFabric, VrpDevice, ADVADevice, IosDevice, JnxDevice, PCDevice, \
    EkinopsDevice
from comocutor.streamer import SshStream

template = """from tests.data.lib import Data


class Data1(Data):
    content = \"\"\"
{content}
    \"\"\"
    cmd = "{cmd}"
    host = "{host}"
    version = \"\"\"
{version}
    \"\"\"
    result = None  # insert parsed result here
"""


async def main(host, cmd):
    ssh_partial = partial(SshStream, host=host)
    fabric = ConnFabric(stream=ssh_partial)
    # change here to PCDevice to make unix tests:
    host_conn = AutoDevice(conn_fabric=[fabric], name=host)
    await host_conn.connect(timeout=20)

    if isinstance(host_conn, VrpDevice):
        version = await host_conn.cmd("dis ver")
    elif isinstance(host_conn, ADVADevice):
        version = await host_conn.cmd("show software release-manifest")
    elif isinstance(host_conn, (IosDevice, JnxDevice)):
        version = await host_conn.cmd("show version")
    elif isinstance(host_conn, PCDevice):
        version = await host_conn.cmd("uname -a")
    elif isinstance(host_conn, EkinopsDevice):
        version = await host_conn.cmd("version")
    else:
        raise Exception("do not know how to get version")
    cmd_res = await host_conn.cmd(cmd)

    version = version.out
    res = template.format(**{"host": host, "cmd": cmd, "version": version, "content": cmd_res.out})
    await host_conn.close()
    await asyncio.sleep(0.01)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make a test file')
    parser.add_argument("--host", help="target host", required=True)
    parser.add_argument("--cmd", help="command to run", required=True)
    parser.add_argument("--outfile", help="name of new test file", required=True)
    parser.add_argument("-d", "--debug", help="debug")
    args = parser.parse_args()
    filename = args.outfile

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level,
                        format="%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s")

    if not filename.endswith(".py"):
        filename = filename + ".py"
    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", filename)
    if os.access(outfile, os.R_OK):
        raise Exception("%s already exists" % outfile)

    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(main(args.host, args.cmd))
    with open(outfile, "w+") as f:
        f.write(res)
