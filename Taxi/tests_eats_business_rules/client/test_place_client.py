import pytest

from tests_eats_business_rules.client import helper


async def test_proxy_place_client_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.ClientTest()
        .request('place', '123', '2017-04-04T15:32:22+00:00')
        .core_response('321', '9.44', '1.2', '100')
        .times_called(3)
        .run(taxi_eats_business_rules, mockserver)
    )


async def test_proxy_place_client_core_error(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.ClientTest()
        .request('place', '123', '2017-04-04T15:32:22+00:00')
        .core_response_error(400, 'error', 'Unknown error')
        .times_called(3)
        .should_fail(400, 'CORE_ERROR', 'Unknown error')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_client_happy_path(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.ClientTest()
        .request('place', '34', '2017-04-04T15:32:22+00:00')
        .expected_result('43')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_client_not_found(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.ClientTest()
        .request('place', '18', '2017-04-04T15:32:22+00:00')
        .should_fail(404, 'NOT_FOUND', 'Cannot find client')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='full_feature')
async def test_full_feature_place_client_incorrect_data(
        taxi_eats_business_rules, mockserver,
):
    await (
        helper.ClientTest()
        .request('place', '12!', '2017-04-04T15:32:22+00:00')
        .should_fail(400, 'FORMAT_ERROR', 'Incorrect counterparty id: \'12!\'')
        .run(taxi_eats_business_rules, mockserver)
    )


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_commission_happy_path(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found')
    def _not_found(data):
        pass

    await (
        helper.ClientTest()
        .request('place', '12', '2017-04-04T15:32:22+00:00')
        .core_response('21', '9', '0.5', '0')
        .times_called(3)
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found.times_called == 0


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_client_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found')
    def _not_found(data):
        pass

    await (
        helper.ClientTest()
        .request('place', '13', '2017-04-04T15:32:22+00:00')
        .core_response('21', '4.44', '0.2', '200')
        .times_called(3)
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found.times_called == 1


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='fallback')
async def test_fallback_place_db_client_mismatch(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found')
    def _not_found(data):
        pass

    @testpoint('mismatch_client_id')
    def _mismatch_client_id(data):
        pass

    await (
        helper.ClientTest()
        .request('place', '12', '2017-04-04T15:32:22+00:00')
        .core_response('22', '4.45', '0.3', '200')
        .times_called(3)
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found.times_called == 0
    assert _mismatch_client_id.times_called == 1


@pytest.mark.config(EATS_BUSINESS_RULES_MODE_SWITCH='compare')
async def test_compare_place_db_client_not_found(
        taxi_eats_business_rules, mockserver, testpoint,
):
    @testpoint('not_found')
    def _not_found(data):
        pass

    @testpoint('not_found_compare_mode')
    def _not_found_compare_mode(data):
        pass

    await (
        helper.ClientTest()
        .request('place', '13', '2017-04-04T15:32:22+00:00')
        .core_response('21', '4.44', '0.2', '200')
        .times_called(3)
        .run(taxi_eats_business_rules, mockserver)
    )

    assert _not_found.times_called == 1
    assert _not_found_compare_mode.times_called == 1
