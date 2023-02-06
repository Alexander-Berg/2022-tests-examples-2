import pytest


pytest.register_assert_rewrite(
    'tests_discounts.common', 'tests_discounts.test_admin.admin_test_utils',
)
