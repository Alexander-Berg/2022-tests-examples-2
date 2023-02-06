#!/usr/bin/env python3.7
import argparse
import pathlib
import typing

import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--value', type=str, required=True)
    return parser.parse_args()


def nested_set(
        mapping: typing.Dict,
        path: str,
        value: str,
) -> typing.Dict:
    """Function is used to change/set value for a key
    in nested dict-like structure. The path to key should be set
    using dot notation.
    Example:
        components_manager.components.place-pg-cache.full-update-interval
    """
    dictionary: typing.Dict = mapping
    keys = path.split('.')
    for key in keys[:-1]:
        if key in dictionary:
            dictionary = dictionary[key]
        else:
            return mapping
    if keys[-1] in dictionary:
        dictionary[keys[-1]] = value
    return mapping


def main():
    args = parse_args()
    config = pathlib.Path(args.config)
    path = args.path
    value = args.value
    if not config.is_file():
        raise RuntimeError(f'Config file {config} is not found')
    with open(config, 'r') as file:
        data = yaml.safe_load(file)

    updated = nested_set(data, path, value)

    with open(config, 'w') as out:
        yaml.dump(updated, out)


if __name__ == '__main__':
    main()
