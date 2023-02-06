import pytest


@pytest.fixture(name='call_calc')
def _call_calc(v1_calc_creator):
    async def calc(requirements):
        v1_calc_creator.payload['taxi_requirements'] = requirements
        response = await v1_calc_creator.execute()
        return response

    return calc


@pytest.fixture(name='v2_prepare_request_requirements')
def _v2_prepare_request_requirements(v1_calc_creator):
    def extractor():
        prepare_req = v1_calc_creator.mock_prepare.request
        return prepare_req['classes_requirements']['cargocorp']

    return extractor


@pytest.fixture(name='conf_exp3_requirements_processing')
def _conf_exp3_requirements_processing(experiments3, taxi_cargo_pricing):
    async def configurate(action):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_pricing_taxi_requirements_processing',
            consumers=['cargo-pricing/v1/taxi/calc-requrements-processing'],
            clauses=[],
            default_value={'action': action},
        )
        await taxi_cargo_pricing.invalidate_caches()

    return configurate


async def test_taxi_requirements_process_no_experiment(
        call_calc, v1_calc_creator, v2_prepare_request_requirements,
):
    requirements = {'some_requirement': 12}
    response = await call_calc(requirements)
    assert response.status_code == 200

    assert v2_prepare_request_requirements() == requirements


async def test_taxi_requirements_process_kwargs(
        call_calc, conf_exp3_requirements_processing, experiments3,
):
    await conf_exp3_requirements_processing(action='leave_as_is')
    requirements = {'some_requirement1': 12, 'some_requirement2': True}
    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_taxi_requirements_processing',
    )

    response = await call_calc(requirements)
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    assert tries[0].kwargs['is_decoupling']
    assert tries[0].kwargs['price_for'] == 'client'
    assert tries[0].kwargs['requirement'] == 'some_requirement1'
    assert tries[1].kwargs['is_decoupling']
    assert tries[1].kwargs['price_for'] == 'client'
    assert tries[1].kwargs['requirement'] == 'some_requirement2'


async def test_taxi_requirements_process_leave_as_is(
        call_calc,
        v2_prepare_request_requirements,
        conf_exp3_requirements_processing,
):
    await conf_exp3_requirements_processing(action='leave_as_is')
    requirements = {'some_requirement1': 12, 'some_requirement2': True}

    response = await call_calc(requirements)
    assert response.status_code == 200

    assert v2_prepare_request_requirements() == requirements


async def test_taxi_requirements_process_bool_to_int_cast(
        call_calc,
        v2_prepare_request_requirements,
        conf_exp3_requirements_processing,
):
    await conf_exp3_requirements_processing(action='bool_to_int_cast')
    requirements = {'will_be_removed': False, 'will_be_one': True}

    response = await call_calc(requirements)
    assert response.status_code == 200

    assert v2_prepare_request_requirements() == {'will_be_one': 1}


async def test_taxi_requirements_process_remove(
        call_calc,
        v2_prepare_request_requirements,
        conf_exp3_requirements_processing,
):
    await conf_exp3_requirements_processing(action='remove')
    requirements = {
        'some_requirement1': 12,
        'some_requirement2': {'bool': True},
        'some_requirement3': 'value',
    }

    response = await call_calc(requirements)
    assert response.status_code == 200

    assert v2_prepare_request_requirements() == {}
