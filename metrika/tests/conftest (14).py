import pytest

import yatest.common

from metrika.pylib.structures.dotdict import DotDict

import metrika.admin.python.mtapi.lib.app as lib_app


@pytest.fixture()
def args():
    return DotDict.from_dict(
        {
            "app": "zookeeper",
            "bishop_env": None,
            "config": yatest.common.source_path('metrika/admin/python/mtapi/lib/api/zookeeper/tests/config.yaml')
        }
    )


@pytest.fixture()
def client(args):
    app, config = lib_app.create_app(args)

    with app.test_client() as client:
        yield client
