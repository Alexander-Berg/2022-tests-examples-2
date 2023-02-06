# pylint: disable=unused-variable
import pytest

from taxi_config_schemas import repo_manager


@pytest.mark.parametrize(
    'lines,valid_lines',
    [
        (
            [
                'schemas/configs/declarations/group/NEW_SETTINGS.yaml',
                'schemas/configs/declarations/group/NEW_SETTINGS_V2.yaml',
                'schemas/configs/declarations/group/ROUTER42_PARAMS.yaml',
                'schemas/configs/declarations/group/123NUMBER_BEFORE.yaml',
                'schemas/configs/declarations/group/small_leters.yaml',
                'schemas/configs/declarations/group/white space.yaml',
                'schemas/configs/declaration/group/BAD_PATH.yaml',
            ],
            [
                'schemas/configs/declarations/group/NEW_SETTINGS.yaml',
                'schemas/configs/declarations/group/NEW_SETTINGS_V2.yaml',
                'schemas/configs/declarations/group/ROUTER42_PARAMS.yaml',
            ],
        ),
    ],
)
def test_config_name_valid(lines, valid_lines):
    # pylint: disable=protected-access
    result = repo_manager.common.get_lines_with_configs(lines)
    assert result == valid_lines
