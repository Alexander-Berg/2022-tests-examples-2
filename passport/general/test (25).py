#!/usr/bin/env python
from __future__ import print_function

import passport.infra.libs.python.gammer as gammer
import yatest.common as yc


def _prepare_config():
    test_data = yc.source_path('passport/infra/libs/python/gammer/ut/data')
    with open(test_data + '/config_template.xml') as f:
        templ = f.read()

    with open("tvmapi.port") as f:
        tvmapi_port = int(f.read())
    tvm_secret_path = './tvm.secret'
    with open(tvm_secret_path, 'wt') as out:
        out.write('bAicxJVa5uVY7MjDlapthw')

    replaces = {
        'TVM_PORT': tvmapi_port,
        'TVM_SECRET_PATH': tvm_secret_path,
        'TEST_DATA_PATH': test_data,
    }

    for k, v in replaces.items():
        templ = templ.replace('{{%s}}' % k, str(v))

    tmp_config_file = './testing_out_stuff/config.xml'
    with open(tmp_config_file, 'wt') as out:
        out.write(templ)

    return tmp_config_file


def test_common():
    g = gammer.Gammer(_prepare_config())

    encrypted = g.encrypt_aes(
        input=b'kek',
        random=b'foo',
        aadata=b'bar',
    )

    decrypted = g.decrypt_aes(
        iv=encrypted['iv'],
        text=encrypted['text'],
        tag=encrypted['tag'],
        gamma_id=encrypted['gamma_id'],
        random=b'foo',
        aadata=b'bar',
    )

    assert decrypted == b'kek'
