import pytest

pytest.register_assert_rewrite(
    'tests_eats_business_rules.admin.commission_helper',
    'tests_eats_business_rules.admin.fine_helper',
)
