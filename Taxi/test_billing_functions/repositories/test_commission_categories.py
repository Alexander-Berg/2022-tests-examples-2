import dataclasses
from typing import Collection
from typing import Optional

import pytest

from billing_functions.repositories import commission_categories


Category = commission_categories.CategoryDescription
AccountTemplate = commission_categories.AccountTemplate


@dataclasses.dataclass(frozen=True)
class Description:
    categories: Collection[dict]
    query: dict
    expected_category: Optional[Category] = None
    expected_exception: Optional[Exception] = None


@pytest.mark.parametrize(
    'test_data_json',
    ('test_fetch_by_kind.json', 'test_raises_if_unknown_kind.json'),
)
@pytest.mark.json_obj_hook(
    CategoryDescription=Category, AccountTemplate=AccountTemplate,
)
async def test_fetch_category(
        test_data_json,
        *,
        load_py_json,
        mock_billing_commissions,
        stq3_context,
):
    test_data = Description(**load_py_json(test_data_json))
    mock_billing_commissions(categories=test_data.categories)
    repo = stq3_context.commission_categories

    if test_data.expected_category:
        result = await repo.fetch(**test_data.query)
        assert result == test_data.expected_category
    else:
        assert test_data.expected_exception
        with pytest.raises(test_data.expected_exception):
            await repo.fetch(**test_data.query)
