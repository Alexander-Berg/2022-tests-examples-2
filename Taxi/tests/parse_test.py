import yatest.common
import json

import taxi.tools.dorblu.dorblu_uploader.validation as validation


def test_parse_config():
    res = validation.do_file(
        'MyProject',
        yatest.common.source_path(
            'taxi/tools/dorblu/dorblu_configs_uploader/lib/tests/mobile_dev_oxcd8o.yaml'),
        {},
        None,
        True)

    with open("parsed_config", "w") as f:
        json.dump(res, f)

    return [yatest.common.canonical_file("parsed_config", local=True)]
