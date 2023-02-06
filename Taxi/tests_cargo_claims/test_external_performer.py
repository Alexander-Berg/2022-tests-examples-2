# pylint: disable=redefined-outer-name

import pytest
import uuid

from testsuite.utils import matching


@pytest.fixture(name='mock_eats_couriers_binding')
def _mock_eats_couriers_binding(mockserver):
    def _wrapper(**response_kwargs):
        @mockserver.json_handler(
            '/driver-profiles/v1/eats-couriers-binding/'
            'retrieve_by_park_driver_profile_id',
        )
        def _mock_driver_profile(request):
            assert request.json['id_in_set'] == ['park_id1_driver_id1']
            return mockserver.make_response(**response_kwargs)

        return _mock_driver_profile

    return _wrapper


@pytest.fixture
async def driver_profiles_retrieve(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profile_retrieve_post(request):
        assert len(request.json['id_in_set']) == 1
        assert request.json['projection'] == ['data.full_name.first_name']

        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'known_id',
                    'data': {'full_name': {'first_name': 'some first name'}},
                },
            ],
        }


async def test_external_performer_found(
        mockserver,
        create_claim_with_performer,
        taxi_cargo_claims,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        driver_profiles_retrieve,
):
    mock_eats_couriers_binding(
        json={'binding': [{'eats_id': '123', 'taxi_id': '456'}]}, status=200,
    )
    mock_waybill_path_info({})

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': create_claim_with_performer.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'eats_profile_id': '123',
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'zone_id': 'moscow',
    }


async def test_external_external_performer_not_found(
        mockserver,
        create_claim_with_performer,
        taxi_cargo_claims,
        mock_eats_couriers_binding,
        driver_profiles_retrieve,
        mock_waybill_path_info,
):
    mock_waybill_path_info({})
    mock_eats_couriers_binding(
        json={'binding': [{'taxi_id': '456'}]}, status=200,
    )

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': create_claim_with_performer.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'zone_id': 'moscow',
    }


async def test_external_no_driver_profile(
        mockserver,
        create_claim_with_performer,
        taxi_cargo_claims,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        driver_profiles_retrieve,
):
    mock_waybill_path_info({})
    mock_eats_couriers_binding(json={'binding': []}, status=200)

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': create_claim_with_performer.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'zone_id': 'moscow',
    }


@pytest.fixture(name='mock_waybill_path_info', autouse=True)
def _mock_waybill_path_info(mockserver):
    def _wrapper(response: dict):
        @mockserver.json_handler('/cargo-dispatch/v1/waybill/path/info')
        def mock(request):
            return response

        return mock

    return _wrapper


async def test_dragon_without_batch(
        mockserver,
        taxi_cargo_claims,
        create_segment_with_performer,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        driver_profiles_retrieve,
):
    result = await create_segment_with_performer()

    mock_eats_couriers_binding(
        json={'binding': [{'eats_id': '123', 'taxi_id': '456'}]}, status=200,
    )

    waybill_mock = mock_waybill_path_info(
        response={
            'waybill_ref': 'waybill_1',
            'segments': [
                {'segment_id': 'some_segment_id', 'claim_id': 'some_claim_id'},
            ],
            'path': [
                {
                    'segment_id': 'some_segment_id',
                    'waybill_point_id': 'point_id',
                    'visit_order': 1,
                },
            ],
        },
    )

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': result.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'eats_profile_id': '123',
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'zone_id': 'moscow',
    }

    request_query = waybill_mock.next_call()['request'].query
    assert request_query['cargo_order_id'] == matching.any_string
    assert len(request_query) == 1


@pytest.fixture(name='build_waybill_path')
async def _build_waybill_path(get_db_segment_ids, fetch_segment_points):
    async def _wrapper(first_seg: str, second_seg: str, third_seg: str = None):
        """
        Build stardart points path:
        A1 -> A2 -> B1 -> B2 -> A1 -> A2
        """
        # Format like respone in waybill.path
        path: list = list()

        first_seg_points = await fetch_segment_points(first_seg)
        second_seg_points = await fetch_segment_points(second_seg)
        third_seg_points = (
            await fetch_segment_points(third_seg) if third_seg else []
        )

        i = j = k = 0
        while len(path) < len(first_seg_points) + len(second_seg_points) + len(
                third_seg_points,
        ):
            if i < len(first_seg_points):
                path.append(
                    {
                        'segment_id': first_seg,
                        'waybill_point_id': first_seg_points[i]['point_id'],
                        'visit_order': len(path) + 1,
                    },
                )
                i += 1
            if j < len(second_seg_points):
                path.append(
                    {
                        'segment_id': second_seg,
                        'waybill_point_id': second_seg_points[j]['point_id'],
                        'visit_order': len(path) + 1,
                    },
                )
                j += 1
            if k < len(third_seg_points):
                path.append(
                    {
                        'segment_id': third_seg,
                        'waybill_point_id': third_seg_points[k]['point_id'],
                        'visit_order': len(path) + 1,
                    },
                )
                k += 1

        return path

    return _wrapper


async def test_dragon_batch(
        mockserver,
        taxi_cargo_claims,
        create_segment_with_performer,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        get_db_segment_ids,
        build_waybill_path,
        driver_profiles_retrieve,
):
    claim_1 = await create_segment_with_performer(claim_index=0)
    claim_2 = await create_segment_with_performer(claim_index=1)
    claim_3 = await create_segment_with_performer(claim_index=2)
    seg1, seg2, seg3 = await get_db_segment_ids()

    waybill_path = await build_waybill_path(seg1, seg2, seg3)

    mock_eats_couriers_binding(
        json={'binding': [{'eats_id': '123', 'taxi_id': '456'}]}, status=200,
    )

    waybill_mock = mock_waybill_path_info(
        response={
            'waybill_ref': 'waybill_1',
            'segments': [
                {'segment_id': seg1, 'claim_id': claim_1.claim_id},
                {'segment_id': seg2, 'claim_id': claim_2.claim_id},
                {'segment_id': seg3, 'claim_id': claim_3.claim_id},
            ],
            'path': waybill_path,
        },
    )

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': claim_1.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'eats_profile_id': '123',
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'batch_info': {
            'delivery_order': [
                {'claim_id': claim_1.claim_id, 'order': 1},
                {'claim_id': claim_2.claim_id, 'order': 2},
                {'claim_id': claim_3.claim_id, 'order': 3},
            ],
        },
        'zone_id': 'moscow',
    }

    request_query = waybill_mock.next_call()['request'].query
    assert request_query['cargo_order_id'] == matching.any_string
    assert len(request_query) == 1


async def test_waybill_empty_path(
        mockserver,
        taxi_cargo_claims,
        create_segment_with_performer,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        get_db_segment_ids,
        driver_profiles_retrieve,
):
    claim_1 = await create_segment_with_performer(claim_index=0)
    claim_2 = await create_segment_with_performer(claim_index=1)
    seg1, seg2 = await get_db_segment_ids()

    mock_eats_couriers_binding(
        json={'binding': [{'eats_id': '123', 'taxi_id': '456'}]}, status=200,
    )
    mock_waybill_path_info(
        response={
            'waybill_ref': 'waybill_1',
            'segments': [
                {'segment_id': seg1, 'claim_id': claim_1.claim_id},
                {'segment_id': seg2, 'claim_id': claim_2.claim_id},
            ],
            'path': [],
        },
    )

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': claim_1.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'eats_profile_id': '123',
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'zone_id': 'moscow',
    }


async def test_many_orders(
        mockserver,
        taxi_cargo_claims,
        create_segment_with_performer,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        get_db_segment_ids,
        build_waybill_path,
        driver_profiles_retrieve,
):
    claim_1 = await create_segment_with_performer(claim_index=0)
    claim_2 = await create_segment_with_performer(claim_index=1)
    claim_3 = await create_segment_with_performer(claim_index=2)
    seg1, seg2, seg3 = await get_db_segment_ids()

    waybill_path = await build_waybill_path(seg1, seg2, seg3)

    mock_eats_couriers_binding(
        json={'binding': [{'eats_id': '123', 'taxi_id': '456'}]}, status=200,
    )

    waybill_mock = mock_waybill_path_info(
        response={
            'waybill_ref': 'waybill_1',
            'segments': [
                {'segment_id': seg1, 'claim_id': claim_1.claim_id},
                {'segment_id': seg2, 'claim_id': claim_2.claim_id},
                {'segment_id': seg3, 'claim_id': claim_3.claim_id},
            ],
            'path': waybill_path,
        },
    )

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': claim_1.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'eats_profile_id': '123',
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'batch_info': {
            'delivery_order': [
                {'claim_id': claim_1.claim_id, 'order': 1},
                {'claim_id': claim_2.claim_id, 'order': 2},
                {'claim_id': claim_3.claim_id, 'order': 3},
            ],
        },
        'zone_id': 'moscow',
    }

    request_query = waybill_mock.next_call()['request'].query
    assert request_query['cargo_order_id'] == matching.any_string
    assert len(request_query) == 1


async def test_pull_dispatch_batch(
        mockserver,
        taxi_cargo_claims,
        create_segment_with_performer,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        get_db_segment_ids,
        build_waybill_path,
        driver_profiles_retrieve,
):
    # Pull-dispatch order: A -> B1 -> B2

    claim_1 = await create_segment_with_performer(
        claim_index=0, use_create_v2=True, multipoints=True,
    )
    claim_2 = await create_segment_with_performer(claim_index=1)
    seg1, seg2 = await get_db_segment_ids()
    waybill_path = await build_waybill_path(seg1, seg2)

    mock_eats_couriers_binding(
        json={'binding': [{'eats_id': '123', 'taxi_id': '456'}]}, status=200,
    )
    mock_waybill_path_info(
        response={
            'waybill_ref': 'waybill_1',
            'segments': [
                {'segment_id': seg1, 'claim_id': claim_1.claim_id},
                {'segment_id': seg2, 'claim_id': claim_2.claim_id},
            ],
            'path': waybill_path,
        },
    )

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': claim_1.claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
        'eats_profile_id': '123',
        'name': 'Kostya',
        'first_name': 'some first name',
        'legal_name': 'park_name_1',
        'driver_id': 'driver_id1',
        'park_id': 'park_id1',
        'taxi_alias_id': 'order_alias_id_1',
        'batch_info': {
            'delivery_order': [
                {'claim_id': claim_1.claim_id, 'order': 1},
                {'claim_id': claim_2.claim_id, 'order': 2},
            ],
        },
        'zone_id': 'moscow',
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_enable_performers_fetch_from_cargo_orders',
    consumers=['cargo-claims/external-performer'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
async def test_external_performer_eta(
        mockserver,
        build_segment_update_request,
        create_claim_with_performer,
        taxi_cargo_claims,
        mock_eats_couriers_binding,
        mock_waybill_path_info,
        driver_profiles_retrieve,
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info-cached')
    def _mock_performers(request):
        return {
            'performers': [
                {
                    'revision': 1,
                    'order_id': uuid.uuid4().hex,
                    'order_alias_id': 'order_alias_id_1',
                    'phone_pd_id': '+70000000000_pd',
                    'name': 'Kostya',
                    'driver_id': 'driver_id1',
                    'park_id': 'park_id1',
                    'park_clid': 'park_clid1',
                    'car_id': 'car_id_1',
                    'car_number': 'car_number_1',
                    'car_model': 'car_model_1',
                    'lookup_version': 1,
                    'dist_from_point_a': 987,
                    'eta_to_point_a': '2020-06-17T19:40:00+00:00',
                },
            ],
        }

    mock_eats_couriers_binding(
        json={'binding': [{'eats_id': '123', 'taxi_id': '456'}]}, status=200,
    )
    waybill_mock = mock_waybill_path_info(
        response={
            'waybill_ref': 'waybill_1',
            'segments': [
                {'segment_id': 'some_segment_id', 'claim_id': 'some_claim_id'},
            ],
            'path': [
                {
                    'segment_id': 'some_segment_id',
                    'waybill_point_id': 'point_id',
                    'visit_order': 1,
                },
            ],
        },
    )

    response = await taxi_cargo_claims.get(
        '/internal/external-performer',
        params={'sharing_key': create_claim_with_performer.claim_id},
    )
    assert response.status_code == 200
    assert response.json()['eta_to_point_a'] == '2020-06-17T19:40:00+00:00'
