import os

import pytest
import yatest

from sandbox.projects.ads.emily import resources
from sandbox.projects.ads.emily.storage.client.binary import BINARY_CLIENT_DIR, BINARY_CLIENT_NAME, MlStorageBinaryClient, configure_logger

from logos.libs.clients.sandbox.local_sandbox import LocalSandboxClient

configure_logger(debug=True)


def test_binary_client_token_set_correctly():
    cli_path = yatest.common.binary_path(os.path.join(BINARY_CLIENT_DIR, BINARY_CLIENT_NAME))
    MlStorageBinaryClient(token="some_token", cli_path=cli_path, mode=resources.EMlStorageClientMode.TEST.value)


@pytest.mark.parametrize("kwargs, msg",
                         [({"sb_client": LocalSandboxClient(), "cli_path": "bin/{}".format(BINARY_CLIENT_NAME),
                            "mode": resources.EMlStorageClientMode.TEST.value},
                           "Sandbox client and local client path both provided, but no error")])
def test_binary_client_attributes_raises(kwargs, msg):
    try:
        MlStorageBinaryClient(token="some_token", **kwargs)
    except AttributeError:
        return
    raise ValueError(msg)
