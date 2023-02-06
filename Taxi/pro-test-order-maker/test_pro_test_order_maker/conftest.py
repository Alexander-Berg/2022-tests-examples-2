# pylint: disable=redefined-outer-name
import pro_test_order_maker.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'pro_test_order_maker.generated.service.pytest_plugins',
    'test_pro_test_order_maker.plugins',
]
