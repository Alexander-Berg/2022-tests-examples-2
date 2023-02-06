import pytest
import six
import re

from sandbox import sdk2
from sandbox.projects.common import parameters as common_parameters


@pytest.mark.parametrize("value", [
    "$(vault:value:theowner:thesecret)",
    "$(vault:file:theowner:thesecret)",
])
def test__vault_pattern__should_match(value):
    assert re.match(common_parameters.EnvironmentVariablesContainer.VAULT_PATTERN, value) is not None, (
        "String '{}' cannot be recognized as a Vault replacement template".format(value)
    )


@pytest.mark.parametrize("value", [
    "random string",
    "$(vault:value:theowner)",           # no name (value dest)
    "$(vault:hell:theowner:thesecret)",  # wrong destination
    "$(vault:file:theowner)",            # no name (file dest)
    "$(vault:::)",                       # empty (no dest no nothing)
    "$(vault:value::)",                  # empty values (value dest)
    "$(vault:file::)",                   # empty values (file dest)
])
def test__vault_pattern__should_not_match(value):
    assert re.match(common_parameters.EnvironmentVariablesContainer.VAULT_PATTERN, value) is None, (
        "String '{}' should NOT be parsed as a Vault replacement template".format(value)
    )


@pytest.mark.parametrize("value", [
    "$(yav:sec-ak4s7d8jy8fh8k00sdjfh#token)",
])
def test__yav_pattern__should_match(value):
    assert re.match(common_parameters.EnvironmentVariablesContainer.YAV_PATTERN, value) is not None, (
        "String '{}' cannot be recognized as a YaV replacement template".format(value)
    )


@pytest.mark.parametrize("value", [
    "random string",
    "$(yav:abcdefgkfgh#token)",            # secret id does not start with 'sec-'
    "$(sec-ldsfjskdf#something)",          # no 'yav:' prefix
    "$(yav:sec-ak4s7d8jy8fh8k00sdjfh)",    # no key provided
])
def test__yav_pattern__should_not_match(value):
    assert re.match(common_parameters.EnvironmentVariablesContainer.YAV_PATTERN, value) is None, (
        "String '{}' should NOT be parsed as a YaV replacement template".format(value)
    )


@pytest.mark.parametrize("value", [
    "A=1",
    "A='1'",
    "A='1' B='2'",
    "YT_TOKEN='$(vault:value:yazevnul:yazevnul-yt_token)'",
    "TOKEN='$(yav:sec-09dkjadgcn7583sdkfjh#token)'",
])
def test__env_var_pattern__should_match(value):
    assert common_parameters.EnvironmentVariablesContainer.is_value_valid(value)


@pytest.mark.parametrize("value", [
    "ABC",
    "-TOKEN=1 --OTHER=something"
])
def test__env_var_pattern__should_not_match(value):
    assert not common_parameters.EnvironmentVariablesContainer.is_value_valid(value)


def test__simple_variables():

    env_str = "A=1 B=2.1 C=potato D='cucumber'"

    env_dict = common_parameters.EnvironmentVariables.cast(env_str).as_dict_deref()

    assert isinstance(env_dict, dict)

    for value in six.itervalues(env_dict):
        assert isinstance(value, six.string_types)

    assert "A" in env_dict
    assert env_dict["A"] == "1"

    assert "B" in env_dict
    assert env_dict["B"] == "2.1"

    assert "C" in env_dict
    assert env_dict["C"] == "potato"

    assert "D" in env_dict
    assert env_dict["D"] == "cucumber"


def test__deref__vault(monkeypatch):

    vault_data = {
        "secret": "My friends they all told me: 'Man there's something '"
    }

    def vault_data_mocked(vault_cls, owner_or_name, name=None):
        owner, name = (None, owner_or_name) if name is None else (owner_or_name, name)
        return vault_data[name]

    monkeypatch.setattr(sdk2.Vault, "data", classmethod(vault_data_mocked))

    try:
        result = common_parameters.EnvironmentVariables.cast("SECRET='$(vault:value:someone:secret)'").as_dict_deref()
    except KeyError:
        assert False, "Sandbox Vault dereference is broken"

    assert result
    assert isinstance(result, dict)
    assert "SECRET" in result
    assert result["SECRET"] == vault_data["secret"]


def test__deref__yav(monkeypatch):

    yav_data = {
        "sec-ret": {
            "token": "AAA",
        },
    }

    def yav_data_mocked(instance):
        return yav_data[instance.secret.secret_uuid]

    monkeypatch.setattr(sdk2.yav.Secret, "data", yav_data_mocked)

    try:
        result = common_parameters.EnvironmentVariables.cast("TOKEN='$(yav:sec-ret#token)'").as_dict_deref()
    except KeyError:
        assert False, "YaV dereference is broken"

    assert result
    assert isinstance(result, dict)
    assert "TOKEN" in result
    assert result["TOKEN"] == yav_data["sec-ret"]["token"]
