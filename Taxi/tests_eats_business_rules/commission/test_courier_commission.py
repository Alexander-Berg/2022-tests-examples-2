import pytest

from tests_eats_business_rules.commission import helper


async def test_proxy_courier_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('123', 'picker_delivery', '2017-04-04T15:32:22+00:00')
        .core_response('321', '9.44', '1.2', '100')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_core_error(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('123', 'courier_delivery', '2017-04-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(400, 'CORE_ERROR', 'Something went wrong')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_donation_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'donation', '2021-12-04T15:32:22+00:00')
        .expected_result('', '12', '2', '0.01', '0')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_subsidized_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request(
            '12', 'subsidized_by_place_promocode', '2021-12-04T15:32:22+00:00',
        )
        .expected_result('', '12', '0', '1', '0')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_grocery_delivery_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_delivery', '2021-12-04T15:32:22+00:00')
        .expected_result('', '12', '2', '0', '0', 'weekly')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_grocery_product_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_product', '2021-12-04T15:32:22+00:00')
        .expected_result('', '12', '2', '0', '0', 'weekly')
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_donation_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'donation', '2010-12-04T15:32:22+00:00')
        .should_fail(
            404, 'NOT_FOUND', 'Cannot find appropriate donation commission',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_grocery_delivery_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_delivery', '2021-06-04T15:32:22+00:00')
        .should_fail(
            404,
            'NOT_FOUND',
            'Cannot find appropriate grocery_delivery commission',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_courier_commission_grocery_product_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_product', '2021-06-04T15:32:22+00:00')
        .should_fail(
            404,
            'NOT_FOUND',
            'Cannot find appropriate grocery_product commission',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'tips', '2020-12-04T15:32:22+00:00')
        .expected_result('commission_10', '121', '5.4', '10', '1.5')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'picker_delivery', '2000-12-04T15:32:22+00:00')
        .should_fail(404, 'NOT_FOUND', 'Cannot find commission')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_incorrect_data(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12!', 'tips', '2000-12-04T15:32:22+00:00')
        .should_fail(400, 'FORMAT_ERROR', 'Incorrect counterparty id: \'12!\'')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_donation_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'donation', '2020-12-04T15:32:22+00:00')
        .expected_result('', '12', '20', '0.01', '0')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_donation_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'donation', '2010-12-04T15:32:22+00:00')
        .should_fail(
            404, 'NOT_FOUND', 'Cannot find appropriate donation commission',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_grocery_delivery_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_delivery', '2021-12-04T15:32:22+00:00')
        .expected_result('', '12', '2', '0', '0', 'weekly')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_grocery_product_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_product', '2021-12-04T15:32:22+00:00')
        .expected_result('', '12', '2', '0', '0', 'weekly')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_grocery_delivery_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_delivery', '2010-12-04T15:32:22+00:00')
        .should_fail(
            404,
            'NOT_FOUND',
            'Cannot find appropriate grocery_delivery commission',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_courier_commission_grocery_product_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'grocery_product', '2010-12-04T15:32:22+00:00')
        .should_fail(
            404,
            'NOT_FOUND',
            'Cannot find appropriate grocery_product commission',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


# Комиссии нет нигде fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_courier_commission_not_found_everywhere(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('13', 'tips', '2020-12-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_EVERYWHERE', 'Commission id: \'13\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


# Комиссии нет нигде compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_courier_commission_not_found_everywhere(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('13', 'tips', '2020-12-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_EVERYWHERE', 'Commission id: \'13\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


# Комиссия есть везде и совпадает fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_courier_commission_happy_path(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'tips', '2020-12-04T15:32:22+00:00')
        .expected_result('commission_8', '121', '5.4', '10', '1.5')
        .core_response('121', '5.4', '1.5', '10')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 0


# Комиссия есть везде и не совпадает fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_courier_commission_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'tips', '2020-12-04T15:32:22+00:00')
        .expected_result('', '22', '4.45', '200', '0.3')
        .core_response('22', '4.45', '0.3', '200')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 1


# Комиссия есть везде и совпадает compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_courier_commission_happy_path(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'tips', '2020-12-04T15:32:22+00:00')
        .expected_result('commission_8', '121', '5.4', '10', '1.5')
        .core_response('121', '5.4', '1.5', '10')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 0


# Комиссия есть везде и не совпадает compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_courier_commission_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'tips', '2020-12-04T15:32:22+00:00')
        .expected_result('', '22', '4.45', '200', '0.3')
        .core_response('22', '4.45', '0.3', '200')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 1


# Нету комисси в коре, режим fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_courier_proxy_commission_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found_commission_fallback')
    def _not_found_commission_fallback(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'tips', '2020-12-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_FALLBACK', 'Commission id: \'12\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found_commission_fallback.times_called == 1


# Нету комисси в сервисе есть в коре, режим fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_courier_proxy_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('13', 'tips', '2010-04-04T15:32:22+00:00')
        .expected_result('', '22', '4.45', '200', '0.3')
        .core_response('22', '4.45', '0.3', '200')
        .run(taxi_eats_business_rules, mockserver)
    )


# Нету комисси в коре, режим compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_courier_db_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('12', 'tips', '2020-12-04T15:32:22+00:00')
        .expected_result('commission_8', '121', '5.4', '10', '1.5')
        .core_response_error(400, 'error', 'Something went wrong')
        .run(taxi_eats_business_rules, mockserver)
    )


# Нету комисси в сервисе есть в коре, режим compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_courier_db_commission_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found_commission_compare')
    def _not_found_commission_compare(data):
        pass

    await (
        helper.CommissionTest()
        .request('13', 'tips', '2010-04-04T15:32:22+00:00')
        .core_response('22', '4.45', '0.3', '200')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_COMPARE', 'Commission id: \'13\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found_commission_compare.times_called == 1
