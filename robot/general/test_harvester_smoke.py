import os
import pytest

from fixtures.tmpdir_fixtures import tmpdir_module
from fixtures.lemur_fixtures import lyt, harvester_config

import lemur.info as lemurinfo
import ytio.writers as writers
import test.info as testinfo

import yatest.common

def test_harvester_smoke(lyt, tmpdir_module, harvester_config):
    testinfo.setup_environ(os.environ, "1480423734", True) # 29.11.2016
    writers._load_table_from_file_with_template_name(lyt, "incoming__final__some")
    lemurinfo.Harvester(lyt.instance_config, harvester_config, tmpdir_module, os.environ.copy()).run()
