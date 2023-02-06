# import pytest
#
# from tests_eats_billing_processor import rules
# from tests_eats_billing_processor.input_processor import helper
#
#
# @pytest.mark.parametrize(
#     'kind, rule_name',
#     [
#         pytest.param('monthly_payment', 'default'),
#         pytest.param('additional_promo_payment', 'shop'),
#         pytest.param('mercury_discount', 'inplace'),
#         pytest.param('receipt', 'retail'),
#         pytest.param('order_gmv', 'shop'),
#         # pytest.param('payment_refund', 'retail'),
#         # pytest.param('payment_not_received', 'restaurant'),
#         # pytest.param('order_cancelled', 'marketplace'),
#         # pytest.param('order_delivered', 'shop'),
#         # pytest.param('compensation', 'restaurant'),
#         # pytest.param('plus_cashback_emission', 'restaurant'),
#         # pytest.param('payment_update_plus_cashback', 'shop_marketplace'),
#     ],
# )
# @pytest.mark.config(
#     EATS_BILLING_PROCESSOR_FEATURES={
#         'create_handler_enabled': True,
#         'input_events_v2_enabled': True,
#     },
# )
# async def test_converter_happy_path(
# input_processor_fixtures, kind, rule_name):
#     await (
#         helper.InputProcessorTest()
#         .request(
#             order_nr='123456',
#             external_id='event/123456',
#             event_at='2021-03-18T15:00:00+00:00',
#             rule_name=rule_name,
#             kind=kind,
#             data=input_processor_fixtures.load_json(f'v1/{kind}.json'),
#         )
#         .using_business_rules(
#             place_id='4556',
#             client_info=rules.client_info(
#                 client_id='1', mvp='MSKc', contract_id='1',
#             ),
#         )
#         .expected_rule_name(rule_name)
#         .expected_v2(True)
#         .run(input_processor_fixtures)
#     )
#
#
# @pytest.mark.parametrize(
#     'kind, rule_name, expect_v2',
#     [
#         pytest.param('payment_received', 'restaurant', True),
#         pytest.param('payment_refund', 'retail', False),
#         pytest.param('payment_not_received', 'restaurant', True),
#         pytest.param('order_cancelled', 'marketplace', False),
#         pytest.param('order_delivered', 'shop', False),
#     ],
# )
# @pytest.mark.config(
#     EATS_BILLING_PROCESSOR_FEATURES={
#         'create_handler_enabled': True,
#         'input_events_v2_enabled': True,
#         'input_events_v2_whitelist': {
#             'restaurant': ['payment_received', 'payment_not_received'],
#             'marketplace': [],
#         },
#     },
# )
# async def test_converter_white_list(
#         input_processor_fixtures, kind, rule_name, expect_v2,
# ):
#     await (
#         helper.InputProcessorTest()
#         .request(
#             order_nr='123456',
#             external_id='event/123456',
#             event_at='2021-03-18T15:00:00+00:00',
#             rule_name=rule_name,
#             kind=kind,
#             data=input_processor_fixtures.load_json(f'v2/{kind}.json'),
#         )
#         .expected_rule_name(rule_name)
#         .expected_v2(expect_v2)
#         .run(input_processor_fixtures)
#     )
