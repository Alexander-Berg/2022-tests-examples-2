import pytest

from tests_eats_business_rules.fine import helper


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_fine_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'courier',
            '12',
            'restaurant',
            'native',
            'return',
            '2020-11-03T15:32:22+00:00',
        )
        .expected_result('rule_8', '121', 72, '3.5', '5', '0.5', '10', '7')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_fine_cancelled_at(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'courier',
            '34',
            'restaurant',
            'native',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_10', '444', 23, '4.5', '5', '0.5', '10', '7')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_fine_happy_path_common_rule(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'courier',
            '34',
            'restaurant',
            'native',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_10', '444', 23, '4.5', '5', '0.5', '10', '7')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_fine_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'courier',
            '12',
            'restaurant',
            'native',
            'cancellation',
            '2020-12-04T15:32:22+00:00',
        )
        .should_fail(404, 'NOT_FOUND', 'Cannot find fine')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_fine_incorrect_data(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'courier',
            '12!',
            'restaurant',
            'native',
            'cancellation',
            '2020-12-04T15:32:22+00:00',
        )
        .should_fail(400, 'FORMAT_ERROR', 'Incorrect counterparty id: \'12!\'')
        .run(taxi_eats_business_rules, mockserver)
    )
