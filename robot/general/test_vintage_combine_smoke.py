import logging
import os
import pytest

from fixtures.tmpdir_fixtures import tmpdir_module
from fixtures.lemur_fixtures import lyt, vintage_config

import lemur.info as lemurinfo
import ytio.writers as writers
import test.info as testinfo

def test_vintage_combine_smoke(lyt, vintage_config, tmpdir_module):
    testinfo.setup_environ(os.environ, "1480423734", True) # 29.11.2016
    writers.load_tables_from_directory(lyt, "vintage_combine_input", True)
    for shard in range(lyt.instance_config.proto.LocatorConfig.ShardCount):
        lemurinfo.Vintage(lyt.instance_config, vintage_config, tmpdir_module, os.environ.copy()).run(shard, "combine")


