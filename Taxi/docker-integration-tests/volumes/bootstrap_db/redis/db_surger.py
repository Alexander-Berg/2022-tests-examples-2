#!/usr/bin/env python
# -*- coding: utf-8 -*

import json
import os
import time


def _get_data_dir():
    return '{}/db_surger'.format(os.path.dirname(os.path.realpath(__file__)))


def _get_file_path(file_name):
    return '{}/{}'.format(_get_data_dir(), file_name)


def _load_binary(file_path):
    with open(file_path, 'rb') as file_handle:
        return file_handle.read()


def _populate_data(connection):
    timestamp = int(time.time())

    grid_desc = {
        'CellSize': 250,
        'GridId': '15450017746124931280',
        'RegionId': '15450017746124931280_%i' % timestamp,
        'Updated': timestamp,
        'TlBr': {
            'Bottom': 55.472370163516132,
            'Left': 37.135591841918192,
            'Right': 38.077641704627929,
            'Top': 56.003460457113277,
        },
    }

    connection.hset(
        'CPP:SURGE_FULL:GRID:DESC',
        '15450017746124931280',
        json.dumps(grid_desc),
    )

    connection.set(
        'CPP:SURGE_FULL:GRID:BINARY:15450017746124931280',
        _load_binary(_get_file_path('grid.bin')),
    )

    connection.set(
        'CPP:SURGE_FULL:VALUES:BINARY:15450017746124931280_%i' % timestamp,
        _load_binary(_get_file_path('cells.bin')),
    )


def populate_data(connection):
    _populate_data(connection)
