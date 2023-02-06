import pytest

from yatest import common

from rtmapreduce.tests.yatest import rtmr_test

tasks = [
    "adnet_hits_extractor",
    "adnet_hits_aggregator"
]

manifests = {
    "adnet_hits_extractor": {
        "input_tables": [
            "adnet_hits"
        ],
        "output_tables": [
            "adnet_hits_intermediate",
            "adnet_hits.errors"
        ]
    },

    "adnet_hits_aggregator": {
        "input_tables": [
            "adnet_hits_intermediate"
        ],
        "output_tables": [
            "adnet_hits"
        ],
    }
}


@pytest.mark.parametrize("task", tasks)
def test_adnet_hits(task, tmpdir):
    rtmr_test.init(tmpdir)
    manifest = manifests[task]
    manifest["config"] = common.source_path("robot/samovar/rtmr/adnet_hits/tests/" + task + ".cfg")
    manifest["dynlibs"] = [
        common.binary_path("robot/samovar/rtmr/adnet_hits/dynlib/libadnet_hits-dynlib.so")
    ]

    return rtmr_test.run(task, manifest, diff_tool=None, split_files=True)
