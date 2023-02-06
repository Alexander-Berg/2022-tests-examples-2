import pathlib

import pytest

_BASE_PATH = pathlib.Path(__file__).parent.parent.parent.absolute()
_TAXI_REPLICATION_RULES_PATH = pathlib.Path(
    _BASE_PATH, 'taxi_replication_rules',
)
_EDA_REPLICATION_RULES_PATH = pathlib.Path(_BASE_PATH, 'eda_replication_rules')


@pytest.mark.parametrize(
    'dir_to_check',
    (_TAXI_REPLICATION_RULES_PATH, _EDA_REPLICATION_RULES_PATH),
)
def test_empty_dirs(dir_to_check):
    assert not dir_to_check.exists() or not list(dir_to_check.iterdir()), (
        f'The entire contents of {dir_to_check.name} were moved '
        f'to replication_rules. Please, update your develop '
        f'and use new version of rules generator tool '
        f'(see more: https://github.yandex-team.ru/taxi-dwh/dwh/'
        f'tree/develop/replication_rules#генерация-правил).'
    )
