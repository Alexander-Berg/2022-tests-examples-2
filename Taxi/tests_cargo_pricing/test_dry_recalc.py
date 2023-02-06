import pytest

from tests_cargo_pricing import utils


@pytest.fixture(name='config_requirements_desciption')
async def _config_requirements_desciption(taxi_cargo_pricing, taxi_config):
    taxi_config.set_values(
        dict(
            CARGO_PRICING_DRY_RECALC_REQUIREMENTS_DESCRIPTION={
                'select': {
                    'cargo_type_int': [
                        {'name': 'lvm', 'value': 1, 'independent': True},
                    ],
                    'select_requirement2': [
                        {'name': 'val1', 'value': 1, 'independent': False},
                        {'name': 'val2', 'value': 2, 'independent': False},
                    ],
                    'pro_courier': [
                        {'name': 'coef', 'value': 1, 'independent': True},
                    ],
                },
            },
        ),
    )
    await taxi_cargo_pricing.invalidate_caches()


def _get_default_dry_recalc_request(prev_calc_id=None, price_for='client'):
    request = utils.get_default_calc_request()
    request['taxi_requirements'] = {
        'door_to_door': True,
        'cargo_type_int': 1,
        'select_requirement2': 2,
        'bool_requirement2': True,
        'false_bool_requirement': False,
    }
    request['price_for'] = price_for
    if prev_calc_id is not None:
        request['previous_calc_id'] = prev_calc_id
    if price_for == 'performer':
        request['performer'] = {'driver_id': 'uuid0', 'park_db_id': 'dbid0'}
    return request


@pytest.fixture(name='v1_dry_recalc')
def _v1_dry_recalc(taxi_cargo_pricing):
    async def _call(request):
        return await taxi_cargo_pricing.post(
            '/cargo-pricing/admin/v1/taxi/dry-recalc', json=request,
        )

    return _call


@pytest.fixture(name='call_dry_recalc')
async def _call_dry_recalc(
        v1_dry_recalc,
        mock_pricing_recalc,
        mock_route,
        config_requirements_desciption,
        user_options,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_get_calc_id_from_processing,
):
    class CalcRequestCreator:
        mock_recalc = mock_pricing_recalc
        mock_router = mock_route

        async def execute(
                self,
                prev_calc_id=None,
                price_for='client',
                extra_requirements=None,
        ):
            payload = _get_default_dry_recalc_request(
                prev_calc_id=prev_calc_id, price_for=price_for,
            )
            if extra_requirements is not None:
                payload['taxi_requirements'].update(extra_requirements)
            return await v1_dry_recalc(request=payload)

    await conf_exp3_get_calc_id_from_processing(enabled=True)

    return CalcRequestCreator()


@pytest.fixture(name='create_previous_calc')
def _create_previous_calc(v1_calc_creator, mock_get_processing_events):
    async def _call(put_processing_events=True, price_for='client'):
        create_resp = await v1_calc_creator.execute()
        assert create_resp.status_code == 200
        calc_id = create_resp.json()['calc_id']

        if put_processing_events:
            processing_events = [
                {
                    'event_id': 'event_id_1',
                    'created': utils.from_start(minutes=0),
                    'handled': True,
                    'payload': {'kind': 'create'},
                },
                {
                    'event_id': 'event_id_2',
                    'created': utils.from_start(minutes=0),
                    'handled': True,
                    'payload': {
                        'kind': 'calculation',
                        'calc_id': calc_id,
                        'price_for': price_for,
                        'origin_uri': 'some/origin/uri',
                        'calc_kind': 'final',
                    },
                },
            ]
            if price_for == 'performer':
                processing_events[1]['payload']['performer'] = {
                    'driver_id': 'uuid0',
                    'park_db_id': 'dbid0',
                }
        else:
            processing_events = []

        mock_get_processing_events.response = {'events': processing_events}

        return calc_id

    return _call


@pytest.fixture(name='default_dry_recalc_response')
def _default_dry_recalc_response(load_json):
    def _get(prev_calc_id, processing_event=True, price_for='client'):
        expected_resp = load_json('expected_taxi_calc_response.json')
        expected_diagnostics = expected_resp['diagnostics']

        dry_recalc_request = _get_default_dry_recalc_request(
            prev_calc_id=prev_calc_id, price_for=price_for,
        )
        expected_diagnostics['calc_request'] = dry_recalc_request

        expected_diagnostics['calc_request']['previous_calc_id'] = prev_calc_id
        expected_diagnostics['calc_request']['price_for'] = price_for

        expected_requirements = _get_default_v2_prepare_expected_requirements()
        if price_for == 'performer':
            expected_resp['prices']['total_price'] = str(
                expected_diagnostics['recalc_response']['driver']['total'],
            )
            expected_diagnostics['taxi_pricing_response']['driver']['data'][
                'requirements'
            ] = expected_requirements
        else:
            expected_diagnostics['taxi_pricing_response']['user']['data'][
                'requirements'
            ] = expected_requirements

        if processing_event:
            expected_diagnostics['processing_events'] = [
                {'kind': 'create'},
                {
                    'calc_id': prev_calc_id,
                    'calc_kind': 'final',
                    'kind': 'calculation',
                    'origin_uri': 'some/origin/uri',
                    'price_for': price_for,
                },
            ]
            if price_for == 'performer':
                expected_diagnostics['processing_events'][1]['performer'] = {
                    'driver_id': 'uuid0',
                    'park_db_id': 'dbid0',
                }
        else:
            expected_diagnostics['processing_events'] = []

        return expected_resp

    return _get


def _get_default_v2_prepare_expected_requirements():
    return {
        'select': {
            'cargo_type_int': [{'independent': True, 'name': 'lvm'}],
            'select_requirement2': [{'independent': False, 'name': 'val2'}],
        },
        'simple': ['bool_requirement2', 'door_to_door'],
    }


async def test_dry_recalc_response(
        call_dry_recalc, create_previous_calc, default_dry_recalc_response,
):
    prev_calc_id = await create_previous_calc()

    response = await call_dry_recalc.execute(prev_calc_id=prev_calc_id)
    assert response.status_code == 200
    resp = response.json()

    assert resp.pop('calc_id') == ''
    assert resp == default_dry_recalc_response(prev_calc_id=prev_calc_id)


async def test_dry_recalc_response_performer_price(
        call_dry_recalc,
        create_previous_calc,
        default_dry_recalc_response,
        v1_drivers_match_profile,
):
    prev_calc_id = await create_previous_calc(price_for='performer')

    response = await call_dry_recalc.execute(
        prev_calc_id=prev_calc_id, price_for='performer',
    )
    assert response.status_code == 200
    resp = response.json()

    assert resp.pop('calc_id') == ''
    assert resp == default_dry_recalc_response(
        prev_calc_id=prev_calc_id, price_for='performer',
    )


async def test_dry_recalc_response_old_way_previous_calc_id(
        call_dry_recalc,
        create_previous_calc,
        default_dry_recalc_response,
        conf_exp3_get_calc_id_from_processing,
):
    prev_calc_id = await create_previous_calc(put_processing_events=False)
    await conf_exp3_get_calc_id_from_processing(enabled=False)

    response = await call_dry_recalc.execute(prev_calc_id=prev_calc_id)
    assert response.status_code == 200
    resp = response.json()

    assert resp.pop('calc_id') == ''
    assert resp == default_dry_recalc_response(
        prev_calc_id=prev_calc_id, processing_event=False,
    )


async def test_dry_recalc_pdp_calls(
        call_dry_recalc,
        create_previous_calc,
        mock_pricing_prepare,
        mock_pricing_recalc,
):
    prev_calc_id = await create_previous_calc()
    assert mock_pricing_prepare.mock.times_called == 1
    assert mock_pricing_recalc.mock.times_called == 1

    response = await call_dry_recalc.execute(prev_calc_id=prev_calc_id)
    assert response.status_code == 200
    assert mock_pricing_prepare.mock.times_called == 1
    assert mock_pricing_recalc.mock.times_called == 2


async def test_dry_recalc_pdp_recalc_requirements(
        call_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    response = await call_dry_recalc.execute(prev_calc_id=prev_calc_id)
    assert response.status_code == 200

    recalc_request = call_dry_recalc.mock_recalc.request
    assert (
        recalc_request['user']['backend_variables']['requirements']
        == _get_default_v2_prepare_expected_requirements()
    )


async def test_dry_recalc_no_old_way_previous_calc(
        call_dry_recalc, conf_exp3_get_calc_id_from_processing,
):
    await conf_exp3_get_calc_id_from_processing(enabled=False)

    response = await call_dry_recalc.execute(
        prev_calc_id='cargo-pricing/v1/00000000-0000-0000-0000-000000000000',
    )
    assert response.status_code == 404
    assert response.json() == {}


async def test_dry_recalc_no_previous_calc_in_processing(
        call_dry_recalc, mock_get_processing_events,
):
    response = await call_dry_recalc.execute()
    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_request',
        'message': 'No previous calc id',
    }


async def test_dry_recalc_undescribed_requirement(
        call_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    response = await call_dry_recalc.execute(
        prev_calc_id=prev_calc_id,
        extra_requirements={'unknown_requirement': 1},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_requirements',
        'message': 'unknown_requirement-requirement not descripted in config',
    }


async def test_dry_recalc_undescribed_requirement_select_value(
        call_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    response = await call_dry_recalc.execute(
        prev_calc_id=prev_calc_id, extra_requirements={'cargo_type_int': 2},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_requirements',
        'message': (
            'cargo_type_int-requirement has undescribed in config value'
        ),
    }


@pytest.mark.skip('flappy in the last assertion')
async def test_dry_recalc_with_pro_courier(
        call_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    response = await call_dry_recalc.execute(
        prev_calc_id=prev_calc_id, extra_requirements={'pro_courier': True},
    )
    assert response.status_code == 200

    recalc_request = call_dry_recalc.mock_recalc.request
    expected_reqs = _get_default_v2_prepare_expected_requirements()
    expected_reqs['select']['pro_courier'] = [
        {'name': 'coef', 'independent': True},
    ]
    assert (
        recalc_request['user']['backend_variables']['requirements']
        == expected_reqs
    )


async def test_dry_recalc_with_false_pro_courier(
        call_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    response = await call_dry_recalc.execute(
        prev_calc_id=prev_calc_id, extra_requirements={'pro_courier': False},
    )
    assert response.status_code == 200

    recalc_request = call_dry_recalc.mock_recalc.request
    assert (
        recalc_request['user']['backend_variables']['requirements']
        == _get_default_v2_prepare_expected_requirements()
    )


async def test_dry_recalc_with_pro_courier_wrong_type(
        call_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    response = await call_dry_recalc.execute(
        prev_calc_id=prev_calc_id, extra_requirements={'pro_courier': 1},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_requirements',
        'message': 'pro_courier requirement expected of \'bool\' type',
    }


async def test_dry_recalc_with_empty_requirements_list(
        call_dry_recalc, v1_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    request = _get_default_dry_recalc_request(prev_calc_id=prev_calc_id)
    request['taxi_requirements'] = {}
    response = await v1_dry_recalc(request=request)
    assert response.status_code == 200

    recalc_request = call_dry_recalc.mock_recalc.request
    expected_reqs = _get_default_v2_prepare_expected_requirements()
    expected_reqs['select'] = {}
    expected_reqs['simple'] = []
    assert (
        recalc_request['user']['backend_variables']['requirements']
        == expected_reqs
    )


async def test_dry_recalc_with_null_requirements_list(
        call_dry_recalc, v1_dry_recalc, create_previous_calc,
):
    prev_calc_id = await create_previous_calc()

    request = _get_default_dry_recalc_request(prev_calc_id=prev_calc_id)
    request.pop('taxi_requirements')
    response = await v1_dry_recalc(request=request)
    assert response.status_code == 200

    recalc_request = call_dry_recalc.mock_recalc.request
    expected_reqs = _get_default_v2_prepare_expected_requirements()
    expected_reqs['select'] = {}
    expected_reqs['simple'] = []
    assert (
        recalc_request['user']['backend_variables']['requirements']
        == expected_reqs
    )
