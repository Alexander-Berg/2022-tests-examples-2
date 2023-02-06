from . import build_test
from pytest import Function
from typing import List


# Хук для pytest для изменения порядка выполнения тестов
# Так как сборка документации занимает много времени, её установим первой в очередь
# https://docs.pytest.org/en/latest/reference/reference.html?#pytest.hookspec.pytest_collection_modifyitems
def pytest_collection_modifyitems(session, config, items: List[Function]):
    for i, func in enumerate(items):
        if func.module is build_test:
            name = func.originalname or func.name
            if name == build_test.test_documentation_building.__name__:
                items[0], items[i] = items[i], items[0]
                break
