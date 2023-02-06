from tests_eats_business_rules.commission import helper


async def test_dynamic_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('123', 'markup', '2022-04-04T15:32:22+00:00')
        .expected_result('', '', '50', '0', '0')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_dynamic_commission_by_place_id(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('561', 'markup', '2022-04-04T15:32:22+00:00')
        .expected_result('', '', '55', '0', '0')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_dynamic_commission_fail(taxi_eats_business_rules, mockserver):
    await (
        helper.CommissionTest()
        .request('561', 'markup', '2010-04-04T15:32:22+00:00')
        .should_fail(404, 'NOT_FOUND', 'Dynamic commission not found')
        .run(taxi_eats_business_rules, mockserver)
    )
