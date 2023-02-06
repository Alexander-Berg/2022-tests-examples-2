import pytest
from marshmallow.exceptions import ValidationError


class TestTenantSettingsValidator:
    def test_correct_config(self, core):
        validated_settings = core.validate_tenant_faas_settings(
            {
                "tenants": [
                    {
                        "name": "test_tenant",
                        "instances": [{"name": "test_instance", "active": True, "dcs": []}],
                    }
                ]
            }
        )
        assert validated_settings == {
            "test_tenant": {
                "instances": {
                    "test_instance": {"active": True, "dcs": []},
                }
            },
        }

    def test_empty_config(self, core):
        validated_settings = core.validate_tenant_faas_settings({"tenants": []})
        assert validated_settings == {}

    def test_default_config(self, core):
        validated_settings = core.validate_tenant_faas_settings({"tenants": [{"name": "test", "instances": []}]})

        assert validated_settings == {"test": {"instances": {}}}

    def test_set_default(self, core):
        validated_settings = core.validate_tenant_faas_settings(
            {"tenants": [{"name": "test", "instances": [{"name": "test_instance"}]}]}
        )

        assert validated_settings == {"test": {"instances": {"test_instance": {"active": True, "dcs": []}}}}

    def test_incorrect_config(self, core):
        with pytest.raises(ValidationError):
            core.validate_tenant_faas_settings(
                {
                    "tenants": [
                        {
                            # name is not set
                            "instances": []
                        }
                    ]
                }
            )

        with pytest.raises(ValidationError):
            core.validate_tenant_faas_settings(
                {
                    "tenants": [
                        {
                            "name": "test_tenant",
                            "instances": [
                                {
                                    # name is not set
                                    "dcs": [],
                                }
                            ],
                        }
                    ]
                }
            )


class TestParseInstances:
    def test_default(self, core):
        parsed_instance = core.parse_instances(
            {
                "test": {
                    "faas": {
                        "function": "billing.test.function",
                        "peerdir": '"billing/test/"',
                        "revision": 123,
                    }
                }
            },
            "test_namespace",
            "test_namespace",
        )

        assert parsed_instance == {
            "default": [
                {
                    "function": "billing.test.function",
                    "revision": 123,
                    "instance": "default",
                    "peerdir": '"billing/test/"',
                    "pr_id": 0,
                    "settings": {},
                    "namespace": "test_namespace",
                    "tenant": "test_namespace",
                    "endpoint": "test",
                }
            ]
        }

    def test_namespace_differ_from_tenant(self, core):
        """
        If endpoint is placed outside its default tenant (== namespace_name), then we add prefix.
        :param core:
        :return:
        """
        parsed_instance = core.parse_instances(
            {
                "test": {
                    "faas": {
                        "function": "billing.test.function",
                        "peerdir": '"billing/test/"',
                        "revision": 123,
                    }
                }
            },
            "namespace",
            "tenant",
        )

        assert parsed_instance == {
            "default": [
                {
                    "function": "billing.test.function",
                    "revision": 123,
                    "instance": "default",
                    "peerdir": '"billing/test/"',
                    "pr_id": 0,
                    "settings": {},
                    "namespace": "namespace",
                    "tenant": "tenant",
                    "endpoint": "namespace-test",
                }
            ]
        }

    def test_instance_with_name(self, core):
        parsed_instance = core.parse_instances(
            {
                "test": {
                    "faas": {
                        "function": "billing.test.function",
                        "peerdir": '"billing/test/"',
                        "revision": 123,
                        "instance": "billing",
                    }
                }
            },
            "namespace",
            "tenant",
        )

        assert parsed_instance == {
            "billing": [
                {
                    "function": "billing.test.function",
                    "revision": 123,
                    "instance": "billing",
                    "peerdir": '"billing/test/"',
                    "pr_id": 0,
                    "settings": {},
                    "namespace": "namespace",
                    "tenant": "tenant",
                    "endpoint": "namespace-test",
                }
            ]
        }

    def test_instances_with_default(self, core):
        parsed_instance = core.parse_instances(
            {
                "test": {
                    "faas": {
                        "function": "billing.test.function",
                        "peerdir": '"billing/test/"',
                        "revision": 123,
                        "instance": "billing",
                    }
                },
                "bar": {
                    "faas": {
                        "function": "billing.bar.function",
                        "peerdir": '"billing/bar/"',
                        "revision": 321,
                        "settings": {"foo": "bae"},
                    }
                },
            },
            "namespace",
            "tenant",
        )

        assert parsed_instance == {
            "billing": [
                {
                    "function": "billing.test.function",
                    "revision": 123,
                    "instance": "billing",
                    "peerdir": '"billing/test/"',
                    "pr_id": 0,
                    "settings": {},
                    "namespace": "namespace",
                    "tenant": "tenant",
                    "endpoint": "namespace-test",
                }
            ],
            "default": [
                {
                    "function": "billing.bar.function",
                    "peerdir": '"billing/bar/"',
                    "revision": 321,
                    "instance": "default",
                    "pr_id": 0,
                    "settings": {"foo": "bae"},
                    "namespace": "namespace",
                    "tenant": "tenant",
                    "endpoint": "namespace-bar",
                }
            ],
        }


class TestValidateInstances:
    def test_valid_endpoints(self, core):
        core.validate_endpoints_in_instance(
            "test_instance",
            [
                {
                    "function": "billing.bar.function",
                    "peerdir": '"billing/bar/"',
                    "revision": 321,
                    "instance": "test_instance",
                    "pr_id": 0,
                    "settings": {"foo": "bae"},
                    "namespace": "namespace",
                    "tenant": "tenant",
                    "endpoint": "foo",
                },
                {
                    "function": "billing.bar.function",
                    "peerdir": '"billing/bar/"',
                    "revision": 321,
                    "instance": "test_instance",
                    "pr_id": 0,
                    "settings": {"foo": "bae"},
                    "namespace": "namespace",
                    "tenant": "tenant",
                    "endpoint": "bar",
                },
            ],
        )

    def test_endpoints_with_different_revisions(self, core):
        with pytest.raises(Exception):
            core.validate_endpoints_in_instance(
                "test_instance",
                [
                    {
                        "function": "billing.bar.function",
                        "peerdir": '"billing/bar/"',
                        "revision": 321,
                        "instance": "test_instance",
                        "pr_id": 0,
                        "settings": {"foo": "bae"},
                        "namespace": "tenant",
                        "tenant": "tenant",
                        "endpoint": "foo",
                    },
                    {
                        "function": "billing.bar.function",
                        "peerdir": '"billing/bar/"',
                        "revision": 123,
                        "instance": "test_instance",
                        "pr_id": 0,
                        "settings": {"foo": "bae"},
                        "namespace": "tenant",
                        "tenant": "tenant",
                        "endpoint": "bar",
                    },
                ],
            )

    def test_valid_minimal_revision(self, core):
        core.validate_revision = True
        core.minimal_revision = 2
        core.validate_endpoints_in_instance(
            "test_instance",
            [
                {
                    "function": "billing.bar.function",
                    "peerdir": '"billing/bar/"',
                    "revision": 3,
                    "instance": "test_instance",
                    "pr_id": 0,
                    "settings": {"foo": "bae"},
                    "namespace": "tenant",
                    "tenant": "tenant",
                    "endpoint": "foo",
                },
            ],
        )

    def test_invalid_minimal_revision(self, core):
        core.validate_revision = True
        core.minimal_revision = 2
        with pytest.raises(Exception):
            core.validate_endpoints_in_instance(
                "test_instance",
                [
                    {
                        "function": "billing.bar.function",
                        "peerdir": '"billing/bar/"',
                        "revision": 1,
                        "instance": "test_instance",
                        "pr_id": 0,
                        "settings": {"foo": "bae"},
                        "namespace": "tenant",
                        "tenant": "tenant",
                        "endpoint": "foo",
                    },
                ],
            )


class TestParseNamespaceConfiguration:
    def test_correct(self, core):

        data = {"namespace": "test", "faas": {"tenants": ["billing", "common"]}}

        res = core.validate_namespace_faas_configuration(data)

        assert res == {"tenants": ["billing", "common"]}

    def test_tenants_are_not_set(self, core):
        data = {"namespace": "test"}

        res = core.validate_namespace_faas_configuration(data)

        assert res == {"tenants": ["test"]}

    def test_tenants_empty(self, core):
        data = {"namespace": "test", "faas": {"tenants": []}}

        res = core.validate_namespace_faas_configuration(data)

        assert res == {"tenants": ["test"]}
