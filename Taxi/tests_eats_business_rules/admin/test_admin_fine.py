import datetime

import psycopg2
import pytest

from tests_eats_business_rules.admin import fine_helper


def _pg_dttm(dttm):
    pg_tz = psycopg2.tz.FixedOffsetTimezone(offset=180)
    pg_dttm = datetime.datetime.strptime(dttm, '%Y-%m-%dT%H:%M:%S')
    return pg_dttm.replace(tzinfo=pg_tz)


async def test_fine_list_happy_path_region(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/list'
    await (
        fine_helper.AdminFineTest()
        .list_request(
            0,
            2,
            None,
            None,
            None,
            'Московская область',
            None,
            None,
            None,
            '2020-12-02T15:32:22+0000',
        )
        .expected_result_list(
            [
                {
                    'rule_id': '8',
                    'applied_at': '2020-10-31T23:00:00+00:00',
                    'cancelled_at': None,
                    'level': 'region',
                    'business_type': 'store',
                    'delivery_type': 'native',
                    'reason': 'return',
                    'region_name': 'Московская область',
                    'commission_type': 'pickup',
                    'fine_params': {
                        'application_period': 24,
                        'fine': '1',
                        'fix_fine': '5',
                        'min_fine': '0.5',
                        'max_fine': '10',
                        'gmv_limit': '7',
                    },
                },
                {
                    'rule_id': '12',
                    'applied_at': '2020-11-01T00:00:00+00:00',
                    'cancelled_at': None,
                    'level': 'region',
                    'business_type': 'restaurant',
                    'delivery_type': 'native',
                    'reason': 'return',
                    'region_name': 'Московская область',
                    'fine_params': {
                        'application_period': 72,
                        'fine': '3.5',
                        'fix_fine': '5',
                        'min_fine': '0.5',
                        'max_fine': '10',
                        'gmv_limit': '7',
                    },
                },
            ],
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


async def test_fine_list_no_counterparty_or_name(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/fine/list'
    await (
        fine_helper.AdminFineTest()
        .list_request(
            11,
            2,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            '2020-12-02T15:32:22+0000',
        )
        .should_fail(
            400, 'FORMAT_ERROR', 'Fine must have counterparty or region name',
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


async def test_fine_list_not_found(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/list'
    await (
        fine_helper.AdminFineTest()
        .list_request(
            0,
            2,
            None,
            'place',
            '52',
            None,
            None,
            None,
            None,
            '2010-12-02T15:32:22+0000',
        )
        .should_fail(404, 'NOT_FOUND', 'Cannot find any counterparty fine')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_fine_create_happy_path(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/create'

    await (
        fine_helper.AdminFineTest()
        .create_request(
            '2022-05-14T12:00:00+00:00',
            'counterparty',
            'store',
            'pickup',
            'cancellation',
            '22',
            'courier',
            None,
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .expected_result(
            'fine_13',
            '2022-05-14T12:00:00+00:00',
            None,
            'counterparty',
            'store',
            'pickup',
            'cancellation',
            '6',
            None,
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2021-01-01T12:00:00+0000')
async def test_fine_create_backdate_fail(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/create'
    await (
        fine_helper.AdminFineTest()
        .create_request(
            '2020-05-14T12:00:00+00:00',
            'counterparty',
            'store',
            'pickup',
            'cancellation',
            '22',
            'courier',
            None,
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .should_fail(400, 'FORMAT_ERROR', 'Cannot set backdated fine')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_fine_create_duplicate_fail(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/create'
    await (
        fine_helper.AdminFineTest()
        .create_request(
            '2020-11-03T22:00:00+00:00',
            'counterparty',
            'restaurant',
            'native',
            'return',
            '12',
            'courier',
            None,
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .should_fail(
            400,
            'FORMAT_ERROR',
            'Cannot set fine. Is such counterparty already exists?',
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_fine_create_counterparty_not_found(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/fine/create'
    await (
        fine_helper.AdminFineTest()
        .create_request(
            '2020-11-03T22:00:00+00:00',
            'counterparty',
            'restaurant',
            'native',
            'return',
            '13',
            'courier',
            None,
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .should_fail(
            404, 'NOT_FOUND', 'courier counterparty id == 13 not found',
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_fine_update_happy_path(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/update'
    await (
        fine_helper.AdminFineTest()
        .update_request(
            '2020-10-31T23:00:00+00:00',
            '2020-11-15T13:00:00+00:00',
            'region',
            'store',
            'native',
            'return',
            None,
            None,
            'Московская область',
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .expected_result(
            'fine_13',
            '2020-11-15T13:00:00+00:00',
            None,
            'region',
            'store',
            'native',
            'return',
            None,
            'Московская область',
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_fine_update_not_found_fail(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/update'
    await (
        fine_helper.AdminFineTest()
        .update_request(
            '2020-10-31T23:00:00+00:00',
            '2020-11-15T13:00:00+00:00',
            'region',
            'restaurant',
            'native',
            'return',
            None,
            None,
            'Московская область',
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .should_fail(404, 'NOT_FOUND', 'Cannot find any fine')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_fine_update_backdate_fail(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/update'
    await (
        fine_helper.AdminFineTest()
        .update_request(
            '2020-10-31T23:00:00+00:00',
            '2020-11-15T13:00:00+00:00',
            'region',
            'store',
            'native',
            'return',
            None,
            None,
            'Московская область',
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .should_fail(400, 'FORMAT_ERROR', 'Cannot set backdated fine')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2020-01-01T12:00:00+0000')
async def test_fine_update_new_date_earlier_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/fine/update'
    await (
        fine_helper.AdminFineTest()
        .update_request(
            '2020-10-31T23:00:00+00:00',
            '2020-09-15T13:00:00+00:00',
            'region',
            'store',
            'native',
            'return',
            None,
            None,
            'Московская область',
            {
                'application_period': 4,
                'fine': '2',
                'fix_fine': '3',
                'min_fine': '1',
                'max_fine': '10',
                'gmv_limit': '8',
            },
        )
        .should_fail(
            400,
            'FORMAT_ERROR',
            'New application date must be later than modifiable fine',
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_fine_delete_happy_path(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/delete'
    await (
        fine_helper.AdminFineTest()
        .delete_request(
            '2020-11-03T22:00:00+00:00',
            'counterparty',
            'restaurant',
            'native',
            'return',
            '12',
            'courier',
            None,
        )
        .expected_result(
            'fine_4',
            '2020-11-03T22:00:00+00:00',
            None,
            'counterparty',
            'restaurant',
            'native',
            'return',
            '4',
            None,
            {
                'application_period': 24,
                'fine': '1',
                'fix_fine': '5',
                'min_fine': '0.5',
                'max_fine': '10',
                'gmv_limit': '7',
            },
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )

    fine_helper.check_db_state(
        pgsql,
        'counterparty',
        'restaurant',
        'native',
        'return',
        [
            (
                3,
                _pg_dttm('2020-11-01T02:00:00'),
                _pg_dttm('2020-11-04T01:00:00'),
            ),
            (
                5,
                _pg_dttm('2020-12-01T00:00:00'),
                _pg_dttm('2020-12-04T00:00:00'),
            ),
        ],
    )


@pytest.mark.now('2021-01-01T12:00:00+0000')
async def test_fine_delete_backdated_fail(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/fine/delete'
    await (
        fine_helper.AdminFineTest()
        .delete_request(
            '2020-11-03T22:00:00+00:00',
            'counterparty',
            'restaurant',
            'native',
            'return',
            '12',
            'courier',
            None,
        )
        .should_fail(400, 'FORMAT_ERROR', 'Cannot delete backdated fine')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_delete_not_found_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/fine/delete'
    await (
        fine_helper.AdminFineTest()
        .delete_request(
            '2020-11-03T22:00:00+00:00',
            'counterparty',
            'shop',
            'native',
            'return',
            '12',
            'courier',
            None,
        )
        .should_fail(404, 'NOT_FOUND', 'Cannot find any fine')
        .run(taxi_eats_business_rules, pgsql, handler)
    )
