# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from passport.backend.social.common.grants import GrantsConfig


class FakeGrantsConfig(object):
    def __init__(self):
        self._read_config_file = Mock(
            name='read_config_file',
            return_value=dict(),
        )

        self.__patches = [
            patch.object(
                GrantsConfig,
                '_make_grants_paths',
                return_value=[__file__],
            ),
            patch.object(
                GrantsConfig,
                '_saved_mtimes_match',
                return_value=False,
            ),
            patch.object(
                GrantsConfig,
                'is_expired',
                return_value=True,
            ),
            patch.object(
                GrantsConfig,
                'read_config_file',
                self._read_config_file,
            ),
        ]

    def _get_config(self):
        return self._read_config_file.return_value

    def start(self):
        for _patch in self.__patches:
            _patch.start()
        return self

    def stop(self):
        for _patch in reversed(self.__patches):
            _patch.stop()

    def add_consumer(self, consumer, networks=None, grants=None, tvm_client_id=None):
        config = self._get_config()
        config[consumer] = {'networks': [], 'grants': []}

        if tvm_client_id is not None:
            config[consumer]['client'] = {'client_id': tvm_client_id}

        self.add_networks(networks, consumer)
        self.add_grants(grants, consumer)

    def add_networks(self, networks, consumer):
        networks = networks or []
        config = self._get_config()
        config[consumer]['networks'] = networks

    def add_grants(self, grants, consumer):
        grants = grants or []
        config = self._get_config()
        config[consumer]['grants'] = grants
