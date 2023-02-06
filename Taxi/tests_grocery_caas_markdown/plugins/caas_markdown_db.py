import dataclasses
import decimal

import pytest

from tests_grocery_caas_markdown.common import constants


ADD_MARKDOWN_PRODUCTS = """
INSERT INTO caas_markdown.markdown_products (
    depot_id, product_id, quantity
)
VALUES
{}
ON CONFLICT (depot_id, product_id)
DO UPDATE
SET quantity = excluded.quantity
"""

GET_MARKDOWN_PRODUCTS = """
SELECT depot_id, product_id, quantity
FROM caas_markdown.markdown_products
"""


@dataclasses.dataclass
class MarkdownProduct:
    product_id: str
    quantity: decimal.Decimal = constants.DEFAULT_PRODUCT_QUANTITY


@dataclasses.dataclass
class MarkdownProductWithDepot:
    depot_id: str
    product_id: str
    quantity: decimal.Decimal


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['grocery_caas_markdown']
    cursor = db.cursor()
    cursor.execute(sql_query)
    return cursor


class CaasMarkdownDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def add_markdown_products(self, depot_id, products):
        if isinstance(products, MarkdownProduct):
            products = [products]
        elif isinstance(products, str):
            products = [MarkdownProduct(product_id=products)]
        elif isinstance(products, list) and isinstance(products[0], str):
            products = [
                MarkdownProduct(product_id=product) for product in products
            ]

        values = [
            f'(\'{depot_id}\', \'{product.product_id}\', '
            f'\'{product.quantity}\')'
            for product in products
        ]
        sql_query = ADD_MARKDOWN_PRODUCTS.format(', '.join(values))
        _execute_sql_query(sql_query=sql_query, pgsql=self._pgsql)

    def get_markdown_products(self):
        cursor = _execute_sql_query(
            sql_query=GET_MARKDOWN_PRODUCTS, pgsql=self._pgsql,
        )
        markdown_products = cursor.fetchall()
        markdown_products = [
            MarkdownProductWithDepot(
                depot_id=markdown_product[0],
                product_id=markdown_product[1],
                quantity=markdown_product[2],
            )
            for markdown_product in markdown_products
        ]
        return sorted(
            markdown_products,
            key=lambda product: (product.depot_id, product.product_id),
        )


@pytest.fixture(name='caas_markdown_db')
def mock_caas_markdown_db(pgsql):
    return CaasMarkdownDbAgent(pgsql=pgsql)
