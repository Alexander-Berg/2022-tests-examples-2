import pytest

from tests_eats_business_rules.fine import helper


async def test_proxy_place_fine_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .core_response(22, '1.0', '5')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_place_fine_core_error(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(400, 'CORE_ERROR', 'Something went wrong')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_fine_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_2', '12', 48, '2.5', '4.5', '0.5', '10', '7')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_fine_happy_path_common_rule(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'place',
            '52',
            'restaurant',
            'native',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_7', '777', 24, '2.5', '5', '0.7', '10', '8')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_fine_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'place',
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
async def test_full_feature_place_fine_incorrect_data(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.FineTest()
        .request(
            'place',
            '1200000000000000000000',
            'restaurant',
            'native',
            'cancellation',
            '2020-12-04T15:32:22+00:00',
        )
        .should_fail(
            400,
            'FORMAT_ERROR',
            'Incorrect counterparty id: \'1200000000000000000000\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


# штрафа нет нигде fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_fine_not_found_everywhere(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'restaurant',
            'native',
            'cancellation',
            '2020-12-04T15:32:22+00:00',
        )
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(404, 'NOT_FOUND_FINE_ANYWHERE', 'Fine id: \'12\'')
        .run(taxi_eats_business_rules, mockserver)
    )


# Штрафа нет нигде compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_fine_not_found_everywhere(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'restaurant',
            'native',
            'cancellation',
            '2020-12-04T15:32:22+00:00',
        )
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(404, 'NOT_FOUND_FINE_ANYWHERE', 'Fine id: \'12\'')
        .run(taxi_eats_business_rules, mockserver)
    )


# Штраф есть везде и совпадает fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_fine_happy_path(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .core_response(48, '2.5', '7')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 0


# Штраф есть везде и не совпадает fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_fine_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_2', '21', 48, '2.5', '4.5', '0.5', '10', '7')
        .core_response(48, '2.5', '8')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 1


# Штраф есть везде и совпадает compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_fine_happy_path(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_2', '21', 48, '2.5', '4.5', '0.5', '10', '7')
        .core_response(48, '2.5', '7')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 0


# Штраф есть везде и не совпадает compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_fine_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_2', '21', 48, '2.5', '4.5', '0.5', '10', '7')
        .core_response(50, '2.5', '7')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 1


# Нет штрафа в коре, режим fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_proxy_fine_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found_fine_fallback')
    def _not_found_fine_fallback(data):
        pass

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(404, 'NOT_FOUND_FINE_FALLBACK', 'Fine id: \'12\'')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found_fine_fallback.times_called == 1


# Нет штрафа в сервисе есть в коре, режим fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_proxy_fine_happy_path(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.FineTest()
        .request(
            'place',
            '12121',
            'shop',
            'pickup',
            'return',
            '2010-12-04T15:32:22+00:00',
        )
        .expected_result('', '15', 24, '2.5', '', '', '10', '7')
        .core_response(24, '2.5', '7')
        .run(taxi_eats_business_rules, mockserver)
    )


# Нет штрафа в коре, режим compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_fine_happy_path(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.FineTest()
        .request(
            'place',
            '12',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .expected_result('rule_2', '21', 48, '2.5', '4.5', '0.5', '10', '7')
        .core_response_error(400, 'error', 'Something went wrong')
        .run(taxi_eats_business_rules, mockserver)
    )


# Нет штрафа в сервисе есть в коре, режим compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_fine_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found_fine_compare')
    def _not_found_fine_compare(data):
        pass

    await (
        helper.FineTest()
        .request(
            'place',
            '123',
            'shop',
            'pickup',
            'return',
            '2020-12-04T15:32:22+00:00',
        )
        .core_response(50, '2.5', '7')
        .should_fail(404, 'NOT_FOUND_FINE_COMPARE', 'Fine id: \'123\'')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found_fine_compare.times_called == 1
