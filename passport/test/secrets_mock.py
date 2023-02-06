# -*- coding: utf-8 -*-

import mock
from passport.backend.vault.api.utils import secrets


class SecretsMock(object):
    range = 1000000

    def __init__(self, token_urlsafe_value='secret-token'):
        self.mock = mock.patch.object(
            secrets,
            'token_urlsafe',
            return_value=token_urlsafe_value,
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self.mock.start()

    def stop(self):
        self.mock.stop()
