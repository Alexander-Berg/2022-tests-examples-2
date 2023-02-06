# coding: utf-8

import string
import hashlib

import six

from sandbox import sdk2
from sandbox import common


class TestYAV(sdk2.Task):
    """
    This task tests Sandbox integration with Yandex Vault.
    It fetches a secret and validates that it has expected keys and values.
    """

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 2048
        disk_space = 15

        class Caches(sdk2.Requirements.Caches):
            pass  # no shared caches

    class Parameters(sdk2.Parameters):
        description = "Test YAV"
        kill_timeout = 180

        with sdk2.parameters.Group("Yav parameter") as yav_group:
            secret = sdk2.parameters.YavSecret("YAV secret identifier (with optional version)", required=True)
            expected = sdk2.parameters.Dict(
                "Expected keys and their values (or SHA256 hashes)",
                description="The values will be hashed once saved"
            )

        with sdk2.parameters.Group("Vault parameter") as vault_group:
            vault_secret = sdk2.parameters.Vault("Vault parameter that reads secrets from Yav")
            vault_expected = sdk2.parameters.String(
                "Expected value (or SHA256 hash)",
                description="The value will be hashed once saved"
            )

    @staticmethod
    def hash(value):
        return hashlib.sha256(value).hexdigest()

    @staticmethod
    def is_hash(value):
        return len(value) == 64 and all(c in string.hexdigits for c in value)

    def on_execute(self):

        if not self.Parameters.expected:
            return

        secret = self.Parameters.secret.data()
        self.set_info("Secret has been successfully fetched via task parameter")
        self.check_yav_data(secret)

        secrets = sdk2.yav.Yav(data=self.Parameters.secret)
        self.set_info("Secret has been successfully fetched via `sdk2.yav.Yav`")
        self.check_yav_data(secrets.data)

        auto_decode_secret_data = self.Parameters.secret.data(auto_decode=True)
        self.set_info("Secret has been successfully fetched with auto_decode")
        self.check_yav_data(auto_decode_secret_data)

        if len(self.Parameters.vault_secret):
            secret = self.Parameters.vault_secret.data()
            self.set_info("Secret has been successfully fetched via `sdk2.Vault`")
            if self.hash(secret) != self.Parameters.vault_expected:
                raise common.errors.TaskFailure("Value for `{}` does not match".format(self.Parameters.vault_secret))

        self.set_info("Secret has all expected keys and values")

    def check_yav_data(self, data):
        for key, expected_value in six.iteritems(self.Parameters.expected):
            try:
                value = data[key]
            except KeyError:
                raise common.errors.TaskFailure("Key `{}` not found in the secret".format(key))

            if isinstance(value, unicode):
                value = value.encode('utf-8')

            if self.hash(value) != expected_value:
                raise common.errors.TaskFailure("Values for key `{}` do not match".format(key))

    def on_save(self):
        if not self.Parameters.expected:
            return

        expected = []

        for key, value in six.iteritems(self.Parameters.expected):
            if not self.is_hash(value):
                value = self.hash(value)
            expected.append((key, value))

        self.Parameters.expected = expected

        # noinspection PyTypeChecker
        if not self.is_hash(self.Parameters.vault_expected):
            self.Parameters.vault_expected = self.hash(self.Parameters.vault_expected)
