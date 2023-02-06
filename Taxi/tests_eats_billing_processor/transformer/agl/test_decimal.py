import pytest
import yaml

from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    order_cancelled:
      - skip:
            - test#add:
                values#xget: /event/products
                path: value_amount
                filter-key: product_type
                filter-value: product
            - test_sub#sub:
                values#xget: /event/products
                path: value_amount
            - test_mul#mul:
                values#xget: /event/products
                path: value_amount
            - test_div#div:
                values#xget: /event/products
                path: value_amount
            - test_min#min:
                values#xget: /event/products
                path: value_amount
            - test_max#max:
                values#xget: /event/products
                path: value_amount
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_add(testpoint, transformer_fixtures):
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='2000',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='10',
                    product_type='delivery',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='5',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='2',
                    product_type='product',
                ),
            ],
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {
        'test': '2007',
        'test_div': '20',
        'test_max': '2000',
        'test_min': '2',
        'test_mul': '200000',
        'test_sub': '1983',
    }


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    compensation:
      - skip:
            - amount#add:
                values#concat-arrays:
                    - value#array:
                        - value#add:
                            values#xget: /event/items
                            path: amount
                            filter-key: type
                            filter-value: product
                    - value#map:
                        input#xget: /event/items
                        iterator: item
                        element#add:
                            values#xget: /iterators/item/discounts
                            path: amount
                        filter#equal:
                            - value#xget: /iterators/item/type
                            - value: product
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_add_subarray(testpoint, transformer_fixtures):
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .on_compensation(
            is_place_fault=True,
            place_id='place_2',
            items=[
                common.make_compensation_item(
                    product_type='product',
                    amount='200',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='compensation', amount='50',
                        ),
                    ],
                ),
                common.make_compensation_item(
                    product_type='product',
                    amount='400',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='compensation', amount='50',
                        ),
                        common.make_compensation_discount(
                            discount_type='marketing', amount='150',
                        ),
                    ],
                ),
                common.make_compensation_item(
                    product_type='delivery',
                    amount='100',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='marketing', amount='20',
                        ),
                    ],
                ),
            ],
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {'amount': '850'}
