#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

import yatest.common

KWDUMPWORK_BIN = yatest.common.binary_path('robot/jupiter/tools/kwdumpwork/kwdumpwork')

def test_link_mapper():
    # our config requires data files in the current directory
    for file in os.listdir('link-data'):
        os.symlink(os.path.realpath(os.path.join('link-data', file)), file)

    subprocess.check_call([
        KWDUMPWORK_BIN,
        '--input=input.yson:yson',
        '--map=builtin://robot/library/oxygen/config/files/mapper/Links.pb.txt',
        '--output=output:name2tuples',
    ])
    return yatest.common.canonical_file('output')
