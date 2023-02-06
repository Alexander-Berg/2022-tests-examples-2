#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

import pytest
import yatest.common

KWDUMPWORK_BIN = yatest.common.binary_path('robot/jupiter/tools/kwdumpwork/kwdumpwork')

@pytest.mark.parametrize("output_format", [
    'dump',
    'protobin',
    'prototext',
    'yson',
    'protobin-yamr',
    'name2tuples',
])
def test_output(output_format):
    output_file_name = 'result.{}'.format(output_format)
    subprocess.check_call([
        KWDUMPWORK_BIN,
        '--input=ozon_pers_dump.protobin_yamr:protobin-yamr',
        '--output={file}:{format}'.format(file=output_file_name, format=output_format)
    ])
    return yatest.common.canonical_file(output_file_name)
