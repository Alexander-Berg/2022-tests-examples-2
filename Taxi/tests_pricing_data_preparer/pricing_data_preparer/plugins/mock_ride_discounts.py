# pylint: disable=redefined-outer-name, import-error
from typing import List
from typing import Optional
from typing import Tuple

from pricing_extended import mocking_base
import pytest


def _make_discount_value(value: dict) -> dict:
    return {
        'discount_id': '100',
        'discount_class': 'default',
        'name': '1',
        'discount_value': value,
        'is_price_strikethrough': True,
    }


def _get_hyperbolas(
        threshold: Optional[float],
        lower_hyperbola_pac: Optional[Tuple[float, float, float]],
        upper_hyperbola_pac: Optional[Tuple[float, float, float]],
) -> dict:
    return {
        'value': {
            'hyperbola_lower': {
                'p': lower_hyperbola_pac[0] if lower_hyperbola_pac else 0.0,
                'a': lower_hyperbola_pac[1] if lower_hyperbola_pac else 0.0,
                'c': lower_hyperbola_pac[2] if lower_hyperbola_pac else 0.0,
            },
            'hyperbola_upper': {
                'p': upper_hyperbola_pac[0] if upper_hyperbola_pac else 0.0,
                'a': upper_hyperbola_pac[1] if upper_hyperbola_pac else 0.0,
                'c': upper_hyperbola_pac[2] if upper_hyperbola_pac else 0.0,
            },
            'threshold': threshold if threshold is not None else 0.0,
        },
        'value_type': 'hyperbolas',
    }


def _get_table(table: Optional[List[Tuple[float, float]]]) -> dict:
    return {
        'value_type': 'table',
        'value': (
            [{'from_cost': item[0], 'discount': item[1]} for item in table]
            if table is not None
            else [{'from_cost': 0.0, 'discount': 0.0}]
        ),
    }


def _get_flat(value: Optional[float]) -> dict:
    return {'value_type': 'flat', 'value': value if value is not None else 10}


def _add_discount(
        response: dict, category_name: str, value: dict, is_cashback: bool,
):
    results = response['discounts']
    discount_value = _make_discount_value(value)
    key = 'cashback_discounts' if is_cashback else 'money_discounts'

    for item in response['discounts']:
        if item['tariff'] == category_name:
            item[key] = [discount_value]
            return
    item = {
        'tariff': category_name,
        'cashback_discounts': [],
        'money_discounts': [],
    }
    item[key].append(discount_value)
    results.append(item)


class V3RideDiscountsContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = {'discount_offer_id': '0' * 24, 'discounts': []}

    def add_hyperbolas_discount(
            self,
            category_name: str,
            threshold: Optional[float] = None,
            lower_hyperbola_pac: Optional[Tuple[float, float, float]] = None,
            upper_hyperbola_pac: Optional[Tuple[float, float, float]] = None,
            is_cashback: bool = False,
    ):
        hyperbolas = _get_hyperbolas(
            threshold, lower_hyperbola_pac, upper_hyperbola_pac,
        )
        _add_discount(self.response, category_name, hyperbolas, is_cashback)

    def add_table_discount(
            self,
            category_name: str,
            table: Optional[List[Tuple[float, float]]] = None,
            is_cashback: bool = False,
    ):
        discount = _get_table(table)
        _add_discount(self.response, category_name, discount, is_cashback)

    def add_flat_discount(
            self,
            category_name: str,
            value: Optional[float] = None,
            is_cashback: bool = False,
    ):
        discount = _get_flat(value)
        _add_discount(self.response, category_name, discount, is_cashback)


@pytest.fixture
def ride_discounts():
    return V3RideDiscountsContext()


@pytest.fixture
def mock_ride_discounts(mockserver, ride_discounts):
    @mockserver.json_handler('/ride-discounts/v3/match-discounts')
    def match_discounts_handler(request):
        return ride_discounts.process(mockserver)

    return match_discounts_handler
