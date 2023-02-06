import freeswitch_testsuite.cases as cases
from argparse import ArgumentParser
from asyncio import AbstractEventLoop, get_event_loop, sleep
from freeswitch_testsuite.environment_config import BASE, make_environment
from freeswitch_testsuite.freeswitch import FreeSwitch
from freeswitch_testsuite.ivr_dispatcher import MockDispatcher
from freeswitch_testsuite.logs import log_debug, log_info, log_error
from freeswitch_testsuite.metrics import collect_metrics
from freeswitch_testsuite.sip_b2b_ua import B2BUA
from freeswitch_testsuite.speechkit import MockSk
from inspect import getmembers, isfunction
from sys import exit
from shutil import rmtree
from termcolor import colored
from typing import List


def is_test(obj) -> bool:
    if isfunction(obj):
        name: str = obj.__name__
        return name.startswith('test_')
    return False


def get_cases() -> List:
    case_list: List = []
    for _, case_func in getmembers(cases, is_test):
        case_list.append(case_func)
    return case_list


async def run_tests(loop):
    calls: B2BUA = B2BUA(loop)
    ivr_disp: MockDispatcher = await MockDispatcher(loop).start()
    sk_mock: MockSk = await MockSk(loop).start()
    failed: int = 0
    passed: int = 0
    current: int = 0
    my_cases: List = get_cases()
    for case in my_cases:
        log_debug(f'Preparing {case.__name__}')
        current += 1
        # Reset environment
        await collect_metrics()
        calls.reset()
        sk_mock.reset()
        await ivr_disp.reset()
        case_name: str = f'[{current} of {len(my_cases)}]: {case.__name__}'
        try:
            await case(calls, ivr_disp, sk_mock)
            passed += 1
            log_info(f'Case {case_name:<60} {colored("OK", "green"):>5}')
        except Exception:
            failed += 1
            log_error(f'Case {case_name:<60} {colored(f"FAIL!", "red"):>5}',
                      print_trace=True)
        # Prevent throttle error in FS
        await sleep(0.5)
    log_info(
        f'{len(my_cases)} tests executed. '
        f'{colored(f"{passed} passed", "green")}, '
        f'{colored(f"{failed} failed", "green" if failed < 1 else "red")}')
    calls.stop()
    await sk_mock.stop()
    # wait to allow all entities from
    # another threads to complete
    await sleep(0)
    calls.libDestroy()
    await ivr_disp.stop()


def main():
    parser = ArgumentParser(description='freeswitch path')
    parser.add_argument('--path', type=str, required=True)
    args = parser.parse_args()
    if not args.path:
        print('Error: Path to FS binary not provided')
        exit(-1)
    loop: AbstractEventLoop = get_event_loop()
    rmtree(BASE, ignore_errors=True)
    make_environment()
    fs: FreeSwitch = loop.run_until_complete(
        FreeSwitch(args.path).start())
    try:
        loop.run_until_complete(run_tests(loop))
    except Exception as exc:
        log_error(f'General error: {exc}', print_trace=True)

    if fs:
        loop.run_until_complete(fs.stop())


if __name__ == '__main__':
    main()
