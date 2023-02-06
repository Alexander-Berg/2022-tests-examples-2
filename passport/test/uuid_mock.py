# -*- coding: utf-8 -*-

import mock
from passport.backend.vault.api.utils import ulid


class UuidMock(object):
    def __init__(self, uuid_value=None, base_value=1000000):
        if uuid_value:
            self.mock_ulid = mock.patch(
                'passport.backend.vault.api.utils.ulid.create_ulid',
                mock.Mock(return_value=ulid.ULID(uuid_value)),
            )
        else:
            prepared_ulids = [
                ulid.ULID(bytes_=ulid.int_to_bytes(x, 16, 'big')) for x in range(base_value, base_value + 10000)
            ]
            self.mock_ulid = mock.patch(
                'passport.backend.vault.api.utils.ulid.create_ulid',
                mock.Mock(side_effect=prepared_ulids),
            )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self.mock_ulid.start()

    def stop(self):
        self.mock_ulid.stop()
