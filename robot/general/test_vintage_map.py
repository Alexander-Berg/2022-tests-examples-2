import os
import pytest
import logging

from yatest.common import test_output_path
from fixtures.lemur_fixtures import lyt, vintage_config
from fixtures.tmpdir_fixtures import tmpdir_module

import test.info as testinfo
import test.utils as testutils
import lemur.info as lemurinfo
import ytio.writers as writers

def test_vintage_map(lyt, vintage_config, tmpdir_module):
    testinfo.setup_environ(os.environ, "1470425319", True)
    writers.load_tables_from_directory(lyt, "vintage_map_input", True)

    for i in range(lyt.instance_config.proto.LocatorConfig.ShardCount):
        lemurinfo.Vintage(lyt.instance_config, vintage_config, tmpdir_module, os.environ.copy()).run(i, "map")

    lemurinfo.CountersTool(lyt.instance_config, tmpdir_module, os.environ.copy()).run("merge")

    test_out = test_output_path("test_out")
    if not os.path.exists(test_out):
        os.makedirs(test_out)

    for i in range(lyt.instance_config.proto.LocatorConfig.ShardCount):
        with open("{}/vintage_map.counters.shard-{}.json".format(test_out, i), "w") as stdout:
            lemurinfo.CountersTool(lyt.instance_config
                                  ,tmpdir_module
                                  ,os.environ.copy()).run("read"
                                                         ,"vintage_map"
                                                         ,i
                                                         ,stdout=stdout)


    testutils.save_cypress(lyt, lyt.instance_config.get_base_prefix(), test_out)
