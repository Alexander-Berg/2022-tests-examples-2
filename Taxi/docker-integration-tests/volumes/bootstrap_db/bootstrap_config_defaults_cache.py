#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
from __future__ import unicode_literals

import json

import bootstrap_schemas

PATH_TO_CACHE = '/taxi/cache_dumps/config_defaults.json'


def init():
    config_defaults = {}
    for (
        config_name, config_schema,
    ) in bootstrap_schemas.SCHEMAS.iteritems():  # pylint: disable=E1101
        config_defaults[config_name] = {
            'name': config_name,
            'updated': '1970-01-01T00:00:00+00:00',
            'c': '',
            't': '',
            'stage_name': '',
            'v': config_schema['default'],
        }
    config_defaults = {'commit': 'master', 'configs': config_defaults}
    with open(PATH_TO_CACHE, 'w') as dump_file:
        json.dump(config_defaults, dump_file)
    print('Successfully update configs default cache')


if __name__ == '__main__':
    init()
