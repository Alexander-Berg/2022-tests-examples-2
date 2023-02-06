# coding: utf-8
from __future__ import absolute_import, unicode_literals

import os
import shutil

import py
import pytest

from sandbox.common import config


@pytest.fixture()
def config_dir(tmpdir):
    return py.path.local(str(tmpdir))


if config._inside_the_binary():
    @pytest.fixture()
    def base_config():
        pass

    @pytest.fixture()
    def custom_config(config_dir):
        from library.python import resource
        custom_data = resource.find("sandbox/etc/settings.yaml")

        with config_dir.join("settings.yaml").open("wb") as f:
            f.write(custom_data)

        os.environ[config.Registry.CONFIG_ENV_VAR] = str(config_dir.join("settings.yaml"))
        yield
        del os.environ[config.Registry.CONFIG_ENV_VAR]

else:
    @pytest.fixture()
    def base_config(config_dir, monkeypatch):
        base_config = os.path.join(os.path.dirname(__file__), "etc/.settings.yaml")
        config_path = config_dir.join(".settings.yaml")
        shutil.copy2(base_config, str(config_path))
        monkeypatch.setattr(config.Registry, "_config_dir", config_dir)
        yield
        config_path.remove()

    @pytest.fixture()
    def custom_config(base_config, config_dir, monkeypatch):
        custom_config = os.path.join(os.path.dirname(__file__), "etc/settings.yaml")
        config_path = config_dir.join("settings.yaml")
        monkeypatch.setattr(config.Registry, "custom", config_path)
        shutil.copy2(custom_config, str(config_path))
        yield
        config_path.remove()


@pytest.mark.skipif(not config._inside_the_binary(), reason="non-binary tests go crazy when mocking config files")
class TestConfig(object):

    def test__singleton(self, base_config):
        assert config.Registry() is config.Registry()

    def test__base(self, base_config):
        c = config.Registry()
        c.reload()
        assert c.foo.nested.key == "base"
        assert set(c.this) >= {"id", "fqdn", "system", "cpu"}

    def test__base_copy(self, base_config):
        c = config.Registry()
        c.reload()

        foo = c.foo
        foo_copy = foo.copy()

        assert foo == foo_copy
        assert id(foo) != foo_copy
        assert foo_copy.not_identifier == "ok"

    def test__custom(self, custom_config):
        c = config.Registry()
        c.reload()
        assert c.foo.nested.key == "custom"
        assert c.another is None

    def test__evaluated(self, base_config):
        c = config.Registry()
        c.reload()
        assert c.evaluated == "SANDBOX_CONFIG"

    def test__evaluated_custom(self, custom_config):
        c = config.Registry()
        c.reload()
        assert c.evaluated == "SANDBOX_CUSTOM_CONFIG"

    def test__query(self):
        base = {"foo": {"bar": "123"}, "baz": True}
        data = {"foo": {"bar": "SANDBOX"}}
        overrides = {"foo.bar": "CUSTOM"}

        expected = {"foo": {"bar": "CUSTOM"}, "baz": True}

        result = config.Registry.query(data, base=base, overrides=overrides)
        assert isinstance(result, config.Registry.Config)
        assert result == expected

        result = config.Registry.query(data, base=base, overrides=overrides, as_dict=True)
        assert type(result) is dict
        assert result == expected

    def test__query_fix_keys(self):
        base = {"config": {"foo-bar": 42, "1key": 43}}
        result = config.Registry.query({}, base=base)

        assert result.config.foo_bar == 42
        assert result.config._key == 43

        with pytest.raises(TypeError):
            config.Registry.query({}, base=base, fix_keys=False)

    def test__query_evaluated_complex(self):
        data = {"integer": 42, "string": "foo"}
        result = config.Registry.query(data, overrides={"eval": ("${integer}", "${string}")})
        assert result["eval"] == ["42", "foo"]

    def test__query_non_evaluated(self):
        data = {"integer": 42, "another_integer": "${integer}"}
        assert config.Registry.query(data, evaluate=False) == {"integer": 42, "another_integer": "${integer}"}

    def test__query_nested_override(self):
        base = {"a": 1}
        overrides = {"a.b.c": 1}
        assert config.Registry.query({}, base=base, overrides=overrides) == {"a": {"b": {"c": 1}}}

    if config._inside_the_binary():

        def test__ensure_custom(self, custom_config):
            config.ensure_local_settings_defined()

        def test__ensure_custom_failure(self):
            with pytest.raises(RuntimeError):
                config.ensure_local_settings_defined()
