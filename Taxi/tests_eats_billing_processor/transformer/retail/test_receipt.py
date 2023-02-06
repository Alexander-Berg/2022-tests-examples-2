from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.retail import helper


async def test_happy_path_positive_commission(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_receipt(place_id='place_1', amount='200')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='1',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payload={
                    'commission_rate': '10',
                    'date': '2021-07-10T12:22:00+03:00',
                    'fiscal_document_number': 1,
                    'fiscal_drive_number': 'fdn',
                    'fiscal_sign': 'fs',
                    'operation_type': 'income',
                    'place_id': 'place_1',
                    'sum': '200',
                },
                commission=common.make_commission(
                    product_type='retail',
                    product_id='retail__001',
                    amount='32',
                    commission_type='retail',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_negative_commission(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_receipt(place_id='place_2', amount='-300')
        .using_business_rules(
            place_id='place_2',
            client_info=rules.client_info(client_id='2345'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='1',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='2345'),
                payload={
                    'commission_rate': '10',
                    'date': '2021-07-10T12:22:00+03:00',
                    'fiscal_document_number': 1,
                    'fiscal_drive_number': 'fdn',
                    'fiscal_sign': 'fs',
                    'operation_type': 'income',
                    'place_id': 'place_2',
                    'sum': '-300',
                },
                commission=common.make_commission(
                    product_type='retail',
                    product_id='retail__001',
                    amount='-43',
                    commission_type='retail',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
