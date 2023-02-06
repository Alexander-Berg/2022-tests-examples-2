#!/usr/bin/python3

import argparse
import sys

import requests


def flatten_json(prefix, obj):
    result = {}
    for key in obj:
        if key == '$meta':
            # currently no metadata is used for graphite/text output
            continue
        if prefix:
            prefixed_key = prefix + '.' + key.replace('.', '_')
        else:
            prefixed_key = key.replace('.', '_')
        value = obj[key]
        if isinstance(value, dict):
            values = flatten_json(prefixed_key, value)
            result.update(values)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            result[prefixed_key] = value
        elif isinstance(value, str):
            result[prefixed_key] = value
        elif value is None:
            pass
        else:
            try:
                result[prefixed_key] = float(value)
            except ValueError as e:
                sys.stderr.write(
                    'Error converting metric {}: {} ({})\n'.format(
                        prefixed_key, e, value,
                    ),
                )
            except TypeError as e:
                sys.stderr.write(
                    'Error converting metric {}: {} ({})\n'.format(
                        prefixed_key, e, value,
                    ),
                )
    return result


def handle_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--hostname',
        help='Hostname and monitor port of test-service service',
        default='[::1]:1188',
        type=str,
    )
    parser.add_argument('--url', help='statistics url', default='/', type=str)
    parser.add_argument(
        '--timeout', help='HTTP timeout (in seconds)', default=5, type=float,
    )
    parser.add_argument(
        'url_prefix',
        type=str,
        nargs='?',
        help='Shows metrics starting with this prefix (a hint for the server)',
    )
    opts = parser.parse_args()
    return opts


def main():
    opts = handle_options()

    url = 'http://' + opts.hostname + opts.url
    if opts.url_prefix:
        url += '?prefix=' + opts.url_prefix
    r = requests.get(url, timeout=opts.timeout)
    r.raise_for_status()

    j = r.json()

    j.pop('$version', 1)  # not used here

    fl = flatten_json('', j)
    for k in sorted(fl):
        print('{} {}'.format(k, fl[k]))


if __name__ == '__main__':
    main()
