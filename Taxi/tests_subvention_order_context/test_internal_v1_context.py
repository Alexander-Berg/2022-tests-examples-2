import copy
import json

import pytest

from . import test_common


RESPONSE_PARAMS = {
    'order_id': 'order_id',
    'driver_profile_id': 'uuid',
    'park_id': 'dbid',
}


async def test_fetch_from_storage(taxi_subvention_order_context, mongodb):
    mongodb.subvention_order_context.insert_one(
        copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA),
    )

    response = await taxi_subvention_order_context.get(
        '/internal/subvention-order-context/v1/context',
        params=RESPONSE_PARAMS,
    )

    assert response.status_code == 200

    assert response.json() == {
        'activity_points': 91,
        'subvention_geoareas': ['geoarea1'],
        'branding': {'has_lightbox': False, 'has_sticker': False},
        'ref_time': '2020-01-01T12:00:00+00:00',
        'tags': ['tag1', 'tag2'],
        'tariff_class': 'econom',
        'tariff_zone': 'moscow',
        'geonodes': 'br_root/br_russia/br_moscow/moscow',
        'time_zone': 'Europe/Moscow',
        'unique_driver_id': 'unique_driver_id',
    }


@pytest.mark.parametrize(
    'params, result, expected_response',
    [
        (
            {
                'order_id': 'orderid',
                'driver_profile_id': 'uuid',
                'park_id': 'dbid',
            },
            200,
            {
                'activity_points': 100,
                'subvention_geoareas': ['geoarea1', 'geoarea2'],
                'branding': {'has_lightbox': True, 'has_sticker': True},
                'ref_time': '2020-01-01T12:00:00+00:00',
                'tags': ['tag1', 'tag2'],
                'tariff_class': 'econom',
                'tariff_zone': 'moscow',
                'geonodes': 'br_root/br_russia/br_moscow/moscow',
                'time_zone': 'Europe/Moscow',
                'unique_driver_id': 'unique_driver_id',
            },
        ),
        (
            {
                'order_id': 'orderid2',
                'driver_profile_id': 'uuid',
                'park_id': 'dbid',
            },
            500,
            None,
        ),
    ],
)
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt_data.yaml'])
async def test_fetch_from_yt(
        yt_apply,
        taxi_subvention_order_context,
        mongodb,
        params,
        result,
        expected_response,
):
    response = await taxi_subvention_order_context.get(
        '/internal/subvention-order-context/v1/context', params=params,
    )

    assert response.status_code == result

    if result == 200:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'order_proc_response',
    [
        'order_proc.json',
        'order_proc_check_parsing_bug.json',
        'order_proc_bad_1.json',
        'order_proc_bad_2.json',
    ],
)
async def test_build_context_on_fly(
        taxi_subvention_order_context,
        mock_order_core,
        mongodb,
        load_json,
        order_proc_response,
):
    context_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    del context_data['value']['activity_points']
    mongodb.subvention_order_context.insert_one(context_data)

    mock_order_core.set_response(load_json(order_proc_response))

    response = await taxi_subvention_order_context.get(
        '/internal/subvention-order-context/v1/context',
        params=RESPONSE_PARAMS,
    )

    assert response.status_code == 200

    assert response.json() == {
        'activity_points': 91,
        'subvention_geoareas': ['geoarea1'],
        'branding': {'has_lightbox': False, 'has_sticker': False},
        'ref_time': '2020-01-01T12:00:00+00:00',
        'tags': ['tag1', 'tag2'],
        'tariff_class': 'econom',
        'tariff_zone': 'moscow',
        'geonodes': 'br_root/br_russia/br_moscow/moscow',
        'time_zone': 'Europe/Moscow',
        'unique_driver_id': 'unique_driver_id',
    }


async def test_404(taxi_subvention_order_context, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_get_fields(request):
        return mockserver.make_response(
            status=404,
            response=json.dumps(
                {'code': 'no_such_order', 'message': 'no such order'},
            ),
        )

    response = await taxi_subvention_order_context.get(
        '/internal/subvention-order-context/v1/context',
        params=RESPONSE_PARAMS,
    )

    assert response.status_code == 404


async def test_500(
        taxi_subvention_order_context,
        mockserver,
        mock_order_core,
        mongodb,
        load_json,
):
    context_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    del context_data['value']['unique_driver_id']
    mongodb.subvention_order_context.insert_one(context_data)

    mock_order_core.set_response(load_json('order_proc.json'))

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_retrieve_by_profiles(request):
        return mockserver.make_response(status=500, response='{}')

    response = await taxi_subvention_order_context.get(
        '/internal/subvention-order-context/v1/context',
        params=RESPONSE_PARAMS,
    )

    assert response.status_code == 500


@pytest.mark.config(SUBVENTION_ORDER_CONTEXT_APPEND_VIRTUAL_TAGS=True)
async def test_append_virtual_tags(
        taxi_subvention_order_context,
        mockserver,
        mock_order_core,
        mongodb,
        load_json,
):
    context_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    mongodb.subvention_order_context.insert_one(context_data)

    response = await taxi_subvention_order_context.get(
        '/internal/subvention-order-context/v1/context',
        params=RESPONSE_PARAMS,
    )

    assert response.status_code == 200

    assert response.json() == {
        'activity_points': 91,
        'branding': {'has_lightbox': False, 'has_sticker': False},
        'geonodes': 'br_root/br_russia/br_moscow/moscow',
        'ref_time': '2020-01-01T12:00:00+00:00',
        'subvention_geoareas': ['geoarea1'],
        'tags': ['tag1', 'tag2', 'virtual_tag1'],
        'tariff_class': 'econom',
        'tariff_zone': 'moscow',
        'time_zone': 'Europe/Moscow',
        'unique_driver_id': 'unique_driver_id',
    }
