import copy
import typing

import pytest

from taxi_corp_integration_api.api.common import cost_center_utils
from taxi_corp_integration_api.generated.service.swagger import models


def _build_cost_center_fields(
        order_flows: typing.List[str], fields_count: int,
) -> typing.List[models.api.CostCenterFieldInResponse]:
    return [
        models.api.CostCenterFieldInResponse(
            id=f'id_{n}',
            title=f'Title {n}',
            required=bool(n % 2),
            format=['text', 'mixed', 'select'][n % 3],
            values=['1', '2', '3'],
            services=['taxi'],
            order_flows=order_flows.copy(),
        )
        for n in range(fields_count)
    ]


@pytest.mark.parametrize(
    ['initial_fields', 'client_categories', 'config_value', 'expected_fields'],
    [
        pytest.param(
            _build_cost_center_fields(['taxi'], fields_count=1),
            ['courier', 'econom'],
            {},
            _build_cost_center_fields(['taxi'], fields_count=1),
            id='empty config, nothing added',
        ),
        pytest.param(
            _build_cost_center_fields(['taxi'], fields_count=1),
            ['courier', 'econom'],
            {'delivery': ['courier', 'cargo', 'express']},
            _build_cost_center_fields(['taxi', 'delivery'], fields_count=1),
            id='category fits, new delivery added',
        ),
        pytest.param(
            _build_cost_center_fields(['taxi'], fields_count=2),
            ['courier', 'econom'],
            {'delivery': ['courier', 'cargo', 'express']},
            _build_cost_center_fields(['taxi', 'delivery'], fields_count=2),
            id='category fits, new delivery added, more fields',
        ),
        pytest.param(
            _build_cost_center_fields(['taxi', 'delivery'], fields_count=1),
            ['courier', 'econom'],
            {'delivery': ['courier', 'cargo', 'express']},
            _build_cost_center_fields(['taxi', 'delivery'], fields_count=1),
            id='category fits, old delivery present',
        ),
        pytest.param(
            _build_cost_center_fields(['taxi'], fields_count=1),
            ['econom'],
            {'delivery': ['courier', 'cargo', 'express']},
            _build_cost_center_fields(['taxi'], fields_count=1),
            id='other category, nothing added',
        ),
    ],
)
def test_skip_cost_centers_check(
        initial_fields: typing.List[models.api.CostCenterFieldInResponse],
        client_categories: typing.List[str],
        config_value: typing.Dict[str, typing.List[str]],
        expected_fields: typing.List[models.api.CostCenterFieldInResponse],
):
    fields_to_change = copy.deepcopy(initial_fields)
    cost_center_utils.add_order_flows_by_categories(
        fields_to_change, client_categories, config_value,
    )
    assert len(fields_to_change) == len(expected_fields)
    comparison_pairs = zip(fields_to_change, expected_fields)
    for field_n, (old_field, new_field) in enumerate(comparison_pairs):
        assert_msg = f'field {field_n} comparison failed'
        assert old_field.serialize() == new_field.serialize(), assert_msg
