#!/usr/bin/env python

import os
import shutil
import yatest.common

from os.path import join as pj

'''
    Test to ensure fqdn_to_ip consistency.
    If the changes are valid - canonize them and make sure external clients (like abc:domenator) got this changes.
    See https://st.yandex-team.ru/ZORA-1696
'''


def test_gozora_ip_conf():
    work_path = yatest.common.work_path()
    fqdn_to_ip_config = yatest.common.source_path('robot/zora/gozora/conf/production/fqdn_to_ip.conf')

    out_path = pj(work_path, 'conf')
    os.mkdir(out_path)
    shutil.copy(fqdn_to_ip_config, out_path)

    return yatest.common.canonical_dir(out_path)
