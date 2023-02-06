import pytest

from rida.models import device as device_models


@pytest.mark.parametrize(
    ['version', 'is_expected_exception'],
    [
        pytest.param('2.6.0', False),
        pytest.param('2.11.999', False),
        pytest.param('2.6.w', True),
        pytest.param('2.6', True),
        pytest.param('2.6.0.1', True),
    ],
)
@pytest.mark.parametrize('ignore_errors', [True, False])
def test_parsing(
        version: str, ignore_errors: bool, is_expected_exception: bool,
):
    try:
        build_number = device_models.BuildNumberName.from_string(
            version, ignore_errors=ignore_errors,
        )
        if is_expected_exception is True:
            assert ignore_errors is True
            assert build_number.to_string() == '0.0.0'
        else:
            assert build_number.to_string() == version
    except ValueError:
        assert is_expected_exception is True
        assert ignore_errors is False


def test_order():
    raw_versions = ['2.6.0', '2.6.1', '2.6.999', '2.7.0', '3.0.0', '3.1.0']
    versions = [
        device_models.BuildNumberName.from_string(v) for v in raw_versions
    ]
    versions.sort()
    for raw_version, version in zip(raw_versions, versions):
        assert raw_version == version.to_string()
