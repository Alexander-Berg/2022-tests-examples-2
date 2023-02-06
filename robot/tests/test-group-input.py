#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import yatest.common

KWDUMPWORK_BIN = yatest.common.binary_path('robot/jupiter/tools/kwdumpwork/kwdumpwork')

def test_cat_stream():
    with open("input1", 'w') as outf:
        print >>outf, "foo"
        print >>outf, "bar"

    with open("input2", 'w') as outf:
        print >>outf, "baz"

    with open("input3", 'w') as outf:
        print >>outf, "qux"

    out = subprocess.check_output([
        KWDUMPWORK_BIN,
        '--field-read=input1:Name',
        '--field-read=input2:Name',
        '--field-read=input3:Name',
        '--group-input=3',
        '--transform=Surname="variable"',
        '--field-write=-:Name,Surname',
    ])
    assert out == (
        "foo\tvariable\n"
        "bar\tvariable\n"
        "baz\tvariable\n"
        "qux\tvariable\n"
    )
