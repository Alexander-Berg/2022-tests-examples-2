import pytest

from .. import utils_v2

PLATFORM_USAGE = 'platform_usage'


@pytest.fixture(name='set_up_claim_kind_exp')
def _set_up_claim_kind_exp(experiments3):
    def _wrapper(
            *,
            enabled: bool = True,
            corp_client_id: str = 'unknown',
            zone_id: str = 'unknown',
            recipient_phone: str = 'unknown',
            claim_kind: str = None,
            tariff_classes: list = None,
    ):
        if claim_kind:
            predicates_by_corp = [
                {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'set': [corp_client_id],
                                    'arg_name': 'corp_client_id',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'set': [claim_kind],
                                    'arg_name': 'claim_kind',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            ]
        else:
            predicates_by_corp = [
                {
                    'init': {
                        'set': [corp_client_id],
                        'arg_name': 'corp_client_id',
                        'set_elem_type': 'string',
                    },
                    'type': 'in_set',
                },
            ]

        predicates_by_zone = [
            {
                'init': {
                    'set': [zone_id],
                    'arg_name': 'zone_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        ]
        predicates_by_phone = [
            {
                'init': {
                    'value': recipient_phone,
                    'arg_name': 'recipients_phones',
                    'set_elem_type': 'string',
                },
                'type': 'contains',
            },
        ]

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claim_set_client_tariffs_by_claim_kind',
            consumers=['cargo-claims/create-claim-client-tariffs'],
            clauses=[
                {
                    'title': 'by corp_client_id',
                    'predicate': {
                        'init': {'predicates': predicates_by_corp},
                        'type': 'all_of',
                    },
                    'value': {
                        'enabled': enabled,
                        'tariff_classes': tariff_classes,
                    },
                },
                {
                    'title': 'by zone_id',
                    'predicate': {
                        'init': {'predicates': predicates_by_zone},
                        'type': 'all_of',
                    },
                    'value': {
                        'enabled': enabled,
                        'tariff_classes': tariff_classes,
                    },
                },
                {
                    'title': 'by recipient_phone',
                    'predicate': {
                        'init': {'predicates': predicates_by_phone},
                        'type': 'all_of',
                    },
                    'value': {
                        'enabled': enabled,
                        'tariff_classes': tariff_classes,
                    },
                },
            ],
            default_value={'enabled': not enabled},
        )

    return _wrapper


async def test_no_modified_classes_without_kind(
        get_state_finished_claim, get_segment_info_from_handler,
):
    state = await get_state_finished_claim(None)
    segment_info = await get_segment_info_from_handler(state.segment_id)
    assert 'modified_classes' not in segment_info


@pytest.mark.config(
    BILLING_TARIFFS_WITH_NO_CHARGE=['eda', 'lavka'],
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'eats',
    },
)
@pytest.mark.parametrize(
    'taxi_class,expected_modified_classes',
    [
        ('courier', ['courier', 'express']),
        ('eda', ['eda', 'lavka']),
        ('lavka', ['eda', 'lavka']),
    ],
)
async def test_modified_classes_with_specified_kind(
        get_state_finished_claim,
        get_segment_info_from_handler,
        taxi_class,
        expected_modified_classes,
):
    state = await get_state_finished_claim(
        taxi_class, claim_kind=PLATFORM_USAGE,
    )
    segment_info = await get_segment_info_from_handler(state.segment_id)
    taxi_classes = segment_info['performer_requirements']['taxi_classes']
    assert taxi_classes == ['courier', 'express', 'eda', 'lavka']
    assert segment_info['modified_classes'] == expected_modified_classes


async def test_nothing_to_pay_when_kind_platform_usage(
        get_state_finished_claim,
):
    state = await get_state_finished_claim('eda')
    assert state.claim['pricing']['final_price'] == '0.0000'


async def test_pay_when_kind_platform_usage(get_state_finished_claim):
    state = await get_state_finished_claim('courier')
    epsilon = 0.0001
    assert float(state.claim['pricing']['final_price']) - epsilon > 0


@pytest.fixture(name='get_state_finished_claim')
def _get_state_finished_claim(
        create_claim_segment_matched_car_taxi_class,
        build_segment_update_request,
        get_default_corp_client_id,
        taxi_cargo_claims,
        state_controller,
        stq_runner,
):
    async def wrapper(taxi_class, *, claim_kind=None):
        taxi_order_id = 'taxi_order_id_1'

        claim_info, segment_id = (
            await create_claim_segment_matched_car_taxi_class(
                get_default_corp_client_id,
                taxi_class='courier',
                claim_kind=claim_kind,
            )
        )

        update_segment_body = build_segment_update_request(
            segment_id,
            taxi_order_id,
            with_performer=True,
            revision=2,
            taxi_class=taxi_class,
        )
        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={'segments': [update_segment_body]},
        )
        assert response.status_code == 200

        claim_info = await state_controller.apply(
            target_status='delivered_finish', fresh_claim=False,
        )

        # Update claim via stq
        await stq_runner.cargo_claims_change_claim_order_price.call(
            task_id=claim_info.claim_id,
            args=[claim_info.claim_id, '123.0', 'some reason'],
            expect_fail=False,
        )

        claim = await utils_v2.get_claim(
            claim_info.claim_id, taxi_cargo_claims,
        )

        class State:
            def __init__(self):
                self.segment_id = segment_id
                self.claim_info = claim_info
                self.claim = claim

        return State()

    return wrapper


@pytest.fixture(name='get_segment_info_from_handler')
def _get_segment_info_from_handler(taxi_cargo_claims):
    async def wrapper(segment_id):
        response = await taxi_cargo_claims.post(
            '/v1/segments/info', params={'segment_id': segment_id},
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'eats',
    },
)
@pytest.mark.parametrize(
    'claim_kind, performer_classes',
    [
        ('platform_usage', ['courier', 'express', 'eda', 'lavka']),
        ('delivery_service', ['courier', 'express']),
    ],
)
async def test_create_with_claim_kind(
        create_segment,
        get_segment_id,
        get_segment_info_from_handler,
        claim_kind,
        performer_classes,
        fetch_claim_kind,
):
    claim_info = await create_segment(claim_kind=claim_kind)

    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)
    assert (
        segment_info['performer_requirements']['taxi_classes']
        == performer_classes
    )
    assert 'modified_classes' not in segment_info

    claim_kind = await fetch_claim_kind(claim_info.claim_id)
    assert not claim_kind


async def test_create_claim_kind_without_client_req(
        create_segment,
        get_segment_id,
        get_segment_info_from_handler,
        fetch_claim_kind,
):
    """
    Set client_requirements.taxi_classes field even if
    client didn't send field 'client_requirements' but send
    claim_kind field
    """
    claim_info = await create_segment(
        claim_kind='delivery_service', skip_client_requirements=True,
    )

    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)
    assert segment_info['performer_requirements']['taxi_classes'] == [
        'courier',
        'express',
    ]
    assert 'modified_classes' not in segment_info

    claim_kind = await fetch_claim_kind(claim_info.claim_id)
    assert not claim_kind


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'eats',
    },
)
async def test_update_claim_kind(
        taxi_cargo_claims,
        create_segment,
        get_default_corp_client_id,
        build_segment_update_request,
        get_segment_id,
        get_segment_info_from_handler,
        testpoint,
):
    """
    Eda creates claim with claim_kind = 'platform_usage'.
    Do not save this claim_kind,
    just calculate client_requirements.taxi_classes and save it
    When taxi performer found, claim kind must be set to 'delivery_service'
    """

    @testpoint('update-segment-dispatch-state')
    def testpoint_finish(data):
        pass

    # Create claim with claim_kind = 'platform_usage'
    await create_segment(claim_kind='platform_usage')
    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)
    assert segment_info['performer_requirements']['taxi_classes'] == [
        'courier',
        'express',
        'eda',
        'lavka',
    ]

    # Taxi driver was assigned to order
    update_segment_body = build_segment_update_request(
        segment_id,
        'taxi_order_id_1',
        with_performer=True,
        revision=2,
        taxi_class='cargo',
    )
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={'segments': [update_segment_body]},
    )
    assert response.status_code == 200

    # Check that there are new 'modified_classes'
    segment_info = await get_segment_info_from_handler(segment_id)
    assert segment_info['modified_classes'] == ['courier', 'express']
    assert segment_info['performer_requirements']['taxi_classes'] == [
        'courier',
        'express',
        'eda',
        'lavka',
    ]

    assert testpoint_finish.next_call()['data'] == {
        'updated_segments_count': 1,
        'segments_with_upserted_performer': 1,
        'segments_with_changed_claim_kind_after_perf_found': 0,
    }


@pytest.mark.parametrize(
    'experiment_is_set, claim_kind_enabled',
    [(False, True), (True, False), (True, True)],
)
@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'eats',
    },
)
async def test_claim_kind_exp(
        taxi_cargo_claims,
        create_segment,
        get_default_corp_client_id,
        build_segment_update_request,
        get_segment_id,
        get_segment_info_from_handler,
        testpoint,
        set_up_claim_kind_exp,
        experiment_is_set: bool,
        claim_kind_enabled: bool,
):
    """
    Check for claim_kind for specific corp_client_id/zone_id
    """

    if experiment_is_set:
        set_up_claim_kind_exp(
            enabled=claim_kind_enabled,
            corp_client_id=get_default_corp_client_id,
        )

    @testpoint('update-segment-dispatch-state')
    def testpoint_finish(data):
        pass

    # Create claim with claim_kind = 'platform_usage'
    await create_segment(claim_kind='platform_usage')
    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)

    if claim_kind_enabled:
        expected_classes = ['courier', 'express', 'eda', 'lavka']
    else:
        expected_classes = ['cargo']

    assert (
        segment_info['performer_requirements']['taxi_classes']
        == expected_classes
    )

    # Taxi driver was assigned to order
    update_segment_body = build_segment_update_request(
        segment_id,
        'taxi_order_id_1',
        with_performer=True,
        revision=2,
        taxi_class='cargo',
    )
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={'segments': [update_segment_body]},
    )
    assert response.status_code == 200

    # Check that there are new 'modified_classes'
    segment_info = await get_segment_info_from_handler(segment_id)
    if claim_kind_enabled:
        assert segment_info['modified_classes'] == ['courier', 'express']
    else:
        assert segment_info['modified_classes'] == expected_classes
    assert (
        segment_info['performer_requirements']['taxi_classes']
        == expected_classes
    )

    assert testpoint_finish.next_call()['data'] == {
        'updated_segments_count': 1,
        'segments_with_upserted_performer': 1,
        'segments_with_changed_claim_kind_after_perf_found': 0,
    }


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'eats',
    },
)
async def test_wrong_update_claim_kind(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_corp_client_id,
        build_segment_update_request,
        get_segment_id,
        get_segment_info_from_handler,
        testpoint,
):
    """
    ERROR.
    Update claim_kind for segment with performer already found
    """

    @testpoint('update-segment-dispatch-state')
    def testpoint_finish(data):
        pass

    # Create claim with claim_kind = 'platform_usage'
    await create_segment_with_performer(
        claim_kind='platform_usage', taxi_class='eda',
    )
    segment_id = await get_segment_id()
    assert testpoint_finish.next_call()['data'] == {
        'updated_segments_count': 1,
        'segments_with_upserted_performer': 1,
        'segments_with_changed_claim_kind_after_perf_found': 0,
    }

    # New taxi driver was assigned to order
    update_segment_body = build_segment_update_request(
        segment_id,
        'taxi_order_id_1',
        with_performer=True,
        revision=2,
        taxi_class='cargo',
    )
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={'segments': [update_segment_body]},
    )
    assert response.status_code == 200

    # Check that we wrote ERROR log
    assert testpoint_finish.next_call()['data'] == {
        'updated_segments_count': 1,
        'segments_with_upserted_performer': 1,
        'segments_with_changed_claim_kind_after_perf_found': 1,
    }


async def test_do_not_set_claim_kind_if_oldway_claim(
        taxi_cargo_claims,
        claim_creator,
        get_default_request,
        get_default_headers,
        fetch_claim_kind,
):
    request_data = get_default_request()
    request_data['claim_kind'] = 'platform_usage'
    response = await claim_creator(request=request_data)
    claim_id = response.json()['id']

    claim_kind = await fetch_claim_kind(claim_id)
    assert not claim_kind


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'eats',
    },
    CARGO_ORDERS_TAXI_REQUIREMENTS_VALIDATION={
        'allowed_classes': ['eda'],
        'allowed_requirements': [],
    },
)
async def test_client_req_taxi_classes(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_segment_info_from_handler,
):
    """
    Send client_requirements.taxi_classes field
    Use only this classes in segment.performer_requirements.taxi_classes
    """
    await create_segment(client_req_taxi_classes=['eda'])
    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)
    assert segment_info['performer_requirements']['taxi_classes'] == ['eda']


async def test_wrong_client_req_taxi_classes(
        taxi_cargo_claims,
        claim_creator,
        get_default_request,
        get_default_headers,
        fetch_claim_kind,
):
    request_data = get_default_request()
    request_data['client_requirements']['taxi_classes'] = ['unknown']
    response = await claim_creator(request=request_data)
    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': 'Wrong taxi_class unknown',
    }


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'eats',
    },
)
@pytest.mark.parametrize('exp_with_destination_phone', [True, False])
async def test_claim_kind_phone(
        taxi_cargo_claims,
        create_segment,
        get_default_corp_client_id,
        build_segment_update_request,
        get_segment_id,
        get_segment_info_from_handler,
        set_up_claim_kind_exp,
        exp_with_destination_phone: bool,
):
    """
    Check for claim_kind exp supporting recipient phones.

    """

    if exp_with_destination_phone:
        set_up_claim_kind_exp(recipient_phone='+72222222222')
    else:
        set_up_claim_kind_exp()

    # Create claim with claim_kind = 'platform_usage'
    await create_segment(claim_kind='platform_usage')
    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)

    if exp_with_destination_phone:
        expected_classes = ['courier', 'express', 'eda', 'lavka']
    else:
        expected_classes = ['cargo']

    assert (
        segment_info['performer_requirements']['taxi_classes']
        == expected_classes
    )


async def test_experiment_enabled_for_other_claim_kind(
        create_segment,
        get_segment_id,
        get_segment_info_from_handler,
        fetch_claim_kind,
        set_up_claim_kind_exp,
        get_default_corp_client_id,
):
    set_up_claim_kind_exp(
        corp_client_id=get_default_corp_client_id,
        claim_kind='platform_usage',
        tariff_classes=['courier'],
    )

    await create_segment(
        claim_kind='delivery_service', skip_client_requirements=True,
    )

    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)
    assert segment_info['performer_requirements']['taxi_classes'] == ['cargo']


async def test_use_experiment_tariff_classes(
        create_segment,
        get_segment_id,
        get_segment_info_from_handler,
        fetch_claim_kind,
        set_up_claim_kind_exp,
        get_default_corp_client_id,
):
    set_up_claim_kind_exp(
        corp_client_id=get_default_corp_client_id,
        tariff_classes=['eda'],
        claim_kind='platform_usage',
    )

    await create_segment(
        claim_kind='platform_usage', skip_client_requirements=True,
    )

    segment_id = await get_segment_id()
    segment_info = await get_segment_info_from_handler(segment_id)
    assert segment_info['performer_requirements']['taxi_classes'] == ['eda']
