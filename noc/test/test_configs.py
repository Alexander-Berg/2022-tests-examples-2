import yatest

from noc.grad.grad.lib.config_functions import read_poller_config, conf_merge


def test_conf_merge():
    assert conf_merge({1: 1}, {2: 2}) == {1: 1, 2: 2}
    assert conf_merge({1: {2: 2}}, {1: {3: 3}}) == {1: {2: 2, 3: 3}}
    assert conf_merge({1: [4, 5]}, {1: [2, 3]}) == {1: [2, 3, 4, 5]}


def test_config():
    return  # FIXME: fix templated config check
    read_poller_config(
        yatest.common.source_path("admins/salt-media/noc/roots/units/nocdev-grads/files/etc/grad/grad_server.yml"),
        yatest.common.source_path("admins/salt-media/noc/roots/units/nocdev-grads/files/etc/grad/conf.d"),
    )
