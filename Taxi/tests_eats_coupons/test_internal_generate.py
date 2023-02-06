import pytest

from tests_eats_coupons import conftest


@pytest.mark.parametrize(
    'promocode_type,' 'refund_type,' 'value, promo_num',
    [
        pytest.param('sorry', 'percent', 30, 0),
        pytest.param('welcome', 'fixed', 100, 1),
    ],
)
async def test_internal_generate(
        taxi_eats_coupons,
        mockserver,
        taxi_config,
        promocode_type,
        refund_type,
        value,
        promo_num,
        mock_coupons_client,
        request_context,
):
    promocode = 'promic'
    request_context.set_params(
        conftest.RequestParams(promo_num, value, promocode),
    )

    config = {promocode_type: conftest.PROMOCODE_DESCRIPTION}
    taxi_config.set_values(
        {'EATS_COUPONS_PROMOCODES_SERIES_AND_CONDITIONS': config},
    )

    request = conftest.DEFAULT_REQUEST.copy()
    request['promocode_type'] = promocode_type
    request['conditions']['refund_type'] = refund_type
    request['value'] = value

    response = await taxi_eats_coupons.post(conftest.PATH, json=request)
    assert response.status_code == 200
    assert promocode


async def test_no_promocode_type_in_config(taxi_eats_coupons):
    response = await taxi_eats_coupons.post(
        conftest.PATH, json=conftest.DEFAULT_REQUEST,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'resp_code, add_cond',
    [
        (
            200,
            {
                'refund_type': 'percent',
                'country': 'rus',
                'brand_ids': [4, 2, 5, 1, 7],
                'other1': [4, 2, 3],
                'other2': ['hello', 'world'],
                'other3': 123,
                'other4': 'Hello world',
            },
        ),
        (
            400,
            {
                'refund_type': 'percent',
                'country': 'rus',
                'brand_ids': [4, 2, 5, 1, 7],
                'other1': [4, '2', 3],
            },
        ),
        (
            400,
            {
                'refund_type': 'percent',
                'country': 'us',
                'brand_ids': [4, 2, 5, 1, 7],
                'other1': [4, 2, 3],
            },
        ),
    ],
)
async def test_internal_generate_additional_conditions(
        taxi_eats_coupons,
        mockserver,
        taxi_config,
        mock_coupons_client,
        request_context,
        resp_code,
        add_cond,
):
    promocode = 'promic'
    promocode_type = 'welcome'
    value = 10
    request_context.set_params(conftest.RequestParams(2, value, promocode))

    config = {promocode_type: conftest.PROMOCODE_DESCRIPTION}
    taxi_config.set_values(
        {'EATS_COUPONS_PROMOCODES_SERIES_AND_CONDITIONS': config},
    )

    request = conftest.DEFAULT_REQUEST.copy()
    request['promocode_type'] = promocode_type
    request['value'] = value
    request['conditions'] = add_cond

    response = await taxi_eats_coupons.post(conftest.PATH, json=request)
    assert response.status_code == resp_code
    assert promocode


@pytest.mark.parametrize('taxi_coupons_response', [409, 424])
async def test_response_proxy(
        taxi_eats_coupons,
        mockserver,
        mock_coupons_response_proxy,
        response_context,
        taxi_config,
        taxi_coupons_response,
):
    response_context.set_params(
        conftest.ResponseParams(code=taxi_coupons_response),
    )

    config = {
        conftest.DEFAULT_REQUEST[
            'promocode_type'
        ]: conftest.PROMOCODE_DESCRIPTION,
    }
    taxi_config.set_values(
        {'EATS_COUPONS_PROMOCODES_SERIES_AND_CONDITIONS': config},
    )

    response = await taxi_eats_coupons.post(
        conftest.PATH, json=conftest.DEFAULT_REQUEST,
    )
    assert response.status_code == taxi_coupons_response


async def test_request_generate_timeout(
        taxi_config, taxi_eats_coupons, mockserver,
):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + conftest.PATH)
    def _mock_coupons(request):
        raise mockserver.TimeoutError()

    config = {
        conftest.DEFAULT_REQUEST[
            'promocode_type'
        ]: conftest.PROMOCODE_DESCRIPTION,
    }
    taxi_config.set_values(
        {'EATS_COUPONS_PROMOCODES_SERIES_AND_CONDITIONS': config},
    )

    expected_status_code = 408

    response = await taxi_eats_coupons.post(
        conftest.PATH, json=conftest.DEFAULT_REQUEST,
    )
    assert response.status_code == expected_status_code


async def test_request_generate_network(
        taxi_config, taxi_eats_coupons, mockserver,
):
    @mockserver.json_handler('/coupons' + conftest.PATH)
    def _mock_coupons(request):
        raise mockserver.NetworkError()

    config = {
        conftest.DEFAULT_REQUEST[
            'promocode_type'
        ]: conftest.PROMOCODE_DESCRIPTION,
    }
    taxi_config.set_values(
        {'EATS_COUPONS_PROMOCODES_SERIES_AND_CONDITIONS': config},
    )

    expected_status_code = 424

    response = await taxi_eats_coupons.post(
        conftest.PATH, json=conftest.DEFAULT_REQUEST,
    )
    assert response.status_code == expected_status_code


@pytest.mark.config(
    EATS_COUPONS_PROMOCODES_SERIES_AND_CONDITIONS={
        'sorry': conftest.PROMOCODE_DESCRIPTION,
    },
)
async def test_promocode_meta_save(
        taxi_eats_coupons,
        mockserver,
        mock_coupons_client,
        request_context,
        mongodb,
):
    promocode = 'promic'
    request_context.set_params(
        conftest.RequestParams(promo_num=0, value=300, promocode=promocode),
    )

    request = conftest.DEFAULT_REQUEST.copy()
    request['promocode_type'] = 'sorry'
    request['conditions']['refund_type'] = 'percent'
    request['value'] = 300
    request['promocode_meta'] = {'places-ids': ['1', '2']}

    response = await taxi_eats_coupons.post(conftest.PATH, json=request)
    assert response.status_code == 200

    doc = mongodb.mdb_promocode_additional_info.find_one(
        {'promocode': promocode},
    )
    assert doc
    assert doc['promocode_meta'] == request['promocode_meta']
