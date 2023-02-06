#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

import yatest.common

KWDUMPWORK_BIN = yatest.common.binary_path('robot/jupiter/tools/kwdumpwork/kwdumpwork')

# TODO: factorize heavily with test-arcdir.py

def test_pruning_processor():
    work_dir = "processor_output"

    PRUNING_OPTIONS = '''
        Shard {
            OutputDir: "."
        }
        Sorter {
            Pruning {
                SelectionRankName: "rus"
                RankValuesTupleName: "SelectionRanks"
                UrlTupleName: "Url"
                IsRequired: false
            }
        }
        PlainTextOptions {
            TupleName: "Url"
            OutputFileName: "urls.txt"
        }
    '''

    input_file = os.path.realpath('input.dump.snappy')
    kwdumpwork_err = os.path.realpath('kwdumpwork.err')

    index_options = os.path.realpath('index-options.pb.txt')
    with open(index_options, 'w') as outf:
        print >>outf, PRUNING_OPTIONS

    cur_dir = os.getcwd()
    os.mkdir(work_dir)
    try:
        os.chdir(work_dir)

        subprocess.check_call([
            KWDUMPWORK_BIN,
            '--input', '{input_file}:dump'.format(input_file=input_file),
            '--index', index_options,
        ], stderr=open(kwdumpwork_err, 'w'))

        result = list(sorted(os.listdir('.')))
        for r in result[:]:
            result.append(yatest.common.canonical_file(r))

        return result
    finally:
        os.chdir(cur_dir)

