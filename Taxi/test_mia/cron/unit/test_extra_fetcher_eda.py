# pylint: disable=protected-access

import pytest

from mia.crontasks import personal_wrapper
from mia.crontasks.extra_fetcher import extra_fetcher_eda
from mia.crontasks.request_parser import request_parser_eda
from test_mia.cron import personal_dummy
from test_mia.cron import yt_dummy


@pytest.fixture(name='fetcher')
def create_fetcher(yt_client):
    return extra_fetcher_eda.ExtraFetcherEda(
        yt_dummy.YtLocalDummy(yt_client),
        personal_wrapper.PersonalWrapper(personal_dummy.PersonalDummy()),
    )


@pytest.mark.parametrize(
    'rows, expected',
    [
        (
            [
                {
                    'id': 1,
                    'created_idx': 1578225600,
                    'created_at': 1578225600.123,
                    'latest_revision_id': 1,
                    'courier_id': 1,
                    'user_id': 1,
                    'place_id': 1,
                    'order_nr': 'order_nr_1',
                    'personal_phone_id': 'user_phone_1_id',
                },
            ],
            [
                extra_fetcher_eda.RowWithExtraEda(
                    row={
                        'id': 1,
                        'created_idx': 1578225600,
                        'created_at': 1578225600.123,
                        'latest_revision_id': 1,
                        'courier_id': 1,
                        'user_id': 1,
                        'place_id': 1,
                        'order_nr': 'order_nr_1',
                        'personal_phone_id': 'user_phone_1_id',
                        'phone_number': 'user_phone_1',
                    },
                    order={'id': 1, 'payment_method_id': 1},
                    courier_personal_data={
                        'id': 1,
                        'inn': 'test_inn_1',
                        'address': 'test_address_1',
                        'phone_number': 'test_phone_number_1',
                    },
                    courier_service={
                        'id': 1,
                        'inn': 'test_inn_1',
                        'address': 'test_address_1',
                        'phone_number': 'test_phone_number_1',
                        'name': 'test_name_1',
                    },
                    place={
                        'id': 1,
                        'name': 'test_name_1',
                        'address_full': 'test_address_full_1',
                    },
                    user={
                        'id': 1,
                        'first_name': 'test_first_name_1',
                        'email': 'test_email_1',
                    },
                    order_revision={
                        'id': 1,
                        'cost_for_customer': 11,
                        'cost_for_place': 111,
                        'items_cost': 1111,
                        'delivery_cost': 11111,
                        'composition_id': 1,
                    },
                    order_refunds=[
                        {'id': 1, 'order_id': 1, 'amount': 1},
                        {'id': 2, 'order_id': 1, 'amount': 2},
                    ],
                    phone_numbers=[
                        {
                            'place_id': 1,
                            'phone_number': 'test_phone_number_1_1',
                        },
                        {
                            'place_id': 1,
                            'phone_number': 'test_phone_number_1_2',
                        },
                    ],
                    order_items=[
                        {
                            'id': 1,
                            'composition_id': 1,
                            'name': 'test_name_1',
                            'quantity': 1,
                        },
                        {
                            'id': 2,
                            'composition_id': 1,
                            'name': 'test_name_2',
                            'quantity': 2,
                        },
                    ],
                    order_items_options=[
                        {
                            'id': 1,
                            'item_id': 1,
                            'name': 'test_name_1',
                            'group_name': 'test_group_1',
                            'quantity': 1,
                        },
                        {
                            'id': 2,
                            'item_id': 1,
                            'name': 'test_name_2',
                            'group_name': 'test_group_1',
                            'quantity': 2,
                        },
                    ],
                    taxi_performer_info={
                        'taxi_order_id': 'taxi_order_id_1',
                        'name': 'name_1',
                        'phone_pd_id': 'phone_1_id',
                        'phone': 'phone_1',
                        'park_name': 'park_name_1',
                        'park_org_name': 'park_org_name_1',
                        'park_clid': 'park_clid_1',
                    },
                    park={
                        'id': 'park_clid_1',
                        'account_details_legal_address': 'address_1',
                        'account_details_inn': 'inn_1',
                        'phone': 'phone_1',
                        'name': 'name_1',
                    },
                ),
            ],
        ),
        (
            [
                {
                    'id': 1000,
                    'created_idx': 1578225600,
                    'created_at': 1578225600.123,
                    'latest_revision_id': 1000,
                    'courier_id': 1000,
                    'user_id': 1000,
                    'place_id': 1000,
                    'order_nr': 'order_nr_2',
                    'personal_phone_id': None,
                    'phone_number': 'user_phone_2',
                },
            ],
            [
                extra_fetcher_eda.RowWithExtraEda(
                    row={
                        'id': 1000,
                        'created_idx': 1578225600,
                        'created_at': 1578225600.123,
                        'latest_revision_id': 1000,
                        'courier_id': 1000,
                        'user_id': 1000,
                        'place_id': 1000,
                        'order_nr': 'order_nr_2',
                        'personal_phone_id': None,
                        'phone_number': 'user_phone_2',
                    },
                    order={'id': 1000, 'payment_method_id': 1},
                    courier_personal_data={
                        'id': 1000,
                        'inn': None,
                        'address': None,
                        'phone_number': None,
                    },
                    courier_service={},
                    place={},
                    user={},
                    order_revision={
                        'id': 1000,
                        'cost_for_customer': 11,
                        'cost_for_place': 111,
                        'items_cost': 1111,
                        'delivery_cost': 11111,
                        'composition_id': 1000,
                    },
                    order_refunds=[],
                    phone_numbers=[],
                    order_items=[],
                    order_items_options=[],
                    taxi_performer_info=None,
                    park=None,
                ),
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_courier_services.yaml',
        'yt_eda_courier_billing_data_history.yaml',
        'yt_eda_couriers.yaml',
        'yt_eda_courier_personal_data.yaml',
        'yt_eda_orders_monthly_2020_01.yaml',
        'yt_eda_orders_monthly_2020_02.yaml',
        'yt_eda_order_revisions_monthly_2020_01.yaml',
        'yt_eda_order_revisions_monthly_2020_02.yaml',
        'yt_eda_users.yaml',
        'yt_eda_places.yaml',
        'yt_eda_place_phone_numbers.yaml',
        'yt_eda_order_refunds_monthly_2020_01.yaml',
        'yt_eda_order_refunds_monthly_2020_02.yaml',
        'yt_eda_order_revision_items_options_2020_01.yaml',
        'yt_eda_order_revision_items_options_2020_02.yaml',
        'yt_eda_order_revision_items_2020_01.yaml',
        'yt_eda_order_revision_items_2020_02.yaml',
        'yt_eda_logistics_taxi_dispatch_requests.yaml',
        'yt_taxi_cargo_claims_denorm.yaml',
        'yt_taxi_parks.yaml',
    ],
)
@pytest.mark.now('2020-02-28T12:20:00.0')
async def test_fetch_extra(rows, expected, yt_apply, yt_client, fetcher):
    assert (
        await fetcher.fetch_extra(
            rows, request_parser_eda.ProcessorsConfigEda(),
        )
        == expected
    )


@pytest.mark.parametrize(
    'courier_services_ids, expected',
    [
        ([], []),
        (
            [1],
            [
                {
                    'address': 'test_address_1',
                    'id': 1,
                    'inn': 'test_inn_1',
                    'name': 'test_name_1',
                    'phone_number': 'test_phone_number_1',
                },
            ],
        ),
        (
            [1, 2, 3, 4, 100, 200],
            [
                {
                    'address': 'test_address_1',
                    'id': 1,
                    'inn': 'test_inn_1',
                    'name': 'test_name_1',
                    'phone_number': 'test_phone_number_1',
                },
                {
                    'address': 'test_address_2',
                    'id': 2,
                    'inn': 'test_inn_2',
                    'name': 'test_name_2',
                    'phone_number': 'test_phone_number_2',
                },
                {
                    'address': 'test_address_3',
                    'id': 3,
                    'inn': 'test_inn_3',
                    'name': 'test_name_3',
                    'phone_number': 'test_phone_number_3',
                },
                {
                    'address': 'test_address_4',
                    'id': 4,
                    'inn': 'test_inn_4',
                    'name': 'test_name_4',
                    'phone_number': 'test_phone_number_4',
                },
                {
                    'address': 'test_address_100',
                    'id': 100,
                    'inn': 'test_inn_100',
                    'name': 'test_name_100',
                    'phone_number': 'test_phone_number_100',
                },
                {
                    'address': 'test_address_200',
                    'id': 200,
                    'inn': 'test_inn_200',
                    'name': 'test_name_200',
                    'phone_number': 'test_phone_number_200',
                },
            ],
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_eda_courier_services.yaml'])
@pytest.mark.now('2020-02-28T12:20:00.0')
async def test_fetch_courier_services(
        courier_services_ids, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_courier_services(courier_services_ids)

    assert result == expected


@pytest.mark.parametrize(
    'rows, expected',
    [
        ([{'courier_id': 1, 'created_idx': 1581681600}], {1: 1}),
        ([{'courier_id': 2, 'created_idx': 1581681612}], {2: 2}),
        ([{'courier_id': 2, 'created_idx': 1581681610}], {2: 200}),
        ([{'courier_id': 2, 'created_idx': 1581681500}], {2: 100}),
        (
            [
                {'courier_id': 1, 'created_idx': 1581681600},
                {'courier_id': 2, 'created_idx': 1581681610},
            ],
            {1: 1, 2: 200},
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_courier_billing_data_history.yaml',
        'yt_eda_couriers.yaml',
    ],
)
@pytest.mark.now('2020-02-28T12:20:00.0')
async def test_fetch_courier_service_ids(
        rows, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_courier_service_ids(rows)

    assert result == expected


@pytest.mark.parametrize(
    'rows, expected',
    [
        (
            [{'id': 1, 'created_idx': 1578225600}],
            {1: {'id': 1, 'payment_method_id': 1}},
        ),
        (
            [
                {'id': 1, 'created_idx': 1578225600},
                {'id': 2, 'created_idx': 1578225700},
                {'id': 3, 'created_idx': 1581681600},
            ],
            {
                1: {'id': 1, 'payment_method_id': 1},
                2: {'id': 2, 'payment_method_id': 2},
                3: {'id': 3, 'payment_method_id': 3},
            },
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_orders_monthly_2020_01.yaml',
        'yt_eda_orders_monthly_2020_02.yaml',
    ],
)
async def test_fetch_orders(rows, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_orders(rows)

    assert result == expected


@pytest.mark.parametrize(
    'rows, expected',
    [
        (
            [{'latest_revision_id': 1, 'created_at': 1578225600}],
            {
                1: {
                    'id': 1,
                    'cost_for_customer': 11,
                    'cost_for_place': 111,
                    'items_cost': 1111,
                    'delivery_cost': 11111,
                    'composition_id': 1,
                },
            },
        ),
        (
            [
                {'latest_revision_id': 1, 'created_at': 1578225600},
                {'latest_revision_id': 2, 'created_at': 1578225700},
                {'latest_revision_id': 3, 'created_at': 1581681600},
            ],
            {
                1: {
                    'id': 1,
                    'cost_for_customer': 11,
                    'cost_for_place': 111,
                    'items_cost': 1111,
                    'delivery_cost': 11111,
                    'composition_id': 1,
                },
                2: {
                    'id': 2,
                    'cost_for_customer': 22,
                    'cost_for_place': 222,
                    'items_cost': 2222,
                    'delivery_cost': 22222,
                    'composition_id': 2,
                },
                3: {
                    'id': 3,
                    'cost_for_customer': 33,
                    'cost_for_place': 333,
                    'items_cost': 3333,
                    'delivery_cost': 33333,
                    'composition_id': 3,
                },
            },
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_order_revisions_monthly_2020_01.yaml',
        'yt_eda_order_revisions_monthly_2020_02.yaml',
    ],
)
@pytest.mark.now('2020-02-28T12:20:00.0')
async def test_fetch_order_revisions(
        rows, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_order_revisions(rows)

    assert result == expected


@pytest.mark.parametrize(
    'rows, expected',
    [
        (
            [{'courier_id': 5}],
            [{'address': None, 'id': 5, 'inn': None, 'phone_number': None}],
        ),
        (
            [{'courier_id': 1}],
            [
                {
                    'id': 1,
                    'address': 'test_address_1',
                    'inn': 'test_inn_1',
                    'phone_number': 'test_phone_number_1',
                },
            ],
        ),
        (
            [
                {'courier_id': 1},
                {'courier_id': 2},
                {'courier_id': 3},
                {'courier_id': 4},
            ],
            [
                {
                    'id': 1,
                    'address': 'test_address_1',
                    'inn': 'test_inn_1',
                    'phone_number': 'test_phone_number_1',
                },
                {
                    'id': 2,
                    'address': 'test_address_2',
                    'inn': 'test_inn_2',
                    'phone_number': 'test_phone_number_2',
                },
                {
                    'id': 3,
                    'address': 'test_address_3',
                    'inn': 'test_inn_3',
                    'phone_number': None,
                },
                {
                    'id': 4,
                    'address': None,
                    'inn': None,
                    'phone_number': 'test_phone_number_4',
                },
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_courier_personal_data.yaml',
        'yt_eda_couriers.yaml',
    ],
)
async def test_fetch_couriers_pd(rows, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_couriers_pd(rows)

    assert result == expected


@pytest.mark.parametrize(
    'rows, expected',
    [
        ([{'user_id': 4}], []),
        (
            [{'user_id': 1}],
            [
                {
                    'id': 1,
                    'first_name': 'test_first_name_1',
                    'email': 'test_email_1',
                },
            ],
        ),
        (
            [{'user_id': 1}, {'user_id': 2}, {'user_id': 3}],
            [
                {
                    'email': 'test_email_1',
                    'first_name': 'test_first_name_1',
                    'id': 1,
                },
                {
                    'email': 'test_email_2',
                    'first_name': 'test_first_name_2',
                    'id': 2,
                },
                {'email': None, 'first_name': None, 'id': 3},
            ],
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_eda_users.yaml'])
async def test_fetch_users(rows, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_users(rows)

    assert result == expected


@pytest.mark.parametrize(
    'rows, expected',
    [
        ([{'place_id': 4}], []),
        (
            [{'place_id': 1}],
            [
                {
                    'id': 1,
                    'name': 'test_name_1',
                    'address_full': 'test_address_full_1',
                },
            ],
        ),
        (
            [{'place_id': 1}, {'place_id': 2}, {'place_id': 3}],
            [
                {
                    'id': 1,
                    'name': 'test_name_1',
                    'address_full': 'test_address_full_1',
                },
                {
                    'id': 2,
                    'name': 'test_name_2',
                    'address_full': 'test_address_full_2',
                },
                {'name': None, 'address_full': None, 'id': 3},
            ],
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_eda_places.yaml'])
async def test_fetch_places(rows, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_places(rows)

    assert result == expected


@pytest.mark.parametrize(
    'places, expected',
    [
        ([{'id': 4}], []),
        (
            [{'id': 1}],
            [
                {'place_id': 1, 'phone_number': 'test_phone_number_1_1'},
                {'place_id': 1, 'phone_number': 'test_phone_number_1_2'},
            ],
        ),
        (
            [{'id': 1}, {'id': 2}, {'id': 3}],
            [
                {'place_id': 1, 'phone_number': 'test_phone_number_1_1'},
                {'place_id': 1, 'phone_number': 'test_phone_number_1_2'},
                {'place_id': 2, 'phone_number': 'test_phone_number_2_1'},
                {'place_id': 3, 'phone_number': None},
            ],
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_eda_place_phone_numbers.yaml'])
async def test_fetch_place_phone_numbers(
        places, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_place_phone_numbers(places)

    assert sorted(result, key=lambda x: str(x['phone_number'])) == sorted(
        expected, key=lambda x: str(x['phone_number']),
    )


@pytest.mark.parametrize(
    'rows, expected',
    [
        ([{'id': 1, 'created_idx': 1581681601}], []),
        ([{'id': 2, 'created_idx': 1582225600}], []),
        (
            [{'id': 1, 'created_idx': 1578225600}],
            [
                {'amount': 1, 'order_id': 1, 'id': 1},
                {'id': 2, 'amount': 2, 'order_id': 1},
            ],
        ),
        (
            [
                {'id': 1, 'created_idx': 1578225600},
                {'id': 2, 'created_idx': 1578225700},
                {'id': 3, 'created_idx': 1581681600},
            ],
            [
                {'id': 1, 'amount': 1, 'order_id': 1},
                {'id': 2, 'amount': 2, 'order_id': 1},
                {'id': 3, 'amount': 3, 'order_id': 2},
                {'id': 4, 'amount': 4, 'order_id': 3},
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_order_refunds_monthly_2020_01.yaml',
        'yt_eda_order_refunds_monthly_2020_02.yaml',
    ],
)
@pytest.mark.now('2020-02-28T12:20:00.0')
async def test_fetch_order_refunds(
        rows, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_orders_refunds(rows)

    assert sorted(result, key=lambda x: x['id']) == sorted(
        expected, key=lambda x: x['id'],
    )


@pytest.mark.parametrize(
    'items, min_created, expected',
    [
        (
            [{'id': 1}],
            1578225600,
            [
                {
                    'group_name': 'test_group_1',
                    'id': 1,
                    'item_id': 1,
                    'name': 'test_name_1',
                    'quantity': 1,
                },
                {
                    'group_name': 'test_group_1',
                    'id': 2,
                    'item_id': 1,
                    'name': 'test_name_2',
                    'quantity': 2,
                },
            ],
        ),
        (
            [{'id': 1}, {'id': 2}, {'id': 3}],
            1578225600,
            [
                {
                    'group_name': 'test_group_1',
                    'id': 1,
                    'item_id': 1,
                    'name': 'test_name_1',
                    'quantity': 1,
                },
                {
                    'group_name': 'test_group_1',
                    'id': 2,
                    'item_id': 1,
                    'name': 'test_name_2',
                    'quantity': 2,
                },
                {
                    'group_name': 'test_group_2',
                    'id': 3,
                    'item_id': 2,
                    'name': 'test_name_3',
                    'quantity': 3,
                },
                {
                    'group_name': 'test_group_4',
                    'id': 4,
                    'item_id': 3,
                    'name': 'test_name_4',
                    'quantity': 4,
                },
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_order_revision_items_options_2020_01.yaml',
        'yt_eda_order_revision_items_options_2020_02.yaml',
    ],
)
@pytest.mark.now('2020-02-28T12:20:00.0')
async def test_fetch_order_items_options(
        items, min_created, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_items_options(items, min_created)

    assert sorted(result, key=lambda x: x['id']) == sorted(
        expected, key=lambda x: x['id'],
    )


@pytest.mark.parametrize(
    'rows, revision_id_to_revision, expected',
    [
        (
            [
                {'latest_revision_id': 1, 'created_idx': 1578225600},
                {'latest_revision_id': 2, 'created_idx': 1578225600},
                {'latest_revision_id': 3, 'created_idx': 1578225600},
                {'latest_revision_id': 4, 'created_idx': 1581225600},
            ],
            {
                1: {'composition_id': 1},
                2: {'composition_id': 2},
                3: {'composition_id': 3},
                4: {'composition_id': 4},
            },
            [
                {
                    'composition_id': 1,
                    'id': 1,
                    'name': 'test_name_1',
                    'quantity': 1,
                },
                {
                    'composition_id': 1,
                    'id': 2,
                    'name': 'test_name_2',
                    'quantity': 2,
                },
                {
                    'composition_id': 2,
                    'id': 3,
                    'name': 'test_name_3',
                    'quantity': 3,
                },
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_order_revision_items_2020_01.yaml',
        'yt_eda_order_revision_items_2020_02.yaml',
    ],
)
@pytest.mark.now('2020-02-28T12:20:00.0')
async def test_fetch_order_items(
        rows, revision_id_to_revision, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_orders_items(rows, revision_id_to_revision)

    assert sorted(result, key=lambda x: x['id']) == sorted(
        expected, key=lambda x: x['id'],
    )


@pytest.mark.parametrize(
    'order_nrs, expected',
    [
        ([], {}),
        (
            ['order_nr_1', 'order_nr_3'],
            {'order_nr_1': 'claim_uuid_id_1', 'order_nr_3': 'claim_uuid_id_3'},
        ),
        (['order_not_existing_in_claims'], {}),
    ],
)
@pytest.mark.yt(
    dyn_table_data=['yt_eda_logistics_taxi_dispatch_requests.yaml'],
)
async def test_fetch_claim_uuid_ids(
        order_nrs, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_claim_uuid_ids(order_nrs)
    assert result == expected


@pytest.mark.parametrize(
    'claim_uuid_ids, expected',
    [
        ([], {}),
        (
            ['claim_uuid_id_1'],
            {
                'claim_uuid_id_1': {
                    'taxi_order_id': 'taxi_order_id_1',
                    'name': 'name_1',
                    'park_clid': 'park_clid_1',
                    'park_name': 'park_name_1',
                    'park_org_name': 'park_org_name_1',
                    'phone_pd_id': 'phone_1_id',
                },
            },
        ),
        (['claim_uuid_id_not_existing_in_claims'], {}),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_taxi_cargo_claims_denorm.yaml'])
async def test_fetch_taxi_performer_info(
        claim_uuid_ids, expected, yt_apply, yt_client, fetcher,
):
    result = await fetcher._fetch_taxi_performer_info(claim_uuid_ids)
    assert result == expected


@pytest.mark.parametrize(
    'park_clids, expected',
    [
        ([], {}),
        (
            ['park_clid_1'],
            {
                'park_clid_1': {
                    'id': 'park_clid_1',
                    'account_details_legal_address': 'address_1',
                    'account_details_inn': 'inn_1',
                    'name': 'name_1',
                    'phone': 'phone_1',
                },
            },
        ),
        (['park_clid_not_existing_in_parks'], {}),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_taxi_parks.yaml'])
async def test_fetch_parks(park_clids, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_parks(park_clids)
    assert result == expected
