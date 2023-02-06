import pytest


def get_receipt_used_time(pgsql, order_id):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            f'SELECT used FROM receipts.custom_receipts WHERE order_id=%s',
            (order_id,),
        )
        result = cursor.fetchall()
        if not result:
            return None
        return result[0][0]


@pytest.mark.parametrize(
    'order_id, expected_code, expected_response',
    [
        ('00000000000000000000000000000000', 404, 'expected_response_0.json'),
        ('00000000000000000000000000000001', 422, 'expected_response_1.json'),
        ('00000000000000000000000000000003', 200, 'expected_response_3.json'),
        ('00000000000000000000000000000004', 404, 'expected_response_4.json'),
        ('00000000000000000000000000000005', 200, 'expected_response_5.json'),
        ('00000000000000000000000000000006', 422, 'expected_response_6.json'),
        ('20000000000000000000000000000000', 200, 'expected_response_7.json'),
        ('00000000000000000000000000000008', 200, 'expected_response_8.json'),
    ],
    ids=[
        'unexistent_order',  # 0
        'not_finished_order',  # 1
        'no_fixed_price_extra_discount',  # 3
        'order_not_in_yt',  # 4
        'has_modification_discount',  # 5
        'canceled_order',  # 6
        'custom_receipt',  # 7
        'fixed_price_uuid_flow',  # 8
    ],
)
@pytest.mark.yt(
    schemas=[
        'yt_v2_prepare_common_schema.yaml',
        'yt_v2_calc_paid_supply_category_schema.yaml',
        'yt_v2_prepare_route_schema.yaml',
        'yt_v2_prepare_category_info_schema.yaml',
        'yt_order_verification_result_schema.yaml',
        'yt_taximeter_order_details_schema.yaml',
    ],
    dyn_table_data=[
        'yt_v2_prepare_common.yaml',
        'yt_v2_calc_paid_supply_category.yaml',
        'yt_v2_prepare_route.yaml',
        'yt_v2_prepare_category_info.yaml',
        'yt_order_verification_result.yaml',
        'yt_taximeter_order_details.yaml',
    ],
)
@pytest.mark.config(
    PRICING_DATA_PREPARER_BLOCK_V2_OFFER_YTDATA=False,
    PRICING_ADMIN_RECEIPT_MODIFICATION_GROUPS={
        'md': {'coupon': ['coupon'], 'discount': ['disconuts']},
    },
    CURRENCY_FORMATTING_RULES={'MDL': {'__default__': 1, 'iso4217': 2}},
)
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'receipts.sql'],
)
@pytest.mark.now('2020-04-22 12:00:00.0000+03')
async def test_v1_receipt_md(
        taxi_pricing_admin,
        order_id,
        expected_code,
        expected_response,
        load_json,
        order_archive_mock,
        yt_apply,
        pgsql,
        mocked_time,
):
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    expected_json = load_json(expected_response)
    # main request starting reading YT
    response = await taxi_pricing_admin.get(
        'v1/receipt/md', params={'order_id': order_id},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_json

    if order_id == '22222222222222222222222222222222':
        used = get_receipt_used_time(pgsql, order_id)
        assert used is not None
        assert used.replace(tzinfo=None) == mocked_time.now()


def get_receipt_counter(pgsql, order_id):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            f'SELECT counter '
            f'FROM receipts.receipts_counters WHERE order_id=%s',
            (order_id,),
        )
        result = cursor.fetchall()
        if not result:
            return None
        return result[0][0]


@pytest.mark.config(PRICING_ADMIN_RECEIPTS_ATTEMPTS_LIMIT=3)
async def test_v1_receipt_md_counter(
        taxi_pricing_admin, pgsql, order_archive_mock, load_json,
):
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    order_id = '00000000000000000000000000000000'
    for i in range(1, 7):
        await taxi_pricing_admin.get(
            'v1/receipt/md', params={'order_id': order_id},
        )
        counter = get_receipt_counter(pgsql, order_id)
        assert counter == i


@pytest.mark.parametrize('forced', [True, False], ids=['forced', 'normal'])
@pytest.mark.parametrize(
    'order_id, expected_json',
    [
        (
            '30000000000000000000000000000000',
            {
                'error_flag': False,
                'receipt': {
                    'ride_cost': '73.7',
                    'ride_destination_waiting_time': 0,
                    'ride_discount_amount': '76.13',
                    'ride_start_cost': '89',
                    'ride_total_distance_km': '11.062',
                    'ride_total_time_sec': 1347,
                    'ride_transit_waiting_time': 0,
                    'ride_waiting_cost': '16.26',
                    'ride_waiting_time': 244,
                    'ride_zones': [
                        {
                            'ride_distance_cost': '22.12',
                            'ride_distance_km': '11.062',
                            'ride_time_sec': 1347,
                            'ride_time_cost': '22.45',
                            'zone_name': 'kishinev',
                            'tariff_distance_price': '2',
                            'tariff_time_price': '1',
                        },
                    ],
                    'tariff_waiting_price': '4',
                },
            },
        ),
        (
            '40000000000000000000000000000000',
            {
                'error_flag': False,
                'receipt': {
                    'ride_cost': '66.7',
                    'ride_discount_amount': '79.14',
                    'ride_start_cost': '89',
                    'ride_total_distance_km': '8.954',
                    'ride_total_time_sec': 1064,
                    'ride_waiting_cost': '21.2',
                    'ride_waiting_time': 318,
                    'ride_zones': [
                        {
                            'ride_distance_cost': '17.9',
                            'ride_distance_km': '8.954',
                            'ride_time_sec': 1064,
                            'ride_time_cost': '17.73',
                            'tariff_distance_price': '2',
                            'tariff_time_price': '1',
                            'zone_name': 'kishinev',
                        },
                    ],
                    'tariff_waiting_price': '4',
                },
            },
        ),
        (
            '50000000000000000000000000000000',
            {
                'error_flag': False,
                'receipt': {
                    'ride_cost': '42.5',
                    'ride_start_cost': '42.5',
                    'ride_total_distance_km': '0',
                    'ride_total_time_sec': 0,
                    'ride_zones': [],
                },
            },
        ),
        (
            '60000000000000000000000000000000',
            {
                'error_flag': False,
                'receipt': {
                    'ride_cost': '0',
                    'ride_start_cost': '0',
                    'ride_total_distance_km': '0',
                    'ride_total_time_sec': 0,
                    'ride_zones': [],
                },
            },
        ),
    ],
    ids=[
        'new_pricing',
        'old_pricing',
        'support_closed_order',
        'closed_by_disp',
    ],
)
@pytest.mark.config(
    PRICING_ADMIN_RECEIPT_FALLBACK_ATTEMPTS_LIMIT=3,
    CURRENCY_ROUNDING_RULES={'MDL': {'__default__': 0.1}},
    CURRENCY_FORMATTING_RULES={'MDL': {'__default__': 1, 'iso4217': 2}},
)
@pytest.mark.now('2020-04-22 12:00:00.0000+03')
async def test_v1_receipt_md_fallback(
        taxi_pricing_admin,
        forced,
        order_archive_mock,
        load_json,
        taxi_config,
        order_id,
        expected_json,
):
    taxi_config.set(PRICING_ADMIN_RECEIPT_FALLBACK_FORCED=forced)
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    for i in range(0, 4):
        response = await taxi_pricing_admin.get(
            'v1/receipt/md', params={'order_id': order_id},
        )
        if i < 3 and not forced:
            assert response.status_code == 404
        else:
            assert response.status_code == 200
            assert response.json() == expected_json
