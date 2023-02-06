import pytest
import yaml

from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    courier_earning:
      - templates:
          - service_name: eats_delivery_selfemp
          - order_nr#xget: /event/order_nr
          - items#map:
                input#xget: /event/details
                iterator: detail
                element#object:
                  - context#object:
                      - order_nr#xget: /event/order_nr
                      - courier_id#xget: /event/courier_id
                      - amount#xget: /iterators/detail/amount
                      - currency#xget: /iterators/detail/currency
                  - template_name#xget: /iterators/detail/account
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_courier_earning(transformer_fixtures):
    await (
        helper.TransformerTest()
        .on_courier_earning(
            courier_id='courier_1',
            details=[
                {
                    'account': 'slot_base_rate',
                    'amount': '100',
                    'currency': 'RUB',
                },
                {
                    'account': 'slot_late_penalty',
                    'amount': '11.25',
                    'currency': 'RUB',
                },
            ],
        )
        .expect_billing_orders_call()
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )
