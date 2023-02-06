#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import subprocess
import shutil

import yatest.common

KWDUMPWORK_BIN = yatest.common.binary_path('robot/jupiter/tools/kwdumpwork/kwdumpwork')

WITHOUT_SORTER = 1
WITH_SORTER_NO_DELETION = 2
WITH_SORTER_WITH_DELETION = 4

def mode2str(mode):
    return {
        WITHOUT_SORTER: "without_sorter",
        WITH_SORTER_NO_DELETION: "with_sorter_no_deletion",
        WITH_SORTER_WITH_DELETION: "with_sorter_with_deletion",
    }[mode]

def run_processor_test(
    config,
    input_file_name,
    input_file_format,
    test_name=None,
    run_without_sorter=True,
    run_with_sorter_no_deletion=True,
    run_with_sorter_with_deletion=True):

    modes_to_run = []
    if test_name == None:
        test_name = "test"
    if run_without_sorter:
        modes_to_run.append(WITHOUT_SORTER)
    if run_with_sorter_no_deletion:
        modes_to_run.append(WITH_SORTER_NO_DELETION)
    if run_with_sorter_with_deletion:
        modes_to_run.append(WITH_SORTER_WITH_DELETION)

    result = {}
    # TODO: it's better when each mode corresponds to different test
    for mode in modes_to_run:
        result[mode2str(mode)] = run_single_mode_processor_test(
            test_name, config, mode, input_file_name, input_file_format)
    return result

def run_single_mode_processor_test(
    test_name,
    config,
    mode,
    input_file_name,
    input_file_format,
    output_directory=None,
    config_filename=None
):
    mode_str = mode2str(mode)
    if not config_filename:
        config_filename = '{}.{}.config'.format(test_name, mode_str)
    if not output_directory:
        output_directory = '{}.{}.output'.format(test_name, mode_str)

    assert not os.path.exists(output_directory), "Output directory for test already exists: {}".format(
        os.path.realpath(output_directory))

    assert not os.path.exists(config_filename), "Config file for test already exists: {}".format(
        os.path.realpath(config_filename))

    os.mkdir(output_directory)
    with open(config_filename, 'w') as outf:
        print >>outf, config
        print >>outf, """
            Shard {{
              OutputDir: "{}"
            }}
        """.format(output_directory)
        if mode == WITHOUT_SORTER:
            pass
        elif mode == WITH_SORTER_NO_DELETION:
            print >>outf, """
            Sorter {
                RandomSorter {
                    Seed: 42
                    PercentRemoved: 0
                }
            }
            """
        elif mode == WITH_SORTER_WITH_DELETION:
            print >>outf, """
            Sorter {
                RandomSorter {
                    Seed: 54
                    PercentRemoved: 42
                }
            }
            """

    cmd = [
        KWDUMPWORK_BIN,
        '--input', '{}:{}'.format(input_file_name, input_file_format),
        '--index', config_filename
    ]

    kwdumpwork_out = yatest.common.output_path('{}.kwdumpwork.{}.out'.format(test_name, mode_str))
    kwdumpwork_err = yatest.common.output_path('{}.kwdumpwork.{}.err'.format(test_name, mode_str))
    with open(kwdumpwork_out, 'w') as outf, open(kwdumpwork_err, 'w') as errf:
        subprocess.check_call(cmd, stdout=outf, stderr=errf)

    result = []
    processor_generated_files = os.listdir(output_directory)
    result.append(processor_generated_files)
    processor_generated_files.sort()
    for filename in processor_generated_files:
        result.append(yatest.common.canonical_file(os.path.join(output_directory, filename)))
    return result

def test_arcdir():
    return run_processor_test(
        '''
        ArcOptions {
          TupleName: "arc"
          ArcFileName: "indexarc"
          DirFileName: "indexdir"
          AllowEmptyArchives: false
          IsFakeTupleName: "IsFake"
          LastAccessTupleName: "LastAccess"
          MTimeTupleName: "HttpModTime"
          MimeTypeTupleName: "MimeType"
          EncodingTupleName: "Encoding"
          LanguageTupleName: "Language"
          PatchTextArcHeaders: true
          BeautyUrlTupleName: "RobotBeautyUrl"
          MainContentUrlTupleName: "Url"
          SnippetsTupleName: "ExternalSnippets"
          DocSizeTupleName: "DocSize"
          LanguageRegionTupleName: "LanguageRegion"
          UrlMenuTupleName: "UrlMenu"
        }
        ''',
        yatest.common.data_path("oxygen/processors/arcdir/input.dump.snappy"),
        "dump"
    )

def test_arcdir_OXYGEN_2178():
    return run_processor_test(
        '''
        ArcOptions {
          TupleName: "arc"
          ArcFileName: "indexarc"
          DirFileName: "indexdir"
          SnippetsTupleName: "ExternalSnippets"
        }
        ''',
        yatest.common.data_path("oxygen/processors/arcdir/OXYGEN-2178.prototext"),
        "prototext",
        test_name="OXYGEN_2178"
    )
