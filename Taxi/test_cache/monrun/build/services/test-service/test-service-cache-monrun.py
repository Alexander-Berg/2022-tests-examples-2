#!/usr/bin/env python3

import json
import subprocess
import sys


SERVICE = 'test-service'
FS_CACHE_PATH = '/var/cache/yandex/taxi-test-service/config_cache.json'
CONFIG_NAME = 'MONRUN_CONFIG'
STATS_EXE = 'taxi-{}-stats.py'.format(SERVICE)

LEVEL_ERROR = 2
LEVEL_WARNING = 1
LEVEL_OK = 0


def read_cache_config():
    with open(FS_CACHE_PATH) as fi:
        return json.loads(fi.read())[CONFIG_NAME]


def read_current_values():
    args = [STATS_EXE, 'cache']
    try:
        output = subprocess.check_output(args).decode('utf-8')
    except Exception:  # pylint: disable=broad-except
        print('2;service is not alive')
        sys.exit(1)
    values = [line.split(' ') for line in output.split('\n') if line]

    CACHE_AGE_SUFFIX = 'any.time.time-from-last-successful-start-ms'
    CACHE_PREFIX = 'cache'
    cache_values = dict()
    for key, value in values:
        if key.endswith(CACHE_AGE_SUFFIX):
            cache_name = key[len(CACHE_PREFIX) + 1:-len(CACHE_AGE_SUFFIX) - 1]
            cache_age = float(value)
            cache_values[cache_name] = cache_age
    return cache_values


def monrun_check(config, values):
    def get(name):
        fallback = {'error-ms': 0, 'warning-ms': 0}
        return config.get(name, config.get('default', fallback))

    level = LEVEL_OK
    msgs = []
    for config_name in sorted(values):
        value = values[config_name]
        config_levels = get(config_name)
        warn, err = config_levels['warning-ms'], config_levels['error-ms']

        if err > 0 and value > err:
            level = LEVEL_ERROR
            msgs.append('{} CRITICAL ({} ms > {} ms)'.format(
                config_name, value, err,
            ))
        elif warn > 0 and value > warn:
            if level < LEVEL_WARNING:
                level = LEVEL_WARNING
            msgs.append('{} WARNING ({} ms > {} ms)'.format(
                config_name, value, warn,
            ))

    if level == LEVEL_OK:
        msg = 'OK'
    else:
        msg = ', '.join(msgs)
    return level, msg


def main():
    cache_config = read_cache_config()
    current_values = read_current_values()
    level, msg = monrun_check(cache_config, current_values)
    print('{};{}'.format(level, msg))


if __name__ == '__main__':
    main()
