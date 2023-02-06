import pytest

from eslogadminpy3.lib import api_utils


@pytest.mark.parametrize('raw', ['true', 'TRUE', '1', 't', 'T', 'True'])
def test_boolean_parser_success_true(raw):
    assert api_utils.parse_boolean(raw) is True


@pytest.mark.parametrize('raw', ['false', 'FALSE', '0', 'f', 'F', 'False'])
def test_boolean_parser_success_false(raw):
    assert api_utils.parse_boolean(raw) is False


@pytest.mark.parametrize('raw', ['yes', 'no', 'some thing'])
def test_boolean_parser_fail(raw):
    with pytest.raises(api_utils.UnParsableBoolean):
        api_utils.parse_boolean(raw)


def test_boolean_parser_with_none():
    with pytest.raises(api_utils.UnParsableBoolean):
        api_utils.parse_boolean(None)

    assert api_utils.parse_boolean(None, default=True) is True
    assert api_utils.parse_boolean(None, default=False) is False

    with pytest.raises(api_utils.UnParsableBoolean):
        api_utils.parse_boolean('some-bad-value', default=True)
