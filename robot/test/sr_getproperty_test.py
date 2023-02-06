#!/usr/bin/env python

import yatest


def test_entry():

    bin_path = yatest.common.binary_path("robot/jupiter/tools/selectionrank/selectionrank")
    config_path = yatest.common.source_path("robot/jupiter/tools/selectionrank/UploadRules.pb.txt")

    yatest.common.execute([bin_path,
                           "GetProperty",
                           "--server-name",
                           "banach.yt.yandex.net",
                           "--mr-prefix",
                           "//home/jupiter",
                           "--current-state",
                           "20170825-213641",
                           "--prev-state",
                           "20170824-015055",
                           "--selectionrank-upload-rules-cfg",
                           config_path,
                           "--property",
                           "SRP_FML_FORMULA_ID"],
                          cwd=yatest.common.output_path())

if __name__ == '__main__':
    test_entry()
