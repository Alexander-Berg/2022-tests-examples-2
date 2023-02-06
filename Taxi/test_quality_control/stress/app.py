import argparse
import asyncio
import sys

from test_quality_control.stress import init
from test_quality_control.stress import load

ACTION_AMMO = 'ammo'
ACTION_INIT = 'init'
HOST = 'http://mletunov.vla.yp-c.yandex.net'


def main(args):
    parser = argparse.ArgumentParser(description='Stress testing')
    parser.add_argument(
        '-a',
        '-action',
        dest='action',
        type=str,
        choices=[ACTION_AMMO, ACTION_INIT],
    )
    parser.add_argument(
        '-m',
        '-mode',
        dest='mode',
        type=str,
        choices=[
            load.Mode.DATA_LOAD,
            load.Mode.STATE_ID,
            load.Mode.STATE_LIMIT,
            load.Mode.STATE_LOAD,
            load.Mode.STATE_ENABLE_PARKS,
            load.Mode.STATE_ENABLE_CITY,
        ],
    )
    result = parser.parse_args(args)

    tasks = []
    if result.action == ACTION_AMMO:
        tasks.append(load.generate_bullets(HOST, result.mode))
    elif result.action == ACTION_INIT:
        tasks.append(init.prepare(HOST))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':
    main(sys.argv[1:])
