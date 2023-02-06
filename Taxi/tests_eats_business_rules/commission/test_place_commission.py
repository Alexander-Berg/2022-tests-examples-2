import pytest

from tests_eats_business_rules.commission import helper


async def test_proxy_place_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('123', 'place_delivery', '2017-04-04T15:32:22+00:00')
        .core_response('321', '9.44', '1.2', '100')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(
    EATS_BUSINESS_RULES_FEATURES={
        'core_commission_verification_enabled': True,
    },
)
async def test_proxy_place_commission(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('commission_mismatch')
    def _commission_mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('123', 'place_delivery', '2017-04-04T15:32:22+00:00')
        .core_response('321', '9.44', '1.2', '100')
        .core_commission_response('9.44', '1.2', '100')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _commission_mismatch.times_called == 0


@pytest.mark.config(
    EATS_BUSINESS_RULES_FEATURES={
        'core_commission_verification_enabled': True,
    },
)
async def test_proxy_place_commission_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('commission_mismatch')
    def _commission_mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('123', 'place_delivery', '2017-04-04T15:32:22+00:00')
        .core_response('321', '9.44', '1.2', '100')
        .core_commission_response('10', '1.2', '100')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _commission_mismatch.times_called == 1


async def test_proxy_place_commission_core_error(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('123', 'place_delivery', '2017-04-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(400, 'CORE_ERROR', 'Something went wrong')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2020-11-04T15:32:22+00:00')
        .expected_result('commission_3', '21', '9', '0', '0.5')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_commission_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2000-12-04T15:32:22+00:00')
        .should_fail(404, 'NOT_FOUND', 'Cannot find commission')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_commission_incorrect_data(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.CommissionTest()
        .request(
            '12000000000000000000000',
            'place_delivery',
            '2000-12-04T15:32:22+00:00',
        )
        .should_fail(
            400,
            'FORMAT_ERROR',
            'Incorrect counterparty id: \'12000000000000000000000\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


# Комиссии нет нигде fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_commission_not_found_everywhere(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2018-04-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_EVERYWHERE', 'Commission id: \'12\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


# Комиссии нет нигде compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_commission_not_found_everywhere(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2018-04-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_EVERYWHERE', 'Commission id: \'12\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )


# Комиссия есть везде и совпадает fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_commission_happy_path(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2020-12-02T15:32:22+00:00')
        .expected_result('commission_5', '21', '4.44', '200', '0.2')
        .core_response('21', '4.44', '0.2', '200')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 0


# Комиссия есть везде и не совпадает fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_commission_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2021-04-04T15:32:22+00:00')
        .expected_result('', '22', '4.45', '200', '0.3')
        .core_response('22', '4.45', '0.3', '200')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 1


# Комиссия есть везде и совпадает compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_commission_happy_path(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2020-12-02T15:32:22+00:00')
        .expected_result('commission_5', '21', '4.44', '200', '0.2')
        .core_response('21', '4.44', '0.2', '200')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 0


# Комиссия есть везде и не совпадает compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_commission_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('mismatch')
    def _mismatch(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2021-04-04T15:32:22+00:00')
        .expected_result('', '22', '4.45', '200', '0.3')
        .core_response('22', '4.45', '0.3', '200')
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _mismatch.times_called == 1


# Нету комисси в коре, режим fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_proxy_commission_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found_commission_fallback')
    def _not_found_commission_fallback(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2021-04-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Something went wrong')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_FALLBACK', 'Commission id: \'12\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found_commission_fallback.times_called == 1


# Нету комисси в сервисе есть в коре, режим fallback
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_proxy_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2010-04-04T15:32:22+00:00')
        .expected_result('', '22', '4.45', '200', '0.3')
        .core_response('22', '4.45', '0.3', '200')
        .run(taxi_eats_business_rules, mockserver)
    )


# Нету комисси в коре, режим compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_commission_happy_path(
        taxi_eats_business_rules, mockserver,
):

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2021-04-04T15:32:22+00:00')
        .expected_result('commission_5', '21', '4.44', '200', '0.2')
        .core_response_error(400, 'error', 'Something went wrong')
        .run(taxi_eats_business_rules, mockserver)
    )


# Нету комисси в сервисе есть в коре, режим compare
@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_commission_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found_commission_compare')
    def _not_found_commission_compare(data):
        pass

    await (
        helper.CommissionTest()
        .request('12', 'place_delivery', '2010-04-04T15:32:22+00:00')
        .core_response('22', '4.45', '0.3', '200')
        .should_fail(
            404, 'NOT_FOUND_COMMISSION_COMPARE', 'Commission id: \'12\'',
        )
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found_commission_compare.times_called == 1
