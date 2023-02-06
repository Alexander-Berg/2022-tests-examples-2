import pytest

pytest.register_assert_rewrite(
    'grocery_mocks.utils.handle_context',
    'grocery_mocks.utils.helpers',
    'grocery_mocks.utils.stq',
)
