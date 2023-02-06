# -*- coding: utf-8 -*-
from collections import Counter
import json

import pytest
import yatest.common


@pytest.mark.parametrize(
    'env',
    [
        'production',
        'testing',
        'stress',
        'intranet.production',
        'intranet.testing',
    ],
)
def test_all_tvm_client_ids_are_unique(env):
    filename = 'passport/backend/api/deb/debian/tvm_keyring/passport_api.{}'.format(env)
    with open(yatest.common.source_path(filename)) as f:
        keyring = json.load(f)
    client_ids_freq = Counter([d['client_id'] for d in keyring['destinations']])
    above_one = [client_id for client_id, freq in client_ids_freq.most_common() if freq > 1]
    assert above_one == []


@pytest.mark.parametrize(
    'env',
    [
        'production',
        'testing',
        'stress',
        'intranet.production',
        'intranet.testing',
    ],
)
def test_all_tvm_aliases_are_unique(env):
    filename = 'passport/backend/api/deb/debian/tvm_keyring/passport_api.{}'.format(env)
    with open(yatest.common.source_path(filename)) as f:
        keyring = json.load(f)
    aliases_freq = Counter([d['alias'] for d in keyring['destinations']])
    above_one = [alias for alias, freq in aliases_freq.most_common() if freq > 1]
    assert above_one == []
