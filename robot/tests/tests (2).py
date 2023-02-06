import pytest

from yatest import common

from rtmapreduce.tests.yatest import rtmr_test

tasks = [
    "watch_log_extractor",
    "watch_log_aggregator"
]

manifests = {
    "watch_log_extractor": {
        "input_tables": [
            "watch_log"
        ],
        "output_tables": [
            "watch_log_intermediate",
            "watch_log_intermediate.errors"
        ],
        "expect_empty_tables": [
            "watch_log_intermediate.errors"
        ]
    },
    "watch_log_aggregator": {
        "input_tables": [
            "watch_log_intermediate"
        ],
        "output_tables": [
            "watch_log"
        ]
    }
}


@pytest.mark.parametrize("task", tasks)
def test_watch_log(task, tmpdir):
    rtmr_test.init(tmpdir)
    manifest = manifests[task]
    manifest["config"] = common.source_path("robot/samovar/rtmr/watch_log/tests/" + task + ".cfg")
    manifest["dynlibs"] = [
        common.binary_path("robot/samovar/rtmr/watch_log/dynlib/libwatch_log-dynlib.so")
    ]
    return rtmr_test.run(task, manifest)
